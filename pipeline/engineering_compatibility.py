#!/usr/bin/env python3
"""Compatibility report helper backed by the canonical v1.1 Golden Rule gate.

This module intentionally contains no independent release thresholds or blocker
logic. All validation delegates to engineering_compatibility_gate.py so direct
CLI use and CI cannot disagree.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:  # Package import used by pytest and other Python callers.
    from .engineering_compatibility_gate import (
        DEFAULT_CONFIG,
        DEFAULT_SCHEMA,
        _load_policy_config,
        load_json,
        validate_data,
    )
except ImportError:  # Direct CLI execution: python pipeline/engineering_compatibility.py
    from engineering_compatibility_gate import (  # type: ignore
        DEFAULT_CONFIG,
        DEFAULT_SCHEMA,
        _load_policy_config,
        load_json,
        validate_data,
    )


def summarize(data: Any, errors: list[str]) -> dict:
    effective_errors = list(errors)
    if not isinstance(data, dict):
        if not effective_errors:
            effective_errors.append("datasheet top-level value must be an object")
        return {
            "project": None,
            "coverage": None,
            "compatibility": None,
            "severity_count": {key: 0 for key in ("CRITICAL", "HIGH", "MEDIUM", "LOW")},
            "validation_error_count": len(effective_errors),
            "validation_errors": effective_errors,
            "release_gate": "BLOCK",
        }

    findings = data.get("findings", [])
    by_severity = {key: 0 for key in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    if isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            severity = finding.get("severity")
            if severity in by_severity:
                by_severity[severity] += 1

    protocol = data.get("protocol_zero", {})
    questions = protocol.get("questions", []) if isinstance(protocol, dict) else []
    answered = sum(
        1 for item in questions
        if isinstance(item, dict) and item.get("status") == "ANSWERED"
    ) if isinstance(questions, list) else 0
    unresolved = sum(
        1 for item in questions
        if isinstance(item, dict) and item.get("status") == "UNANSWERED"
    ) if isinstance(questions, list) else 0

    reference = data.get("reference_library", {})
    standards = reference.get("standards", []) if isinstance(reference, dict) else []
    applicability_count: dict[str, int] = {}
    if isinstance(standards, list):
        for item in standards:
            if not isinstance(item, dict):
                continue
            key = str(item.get("applicability", "UNKNOWN"))
            applicability_count[key] = applicability_count.get(key, 0) + 1

    findings_with_documents = sum(
        1 for item in findings
        if isinstance(item, dict) and isinstance(item.get("documents_involved"), dict)
    ) if isinstance(findings, list) else 0

    return {
        "project": data.get("project"),
        "report_model": (data.get("report_model") or {}).get("model") if isinstance(data.get("report_model"), dict) else None,
        "coverage": data.get("coverage"),
        "compatibility": data.get("compatibility"),
        "severity_count": by_severity,
        "protocol_zero": {
            "answered": answered,
            "unresolved": unresolved,
        },
        "reference_applicability_count": applicability_count,
        "findings_with_documents_involved": findings_with_documents,
        "finding_count": len(findings) if isinstance(findings, list) else 0,
        "validation_error_count": len(effective_errors),
        "validation_errors": effective_errors,
        "release_gate": "BLOCK" if effective_errors else "PASS",
    }


def _write_summary(path: Path | None, summary: dict) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and summarize an engineering compatibility datasheet."
    )
    parser.add_argument("datasheet", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()

    try:
        data = load_json(args.datasheet)
        schema = load_json(args.schema)
        config = _load_policy_config(args.config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        summary = {
            "project": None,
            "validation_error_count": 1,
            "validation_errors": [f"load error: {exc}"],
            "release_gate": "BLOCK",
        }
        _write_summary(args.summary, summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    try:
        errors = validate_data(data, schema, config)
        summary = summarize(data, errors)
    except Exception as exc:  # Fail closed and overwrite any stale persisted PASS summary.
        errors = [f"validation error: {type(exc).__name__}: {exc}"]
        summary = summarize(None, errors)

    _write_summary(args.summary, summary)

    stream = sys.stderr if summary["release_gate"] == "BLOCK" else sys.stdout
    print(json.dumps(summary, indent=2, ensure_ascii=False), file=stream)
    return 1 if summary["release_gate"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())