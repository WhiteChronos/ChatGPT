import hashlib
import importlib.util
from pathlib import Path
import pytest
from openpyxl import Workbook

p = Path(__file__).resolve().parents[1] / 'scripts' / 'mce_pv_controller.py'
spec = importlib.util.spec_from_file_location('mce_pv_controller', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture(tmp_path):
    book = Workbook()
    book.active.title = 'FOLHA 1'
    book.active['C8'] = 'Synthetic cause'
    source = tmp_path / 'mce.xlsx'
    book.save(source)
    return source


def test_pv01_copy_only(tmp_path):
    source = fixture(tmp_path)
    digest = mod.sha256(source)
    record = mod.stage(tmp_path, 'mce.xlsx', 'DE-001_MCE_TESTE', digest)
    assert record['filename'] == 'DE-001_MCE_TESTE (PRELIMINAR VERS\u00c3O 01) PV 01.xlsx'
    assert record['pv_number'] == 1
    assert record['engineering_approved'] is False
    assert Path(record['file']).read_bytes() == source.read_bytes()
    assert mod.read_ledger(tmp_path/'pv'/'pv_versions.jsonl', tmp_path/'pv')[0]['digest']


def test_next_pv_requires_change_and_has_chain(tmp_path):
    source = fixture(tmp_path)
    mod.stage(tmp_path, 'mce.xlsx', 'MCE_ALFA', mod.sha256(source))
    with pytest.raises(mod.PVBlocked, match='Sem mudanca'):
        mod.stage(tmp_path, 'mce.xlsx', 'MCE_ALFA', mod.sha256(source))
    wb = Workbook(); wb.active.title='FOLHA 1';wb.active['A1']='updated';wb.save(source)
    r=mod.stage(tmp_path,'mce.xlsx','MCE_ALFA',mod.sha256(source))
    assert r['pv_number']==2
    assert '(PRELIMINAR VERS\u00c3O 02) PV 02.xlsx' in r['filename']
    assert len(mod.read_ledger(tmp_path/'pv'/'pv_versions.jsonl',tmp_path/'pv')) == 2


def test_new_document_restarts_at_pv01(tmp_path):
    src=fixture(tmp_path); s=mod.sha256(src)
    mod.stage(tmp_path,'mce.xlsx','MCE_ALFA',s)
    r=mod.stage(tmp_path,'mce.xlsx','MCE_BETA',s)
    assert r['pv_number']==1


@pytest.mark.parametrize('name', ['../escape','bad/name','bad\\name','A (PRELIMINAR VERS\u00c3O 01) PV 01','MCE ', 'abc.xlsx/'])
def test_bad_names_fail(tmp_path,name):
    src=fixture(tmp_path)
    with pytest.raises(mod.PVBlocked):mod.stage(tmp_path,'mce.xlsx',name,mod.sha256(src))


def test_prevent_path_escape_and_sha_error(tmp_path):
    src=fixture(tmp_path)
    with pytest.raises(mod.PVBlocked):mod.stage(tmp_path,'../outside.xlsx','ABC',mod.sha256(src))
    with pytest.raises(mod.PVBlocked):mod.stage(tmp_path,'mce.xlsx','ABC','0'*64)


def test_detect_tampered_ledger(tmp_path):
    src=fixture(tmp_path)
    mod.stage(tmp_path,'mce.xlsx','ABC',mod.sha256(src))
    ledger=tmp_path/'pv'/'pv_versions.jsonl'
    ledger.write_text(ledger.read_text().replace('PRELIMINAR_NAO_HOMOLOGADA', 'APROVADO'),encoding='utf-8')
    with pytest.raises(mod.PVBlocked):mod.stage(tmp_path,'mce.xlsx','ABC',mod.sha256(src))


def test_detect_tampered_xlsx(tmp_path):
    src=fixture(tmp_path)
    r=mod.stage(tmp_path,'mce.xlsx','ABC',mod.sha256(src))
    Path(r['file']).write_bytes(b'corrupt')
    with pytest.raises(mod.PVBlocked):mod.read_ledger(tmp_path/'pv'/'pv_versions.jsonl',tmp_path/'pv')


def test_pv_filename_parser():
    assert mod.parse_pv_filename('MCE_ADM (PRELIMINAR VERS\u00c3O 01) PV 01.xlsx') == ('MCE_ADM',1)
    with pytest.raises(mod.PVBlocked):mod.parse_pv_filename('MCE_ADM (PRELIMINAR VERS\u00c3O 01) PV 02.xlsx')
    with pytest.raises(mod.PVBlocked):mod.parse_pv_filename('MCE_ADM (PRELIMINAR VERS\u00c3O 00) PV 00.xlsx')
