#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def evaluate_activation(registry: dict[str, Any]) -> dict[str, Any]:
    approved = (
        registry.get("activation_allowed") is True
        and registry.get("license_status") == "APPROVED"
        and registry.get("security_review_status") == "APPROVED"
        and isinstance(registry.get("pinned_commit"), str)
        and len(registry["pinned_commit"]) == 40
    )
    return {
        "status": "PASS" if approved else "HOLD_EXTERNAL_BENCHMARK",
        "execute": approved,
        "repository": registry.get("repository"),
        "pinned_commit": registry.get("pinned_commit"),
    }


def main() -> int:
    path = Path("plugins/agent_memory_benchmark_registry.json")
    result = evaluate_activation(json.loads(path.read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
    return 0 if result["execute"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
