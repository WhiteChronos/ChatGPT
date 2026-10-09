from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_PROVIDERS = {"github", "gitlab", "local"}
_RESULTS = {"PASS", "FAIL", "UNAVAILABLE"}
_EVIDENCE_MAX_AGE_SECONDS = 3600
_MAX_FUTURE_CLOCK_SKEW_SECONDS = 300
_EXPECTED_REPOSITORY_IDENTITIES = {
    "github": "WhiteChronos/ChatGPT",
    "gitlab": "chronoswhite-group/ChronosWhite-project",
}
_PROVENANCE_FIELDS = (
    "provider",
    "repository_identity",
    "subject_sha",
    "pipeline_or_run_id",
    "gate_name",
    "result",
    "timestamp",
    "ci_config_revision",
    "mirror_parity_status",
    "attempt",
    "input_artifacts_sha256",
)


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
    input_artifacts_sha256: dict[str, str]
    provenance_sha256: str
    worker_revision: str | None = None
    schema_version: int = 2


def compute_provenance_sha256(record: CIProviderEvidence | Mapping[str, object]) -> str:
    """Retain historical v1 digests; bind worker revision and version in v2."""
    def read(key: str, default: object = None):
        if isinstance(record, Mapping):
            return record.get(key, default)
        return getattr(record, key, default)

    version = read("schema_version")
    if version is None:
        version = 2 if read("worker_revision") is not None else 1
    if type(version) is not int or version not in (1, 2):
        raise ValueError("unsupported evidence schema version")
    payload: dict[str, object] = {}
    for key in _PROVENANCE_FIELDS:
        value = read(key)
        if key == "timestamp" and isinstance(value, datetime):
            value = value.isoformat()
        if key in {"subject_sha", "ci_config_revision"}:
            value = str(value).lower()
        payload[key] = value
    if version == 2:
        revision = read("worker_revision")
        if not isinstance(revision, str) or not _SHA_RE.fullmatch(revision):
            raise ValueError("v2 evidence requires a valid worker revision")
        payload["worker_revision"] = revision.lower()
        payload["schema_version"] = 2
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_evidence_json(path: Path) -> CIProviderEvidence:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    timestamp = raw.get("timestamp")
    if isinstance(timestamp, str):
        raw["timestamp"] = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    raw.setdefault("schema_version", 2 if "worker_revision" in raw else 1)
    return CIProviderEvidence(**raw)


class EvidenceDisposition(StrEnum):
    CORROBORATED = "CORROBORATED"
    DISCREPANCY_BLOCKED = "DISCREPANCY_BLOCKED"
    CONTINGENCY_EVIDENCE_ONLY = "CONTINGENCY_EVIDENCE_ONLY"
    PRIMARY_EVIDENCE_ONLY = "PRIMARY_EVIDENCE_ONLY"
    GITLAB_EVIDENCE_INELIGIBLE = "GITLAB_EVIDENCE_INELIGIBLE"
    GITLAB_LIVE_VERIFICATION_REQUIRED = "GITLAB_LIVE_VERIFICATION_REQUIRED"
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
    expected_identity = _EXPECTED_REPOSITORY_IDENTITIES.get(record.provider)
    if expected_identity is not None and record.repository_identity != expected_identity:
        raise ValueError("provider repository identity does not match the configured evidence source")
    if not _SHA_RE.fullmatch(record.subject_sha):
        raise ValueError("subject_sha must be a 40-character hexadecimal Git SHA")
    if not _SHA_RE.fullmatch(record.ci_config_revision):
        raise ValueError("ci_config_revision must be a 40-character hexadecimal Git SHA")
    if type(record.schema_version) is not int or record.schema_version not in (1, 2):
        raise ValueError("unsupported evidence schema version")
    if record.schema_version == 1:
        if record.worker_revision is not None:
            raise ValueError("legacy v1 evidence must not declare worker revision")
    elif not isinstance(record.worker_revision, str) or not _SHA_RE.fullmatch(record.worker_revision):
        raise ValueError("v2 worker_revision must be a 40-character hexadecimal Git SHA")
    if not _SHA256_RE.fullmatch(record.provenance_sha256):
        raise ValueError("provenance_sha256 must be a 64-character hexadecimal SHA-256 digest")
    if record.provenance_sha256.lower() != compute_provenance_sha256(record):
        raise ValueError("provenance_sha256 does not match the complete evidence record")
    if record.result not in _RESULTS:
        raise ValueError(f"invalid CI result: {record.result}")
    if type(record.attempt) is not int:
        raise ValueError("attempt must be an integer")
    if record.attempt < 1:
        raise ValueError("attempt must be >= 1")
    for name, digest in record.input_artifacts_sha256.items():
        if not str(name).strip() or not _SHA256_RE.fullmatch(str(digest)):
            raise ValueError("input artifact digests must be named SHA-256 values")
    if record.provider == "gitlab":
        required_inputs = {
            "mirror-input.json",
            "mirror-parity.json",
            "gitlab-runtime-identity.json",
            "contingency-python.json",
            "contingency-broker.json",
            "mirror-parity-final.json",
        }
        if set(record.input_artifacts_sha256) != required_inputs:
            raise ValueError("GitLab evidence must bind every required input artifact")
    if record.timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    observed = record.timestamp.astimezone(timezone.utc)
    if (observed - current).total_seconds() > _MAX_FUTURE_CLOCK_SKEW_SECONDS:
        raise ValueError("evidence timestamp exceeds allowed future clock skew")
    if (current - observed).total_seconds() > _EVIDENCE_MAX_AGE_SECONDS:
        raise ValueError("evidence timestamp is expired")
    if record.provider == "gitlab" and record.mirror_parity_status != "HEALTHY":
        raise ValueError("GitLab evidence is ineligible unless mirror parity is HEALTHY")
    if record.provider != "gitlab" and record.mirror_parity_status not in {"NOT_APPLICABLE", "HEALTHY"}:
        raise ValueError("non-GitLab evidence has invalid mirror parity status")


