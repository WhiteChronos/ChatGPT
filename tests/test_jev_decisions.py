"""Offline contract and safety tests for the opt-in DefAPI Jev adapter."""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "jev-decisions"))
from defapi_jev import DEFAPI_URL, MODEL, DecisionError, decide


def _response(kind="choice", key="owner"):
    answers = {
        "choice": {"type": "choice", "choice": "engineering", "probabilities": {"engineering": 0.85, "sales": 0.15}, "confidence": 0.85},
        "noul": {"type": "noul", "noul": 0.65},
        "score": {"type": "score", "score": 1.5, "probabilities": {"0": 0.0, "1": 0.5, "2": 0.5}, "confidence": 0.8},
    }
    return {"model": MODEL, "answers": {key: answers[kind]}, "usage": {"input_tokens": 12, "output_tokens": 9}, "task_id": "fake-task", "consumed": "0.0001"}


def _mock_urlopen(monkeypatch, result, observer=None):
    def fake_urlopen(request, *, timeout):
        if observer is not None:
            observer(request, timeout)
        return io.BytesIO(json.dumps(result).encode("utf-8"))
    monkeypatch.setattr("defapi_jev.urlopen", fake_urlopen)


def test_no_credentials_fails_closed_before_network(monkeypatch):
    monkeypatch.delenv("DEFAPI_API_KEY", raising=False)
    monkeypatch.setattr("defapi_jev.urlopen", lambda *_a, **_kw: pytest.fail("Unexpected network"))
    with pytest.raises(DecisionError, match="DEFAPI_API_KEY"):
        decide("ticket", {"owner": {"type": "choice", "instructions": "Choose", "criteria": {"engineering": "Tech", "sales": "Sale"}}})


def test_choice_uses_fixed_endpoint_bearer_and_expected_payload(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "test-secret")
    def observer(req, timeout):
        assert req.full_url == DEFAPI_URL
        assert req.get_header("Authorization") == "Bearer test-secret"
        assert req.get_header("Content-type") == "application/json"
        assert timeout == 7
        data = json.loads(req.data.decode("utf-8"))
        assert data == {"model": MODEL, "state": {"ticket": "bad layout"}, "questions": {"owner": {"type": "choice", "instructions": "Choose", "criteria": {"engineering": "Tech", "sales": "Sale"}}}}
    _mock_urlopen(monkeypatch, _response(), observer)
    result = decide({"ticket": "bad layout"}, {"owner": {"type": "choice", "instructions": "Choose", "criteria": {"engineering": "Tech", "sales": "Sale"}}}, timeout=7)
    assert result["answers"]["owner"]["choice"] == "engineering"


@pytest.mark.parametrize(("kind", "criteria"), [("noul", {"true": "safe", "false": "unsafe"}), ("score", ["low", "medium", "high"])])
def test_other_decisions_return_typed_answers(monkeypatch, kind, criteria):
    monkeypatch.setenv("DEFAPI_API_KEY", "test-secret")
    _mock_urlopen(monkeypatch, _response(kind, "rating"))
    result = decide("Internal test", {"rating": {"type": kind, "instructions": "Assess", "criteria": criteria}})
    assert result["answers"]["rating"]["type"] == kind


@pytest.mark.parametrize("state,questions", [
    (99, {"owner": {"type": "noul", "instructions": "Decide"}}),
    ("x", {}),
    ("x", {"owner": {"type": "choice", "instructions": "Choose", "criteria": {"one": "only one"}}}),
    ("x", {"owner": {"type": "score", "instructions": "Rate", "criteria": ["one"]}}),
    ("x", {"owner": {"type": "score", "instructions": "Rate", "criteria": ["x"] * 11}}),
    ("x", {"owner": {"type": "invalid", "instructions": "Rate"}}),
    ("x", {"owner": {"type": "noul", "instructions": " "}}),
    ({"x": float("nan")}, {"owner": {"type": "noul", "instructions": "Rate"}}),
])
def test_bad_requests_never_call_network(monkeypatch, state, questions):
    monkeypatch.setenv("DEFAPI_API_KEY", "test-secret")
    monkeypatch.setattr("defapi_jev.urlopen", lambda *_a, **_kw: pytest.fail("Unexpected network"))
    with pytest.raises(DecisionError):
        decide(state, questions)


def test_http_error_does_not_leak_secret_or_state(monkeypatch):
    monkeypatch.setenv("DEFAPI_API_KEY", "test-secret")
    def reject(req, *, timeout):
        raise HTTPError(req.full_url, 401, "bad secret: test-secret", None, None)
    monkeypatch.setattr("defapi_jev.urlopen", reject)
    with pytest.raises(DecisionError) as ex:
        decide("confidential-state", {"q": {"type": "noul", "instructions": "Rate"}})
    assert "401" in str(ex.value)
    assert "test-secret" not in str(ex.value)
    assert "confidential-state" not in str(ex.value)


@pytest.mark.parametrize("bad_result", [
    {"answers": {}, "usage": {}, "task_id": "x", "consumed": "0"},
    {"model": MODEL, "answers": {}, "usage": {"input_tokens": 0, "output_tokens": 0}, "task_id": "x", "consumed": "0"},
    _response("choice", "unexpected"),
    {**_response("noul", "owner"), "answers": {"owner": {"type": "noul", "noul": 7}}},
])
def test_invalid_response_fails_closed(monkeypatch, bad_result):
    monkeypatch.setenv("DEFAPI_API_KEY", "test-secret")
    _mock_urlopen(monkeypatch, bad_result)
    with pytest.raises(DecisionError):
        decide("x", {"owner": {"type": "choice", "instructions": "Choose", "criteria": {"engineering": "Tech", "sales": "Sale"}}})


def test_openapi_schema_is_importable_shape_and_never_contains_secret():
    path = ROOT / "plugins" / "jev-decisions" / "chatgpt-action.openapi.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["openapi"].startswith("3.0.")
    assert data["servers"] == [{"url": "https://api.defapi.org"}]
    operation = data["paths"]["/api/v1/decisions"]["post"]
    assert operation["operationId"] == "submitJevDecisions"
    assert operation["security"] == [{"ApiKeyAuth": []}]
    assert data["components"]["securitySchemes"]["ApiKeyAuth"]["name"] == "Authorization"
    assert "test-secret" not in path.read_text(encoding="utf-8")


def test_registry_is_activation_gated_and_non_executable():
    reg = ROOT / "registry" / "integrations"
    index = json.loads((reg / "index.json").read_text())
    assert "defapi-jev.json" in index["descriptors"]
    descriptor = json.loads((reg / "defapi-jev.json").read_text())
    assert descriptor["id"] == "defapi-jev"
    assert descriptor["status"] == "ACTIVATION_GATED"
    assert descriptor["execution_class"] == "CREDENTIALLED"
    assert descriptor["mcp_servers"] == []
    assert descriptor["runtime_probe"] is None
