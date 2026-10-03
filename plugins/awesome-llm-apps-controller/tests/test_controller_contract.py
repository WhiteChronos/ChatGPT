import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PLUGIN = ROOT / 'plugins' / 'awesome-llm-apps-controller'
SKILL = PLUGIN / 'skills' / 'awesome-llm-apps-controller' / 'SKILL.md'


def _all_controller_text() -> str:
    parts=[SKILL.read_text(encoding='utf-8')]
    refs=SKILL.parent/'references'
    if refs.exists():
        parts += [p.read_text(encoding='utf-8') for p in sorted(refs.glob('*.md'))]
    return '\n'.join(parts)


def test_controller_routes_concrete_families_through_catalog_discovery():
    text=_all_controller_text().lower()
    for term in ['rag','mcp','voice','always-on','generative ui']:
        assert term in text
    assert 'catalog' in text and 'registry/awesome-llm-apps/catalog.json' in text


def test_controller_preserves_routing_precedence():
    text=_all_controller_text()
    assert re.search(r'Superpowers.*ECC.*Matt.*Awesome', text, re.S)


def test_controller_forbids_unsafe_auto_execution():
    text=_all_controller_text().lower()
    for klass in ['credentialled','background_autonomous','self_modifying','external_reference']:
        assert klass in text
    assert 'do not auto-run' in text or 'never auto-run' in text


def test_controller_does_not_claim_examples_are_native_subagents():
    text=_all_controller_text().lower()
    assert 'native codex subagent' in text
    assert 'do not claim' in text or 'never claim' in text


def test_project_graveyard_and_advisor_dispatch_require_explicit_request():
    text=_all_controller_text().lower()
    assert 'project-graveyard' in text and 'explicit user request' in text
    assert 'advisor-orchestrator-worker' in text and 'explicit user request' in text


def test_controller_references_catalog_and_provenance_lock():
    text=_all_controller_text()
    assert 'registry/awesome-llm-apps/catalog.json' in text
    assert 'plugins/awesome-llm-apps-controller/upstream.lock.json' in text


def test_plugin_is_read_interactive_only_without_hooks_or_mcp():
    data=json.loads((PLUGIN/'.codex-plugin'/'plugin.json').read_text(encoding='utf-8'))
    assert data['name']=='awesome-llm-apps-controller'
    assert data['capabilities']==['Interactive','Read']
    assert data.get('hooks',{})=={}
    assert 'mcpServers' not in data and 'mcp_servers' not in data


def test_skill_frontmatter_contains_only_name_and_description():
    text=SKILL.read_text(encoding='utf-8')
    assert text.startswith('---\n')
    end=text.find('\n---\n',4)
    assert end>0
    keys=[]
    for line in text[4:end].splitlines():
        if line and not line.startswith(' ') and ':' in line:
            keys.append(line.split(':',1)[0].strip())
    assert keys==['name','description']
