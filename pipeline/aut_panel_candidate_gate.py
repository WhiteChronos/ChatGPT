#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _valid_hashes(values: dict[str, Any] | None) -> bool:
    return bool(values) and all(
        isinstance(value, str) and bool(_SHA256_RE.fullmatch(value))
        for value in values.values()
    )


def _valid_approval(record: dict[str, Any] | None) -> bool:
    if not isinstance(record, dict):
        return False
    required = ("approval_id", "approver", "approved_at", "reference")
    return record.get("human_approved") is True and all(
        isinstance(record.get(key), str) and record[key].strip() for key in required
    )


def evaluate_candidate(
    candidate_manifest: dict[str, Any],
    approval_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_id = str(candidate_manifest.get("candidate_id") or "")
    base = {
        "candidate_id": candidate_id,
        "release_executed": False,
        "human_release_required": True,
    }

    forbidden = [
        key
        for key in ("release_executed", "auto_merge", "production_plc_download")
        if candidate_manifest.get(key) is True
    ]
    if forbidden:
        return {
            **base,
            "status": "REPROVADO",
            "reasons": [f"forbidden side effect requested: {key}" for key in forbidden],
        }

    if candidate_manifest.get("deterministic_status") == "REPROVADO":
        return {
            **base,
            "status": "REPROVADO",
            "reasons": ["deterministic gate rejected candidate"],
        }

    holds = list(candidate_manifest.get("blocking_holds") or [])
    if candidate_manifest.get("qa_status") != "PASS":
        holds.append("QA_NOT_PASS")
    if not _valid_hashes(candidate_manifest.get("source_hashes")):
        holds.append("SOURCE_HASHES_MISSING_OR_INVALID")
    if not _valid_hashes(candidate_manifest.get("artifact_hashes")):
        holds.append("ARTIFACT_HASHES_MISSING_OR_INVALID")
    if not str(candidate_manifest.get("rollback_target") or "").strip():
        holds.append("ROLLBACK_TARGET_MISSING")

    if holds:
        return {
            **base,
            "status": "HOLD",
            "reasons": holds,
        }

    if approval_record is None:
        return {
            **base,
            "status": "CANDIDATE_READY_FOR_HUMAN_REVIEW",
            "reasons": [],
        }

    if not _valid_approval(approval_record):
        return {
            **base,
            "status": "HOLD",
            "reasons": ["INVALID_HUMAN_APPROVAL_RECORD"],
        }

    return {
        **base,
        "status": "RELEASE_AUTHORIZED_BY_HUMAN",
        "approval_record_id": approval_record["approval_id"],
        "approval_reference": approval_record["reference"],
        "reasons": [],
    }
