from __future__ import annotations

import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
CLI = PLUGIN_ROOT / "scripts" / "connection_preflight.py"
sys.path.insert(0, str(PLUGIN_ROOT))


def _api():
    assert importlib.util.find_spec("runtime.connection_preflight") is not None, "connection_preflight module missing"
    return importlib.import_module("runtime.connection_preflight")


def _provider_signal(
    *,
    host_visible: bool | None = True,
    authenticated: bool | None = True,
    target_accessible: bool | None = True,
    live_verified: bool | None = None,
    host_absence_status: str = "UNAVAILABLE",
    required_blocker: str | None = None,
    optional_degradations: list[str] | None = None,
) -> dict[str, object]:
    return {
        "host_visible": host_visible,
        "authenticated": authenticated,
        "target_accessible": target_accessible,
        "live_verified": live_verified,
        "host_absence_status": host_absence_status,
        "required_blocker": required_blocker,
        "optional_degradations": optional_degradations or [],
        "evidence": [
            {
                "source": "test-harness",
                "operation": "safe_probe",
                "observed_at": "2026-10-08T21:00:00Z",
                "target": "test-target",
                "summary": "non-secret provider evidence",
            }
        ],
    }


def _payload() -> dict[str, object]:
    return {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": True,
                "live_verification_required": False,
            },
            {
                "integration_id": "gitlab-connector",
                "target_required": True,
                "live_verification_required": False,
            },
        ],
        "integrations": {
            "github-connector": _provider_signal(),
            "gitlab-connector": _provider_signal(),
        },
        "process_layers": {
            "SUPERPOWERS": "PASS",
            "ARENA": "PASS",
            "RUNTIME_DOCTOR": "NOT_APPLICABLE",
        },
    }


def test_preflight_passes_required_github_and_gitlab_with_fresh_signals():
    api = _api()
    report = api.build_connection_report(REPO, _payload())
    assert report.required_task_connections_pass is True
    assert report.blockers == ()
    assert [item.integration_id for item in report.observations] == [
        "github-connector",
        "gitlab-connector",
    ]
    assert [item.status.value for item in report.observations] == ["PASS", "PASS"]


def test_optional_tinyfish_profile_degradation_does_not_fail_required_connections():
    api = _api()
    payload = _payload()
    payload["requirements"].append(
        {
            "integration_id": "tinyfish",
            "target_required": False,
            "live_verification_required": False,
        }
    )
    payload["integrations"]["tinyfish"] = _provider_signal(
        target_accessible=None,
        optional_degradations=["profile_api_error"],
    )
    report = api.build_connection_report(REPO, payload)
    tinyfish = report.observations[-1]
    assert tinyfish.status.value == "DEGRADED"
    assert report.required_task_connections_pass is True
    assert report.blockers == ()


def test_required_tinyfish_browser_policy_block_fails_required_connections():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "tinyfish",
                "target_required": False,
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "tinyfish": _provider_signal(
                target_accessible=None,
                required_blocker="HOST_POLICY_BLOCKED",
                optional_degradations=["profile_api_error"],
            )
        },
    }
    report = api.build_connection_report(REPO, payload)
    assert report.observations[0].status.value == "HOST_POLICY_BLOCKED"
    assert report.required_task_connections_pass is False
    assert report.blockers == ("tinyfish:HOST_POLICY_BLOCKED",)


def test_unknown_integration_id_fails_closed():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "unknown-provider",
                "target_required": False,
                "live_verification_required": False,
            }
        ],
        "integrations": {"unknown-provider": _provider_signal(target_accessible=None)},
    }
    with pytest.raises(ValueError, match="unknown integration id"):
        api.build_connection_report(REPO, payload)


def test_preflight_output_does_not_echo_secret_fields():
    api = _api()
    payload = _payload()
    signal = payload["integrations"]["github-connector"]
    signal["token"] = "secret-token-value"
    signal["password"] = "secret-password-value"
    signal["cookie"] = "secret-cookie-value"
    signal["authorization"] = "Bearer secret-auth-value"
    report = api.build_connection_report(REPO, payload)
    encoded = json.dumps(api.report_to_json(report, process_layers=payload["process_layers"]), sort_keys=True)
    for secret in (
        "secret-token-value",
        "secret-password-value",
        "secret-cookie-value",
        "secret-auth-value",
    ):
        assert secret not in encoded


def test_cli_emits_deterministic_json(tmp_path):
    _api()
    assert CLI.exists(), "connection_preflight.py CLI missing"
    input_path = tmp_path / "evidence.json"
    input_path.write_text(json.dumps(_payload()), encoding="utf-8")
    command = [
        sys.executable,
        str(CLI),
        "--repo",
        str(REPO),
        "--input",
        str(input_path),
        "--json",
    ]
    first = subprocess.run(command, text=True, capture_output=True)
    second = subprocess.run(command, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    data = json.loads(first.stdout)
    assert data["required_task_connections_pass"] is True


def test_acceptance_matrix_can_combine_connections_with_process_layer_evidence():
    api = _api()
    payload = _payload()
    report = api.build_connection_report(REPO, payload)
    data = api.report_to_json(report, process_layers=payload["process_layers"])
    assert data["process_layers"] == {
        "ARENA": "PASS",
        "RUNTIME_DOCTOR": "NOT_APPLICABLE",
        "SUPERPOWERS": "PASS",
    }
    assert data["required_task_connections_pass"] is True
