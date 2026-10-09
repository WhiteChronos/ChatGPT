"""Stdlib-only, fail-closed GitHub -> GitLab mirror policy projection.

Credentialled GitHub Actions workers must not import mutable third-party packages.
This is a deliberately narrow read-only projection of the canonical policy
for the mirror transport; the full JSON Schema gate remains elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class TrustedMirrorPolicy:
    source_repository: str
    gitlab_project_path: str
    allowed_mirror_ref_classes: tuple[str, ...]


@dataclass(frozen=True)
class RefDecision:
    ref_name: str
    eligible: bool
    reason: str


_EXPECTED = {
    "schema_version": 1,
    "authority_provider": "github",
    "mirror_provider": "gitlab",
    "mirror_direction": "github_to_gitlab",
    "active_failover": False,
    "gitlab_merge_authority": False,
    "gitlab_deploy_authority": False,
    "source_repository": "WhiteChronos/ChatGPT",
    "evidence_requires_exact_sha": True,
    "provisioning_state": "PROVISIONED",
    "gitlab_project_id": 86465539,
    "gitlab_project_path": "chronoswhite-group/ChronosWhite-project",
    "mirror_transport": "neutral_worker",
    "mirror_divergence_behavior": "FAIL_CLOSED",
    "provider_disagreement_behavior": "BLOCK_FOR_INVESTIGATION",
}
_ALLOWED_REFS = ("main", "spec/*", "plan/*", "feat/*", "fix/*", "release/*")


def load_policy(path: Path) -> TrustedMirrorPolicy:
    target = Path(path)
    if ".." in target.parts:
        raise ValueError("mirror policy path traversal forbidden")
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError("mirror policy unavailable or malformed") from exc
    if type(raw) is not dict:
        raise ValueError("mirror policy must be a JSON object")
    for field, required in _EXPECTED.items():
        if type(raw.get(field)) is not type(required) or raw.get(field) != required:
            raise ValueError(f"mirror policy invariant violated: {field}")
    classes = raw.get("allowed_mirror_ref_classes")
    if type(classes) is not list or classes != list(_ALLOWED_REFS):
        raise ValueError("mirror ref eligibility policy diverged from reviewed contract")
    retry = raw.get("infrastructure_retry")
    if type(retry) is not dict or type(retry.get("limit")) is not int:
        raise ValueError("mirror retry policy is invalid")
    return TrustedMirrorPolicy(
        source_repository=raw["source_repository"],
        gitlab_project_path=raw["gitlab_project_path"],
        allowed_mirror_ref_classes=tuple(classes),
    )


def classify_ref(ref_name: str, policy: TrustedMirrorPolicy) -> RefDecision:
    if not isinstance(ref_name, str):
        return RefDecision("", False, "ref must be a string")
    raw = ref_name.strip()
    if raw.startswith("refs/heads/"):
        raw = raw[len("refs/heads/"):]
    if not raw or raw.startswith("refs/") or ".." in raw.split("/"):
        return RefDecision(ref_name, False, "unsafe or missing head ref")
    if any(c in raw for c in (" ", "\t", "\r", "\n", "\0", "~", "^", ":", "?", "*", "[", "\\")) or raw.endswith(("/", ".", ".lock")):
        return RefDecision(ref_name, False, "unsafe git ref characters")
    if raw == "main":
        return RefDecision(raw, True, "authoritative main")
    for item in policy.allowed_mirror_ref_classes:
        if item.endswith("*") and raw.startswith(item[:-1]) and raw != item[:-1]:
            return RefDecision(raw, True, f"eligible by {item}")
    return RefDecision(raw, False, "ref class not eligible")
