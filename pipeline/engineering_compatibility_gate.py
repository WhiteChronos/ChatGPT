#!/usr/bin/env python3
"""Engineering compatibility CI gate.

Validates compatibility datasheets against the repository schema and enforces
VISUALIZE_GOLDEN_RULE_v1_0 release rules.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
DEFAULT_CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
DEFAULT_DATA = ROOT / "datasheet" / "ENGINEERING_COMPATIBILITY_DATA_SHEET.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_semantics(data: dict, config: dict) -> list[str]:
    errors: list[str] = []
    thresholds = config["thresholds"]

    viz = data.get("visualization", {})
    if viz.get("model") != "VISUALIZE_GOLDEN_RULE_v1_0":
        fail("visualization.model must be VISUALIZE_GOLDEN_RULE_v1_0", errors)
    if viz.get("complete_not_summary") is not True:
        fail("/visualize output must be complete_not_summary=true", errors)

    required_sections = set(config["visualization"]["mandatory_sections"])
    actual_sections = set(viz.get("mandatory_sections", []))
    missing_sections = sorted(required_sections - actual_sections)
    if missing_sections:
        fail(f"missing visualization sections: {', '.join(missing_sections)}", errors)

    coverage = float(data.get("coverage", 0))
    if coverage < float(thresholds["minimum_coverage_percent"]):
        fail(
            f"coverage {coverage:.2f}% below minimum "
            f"{thresholds['minimum_coverage_percent']}%",
            errors,
        )

    global_compat = float(data.get("compatibility", {}).get("global", 0))
    if global_compat < float(thresholds["minimum_global_compatibility_percent"]):
        fail(
            f"global compatibility {global_compat:.2f}% below minimum "
            f"{thresholds['minimum_global_compatibility_percent']}%",
            errors,
        )

    missing_docs = data.get("blocking_missing_documents", [])
    if thresholds.get("block_on_missing_mandatory_document") and missing_docs:
        fail(f"blocking mandatory documents are missing: {missing_docs}", errors)

    open_critical = [
        f.get("id", "UNKNOWN")
        for f in data.get("findings", [])
        if f.get("severity") == "CRITICAL" and f.get("status") not in {"CLOSED", "WAIVED"}
    ]
    if thresholds.get("block_on_open_critical") and open_critical:
        fail(f"open CRITICAL findings: {', '.join(open_critical)}", errors)

    # Golden-rule completeness checks for every actionable finding.
    impact_keys = {
        "design", "procurement", "fabrication", "programming", "commissioning",
        "operation", "maintenance", "safety", "cost", "schedule",
    }
    for finding in data.get("findings", []):
        fid = finding.get("id", "UNKNOWN")
        if not finding.get("evidence"):
            fail(f"{fid}: no evidence provided", errors)
        if not finding.get("root_cause"):
            fail(f"{fid}: root_cause is required", errors)
        impacts = finding.get("impacts", {})
        missing_impacts = sorted(impact_keys - set(impacts))
        if missing_impacts:
            fail(f"{fid}: missing lifecycle impact fields {missing_impacts}", errors)
        if finding.get("classification") == "DIVERGENT" and not finding.get("solution"):
            fail(f"{fid}: divergent finding requires solution", errors)
        if finding.get("status") != "CLOSED" and not finding.get("closure_criterion"):
            fail(f"{fid}: open finding requires closure criterion", errors)

    # Gate field must match computed result.
    expected_gate = "BLOCK" if errors else "PASS"
    if data.get("release_gate") != expected_gate:
        fail(
            f"release_gate={data.get('release_gate')} inconsistent with computed gate {expected_gate}",
            errors,
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("datasheet", nargs="?", default=str(DEFAULT_DATA))
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    data_path = Path(args.datasheet)
    schema = load_json(Path(args.schema))
    config = load_json(Path(args.config))
    data = load_json(data_path)

    schema_errors = sorted(
        Draft202012Validator(schema).iter_errors(data),
        key=lambda exc: list(exc.absolute_path),
    )
    errors = [
        f"schema:{'/'.join(map(str, exc.absolute_path)) or '<root>'}: {exc.message}"
        for exc in schema_errors
    ]
    if not schema_errors:
        errors.extend(validate_semantics(data, config))

    print("=== Engineering Compatibility Golden Rule Gate ===")
    print(f"datasheet: {data_path}")
    print(f"project: {data.get('project', 'UNKNOWN')}")
    print(f"coverage: {data.get('coverage', 'N/A')}%")
    print(f"global compatibility: {data.get('compatibility', {}).get('global', 'N/A')}%")
    print(f"declared release gate: {data.get('release_gate', 'N/A')}")

    if errors:
        print("RESULT: BLOCK")
        for error in errors:
            print(f"- {error}")
        return 1

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
