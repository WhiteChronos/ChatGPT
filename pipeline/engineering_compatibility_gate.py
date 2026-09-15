#!/usr/bin/env python3
"""Canonical Engineering Compatibility /visualize CI gate v1.1."""
from __future__ import annotations

import argparse
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
ISSUE_CLASSIFICATIONS = {"PARTIAL", "DIVERGENT", "NOT_VERIFIABLE"}


def _reject_non_standard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def load_json(path: Path) -> dict[str, Any]:
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
    verified = int(scope_summary.get("VERIFIED", 0))
    partial = int(scope_summary.get("PARTIAL", 0))
    divergent = int(scope_summary.get("DIVERGENT", 0))
    not_verifiable = int(scope_summary.get("NOT_VERIFIABLE", 0))
    denominator = verified + partial + divergent + not_verifiable
    if denominator <= 0:
        return None
    return 100.0 * (verified + partial + divergent) / denominator


def _score(records: list[dict[str, Any]], weights: dict[str, float]) -> float | None:
    applicable = [
        record for record in records
        if record.get("classification") not in {"NOT_APPLICABLE", "NOT_VERIFIABLE"}
    ]
    if not applicable:
        return None
    total = sum(float(weights[record["classification"]]) for record in applicable)
    return 100.0 * total / len(applicable)


def _assert_metric(
    label: str,
    declared: Any,
    computed: float | None,
    tolerance: float,
    errors: list[str],
) -> float | None:
    value = _finite_metric(declared, label, errors)
    if computed is None:
        fail(f"{label} cannot be computed from assessment_records", errors)
    elif value is not None and abs(value - computed) > tolerance:
        fail(
            f"{label} {value:.4f}% inconsistent with assessment_records computed {computed:.4f}%",
            errors,
        )
    return value


