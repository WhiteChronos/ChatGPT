from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.cloud_bootstrap import BootstrapResult, BootstrapStep
from runtime.cloud_model import (
    CloudEnvironmentProfile,
    CloudNetworkPolicy,
    CloudPreflightReport,
    CloudRepositorySpec,
    CloudToolchainSpec,
)
from runtime.model import CheckResult, CheckStatus


def _load(name: str):
    path = PLUGIN_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _profile() -> CloudEnvironmentProfile:
    return CloudEnvironmentProfile(
        "whitechronos-codex-cloud/v1",
        "whitechronos-control-plane",
        "codex_cloud",
        (
            CloudRepositorySpec("WhiteChronos/ChatGPT", "consumer", True),
            CloudRepositorySpec("WhiteChronos/subagent-broker-runtime", "broker", True),
        ),
        CloudToolchainSpec((3, 11), 22, True, True, True, True, True),
        CloudNetworkPolicy("explicit_allowlist", ("pypi.org",)),
        (),
    )


def _report(ready: bool = True) -> CloudPreflightReport:
    check = CheckResult(
        "CLOUD_GIT",
        CheckStatus.PASS if ready else CheckStatus.UNAVAILABLE,
        "Git available" if ready else "missing",
        {},
    )
    return CloudPreflightReport(
        (check,),
        ready,
        () if ready else ("CLOUD_GIT",),
    )


def _args(tmp_path: Path) -> list[str]:
    return [
        "--repo-root",
        str(tmp_path),
        "--profile",
        str(tmp_path / "profile.json"),
        "--repo-path",
        f"WhiteChronos/ChatGPT={tmp_path}/consumer",
        "--repo-path",
        f"WhiteChronos/subagent-broker-runtime={tmp_path}/broker",
    ]


def test_preflight_json_has_stable_top_level_fields(tmp_path, monkeypatch, capsys):
    module = _load("cloud_preflight")
    monkeypatch.setattr(module, "load_cloud_profile", lambda *_: _profile())
    monkeypatch.setattr(module, "run_cloud_preflight", lambda *_: _report(True))
    code = module.main([*_args(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert tuple(payload) == (
        "profile",
        "environment_name",
        "runtime_kind",
        "checks",
        "ready",
        "blockers",
    )
    assert payload["environment_name"] == "whitechronos-control-plane"
    assert payload["runtime_kind"] == "codex_cloud"
    assert payload["ready"] is True


def test_preflight_require_ready_exits_two_when_not_ready(
    tmp_path, monkeypatch, capsys
):
    module = _load("cloud_preflight")
    monkeypatch.setattr(module, "load_cloud_profile", lambda *_: _profile())
    monkeypatch.setattr(module, "run_cloud_preflight", lambda *_: _report(False))
    code = module.main([*_args(tmp_path), "--json", "--require-ready"])
    assert code == 2
    assert json.loads(capsys.readouterr().out)["blockers"] == ["CLOUD_GIT"]


def test_setup_defaults_to_dry_run(tmp_path, monkeypatch, capsys):
    module = _load("setup_codex_cloud")
    monkeypatch.setattr(module, "load_cloud_profile", lambda *_: _profile())
    step = BootstrapStep(
        "WhiteChronos/ChatGPT",
        tmp_path / "consumer",
        ("python", "-m", "pip"),
    )
    monkeypatch.setattr(module, "build_bootstrap_plan", lambda *_: (step,))
    seen: list[bool] = []

    def execute(steps, *, apply, timeout_seconds=300.0):
        seen.append(apply)
        return (BootstrapResult(step, 0, "DRY_RUN", ""),)

    monkeypatch.setattr(module, "execute_bootstrap_plan", execute)
    code = module.main([*_args(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert seen == [False]
    assert payload["apply"] is False


def test_invalid_repo_mapping_exits_one_without_traceback(tmp_path, capsys):
    module = _load("cloud_preflight")
    code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--repo-path",
            "broken-mapping",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "invalid --repo-path" in captured.err
    assert "Traceback" not in captured.err


def test_cli_output_contains_no_host_discovered_or_live_verified_claim(
    tmp_path, monkeypatch, capsys
):
    module = _load("cloud_preflight")
    monkeypatch.setattr(module, "load_cloud_profile", lambda *_: _profile())
    monkeypatch.setattr(module, "run_cloud_preflight", lambda *_: _report(True))
    assert module.main([*_args(tmp_path), "--json"]) == 0
    output = capsys.readouterr().out
    assert "HOST_DISCOVERED" not in output
    assert "LIVE_VERIFIED" not in output
    assert "LIVE_SMOKE_READY" not in output


def test_codex_cloud_runbook_contract():
    path = REPO / "docs" / "codex-cloud.md"
    text = path.read_text(encoding="utf-8")
    for term in (
        "WhiteChronos/ChatGPT",
        "WhiteChronos/subagent-broker-runtime",
        "setup_codex_cloud.py",
        "cloud_preflight.py",
        "Runtime Doctor",
        "HOST_RELOAD_REQUIRED",
        "LIVE_SMOKE_READY",
        "Desktop Commander",
        "DigitalOcean",
    ):
        assert term in text
    lower = text.lower()
    assert "desktop commander is not required" in lower
    assert "digitalocean is not required" in lower
