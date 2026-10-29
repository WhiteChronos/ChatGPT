"""TDD regression for REA_INDEPENDENTE independent SQLite memory."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/rea_memory.py'

def load():
    spec = importlib.util.spec_from_file_location('memory_test_rea', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def fresh(tmp_path):
    mod = load()
    db = tmp_path / 'rea-private.sqlite3'
    assert mod.init(db)['event_count'] == 0
    return mod, db

def test_initialize_and_empty_verify(tmp_path):
    m, db = fresh(tmp_path)
    assert m.init(db)['product'] == m.PRODUCT
    assert m.verify(db)['status'] == 'INTEGRITY_PASS'

def test_persistent_history_and_linked_events(tmp_path):
    m, db = fresh(tmp_path)
    one = m.append(db, 'DECISION', 'Revisao pendente', {'approved': False})
    two = load().append(db, 'PENDENCY', 'Host pendente', {'status': 'BLOCKED'})
    result = m.verify(db)
    assert result['event_count'] == 2
    assert result['head_sha256'] == two['event_sha256']
    assert result['head_sha256'] != one['event_sha256']
    assert result['by_kind']['DECISION'] == 1
    assert result['production_complete'] is False

def test_sql_injection_remains_data(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', "'; DROP TABLE memory_events; --", {'text': 'UNION SELECT 1'})
    assert m.verify(db)['event_count'] == 1

def test_history_is_append_only(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', 'Original', {})
    with sqlite3.connect(db) as con:
        with pytest.raises(sqlite3.DatabaseError):
            con.execute('UPDATE memory_events SET subject=?', ('modified',))
        with pytest.raises(sqlite3.DatabaseError):
            con.execute('DELETE FROM memory_events')

def test_tampering_or_trigger_removal_is_detected(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', 'Original', {})
    with sqlite3.connect(db) as con:
        con.execute('DROP TRIGGER events_no_update')
        con.execute('UPDATE memory_events SET subject=?', ('modified',))
    with pytest.raises(ValueError):
        m.verify(db)

def test_wrong_product_rejected(tmp_path):
    m, db = fresh(tmp_path)
    with sqlite3.connect(db) as con:
        con.execute("UPDATE system_meta SET value='WRONG_PRODUCT' WHERE key='product'")
    with pytest.raises(ValueError):
        m.verify(db)

def test_secrets_and_invalid_events_blocked(tmp_path):
    m, db = fresh(tmp_path)
    with pytest.raises(ValueError):
        m.append(db, 'NOTE', 'X', {'api_key': 'NEVER'})
    with pytest.raises(ValueError):
        m.append(db, 'NOTE', 'X', {'text': '-----BEGIN PRIVATE KEY-----'})
    with pytest.raises(ValueError):
        m.append(db, 'APPROVED', 'X', {})
    with pytest.raises(ValueError):
        m.append(db, 'EVIDENCE', 'X', {}, source_sha256='wrong')
    assert m.verify(db)['event_count'] == 0

def test_datasheet_redaction_full_export_and_no_overwrite(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'EVIDENCE', 'Arquivo aprovado fora do banco',
             {'internal_note':'Private detail'}, source_sha256='a'*64)
    summary = tmp_path / 'datasheet-summary.json'
    full = tmp_path / 'datasheet-full.json'
    m.datasheet(db, summary)
    m.datasheet(db, full, full=True)
    a = json.loads(summary.read_text())
    b = json.loads(full.read_text())
    assert 'detail' not in a['events'][0]
    assert b['events'][0]['detail']['internal_note'] == 'Private detail'
    assert a['product'] == m.PRODUCT
    assert a['head_sha256'] == m.verify(db)['head_sha256']
    with pytest.raises(ValueError):
        m.datasheet(db, summary)

def test_backup_restore_in_new_destination(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', 'Persistir', {'count': 1})
    back = tmp_path / 'backup.sqlite3'
    meta = m.backup(db, back)
    assert meta['backup_sha256'] == hashlib.sha256(back.read_bytes()).hexdigest()
    restored = tmp_path / 'restored.sqlite3'
    m.restore(back, restored)
    assert m.verify(db)['head_sha256'] == m.verify(restored)['head_sha256']
    with pytest.raises(ValueError):
        m.restore(back, restored)

def test_forbid_repo_path_and_symlink(tmp_path):
    m, db = fresh(tmp_path)
    with pytest.raises(ValueError):
        m.init(ROOT / 'datacenter' / 'private.sqlite3')
    sym = tmp_path / 'alias.sqlite3'
    try:
        sym.symlink_to(db)
    except OSError:
        pytest.skip('Symlink unavailable')
    with pytest.raises(ValueError):
        m.verify(sym)

def test_cli_exit_codes(tmp_path):
    m, db = fresh(tmp_path)
    ok = subprocess.run([sys.executable,str(SCRIPT),'--db',str(db),'verify'],capture_output=True,text=True)
    assert ok.returncode == 0
    assert json.loads(ok.stdout)['production_complete'] is False
    denied = subprocess.run([sys.executable,str(SCRIPT),'--db',str(tmp_path/'missing.sqlite'),'verify'],capture_output=True,text=True)
    assert denied.returncode == 2
    assert json.loads(denied.stdout)['status'] == 'BLOCKED'


def test_digest_tampering_after_reinstating_trigger(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', 'Original', {})
    with sqlite3.connect(db) as con:
        trigger_sql = con.execute("SELECT sql FROM sqlite_master WHERE type='trigger' AND name='events_no_update'").fetchone()[0]
        con.execute('DROP TRIGGER events_no_update')
        con.execute('UPDATE memory_events SET subject=?', ('Modified',))
        con.execute(trigger_sql)
    with pytest.raises(ValueError, match='digest'):
        m.verify(db)

def test_no_other_system_dependency():
    source = SCRIPT.read_text()
    assert 'from systems.' not in source and 'import systems.' not in source
    assert 'systems/mce/' not in source


def test_search_history_without_exporting_payload(tmp_path):
    m, db = fresh(tmp_path)
    m.append(db, 'NOTE', 'Pending integration', {'detail': 'UniqueFindingXYZ'})
    result = m.search(db, 'UniqueFindingXYZ')
    assert len(result['matches']) == 1
    assert 'detail' not in result['matches'][0]
    assert m.search(db, 'NotFound')['matches'] == []
    with pytest.raises(ValueError):
        m.search(db, 'x', limit=99999)


def test_pipeline_records_local_doctor_without_host_claim(tmp_path):
    if not (ROOT/'src/bridge.py').exists():
        pytest.skip('REA bridge is available in GitHub checkout')
    m, db = fresh(tmp_path)
    out = tmp_path/'pipeline-rea.json'
    result = subprocess.run([sys.executable,str(ROOT/'scripts/continuity_pipeline.py'),
                             '--db',str(db),'--datasheet',str(out)],
                            capture_output=True,text=True)
    assert result.returncode == 0, result.stdout+result.stderr
    record = json.loads(result.stdout)
    assert record['host_discovered'] is False
    assert record['live_verified'] is False
    assert m.verify(db)['by_kind']['STATUS'] == 1
    assert out.is_file()
