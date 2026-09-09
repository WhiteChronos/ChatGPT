from __future__ import annotations

from typing import Any


def grade(case: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expect = case["expect"]
    comments = payload.get("comments", [])

    if payload.get("source_formal_comment_count") != expect.get("source_formal_comment_count"):
        errors.append("formal_count_mismatch")

    ids = [c.get("comment_id") for c in comments]
    if ids != expect.get("comment_ids"):
        errors.append(f"comment_ids_mismatch:{ids!r}")

    if expect.get("forbidden_checked") and any(c.get("status_control") == "CHECKED" for c in comments):
        errors.append("agent_marked_checked")

    if len(payload.get("new_divergences", [])) < expect.get("new_divergence_min", 0):
        errors.append("new_divergence_missing")

    required_min = expect.get("required_documents_min")
    if required_min is not None:
        largest = max((len(c.get("required_documents") or []) for c in comments), default=0)
        if largest < required_min:
            errors.append("multidoc_traceability_missing")

    return errors
