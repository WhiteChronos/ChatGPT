from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import jsonschema


@dataclass(frozen=True)
class GitLabContingencyPolicy:
    schema_version: int
    authority_provider: str
    mirror_provider: str
    mirror_direction: str
    active_failover: bool
    gitlab_merge_authority: bool
    gitlab_deploy_authority: bool
    source_repository: str
    evidence_requires_exact_sha: bool
    mirror_freshness_seconds: int
    max_clock_skew_seconds: int
    provisioning_state: str
    gitlab_project_id: int | None
    gitlab_project_path: str | None
    mirror_transport: str | None
    mirror_divergence_behavior: str
    provider_disagreement_behavior: str
    allowed_evidence_providers: tuple[str, ...]
    allowed_mirror_ref_classes: tuple[str, ...]
    infrastructure_retry_limit: int
    infrastructure_retry_eligible_failures: tuple[str, ...]


def _schema_path(policy_path: Path) -> Path:
    candidate = policy_path.resolve().parent.parent / "schemas" / "gitlab_contingency_ci.schema.json"
    if candidate.exists():
        return candidate
    repo_candidate = Path(__file__).resolve().parents[1] / "schemas" / "gitlab_contingency_ci.schema.json"
    return repo_candidate


def _policy_from_raw(raw: dict[str, Any]) -> GitLabContingencyPolicy:
    retry = raw["infrastructure_retry"]
    return GitLabContingencyPolicy(
        schema_version=raw["schema_version"],
        authority_provider=raw["authority_provider"],
        mirror_provider=raw["mirror_provider"],
        mirror_direction=raw["mirror_direction"],
        active_failover=raw["active_failover"],
        gitlab_merge_authority=raw["gitlab_merge_authority"],
        gitlab_deploy_authority=raw["gitlab_deploy_authority"],
        source_repository=raw["source_repository"],
        evidence_requires_exact_sha=raw["evidence_requires_exact_sha"],
        mirror_freshness_seconds=raw["mirror_freshness_seconds"],
        max_clock_skew_seconds=raw["max_clock_skew_seconds"],
        provisioning_state=raw["provisioning_state"],
        gitlab_project_id=raw["gitlab_project_id"],
        gitlab_project_path=raw["gitlab_project_path"],
        mirror_transport=raw["mirror_transport"],
        mirror_divergence_behavior=raw["mirror_divergence_behavior"],
        provider_disagreement_behavior=raw["provider_disagreement_behavior"],
        allowed_evidence_providers=tuple(raw["allowed_evidence_providers"]),
        allowed_mirror_ref_classes=tuple(raw["allowed_mirror_ref_classes"]),
        infrastructure_retry_limit=retry["limit"],
        infrastructure_retry_eligible_failures=tuple(retry["eligible_failures"]),
    )


def load_policy(path: Path) -> GitLabContingencyPolicy:
    path = Path(path)
    if ".." in path.parts:
        raise ValueError("policy path traversal is not allowed")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        schema = json.loads(_schema_path(path).read_text(encoding="utf-8"))
        jsonschema.validate(raw, schema)
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError, KeyError, TypeError) as exc:
        raise ValueError(f"invalid GitLab contingency policy: {exc}") from exc
    return _policy_from_raw(raw)


@dataclass(frozen=True)
class RefDecision:
    ref_name: str
    eligible: bool
    reason: str


def classify_ref(ref_name: str, policy: GitLabContingencyPolicy) -> RefDecision:
    # No ref may be mirror-eligible when contingency mirroring is disabled.
    if policy.provisioning_state != "PROVISIONED":
        return RefDecision(ref_name, False, "GitLab mirroring disabled by policy")
    raw = ref_name.strip()
    if raw.startswith("refs/heads/"):
        raw = raw[len("refs/heads/"):]
    if not raw:
        return RefDecision(ref_name, False, "empty ref")
    if ".." in raw.split("/") or raw.startswith("refs/"):
        return RefDecision(ref_name, False, "unsafe or non-head ref")
    if raw == "main":
        return RefDecision(raw, True, "authoritative default branch")
    for pattern in policy.allowed_mirror_ref_classes:
        if pattern.endswith("*") and raw.startswith(pattern[:-1]):
            return RefDecision(raw, True, f"allowed by {pattern}")
    return RefDecision(raw, False, "ref class not eligible")


def ref_is_mirror_eligible(ref_name: str, policy: GitLabContingencyPolicy) -> bool:
    return classify_ref(ref_name, policy).eligible
