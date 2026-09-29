#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _next_candidate_revision(conn: sqlite3.Connection, panel_id: str, source_revision: str) -> str:
    rows = conn.execute(
        "SELECT candidate_revision FROM candidate_revisions WHERE panel_id=? AND source_revision=?",
        (panel_id, source_revision),
    ).fetchall()
    used: set[int] = set()
    prefix = f"{source_revision}-C"
    for row in rows:
        value = str(row["candidate_revision"])
        if value.startswith(prefix):
            suffix = value[len(prefix):]
            if suffix.isdigit():
                used.add(int(suffix))
    n = 1
    while n in used:
        n += 1
    return f"{source_revision}-C{n:03d}"


def create_candidate(
    db_path: Path,
    *,
    panel_id: str,
    source_revision: str,
    trigger: dict[str, Any],
    canonical_inputs: dict[str, str],
) -> dict[str, Any]:
    if not trigger.get("type"):
        raise ValueError("trigger.type is required")
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in canonical_inputs.items()):
        raise ValueError("canonical_inputs must map strings to strings")

    candidate_id = f"CAND-{uuid.uuid4().hex[:16].upper()}"
    now = _now_iso()
    with _connect(db_path) as conn:
        source = conn.execute(
            "SELECT panel_id, revision FROM panels WHERE panel_id=? AND revision=?",
            (panel_id, source_revision),
        ).fetchone()
        if source is None:
            raise ValueError(f"source panel revision not found: {panel_id} {source_revision}")
        candidate_revision = _next_candidate_revision(conn, panel_id, source_revision)
        conn.execute(
            """INSERT INTO candidate_revisions
            (candidate_id,panel_id,source_revision,candidate_revision,status,trigger_type,
             trigger_json,canonical_inputs_json,rollback_target,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                candidate_id,
                panel_id,
                source_revision,
                candidate_revision,
                "DRAFT",
                str(trigger["type"]),
                json.dumps(trigger, ensure_ascii=False, sort_keys=True),
                json.dumps(canonical_inputs, ensure_ascii=False, sort_keys=True),
                source_revision,
                now,
                now,
            ),
        )

    return {
        "candidate_id": candidate_id,
        "panel_id": panel_id,
        "source_revision": source_revision,
        "candidate_revision": candidate_revision,
        "status": "DRAFT",
        "trigger": trigger,
        "canonical_inputs": canonical_inputs,
        "rollback_target": source_revision,
        "historical_source_mutation_allowed": False,
    }


def apply_change(
    db_path: Path,
    *,
    candidate_id: str,
    change: dict[str, Any],
) -> dict[str, Any]:
    required = ("change_type", "path", "before", "after", "evidence", "invalidates")
    missing = [key for key in required if key not in change]
    if missing:
        raise ValueError(f"missing change fields: {missing}")
    if not isinstance(change["invalidates"], list):
        raise ValueError("invalidates must be a list")
    if not isinstance(change["evidence"], dict):
        raise ValueError("evidence must be an object")

    from pipeline.evolution_engine import classify_candidate_change
    policy = yaml.safe_load(
        (ROOT / "configs" / "auto_engineering_v1.yaml").read_text(encoding="utf-8")
    )
    decision = classify_candidate_change(change, policy)
    if not decision["allowed"]:
        raise ValueError(
            f"change_type not authorized for candidate revision: {change.get('change_type')}"
        )

    change_id = f"CHG-{uuid.uuid4().hex[:16].upper()}"
    now = _now_iso()
    with _connect(db_path) as conn:
        candidate = conn.execute(
            "SELECT status FROM candidate_revisions WHERE candidate_id=?",
            (candidate_id,),
        ).fetchone()
        if candidate is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        if candidate["status"] == "ABANDONED":
            raise ValueError("cannot modify abandoned candidate")

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
        conn.execute(
            "UPDATE candidate_revisions SET status='IN_PROGRESS', updated_at=? WHERE candidate_id=?",
            (now, candidate_id),
        )

    return {
        "change_id": change_id,
        "candidate_id": candidate_id,
        "change_type": change["change_type"],
        "path": change["path"],
        "before": change["before"],
        "after": change["after"],
        "evidence": change["evidence"],
        "invalidates": list(change["invalidates"]),
    }


def rollback_candidate(
    db_path: Path,
    *,
    candidate_id: str,
    reason: str,
) -> dict[str, Any]:
    if not reason.strip():
        raise ValueError("rollback reason is required")
    now = _now_iso()
    with _connect(db_path) as conn:
        candidate = conn.execute(
            "SELECT candidate_id,rollback_target FROM candidate_revisions WHERE candidate_id=?",
            (candidate_id,),
        ).fetchone()
        if candidate is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        conn.execute(
            "UPDATE candidate_revisions SET status='ABANDONED', updated_at=? WHERE candidate_id=?",
            (now, candidate_id),
        )
    return {
        "candidate_id": candidate_id,
        "status": "ABANDONED",
        "rollback_target": candidate["rollback_target"],
        "reason": reason,
    }
