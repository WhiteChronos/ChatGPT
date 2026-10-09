from __future__ import annotations

import importlib
import importlib.util
import json
from datetime import datetime, timezone
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
    operations: list[tuple[str, str | None]] | None = None,
    observed_at: str | None = None,
    summary: str = "non-secret provider evidence",
) -> dict[str, object]:
    operations = operations or [("safe_probe", "test-target")]
    observed_at = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
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
                "operation": operation,
                "observed_at": observed_at,
                "target": target,
                "summary": summary,
            }
            for operation, target in operations
        ],
    }


def _payload() -> dict[str, object]:
    return {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": True,
                "target": "WhiteChronos/ChatGPT",
                "live_verification_required": False,
            },
            {
                "integration_id": "gitlab-connector",
                "target_required": True,
                "target": "chronoswhite-group/ChronosWhite-project",
                "live_verification_required": False,
            },
        ],
        "integrations": {
            "github-connector": _provider_signal(
                operations=[
                    ("github.get_profile", None),
                    ("github.get_repo", "WhiteChronos/ChatGPT"),
                ]
            ),
            "gitlab-connector": _provider_signal(
                operations=[
                    ("gitlab.get_current_user", None),
                    ("gitlab.get_project", "chronoswhite-group/ChronosWhite-project"),
                ]
            ),
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
        operations=[("tinyfish.get_wallet", None)],
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
                operations=[("tinyfish.get_wallet", None)],
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



@pytest.mark.parametrize("status", ["PASS", "DEGRADED", "NOT_APPLICABLE"])
def test_required_blocker_rejects_non_blocking_status(status):
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": False,
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "github-connector": _provider_signal(
                required_blocker=status,
                operations=[("github.get_profile", None)],
            )
        },
    }
    with pytest.raises(ValueError, match=r"required_blocker.*blocking"):
        api.build_connection_report(REPO, payload)


def test_positive_auth_requires_registered_safe_probe_evidence():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": False,
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "github-connector": _provider_signal(
                operations=[("unrelated.probe", None)],
            )
        },
    }
    with pytest.raises(ValueError, match=r"safe_probe.*github\.get_profile"):
        api.build_connection_report(REPO, payload)


def test_positive_target_requires_registered_target_probe_evidence():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": True,
                "target": "WhiteChronos/ChatGPT",
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "github-connector": _provider_signal(
                operations=[("github.get_profile", None)],
            )
        },
    }
    with pytest.raises(ValueError, match=r"target_probe.*github\.get_repo"):
        api.build_connection_report(REPO, payload)


def test_target_requirement_rejected_when_descriptor_has_no_target_probe():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "tinyfish",
                "target_required": True,
                "target": "unused-target",
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "tinyfish": _provider_signal(
                operations=[("tinyfish.get_wallet", None)],
            )
        },
    }
    with pytest.raises(ValueError, match=r"target_required.*no target_probe"):
        api.build_connection_report(REPO, payload)


def test_evidence_rejects_secret_in_allowed_summary():
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
                operations=[("tinyfish.get_wallet", None)],
                summary="Authorization: Bearer secret-provider-token-value",
            )
        },
    }
    with pytest.raises(ValueError, match=r"evidence.*secret"):
        api.build_connection_report(REPO, payload)


def test_evidence_requires_timezone_aware_timestamp():
    api = _api()
    payload = {
        "requirements": [
            {
                "integration_id": "github-connector",
                "target_required": True,
                "target": "WhiteChronos/ChatGPT",
                "live_verification_required": False,
            }
        ],
        "integrations": {
            "github-connector": _provider_signal(
                operations=[
                    ("github.get_profile", None),
                    ("github.get_repo", "WhiteChronos/ChatGPT"),
                ],
                observed_at="2026-10-08T21:00:00",
            )
        },
    }
    with pytest.raises(ValueError, match=r"observed_at.*timezone"):
        api.build_connection_report(REPO, payload)


def test_stale_provider_evidence_is_rejected():
    api = _api()
    payload = _payload()
    for signal in payload["integrations"].values():
        for item in signal["evidence"]:
            item["observed_at"] = "2000-01-01T00:00:00Z"
    with pytest.raises(ValueError, match=r"evidence.*stale"):
        api.build_connection_report(REPO, payload)


def test_implausible_future_provider_evidence_is_rejected():
    api = _api()
    payload = _payload()
    for signal in payload["integrations"].values():
        for item in signal["evidence"]:
            item["observed_at"] = "2999-01-01T00:00:00Z"
    with pytest.raises(ValueError, match=r"evidence.*future"):
        api.build_connection_report(REPO, payload)


