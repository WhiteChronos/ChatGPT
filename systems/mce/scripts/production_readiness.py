#!/usr/bin/env python3
"""Fail-closed, read-only MCE technical readiness audit.

This checks one workspace, NOT the independent project/SS approval,
GitHub main/CI, FAT/SAT, operational sign-off or PRODUCTION_COMPLETE.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / '.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py'


def _engine():
    spec = importlib.util.spec_from_file_location('mce_workflow_read_only', WF)
    if spec is None or spec.loader is None:
        raise RuntimeError('MCE workflow is not available')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _status(allowed: bool, note: str) -> dict:
    return {'status': 'PASS' if allowed else 'BLOCKED', 'detail': note}


def assess(workspace: Path) -> dict:
    """Review raw SHA evidence; never mutate the workbook or claim acceptance."""
    w = Path(workspace)
    checks = {key: _status(False, 'Not yet verified') for key in (
        'workspace', 'baseline_integrity', 'documented_identity', 'contract',
        'approval_record', 'preliminary_output', 'ooxml_audit')}
    checks['external_engineering_acceptance'] = {
        'status': 'USER_ACTION_REQUIRED',
        'detail': 'Engineering review, relevant FAT/SAT and formal owner sign-off required; never auto-approved.'}
    checks['github_release'] = {
        'status': 'EXTERNAL_VERIFICATION_REQUIRED',
        'detail': 'Verify merged main SHA, current CI and release on GitHub independently.'}

    def finish():
        technical = all(checks[k]['status'] == 'PASS' for k in (
            'workspace', 'baseline_integrity', 'documented_identity', 'contract',
            'approval_record', 'preliminary_output', 'ooxml_audit'))
        return {
            'product': 'MCE_INDEPENDENTE',
            'status': 'TECHNICAL_READY_FOR_ENGINEERING_ACCEPTANCE' if technical else 'BLOCKED',
            'production_complete': False,
            'checks': checks,
            'note': 'Automated technical readiness is not an engineering release or operating acceptance.'}

    if not w.is_dir() or not (w / 'state.json').is_file():
        checks['workspace'] = _status(False, 'No initialized MCE workspace/state.json was provided')
        return finish()
    checks['workspace'] = _status(True, 'Initialized workspace found')
    try:
        core = _engine()
        state = core.load_state(w)
        sources = state.get('sources')
        if not isinstance(sources, list) or not sources:
            raise ValueError('Source inventory must be nonempty')
        manifest_sha = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
        if manifest_sha != state.get('source_manifest_sha256'):
            raise ValueError('Source inventory digest does not match state')
        checks['baseline_integrity'] = _status(True, 'Workbook and source hashes match inventory')
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError, RuntimeError) as exc:
        checks['baseline_integrity'] = _status(False, 'Master/source/inventory verification failed')
        return finish()

    try:
        analysis = core.readjson(w / 'analysis.json')
        if not isinstance(analysis, dict):
            raise ValueError('Analysis must be a JSON object')
        if analysis.get('source_manifest_sha256') != state['source_manifest_sha256']:
            raise ValueError('Analysis is not bound to source manifest')
        for field in ('project', 'ss'):
            identifier = analysis.get(field, '')
            if (not isinstance(identifier, str) or not identifier.strip() or
                identifier.upper().startswith(('NAO IDENTIFICAD', 'A DEFINIR'))):
                raise ValueError('Project and SS require documented identities')
            proof = analysis.get('identity_evidence', {}).get(field)
            if not isinstance(proof, dict) or identifier not in proof.get('verbatim_excerpt', ''):
                raise ValueError('Documentary identity evidence missing')
            core.validate_finding(w, state, {**proof, 'classification': 'DOCUMENTADO'})
        checks['documented_identity'] = _status(True, 'Project/SS evidence bound to inventoried sources')
    except (ValueError, OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError):
        checks['documented_identity'] = _status(False, 'Documentary project/SS evidence not verified')

    try:
        contract = core.verify_contract(w, state)
        checks['contract'] = _status(True, 'Approved workbook contract; <=50 causes per sheet')
    except (ValueError, OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError):
        contract = None
        checks['contract'] = _status(False, 'Approved model and protected-cell contract not verified')

    approval = state.get('approval')
    valid_approval = (isinstance(approval, dict) and
        approval.get('decision') == 'AUTORIZO_ELABORACAO_MCE' and
        isinstance(approval.get('approver'), str) and bool(approval['approver'].strip()) and
        approval.get('source_manifest_sha256') == state['source_manifest_sha256'])
    checks['approval_record'] = _status(valid_approval, 'Authorization record bound to sources (identity not independently attested)' if valid_approval else 'No valid source-bound authorization record')

    out = w / 'output' / 'MCE_PRELIMINAR.xlsx'
    try:
        if state.get('status') != 'MCE_PRELIMINAR_PARA_REVISAO':
            raise ValueError('Output phase not reached')
        if not out.is_file() or core.digest(out) != state.get('output_sha256'):
            raise ValueError('Preliminary output missing or modified')
        checks['preliminary_output'] = _status(True, 'Preliminary derived workbook matches inventory SHA')
    except (ValueError, OSError, TypeError):
        checks['preliminary_output'] = _status(False, 'No intact preliminary derived workbook')

    if contract and checks['preliminary_output']['status'] == 'PASS':
        try:
            diffs = core.readjson(w / 'ALTERACOES_MCE.json')
            saved = core.readjson(w / 'AUDITORIA_MCE.json')
            if not isinstance(diffs, list) or not isinstance(saved, dict) or saved.get('passed') is not True:
                raise ValueError('Saved audit is absent or unsuccessful')
            expected = [{'sheet':x['sheet'], 'cell':x['cell'], 'new_text':x['after']} for x in diffs]
            current = core.audit(core.master_path(w), out, expected, contract)
            if not current.get('passed') or current.get('differences') != diffs:
                raise ValueError('Fresh OOXML diff is not identical to recorded audit')
            checks['ooxml_audit'] = _status(True, 'Fresh audit confirms text-only modifications and structural invariants')
        except (ValueError, OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError):
            checks['ooxml_audit'] = _status(False, 'Fresh OOXML audit failed or cannot be reproduced')
    else:
        checks['ooxml_audit'] = _status(False, 'Approved model and preliminary output required for fresh audit')
    return finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', required=True, type=Path)
    args = parser.parse_args()
    report = assess(args.workspace)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report['status'] == 'TECHNICAL_READY_FOR_ENGINEERING_ACCEPTANCE' else 2


if __name__ == '__main__':
    raise SystemExit(main())
