from pathlib import Path
import subprocess

import pytest

from pipeline.git_mirror_observation import observe_remote_ref


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, check=True, text=True, capture_output=True).stdout.strip()


def make_repo(tmp_path: Path):
    work = tmp_path / 'work'
    bare = tmp_path / 'remote.git'
    work.mkdir()
    git('init', '-b', 'main', cwd=work)
    git('config', 'user.email', 'tests@example.com', cwd=work)
    git('config', 'user.name', 'Tests', cwd=work)
    (work / 'a.txt').write_text('one', encoding='utf-8')
    git('add', 'a.txt', cwd=work)
    git('commit', '-m', 'one', cwd=work)
    git('init', '--bare', str(bare))
    git('remote', 'add', 'origin', str(bare), cwd=work)
    git('push', 'origin', 'main', cwd=work)
    return work, bare, git('rev-parse', 'HEAD', cwd=work)


def test_observe_remote_ref_returns_exact_sha(tmp_path):
    _, bare, sha = make_repo(tmp_path)
    obs = observe_remote_ref(str(bare), 'main')
    assert obs.available is True
    assert obs.sha == sha
    assert obs.ref_name == 'main'


def test_observe_missing_ref_is_unavailable(tmp_path):
    _, bare, _ = make_repo(tmp_path)
    obs = observe_remote_ref(str(bare), 'fix/missing')
    assert obs.available is False
    assert obs.sha is None


def test_observe_rejects_inline_https_credentials():
    with pytest.raises(ValueError):
        observe_remote_ref('https://user:secret@example.com/repo.git', 'main')
