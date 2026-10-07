from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'sync_gitlab_mirror.py'
ROOT = Path(__file__).resolve().parents[3]


def load_module():
    spec = spec_from_file_location('sync_gitlab_mirror', SCRIPT)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(*args, cwd=None, check=True):
    return subprocess.run(['git', *args], cwd=cwd, check=check, text=True, capture_output=True)


def init_world(tmp_path: Path):
    source_work = tmp_path / 'source-work'
    source_bare = tmp_path / 'source.git'
    target_bare = tmp_path / 'target.git'
    source_work.mkdir()
    git('init', '-b', 'main', cwd=source_work)
    git('config', 'user.email', 'tests@example.com', cwd=source_work)
    git('config', 'user.name', 'Tests', cwd=source_work)
    (source_work / 'a.txt').write_text('one', encoding='utf-8')
    git('add', 'a.txt', cwd=source_work)
    git('commit', '-m', 'one', cwd=source_work)
    git('init', '--bare', str(source_bare))
    git('init', '--bare', str(target_bare))
    git('remote', 'add', 'origin', str(source_bare), cwd=source_work)
    git('push', 'origin', 'main', cwd=source_work)
    return source_work, source_bare, target_bare


def sha(repo, ref='refs/heads/main'):
    out = git('--git-dir', str(repo), 'rev-parse', ref).stdout.strip()
    return out


def test_fast_forward_sync_preserves_exact_sha(tmp_path):
    m = load_module()
    work, source, target = init_world(tmp_path)
    receipt = tmp_path / 'receipt.json'
    first = m.sync_ref(ROOT, str(source), str(target), 'main', receipt)
    assert first['source_sha'] == first['target_sha'] == sha(source)
    (work / 'a.txt').write_text('two', encoding='utf-8')
    git('commit', '-am', 'two', cwd=work)
    git('push', 'origin', 'main', cwd=work)
    second = m.sync_ref(ROOT, str(source), str(target), 'main', receipt)
    assert second['source_sha'] == second['target_sha'] == sha(source)
    assert sha(target) == sha(source)
    assert second['transport'] == 'neutral_worker'


def test_target_divergence_is_rejected(tmp_path):
    m = load_module()
    work, source, target = init_world(tmp_path)
    receipt = tmp_path / 'receipt.json'
    m.sync_ref(ROOT, str(source), str(target), 'main', receipt)

    target_work = tmp_path / 'target-work'
    git('clone', '-b', 'main', str(target), str(target_work))
    git('config', 'user.email', 'target@example.com', cwd=target_work)
    git('config', 'user.name', 'Target', cwd=target_work)
    (target_work / 'target.txt').write_text('diverge', encoding='utf-8')
    git('add', 'target.txt', cwd=target_work)
    git('commit', '-m', 'target diverges', cwd=target_work)
    git('push', 'origin', 'main', cwd=target_work)

    (work / 'source.txt').write_text('source', encoding='utf-8')
    git('add', 'source.txt', cwd=work)
    git('commit', '-m', 'source moves', cwd=work)
    git('push', 'origin', 'main', cwd=work)

    with pytest.raises(RuntimeError, match='diverg'):
        m.sync_ref(ROOT, str(source), str(target), 'main', receipt)


def test_ineligible_ref_is_rejected(tmp_path):
    m = load_module()
    _, source, target = init_world(tmp_path)
    with pytest.raises(ValueError, match='eligible'):
        m.sync_ref(ROOT, str(source), str(target), 'subagent/temp', tmp_path / 'r.json')


def test_inline_credentials_are_rejected_without_leaking_secret(tmp_path):
    m = load_module()
    with pytest.raises(ValueError) as exc:
        m.sync_ref(
            ROOT,
            'https://user:source-secret@example.com/repo.git',
            'https://user:target-secret@example.com/repo.git',
            'main',
            tmp_path / 'r.json',
        )
    message = str(exc.value)
    assert 'source-secret' not in message
    assert 'target-secret' not in message


def test_source_ref_is_never_mutated(tmp_path):
    m = load_module()
    _, source, target = init_world(tmp_path)
    before = sha(source)
    m.sync_ref(ROOT, str(source), str(target), 'main', tmp_path / 'r.json')
    assert sha(source) == before


def test_script_contains_no_force_push():
    assert 'git push --force' not in SCRIPT.read_text(encoding='utf-8')