def test_target_probe_must_match_required_target():
    api = _api()
    payload = _payload()
    github = payload["integrations"]["github-connector"]
    github["evidence"] = [
        {
            "source": "test-harness",
            "operation": "github.get_profile",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "target": None,
            "summary": "profile ok",
        },
        {
            "source": "test-harness",
            "operation": "github.get_repo",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "target": "someone/else",
            "summary": "wrong repository",
        },
    ]
    with pytest.raises(ValueError, match=r"target.*WhiteChronos/ChatGPT"):
        api.build_connection_report(REPO, payload)


def test_live_verification_true_requires_task_specific_operation_evidence():
    api = _api()
    payload = _payload()
    requirement = payload["requirements"][0]
    requirement["live_verification_required"] = True
    requirement["live_operation"] = "github.live_write_probe"
    payload["integrations"]["github-connector"]["live_verified"] = True
    with pytest.raises(ValueError, match=r"live.*github\.live_write_probe"):
        api.build_connection_report(REPO, payload)


def test_fine_grained_github_token_is_rejected_from_evidence():
    api = _api()
    payload = _payload()
    payload["integrations"]["github-connector"]["evidence"][0]["summary"] = (
        "github_pat_11AAABBBCCCDDDEEEFFF_abcdefghijklmnopqrstuvwxyz0123456789"
    )
    with pytest.raises(ValueError, match=r"evidence.*secret"):
        api.build_connection_report(REPO, payload)


def test_mirror_parity_failure_is_preserved_and_blocks_required_task():
    api = _api()
    payload = _payload()
    payload["process_layers"]["MIRROR_PARITY"] = "FAIL"
    report = api.build_connection_report(REPO, payload)
    data = api.report_to_json(report, process_layers=payload["process_layers"])
    assert data["process_layers"]["MIRROR_PARITY"] == "FAIL"
    assert report.required_task_connections_pass is False
    assert "MIRROR_PARITY:FAIL" in report.blockers


def test_unknown_process_layer_is_rejected_instead_of_silently_dropped():
    api = _api()
    payload = _payload()
    payload["process_layers"]["UNKNOWN_LAYER"] = "PASS"
    with pytest.raises(ValueError, match=r"unknown process layer"):
        api.build_connection_report(REPO, payload)


def test_positive_claim_rejects_failed_probe_outcome():
    api = _api()
    payload = _payload()
    github = payload["integrations"]["github-connector"]
    for item in github["evidence"]:
        item["source"] = "chatgpt-github-connector"
        item["outcome"] = "failure"
    with pytest.raises(ValueError, match=r"successful.*outcome"):
        api.build_connection_report(REPO, payload)


def test_positive_claim_requires_trusted_probe_source():
    api = _api()
    payload = _payload()
    github = payload["integrations"]["github-connector"]
    for item in github["evidence"]:
        item["source"] = "caller-controlled-source"
        item["outcome"] = "success"
    with pytest.raises(ValueError, match=r"trusted.*source"):
        api.build_connection_report(REPO, payload)


def test_positive_process_layer_rejects_bare_string_without_authoritative_evidence():
    api = _api()
    payload = _payload()
    payload["process_layers"]["ARENA"] = "PASS"
    with pytest.raises(ValueError, match=r"process_layers\.ARENA.*structured.*evidence"):
        api.build_connection_report(REPO, payload)


def test_optional_degradation_rejects_secret_material():
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
        optional_degradations=[
            "Authorization: Bearer SUPER_SECRET_DEGRADATION_TOKEN"
        ],
        operations=[("tinyfish.get_wallet", None)],
    )
    with pytest.raises(ValueError, match=r"optional_degradations.*safe identifier"):
        api.build_connection_report(REPO, payload)


@pytest.mark.parametrize(
    "summary",
    [
        "token=oauth-secret-123",
        "client_secret=oauth-client-secret-456",
        "Authorization: Basic dXNlcjpzZWNyZXQ=",
        "ya29.a0AfH6SMBExampleOpaqueOAuthTokenValue",
    ],
)
def test_generic_oauth_material_is_never_serialized_from_evidence(summary):
    api = _api()
    payload = _payload()
    payload["integrations"]["github-connector"]["evidence"][0]["summary"] = summary
    report = api.build_connection_report(REPO, payload)
    encoded = json.dumps(
        api.report_to_json(report, process_layers=payload["process_layers"]),
        sort_keys=True,
    )
    assert summary not in encoded


def test_cli_validation_error_does_not_echo_untrusted_secret(tmp_path):
    payload = _payload()
    secret = "Authorization: Bearer TOP_SECRET_VALUE_123"
    payload["integrations"]["github-connector"]["host_absence_status"] = secret
    input_path = tmp_path / "evidence.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(CLI),
            "--repo",
            str(REPO),
            "--input",
            str(input_path),
            "--json",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
    assert secret not in result.stderr
    assert "TOP_SECRET_VALUE_123" not in result.stderr


def test_cli_argument_error_returns_one_not_blocker_exit_code():
    result = subprocess.run(
        [sys.executable, str(CLI), "--json"],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 1
