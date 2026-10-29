"""TDD: um workspace MCE nao equivale a homologacao/100% producao."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / '.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'
SPEC = importlib.util.spec_from_file_location('mce_production_readiness', ROOT / 'scripts/production_readiness.py')


def load_release_module():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module


def init_workspace(tmp_path, *, classification='MODELO_APROVADO'):
    master = tmp_path / 'master.xlsx'
    Workbook().save(master)
    doc = tmp_path / 'fonte.txt'
    doc.write_text('Projeto PROJETO-TESTE, SS-TESTE, somente fonte sintetica\n', encoding='utf-8')
    ws = tmp_path / 'ws'
    run = subprocess.run([sys.executable, str(WF), 'init', '--workspace', str(ws), '--master', str(master),
        '--classification', classification, '--sources', str(doc)], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    return ws, master


def test_requires_a_real_workspace(tmp_path):
    report = load_release_module().assess(tmp_path / 'inexistente')
    assert report['status'] == 'BLOCKED'
    assert report['checks']['workspace']['status'] == 'BLOCKED'
    assert report['production_complete'] is False


def test_inventory_does_not_mean_engineering_release(tmp_path):
    ws, master = init_workspace(tmp_path)
    before = hashlib.sha256(master.read_bytes()).hexdigest()
    report = load_release_module().assess(ws)
    assert report['checks']['baseline_integrity']['status'] == 'PASS'
    assert report['checks']['contract']['status'] == 'BLOCKED'
    assert report['checks']['preliminary_output']['status'] == 'BLOCKED'
    assert report['status'] == 'BLOCKED'
    assert report['production_complete'] is False
    assert hashlib.sha256(master.read_bytes()).hexdigest() == before
    assert not (ws / 'output/MCE_PRELIMINAR.xlsx').exists()


def test_tampered_master_fails_closed(tmp_path):
    ws, _ = init_workspace(tmp_path)
    (ws / 'base/modelo.xlsx').write_bytes(b'modificado')
    report = load_release_module().assess(ws)
    assert report['checks']['baseline_integrity']['status'] == 'BLOCKED'
    assert report['production_complete'] is False


def test_forged_approval_or_status_cannot_bypass_audit(tmp_path):
    ws, _ = init_workspace(tmp_path)
    state_path = ws / 'state.json'
    state = json.loads(state_path.read_text(encoding='utf-8'))
    state['status'] = 'MCE_PRELIMINAR_PARA_REVISAO'
    state['approval'] = {'approver': 'Pessoa teste', 'decision': 'AUTORIZO_ELABORACAO_MCE',
                         'source_manifest_sha256': state['source_manifest_sha256']}
    state_path.write_text(json.dumps(state), encoding='utf-8')
    report = load_release_module().assess(ws)
    assert report['checks']['preliminary_output']['status'] == 'BLOCKED'
    assert report['checks']['ooxml_audit']['status'] == 'BLOCKED'
    assert report['production_complete'] is False


def test_approval_cannot_be_claimed_automatically(tmp_path):
    ws, _ = init_workspace(tmp_path)
    report = load_release_module().assess(ws)
    assert report['checks']['external_engineering_acceptance']['status'] == 'USER_ACTION_REQUIRED'
    assert report['production_complete'] is False
    assert 'TECHNICAL' not in report['status']


def test_corrupt_state_is_blocked_instead_of_crashing(tmp_path):
    ws, _ = init_workspace(tmp_path)
    (ws / 'state.json').write_text('[]', encoding='utf-8')
    report = load_release_module().assess(ws)
    assert report['status'] == 'BLOCKED'
    assert report['production_complete'] is False


def test_corrupt_contract_is_blocked_instead_of_crashing(tmp_path):
    ws, _ = init_workspace(tmp_path)
    (ws / 'contract.json').write_text('[]', encoding='utf-8')
    report = load_release_module().assess(ws)
    assert report['checks']['contract']['status'] == 'BLOCKED'
    assert report['production_complete'] is False


def test_invalid_analysis_type_blocks_without_exception(tmp_path):
    ws, _ = init_workspace(tmp_path)
    (ws / 'analysis.json').write_text('[]', encoding='utf-8')
    report = load_release_module().assess(ws)
    assert report['checks']['documented_identity']['status'] == 'BLOCKED'
    assert report['production_complete'] is False
