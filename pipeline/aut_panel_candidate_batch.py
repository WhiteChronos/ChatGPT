#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from pipeline.evolution_engine import classify_candidate_change

ROOT = Path(__file__).resolve().parents[1]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_changes_atomic(
    db_path: Path,
    *,
    candidate_id: str,
    changes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    policy = yaml.safe_load(
        (ROOT / "configs" / "auto_engineering_v1.yaml").read_text(encoding="utf-8")
    )
    required = ("change_type", "path", "before", "after", "evidence", "invalidates")
    for change in changes:
        missing = [key for key in required if key not in change]
        if missing:
            raise ValueError(f"missing change fields: {missing}")
        if not isinstance(change["invalidates"], list):
            raise ValueError("invalidates must be a list")
        if not isinstance(change["evidence"], dict):
            raise ValueError("evidence must be an object")
        if not classify_candidate_change(change, policy)["allowed"]:
            raise ValueError(
                f"change_type not authorized for candidate revision: {change.get('change_type')}"
            )

    now = _now_iso()
    results: list[dict[str, Any]] = []
    with _connect(db_path) as conn:
        candidate = conn.execute(
            "SELECT status FROM candidate_revisions WHERE candidate_id=?",
            (candidate_id,),
        ).fetchone()
        if candidate is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        if candidate["status"] == "ABANDONED":
            raise ValueError("cannot modify abandoned candidate")

        for change in changes:
            change_id = f"CHG-{uuid.uuid4().hex[:16].upper()}"
            conn.execute(
                """INSERT INTO candidate_revision_changes
                (change_id,candidate_id,change_type,path,before_json,after_json,evidence_json,
                 invalidates_json,created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    change_id,
                    candidate_id,
                    str(change["change_type"]),
                    str(change["path"]),
                    json.dumps(change["before"], ensure_ascii=False, sort_keys=True),
                    json.dumps(change["after"], ensure_ascii=False, sort_keys=True),
                    json.dumps(change["evidence"], ensure_ascii=False, sort_keys=True),
                    json.dumps(change["invalidates"], ensure_ascii=False),
                    now,
                ),
            )
            results.append(
                {
                    "change_id": change_id,
                    "candidate_id": candidate_id,
                    "change_type": change["change_type"],
                    "path": change["path"],
                    "before": change["before"],
                    "after": change["after"],
                    "evidence": change["evidence"],
                    "invalidates": list(change["invalidates"]),
                }
            )

        if changes:
            conn.execute(
                "UPDATE candidate_revisions SET status='IN_PROGRESS', updated_at=? WHERE candidate_id=?",
                (now, candidate_id),
            )
    return results