def _validate_evidence(
    owner: str,
    evidence: list[dict[str, Any]],
    document_by_id: dict[Any, dict[str, Any]],
    thresholds: dict[str, Any],
    errors: list[str],
    *,
    allowed_document_ids: set[Any] | None = None,
) -> set[str]:
    """Validate provenance-bearing evidence and return evidenced disciplines."""
    evidenced_disciplines: set[str] = set()
    if not evidence:
        fail(f"{owner}: no evidence provided", errors)
        return evidenced_disciplines

    for index, item in enumerate(evidence, start=1):
        doc_id = item.get("document_id")
        doc = document_by_id.get(doc_id)
        for key in ("document_id", "revision", "location", "statement", "source_hash"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                fail(f"{owner}: evidence[{index}] {key} must be non-empty", errors)

        if allowed_document_ids is not None and doc_id not in allowed_document_ids:
            fail(
                f"{owner}: evidence[{index}] document {doc_id} is not declared in document_ids",
                errors,
            )

        if doc is None:
            fail(f"{owner}: evidence[{index}] document {doc_id} is not in baseline.documents", errors)
            continue

        discipline = doc.get("discipline")
        if isinstance(discipline, str):
            evidenced_disciplines.add(discipline)

        if item.get("revision") != doc.get("revision"):
            fail(
                f"{owner}: evidence[{index}] revision {item.get('revision')} does not match "
                f"baseline revision {doc.get('revision')} for {doc_id}",
                errors,
            )
        source_hash = item.get("source_hash")
        baseline_hash = doc.get("sha256")
        if (
            thresholds.get("require_provenance_hash")
            and isinstance(source_hash, str)
            and isinstance(baseline_hash, str)
            and source_hash.lower() != baseline_hash.lower()
        ):
            fail(
                f"{owner}: evidence[{index}] source_hash does not match baseline sha256 for {doc_id}",
                errors,
            )
    return evidenced_disciplines


def validate_semantics(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    thresholds = config["thresholds"]
    tolerance = float(thresholds.get("metric_tolerance_percent", 0.05))
    classifications = list(config["classifications"])

    viz = data.get("visualization", {})
    if viz.get("model") != "VISUALIZE_GOLDEN_RULE_v1_0":
        fail("visualization.model must be VISUALIZE_GOLDEN_RULE_v1_0", errors)
    if viz.get("complete_not_summary") is not True:
        fail("/visualize output must be complete_not_summary=true", errors)
    missing_sections = sorted(
        set(config["visualization"]["mandatory_sections"])
        - set(viz.get("mandatory_sections", []))
    )
    if missing_sections:
        fail(f"missing visualization sections: {', '.join(missing_sections)}", errors)
    for severity, expected in config["severity"].items():
        if viz.get("severity_colors", {}).get(severity) != expected:
            fail(f"visualization.severity_colors.{severity} must be {expected}", errors)

    baseline = data.get("baseline", {})
    disciplines = list(baseline.get("disciplines", []))
    discipline_set = set(disciplines)
    documents = list(baseline.get("documents", []))
    document_ids = [doc.get("id") for doc in documents]
    document_id_set = set(document_ids)
    document_by_id = {doc.get("id"): doc for doc in documents}

    if thresholds.get("require_baseline_documents") and not documents:
        fail("baseline.documents must contain at least one source document", errors)
    if len(document_ids) != len(document_id_set):
        fail("baseline.documents contains duplicate document ids", errors)
    if thresholds.get("block_on_unreconciled_baseline") and baseline.get("reconciled") is not True:
        fail("baseline is not reconciled with the current approved revisions", errors)
    for doc in documents:
        if doc.get("discipline") not in discipline_set:
            fail(
                f"baseline document {doc.get('id', 'UNKNOWN')} uses discipline "
                f"{doc.get('discipline')} outside baseline.disciplines",
                errors,
            )
        if thresholds.get("require_provenance_hash") and not doc.get("sha256"):
            fail(f"baseline document {doc.get('id', 'UNKNOWN')} missing sha256", errors)

    required_document_ids = set(baseline.get("required_document_ids", []))
    eligible_statuses = set(
        config.get("baseline_policy", {}).get(
            "eligible_required_document_statuses", ["CURRENT"]
        )
    )
    eligible_required_ids = {
        doc.get("id")
        for doc in documents
        if doc.get("id") in required_document_ids and doc.get("status") in eligible_statuses
    }
    computed_missing = required_document_ids - eligible_required_ids
    declared_missing = set(data.get("blocking_missing_documents", []))
    if computed_missing != declared_missing:
        fail(
            "blocking_missing_documents must exactly match missing or non-current "
            "baseline.required_document_ids; "
            f"computed={sorted(computed_missing)} declared={sorted(declared_missing)}",
            errors,
        )
    if thresholds.get("block_on_missing_mandatory_document") and declared_missing:
        fail(
            f"blocking mandatory documents are missing or non-current: {sorted(declared_missing)}",
            errors,
        )

    records = list(data.get("assessment_records", []))
    record_ids = [record.get("id") for record in records]
    if len(record_ids) != len(set(record_ids)):
        fail("assessment_records contains duplicate ids", errors)

    derived_counts = {name: 0 for name in classifications}
    for record in records:
        rid = record.get("id", "UNKNOWN")
        classification = record.get("classification")
        if classification in derived_counts:
            derived_counts[classification] += 1

        record_disciplines = set(record.get("disciplines", []))
        record_documents = set(record.get("document_ids", []))
        for discipline in record_disciplines:
            if discipline not in discipline_set:
                fail(f"assessment {rid} uses discipline {discipline} outside baseline.disciplines", errors)
        for document_id in record_documents:
            if document_id not in document_id_set:
                fail(f"assessment {rid} uses document {document_id} outside baseline.documents", errors)

        evidenced_disciplines = _validate_evidence(
            f"assessment {rid}",
            list(record.get("evidence", [])),
            document_by_id,
            thresholds,
            errors,
            allowed_document_ids=record_documents,
        )
        if not evidenced_disciplines.issubset(record_disciplines):
            extra = sorted(evidenced_disciplines - record_disciplines)
            fail(
                f"assessment {rid} evidence uses disciplines outside assessment.disciplines: {extra}",
                errors,
            )
        if record.get("interface") is True:
            if len(record_disciplines) < 2:
                fail(
                    f"assessment {rid} marked interface=true must include at least two disciplines",
                    errors,
                )
            if len(evidenced_disciplines & record_disciplines) < 2:
                fail(
                    f"assessment {rid} interface evidence must cover at least two distinct baseline disciplines",
                    errors,
                )

    scope_summary = data.get("scope_summary", {})
    declared_counts = {name: int(scope_summary.get(name, 0)) for name in classifications}
    if declared_counts != derived_counts:
        fail(
            "scope_summary must equal counts derived from assessment_records; "
            f"computed={derived_counts} declared={declared_counts}",
            errors,
        )

    declared_coverage = _finite_metric(data.get("coverage"), "coverage", errors)
    computed_coverage = compute_coverage(derived_counts)
    if computed_coverage is None:
        fail("assessment_records has no applicable scope items; coverage cannot be computed", errors)
    elif declared_coverage is not None and abs(declared_coverage - computed_coverage) > tolerance:
        fail(
            f"coverage {declared_coverage:.4f}% inconsistent with assessment_records "
            f"computed {computed_coverage:.4f}%",
            errors,
        )
    if (
        declared_coverage is not None
        and declared_coverage < float(thresholds["minimum_coverage_percent"])
    ):
        fail(
            f"coverage {declared_coverage:.2f}% below minimum "
            f"{thresholds['minimum_coverage_percent']}%",
            errors,
        )

    compatibility = data.get("compatibility", {})
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
        fail(f"compatibility.method.status_weights must equal {required_weights}", errors)
    weights = {key: float(value) for key, value in required_weights.items()}

    global_compat = _assert_metric(
        "compatibility.global",
        compatibility.get("global"),
        _score(records, weights),
        tolerance,
        errors,
    )
    interface_records = [record for record in records if record.get("interface") is True]
    interface_compat = _assert_metric(
        "compatibility.interface",
        compatibility.get("interface"),
        _score(interface_records, weights),
        tolerance,
        errors,
    )

    discipline_scores = compatibility.get("by_discipline", {})
    if thresholds.get("require_discipline_scores") and set(discipline_scores) != discipline_set:
        fail(
            "compatibility.by_discipline keys must exactly match baseline.disciplines; "
            f"expected={sorted(discipline_set)} actual={sorted(discipline_scores)}",
            errors,
        )
    for discipline in disciplines:
        related = [record for record in records if discipline in record.get("disciplines", [])]
        _assert_metric(
            f"compatibility.by_discipline.{discipline}",
            discipline_scores.get(discipline),
            _score(related, weights),
            tolerance,
            errors,
        )

    document_scores = compatibility.get("by_document", {})
    if thresholds.get("require_document_scores") and set(document_scores) != document_id_set:
        fail(
            "compatibility.by_document keys must exactly match baseline document ids; "
            f"expected={sorted(document_id_set)} actual={sorted(document_scores)}",
            errors,
        )
    for document_id in document_ids:
        related = [record for record in records if document_id in record.get("document_ids", [])]
        _assert_metric(
            f"compatibility.by_document.{document_id}",
            document_scores.get(document_id),
            _score(related, weights),
            tolerance,
            errors,
        )

    if (
        global_compat is not None
        and global_compat < float(thresholds["minimum_global_compatibility_percent"])
    ):
        fail(
            f"global compatibility {global_compat:.2f}% below minimum "
            f"{thresholds['minimum_global_compatibility_percent']}%",
            errors,
        )
    if (
        interface_compat is not None
        and interface_compat < float(thresholds["minimum_interface_compatibility_percent"])
    ):
        fail(
            f"interface compatibility {interface_compat:.2f}% below minimum "
            f"{thresholds['minimum_interface_compatibility_percent']}%",
            errors,
        )

    record_by_id = {record.get("id"): record for record in records}
    open_critical: list[str] = []
    trusted_approvals = config.get("waiver_authorization", {}).get(
        "trusted_approval_records", {}
    )
    linked_assessment_ids: set[Any] = set()

    for finding in data.get("findings", []):
        fid = finding.get("id", "UNKNOWN")
        status = finding.get("status")
        if finding.get("severity") == "CRITICAL" and status in OPEN_STATUSES:
            open_critical.append(fid)

        assessment_id = finding.get("assessment_id")
        assessment = record_by_id.get(assessment_id)
        if assessment is None:
            fail(f"{fid}: assessment_id {assessment_id} is not in assessment_records", errors)
        else:
            linked_assessment_ids.add(assessment_id)
            if finding.get("classification") != assessment.get("classification"):
                fail(f"{fid}: classification must match assessment {assessment_id}", errors)
            if set(finding.get("disciplines", [])) != set(assessment.get("disciplines", [])):
                fail(f"{fid}: disciplines must match assessment {assessment_id}", errors)

        for discipline in finding.get("disciplines", []):
            if discipline not in discipline_set:
                fail(f"{fid}: discipline {discipline} is outside baseline.disciplines", errors)
        for key in ("comparison", "root_cause", "solution", "closure_criterion"):
            value = finding.get(key)
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: {key} must be non-empty", errors)

        for key in IMPACT_KEYS:
            value = finding.get("impacts", {}).get(key)
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: lifecycle impact {key} must be explicit or NONE", errors)

        primary_document = finding.get("primary_document")
        if primary_document not in document_id_set and primary_document not in declared_missing:
            fail(f"{fid}: primary_document {primary_document} is not in the baseline inventory", errors)
        for secondary in finding.get("secondary_documents", []):
            if secondary not in document_id_set and secondary not in declared_missing:
                fail(f"{fid}: secondary document {secondary} is not in the baseline inventory", errors)

        _validate_evidence(
            fid,
            list(finding.get("evidence", [])),
            document_by_id,
            thresholds,
            errors,
        )

        if status == "WAIVED" and thresholds.get("require_waiver_metadata"):
            waiver = finding.get("waiver", {})
            reason = waiver.get("reason")
            approval_record_id = waiver.get("approval_record_id")
            if not isinstance(reason, str) or not reason.strip():
                fail(f"{fid}: waived finding requires waiver.reason", errors)
            if not isinstance(approval_record_id, str) or not approval_record_id.strip():
                fail(f"{fid}: waived finding requires waiver.approval_record_id", errors)
            approval = trusted_approvals.get(approval_record_id)
            if not isinstance(approval, dict) or approval.get("human_approved") is not True:
                fail(
                    f"{fid}: waiver approval_record_id must reference a trusted human approval record",
                    errors,
                )

        if finding.get("architecture_impact") and thresholds.get("require_architecture_viability"):
            if not finding.get("alternatives"):
                fail(f"{fid}: architecture finding requires at least one alternative", errors)
            viability = finding.get("viability")
            if not isinstance(viability, str) or not viability.strip():
                fail(f"{fid}: architecture finding requires viability analysis", errors)

    for record in records:
        if (
            record.get("classification") in ISSUE_CLASSIFICATIONS
            and record.get("id") not in linked_assessment_ids
        ):
            fail(
                f"assessment {record.get('id')} classified {record.get('classification')} "
                "requires a corresponding finding",
                errors,
            )

    if thresholds.get("block_on_open_critical") and open_critical:
        fail(f"open CRITICAL findings: {', '.join(open_critical)}", errors)

    expected_gate = "BLOCK" if errors else "PASS"
    if data.get("release_gate") != expected_gate:
        fail(
            f"release_gate={data.get('release_gate')} inconsistent with computed gate {expected_gate}",
            errors,
        )
    return errors


def validate_data(
    data: dict[str, Any], schema: dict[str, Any], config: dict[str, Any]
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
    print("RESULT: BLOCK" if errors else "RESULT: PASS")
    for error in errors:
        print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
