#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def run_retrieval_benchmark(
    cases: list[dict[str, Any]],
    provider,
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    passed = 0
    for case in cases:
        rows = provider.search(
            query=str(case["query"]),
            panel_id=str(case["panel_id"]),
            panel_revision=str(case["panel_revision"]),
            limit=int(case.get("retrieval_limit") or 20),
        )
        retrieved = [
            str((row.get("metadata") or {}).get("event_id"))
            for row in rows
            if (row.get("metadata") or {}).get("event_id")
        ]
        retrieved_set = set(retrieved)
        required = set(case.get("must_include_event_ids") or [])
        forbidden = set(case.get("must_exclude_event_ids") or [])
        missing = sorted(required - retrieved_set)
        unexpected = sorted(forbidden & retrieved_set)
        ok = not missing and not unexpected
        if ok:
            passed += 1
        results.append(
            {
                "case_id": case.get("case_id"),
                "category": case.get("category"),
                "retrieved_event_ids": retrieved,
                "missing_event_ids": missing,
                "unexpected_event_ids": unexpected,
                "passed": ok,
            }
        )
    total = len(cases)
    return {
        "total_cases": total,
        "passed_cases": passed,
        "active_pass_rate": (passed / total) if total else 1.0,
        "llm_judge_used": False,
        "results": results,
    }
