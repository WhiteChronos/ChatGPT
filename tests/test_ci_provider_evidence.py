from dataclasses import asdict, replace
import hashlib
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


def provenance_sha256(data):
    payload = {}
    for key in (
        'provider',
        'repository_identity',
        'subject_sha',
        'pipeline_or_run_id',
        'gate_name',
        'result',
        'timestamp',
        'ci_config_revision',
        'mirror_parity_status',
        'attempt',
        'input_artifacts_sha256',
    ):
        value = data[key]
        if key == 'timestamp' and isinstance(value, datetime):
            value = value.isoformat()
        if key in {'subject_sha', 'ci_config_revision'}:
            value = str(value).lower()
        payload[key] = value
    encoded = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


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
        input_artifacts_sha256=(
            {
                'mirror-input.json': '1' * 64,
                'mirror-parity.json': '2' * 64,
                'gitlab-runtime-identity.json': '3' * 64,
                'contingency-python.json': '4' * 64,
                'contingency-broker.json': '5' * 64,
                'mirror-parity-final.json': '6' * 64,
            }
            if provider == 'gitlab'
            else {}
        ),
    )
    data.update(changes)
    data.setdefault('provenance_sha256', provenance_sha256(data))
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

def test_schema_requires_provenance_sha256():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    data = asdict(ev('gitlab', parity='HEALTHY'))
    data['timestamp'] = NOW.isoformat()
    data.pop('provenance_sha256')
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)


def test_validate_rejects_tampered_provenance_sha256():
    record = ev(provenance_sha256='0' * 64)
    with pytest.raises(ValueError, match='provenance'):
        validate_evidence(record, now=NOW)


@pytest.mark.parametrize(
    ('github_changes', 'gitlab_changes'),
    [
        ({'repository_identity': 'Wrong/Repo'}, {}),
        ({}, {'repository_identity': 'wrong/group-project'}),
        ({'gate_name': 'other-gate'}, {}),
        ({}, {'ci_config_revision': OTHER}),
    ],
)
def test_comparison_rejects_context_identity_mismatch(github_changes, gitlab_changes):
    github = ev('github', **github_changes)
    gitlab = ev('gitlab', parity='HEALTHY', **gitlab_changes)
    assert compare_provider_evidence(github, gitlab).disposition is EvidenceDisposition.DISCREPANCY_BLOCKED

def test_validate_rejects_result_tamper_after_provenance_binding():
    record = ev('gitlab', parity='HEALTHY')
    tampered = replace(record, result='FAIL')
    with pytest.raises(ValueError, match='provenance'):
        validate_evidence(tampered, now=NOW)


def test_schema_rejects_non_sha_ci_config_revision():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    data = asdict(ev('gitlab', parity='HEALTHY'))
    data['timestamp'] = NOW.isoformat()
    data['ci_config_revision'] = 'not-a-git-sha'
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, schema)

def test_comparison_rejects_wrong_provider_in_github_slot():
    github_slot = ev('local', repository_identity='WhiteChronos/ChatGPT')
    gitlab = ev('gitlab', parity='HEALTHY')
    assert compare_provider_evidence(github_slot, gitlab).disposition is EvidenceDisposition.DISCREPANCY_BLOCKED


def test_comparison_rejects_wrong_provider_in_gitlab_slot():
    github = ev('github')
    gitlab_slot = ev('github', parity='HEALTHY', repository_identity='chronoswhite-group/ChronosWhite-project')
    assert compare_provider_evidence(github, gitlab_slot).disposition is EvidenceDisposition.DISCREPANCY_BLOCKED


def test_schema_requires_input_artifact_digests():
    schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    assert 'input_artifacts_sha256' in schema['required']
    assert schema['properties']['input_artifacts_sha256']['type'] == 'object'


def test_persisted_json_loader_parses_timestamp_before_validation(tmp_path):
    from pipeline.ci_provider_evidence import load_evidence_json

    record = ev('gitlab', parity='HEALTHY')
    data = asdict(record)
    data['timestamp'] = record.timestamp.isoformat()
    path = tmp_path / 'evidence.json'
    path.write_text(json.dumps(data), encoding='utf-8')

    loaded = load_evidence_json(path)
    assert isinstance(loaded.timestamp, datetime)
    assert loaded.timestamp.tzinfo is not None
    validate_evidence(loaded, now=NOW)


import pipeline.ci_provider_evidence as evidence_module


def _live_gitlab_attestation(**changes):
    cls = getattr(evidence_module, "GitLabPipelineAttestation", None)
    assert cls is not None, "GitLabPipelineAttestation missing"
    data = dict(
        repository_identity="chronoswhite-group/ChronosWhite-project",
        pipeline_or_run_id="123",
        subject_sha=SHA,
        source="push",
        status="success",
        observed_at=NOW,
    )
    data.update(changes)
    return cls(**data)


def test_unattested_gitlab_evidence_cannot_mint_eligibility():
    record = ev("gitlab", parity="HEALTHY")
    comparison = compare_provider_evidence(None, record)
    assert comparison.disposition.value == "GITLAB_ATTESTATION_REQUIRED"


def test_matching_live_gitlab_attestation_allows_contingency_evidence():
    record = ev("gitlab", parity="HEALTHY")
    comparison = compare_provider_evidence(
        None,
        record,
        gitlab_attestation=_live_gitlab_attestation(),
        now=NOW,
    )
    assert comparison.disposition is EvidenceDisposition.CONTINGENCY_EVIDENCE_ONLY


@pytest.mark.parametrize(
    "changes",
    [
        {"pipeline_or_run_id": "999"},
        {"subject_sha": OTHER},
        {"source": "web"},
        {"status": "failed"},
    ],
)
def test_gitlab_attestation_must_match_authenticated_push(changes):
    record = ev("gitlab", parity="HEALTHY")
    comparison = compare_provider_evidence(
        None,
        record,
        gitlab_attestation=_live_gitlab_attestation(**changes),
        now=NOW,
    )
    assert comparison.disposition is EvidenceDisposition.DISCREPANCY_BLOCKED


def test_validate_rejects_expired_evidence():
    record = ev("gitlab", parity="HEALTHY", timestamp=NOW - timedelta(seconds=3601))
    with pytest.raises(ValueError, match="expired"):
        validate_evidence(record, now=NOW)


def test_gitlab_attestation_rejects_expired_observation():
    record = ev("gitlab", parity="HEALTHY")
    comparison = compare_provider_evidence(
        None,
        record,
        gitlab_attestation=_live_gitlab_attestation(observed_at=NOW - timedelta(seconds=3601)),
        now=NOW,
    )
    assert comparison.disposition is EvidenceDisposition.DISCREPANCY_BLOCKED
