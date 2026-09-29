#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "handoff_id",
    "task_id",
    "from",
    "to",
    "panel",
    "revision",
    "status",
    "outputs",
    "validated_facts",
    "source_refs",
    "holds",
    "next_action",
)

VALID_STATUS = {"PASS", "HOLD", "REPROVADO", "PENDING", "USER_DECISION_REQUIRED"}


class HandoffError(RuntimeError):
    pass


def build_handoff(
    *,
    task_id: str,
    from_agent: str,
    to_agent: str,
    panel: str,
    revision: str,
    status: str,
    outputs: list[dict[str, Any]] | None = None,
    validated_facts: list[dict[str, Any]] | None = None,
    source_refs: list[dict[str, Any]] | None = None,
    holds: list[dict[str, Any]] | None = None,
    next_action: str,
) -> dict[str, Any]:
    if status not in VALID_STATUS:
        raise HandoffError(f"invalid status: {status}")
    if panel not in {"PN-AUT-01", "PN-AUT-02"}:
        raise HandoffError(f"invalid panel: {panel}")

    payload = {
        "schema_version": "1.0",
        "handoff_id": f"HANDOFF-{uuid.uuid4().hex[:12].upper()}",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "task_id": task_id,
        "from": from_agent,
        "to": to_agent,
        "panel": panel,
        "revision": revision,
        "status": status,
        "outputs": outputs or [],
        "validated_facts": validated_facts or [],
        "source_refs": source_refs or [],
        "holds": holds or [],
        "next_action": next_action,
        "chain_of_thought_included": False,
    }
    validate_handoff(payload)
    return payload


def validate_handoff(payload: dict[str, Any]) -> None:
    missing = [x for x in REQUIRED_FIELDS if x not in payload]
    if missing:
        raise HandoffError(f"missing fields: {missing}")
    if payload.get("status") not in VALID_STATUS:
        raise HandoffError("invalid status")
    if payload.get("panel") not in {"PN-AUT-01", "PN-AUT-02"}:
        raise HandoffError("invalid panel")
    if payload.get("chain_of_thought_included") is not False:
        raise HandoffError("handoff must not contain chain of thought")
    for field in ("outputs", "validated_facts", "source_refs", "holds"):
        if not isinstance(payload.get(field), list):
            raise HandoffError(f"{field} must be a list")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input_json")
    p.add_argument("--output", required=True)
    args = p.parse_args()

    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    payload = build_handoff(
        task_id=data["task_id"],
        from_agent=data["from"],
        to_agent=data["to"],
        panel=data["panel"],
        revision=data["revision"],
        status=data["status"],
        outputs=data.get("outputs"),
        validated_facts=data.get("validated_facts"),
        source_refs=data.get("source_refs"),
        holds=data.get("holds"),
        next_action=data["next_action"],
    )
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
