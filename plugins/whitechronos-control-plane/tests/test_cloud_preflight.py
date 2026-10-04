from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.cloud_model import (
    CloudEnvironmentProfile,
    CloudNetworkPolicy,
    CloudPreflightInput,
    CloudRepositorySpec,
    CloudToolchainSpec,
)
from runtime.model import CodexCapabilities, CheckStatus


def _profile() -> CloudEnvironmentProfile:
    return CloudEnvironmentProfile(
        schema_version="whitechronos-codex-cloud/v1",
        environment_name="whitechronos-control-plane",
        runtime_kind="codex_cloud",
        repositories=(
            CloudRepositorySpec("WhiteChronos/ChatGPT", "consumer", True),
            CloudRepositorySpec("WhiteChronos/subagent-broker-runtime", "broker", True),
        ),
        toolchain=CloudToolchainSpec((3, 11), 22, True, True, True, True, True),
        network=CloudNetworkPolicy(
            "explicit_allowlist",
            ("registry.npmjs.org", "pypi.org", "files.pythonhosted.org"),
        ),
        required_secret_names=(),
    )


def _repo(path: Path, remote: str) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote], check=True)
    return path


def _inputs(tmp_path: Path) -> CloudPreflightInput:
    return CloudPreflightInput(
        _profile(),
        {
            "WhiteChronos/ChatGPT": _repo(
                tmp_path / "consumer",
                "https://github.com/WhiteChronos/ChatGPT.git",
            ),
            "WhiteChronos/subagent-broker-runtime": _repo(
                tmp_path / "broker",
                "git@github.com:WhiteChronos/subagent-broker-runtime.git",
            ),
        },
        "codex",
    )


def _fake_capture_ok(args, cwd=None, timeout_seconds=5.0):
    command = args[0]
    if command == "node":
        return 0, "v22.20.0", ""
    if command == "git":
        return 0, "git version 2.50.0", ""
    if command == "npm":
        return 0, "10.9.3", ""
    raise AssertionError(args)


def _caps(*_args, **_kwargs):
    return CodexCapabilities("codex-cli 99.0.0", True, True, True, True, True, True)


def test_preflight_passes_with_expected_repositories_and_toolchain(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    report = cp.run_cloud_preflight(_inputs(tmp_path))
    assert report.ready is True
    assert report.blockers == ()
    assert all(item.status is CheckStatus.PASS for item in report.checks)


def test_missing_broker_repo_is_named_blocker(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    inputs = _inputs(tmp_path)
    inputs = CloudPreflightInput(
        inputs.profile,
        {"WhiteChronos/ChatGPT": inputs.repo_paths["WhiteChronos/ChatGPT"]},
        "codex",
    )
    report = cp.run_cloud_preflight(inputs)
    assert report.ready is False
    assert "REPOSITORY:WhiteChronos/subagent-broker-runtime" in report.blockers


def test_wrong_git_remote_is_failure(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    inputs = _inputs(tmp_path)
    wrong = _repo(
        tmp_path / "wrong",
        "https://github.com/WhiteChronos/not-the-repo.git",
    )
    mapping = dict(inputs.repo_paths)
    mapping["WhiteChronos/subagent-broker-runtime"] = wrong
    report = cp.run_cloud_preflight(CloudPreflightInput(inputs.profile, mapping, "codex"))
    check = next(x for x in report.checks if x.name == "CLOUD_REPOSITORY_BROKER")
    assert check.status is CheckStatus.FAIL
    assert "WhiteChronos/not-the-repo" in check.detail


def test_python_below_311_blocks_readiness(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    monkeypatch.setattr(cp, "_python_version", lambda: (3, 10))
    report = cp.run_cloud_preflight(_inputs(tmp_path))
    assert report.ready is False
    assert "CLOUD_PYTHON_VERSION" in report.blockers


def test_node_not_major_22_blocks_readiness(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    def capture(args, cwd=None, timeout_seconds=5.0):
        if args[0] == "node":
            return 0, "v20.19.0", ""
        return _fake_capture_ok(args, cwd, timeout_seconds)

    monkeypatch.setattr(cp, "_capture", capture)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    report = cp.run_cloud_preflight(_inputs(tmp_path))
    assert report.ready is False
    assert "CLOUD_NODE_VERSION" in report.blockers


@pytest.mark.parametrize("missing", ("git", "npm"))
def test_missing_npm_or_git_blocks_readiness(tmp_path, monkeypatch, missing):
    import runtime.cloud_preflight as cp

    def capture(args, cwd=None, timeout_seconds=5.0):
        if args[0] == missing:
            return 1, "", "missing"
        return _fake_capture_ok(args, cwd, timeout_seconds)

    monkeypatch.setattr(cp, "_capture", capture)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    report = cp.run_cloud_preflight(_inputs(tmp_path))
    assert report.ready is False
    assert ("CLOUD_GIT" if missing == "git" else "CLOUD_NPM") in report.blockers


def test_missing_codex_json_blocks_readiness(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(
        cp,
        "probe_codex_cli",
        lambda *_a, **_k: CodexCapabilities(
            "codex-cli 99.0.0", True, False, True, True, True, True
        ),
    )
    report = cp.run_cloud_preflight(_inputs(tmp_path))
    assert report.ready is False
    assert "CLOUD_CODEX_EXEC_JSON" in report.blockers


def test_cloud_preflight_never_claims_host_or_live_verification(tmp_path, monkeypatch):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    payload = cp.cloud_report_to_json(cp.run_cloud_preflight(_inputs(tmp_path)))
    serialized = json.dumps(payload)
    assert "HOST_DISCOVERED" not in serialized
    assert "LIVE_VERIFIED" not in serialized
    assert "LIVE_SMOKE_READY=YES" not in serialized


def test_repository_remote_credentials_are_redacted_and_identity_still_matches(
    tmp_path, monkeypatch
):
    import runtime.cloud_preflight as cp

    monkeypatch.setattr(cp, "_capture", _fake_capture_ok)
    monkeypatch.setattr(cp, "probe_codex_cli", _caps)
    inputs = _inputs(tmp_path)
    credential_remote = _repo(
        tmp_path / "credential-broker",
        "https://x-access-token:TOPSECRET@github.com/WhiteChronos/subagent-broker-runtime.git",
    )
    mapping = dict(inputs.repo_paths)
    mapping["WhiteChronos/subagent-broker-runtime"] = credential_remote

    report = cp.run_cloud_preflight(
        CloudPreflightInput(inputs.profile, mapping, "codex")
    )
    check = next(
        item for item in report.checks
        if item.name == "CLOUD_REPOSITORY_BROKER"
    )
    serialized = json.dumps(cp.cloud_report_to_json(report))

    assert check.status is CheckStatus.PASS
    assert "TOPSECRET" not in serialized
