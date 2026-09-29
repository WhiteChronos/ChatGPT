#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "database/aut_panel_schema.sql"

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path: Path, schema_path: Path = DEFAULT_SCHEMA) -> None:
    with connect(db_path) as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))

def db_fingerprint(db_path: Path) -> str:
    h = hashlib.sha256()
    with db_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def record_memory_event(db_path: Path, *, agent_id: str, event_type: str, summary: str,
                        panel_id: str | None = None, panel_revision: str | None = None,
                        evidence: dict[str, Any] | None = None, mirror_backend: Any | None = None) -> str:
    event_id = f"MEM-{uuid.uuid4().hex[:16].upper()}"
    with connect(db_path) as conn:
        conn.execute(
            """INSERT INTO memory_events
            (event_id, agent_id, panel_id, panel_revision, event_type, event_at, summary, evidence_json, immutable_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (event_id, agent_id, panel_id, panel_revision, event_type, now_iso(), summary,
             json.dumps(evidence or {}, ensure_ascii=False, sort_keys=True)),
        )
    if mirror_backend is not None:
        from pipeline.aut_panel_mem0 import mirror_memory_event
        mirror_memory_event(event_id, db_path=db_path, backend=mirror_backend)
    return event_id

def record_agent_run(db_path: Path, *, run_id: str, agent_id: str, stage: str, status: str,
                     panel_id: str | None = None, panel_revision: str | None = None,
                     metadata: dict[str, Any] | None = None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """INSERT INTO agent_runs
            (run_id, agent_id, panel_id, panel_revision, stage, started_at, finished_at, status, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run_id, agent_id, panel_id, panel_revision, stage, now_iso(), now_iso(), status,
             json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True)),
        )

def table_counts(db_path: Path) -> dict[str, int]:
    tables = ["panels", "components", "sources", "panel_components", "io_points", "agent_runs",
              "memory_events", "qa_runs", "qa_findings", "training_examples", "model_registry",
              "evolution_proposals", "artifacts"]
    with connect(db_path) as conn:
        return {name: int(conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]) for name in tables}

def main() -> int:
    p = argparse.ArgumentParser(description="AUT Panel database control")
    p.add_argument("--db", default="build/aut-panel/aut_panel.sqlite3")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    mem = sub.add_parser("memory-event")
    mem.add_argument("--agent-id", required=True)
    mem.add_argument("--event-type", required=True)
    mem.add_argument("--summary", required=True)
    mem.add_argument("--panel-id")
    mem.add_argument("--panel-revision")
    args = p.parse_args()
    db = Path(args.db)
    if args.cmd == "init":
        init_db(db)
        print(json.dumps({"status": "PASS", "db": str(db), "sha256": db_fingerprint(db)}, indent=2))
        return 0
    if not db.exists():
        raise SystemExit("database missing; run init first")
    if args.cmd == "status":
        print(json.dumps({"status": "PASS", "counts": table_counts(db), "sha256": db_fingerprint(db)}, indent=2))
        return 0
    event_id = record_memory_event(db, agent_id=args.agent_id, event_type=args.event_type,
                                   summary=args.summary, panel_id=args.panel_id,
                                   panel_revision=args.panel_revision)
    print(json.dumps({"status": "PASS", "event_id": event_id}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
