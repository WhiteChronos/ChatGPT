from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "whitechronos-control-plane"
CLI = PLUGIN / "scripts" / "runtime_doctor.py"
CONNECTION_CLI = PLUGIN / "scripts" / "connection_preflight.py"
SKILL = PLUGIN / "skills" / "codex-runtime-doctor" / "SKILL.md"
CONNECTION_SKILL = PLUGIN / "skills" / "whitechronos-connection-controller" / "SKILL.md"
RUNBOOK = REPO / "docs" / "runbooks" / "codex-subagent-runtime.md"
CONNECTION_RUNBOOK = REPO / "docs" / "runbooks" / "whitechronos-connections.md"

EXISTING_PLUGINS = {
    "github-arena@whitechronos-repo",
    "superpowers@openai-curated",
    "superpowers-controller@whitechronos-repo",
    "matt-pocock-controller@whitechronos-repo",
    "ecc@whitechronos-repo",
    "ecc-controller@whitechronos-repo",
    "subagent-broker@whitechronos-repo",
    "awesome-llm-apps-controller@whitechronos-repo",
}


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(REPO / "registry", repo / "registry")
    for rel in [
        ".codex/config.toml", ".agents/plugins/marketplace.json",
        "plugins/github-arena/.mcp.json", "plugins/github-arena/.codex-plugin/plugin.json",
        "plugins/github-arena/mcp-server/mcp_server.mjs",
        "plugins/subagent-broker/.mcp.json", "plugins/subagent-broker/.codex-plugin/plugin.json",
        "plugins/subagent-broker/tests/fake-codex.mjs",
    ]:
        src = REPO / rel; dst = repo / rel; dst.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dst)
    shutil.copytree(REPO / "plugins/subagent-broker/mcp-server", repo / "plugins/subagent-broker/mcp-server")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "cli@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "CLI Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repo, check=True)
    return repo


def test_marketplace_registers_whitechronos_control_plane():
    data = json.loads((REPO / ".agents/plugins/marketplace.json").read_text())
    item = next(p for p in data["plugins"] if p["name"] == "whitechronos-control-plane")
    assert item["source"] == {"source": "local", "path": "./plugins/whitechronos-control-plane"}
    assert item["policy"]["installation"] == "INSTALLED_BY_DEFAULT"
    assert item["policy"]["products"] == ["CODEX"]


def test_codex_config_enables_control_plane_without_changing_existing_layers():
    with (REPO / ".codex/config.toml").open("rb") as f:
        cfg = tomllib.load(f)
    assert EXISTING_PLUGINS <= set(cfg["plugins"])
    assert cfg["agents"]["enabled"] is True
    assert cfg["features"]["multi_agent"] is True
    assert cfg["plugins"]["whitechronos-control-plane@whitechronos-repo"]["enabled"] is True


def test_plugin_manifest_exposes_runtime_and_connection_skills():
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "whitechronos-control-plane"
    assert manifest["version"] == "0.2.0"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest
    assert sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir()) == [
        "codex-runtime-doctor",
        "whitechronos-connection-controller",
    ]


def test_agents_md_requires_runtime_doctor_for_runtime_claims():
    text = (REPO / "AGENTS.md").read_text()
    assert "Runtime Doctor" in text
    assert "config alone" in text.lower()
    assert "HOST_RELOAD_REQUIRED" in text
    assert "must not trigger code changes" in text


def test_skill_forbids_config_only_success_claims():
    text = SKILL.read_text()
    assert "CONFIGURED" in text
    assert "LOCAL_RUNTIME_HEALTHY" in text
    assert "HOST_DISCOVERED" in text
    assert "LIVE_VERIFIED" in text
    assert "Never treat repository configuration as runtime proof" in text


def test_skill_routes_host_reload_without_source_changes():
    text = SKILL.read_text()
    assert "HOST_RELOAD_REQUIRED" in text
    assert "fresh Codex" in text
    assert "do not change source" in text.lower()


