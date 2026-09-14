#!/usr/bin/env python3
"""Canonical Engineering Compatibility /visualize CI gate v1.1.

This module is the single source of truth for schema and semantic release
validation. Other compatibility CLIs must delegate to this implementation.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
DEFAULT_CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
DEFAULT_DATA = ROOT / "datasheet" / "projects" / "example-project.json"

IMPACT_KEYS = {
    "design", "procurement", "fabrication", "programming", "commissioning",
    "operation", "maintenance", "safety", "cost", "schedule",
}
OPEN_STATUSES = {"OPEN", "IN_REVIEW"}


def _reject_non_standard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def load_json(path: Path) -> dict[str, Any]:
    """Load strict JSON and reject NaN/Infinity constants."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh, parse_constant=_reject_non_standard_constant)


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def schema_errors(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    result: list[str] = []
    for exc in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        location = "/".join(map(str, exc.absolute_path)) or "<root>"
        result.append(f"schema:{location}: {exc.message}")
    return result


def _finite_metric(value: Any, label: str, errors: list[str]) -> float | None:
    try:
        metric = float(value)
    except (TypeError, ValueError):
        fail(f"{label} must be numeric", errors)
        return None
    if not math.isfinite(metric):
        fail(f"{label} must be finite", errors)
        return None
    return metric


def compute_coverage(scope_summary: dict[str, Any]) -> float | None:
    """Coverage = verifiable scope / applicable scope.

    NOT_APPLICABLE is excluded from the denominator. NOT_VERIFIABLE remains in
    the denominator and therefore reduces coverage.
    """
    verified = int(scope_summary.get("VERIFIED", 0))
    partial = int(scope_summary.get("PARTIAL", 0))
    divergent = int(scope_summary.get("DIVERGENT", 0))
    not_verifiable = int(scope_summary.get("NOT_VERIFIABLE", 0))
    denominator = verified + partial + divergent + not_verifiable
    if denominator <= 0:
        return None
    return 100.0 * (verified + partial + divergent) / denominator


def validate_semantics(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    thresholds = config["thresholds"]
    tolerance = float(thresholds.get("metric_tolerance_percent", 0.05))

    # /visualize machine contract.
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

    expected_colors = config["severity"]
    actual_colors = viz.get("severity_colors", {})
    for severity, expected in expected_colors.items():
        if actual_colors.get(severity) != expected:
            fail(
                f"visualization.severity_colors.{severity} must be {expected}",
                errors,
            )

    # Baseline integrity and reconciliation.
    baseline = data.get("baseline", {})
    disciplines = list(baseline.get("disciplines", []))
    documents = list(baseline.get("documents", []))
    document_ids = [doc.get("id") for doc in documents]
    document_id_set = set(document_ids)

    if thresholds.get("require_baseline_documents") and not documents:
        fail("baseline.documents must contain at least one source document", errors)
    if len(document_ids) != len(document_id_set):
        fail("baseline.documents contains duplicate document ids", errors)
    if thresholds.get("block_on_unreconciled_baseline") and baseline.get("reconciled") is not True:
        fail("baseline is not reconciled with the current approved revisions", errors)

    for doc in documents:
        if doc.get("discipline") not in disciplines:
            fail(
                f"baseline document {doc.get('id', 'UNKNOWN')} uses discipline "
                f"{doc.get('discipline')} outside baseline.disciplines",
                errors,
            )
        if thresholds.get("require_provenance_hash") and not doc.get("sha256"):
            fail(f"baseline document {doc.get('id', 'UNKNOWN')} missing sha256", errors)

    required_document_ids = set(baseline.get("required_document_ids", []))
    computed_missing = required_document_ids - document_id_set
    declared_missing = set(data.get("blocking_missing_documents", []))
    if computed_missing != declared_missing:
        fail(
            "blocking_missing_documents must exactly match missing "
            f"baseline.required_document_ids; computed={sorted(computed_missing)} "
            f"declared={sorted(declared_missing)}",
            errors,
        )
    if thresholds.get("block_on_missing_mandatory_document") and declared_missing:
        fail(f"blocking mandatory documents are missing: {sorted(declared_missing)}", errors)

    # Structured coverage: NOT_VERIFIABLE must reduce coverage.
    scope_summary = data.get("scope_summary", {})
    declared_coverage = _finite_metric(data.get("coverage"), "coverage", errors)
    computed_coverage = compute_coverage(scope_summary)
    if computed_coverage is None:
        fail("scope_summary has no applicable scope items; coverage cannot be computed", errors)
    elif declared_coverage is not None and abs(declared_coverage - computed_coverage) > tolerance:
        fail(
            f"coverage {declared_coverage:.4f}% inconsistent with scope_summary "
            f"computed coverage {computed_coverage:.4f}%",
            errors,
        )
    if declared_coverage is not None and declared_coverage < float(thresholds["minimum_coverage_percent"]):
        fail(
            f"coverage {declared_coverage:.2f}% below minimum "
            f"{thresholds['minimum_coverage_percent']}%",
            errors,
        )

    # Compatibility metrics and complete mappings.
    compatibility = data.get("compatibility", {})
    global_compat = _finite_metric(compatibility.get("global"), "compatibility.global", errors)
    interface_compat = _finite_metric(compatibility.get("interface"), "compatibility.interface", errors)
    if global_compat is not None and global_compat < float(thresholds["minimum_global_compatibility_percent"]):
        fail(
            f"global compatibility {global_compat:.2f}% below minimum "
            f"{thresholds['minimum_global_compatibility_percent']}%",
            errors,
        )
    if interface_compat is not None and interface_compat < float(thresholds["minimum_interface_compatibility_percent"]):
        fail(
            f"interface compatibility {interface_compat:.2f}% below minimum "
            f"{thresholds['minimum_interface_compatibility_percent']}%",
            errors,
        )

    discipline_scores = compatibility.get("by_discipline", {})
    for name, value in discipline_scores.items():
        _finite_metric(value, f"compatibility.by_discipline.{name}", errors)
    if thresholds.get("require_discipline_scores"):
        score_disciplines = set(discipline_scores)
        if score_disciplines != set(disciplines):
            fail(
                "compatibility.by_discipline keys must exactly match baseline.disciplines; "
                f"expected={sorted(disciplines)} actual={sorted(score_disciplines)}",
                errors,
            )

    document_scores = compatibility.get("by_document", {})
    for name, value in document_scores.items():
        _finite_metric(value, f"compatibility.by_document.{name}", errors)
    if thresholds.get("require_document_scores"):
        score_documents = set(document_scores)
        if score_documents != document_id_set:
            fail(
                "compatibility.by_document keys must exactly match baseline document ids; "
                f"expected={sorted(document_id_set)} actual={sorted(score_documents)}",
                errors,
            )

    method = compatibility.get("method", {})
    if config["compatibility"].get("require_method_disclosure"):
        if not method.get("denominator_definition"):
            fail("compatibility.method.denominator_definition is required", errors)
        if not method.get("formula"):
            fail("compatibility.method.formula is required", errors)
    if method.get("exclude_not_applicable") is not True:
        fail("compatibility.method.exclude_not_applicable must be true", errors)
    if method.get("exclude_not_verifiable") is not True:
        fail("compatibility.method.exclude_not_verifiable must be true", errors)
    required_weights = config["compatibility"].get("required_status_weights", {})
    if method.get("status_weights") != required_weights:
        fail(
            f"compatibility.method.status_weights must equal {required_weights}",
            errors,
        )

    # Findings, provenance, waiver authorization and architecture viability.
    classification_counts = {name: 0 for name in config["classifications"]}
    open_critical: list[str] = []
    document_by_id = {doc.get("id"): doc for doc in documents}

    for finding in data.get("findings", []):
        fid = finding.get("id", "UNKNOWN")
        classification = finding.get("classification")
        status = finding.get("status")
        severity = finding.get("severity")
        if classification in classification_counts:
            classification_counts[classification] += 1

        if severity == "CRITICAL" and status in OPEN_STATUSES:
            open_critical.append(fid)

        if not finding.get("comparison"):
            fail(f"{fid}: comparison is required", errors)
        if not finding.get("root_cause"):
            fail(f"{fid}: root_cause is required", errors)
        if not finding.get("solution"):
            fail(f"{fid}: solution is required", errors)
        if not finding.get("closure_criterion"):
            fail(f"{fid}: closure_criterion is required", errors)

        impacts = finding.get("impacts", {})
        for key in IMPACT_KEYS:
            value = impacts.get(key)
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: lifecycle impact {key} must be explicit or NONE", errors)

        primary_document = finding.get("primary_document")
        if primary_document not in document_id_set and primary_document not in declared_missing:
            fail(f"{fid}: primary_document {primary_document} is not in the baseline inventory", errors)
        for secondary in finding.get("secondary_documents", []):
            if secondary not in document_id_set and secondary not in declared_missing:
                fail(f"{fid}: secondary document {secondary} is not in the baseline inventory", errors)

        evidence = finding.get("evidence", [])
        if not evidence:
            fail(f"{fid}: no evidence provided", errors)
        for index, item in enumerate(evidence, start=1):
            doc_id = item.get("document_id")
            doc = document_by_id.get(doc_id)
            for key in ("document_id", "revision", "location", "statement", "source_hash"):
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    fail(f"{fid}: evidence[{index}] {key} must be non-empty", errors)
            if doc is None:
                fail(f"{fid}: evidence[{index}] document {doc_id} is not in baseline.documents", errors)
            else:
                if item.get("revision") != doc.get("revision"):
                    fail(
                        f"{fid}: evidence[{index}] revision {item.get('revision')} does not "
                        f"match baseline revision {doc.get('revision')} for {doc_id}",
                        errors,
                    )
                if thresholds.get("require_provenance_hash") and item.get("source_hash") != doc.get("sha256"):
                    fail(
                        f"{fid}: evidence[{index}] source_hash does not match baseline sha256 for {doc_id}",
                        errors,
                    )

        if status == "WAIVED" and thresholds.get("require_waiver_metadata"):
            waiver = finding.get("waiver", {})
            for key in ("reason", "approver", "approved_at", "approval_evidence"):
                value = waiver.get(key)
                if not isinstance(value, str) or not value.strip():
                    fail(f"{fid}: waived finding requires waiver.{key}", errors)
            approved_at = waiver.get("approved_at")
            if approved_at:
                try:
                    datetime.fromisoformat(approved_at.replace("Z", "+00:00"))
                except ValueError:
                    fail(f"{fid}: waiver.approved_at must be ISO-8601 date-time", errors)

        if finding.get("architecture_impact") and thresholds.get("require_architecture_viability"):
            if not finding.get("alternatives"):
                fail(f"{fid}: architecture finding requires at least one alternative", errors)
            if not finding.get("viability"):
                fail(f"{fid}: architecture finding requires viability analysis", errors)

    if thresholds.get("block_on_open_critical") and open_critical:
        fail(f"open CRITICAL findings: {', '.join(open_critical)}", errors)

    # Findings cannot exceed the structured classification inventory. This is
    # especially important for NOT_VERIFIABLE because it must reduce coverage.
    for classification, count in classification_counts.items():
        declared_count = int(scope_summary.get(classification, 0))
        if count > declared_count:
            fail(
                f"findings contain {count} {classification} items but scope_summary "
                f"declares only {declared_count}",
                errors,
            )

    # Gate field must match the complete semantic result.
    expected_gate = "BLOCK" if errors else "PASS"
    if data.get("release_gate") != expected_gate:
        fail(
            f"release_gate={data.get('release_gate')} inconsistent with computed gate {expected_gate}",
            errors,
        )

    return errors


def validate_data(
    data: dict[str, Any],
    schema: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    errors = schema_errors(data, schema)
    if errors:
        return errors
    return validate_semantics(data, config)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an engineering compatibility datasheet against the v1.1 Golden Rule gate."
    )
    parser.add_argument(
        "datasheet",
        nargs="?",
        default=str(DEFAULT_DATA),
        help="Datasheet path. Defaults to the permanent known-good regression fixture.",
    )
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    data_path = Path(args.datasheet)
    try:
        schema = load_json(Path(args.schema))
        config = load_json(Path(args.config))
        data = load_json(data_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("=== Engineering Compatibility Golden Rule Gate ===")
        print(f"datasheet: {data_path}")
        print("RESULT: BLOCK")
        print(f"- load error: {exc}")
        return 1

    errors = validate_data(data, schema, config)

    print("=== Engineering Compatibility Golden Rule Gate v1.1 ===")
    print(f"datasheet: {data_path}")
    print(f"project: {data.get('project', 'UNKNOWN')}")
    print(f"coverage: {data.get('coverage', 'N/A')}%")
    print(f"global compatibility: {data.get('compatibility', {}).get('global', 'N/A')}%")
    print(f"interface compatibility: {data.get('compatibility', {}).get('interface', 'N/A')}%")
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
