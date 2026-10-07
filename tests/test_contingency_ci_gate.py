import json
from pathlib import Path
import subprocess
import sys

import pytest

from pipeline.contingency_ci_gate import commands_for_profile

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
