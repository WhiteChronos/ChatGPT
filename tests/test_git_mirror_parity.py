from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
