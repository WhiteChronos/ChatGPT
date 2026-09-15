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

try:  # Package import used by pytest and other Python callers.
    from .engineering_compatibility_gate import (
        DEFAULT_CONFIG,
        DEFAULT_SCHEMA,
        load_json,
        validate_data,
    )
except ImportError:  # Direct CLI execution: python pipeline/engineering_compatibility.py
    from engineering_compatibility_gate import (  # type: ignore
        DEFAULT_CONFIG,
        DEFAULT_SCHEMA,
        load_json,
        validate_data,
    )


def summarize(data: dict, errors: list[str]) -> dict:
    findings = data.get("findings", [])
    by_severity = {key: 0 for key in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    for finding in findings:
        severity = finding.get("severity")
        if severity in by_severity:
            by_severity[severity] += 1

    return {
        "project": data.get("project"),
        "coverage": data.get("coverage"),
        "compatibility": data.get("compatibility"),
        "severity_count": by_severity,
        "validation_error_count": len(errors),
        "validation_errors": errors,
        "release_gate": "BLOCK" if errors else "PASS",
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
        config = load_json(args.config)
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
    except Exception as exc:  # Fail closed and overwrite any stale persisted PASS summary.
        errors = [f"validation error: {type(exc).__name__}: {exc}"]

    summary = summarize(data, errors)
    _write_summary(args.summary, summary)

    stream = sys.stderr if errors else sys.stdout
    print(json.dumps(summary, indent=2, ensure_ascii=False), file=stream)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
