"""No-network checks for manual-only Jev dual service proof."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "plugins/jev-decisions/scripts/verify_live.py"
spec = importlib.util.spec_from_file_location("jev_live_verifier", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

ENV = {"JEV_LIVE_SMOKE_APPROVED": "YES", "TYPESAFE_API_KEY": "test-official", "DEFAPI_API_KEY": "test-gateway"}
REACHABLE = lambda url: {"status": "HTTPS_RESPONDED", "unauthenticated_status": 401}


def fake_official(state, questions):
    assert questions == mod.QUESTION and state["test"] == "fictional"
    return {"model": "jev-1.13.0", "answers": {"urgent": {"type": "noul", "noul": 0.7}},
            "usage": {"input_tokens": None, "output_tokens": 4}, "debug": ENV["TYPESAFE_API_KEY"]}


def fake_gateway(state, questions):
    return {"model": "typesafe/jev-1.13", "answers": {"urgent": {"type": "noul", "noul": 0.8}},
            "usage": {"input_tokens": 25, "output_tokens": 5}, "task_id": "synthetic-task",
            "debug": ENV["DEFAPI_API_KEY"]}


def test_default_is_uncredentialed_and_never_infers():
    result = mod.verify(env={}, probe=REACHABLE, evaluators={})
    assert result["overall"] == "UNAUTHENTICATED_HTTPS_ONLY"
    assert all("inference" not in v for v in result["results"].values())


def test_auth_gate_is_prior_to_network():
    result = mod.verify(live=True, env={}, probe=lambda u: pytest.fail("network call"))
    assert result["overall"] == "BLOCKED_APPROVAL"


@pytest.mark.parametrize("missing", ["TYPESAFE_API_KEY", "DEFAPI_API_KEY"])
def test_both_tokens_must_be_present(missing):
    env = {k: v for k, v in ENV.items() if k != missing}
    result = mod.verify(live=True, env=env, probe=lambda u: pytest.fail("network call"))
    assert result["overall"] == "BLOCKED_CREDENTIALS"


def test_tls_failure_blocks_all_inference():
    result = mod.verify(live=True, env=ENV, probe=lambda u: {"status": "NETWORK_UNAVAILABLE"},
                        evaluators={"typesafe": lambda *_: pytest.fail("paid call"),
                                    "defapi": lambda *_: pytest.fail("paid call")})
    assert result["overall"] == "BLOCKED_HTTPS"


def test_live_both_pass_and_do_not_echo_secrets():
    result = mod.verify(live=True, env=ENV, probe=REACHABLE,
                        evaluators={"typesafe": fake_official, "defapi": fake_gateway})
    assert result["overall"] == "LIVE_VERIFIED_BOTH"
    assert result["results"]["defapi"]["inference"]["task_id_hash"]
    serialized = json.dumps(result)
    for secret in ENV.values():
        assert secret not in serialized
    assert "synthetic-task" not in serialized


def test_model_mismatch_is_not_live_pass():
    def wrong(state, questions):
        response = fake_official(state, questions)
        response["model"] = "jev-latest"
        return response
    result = mod.verify(live=True, env=ENV, probe=REACHABLE,
                        evaluators={"typesafe": wrong, "defapi": fake_gateway})
    assert result["overall"] == "LIVE_NOT_VERIFIED"


@pytest.mark.parametrize("invalid", [True, -1, 2, float("nan")])
def test_invalid_noul_blocks_pass(invalid):
    def wrong(state, questions):
        response = fake_gateway(state, questions)
        response["answers"]["urgent"]["noul"] = invalid
        return response
    result = mod.verify(live=True, env=ENV, probe=REACHABLE,
                        evaluators={"typesafe": fake_official, "defapi": wrong})
    assert result["overall"] == "LIVE_NOT_VERIFIED"


def test_exceptions_do_not_leak_provider_details():
    def fail(state, questions):
        raise RuntimeError("provider sent back " + ENV["DEFAPI_API_KEY"])
    result = mod.verify(live=True, env=ENV, probe=REACHABLE,
                        evaluators={"typesafe": fake_official, "defapi": fail})
    assert ENV["DEFAPI_API_KEY"] not in json.dumps(result)
    assert result["overall"] == "LIVE_NOT_VERIFIED"


def test_evidence_file_not_overwritten(tmp_path, monkeypatch):
    p = tmp_path / "existing.json"
    p.write_text("retain")
    monkeypatch.setattr(mod, "verify", lambda **kw: {"overall": "BLOCKED_APPROVAL"})
    assert mod.main(["--output", str(p)]) == 2
    assert p.read_text() == "retain"