def compare_provider_evidence(
    github: CIProviderEvidence | None,
    gitlab: CIProviderEvidence | None,
    *,
    gitlab_live_verified: bool = False,
    now: datetime | None = None,
) -> EvidenceComparison:
    if type(gitlab_live_verified) is not bool:
        raise ValueError("gitlab_live_verified must be a boolean")
    if github is not None and github.provider != "github":
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            'GitHub evidence slot requires provider="github"',
        )
    if gitlab is not None and gitlab.provider != "gitlab":
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            'GitLab evidence slot requires provider="gitlab"',
        )
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
    if github is not None and github.repository_identity != _EXPECTED_REPOSITORY_IDENTITIES["github"]:
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            "GitHub evidence repository identity is not authoritative",
        )
    if gitlab is not None and gitlab.repository_identity != _EXPECTED_REPOSITORY_IDENTITIES["gitlab"]:
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            "GitLab evidence repository identity is not the provisioned mirror",
        )
    if github is not None and gitlab is not None:
        if github.gate_name != gitlab.gate_name:
            return EvidenceComparison(
                EvidenceDisposition.DISCREPANCY_BLOCKED,
                "provider evidence gate names do not match",
            )
        if github.ci_config_revision.lower() != gitlab.ci_config_revision.lower():
            return EvidenceComparison(
                EvidenceDisposition.DISCREPANCY_BLOCKED,
                "provider CI configuration revisions do not match",
            )
    if github is not None:
        validate_evidence(github, now=now)
    if gitlab is not None:
        validate_evidence(gitlab, now=now)
    if github is not None and gitlab is not None and github.result != gitlab.result:
        return EvidenceComparison(
            EvidenceDisposition.DISCREPANCY_BLOCKED,
            "providers disagree for the same commit SHA",
        )
    if gitlab is not None and not gitlab_live_verified:
        return EvidenceComparison(
            EvidenceDisposition.GITLAB_LIVE_VERIFICATION_REQUIRED,
            "persisted GitLab evidence requires independent authenticated live provider verification",
        )
    if github is None and gitlab is not None:
        return EvidenceComparison(
            EvidenceDisposition.CONTINGENCY_EVIDENCE_ONLY,
            "GitLab evidence was live-verified in an authenticated provider runtime; it has no merge authority",
        )
    if github is not None and gitlab is not None:
        return EvidenceComparison(
            EvidenceDisposition.CORROBORATED,
            "providers agree for the same commit SHA after authenticated live GitLab verification",
        )
    if github is not None:
        return EvidenceComparison(
            EvidenceDisposition.PRIMARY_EVIDENCE_ONLY,
            "GitLab evidence is unavailable",
        )
    return EvidenceComparison(
        EvidenceDisposition.DISCREPANCY_BLOCKED,
        "no provider evidence is available",
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
