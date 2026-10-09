from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys

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

def test_reversed_network_endpoints_are_rejected_before_git(tmp_path, monkeypatch):
    m = load_module()

    def fail_git(*args, **kwargs):
        raise AssertionError('git must not run before direction validation')

    monkeypatch.setattr(m, '_run_git', fail_git)
    with pytest.raises(ValueError, match='direction'):
        m.sync_ref(
            ROOT,
            'https://gitlab.com/chronoswhite-group/ChronosWhite-project.git',
            'https://github.com/WhiteChronos/ChatGPT.git',
            'main',
            tmp_path / 'r.json',
        )


def test_documented_entrypoint_runs_from_repository_root():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--help'],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert 'ModuleNotFoundError' not in result.stderr


def test_source_is_reobserved_after_push_before_success_receipt(tmp_path, monkeypatch):
    m = load_module()
    _, source, target = init_world(tmp_path)
    original_remote_sha = m._remote_sha

    def moving_source(url, full_ref, **kwargs):
        if url == str(source):
            return 'b' * 40
        return original_remote_sha(url, full_ref, **kwargs)

    monkeypatch.setattr(m, '_remote_sha', moving_source)
    with pytest.raises(RuntimeError, match='authoritative source'):
        m.sync_ref(ROOT, str(source), str(target), 'main', tmp_path / 'r.json')

def test_worker_scrubs_git_control_environment(monkeypatch):
    m = load_module()
    captured = {}

    def fake_run(argv, **kwargs):
        captured['env'] = kwargs.get('env')
        return subprocess.CompletedProcess(argv, 0, '', '')

    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    monkeypatch.setenv('GIT_CONFIG_KEY_0', 'url.file:///tmp/evil.insteadOf')
    monkeypatch.setenv('GIT_CONFIG_VALUE_0', 'https://github.com/')
    monkeypatch.setenv('GIT_SSH_COMMAND', 'touch /tmp/marker')
    monkeypatch.setenv('GIT_ASKPASS', 'touch /tmp/askpass-marker')
    monkeypatch.setenv('SSH_ASKPASS', 'touch /tmp/ssh-askpass-marker')
    monkeypatch.setattr(subprocess, 'run', fake_run)

    m._run_git(['version'])

    env = captured['env']
    assert env is not None
    assert 'GIT_CONFIG_COUNT' not in env
    assert not any(key.startswith('GIT_CONFIG_KEY_') for key in env)
    assert not any(key.startswith('GIT_CONFIG_VALUE_') for key in env)
    assert 'GIT_SSH_COMMAND' not in env
    assert 'GIT_ASKPASS' not in env
    assert 'SSH_ASKPASS' not in env

def test_option_like_remote_is_rejected_before_git(tmp_path, monkeypatch):
    m = load_module()

    def fail_git(*args, **kwargs):
        raise AssertionError('git must not run for an option-like remote')

    monkeypatch.setattr(m, '_run_git', fail_git)
    with pytest.raises(ValueError, match='remote'):
        m.sync_ref(
            ROOT,
            '--upload-pack=touch /tmp/marker',
            str(tmp_path / 'target.git'),
            'main',
            tmp_path / 'r.json',
        )

