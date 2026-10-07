from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import re

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_PROVIDERS = {"github", "gitlab", "local"}
_RESULTS = {"PASS", "FAIL", "UNAVAILABLE"}


@dataclass(frozen=True)
class CIProviderEvidence:
    provider: str
    repository_identity: str
    subject_sha: str
    pipeline_or_run_id: str
    gate_name: str
    result: str
    timestamp: datetime
    ci_config_revision: str
    mirror_parity_status: str
    attempt: int


class EvidenceDisposition(StrEnum):
    CORROBORATED = "CORROBORATED"
    DISCREPANCY_BLOCKED = "DISCREPANCY_BLOCKED"
    CONTINGENCY_EVIDENCE_ONLY = "CONTINGENCY_EVIDENCE_ONLY"
    PRIMARY_EVIDENCE_ONLY = "PRIMARY_EVIDENCE_ONLY"
    GITLAB_EVIDENCE_INELIGIBLE = "GITLAB_EVIDENCE_INELIGIBLE"
    SUBJECT_MISMATCH_BLOCKED = "SUBJECT_MISMATCH_BLOCKED"


@dataclass(frozen=True)
class EvidenceComparison:
    disposition: EvidenceDisposition
    reason: str


def validate_evidence(record: CIProviderEvidence, *, now: datetime | None = None) -> None:
    if record.provider not in _PROVIDERS:
        raise ValueError(f"unknown CI provider: {record.provider}")
    if not record.repository_identity.strip() or not record.pipeline_or_run_id.strip() or not record.gate_name.strip():
        raise ValueError("evidence identity fields must be nonblank")
    if not _SHA_RE.fullmatch(record.subject_sha):
        raise ValueError("subject_sha must be a 40-character hexadecimal Git SHA")
    if record.result not in _RESULTS:
        raise ValueError(f"invalid CI result: {record.result}")
    if record.attempt < 1:
        raise ValueError("attempt must be >= 1")
    if record.timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    observed = record.timestamp.astimezone(timezone.utc)
    if (observed - current).total_seconds() > 300:
        raise ValueError("evidence timestamp exceeds allowed future clock skew")
    if record.provider == "gitlab" and record.mirror_parity_status != "HEALTHY":
        raise ValueError("GitLab evidence is ineligible unless mirror parity is HEALTHY")
    if record.provider != "gitlab" and record.mirror_parity_status not in {"NOT_APPLICABLE", "HEALTHY"}:
        raise ValueError("non-GitLab evidence has invalid mirror parity status")


def compare_provider_evidence(
    github: CIProviderEvidence | None,
    gitlab: CIProviderEvidence | None,
) -> EvidenceComparison:
    if gitlab is not None and gitlab.mirror_parity_status != "HEALTHY":
        return EvidenceComparison(
            EvidenceDisposition.GITLAB_EVIDENCE_INELIGIBLE,
            "GitLab mirror parity is not HEALTHY",
        )
    if github is not None and gitlab is not None and github.subject_sha.lower() != gitlab.subject_sha.lower():
        return EvidenceComparison(
            EvidenceDisposition.SUBJECT_MISMATCH_BLOCKED,
            "provider evidence subjects are different commit SHAs",
        )
    if github is not None:
        validate_evidence(github)
    if gitlab is not None:
        validate_evidence(gitlab)
    if github is None and gitlab is not None:
        return EvidenceComparison(
            EvidenceDisposition.CONTINGENCY_EVIDENCE_ONLY,
            "GitHub evidence is unavailable; GitLab evidence has no merge authority",
        )
    if github is not None and gitlab is None:
        return EvidenceComparison(
            EvidenceDisposition.PRIMARY_EVIDENCE_ONLY,
            "GitLab evidence is unavailable",
        )
    if github is None and gitlab is None:
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            "no provider evidence is available",
        )
    assert github is not None and gitlab is not None
    if github.result != gitlab.result:
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            "providers disagree for the same commit SHA",
        )
    return EvidenceComparison(
        EvidenceDisposition.CORROBORATED,
        "providers agree for the same commit SHA",
    )

class FailureClass(StrEnum):
    PROVIDER_INFRA_FAILURE = "PROVIDER_INFRA_FAILURE"
    RUNNER_ASSIGNMENT_FAILURE = "RUNNER_ASSIGNMENT_FAILURE"
    CODE_FAILURE = "CODE_FAILURE"
    POLICY_FAILURE = "POLICY_FAILURE"
    MIRROR_FAILURE = "MIRROR_FAILURE"
    UNKNOWN = "UNKNOWN"


class RetryDisposition(StrEnum):
    RETRY_ELIGIBLE = "RETRY_ELIGIBLE"
    RETRY_LIMIT_REACHED = "RETRY_LIMIT_REACHED"
    NOT_RETRY_ELIGIBLE = "NOT_RETRY_ELIGIBLE"


def classify_retry(failure: FailureClass, attempt: int, policy) -> RetryDisposition:
    if attempt < 1:
        raise ValueError("attempt must be >= 1")
    if failure.value not in policy.infrastructure_retry_eligible_failures:
        return RetryDisposition.NOT_RETRY_ELIGIBLE
    if attempt >= policy.infrastructure_retry_limit:
        return RetryDisposition.RETRY_LIMIT_REACHED
    return RetryDisposition.RETRY_ELIGIBLE
