import json
from pathlib import Path
import subprocess
import sys

import pytest

from pipeline.contingency_ci_gate import _expanded_argv, commands_for_profile, run_profile

ROOT = Path(__file__).resolve().parents[1]


def argvs(profile):
    return [tuple(c.argv) for c in commands_for_profile(profile)]


def test_python_governance_catalog_uses_canonical_validators():
    assert argvs('python-governance') == [
        ('python', '-m', 'pytest', '-q'),
        ('python', '-m', 'pytest', '-q', 'plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py'),
        ('python', 'pipeline/engineering_compatibility_gate.py'),
        ('python', 'pipeline/protocol_zero_gate.py', 'datasheet/projects/example-project.json'),
    ]


def test_broker_catalog():
    assert argvs('broker') == [
        ('node', '--test', 'plugins/subagent-broker/tests/*.test.mjs'),
    ]


def test_full_contingency_is_union_without_authority_actions():
    commands = argvs('full-contingency')
    assert len(commands) == 5
    flattened = ' '.join(' '.join(c) for c in commands).lower()
    for forbidden in ('git push', 'deploy', 'canary', 'stable', 'live smoke', 'live-smoke'):
        assert forbidden not in flattened


def test_unknown_profile_rejected():
    with pytest.raises(ValueError):
        commands_for_profile('unknown')


def test_dry_run_cli_returns_deterministic_catalog():
    result = subprocess.run(
        [sys.executable, 'pipeline/contingency_ci_gate.py', '--profile', 'full-contingency', '--dry-run', '--json'],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data['profile'] == 'full-contingency'
    assert data['dry_run'] is True
    assert len(data['commands']) == 5

def test_run_profile_scrubs_test_runner_control_environment(tmp_path, monkeypatch):
    seen = []

    def fake_run(argv, **kwargs):
        seen.append(kwargs.get('env'))
        return subprocess.CompletedProcess(argv, 0, '', '')

    monkeypatch.setenv('PYTEST_ADDOPTS', '--collect-only')
    monkeypatch.setenv('PYTEST_PLUGINS', 'evil_plugin')
    monkeypatch.setenv('PYTHONPATH', '/tmp/evil')
    monkeypatch.setenv('NODE_OPTIONS', '--import=data:text/javascript,console.log(1)')
    monkeypatch.setattr(subprocess, 'run', fake_run)

    result = run_profile(ROOT, 'full-contingency')

    assert result.passed is True
    assert seen
    for env in seen:
        assert env is not None
        assert 'PYTEST_ADDOPTS' not in env
        assert 'PYTEST_PLUGINS' not in env
        assert 'PYTHONPATH' not in env
        assert 'NODE_OPTIONS' not in env


def test_run_profile_executes_every_validator_after_failure(monkeypatch):
    calls = []
    outcomes = iter([1, 0, 0, 0])

    def fake_run(argv, **kwargs):
        calls.append(tuple(argv))
        return subprocess.CompletedProcess(argv, next(outcomes), '', '')

    monkeypatch.setattr(subprocess, 'run', fake_run)
    result = run_profile(ROOT, 'python-governance')

    assert result.passed is False
    assert result.failed_command_index == 0
    assert len(result.results) == 4
    assert len(calls) == 4


def test_mandatory_glob_without_matches_fails_closed(tmp_path):
    with pytest.raises(FileNotFoundError, match='mandatory test glob'):
        _expanded_argv(tmp_path, ('node', '--test', 'plugins/subagent-broker/tests/*.test.mjs'))
