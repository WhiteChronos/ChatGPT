#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def evaluate_memory_quality(
    report: dict[str, Any],
    *,
    min_active_pass_rate: float = 0.90,
) -> dict[str, Any]:
    if not 0.0 <= min_active_pass_rate <= 1.0:
        raise ValueError("min_active_pass_rate must be between 0 and 1")

    results = report.get("results") or []
    isolation_failures: list[dict[str, Any]] = []
    for result in results:
        if str(result.get("category") or "") != "cross_panel":
            continue
        unexpected = list(result.get("unexpected_event_ids") or [])
        if result.get("passed") is False or unexpected:
            isolation_failures.append(result)

    base = {
        "engineering_release_authority": False,
        "active_pass_rate": float(report.get("active_pass_rate") or 0.0),
        "minimum_active_pass_rate": float(min_active_pass_rate),
    }

    if isolation_failures:
        return {
            **base,
            "status": "REPROVADO_MEMORY_ISOLATION",
            "reasons": ["CROSS_PANEL_MEMORY_LEAKAGE"],
            "isolation_failures": isolation_failures,
        }

    if base["active_pass_rate"] < min_active_pass_rate:
        return {
            **base,
            "status": "HOLD_MEMORY_QUALITY",
            "reasons": ["ACTIVE_PASS_RATE_BELOW_THRESHOLD"],
            "isolation_failures": [],
        }

    return {
        **base,
        "status": "PASS",
        "reasons": [],
        "isolation_failures": [],
    }
