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

from pipeline.engineering_compatibility_gate import (
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
        if args.summary:
            args.summary.parent.mkdir(parents=True, exist_ok=True)
            args.summary.write_text(
                json.dumps(summary, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        print(json.dumps(summary, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1

    errors = validate_data(data, schema, config)
    summary = summarize(data, errors)

    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    stream = sys.stderr if errors else sys.stdout
    print(json.dumps(summary, indent=2, ensure_ascii=False), file=stream)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
