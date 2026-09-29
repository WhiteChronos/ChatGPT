#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def retrieve_context(
    *,
    query: str,
    panel_id: str,
    panel_revision: str,
    backend,
    canonical_state: dict[str, Any],
    limit: int = 20,
) -> dict[str, Any]:
    if canonical_state.get("panel_id") != panel_id:
        raise ValueError("canonical_state panel_id mismatch")
    if canonical_state.get("panel_revision") != panel_revision:
        raise ValueError("canonical_state panel_revision mismatch")

    accepted_ids = set(canonical_state.get("accepted_event_ids") or [])
    historical_ids = set(canonical_state.get("historical_event_ids") or [])
    rejected_ids = set(canonical_state.get("rejected_event_ids") or [])

    rows = backend.search(
        query=query,
        panel_id=panel_id,
        panel_revision=None,
        limit=limit,
    )

    accepted: list[dict[str, Any]] = []
    historical: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for row in rows:
        meta = row.get("metadata") or {}
        event_id = str(meta.get("event_id") or "")
        if meta.get("panel_id") != panel_id:
            rejected.append({**row, "reason": "WRONG_PANEL"})
            continue
        if not event_id:
            rejected.append({**row, "reason": "MISSING_EVENT_ID"})
            continue
        if not isinstance(meta.get("evidence"), dict) or not meta["evidence"]:
            rejected.append({**row, "reason": "MISSING_PROVENANCE"})
            continue
        if event_id in rejected_ids:
            rejected.append({**row, "reason": "CANONICALLY_REJECTED"})
            continue
        if event_id in historical_ids or meta.get("panel_revision") != panel_revision:
            historical.append({**row, "reason": "HISTORICAL_CONTEXT_ONLY"})
            continue
        if event_id in accepted_ids:
            accepted.append(row)
            continue
        rejected.append({**row, "reason": "UNKNOWN_CANONICAL_EVENT"})

    return {
        "accepted": accepted,
        "historical": historical,
        "rejected": rejected,
        "authority": "CANONICAL_REPOSITORY_AND_SQLITE",
        "memory_backend_authoritative": False,
    }
