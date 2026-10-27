import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / 'pipeline' / 'p0_real_panel_e2e_gate.py'


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def valid_fixture(tmp_path: Path):
    project = '25279'
    panel = 'PN-AUT-001'
    control = tmp_path / 'PN_AUT_01_PROJECT_CONTROL_V1.json'
    root = tmp_path / 'p0_real'
    gap = root / 'INPUT_GAP_REGISTER_CURRENT.json'
    manifest = root / 'PANEL_GEOMETRY_MANIFEST.json'
    result = root / 'P0_REAL_PANEL_E2E_RESULT.json'

    write_json(control, {
        'project_number': project,
        'panel_id': 'PN-AUT-01',
        'status': 'STEP2_PANEL_DEFINITION_FROZEN',
        'downstream_status': 'VALID',
        'previous_project_alias': panel,
    })
    write_json(gap, {
        'project_number': project,
        'panel_id': panel,
        'status': 'CLOSED',
        'open_gaps': [],
    })
    gap_sha = hashlib.sha256(gap.read_bytes()).hexdigest()
    write_json(manifest, {
        'project_number': project,
        'panel_id': panel,
        'status': 'PANEL_GEOMETRY_MANIFEST_FROZEN',
        'step4_status': 'STEP4_LI_LOAD_FROZEN',
        'input_gaps': [],
        'assembly_hash': 'a' * 64,
        'input_gap_register_sha256': gap_sha,
        'source_refs': [
            {'ref_id': 'REF-001', 'sha256': 'b' * 64},
            {'ref_id': 'REF-002', 'sha256': 'c' * 64},
        ],
    })
    manifest_sha = hashlib.sha256(manifest.read_bytes()).hexdigest()
    write_json(result, {
        'project_number': project,
        'panel_id': panel,
        'status': 'PASS',
        'manifest_sha256': manifest_sha,
        'blocking_holds': [],
        'stages': {
            'LI': 'PASS',
            'GEOMETRY': 'PASS',
            'CAD': 'PASS',
            'VIEWS': 'PASS',
            'QA': 'PASS',
        },
    })
    return project, panel, control, root, gap, manifest, result


def run_gate(project, panel, control, root, report=None):
    cmd = [
        sys.executable, str(GATE),
        '--project-number', project,
        '--panel-id', panel,
        '--project-control', str(control),
        '--artifact-root', str(root),
    ]
    if report:
        cmd += ['--report', str(report)]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding='utf-8')


def parsed(run):
    return json.loads(run.stdout)


def test_passes_only_when_all_gates_are_closed_and_manifest_hash_matches(tmp_path):
    project, panel, control, root, *_ = valid_fixture(tmp_path)
    report = tmp_path / 'report.json'
    run = run_gate(project, panel, control, root, report)
    assert run.returncode == 0, run.stderr + run.stdout
    payload = parsed(run)
    assert payload['status'] == 'PASS'
    assert payload['blocking_holds'] == []
    assert report.is_file()
    assert json.loads(report.read_text(encoding='utf-8'))['status'] == 'PASS'


def test_reopened_step2_is_a_hard_hold(tmp_path):
    project, panel, control, root, *_ = valid_fixture(tmp_path)
    data = json.loads(control.read_text(encoding='utf-8'))
    data['status'] = 'STEP2_REOPENED_SOURCE_RECONCILIATION_PENDING'
    data['downstream_status'] = 'INVALIDATED_FROM_PREVIOUS_R06_ASSUMPTIONS'
    write_json(control, data)
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    assert 'STEP2_NOT_FROZEN' in parsed(run)['blocking_holds']
    assert 'DOWNSTREAM_INVALIDATED' in parsed(run)['blocking_holds']


def test_open_input_gap_is_a_hard_hold(tmp_path):
    project, panel, control, root, gap, *_ = valid_fixture(tmp_path)
    data = json.loads(gap.read_text(encoding='utf-8'))
    data['status'] = 'OPEN'
    data['open_gaps'] = [{'gap_id': 'G02', 'status': 'OPEN'}]
    write_json(gap, data)
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    assert 'INPUT_GAPS_OPEN' in parsed(run)['blocking_holds']


def test_stale_e2e_result_manifest_hash_is_a_hard_hold(tmp_path):
    project, panel, control, root, *_, result = valid_fixture(tmp_path)
    data = json.loads(result.read_text(encoding='utf-8'))
    data['manifest_sha256'] = 'd' * 64
    write_json(result, data)
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    assert 'P0_RESULT_STALE_MANIFEST' in parsed(run)['blocking_holds']


def test_failed_p0_stage_is_a_hard_hold(tmp_path):
    project, panel, control, root, *_, result = valid_fixture(tmp_path)
    data = json.loads(result.read_text(encoding='utf-8'))
    data['stages']['QA'] = 'HOLD'
    data['status'] = 'HOLD'
    data['blocking_holds'] = ['HOLD_FINAL_IMAGE_SCALE']
    write_json(result, data)
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    payload = parsed(run)
    assert 'P0_STATUS_NOT_PASS' in payload['blocking_holds']
    assert 'P0_STAGE_QA_NOT_PASS' in payload['blocking_holds']
    assert 'P0_DECLARED_BLOCKING_HOLDS' in payload['blocking_holds']


def test_missing_manifest_is_a_hard_hold(tmp_path):
    project, panel, control, root, _, manifest, _ = valid_fixture(tmp_path)
    manifest.unlink()
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    assert 'MISSING_PANEL_GEOMETRY_MANIFEST' in parsed(run)['blocking_holds']


def test_stale_gap_register_link_is_a_hard_hold(tmp_path):
    project, panel, control, root, gap, manifest, result = valid_fixture(tmp_path)
    gap_data = json.loads(gap.read_text(encoding='utf-8'))
    gap_data['review_note'] = 'changed after manifest freeze'
    write_json(gap, gap_data)
    run = run_gate(project, panel, control, root)
    assert run.returncode == 2
    assert 'MANIFEST_STALE_INPUT_GAP_REGISTER' in parsed(run)['blocking_holds']


def test_workflow_is_manual_reusable_and_fail_closed():
    workflow = ROOT / '.github' / 'workflows' / 'p0-real-panel-e2e.yml'
    text = workflow.read_text(encoding='utf-8')
    assert 'workflow_dispatch:' in text
    assert 'workflow_call:' in text
    assert 'permissions:\n  contents: read' in text
    assert 'python pipeline/p0_real_panel_e2e_gate.py' in text
    assert 'python pipeline/panel_3d_geometry_gate.py' in text
    assert 'validate_multiview_manifest.py' in text
    assert 'verify_final_image_manifest.py' in text
    assert 'if: always()' in text
    assert 'actions/upload-artifact@v4' in text
    assert 'continue-on-error: true' not in text
