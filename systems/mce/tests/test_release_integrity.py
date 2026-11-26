"""TDD: portable MCE ZIP integrity is necessary but never production approval."""
import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('mce_release_integrity', ROOT/'scripts/release_integrity.py')


def load_module():
    assert SPEC is not None and SPEC.loader is not None
    m = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(m)
    return m


def sample_archive(path, *, content=b'engineering metadata only', declared=None, extra=None):
    digest=hashlib.sha256(content).hexdigest()
    manifest={'system':'MCE_INDEPENDENTE', 'files':{'docs/safe.txt':declared or digest}}
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('MCE_INDEPENDENTE/docs/safe.txt',content)
        z.writestr('MCE_INDEPENDENTE/manifest.json',json.dumps(manifest))
        if extra: z.writestr(extra,b'external')


def test_verifies_all_payload_hashes_but_never_certifies_production(tmp_path):
    archive=tmp_path/'mce.zip'; sample_archive(archive)
    report=load_module().assess_archive(archive)
    assert report['status']=='INTEGRITY_PASS'
    assert report['checked_files']==1
    assert report['production_complete'] is False


def test_blocks_content_mismatch(tmp_path):
    archive=tmp_path/'mce.zip'; sample_archive(archive,declared='0'*64)
    assert load_module().assess_archive(archive)['status']=='BLOCKED'


def test_blocks_traversal_and_unmanifested_payload(tmp_path):
    archive=tmp_path/'mce.zip'; sample_archive(archive,extra='../unsafe.txt')
    assert load_module().assess_archive(archive)['status']=='BLOCKED'
    sample_archive(archive,extra='MCE_INDEPENDENTE/private_source.txt')
    assert load_module().assess_archive(archive)['status']=='BLOCKED'




def test_trusted_external_zip_digest_matches(tmp_path):
    archive = tmp_path / 'mce.zip'
    sample_archive(archive)
    expected = hashlib.sha256(archive.read_bytes()).hexdigest()
    report = load_module().assess_archive(archive, expected_sha256=expected)
    assert report['status'] == 'INTEGRITY_PASS'
    assert report['trusted_digest_match'] is True
    assert report['production_complete'] is False


def test_mismatch_external_zip_digest_blocks_even_when_manifest_valid(tmp_path):
    archive = tmp_path / 'mce.zip'
    sample_archive(archive)
    report = load_module().assess_archive(archive, expected_sha256='0' * 64)
    assert report['status'] == 'BLOCKED'
    assert report['trusted_digest_match'] is False


def test_malformed_external_zip_digest_blocks(tmp_path):
    archive = tmp_path / 'mce.zip'
    sample_archive(archive)
    report = load_module().assess_archive(archive, expected_sha256='invalid')
    assert report['status'] == 'BLOCKED'


def test_independent_git_commit_pin_blocks_missing_claim(tmp_path):
    archive = tmp_path / 'mce.zip'
    sample_archive(archive)
    report = load_module().assess_archive(archive, expected_git_sha='a' * 40)
    assert report['status'] == 'BLOCKED'
    assert report['trusted_commit_match'] is False


def test_independent_git_commit_pin_matches_manifest(tmp_path):
    archive = tmp_path / 'mce.zip'
    content = b'static evidence only'
    manifest = {'system': 'MCE_INDEPENDENTE', 'git_sha': 'a' * 40,
                'files': {'docs/safe.txt': hashlib.sha256(content).hexdigest()}}
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('MCE_INDEPENDENTE/docs/safe.txt', content)
        z.writestr('MCE_INDEPENDENTE/manifest.json', json.dumps(manifest))
    report = load_module().assess_archive(archive, expected_git_sha='a' * 40)
    assert report['status'] == 'INTEGRITY_PASS'
    assert report['trusted_commit_match'] is True
    assert report['production_complete'] is False
