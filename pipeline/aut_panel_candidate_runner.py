#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import yaml


def build_candidate_execution_plan(
    candidate: dict[str, Any],
    pipeline_contract: dict[str, Any],
) -> list[str]:
    ordered = [
        str(stage["id"])
        for stage in sorted(
            pipeline_contract.get("sequence") or [],
            key=lambda x: int(x.get("order", 0)),
        )
    ]
    known = set(ordered)
    requested: set[str] = set()
    for change in candidate.get("changes") or []:
        for stage in change.get("invalidates") or []:
            stage_id = str(stage)
            if stage_id not in known:
                raise ValueError(f"unknown invalidated stage: {stage_id}")
            requested.add(stage_id)
    requested.discard("RELEASE")
    return [stage for stage in ordered if stage in requested]


def _load_candidate(db_path: Path, candidate_id: str) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM candidate_revisions WHERE candidate_id=?",
            (candidate_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        changes = conn.execute(
            "SELECT * FROM candidate_revision_changes WHERE candidate_id=? ORDER BY created_at, change_id",
            (candidate_id,),
        ).fetchall()
        return {
            "candidate_id": row["candidate_id"],
            "panel_id": row["panel_id"],
            "source_revision": row["source_revision"],
            "candidate_revision": row["candidate_revision"],
            "status": row["status"],
            "rollback_target": row["rollback_target"],
            "changes": [
                {
                    "change_id": c["change_id"],
                    "change_type": c["change_type"],
                    "path": c["path"],
                    "before": json.loads(c["before_json"]) if c["before_json"] else None,
                    "after": json.loads(c["after_json"]) if c["after_json"] else None,
                    "evidence": json.loads(c["evidence_json"] or "{}"),
                    "invalidates": json.loads(c["invalidates_json"] or "[]"),
                }
                for c in changes
            ],
        }
    finally:
        conn.close()


def run_candidate(
    candidate_id: str,
    *,
    root: Path,
    db_path: Path,
) -> dict[str, Any]:
    candidate = _load_candidate(db_path, candidate_id)
    pipeline_path = root / "pipeline" / "pipeline.yaml"
    contract = yaml.safe_load(pipeline_path.read_text(encoding="utf-8"))
    stages = build_candidate_execution_plan(candidate, contract)
    return {
        "candidate_id": candidate_id,
        "panel_id": candidate["panel_id"],
        "source_revision": candidate["source_revision"],
        "candidate_revision": candidate["candidate_revision"],
        "status": "IN_PROGRESS",
        "planned_stages": stages,
        "stage_execution_mode": "GITHUB_CODEX_AUTOMATION",
        "release_executed": False,
        "release_requires_human": True,
        "rollback_target": candidate["rollback_target"],
    }


def create_and_plan_candidate(
    *,
    db_path: Path,
    root: Path,
    panel_id: str,
    source_revision: str,
    trigger: dict[str, Any],
    canonical_inputs: dict[str, str],
    changes: list[dict[str, Any]],
) -> dict[str, Any]:
    from pipeline.aut_panel_candidate_revision import create_candidate, apply_changes_atomic

    candidate = create_candidate(
        db_path,
        panel_id=panel_id,
        source_revision=source_revision,
        trigger=trigger,
        canonical_inputs=canonical_inputs,
    )
    applied = apply_changes_atomic(
        db_path,
        candidate_id=candidate["candidate_id"],
        changes=changes,
    )

    contract = yaml.safe_load(
        (root / "pipeline" / "pipeline.yaml").read_text(encoding="utf-8")
    )
    planned = build_candidate_execution_plan({"changes": applied}, contract)
    return {
        **candidate,
        "status": "IN_PROGRESS",
        "changes": applied,
        "planned_stages": planned,
        "stage_execution_mode": "GITHUB_CODEX_AUTOMATION",
        "release_executed": False,
        "release_requires_human": True,
    }
