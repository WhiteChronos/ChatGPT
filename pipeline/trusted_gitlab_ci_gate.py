"""Fail-closed, standard-library trusted GitLab CI attestation primitives.

This module is NOT proof of deployment or an authorization to mirror. A protected
separate GitLab project must execute a reviewed/pinned copy of this code, with
the mirrored subject checkout disabled and credential boundaries verified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Mapping

SHA = re.compile(r"^[0-9a-fA-F]{40}$")
DIGEST = re.compile(r"^[0-9a-fA-F]{64}$")
CONFIG = re.compile(r"^([A-Za-z0-9_./-]+\\.ya?ml)@([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+):([A-Za-z0-9_./-]+)$")
MIRROR = "chronoswhite-group/ChronosWhite-project"
SOURCE = "WhiteChronos/ChatGPT"
PROJECT_ID = 86465539
RECEIPT_FIELDS = frozenset({
    "schema_version", "transport", "source_repository", "target_project_path",
    "ref", "pipeline_ref", "source_sha", "target_sha", "timestamp", "worker_revision"
})


class GateState(StrEnum):
    BLOCKED = "BLOCKED"
    PREPARED = "PREPARED"  # configuration only, NOT evidence or live activation
    ATTESTED = "ATTESTED"  # synthetic/unit-test attestation, not live proof


def _sha(x: object) -> bool:
    return isinstance(x, str) and bool(SHA.fullmatch(x))


def check_configuration(
    mirror_project: Mapping[str, Any],
    verifier_branch: Mapping[str, Any],
    *,
    expected_project: str,
    expected_revision: str,
) -> GateState:
    """Check read-only provider snapshots; never mutate GitLab CI settings."""
    if not _sha(expected_revision) or expected_project == MIRROR:
        return GateState.BLOCKED
    if mirror_project.get("id") != PROJECT_ID or mirror_project.get("path_with_namespace") != MIRROR:
        return GateState.BLOCKED
    path = mirror_project.get("ci_config_path")
    if not isinstance(path, str):
        return GateState.BLOCKED
    match = CONFIG.fullmatch(path)
    if not match:
        return GateState.BLOCKED
    filename, project, branch = match.groups()
    if filename.startswith("/") or ".." in filename or project != expected_project:
        return GateState.BLOCKED
    if branch != verifier_branch.get("name"):
        return GateState.BLOCKED
    if not verifier_branch.get("protected") or verifier_branch.get("project_path") != project:
        return GateState.BLOCKED
    if verifier_branch.get("project_id") == PROJECT_ID:
        return GateState.BLOCKED
    sha = (verifier_branch.get("commit") or {}).get("id")
    if not _sha(sha) or sha.lower() != expected_revision.lower():
        return GateState.BLOCKED
    return GateState.PREPARED


def verify_authenticated_receipt(
    receipt: Mapping[str, Any], receipt_sha256: str, signature: str,
    *, signing_key: str, job: Mapping[str, Any], observed_head_sha: str,
    now: datetime | None = None,
) -> GateState:
    """Verify canonical receipt and provider job identity; no side effects."""
    if set(receipt) != RECEIPT_FIELDS:
        return GateState.BLOCKED
    if receipt.get("schema_version") != 1 or receipt.get("transport") != "neutral_worker":
        return GateState.BLOCKED
    if receipt.get("source_repository") != SOURCE or receipt.get("target_project_path") != MIRROR:
        return GateState.BLOCKED
    source_sha, target_sha, worker_sha = (receipt.get(k) for k in ("source_sha", "target_sha", "worker_revision"))
    if not all(_sha(x) for x in (source_sha, target_sha, worker_sha, observed_head_sha)):
        return GateState.BLOCKED
    if not isinstance(signing_key, str) or len(signing_key.encode("utf-8")) < 32:
        return GateState.BLOCKED
    if not isinstance(receipt_sha256, str) or not DIGEST.fullmatch(receipt_sha256):
        return GateState.BLOCKED
    if not isinstance(signature, str) or not DIGEST.fullmatch(signature):
        return GateState.BLOCKED
    ref, pipeline_ref = receipt.get("ref"), receipt.get("pipeline_ref")
    if not isinstance(ref, str) or ref != "main" or pipeline_ref != ref:
        return GateState.BLOCKED
    if source_sha.lower() != target_sha.lower() or source_sha.lower() != observed_head_sha.lower():
        return GateState.BLOCKED
    pipe = job.get("pipeline") or {}
    commit = job.get("commit") or {}
    if pipe.get("source") != "push" or pipe.get("project_id") != PROJECT_ID or not pipe.get("id"):
        return GateState.BLOCKED
    if job.get("tag") is not False or job.get("ref") != pipeline_ref:
        return GateState.BLOCKED
    if str(pipe.get("sha", "")).lower() != source_sha.lower() or str(commit.get("id", "")).lower() != source_sha.lower():
        return GateState.BLOCKED
    try:
        stamp = datetime.fromisoformat(str(receipt["timestamp"]).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            return GateState.BLOCKED
        current = now or datetime.now(timezone.utc)
        elapsed = (current - stamp).total_seconds()
        if elapsed < -300 or elapsed > 3600:
            return GateState.BLOCKED
        encoded = json.dumps(dict(receipt), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        expected_digest = hashlib.sha256(encoded).hexdigest()
        expected_signature = hmac.new(signing_key.encode(), bytes.fromhex(expected_digest), hashlib.sha256).hexdigest()
    except (ValueError, TypeError, KeyError, OverflowError):
        return GateState.BLOCKED
    if not hmac.compare_digest(receipt_sha256.lower(), expected_digest):
        return GateState.BLOCKED
    if not hmac.compare_digest(signature.lower(), expected_signature):
        return GateState.BLOCKED
    return GateState.ATTESTED
