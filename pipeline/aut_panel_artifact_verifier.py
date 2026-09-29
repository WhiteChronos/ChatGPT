#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_bundle(
    bundle_dir: Path,
    *,
    expected_commit_sha: str,
    expected_candidate_id: str,
) -> dict[str, Any]:
    errors: list[str] = []
    holds: list[str] = []
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.is_file():
        return {"status": "REPROVADO", "errors": ["MANIFEST_MISSING"], "verified_artifacts": 0}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidate_id") != expected_candidate_id:
        errors.append("CANDIDATE_ID_MISMATCH")
    if manifest.get("source_commit_sha") != expected_commit_sha:
        errors.append("SOURCE_COMMIT_MISMATCH")

    source_hashes = manifest.get("source_hashes") or {}
    if not source_hashes:
        holds.append("SOURCE_HASHES_MISSING")

    if (manifest.get("bom_counts") or {}) != (manifest.get("render_counts") or {}):
        errors.append("BOM_RENDER_COUNT_MISMATCH")

    qa = manifest.get("qa") or {}
    if qa.get("status") != "PASS":
        errors.append("QA_NOT_PASS")
    if qa.get("candidate_id") != expected_candidate_id:
        errors.append("QA_CANDIDATE_ID_MISMATCH")
    if qa.get("source_commit_sha") != expected_commit_sha:
        errors.append("QA_SOURCE_COMMIT_MISMATCH")

    verified = 0
    for artifact in manifest.get("artifacts") or []:
        rel = str(artifact.get("path") or "")
        expected = str(artifact.get("sha256") or "")
        path = bundle_dir / rel
        if not rel or not path.is_file():
            errors.append(f"ARTIFACT_MISSING:{rel}")
            continue
        if _sha256(path).lower() != expected.lower():
            errors.append(f"ARTIFACT_HASH_MISMATCH:{rel}")
            continue
        verified += 1

    if errors:
        status = "REPROVADO"
        combined = errors + holds
    elif holds:
        status = "HOLD"
        combined = holds
    else:
        status = "PASS"
        combined = []

    return {
        "status": status,
        "errors": combined,
        "verified_artifacts": verified,
        "candidate_id": manifest.get("candidate_id"),
        "source_commit_sha": manifest.get("source_commit_sha"),
    }
