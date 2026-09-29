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
        raw = self.memory.search(query, user_id=panel_id, limit=limit)
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
