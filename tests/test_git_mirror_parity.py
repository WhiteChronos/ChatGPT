from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import subprocess
import sys

import pytest

from pipeline.gitlab_contingency_policy import load_policy
from pipeline.git_mirror_parity import MirrorParityInput, MirrorParityStatus, evaluate_mirror_parity

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json'
SHA = 'a' * 40
OTHER = 'b' * 40


def policy():
    return replace(
        load_policy(POLICY),
        provisioning_state='PROVISIONED',
        gitlab_project_id=86465539,
        gitlab_project_path='chronoswhite-group/ChronosWhite-project',
        mirror_transport='neutral_worker',
    )


def value(**changes):
    now = datetime.now(timezone.utc)
    base = dict(
        github_repository='WhiteChronos/ChatGPT',
        gitlab_project_id=86465539,
        gitlab_project_path='chronoswhite-group/ChronosWhite-project',
        ref_name='main',
        github_sha=SHA,
        gitlab_sha=SHA,
        ci_subject_sha=SHA,
        github_available=True,
        gitlab_available=True,
        receipt_timestamp=now,
        evaluated_at=now,
    )
    base.update(changes)
    return MirrorParityInput(**base)


def test_healthy_exact_sha_and_identity():
    r = evaluate_mirror_parity(value(), policy())
    assert r.status is MirrorParityStatus.HEALTHY
    assert r.evidence_eligible is True


@pytest.mark.parametrize('changes', [
    {'gitlab_sha': OTHER},
    {'ci_subject_sha': OTHER},
    {'github_repository': 'Wrong/Repo'},
    {'gitlab_project_id': 1},
    {'gitlab_project_path': 'wrong/project'},
])
def test_divergence_fails_closed(changes):
    r = evaluate_mirror_parity(value(**changes), policy())
    assert r.status is MirrorParityStatus.DIVERGED
    assert r.evidence_eligible is False


def test_stale_receipt_is_ineligible():
    now = datetime.now(timezone.utc)
    r = evaluate_mirror_parity(
        value(receipt_timestamp=now - timedelta(seconds=3601), evaluated_at=now),
        policy(),
    )
    assert r.status is MirrorParityStatus.STALE
    assert r.evidence_eligible is False


def test_unavailable_provider_is_ineligible():
    r = evaluate_mirror_parity(value(github_available=False, github_sha=None), policy())
    assert r.status is MirrorParityStatus.UNAVAILABLE
    assert r.evidence_eligible is False

def test_ineligible_ref_never_becomes_healthy():
    r = evaluate_mirror_parity(value(ref_name='subagent/temp'), policy())
    assert r.status is MirrorParityStatus.DIVERGED
    assert r.evidence_eligible is False


def test_cli_uses_current_clock_instead_of_replayed_evaluated_at(tmp_path):
    old = '2000-01-01T00:00:00+00:00'
    payload = {
        'github_repository': 'WhiteChronos/ChatGPT',
        'gitlab_project_id': 86465539,
        'gitlab_project_path': 'chronoswhite-group/ChronosWhite-project',
        'ref_name': 'main',
        'github_sha': SHA,
        'gitlab_sha': SHA,
        'ci_subject_sha': SHA,
        'github_available': True,
        'gitlab_available': True,
        'receipt_timestamp': old,
        'evaluated_at': old,
    }
    evidence = tmp_path / 'mirror-input.json'
    evidence.write_text(json.dumps(payload), encoding='utf-8')
    # The subprocess exercises stale-evidence semantics under an explicitly
    # enabled offline fixture; the live repository policy remains DISABLED.
    legacy = json.loads(POLICY.read_text(encoding='utf-8'))
    legacy.update(
        provisioning_state='PROVISIONED',
        gitlab_project_id=86465539,
        gitlab_project_path='chronoswhite-group/ChronosWhite-project',
        mirror_transport='neutral_worker',
    )
    offline_policy = tmp_path / 'test-only-legacy-policy.json'
    offline_policy.write_text(json.dumps(legacy), encoding='utf-8')
    result = subprocess.run(
        [
            sys.executable,
            'pipeline/git_mirror_parity.py',
            '--input',
            str(evidence),
            '--policy',
            str(offline_policy),
            '--json',
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    data = json.loads(result.stdout)
    assert result.returncode == 2
    assert data['status'] == 'STALE'
    assert data['evidence_eligible'] is False


@pytest.mark.parametrize(
    ("github_available", "gitlab_available"),
    [
        ("false", False),
        (False, "false"),
        ("true", True),
        (True, "true"),
    ],
)
def test_cli_rejects_non_boolean_provider_availability(tmp_path, github_available, gitlab_available):
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        "github_repository": "WhiteChronos/ChatGPT",
        "gitlab_project_id": 86465539,
        "gitlab_project_path": "chronoswhite-group/ChronosWhite-project",
        "ref_name": "main",
        "github_sha": SHA,
        "gitlab_sha": SHA,
        "ci_subject_sha": SHA,
        "github_available": github_available,
        "gitlab_available": gitlab_available,
        "receipt_timestamp": now,
    }
    evidence = tmp_path / "mirror-input.json"
    evidence.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "pipeline/git_mirror_parity.py",
            "--input",
            str(evidence),
            "--policy",
            str(POLICY),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert "JSON boolean" in data["error"]
