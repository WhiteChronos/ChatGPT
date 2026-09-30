#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LOCKED_PREFIXES = ("governance/", "templates/", "li/", "datasheet/", "datacenter/", "prompts/", "context/")
LOCKED_EXACT = {"pipeline/pipeline.yaml"}

def is_locked_path(path: str) -> bool:
    norm = path.replace("\\", "/").lstrip("./")
    return norm in LOCKED_EXACT or norm.startswith(LOCKED_PREFIXES)

def build_proposal(data: dict[str, Any]) -> dict[str, Any]:
    affected = [str(x) for x in data.get("affected_files", [])]
    touches_locked = any(is_locked_path(p) for p in affected)
    return {
        "proposal_id": f"EVO-{uuid.uuid4().hex[:12].upper()}",
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "problem": data.get("problem", "unspecified"),
        "evidence": data.get("evidence", []),
        "candidate_change": data.get("candidate_change", {}),
        "affected_files": affected,
        "expected_benefit": data.get("expected_benefit"),
        "risk": data.get("risk", "MEDIUM"),
        "tests": data.get("tests", []),
        "rollback_plan": data.get("rollback_plan", "revert reviewed commit"),
        "confidence": data.get("confidence"),
        "touches_locked_contract": touches_locked,
        "requires_human_approval": True,
        "auto_apply_allowed": False if touches_locked else bool(data.get("allow_unlocked_auto_apply", False)),
        "status": "PENDING_HUMAN_REVIEW",
        "engineering_truth_source": False,
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("input_json")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    proposal = build_proposal(json.loads(Path(args.input_json).read_text(encoding="utf-8")))
    Path(args.output).write_text(json.dumps(proposal, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(proposal, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
