#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


class NullMemoryBackend:
    name = "null"

    def add_event(self, event: dict[str, Any]) -> str:
        return str(event.get("event_id") or "")

    def search(
        self,
        *,
        query: str,
        panel_id: str,
        panel_revision: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        return []


class Mem0MemoryBackend:
    name = "mem0"

    def __init__(self, *, memory: Any):
        self.memory = memory

    def add_event(self, event: dict[str, Any]) -> str:
        event_id = str(event.get("event_id") or "")
        if not event_id:
            raise ValueError("event_id is required")
        metadata = {
            "event_id": event_id,
            "panel_id": event.get("panel_id"),
            "panel_revision": event.get("panel_revision"),
            "event_type": event.get("event_type"),
            "evidence": event.get("evidence") or {},
        }
        summary = str(event.get("summary") or "")
        self.memory.add(
            messages=[{"role": "user", "content": summary}],
            user_id=str(event.get("panel_id") or "GLOBAL"),
            metadata=metadata,
        )
        return event_id

    def search(
        self,
        *,
        query: str,
        panel_id: str,
        panel_revision: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        raw = self.memory.search(query=query, user_id=panel_id, limit=limit)
        entries = raw.get("results", raw) if isinstance(raw, dict) else raw
        out: list[dict[str, Any]] = []
        for item in entries or []:
            meta = item.get("metadata") or {}
            if meta.get("panel_id") not in (None, panel_id):
                continue
            if panel_revision and meta.get("panel_revision") not in (None, panel_revision):
                continue
            out.append(
                {
                    "id": item.get("id"),
                    "memory": item.get("memory"),
                    "score": item.get("score"),
                    "metadata": meta,
                }
            )
        return out[:limit]


def build_memory_backend(
    config: dict[str, Any],
    *,
    memory_factory: Any | None = None,
):
    if not bool(config.get("enabled", False)):
        return NullMemoryBackend()

    if memory_factory is None:
        try:
            from mem0 import Memory
        except Exception as exc:
            raise RuntimeError("Mem0 backend enabled but mem0ai is unavailable") from exc
        mem0_config = config.get("mem0_config") or {}
        memory = Memory.from_config(mem0_config) if mem0_config else Memory()
    else:
        memory = memory_factory(config)

    return Mem0MemoryBackend(memory=memory)


def mirror_memory_event(
    event_id: str,
    *,
    db_path,
    backend,
) -> dict[str, Any]:
    import json
    import sqlite3
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        row = conn.execute(
            "SELECT * FROM memory_events WHERE event_id=?",
            (event_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"memory event not found: {event_id}")

        backend_name = str(getattr(backend, "name", "memory"))
        existing = conn.execute(
            "SELECT status,backend_memory_id FROM memory_mirrors WHERE event_id=? AND backend=?",
            (event_id, backend_name),
        ).fetchone()
        if existing is not None and existing["status"] == "PASS":
            return {
                "status": "ALREADY_MIRRORED",
                "event_id": event_id,
                "backend": backend_name,
                "backend_memory_id": existing["backend_memory_id"],
            }

        event = {
            "event_id": row["event_id"],
            "agent_id": row["agent_id"],
            "panel_id": row["panel_id"],
            "panel_revision": row["panel_revision"],
            "event_type": row["event_type"],
            "event_at": row["event_at"],
            "summary": row["summary"],
            "evidence": json.loads(row["evidence_json"] or "{}"),
        }

        try:
            backend_memory_id = backend.add_event(event)
            status = "PASS"
            error = None
        except Exception as exc:
            backend_memory_id = None
            status = "FAILED"
            error = str(exc)

        conn.execute(
            """INSERT INTO memory_mirrors
               (event_id,backend,status,backend_memory_id,last_error,mirrored_at)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(event_id,backend) DO UPDATE SET
                 status=excluded.status,
                 backend_memory_id=excluded.backend_memory_id,
                 last_error=excluded.last_error,
                 mirrored_at=excluded.mirrored_at""",
            (event_id, backend_name, status, backend_memory_id, error, now),
        )
        conn.commit()
        return {
            "status": status,
            "event_id": event_id,
            "backend": backend_name,
            "backend_memory_id": backend_memory_id,
            "error": error,
        }
    finally:
        conn.close()
