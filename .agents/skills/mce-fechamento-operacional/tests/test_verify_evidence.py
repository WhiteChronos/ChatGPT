import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

HERE = Path(__file__).resolve().parents[1]
SCRIPT = HERE / 'scripts' / 'verify_evidence.py'


def load():
    spec = importlib.util.spec_from_file_location('verify_evidence', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evidence(root, filename='docs/projeto.txt', data=b'PROJETO SS DEMO'):
    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {'product': 'MCE_INDEPENDENTE', 'files': [{'path': filename, 'sha256': hashlib.sha256(data).hexdigest()}]}


def test_valid_manifest_does_not_claim_production(tmp_path):
    manifest = evidence(tmp_path)
    result = load().assess(tmp_path, manifest)
    assert result['status'] == 'ARTIFACT_INTEGRITY_PASS'
    assert result['files_verified'] == 1
    assert result['production_complete'] is False
    assert result['external_gates']['engineering_acceptance'] == 'USER_ACTION_REQUIRED'


def test_wrong_hash_fails_closed(tmp_path):
    manifest = evidence(tmp_path)
    manifest['files'][0]['sha256'] = 'f' * 64
    result = load().assess(tmp_path, manifest)
    assert result['status'] == 'BLOCKED'
    assert result['files_verified'] == 0


@pytest.mark.parametrize('path', ['../escape.txt', '/etc/passwd', 'docs/../../escape.txt', './docs/projeto.txt'])
def test_paths_must_be_canonical_relative(tmp_path, path):
    manifest = evidence(tmp_path)
    manifest['files'][0]['path'] = path
    assert load().assess(tmp_path, manifest)['status'] == 'BLOCKED'


def test_symlink_is_rejected(tmp_path):
    outside = tmp_path.parent / (tmp_path.name + '.external')
    outside.write_bytes(b'PRIVATE')
    link = tmp_path / 'source'
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip('symlink unsupported')
    manifest = {'product': 'MCE_INDEPENDENTE', 'files': [{'path': 'source', 'sha256': hashlib.sha256(outside.read_bytes()).hexdigest()}]}
    assert load().assess(tmp_path, manifest)['status'] == 'BLOCKED'
    outside.unlink()


def test_duplicate_entries_rejected(tmp_path):
    manifest = evidence(tmp_path)
    manifest['files'].append(dict(manifest['files'][0]))
    assert load().assess(tmp_path, manifest)['status'] == 'BLOCKED'


@pytest.mark.parametrize('manifest', [{}, {'product':'REA_INDEPENDENTE','files':[]}, {'product':'MCE_INDEPENDENTE','files':[]}, {'product':'MCE_INDEPENDENTE','files':[{'path':'missing','sha256':'0'*64}]}])
def test_invalid_evidence_rejected(tmp_path, manifest):
    assert load().assess(tmp_path, manifest)['status'] == 'BLOCKED'


def test_cli_returns_failure_and_does_not_modify_input(tmp_path):
    manifest = evidence(tmp_path)
    (tmp_path / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    before = hashlib.sha256((tmp_path / 'docs/projeto.txt').read_bytes()).hexdigest()
    call = subprocess.run([sys.executable, str(SCRIPT), '--root', str(tmp_path), '--manifest', str(tmp_path / 'manifest.json')], capture_output=True, text=True)
    assert call.returncode == 0
    assert json.loads(call.stdout)['status'] == 'ARTIFACT_INTEGRITY_PASS'
    assert hashlib.sha256((tmp_path / 'docs/projeto.txt').read_bytes()).hexdigest() == before
    (tmp_path / 'manifest.json').write_text('{', encoding='utf-8')
    invalid = subprocess.run([sys.executable, str(SCRIPT), '--root', str(tmp_path), '--manifest', str(tmp_path / 'manifest.json')], capture_output=True, text=True)
    assert invalid.returncode == 2
    assert json.loads(invalid.stdout)['status'] == 'BLOCKED'