def test_cli_json_diagnostic_succeeds_without_host_inventory(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    completed = subprocess.run([sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake), "--json"], text=True, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["live_smoke_ready"] is False
    statuses = {item["name"]: item["status"] for item in payload["checks"]}
    assert statuses["HOST_BROKER_DISCOVERY"] == "UNAVAILABLE"


def test_cli_strict_readiness_returns_two_when_host_reload_is_required(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    completed = subprocess.run([
        sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake),
        "--runtime-kind", "trusted_remote", "--expected-commit", head,
        "--host-tool", "unrelated_tool", "--require-live-smoke-ready"
    ], text=True, capture_output=True)
    assert completed.returncode == 2, completed.stderr
    assert "fresh Codex" in completed.stdout


def test_runtime_foundation_workflow_runs_local_suite_but_not_live_smoke():
    workflow = REPO / ".github/workflows/whitechronos-runtime-foundation.yml"
    text = workflow.read_text()
    assert "python -m pytest -q plugins/whitechronos-control-plane/tests" in text
    assert "SUBAGENT_BROKER_LIVE=1" not in text
    assert "smoke_real_codex.mjs" not in text


def test_cli_can_mark_an_observed_empty_host_inventory(tmp_path):
    repo = _fixture_repo(tmp_path)
    fake = repo / "plugins/subagent-broker/tests/fake-codex.mjs"
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    completed = subprocess.run([
        sys.executable, str(CLI), "--repo", str(repo), "--codex-path", str(fake),
        "--runtime-kind", "trusted_remote", "--expected-commit", head,
        "--host-inventory-observed", "--require-live-smoke-ready"
    ], text=True, capture_output=True)
    assert completed.returncode == 2, completed.stderr
    assert "fresh Codex" in completed.stdout


def test_runtime_foundation_workflow_runs_full_repository_regression():
    workflow = REPO / ".github/workflows/whitechronos-runtime-foundation.yml"
    lines = workflow.read_text().splitlines()
    assert any(line.strip() == "run: python -m pytest -q" for line in lines)


def test_runtime_foundation_workflow_runs_doctor_in_clean_detached_worktree():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    assert 'git worktree add --detach /tmp/whitechronos-runtime-doctor-tree "$GITHUB_SHA"' in workflow
    assert '--repo /tmp/whitechronos-runtime-doctor-tree' in workflow


def test_runbook_uses_supported_local_plugin_reinstall_flow():
    text = RUNBOOK.read_text()
    assert "codex plugin marketplace upgrade whitechronos-repo" not in text
    assert "codex plugin remove subagent-broker@whitechronos-repo" in text
    assert "codex plugin add subagent-broker@whitechronos-repo" in text


def test_runbook_runtime_doctor_example_supplies_observed_native_host_tools():
    text = RUNBOOK.read_text()
    for tool in (
        "spawn_agent",
        "send_message",
        "followup_task",
        "wait_agent",
        "interrupt_agent",
        "list_agents",
    ):
        assert f"--host-tool {tool}" in text


def test_runbook_documents_current_v1_and_v2_native_contracts():
    text = RUNBOOK.read_text()
    assert "features.multi_agent" in text
    assert "Stable" in text
    assert "V1" in text
    assert "send_input" in text
    assert "resume_agent" in text
    assert "close_agent" in text
    assert "V2" in text
    assert "send_message" in text
    assert "followup_task" in text
    assert "interrupt_agent" in text
    assert "list_agents" in text
    assert "legacy setting below is forbidden" not in text



def test_readme_documents_runtime_and_connection_preflight_clis():
    text = (PLUGIN / "README.md").read_text()
    assert "runtime_doctor.py" in text
    assert "connection_preflight.py" in text


def test_connection_skill_requires_fresh_provider_and_process_evidence():
    assert CONNECTION_SKILL.exists(), "whitechronos-connection-controller Skill missing"
    text = CONNECTION_SKILL.read_text()
    assert "repository configuration is not authentication proof" in text.lower()
    assert "Superpowers" in text
    assert "Arena" in text
    assert "Runtime Doctor" in text
    assert "GitHub" in text
    assert "GitLab" in text
    assert "TinyFish" in text


def test_connection_cli_exists():
    assert CONNECTION_CLI.exists(), "connection_preflight.py CLI missing"



def test_connection_runbook_documents_state_boundaries_and_recovery():
    assert CONNECTION_RUNBOOK.exists(), "whitechronos-connections runbook missing"
    text = CONNECTION_RUNBOOK.read_text()
    for required in (
        "CONFIGURED != HOST_VISIBLE",
        "HOST_VISIBLE != AUTHENTICATED",
        "AUTHENTICATED != TARGET_ACCESSIBLE",
        "MIRROR_PARITY",
        "DEGRADED",
        "HOST_POLICY_BLOCKED",
        "USER_ACTION_REQUIRED",
        "github.get_profile",
        "github.get_repo",
        "gitlab.get_current_user",
        "gitlab.get_project",
        "tinyfish.get_wallet",
        "list_profiles",
    ):
        assert required in text
    assert "cannot force unrelated ChatGPT conversations" in text
    assert "new session" in text.lower()


def test_runtime_foundation_observes_tinyfish_controller_and_runs_its_tests():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    assert workflow.count('"plugins/tinyfish-controller/**"') >= 2
    assert "python -m pytest -q plugins/tinyfish-controller/tests" in workflow


def test_runtime_foundation_remains_offline_for_provider_authentication():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    for forbidden in (
        "run_web_automation",
        "create_monitor",
        "get_wallet",
        "list_profiles",
        "TINYFISH_API_KEY",
        "GITHUB_TOKEN:",
        "GITLAB_TOKEN",
    ):
        assert forbidden not in workflow


def test_runtime_foundation_preserves_existing_regression_and_governance_steps():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    for required in (
        "python -m pytest -q",
        "plugins/subagent-broker/tests/mcp-protocol.test.mjs",
        "python pipeline/engineering_compatibility_gate.py",
        "python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json",
        "runtime_doctor.py",
    ):
        assert required in workflow
