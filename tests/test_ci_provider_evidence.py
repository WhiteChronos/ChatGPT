from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import jsonschema
import pytest

from pipeline.ci_provider_evidence import (
    CIProviderEvidence,
    EvidenceDisposition,
    compare_provider_evidence,
    validate_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'schemas' / 'ci_provider_evidence.schema.json'
SHA = 'a' * 40
OTHER = 'b' * 40
NOW = datetime.now(timezone.utc)


def ev(provider='github', result='PASS', sha=SHA, parity='NOT_APPLICABLE', **changes):
    data = dict(
        provider=provider,
        repository_identity='WhiteChronos/ChatGPT' if provider != 'gitlab' else 'chronoswhite-group/ChronosWhite-project',
        subject_sha=sha,
        pipeline_or_run_id='123',
        gate_name='full-contingency',
        result=result,
        timestamp=NOW,
        ci_config_revision=SHA,
        mirror_parity_status=parity,
        attempt=1,
    )
    data.update(changes)
    return CIProviderEvidence(**data)


def test_evidence_has_no_authority_grant_fields():
    record = ev('gitlab', parity='HEALTHY')
    data = asdict(record)
    assert 'merge_authorized' not in data
    assert 'deploy_authorized' not in data


def test_schema_rejects_authority_fields():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    data = asdict(ev('gitlab', parity='HEALTHY'))
    data['timestamp'] = NOW.isoformat()
    data['merge_authorized'] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)


@pytest.mark.parametrize(
    ('github', 'gitlab', 'expected'),
    [
        (ev('github', 'PASS'), ev('gitlab', 'PASS', parity='HEALTHY'), EvidenceDisposition.CORROBORATED),
        (ev('github', 'PASS'), ev('gitlab', 'FAIL', parity='HEALTHY'), EvidenceDisposition.DISCREPANCY_BLOCKED),
        (ev('github', 'FAIL'), ev('gitlab', 'PASS', parity='HEALTHY'), EvidenceDisposition.DISCREPANCY_BLOCKED),
        (None, ev('gitlab', 'PASS', parity='HEALTHY'), EvidenceDisposition.CONTINGENCY_EVIDENCE_ONLY),
        (ev('github', 'PASS'), ev('gitlab', 'PASS', parity='DIVERGED'), EvidenceDisposition.GITLAB_EVIDENCE_INELIGIBLE),
        (ev('github', 'PASS'), ev('gitlab', 'PASS', sha=OTHER, parity='HEALTHY'), EvidenceDisposition.SUBJECT_MISMATCH_BLOCKED),
    ],
)
def test_comparison_matrix(github, gitlab, expected):
    assert compare_provider_evidence(github, gitlab).disposition is expected


def test_validate_rejects_future_timestamp():
    record = ev(timestamp=NOW + timedelta(seconds=301))
    with pytest.raises(ValueError):
        validate_evidence(record, now=NOW)


def test_validate_rejects_unknown_provider():
    record = ev(provider='unknown')
    with pytest.raises(ValueError):
        validate_evidence(record, now=NOW)


def test_validate_rejects_ineligible_gitlab_parity():
    record = ev(provider='gitlab', parity='STALE')
    with pytest.raises(ValueError):
        validate_evidence(record, now=NOW)

from pipeline.ci_provider_evidence import FailureClass, RetryDisposition, classify_retry
from pipeline.gitlab_contingency_policy import load_policy

POLICY = ROOT / 'governance' / 'GITLAB_CONTINGENCY_CI_POLICY.json'


@pytest.mark.parametrize(
    ('failure', 'attempt', 'expected'),
    [
        (FailureClass.PROVIDER_INFRA_FAILURE, 1, RetryDisposition.RETRY_ELIGIBLE),
        (FailureClass.RUNNER_ASSIGNMENT_FAILURE, 1, RetryDisposition.RETRY_ELIGIBLE),
        (FailureClass.PROVIDER_INFRA_FAILURE, 2, RetryDisposition.RETRY_LIMIT_REACHED),
        (FailureClass.CODE_FAILURE, 1, RetryDisposition.NOT_RETRY_ELIGIBLE),
        (FailureClass.POLICY_FAILURE, 1, RetryDisposition.NOT_RETRY_ELIGIBLE),
        (FailureClass.MIRROR_FAILURE, 1, RetryDisposition.NOT_RETRY_ELIGIBLE),
        (FailureClass.UNKNOWN, 1, RetryDisposition.NOT_RETRY_ELIGIBLE),
    ],
)
def test_retry_classification(failure, attempt, expected):
    policy = load_policy(POLICY)
    assert classify_retry(failure, attempt, policy) is expected
