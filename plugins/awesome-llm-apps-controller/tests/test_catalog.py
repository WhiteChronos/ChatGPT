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