def test_network_mirror_receipt_push_options_bind_transport_and_sha():
    m = load_module()
    policy = m.load_policy(ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json')
    source_sha = 'a' * 40
    receipt = m._mirror_receipt_claim(
        policy=policy,
        ref='main',
        source_sha=source_sha,
        timestamp='2026-10-07T01:00:00+00:00',
    )
    options = m._mirror_push_options(receipt)

    joined = ' '.join(options)
    assert 'ci.input=mirror_transport=neutral_worker' in joined
    assert 'ci.input=mirror_source_repository=WhiteChronos/ChatGPT' in joined
    assert 'ci.input=mirror_target_project=chronoswhite-group/ChronosWhite-project' in joined
    assert 'ci.input=mirror_ref=main' in joined
    assert 'ci.input=mirror_pipeline_ref=main' in joined
    assert f'ci.input=mirror_source_sha={source_sha}' in joined
    assert f'ci.input=mirror_target_sha={source_sha}' in joined
    assert 'ci.input=mirror_receipt_sha256=' in joined
    assert 'ci.variable=' not in joined

def test_safe_git_environment_disables_global_and_system_config(monkeypatch):
    m = load_module()
    monkeypatch.setenv('HOME', '/tmp/host-home')
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', '/tmp/evil.gitconfig')
    monkeypatch.setenv('GIT_CONFIG_COUNT', '1')
    env = m._safe_git_environment()
    assert env['GIT_CONFIG_NOSYSTEM'] == '1'
    assert env['GIT_CONFIG_GLOBAL'] == m.os.devnull
    assert 'GIT_CONFIG_COUNT' not in env

def test_network_target_requires_explicit_credential_helper(tmp_path, monkeypatch):
    m = load_module()

    def fail_git(*args, **kwargs):
        raise AssertionError('git must not run before credential-helper validation')

    monkeypatch.setattr(m, '_run_git', fail_git)
    with pytest.raises(ValueError, match='target credential helper'):
        m.sync_ref(
            ROOT,
            'https://github.com/WhiteChronos/ChatGPT.git',
            'https://gitlab.com/chronoswhite-group/ChronosWhite-project.git',
            'main',
            tmp_path / 'r.json',
        )


def test_explicit_credential_helper_is_scoped_to_git_command(tmp_path):
    m = load_module()
    helper = tmp_path / 'git-credential-whitechronos'
    helper.write_text('#!/bin/sh\\nexit 0\\n', encoding='utf-8')
    helper.chmod(0o700)

    normalized = m._normalize_credential_helper(str(helper))
    argv = m._git_argv(['ls-remote', 'https://gitlab.com/example/repo.git'], normalized)

    assert argv[:7] == [
        'git',
        '-c', 'credential.helper=',
        '-c', f'credential.helper={helper.resolve()}',
        '-c', 'credential.interactive=false',
    ]
    assert argv[7:] == ['ls-remote', 'https://gitlab.com/example/repo.git']


@pytest.mark.parametrize('value', [
    'manager-core',
    '!touch /tmp/marker',
    '/tmp/helper;touch-marker',
    '/tmp/helper with space',
])
def test_credential_helper_rejects_ambiguous_or_shell_control_value(value):
    m = load_module()
    with pytest.raises(ValueError, match='credential helper'):
        m._normalize_credential_helper(value)


def test_gcm_manager_selector_is_allowed():
    m = load_module()
    assert m._normalize_credential_helper('manager') == 'manager'
    argv = m._git_argv(['ls-remote', 'https://gitlab.com/example/repo.git'], 'manager')
    assert argv[:7] == [
        'git',
        '-c', 'credential.helper=',
        '-c', 'credential.helper=manager',
        '-c', 'credential.interactive=false',
    ]



def test_userless_scp_remote_is_classified_as_network():
    m = load_module()
    assert m._is_network_remote('gitlab.com:chronoswhite-group/ChronosWhite-project.git') is True


def test_refresh_ref_is_unique_and_bound_to_receipt_claim():
    m = load_module()
    policy = m.load_policy(ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json')
    claim = m._mirror_receipt_claim(
        policy=policy,
        ref='main',
        source_sha='a' * 40,
        timestamp='2026-10-08T22:00:00+00:00',
    )
    first = m._refresh_ref(claim)
    changed = dict(claim)
    changed['timestamp'] = '2026-10-08T22:01:00+00:00'
    second = m._refresh_ref(changed)
    assert first.startswith('refs/heads/whitechronos-refresh/')
    assert second.startswith('refs/heads/whitechronos-refresh/')
    assert first != second


def test_source_credential_helper_is_supported_separately_from_target(tmp_path, monkeypatch):
    m = load_module()
    source_helper = tmp_path / 'git-credential-source'
    target_helper = tmp_path / 'git-credential-target'
    for helper in (source_helper, target_helper):
        helper.write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        helper.chmod(0o700)

    calls = []
    def fake_run_git(args, **kwargs):
        calls.append((tuple(args), kwargs.get('credential_helper')))
        if args[:2] == ['rev-parse', 'refs/whitechronos/source/main']:
            return subprocess.CompletedProcess(args, 0, 'a' * 40 + '\n', '')
        if args[:2] == ['merge-base', '--is-ancestor']:
            return subprocess.CompletedProcess(args, 0, '', '')
        return subprocess.CompletedProcess(args, 0, '', '')

    remote_values = iter([None, 'a' * 40, 'a' * 40])
    def fake_remote_sha(url, full_ref, **kwargs):
        calls.append((('remote-sha', url, full_ref), kwargs.get('credential_helper')))
        return next(remote_values)

    monkeypatch.setattr(m, '_run_git', fake_run_git)
    monkeypatch.setattr(m, '_remote_sha', fake_remote_sha)
    monkeypatch.setattr(m, '_is_network_remote', lambda url: True)
    monkeypatch.setattr(m, '_validate_mirror_direction', lambda *args, **kwargs: None)

    m.sync_ref(
        ROOT,
        'https://github.com/WhiteChronos/ChatGPT.git',
        'https://gitlab.com/chronoswhite-group/ChronosWhite-project.git',
        'main',
        tmp_path / 'receipt.json',
        source_credential_helper=str(source_helper),
        target_credential_helper=str(target_helper),
    )

    assert any(helper == str(source_helper.resolve()) for argv, helper in calls if argv and argv[0] in {'fetch', 'remote-sha'})
    assert any(helper == str(target_helper.resolve()) for argv, helper in calls if argv and argv[0] in {'push', 'remote-sha'})


def test_persisted_receipt_hash_binds_complete_record(tmp_path):
    m = load_module()
    _, source, target = init_world(tmp_path)
    receipt_path = tmp_path / 'receipt.json'
    receipt = m.sync_ref(ROOT, str(source), str(target), 'main', receipt_path)
    assert 'record_sha256' in receipt
    semantic = dict(receipt)
    digest = semantic.pop('record_sha256')
    assert digest == m._mirror_receipt_digest(semantic)
    tampered = dict(semantic)
    tampered['dry_run'] = not bool(tampered['dry_run'])
    assert m._mirror_receipt_digest(tampered) != digest


def test_refresh_push_options_bind_reserved_pipeline_ref():
    m = load_module()
    policy = m.load_policy(ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json')
    base = m._mirror_receipt_claim(
        policy=policy,
        ref='main',
        source_sha='a' * 40,
        timestamp='2026-10-08T22:00:00+00:00',
    )
    refresh = m._refresh_ref(base)[len('refs/heads/'):]
    assert refresh.startswith('whitechronos-refresh/')
    assert len(refresh.removeprefix('whitechronos-refresh/')) == 64
    claim = m._mirror_receipt_claim(
        policy=policy,
        ref='main',
        source_sha='a' * 40,
        timestamp='2026-10-08T22:00:00+00:00',
        pipeline_ref=refresh,
    )
    joined = ' '.join(m._mirror_push_options(claim))
    assert f'ci.input=mirror_pipeline_ref={refresh}' in joined
    assert 'ci.input=mirror_ref=main' in joined
