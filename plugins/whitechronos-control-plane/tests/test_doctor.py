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



NATIVE_V1_TOOLS = frozenset((
    "spawn_agent", "send_input", "wait_agent", "resume_agent", "close_agent",
))
NATIVE_V2_TOOLS = frozenset((
    "spawn_agent", "send_message", "followup_task", "wait_agent", "interrupt_agent", "list_agents",
))
NATIVE_V2_TOOLS_WITHOUT_MESSAGE_INTERRUPT = frozenset((
    "spawn_agent", "followup_task", "wait_agent", "list_agents",
))
NATIVE_V1_NAMESPACED_TOOLS = frozenset(f"multi_agent_v1__{name}" for name in NATIVE_V1_TOOLS)
NATIVE_V2_NAMESPACED_TOOLS = frozenset(f"collaboration__{name}" for name in NATIVE_V2_TOOLS)

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
    monkeypatch.setenv("SUBAGENT_BROKER_REPO_ROOT", str(repo.resolve()))
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


def test_observed_empty_host_inventory_requires_reload(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    inputs = DoctorInput(repo, _head(repo), str(repo / "plugins/subagent-broker/tests/fake-codex.mjs"), frozenset(), "trusted_remote", host_inventory_observed=True)
    report = doctor.run_doctor(inputs)
    assert _status(report, "HOST_ARENA_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert report.live_smoke_ready is False


def test_untracked_source_file_blocks_strict_smoke_readiness(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    (repo / "surprise.py").write_text("print('untracked')\n", encoding="utf-8")
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "WORKTREE_STATE") is CheckStatus.FAIL
    assert report.live_smoke_ready is False


def test_untracked_python_cache_does_not_block_smoke_readiness(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    monkeypatch.setenv("SUBAGENT_BROKER_REPO_ROOT", str(repo.resolve()))
    cache = repo / "plugins/example/__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.cpython-312.pyc").write_bytes(b"cache")
    report = _run(repo, host_tools=BROKER_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "WORKTREE_STATE") is CheckStatus.PASS
    assert report.live_smoke_ready is True

def _replace_codex_config(repo: Path, text: str) -> None:
    (repo / ".codex" / "config.toml").write_text(text, encoding="utf-8")


def test_current_agents_enabled_config_is_native_multi_agent_configured(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS


def test_current_multi_agent_feature_is_valid_native_config(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert "[features]\nmulti_agent = true\n" in current
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS
    detail = next(item.detail for item in report.checks if item.name == "NATIVE_MULTI_AGENT_CONFIG")
    assert "legacy" not in detail.lower()


def test_disabling_v1_without_enabling_v2_is_config_drift(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    feature = "[features]\nmulti_agent = true\n\n"
    assert feature in current
    _replace_codex_config(repo, current.replace(feature, "[features]\nmulti_agent = false\n\n"))
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.FAIL


def test_explicit_v2_keeps_config_ready_when_v1_is_disabled(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    feature = "[features]\nmulti_agent = true\n\n"
    assert feature in current
    _replace_codex_config(
        repo,
        current.replace(
            feature,
            "[features]\nmulti_agent = false\nmulti_agent_v2 = true\n\n",
        ),
    )
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS


def test_agents_enabled_defaults_true_when_agents_table_is_absent(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    agents = "[agents]\nenabled = true\n\n"
    assert agents in current
    _replace_codex_config(repo, current.replace(agents, ""))
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS


def test_explicit_v2_takes_precedence_over_agents_disabled(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    agents = "[agents]\nenabled = true\n\n"
    feature = "[features]\nmulti_agent = true\n\n"
    assert agents in current and feature in current
    current = current.replace(agents, "[agents]\nenabled = false\n\n")
    current = current.replace(feature, "[features]\nmulti_agent = false\nmulti_agent_v2 = true\n\n")
    _replace_codex_config(repo, current)
    report = _run(repo)
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS


def test_partial_native_tool_set_is_not_host_discovered(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools={"spawn_agent"}, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert report.selected_subagent_path != "native_codex_multi_agent"


def test_complete_native_tool_set_is_ready_without_broker_host_tools(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(repo, host_tools=NATIVE_V2_TOOLS, runtime_kind="trusted_remote", expected_commit=_head(repo))
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    assert _status(report, "HOST_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    assert report.selected_subagent_path == "native_codex_multi_agent"
    assert "HOST_RELOAD_REQUIRED" not in report.blockers



def test_native_route_requires_all_six_lifecycle_tools(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(
        repo,
        host_tools=NATIVE_V2_TOOLS_WITHOUT_MESSAGE_INTERRUPT,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert report.selected_subagent_path != "native_codex_multi_agent"


def test_native_host_discovery_uses_observed_inventory_even_when_repo_config_is_drifted(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    agents = "[agents]\nenabled = true\n\n"
    feature = "[features]\nmulti_agent = true\n\n"
    assert agents in current and feature in current
    current = current.replace(agents, "[agents]\nenabled = false\n\n")
    current = current.replace(feature, "[features]\nmulti_agent = false\n\n")
    _replace_codex_config(repo, current)
    report = _run(
        repo,
        host_tools=NATIVE_V2_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.FAIL
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    assert _status(report, "HOST_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    assert report.selected_subagent_path == "native_codex_multi_agent"


def test_complete_native_v1_tool_set_is_ready(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(
        repo,
        host_tools=NATIVE_V1_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    evidence = next(item.evidence for item in report.checks if item.name == "HOST_NATIVE_SUBAGENT_DISCOVERY")
    assert evidence["version"] == "v1"
    assert report.selected_subagent_path == "native_codex_multi_agent"


def test_namespaced_native_v1_tool_set_is_ready(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(
        repo,
        host_tools=NATIVE_V1_NAMESPACED_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    evidence = next(item.evidence for item in report.checks if item.name == "HOST_NATIVE_SUBAGENT_DISCOVERY")
    assert evidence["version"] == "v1"


def test_namespaced_native_v2_tool_set_is_ready(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    report = _run(
        repo,
        host_tools=NATIVE_V2_NAMESPACED_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    evidence = next(item.evidence for item in report.checks if item.name == "HOST_NATIVE_SUBAGENT_DISCOVERY")
    assert evidence["version"] == "v2"


def test_unverified_namespace_separators_do_not_count_as_native_tools(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    for separator in (".", "/"):
        host_tools = frozenset(f"collaboration{separator}{name}" for name in NATIVE_V2_TOOLS)
        report = _run(
            repo,
            host_tools=host_tools,
            runtime_kind="trusted_remote",
            expected_commit=_head(repo),
        )
        assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
        assert report.selected_subagent_path != "native_codex_multi_agent"


def test_unconfigured_multi_agent_v2_namespace_is_not_accepted(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    host_tools = frozenset(f"multi_agent_v2__{name}" for name in NATIVE_V2_TOOLS)
    report = _run(
        repo,
        host_tools=host_tools,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.HOST_RELOAD_REQUIRED
    assert report.selected_subagent_path != "native_codex_multi_agent"


def test_configured_custom_v2_namespace_is_ready(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    current = (repo / ".codex" / "config.toml").read_text(encoding="utf-8")
    feature = "[features]\nmulti_agent = true\n\n"
    assert feature in current
    configured = """[features]
multi_agent = false

[features.multi_agent_v2]
enabled = true
tool_namespace = "agents"

"""
    _replace_codex_config(repo, current.replace(feature, configured))
    host_tools = frozenset(f"agents__{name}" for name in NATIVE_V2_TOOLS)
    report = _run(
        repo,
        host_tools=host_tools,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "NATIVE_MULTI_AGENT_CONFIG") is CheckStatus.PASS
    assert _status(report, "HOST_NATIVE_SUBAGENT_DISCOVERY") is CheckStatus.PASS
    evidence = next(item.evidence for item in report.checks if item.name == "HOST_NATIVE_SUBAGENT_DISCOVERY")
    assert evidence["version"] == "v2"


def test_broker_route_requires_codex_resume_support(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    monkeypatch.setenv("SUBAGENT_BROKER_REPO_ROOT", str(repo.resolve()))
    monkeypatch.setattr(
        doctor,
        "probe_codex_cli",
        lambda path, timeout_seconds=5.0: CodexCapabilities(
            "codex-cli no-resume", True, True, False, True, True, True
        ),
    )
    report = _run(
        repo,
        host_tools=BROKER_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(report, "CODEX_RESUME") is CheckStatus.UNAVAILABLE
    assert _status(report, "HOST_BROKER_DISCOVERY") is not CheckStatus.PASS
    assert _status(report, "HOST_SUBAGENT_DISCOVERY") is not CheckStatus.PASS
    assert report.selected_subagent_path != "subagent_broker"
    assert report.live_smoke_ready is False


def test_broker_host_discovery_requires_actual_matching_repo_binding(tmp_path, monkeypatch):
    repo = _fixture_repo(tmp_path); _pass_probes(monkeypatch)
    monkeypatch.delenv("SUBAGENT_BROKER_REPO_ROOT", raising=False)
    report = _run(
        repo,
        host_tools=BROKER_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    names = {item.name for item in report.checks}
    assert "BROKER_REPO_BINDING" in names
    assert _status(report, "BROKER_REPO_BINDING") is CheckStatus.USER_ACTION_REQUIRED
    assert _status(report, "HOST_BROKER_DISCOVERY") is CheckStatus.USER_ACTION_REQUIRED
    assert report.live_smoke_ready is False

    other = tmp_path / "other-repo"
    other.mkdir()
    monkeypatch.setenv("SUBAGENT_BROKER_REPO_ROOT", str(other))
    mismatched = _run(
        repo,
        host_tools=BROKER_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(mismatched, "BROKER_REPO_BINDING") is CheckStatus.USER_ACTION_REQUIRED
    assert _status(mismatched, "HOST_BROKER_DISCOVERY") is CheckStatus.USER_ACTION_REQUIRED

    monkeypatch.setenv("SUBAGENT_BROKER_REPO_ROOT", str(repo.resolve()))
    matched = _run(
        repo,
        host_tools=BROKER_TOOLS,
        runtime_kind="trusted_remote",
        expected_commit=_head(repo),
    )
    assert _status(matched, "BROKER_REPO_BINDING") is CheckStatus.PASS
    assert _status(matched, "HOST_BROKER_DISCOVERY") is CheckStatus.PASS
