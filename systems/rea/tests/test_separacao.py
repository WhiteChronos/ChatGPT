"""TDD red: REA must have zero MCE dependencies, methods or named products."""
from pathlib import Path
import sys
import json
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from bridge import ReaBridge
from internal_engine import InternalEngine

def test_rea_tools_independent(tmp_path):
    bridge=ReaBridge(tmp_path,root)
    names={t['name'] for t in bridge.handle({'jsonrpc':'2.0','id':1,'method':'tools/list'})['result']['tools']}
    assert len(names)>=5
    assert 'rea_pid_preview' not in names
    assert 'rea_mce_gate' not in names
    assert 'rea_internal_analyze' in names
    assert 'rea_arena_compare' in names
    assert not any('mce' in name.lower() for name in names)
    assert 'REA' in bridge.handle({'jsonrpc':'2.0','id':1,'method':'initialize'})['result']['serverInfo']['name'].upper()

def test_no_mce_import_or_filenames():
    for path in (root/'src').rglob('*.py'):
        data=path.read_text().lower()
        assert 'mce' not in data, (str(path), 'MCE token')
    assert not (root/'.agents/skills/engenharia-mce-projeto').exists()

def test_generic_engine(tmp_path):
    (tmp_path/'source.py').write_text('import os\n')
    bridge=ReaBridge(tmp_path,root)
    report=InternalEngine(bridge).analyze('.',10)
    assert report['coverage']['files_analyzed']==1
    assert 'mce' not in json.dumps(report).lower()
    comparison=InternalEngine(bridge).compare_approaches('source_analysis','high')
    assert 'mce' not in json.dumps(comparison).lower()

def test_catalog_is_explicit_and_independent(tmp_path):
    (tmp_path/'rank.json').write_text(json.dumps({'reviewed': [{'repo':'example/a','score_editorial':70,'license':'MIT','head':'x'}],'captured_at':'2026-10-28'}))
    bridge=ReaBridge(tmp_path,root)
    result=bridge._call('rea_repositories_top10',{'catalog':'rank.json'})
    assert len(result['finalists'])==1
    assert result['finalists'][0]['repo']=='example/a'
    assert result['automatically_installed'] is False
