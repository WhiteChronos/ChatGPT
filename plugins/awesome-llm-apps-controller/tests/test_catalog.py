import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from awesome_llm_apps_catalog import normalize_id, classify_execution, build_catalog, build_summary

FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'upstream'

def test_normalize_id_is_stable_and_source_scoped():
    assert normalize_id('upstream_internal','rag_tutorials/vision_rag') == 'upstream-internal:rag-tutorials-vision-rag'
    assert normalize_id('external_reference','https://example.com/agent') != 'upstream-internal:rag-tutorials-vision-rag'

def test_execution_class_uses_most_restrictive_gate():
    assert classify_execution({'self_modifying':True,'credentials_required':True})['execution_class'] == 'SELF_MODIFYING'
    assert classify_execution({'background_capable':True,'credentials_required':True})['execution_class'] == 'BACKGROUND_AUTONOMOUS'
    assert classify_execution({'mcp_related_paths':['mcp.json'],'credentials_required':True})['execution_class'] == 'MCP_OR_CONNECTOR'

def test_execution_flags_detect_high_stakes_and_credentials():
    risk = classify_execution({'title':'Insurance Claim Live Agent Team','upstream_path':'voice_ai_agents/insurance','env_example_paths':['.env.example']})
    assert risk['credentials_required'] is True
    assert risk['high_stakes_domain'] is True

def test_build_catalog_discovers_internal_skills_apps_and_external_links():
    catalog = build_catalog(FIXTURE, 'deadbeef')
    entries = catalog['entries']
    assert any(e['subtype']=='canonical_skill' and e['title']=='skill-a' for e in entries)
    assert any(e['subtype']=='project_internal_skill' and 'internal-app' in e.get('upstream_path','') for e in entries)
    assert any(e['source_type']=='external_reference' and e['external_url']=='https://github.com/example/external-agent' for e in entries)
    assert not any(e.get('external_url')=='https://sponsor.example.com' for e in entries)
    rag = next(e for e in entries if e.get('upstream_path')=='rag_tutorials/sample-rag')
    assert 'rag_tutorials/sample-rag/requirements.txt' in rag['manifest_paths']
    assert rag['upstream_commit']=='deadbeef'

def test_summary_is_deterministic_and_counts_source_types():
    c1 = build_catalog(FIXTURE,'deadbeef')
    c2 = build_catalog(FIXTURE,'deadbeef')
    assert json.dumps(c1, sort_keys=True) == json.dumps(c2, sort_keys=True)
    summary = build_summary(c1)
    assert summary['by_source_type']['external_reference'] == 1
