from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

import runtime.doctor as doctor
from runtime.model import CheckStatus, CodexCapabilities, DoctorInput, McpProbeResult

BROKER_TOOLS = frozenset((
    "subagent_spawn", "subagent_status", "subagent_wait", "subagent_result",
    "subagent_followup", "subagent_list", "subagent_cancel", "subagent_cleanup",
))


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(REPO / "registry", repo / "registry")
    for rel in [
        ".codex/config.toml", ".agents/plugins/marketplace.json",
        "plugins/github-arena/.mcp.json", "plugins/github-arena/.codex-plugin/plugin.json",
        "plugins/github-arena/mcp-server/mcp_server.mjs",
        "plugins/subagent-broker/.mcp.json", "plugins/subagent-broker/.codex-plugin/plugin.json",
        "plugins/subagent-broker/mcp-server/mcp_server.mjs",
        "plugins/subagent-broker/tests/fake-codex.mjs",
    ]:
        _copy_file(REPO / rel, repo / rel)
    (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "doctor@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Doctor Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)
    return repo


def _head(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def _pass_probes(monkeypatch):
    def fake_mcp(launch, *, expected_tools, timeout_seconds=5.0):
        return McpProbeResult("fixture", CheckStatus.PASS, {"name":"fixture"}, tuple(expected_tools), (), (), "")
    monkeypatch.setattr(doctor, "probe_stdio_mcp", fake_mcp)
    monkeypatch.setattr(doctor, "probe_codex_cli", lambda path, timeout_seconds=5.0: CodexCapabilities("codex-cli 99", True, True, True, True, True, True))


def _status(report, name: str) -> CheckStatus:
    return next(item.status for item in report.checks if item.name == name)


def _run(repo: Path, *, host_tools=frozenset(), runtime_kind="unknown", expected_commit=None):
    return doctor.run_doctor(DoctorInput(repo, expected_commit, str(repo / "plugins/subagent-broker/tests/fake-codex.mjs"), frozenset(host_tools), runtime_kind))


def test_configured_is_not_host_discovered(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.UNAVAILABLE
    assert report.live_smoke_ready is False


def test_local_mcp_pass_plus_missing_host_tools_requires_reload(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools={"unrelated_tool"}, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "BROKER_MCP_LOCAL_TOOLS") is CheckStatus.PASS
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert report.live_smoke_ready is False


def test_partial_broker_host_tool_set_is_not_pass(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools={"subagent_spawn"}, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED


def test_no_host_inventory_is_unavailable_not_fail(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo)
    assert _status(report, "HOST_ARENA_DISCOVERY") is CheckStatus.UNAVAILABLE
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.UNAVAILABLE


def test_missing_codex_json_blocks_live_smoke(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    monkeypatch.setattr(doctor, "probe_codex_cli", lambda path, timeout_seconds=5.0: CodexCapabilities("codex-cli old", True, False, False, True, True, True))
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "CODEX_EXEC_JSON") is CheckStatus.FAIL
    assert report.live_smoke_ready is False


def test_commit_mismatch_blocks_strict_smoke_readiness(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit="0" * 40)
    assert _status(report, "GIT_HEAD") is CheckStatus.FAIL
    assert report.live_smoke_ready is False


def test_dirty_worktree_blocks_strict_smoke_readiness(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    (repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "WORKTREE_STATE") is CheckStatus.FAIL
    assert report.live_smoke_ready is False


def test_trusted_remote_with_complete_broker_tools_is_live_smoke_ready(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.PASS
    assert report.selected_subagent_path == "subagent_broker"
    assert report.live_smoke_ready is True


def test_stale_host_never_recommends_source_mutation(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools={"unrelated_tool"}, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert "HOST_RELOAD_REQUIRED" in report.blockers
    rendered = doctor.render_report(report).lower()
    assert "fresh codex" in rendered
    assert "source change" not in rendered
    assert "bugfix" not in rendered
