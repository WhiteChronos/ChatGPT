"""Standalone REA archive verification; no MCE imports, no approval fabrication."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'scripts' / 'release_integrity.py'


def module():
    spec = importlib.util.spec_from_file_location('rea_release_attestor', TARGET)
    assert spec is not None and spec.loader is not None
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def make_zip(path, *, payload=b'read-only metadata', declared=None,
             product='REA_INDEPENDENTE', extra=None, approved=False, git_sha='a' * 40):
    digest = hashlib.sha256(payload).hexdigest()
    manifest = {'system': product, 'git_sha': git_sha,
                'production_approved': approved,
                'files': {'docs/sample.txt': declared or digest}}
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('REA_INDEPENDENTE/docs/sample.txt', payload)
        z.writestr('REA_INDEPENDENTE/manifest.json', json.dumps(manifest))
        if extra:
            z.writestr(extra, b'untrusted')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_valid_archive_integrity_is_not_production_approval(tmp_path):
    z = tmp_path / 'candidate.zip'
    make_zip(z, approved=True)
    report = module().assess_archive(z)
    assert report['status'] == 'INTEGRITY_PASS'
    assert report['checked_files'] == 1
    assert report['production_complete'] is False
    assert report['trusted_digest_match'] is False


def test_outside_trusted_digest_and_source_commit_are_checked(tmp_path):
    z = tmp_path / 'candidate.zip'
    expected = make_zip(z)
    result = module().assess_archive(z, expected_sha256=expected,
                                     expected_git_sha='a' * 40)
    assert result['status'] == 'INTEGRITY_PASS'
    assert result['trusted_digest_match'] is True
    assert result['trusted_commit_match'] is True
    assert result['production_complete'] is False


def test_archive_sha_mismatch_blocks_even_valid_internal_manifest(tmp_path):
    z = tmp_path / 'candidate.zip'
    make_zip(z)
    assert module().assess_archive(z, expected_sha256='0' * 64)['status'] == 'BLOCKED'
    assert module().assess_archive(z, expected_sha256='not-a-hash')['status'] == 'BLOCKED'


def test_source_commit_mismatch_blocks(tmp_path):
    z = tmp_path / 'candidate.zip'
    make_zip(z)
    assert module().assess_archive(z, expected_git_sha='b' * 40)['status'] == 'BLOCKED'


def test_tampered_member_and_wrong_product_block(tmp_path):
    z = tmp_path / 'candidate.zip'
    make_zip(z, declared='0' * 64)
    assert module().assess_archive(z)['status'] == 'BLOCKED'
    make_zip(z, product='MCE_INDEPENDENTE')
    assert module().assess_archive(z)['status'] == 'BLOCKED'


def test_unmanifested_and_unsafe_paths_block(tmp_path):
    z = tmp_path / 'candidate.zip'
    for name in ['REA_INDEPENDENTE/surprise.py', '../secret.py',
                 'REA_INDEPENDENTE/docs/../escape.py',
                 'REA_INDEPENDENTE/docs/./collision.py',
                 'REA_INDEPENDENTE/docs\\escape.py']:
        make_zip(z, extra=name)
        assert module().assess_archive(z)['status'] == 'BLOCKED', name


def test_duplicate_zip_member_and_symlink_block(tmp_path):
    z = tmp_path / 'candidate.zip'
    make_zip(z)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)  # Intentional invalid archive in negative test.
        with zipfile.ZipFile(z, 'a') as f:
            f.writestr('REA_INDEPENDENTE/docs/sample.txt', b'duplicate')
    assert module().assess_archive(z)['status'] == 'BLOCKED'
    make_zip(z)
    info = zipfile.ZipInfo('REA_INDEPENDENTE/docs/link.py')
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(z, 'a') as f:
        f.writestr(info, 'target.py')
    assert module().assess_archive(z)['status'] == 'BLOCKED'
