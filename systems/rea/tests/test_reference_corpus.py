"""Deterministic, synthetic reference cases for REA's static analyzer.

No code from the reference corpus is executed or sent to a model.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from bridge import ReaBridge
from internal_engine import InternalEngine

CORPUS = Path(__file__).parent / 'fixtures' / 'rea_static_golden_v1.json'


def _case(tmp_path):
    case = json.loads(CORPUS.read_text(encoding='utf-8'))
    for name, source in case['source_by_path'].items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding='utf-8')
    bridge = ReaBridge(tmp_path, ROOT)
    return case, bridge, InternalEngine(bridge)


def test_golden_static_graph_hashes_and_review_only_flags(tmp_path):
    case, bridge, engine = _case(tmp_path)
    result = engine.analyze('.', 100)
    assert result['engine'] == 'REA_INDEPENDENT_STATIC_ANALYZER_V1'
    assert result['coverage']['status'] == 'COMPLETE_WITHIN_SCOPE'
    assert result['coverage']['files_analyzed'] == len(case['source_by_path'])
    assert result['upstream_rea_executed'] is False
    assert result['automatic_decision_approval'] is False
    edges = [{'source': e['source'], 'target': e['target']} for e in result['graph']['edges']]
    assert sorted(edges, key=lambda e: (e['source'], e['target'])) == case['expected_edges']
    findings = [{'file': f['file'], 'rule_id': f['rule_id'],
                 'severity': f['severity'], 'classification': f['classification']}
                for f in result['findings']]
    assert findings == case['expected_findings']
    for node in result['graph']['nodes']:
        expected_hash = hashlib.sha256((tmp_path / node['file']).read_bytes()).hexdigest()
        assert node['sha256'] == expected_hash
    assert case['sentinel_not_to_disclose'] not in json.dumps(result)


def test_golden_access_boundaries_and_sensitive_filters(tmp_path):
    case, bridge, engine = _case(tmp_path)
    (tmp_path / '.env').write_text('SYNTHETIC_SECRET=1', encoding='utf-8')
    protected = tmp_path / 'secrets' / 'password.py'
    protected.parent.mkdir()
    protected.write_text('SYNTHETIC_SECRET=1', encoding='utf-8')
    for denied in ('.env', 'secrets/password.py', '../outside.py'):
        with pytest.raises(ValueError):
            bridge._source_inspect({'file': denied})
    inventory = bridge._project_inventory({'directory': '.'})
    paths = {row['path'] for row in inventory['files']}
    assert paths == set(case['source_by_path'])
    assert 'SYNTHETIC_SECRET' not in json.dumps(engine.analyze('.', 100))


def test_golden_bounded_coverage_is_not_reported_complete(tmp_path):
    case, bridge, engine = _case(tmp_path)
    result = engine.analyze('.', 2)
    assert result['coverage']['status'] == 'PARTIAL_LIMIT'
    assert result['coverage']['files_analyzed'] == 2
    assert result['coverage']['truncated'] is True
    assert result['automatic_decision_approval'] is False
