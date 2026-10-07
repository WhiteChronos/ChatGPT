from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
import json
from pathlib import Path
import re
import sys

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.gitlab_contingency_policy import GitLabContingencyPolicy, classify_ref, load_policy

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class MirrorParityStatus(StrEnum):
    HEALTHY = "HEALTHY"
    STALE = "STALE"
    DIVERGED = "DIVERGED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class MirrorParityInput:
    github_repository: str
    gitlab_project_id: int
    gitlab_project_path: str
    ref_name: str
    github_sha: str | None
    gitlab_sha: str | None
    ci_subject_sha: str | None
    github_available: bool
    gitlab_available: bool
    receipt_timestamp: datetime
    evaluated_at: datetime


@dataclass(frozen=True)
class MirrorParityResult:
    status: MirrorParityStatus
    evidence_eligible: bool
    reason: str


def _valid_sha(value: str | None) -> bool:
    return bool(value and _SHA_RE.fullmatch(value))


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(timezone.utc)


def evaluate_mirror_parity(value: MirrorParityInput, policy: GitLabContingencyPolicy) -> MirrorParityResult:
    ref_decision = classify_ref(value.ref_name, policy)
    if not ref_decision.eligible:
        return MirrorParityResult(MirrorParityStatus.DIVERGED, False, "mirror ref is not eligible under policy")
    if not value.github_available or not value.gitlab_available:
        return MirrorParityResult(MirrorParityStatus.UNAVAILABLE, False, "required provider observation unavailable")
    if policy.provisioning_state != "PROVISIONED" or not policy.gitlab_project_id or not policy.gitlab_project_path:
        return MirrorParityResult(MirrorParityStatus.UNAVAILABLE, False, "GitLab mirror identity is not provisioned")
    if value.github_repository != policy.source_repository:
        return MirrorParityResult(MirrorParityStatus.DIVERGED, False, "GitHub repository identity mismatch")
    if value.gitlab_project_id != policy.gitlab_project_id or value.gitlab_project_path != policy.gitlab_project_path:
        return MirrorParityResult(MirrorParityStatus.DIVERGED, False, "GitLab project identity mismatch")
    if not all(_valid_sha(v) for v in (value.github_sha, value.gitlab_sha, value.ci_subject_sha)):
        return MirrorParityResult(MirrorParityStatus.UNAVAILABLE, False, "one or more commit SHAs are unavailable or malformed")
    if len({value.github_sha.lower(), value.gitlab_sha.lower(), value.ci_subject_sha.lower()}) != 1:
        return MirrorParityResult(MirrorParityStatus.DIVERGED, False, "provider or CI subject SHA mismatch")
    receipt = _aware(value.receipt_timestamp)
    evaluated = _aware(value.evaluated_at)
    age = (evaluated - receipt).total_seconds()
    if age > policy.mirror_freshness_seconds or age < -policy.max_clock_skew_seconds:
        return MirrorParityResult(MirrorParityStatus.STALE, False, "mirror receipt is outside the accepted freshness window")
    return MirrorParityResult(MirrorParityStatus.HEALTHY, True, "provider identities and exact commit SHAs match")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--policy", default="governance/GITLAB_CONTINGENCY_CI_POLICY.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
        value = MirrorParityInput(
            github_repository=raw["github_repository"],
            gitlab_project_id=int(raw["gitlab_project_id"]),
            gitlab_project_path=raw["gitlab_project_path"],
            ref_name=raw["ref_name"],
            github_sha=raw.get("github_sha"),
            gitlab_sha=raw.get("gitlab_sha"),
            ci_subject_sha=raw.get("ci_subject_sha"),
            github_available=bool(raw["github_available"]),
            gitlab_available=bool(raw["gitlab_available"]),
            receipt_timestamp=_parse_dt(raw["receipt_timestamp"]),
            evaluated_at=datetime.now(timezone.utc),
        )
        result = evaluate_mirror_parity(value, load_policy(Path(args.policy)))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True) if args.json else f"ERROR: {exc}")
        return 1
    payload = {**asdict(result), "status": result.status.value}
    print(json.dumps(payload, sort_keys=True) if args.json else payload)
    return {
        MirrorParityStatus.HEALTHY: 0,
        MirrorParityStatus.STALE: 2,
        MirrorParityStatus.DIVERGED: 3,
        MirrorParityStatus.UNAVAILABLE: 4,
    }[result.status]


if __name__ == "__main__":
    raise SystemExit(main())
