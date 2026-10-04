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
SKILL = PLUGIN / "skills" / "codex-runtime-doctor" / "SKILL.md"

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
    assert cfg["plugins"]["whitechronos-control-plane@whitechronos-repo"]["enabled"] is True


def test_plugin_manifest_exposes_runtime_doctor_skill_only_in_this_slice():
    manifest = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
    assert manifest["name"] == "whitechronos-control-plane"
    assert manifest["version"] == "0.1.0"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest
    assert sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir()) == ["codex-runtime-doctor"]


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
