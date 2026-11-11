from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/awesome-llm-apps-controller/SKILL.md'

def test_controller_routes_catalog_families_and_preserves_precedence():
    text=SKILL.read_text()
    for term in ['RAG','MCP','voice','always-on','Generative UI','catalog.json']:
        assert term.lower() in text.lower()
    assert 'Superpowers' in text and 'ECC' in text and 'Matt Pocock' in text and 'Awesome LLM Apps' in text

def test_controller_forbids_gated_auto_execution_and_false_subagent_claims():
    text=SKILL.read_text().lower()
    for term in ['credentialled','background_autonomous','self_modifying','external_reference']:
        assert term.lower() in text
    assert 'native subagent' in text or 'native codex subagent' in text
    assert 'do not claim' in text or 'never claim' in text
    assert 'project-graveyard' in text and 'explicit' in text
    assert 'advisor-orchestrator-worker' in text and 'explicit' in text

def test_plugin_manifest_is_read_only_control_plane():
    data=json.loads((ROOT/'.codex-plugin/plugin.json').read_text())
    assert data['name']=='awesome-llm-apps-controller'
    assert data['skills']=='./skills/'
    assert data.get('hooks') in ({},None)
    assert 'Read' in data['capabilities']
