from pathlib import Path
import json
import tomllib

REPO = Path(__file__).resolve().parents[3]
PLUGIN = REPO / "plugins" / "tinyfish-controller"

EXISTING_PLUGINS = {
    "github-arena@whitechronos-repo",
    "superpowers@openai-curated",
    "superpowers-controller@whitechronos-repo",
    "matt-pocock-controller@whitechronos-repo",
    "ecc@whitechronos-repo",
    "ecc-controller@whitechronos-repo",
    "subagent-broker@whitechronos-repo",
    "awesome-llm-apps-controller@whitechronos-repo",
    "whitechronos-control-plane@whitechronos-repo",
}


def test_marketplace_registers_tinyfish_controller():
    data = json.loads((REPO / ".agents/plugins/marketplace.json").read_text())
    item = next(p for p in data["plugins"] if p["name"] == "tinyfish-controller")
    assert item["source"] == {"source": "local", "path": "./plugins/tinyfish-controller"}
    assert item["policy"]["installation"] == "INSTALLED_BY_DEFAULT"
    assert item["policy"]["authentication"] == "ON_INSTALL"
    assert item["policy"]["products"] == ["CODEX"]


def test_codex_config_enables_tinyfish_and_preserves_existing_plugins():
    with (REPO / ".codex/config.toml").open("rb") as handle:
        cfg = tomllib.load(handle)
    assert EXISTING_PLUGINS <= set(cfg["plugins"])
    assert cfg["plugins"]["tinyfish-controller@whitechronos-repo"]["enabled"] is True


def test_plugin_manifest_is_skill_only():
    path = PLUGIN / ".codex-plugin/plugin.json"
    assert path.exists(), "TinyFish controller manifest missing"
    manifest = json.loads(path.read_text())
    assert manifest["name"] == "tinyfish-controller"
    assert manifest["version"] == "1.0.0"
    assert manifest["skills"] == "./skills/"
    assert "mcpServers" not in manifest


def test_agents_md_defines_tinyfish_routing_without_replacing_native_connectors():
    text = (REPO / "AGENTS.md").read_text()
    assert "TinyFish" in text
    assert "Connection Controller" in text
    assert "native GitHub/GitLab" in text
    assert "GitHub Arena" in text
    assert "Superpowers" in text



def test_runtime_foundation_directly_covers_tinyfish_controller():
    workflow = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    assert workflow.count('"plugins/tinyfish-controller/**"') >= 2
    assert "python -m pytest -q plugins/tinyfish-controller/tests" in workflow


def test_connection_runbook_keeps_tinyfish_profile_failure_degraded():
    runbook = REPO / "docs" / "runbooks" / "whitechronos-connections.md"
    assert runbook.exists(), "connection runbook missing"
    text = runbook.read_text()
    assert "TinyFish" in text
    assert "list_profiles" in text
    assert "DEGRADED" in text
    assert "HOST_POLICY_BLOCKED" in text
