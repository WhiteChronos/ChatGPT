import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / 'plugins' / 'awesome-llm-apps-controller' / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from awesome_llm_apps_catalog import classify_execution, normalize_id

SCHEMA = ROOT / 'registry' / 'awesome-llm-apps' / 'catalog.schema.json'


def test_normalize_id_is_stable_and_source_scoped():
    assert normalize_id('upstream_internal', 'rag_tutorials/vision_rag') == (
        'upstream-internal:rag-tutorials-vision-rag'
    )
    assert normalize_id('external_reference', 'https://example.com/agent') != (
        'upstream-internal:rag-tutorials-vision-rag'
    )


def test_execution_flags_classify_background_credentials_and_high_stakes():
    entry = {
        'title': 'Insurance Claim Live Agent Team',
        'upstream_path': 'voice_ai_agents/insurance_claim_live_agent_team',
        'manifest_paths': ['.env.example'],
        'mcp_related_paths': [],
    }
    risk = classify_execution(entry)
    assert risk['credentials_required'] is True
    assert risk['high_stakes_domain'] is True


def test_schema_requires_stable_identity_and_execution_fields():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    required = set(schema['$defs']['entry']['required'])
    for field in ['id', 'source_type', 'category', 'execution_class', 'upstream_commit']:
        assert field in required


def test_execution_class_uses_most_restrictive_gate():
    assert classify_execution({'self_modifying': True, 'credentials_required': True})['execution_class'] == 'SELF_MODIFYING'
    assert classify_execution({'background_capable': True, 'credentials_required': True})['execution_class'] == 'BACKGROUND_AUTONOMOUS'
    assert classify_execution({'mcp_related_paths': ['mcp.json'], 'credentials_required': True})['execution_class'] == 'MCP_OR_CONNECTOR'


def test_high_stakes_is_orthogonal_to_execution_class():
    risk = classify_execution({'title': 'Medical diagnosis assistant'})
    assert risk['high_stakes_domain'] is True
    assert risk['execution_class'] == 'REFERENCE_ONLY'


from awesome_llm_apps_catalog import build_catalog, build_summary, extract_external_references


def _write(path: Path, text: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def _discovery_fixture(tmp_path: Path) -> Path:
    root = tmp_path / 'upstream'
    _write(root / 'LICENSE', 'Apache License Version 2.0')
    _write(root / 'README.md', '''# Fixture

### Advanced AI Agents
- [External Useful](https://github.com/example/external-agent) - independent app
- [Local Agent](starter_ai_agents/simple_agent/)

## Thanks to our sponsors
- [Sponsor](https://sponsor.example/)

## Documentation
- [Docs](https://docs.example.com/)
''')
    _write(root / 'starter_ai_agents' / 'simple_agent' / 'README.md', '# Simple Agent')
    _write(root / 'starter_ai_agents' / 'simple_agent' / 'requirements.txt', 'openai\n')
    _write(root / 'starter_ai_agents' / 'simple_agent' / 'LICENSE.custom', 'Custom license')
    _write(root / 'starter_ai_agents' / 'simple_agent' / 'nested' / 'component' / 'README.md', '# Nested Component')
    _write(root / 'starter_ai_agents' / 'simple_agent' / 'nested' / 'component' / 'package.json', '{}')
    _write(root / 'generative_ui_agents' / 'ui_app' / 'README.md', '# UI App')
    _write(root / 'generative_ui_agents' / 'ui_app' / 'skills' / 'local' / 'SKILL.md', '---\nname: local\n---\n')
    _write(root / 'future_agents' / 'future_app' / 'README.md', '# Future App')
    _write(root / 'agent_skills' / 'canonical-one' / 'SKILL.md', '---\nname: canonical-one\n---\n')
    _write(root / 'agent_skills' / 'registry.json', json.dumps({'version': 1, 'skills': [{'name': 'canonical-one', 'path': 'agent_skills/canonical-one', 'license': 'Apache-2.0'}]}))
    return root


def test_discover_attaches_nested_manifests_to_nearest_qualifying_entry(tmp_path):
    catalog = build_catalog(_discovery_fixture(tmp_path), 'abc1234')
    by_path = {e['upstream_path']: e for e in catalog['entries'] if e['source_type'] == 'upstream_internal'}
    parent = by_path['starter_ai_agents/simple_agent']
    nested = by_path['starter_ai_agents/simple_agent/nested/component']
    assert 'starter_ai_agents/simple_agent/requirements.txt' in parent['manifest_paths']
    assert 'starter_ai_agents/simple_agent/nested/component/package.json' in nested['manifest_paths']
    assert 'starter_ai_agents/simple_agent/nested/component/package.json' not in parent['manifest_paths']


def test_discover_canonical_and_project_internal_skills(tmp_path):
    catalog = build_catalog(_discovery_fixture(tmp_path), 'abc1234')
    assert any(e['subtype'] == 'canonical_skill' and e['upstream_path'] == 'agent_skills/canonical-one' for e in catalog['entries'])
    ui = next(e for e in catalog['entries'] if e['upstream_path'] == 'generative_ui_agents/ui_app')
    assert 'generative_ui_agents/ui_app/skills/local/SKILL.md' in ui['skill_paths']
    assert any(s.get('subtype') == 'project_internal_skill' for s in catalog.get('components', []))


def test_external_reference_only_from_recognized_app_heading():
    readme = '''### Advanced AI Agents
- [Useful](https://github.com/example/useful-agent)

## Thanks to our sponsors
- [Sponsor](https://sponsor.example/)

## Documentation
- [Docs](https://docs.example.com/)
'''
    refs = extract_external_references(readme, 'abc1234')
    assert [r['external_url'] for r in refs] == ['https://github.com/example/useful-agent']
    assert refs[0]['source_type'] == 'external_reference'
    assert refs[0]['license_status'] == 'UNVERIFIED'
    assert refs[0]['execution_class'] == 'REFERENCE_ONLY'


def test_discover_future_top_level_root_and_nearest_license(tmp_path):
    catalog = build_catalog(_discovery_fixture(tmp_path), 'abc1234')
    future = next(e for e in catalog['entries'] if e['upstream_path'] == 'future_agents/future_app')
    assert future['source_type'] == 'upstream_internal'
    simple = next(e for e in catalog['entries'] if e['upstream_path'] == 'starter_ai_agents/simple_agent')
    assert simple['license_status'] == 'VERIFIED_SUBPROJECT_LICENSE'
    assert simple['license_paths'] == ['starter_ai_agents/simple_agent/LICENSE.custom']
    nested = next(e for e in catalog['entries'] if e['upstream_path'] == 'starter_ai_agents/simple_agent/nested/component')
    assert nested['license_status'] == 'VERIFIED_SUBPROJECT_LICENSE'
    assert nested['license_paths'] == ['starter_ai_agents/simple_agent/LICENSE.custom']


def test_deterministic_catalog_and_summary_counts(tmp_path):
    root = _discovery_fixture(tmp_path)
    first = build_catalog(root, 'abc1234')
    second = build_catalog(root, 'abc1234')
    assert first == second
    ids = [e['id'] for e in first['entries']]
    assert ids == sorted(ids)
    summary = build_summary(first)
    assert summary['total_entries'] == len(first['entries'])
    assert sum(summary['by_source_type'].values()) == len(first['entries'])
    assert sum(summary['by_category'].values()) == len(first['entries'])
