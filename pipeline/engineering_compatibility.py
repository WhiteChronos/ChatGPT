#!/usr/bin/env python3
"""Validate engineering compatibility datasheets and enforce the /visualize Golden Rule."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
IMPACT_KEYS = {"design","procurement","fabrication","programming","commissioning","operation","maintenance","safety","cost","schedule"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def schema_errors(data: dict) -> list[str]:
    validator = Draft202012Validator(load_json(SCHEMA))
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = ".".join(str(x) for x in err.absolute_path) or "$"
        errors.append(f"SCHEMA {loc}: {err.message}")
    return errors


def golden_errors(data: dict) -> list[str]:
    errors: list[str] = []
    findings = data.get("findings", [])
    if not findings:
        errors.append("GOLDEN: compatibility report must contain findings")

    for f in findings:
        fid = f.get("id", "<missing-id>")
        classification = f.get("classification")
        severity = f.get("severity")

        if classification == "DIVERGENT":
            for key in ("root_cause", "owner", "secondary_documents"):
                if not f.get(key):
                    errors.append(f"GOLDEN {fid}: divergent finding requires {key}")

        impacts = f.get("impacts", {})
        missing = sorted(IMPACT_KEYS - set(impacts))
        if missing:
            errors.append(f"GOLDEN {fid}: impacts missing {', '.join(missing)}")

        for idx, ev in enumerate(f.get("evidence", []), start=1):
            for key in ("document_id", "revision", "location", "statement"):
                if not ev.get(key):
                    errors.append(f"GOLDEN {fid}: evidence[{idx}] missing {key}")

        if severity in {"CRITICAL", "HIGH"} and not f.get("confidence"):
            errors.append(f"GOLDEN {fid}: critical/high finding requires confidence")

        if severity in {"CRITICAL", "HIGH"} and not f.get("solution"):
            errors.append(f"GOLDEN {fid}: critical/high finding requires solution")

        if not f.get("closure_criterion"):
            errors.append(f"GOLDEN {fid}: closure_criterion is mandatory")

    coverage = float(data.get("coverage", 0))
    global_score = float(data.get("compatibility", {}).get("global", 0))
    blockers = data.get("blocking_missing_documents", [])
    critical_open = any(f.get("severity") == "CRITICAL" and f.get("classification") == "DIVERGENT" for f in findings)

    computed_gate = "BLOCK" if (critical_open or blockers or global_score < 70 or coverage < 85) else "PASS"
    declared_gate = data.get("release_gate")
    if declared_gate and declared_gate != computed_gate:
        errors.append(f"GOLDEN: release_gate={declared_gate} but computed gate is {computed_gate}")

    return errors


def summarize(data: dict) -> dict:
    findings = data.get("findings", [])
    by_severity = {k: 0 for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}
    for f in findings:
        sev = f.get("severity")
        if sev in by_severity:
            by_severity[sev] += 1
    critical_open = any(f.get("severity") == "CRITICAL" and f.get("classification") == "DIVERGENT" for f in findings)
    gate = "BLOCK" if (critical_open or data.get("blocking_missing_documents") or float(data.get("compatibility", {}).get("global", 0)) < 70 or float(data.get("coverage", 0)) < 85) else "PASS"
    return {
        "project": data.get("project"),
        "coverage": data.get("coverage"),
        "compatibility": data.get("compatibility"),
        "severity_count": by_severity,
        "release_gate": gate,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("datasheet", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    data = load_json(args.datasheet)
    errors = schema_errors(data) + golden_errors(data)
    summary = summarize(data)

    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 1

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
