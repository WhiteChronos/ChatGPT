"""Qualify complete packages against actual Git blobs and existing verifier."""
import hashlib
import importlib.util
import json
import subprocess
import zipfile
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def git(repo, *args, input=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], input=input)


def repository(tmp_path):
    repo = tmp_path / 'source'
    repo.mkdir()
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.name', 'Synthetic Test')
    git(repo, 'config', 'user.email', 'synthetic@example.invalid')
    source = repo / 'systems/mce/scripts'
    source.mkdir(parents=True)
    (source / 'example.py').write_bytes(b'print("public code")\n')
    git(repo, 'add', '.')
    git(repo, 'commit', '-qm', 'synthetic fixture')
    return repo, git(repo, 'rev-parse', 'HEAD').decode().strip()


def test_package_uses_commit_bytes_and_excludes_untracked_sources(tmp_path):
    repo, sha = repository(tmp_path)
    (repo / 'systems/mce/scripts/example.py').write_bytes(b'local change')
    (repo / 'systems/mce/private.xlsx').write_bytes(b'private untracked fixture')
    archive = tmp_path / 'candidate.zip'
    report = module('build_release').build_release(repo, sha, archive)
    with zipfile.ZipFile(archive) as z:
        assert z.read('MCE_INDEPENDENTE/scripts/example.py') == b'print("public code")\n'
        assert not any('private.xlsx' in x for x in z.namelist())
        assert json.loads(z.read('MCE_INDEPENDENTE/manifest.json'))['git_sha'] == sha
    verified = module('release_integrity').assess_archive(
        archive, expected_git_sha=sha, expected_sha256=report['sha256'])
    assert verified['status'] == 'INTEGRITY_PASS'
    assert report['production_complete'] is False


def test_reproducible_and_no_overwrite(tmp_path):
    repo, sha = repository(tmp_path)
    builder = module('build_release')
    one, two = tmp_path / 'one.zip', tmp_path / 'two.zip'
    builder.build_release(repo, sha, one)
    builder.build_release(repo, sha, two)
    assert one.read_bytes() == two.read_bytes()
    before = hashlib.sha256(one.read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        builder.build_release(repo, sha, one)
    assert hashlib.sha256(one.read_bytes()).hexdigest() == before


def test_wrong_commit_and_source_destination_refused(tmp_path):
    repo, sha = repository(tmp_path)
    builder = module('build_release')
    with pytest.raises(ValueError):
        builder.build_release(repo, '0' * 40, tmp_path / 'absent.zip')
    assert not (tmp_path / 'absent.zip').exists()
    with pytest.raises(ValueError):
        builder.build_release(repo, sha, repo / 'systems/mce/candidate.zip')


def test_git_symlink_rejected_without_windows_symlink_permission(tmp_path):
    repo, _ = repository(tmp_path)
    blob = git(repo, 'hash-object', '-w', '--stdin', input=b'../../private.xlsx').decode().strip()
    git(repo, 'update-index', '--add', '--cacheinfo', '120000', blob,
        'systems/mce/scripts/link')
    git(repo, 'commit', '-qm', 'synthetic linked blob')
    sha = git(repo, 'rev-parse', 'HEAD').decode().strip()
    output = tmp_path / 'linked.zip'
    with pytest.raises(ValueError):
        module('build_release').build_release(repo, sha, output)
    assert not output.exists()
