#!/usr/bin/env python3
"""Canonical Engineering Compatibility /visualize CI gate v1.1."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
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
FIXED_CLASSIFICATIONS = (
    "VERIFIED", "PARTIAL", "DIVERGENT", "NOT_VERIFIABLE", "NOT_APPLICABLE"
)
FIXED_REQUIRED_DOCUMENT_STATUSES = {"CURRENT", "APPROVED"}
FIXED_STATUS_WEIGHTS = {"VERIFIED": 1.0, "PARTIAL": 0.5, "DIVERGENT": 0.0}
FIXED_METRIC_TOLERANCE_PERCENT = 0.05
FIXED_CLAIM_BASIS_VALUES = {"SOURCE_DERIVED", "INFERENCE", "EXTERNAL_KNOWLEDGE"}
REQUIRED_CLAIM_BASIS_FIELDS = ("comparison", "problem", "root_cause", "solution")
ARCHITECTURE_TRADEOFF_DIMENSIONS = ("simplicity", "safety", "cost", "maintainability")
ARCHITECTURE_TRADEOFF_RATINGS = {"IMPROVES", "EQUIVALENT", "DEGRADES"}
FIXED_MANDATORY_SECTIONS = (
    "executive_gate",
    "baseline_map",
    "compatibility_by_discipline",
    "compatibility_by_document",
    "interfaces",
    "complete_findings",
    "feasibility",
    "missing_evidence",
    "action_plan",
    "release_gate",
)
FIXED_SEVERITY_COLORS = {
    "CRITICAL": "red",
    "HIGH": "orange",
    "MEDIUM": "yellow",
    "LOW": "blue",
    "NOT_VERIFIABLE": "blue",
    "VERIFIED": "green",
    "NOT_APPLICABLE": "gray",
}
FIXED_METHOD_NAME = "weighted_status_v1"
FIXED_METHOD_FORMULA = "100 * sum(status_weight * applicable_criterion) / applicable_criteria"
FIXED_DENOMINATOR_DEFINITION = (
    "Applicable assessment records classified VERIFIED, PARTIAL or DIVERGENT; "
    "NOT_APPLICABLE and NOT_VERIFIABLE are excluded from the compatibility denominator."
)
SHA256_RE = re.compile(r"[A-Fa-f0-9]{64}\Z")
TRACEABLE_LOCATION_RE = re.compile(
    r"\b(?:sheet|page|drawing|section|folha|pagina|página|prancha)\b"
    r"\s*(?:[:#/\-]\s*)?([A-Za-z0-9][A-Za-z0-9._/\-]*)",
    re.IGNORECASE,
)
MAX_APPROVAL_CLOCK_SKEW = timedelta(minutes=5)
VACUOUS_INTERFACE_COMPATIBILITY = 100.0
UNSCORED_SCOPE_COMPATIBILITY = 0.0
MANDATORY_THRESHOLD_FLAGS = (
    "block_on_open_critical",
    "block_on_missing_mandatory_document",
    "block_on_unreconciled_baseline",
    "require_baseline_documents",
    "require_provenance_hash",
    "require_waiver_metadata",
    "require_document_scores",
    "require_discipline_scores",
    "require_architecture_viability",
)
MANDATORY_COMPATIBILITY_FLAGS = (
    "exclude_not_applicable_from_denominator",
    "exclude_not_verifiable_from_compatibility_denominator",
    "not_verifiable_reduces_coverage",
    "require_method_disclosure",
)
RELEASE_PERCENT_THRESHOLD_KEYS = (
    "minimum_coverage_percent",
    "minimum_global_compatibility_percent",
    "minimum_interface_compatibility_percent",
)


def _reject_non_standard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def _reject_non_finite_numbers(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite JSON number is not allowed at {path}")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_non_finite_numbers(item, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_non_finite_numbers(item, f"{path}[{index}]")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh, parse_constant=_reject_non_standard_constant)
    _reject_non_finite_numbers(data)
    return data


def _trusted_approval_records(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    authorization = config.get("waiver_authorization")
    if not isinstance(authorization, dict):
        return {}
    records = authorization.get("trusted_approval_records")
    return records if isinstance(records, dict) else {}


def _load_policy_config(path: Path) -> dict[str, Any]:
    """Load project policy while keeping waiver trust pinned to DEFAULT_CONFIG.

    Project configuration may tune permitted threshold values, but it cannot create
    or replace trusted human approvals. The canonical trust inventory is read from
    the repository-pinned configuration and an arbitrary ``--config`` must carry
    exactly that inventory.
    """
    requested = load_json(path)
    canonical = load_json(DEFAULT_CONFIG)
    if not isinstance(requested, dict) or not isinstance(canonical, dict):
        raise ValueError("engineering compatibility configuration must be a JSON object")
    if _trusted_approval_records(requested) != _trusted_approval_records(canonical):
        raise ValueError(
            "config.waiver_authorization.trusted_approval_records cannot override "
            "the repository-pinned canonical trust source"
        )
    return requested


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def schema_errors(data: Any, schema: dict[str, Any]) -> list[str]:
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


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def _parse_approval_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _valid_approval_timestamp(value: Any) -> bool:
    return _parse_approval_timestamp(value) is not None


def _valid_traceable_location(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and TRACEABLE_LOCATION_RE.search(value.strip()) is not None
    )


def _normalized_identifier(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped.casefold()


def _normalized_identifier_set(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    result: set[str] = set()
    for value in values:
        normalized = _normalized_identifier(value)
        if normalized is not None:
            result.add(normalized)
    return result


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
    try:
        total = sum(float(weights[record["classification"]]) for record in applicable)
    except (KeyError, TypeError, ValueError):
        return None
    return 100.0 * total / len(applicable)


def _scoped_score(records: list[dict[str, Any]], weights: dict[str, float]) -> float | None:
    """Return a defined conservative value when a represented scope is excluded-only."""
    computed = _score(records, weights)
    if computed is None and records:
        return UNSCORED_SCOPE_COMPATIBILITY
    return computed


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
    return computed


def _canonicalize_fingerprint_value(value: Any, *, key: str | None = None) -> Any:
    if isinstance(value, str):
        normalized = " ".join(value.split())
        return normalized.lower() if key in {"source_hash", "sha256", "subject_hash"} else normalized
    if isinstance(value, dict):
        return {
            item_key: _canonicalize_fingerprint_value(item_value, key=item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_canonicalize_fingerprint_value(item) for item in value]
    return value


def _assessment_fingerprint(record: dict[str, Any]) -> str:
    """Stable criterion/scope identity independent of outcome/evidence metadata."""
    criterion = record.get("criterion")
    normalized_criterion = " ".join(criterion.split()).casefold() if isinstance(criterion, str) else criterion
    disciplines = [
        _normalized_identifier(value) or str(value)
        for value in record.get("disciplines", [])
    ]
    document_ids = [
        _normalized_identifier(value) or str(value)
        for value in record.get("document_ids", [])
    ]
    payload = {
        "criterion": normalized_criterion,
        "disciplines": sorted(disciplines),
        "document_ids": sorted(document_ids),
        "interface": record.get("interface"),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _legacy_default_assessment(finding: dict[str, Any]) -> dict[str, Any] | None:
    """Compatibility helper for existing tests/tools that used the old 3-arg hash API."""
    try:
        default_data = load_json(DEFAULT_DATA)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(default_data, dict):
        return None
    assessment_id = finding.get("assessment_id")
    for record in default_data.get("assessment_records", []):
        if isinstance(record, dict) and record.get("id") == assessment_id:
            return record
    return None


def _waiver_subject_hash(
    project: Any,
    finding: dict[str, Any],
    baseline: dict[str, Any],
    assessment: dict[str, Any] | None = None,
) -> str:
    """Bind approval to the exact finding, linked assessment, and baseline snapshot."""
    if assessment is None:
        assessment = _legacy_default_assessment(finding)
    finding_payload = {key: value for key, value in finding.items() if key != "waiver"}
    baseline_documents = [
        {
            "id": document.get("id"),
            "discipline": document.get("discipline"),
            "revision": document.get("revision"),
            "sha256": document.get("sha256"),
            "status": document.get("status"),
        }
        for document in baseline.get("documents", [])
    ]
    baseline_documents.sort(key=lambda item: (_normalized_identifier(item.get("id")) or str(item.get("id"))))
    payload = _canonicalize_fingerprint_value(
        {
            "project": project,
            "finding": finding_payload,
            "assessment": assessment,
            "baseline": {
                "documents": baseline_documents,
                "required_document_ids": sorted(
                    baseline.get("required_document_ids", []),
                    key=lambda value: _normalized_identifier(value) or str(value),
                ),
                "reconciled": baseline.get("reconciled"),
            },
        }
    )
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _validate_evidence(
    owner: str,
    evidence: list[dict[str, Any]],
    document_by_id: dict[Any, dict[str, Any]],
    thresholds: dict[str, Any],
    errors: list[str],
    *,
    allowed_document_ids: set[Any] | None = None,
) -> tuple[set[str], set[Any]]:
    evidenced_disciplines: set[str] = set()
    evidenced_documents: set[Any] = set()
    if not evidence:
        fail(f"{owner}: no evidence provided", errors)
        return evidenced_disciplines, evidenced_documents

    for index, item in enumerate(evidence, start=1):
        doc_id = item.get("document_id")
        doc = document_by_id.get(doc_id)
        for field in ("document_id", "revision", "location", "tag", "statement", "source_hash"):
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{owner}: evidence[{index}] {field} must be non-empty", errors)

        if not _valid_traceable_location(item.get("location")):
            fail(
                f"{owner}: evidence[{index}] location must identify a sheet/page/drawing/section "
                "with a locator value; use tag='NONE' when no TAG applies",
                errors,
            )

        source_hash = item.get("source_hash")
        if not _valid_sha256(source_hash):
            fail(f"{owner}: evidence[{index}] source_hash must be exactly 64 hexadecimal characters", errors)

        if allowed_document_ids is not None and doc_id not in allowed_document_ids:
            fail(
                f"{owner}: evidence[{index}] document {doc_id} is outside the linked assessment document scope",
                errors,
            )

        if doc is None:
            fail(f"{owner}: evidence[{index}] document {doc_id} is not in baseline.documents", errors)
            continue

        evidenced_documents.add(doc_id)
        discipline = doc.get("discipline")
        if isinstance(discipline, str):
            evidenced_disciplines.add(discipline)

        if item.get("revision") != doc.get("revision"):
            fail(
                f"{owner}: evidence[{index}] revision {item.get('revision')} does not match "
                f"baseline revision {doc.get('revision')} for {doc_id}",
                errors,
            )
        baseline_hash = doc.get("sha256")
        if (
            isinstance(source_hash, str)
            and isinstance(baseline_hash, str)
            and source_hash.lower() != baseline_hash.lower()
        ):
            fail(
                f"{owner}: evidence[{index}] source_hash does not match baseline sha256 for {doc_id}",
                errors,
            )
    return evidenced_disciplines, evidenced_documents


def _config_sections(config: dict[str, Any], errors: list[str]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    thresholds = config.get("thresholds") if isinstance(config, dict) else None
    compatibility = config.get("compatibility") if isinstance(config, dict) else None
    if not isinstance(thresholds, dict):
        fail("config.thresholds must be an object", errors)
    if not isinstance(compatibility, dict):
        fail("config.compatibility must be an object", errors)
    if not isinstance(thresholds, dict) or not isinstance(compatibility, dict):
        return None
    return thresholds, compatibility


def validate_semantics(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sections = _config_sections(config, errors)
    if sections is None:
        return errors
    thresholds, compatibility_config = sections

    configured_tolerance = _finite_metric(
        thresholds.get("metric_tolerance_percent"),
        "config.thresholds.metric_tolerance_percent",
        errors,
    )
    if configured_tolerance is not None and not math.isclose(
        configured_tolerance,
        FIXED_METRIC_TOLERANCE_PERCENT,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        fail(
            f"config.thresholds.metric_tolerance_percent must equal canonical "
            f"{FIXED_METRIC_TOLERANCE_PERCENT}",
            errors,
        )
    tolerance = FIXED_METRIC_TOLERANCE_PERCENT

    release_thresholds: dict[str, float | None] = {}
    for key in RELEASE_PERCENT_THRESHOLD_KEYS:
        value = _finite_metric(thresholds.get(key), f"config.thresholds.{key}", errors)
        if value is not None and not 0 <= value <= 100:
            fail(f"config.thresholds.{key} must be between 0 and 100", errors)
            value = None
        release_thresholds[key] = value

    configured_classifications = config.get("classifications")
    if configured_classifications != list(FIXED_CLASSIFICATIONS):
        fail(
            f"config.classifications must equal the fixed classification inventory {list(FIXED_CLASSIFICATIONS)}",
            errors,
        )
    classifications = list(FIXED_CLASSIFICATIONS)

    baseline_policy = config.get("baseline_policy")
    configured_statuses = (
        baseline_policy.get("eligible_required_document_statuses")
        if isinstance(baseline_policy, dict)
        else None
    )
    if set(configured_statuses or []) != FIXED_REQUIRED_DOCUMENT_STATUSES:
        fail(
            "config.baseline_policy.eligible_required_document_statuses must be exactly CURRENT and APPROVED",
            errors,
        )
    eligible_statuses = FIXED_REQUIRED_DOCUMENT_STATUSES

    for flag in MANDATORY_THRESHOLD_FLAGS:
        if thresholds.get(flag) is not True:
            fail(
                f"config.thresholds.{flag} must remain true; mandatory governance controls cannot be disabled",
                errors,
            )
    for flag in MANDATORY_COMPATIBILITY_FLAGS:
        if compatibility_config.get(flag) is not True:
            fail(
                f"config.compatibility.{flag} must remain true; mandatory governance controls cannot be disabled",
                errors,
            )
    if compatibility_config.get("required_status_weights") != FIXED_STATUS_WEIGHTS:
        fail(
            f"config.compatibility.required_status_weights must equal fixed weights {FIXED_STATUS_WEIGHTS}",
            errors,
        )

    waiver_authorization = config.get("waiver_authorization")
    if not isinstance(waiver_authorization, dict):
        fail("config.waiver_authorization must be an object", errors)
        waiver_authorization = {}
    if waiver_authorization.get("require_external_approval_record") is not True:
        fail("config.waiver_authorization.require_external_approval_record must remain true", errors)

    visualization_config = config.get("visualization", {})
    severity_config = config.get("severity", {})
    if not isinstance(visualization_config, dict):
        fail("config.visualization must be an object", errors)
        visualization_config = {}
    if not isinstance(severity_config, dict):
        fail("config.severity must be an object", errors)
        severity_config = {}
    configured_sections = visualization_config.get("mandatory_sections")
    if (
        not isinstance(configured_sections, list)
        or len(configured_sections) != len(FIXED_MANDATORY_SECTIONS)
        or set(configured_sections) != set(FIXED_MANDATORY_SECTIONS)
    ):
        fail("config.visualization.mandatory_sections must equal the fixed mandatory section inventory", errors)
    if severity_config != FIXED_SEVERITY_COLORS:
        fail("config.severity must equal the fixed severity color mapping", errors)

    viz = data.get("visualization", {})
    if viz.get("model") != "VISUALIZE_GOLDEN_RULE_v1_0":
        fail("visualization.model must be VISUALIZE_GOLDEN_RULE_v1_0", errors)
    if viz.get("complete_not_summary") is not True:
        fail("/visualize output must be complete_not_summary=true", errors)
    missing_sections = sorted(set(FIXED_MANDATORY_SECTIONS) - set(viz.get("mandatory_sections", [])))
    if missing_sections:
        fail(f"missing visualization sections: {', '.join(missing_sections)}", errors)
    for severity, expected in FIXED_SEVERITY_COLORS.items():
        if viz.get("severity_colors", {}).get(severity) != expected:
            fail(f"visualization.severity_colors.{severity} must be {expected}", errors)

    baseline = data.get("baseline", {})
    disciplines = list(baseline.get("disciplines", []))
    discipline_set = set(disciplines)
    normalized_baseline_disciplines = _normalized_identifier_set(disciplines)
    for discipline in disciplines:
        if not isinstance(discipline, str) or not discipline.strip():
            fail("baseline.disciplines entries must be nonblank strings", errors)
        elif discipline != discipline.strip():
            fail(f"baseline discipline {discipline!r} must not contain leading or trailing whitespace", errors)
    if len(normalized_baseline_disciplines) != len(disciplines):
        fail("baseline.disciplines contains duplicate identifiers after whitespace/case normalization", errors)

    documents = list(baseline.get("documents", []))
    document_ids = [doc.get("id") for doc in documents]
    document_id_set = set(document_ids)
    normalized_document_ids = _normalized_identifier_set(document_ids)
    document_by_id = {doc.get("id"): doc for doc in documents}

    if not documents:
        fail("baseline.documents must contain at least one source document", errors)
    for document_id in document_ids:
        if not isinstance(document_id, str) or not document_id.strip():
            fail("baseline document ids must be nonblank strings", errors)
        elif document_id != document_id.strip():
            fail(f"baseline document id {document_id!r} must not contain leading or trailing whitespace", errors)
    if len(document_ids) != len(document_id_set):
        fail("baseline.documents contains duplicate document ids", errors)
    if len(normalized_document_ids) != len(document_ids):
        fail("baseline.documents contains duplicate document ids after whitespace/case normalization", errors)
    if baseline.get("reconciled") is not True:
        fail("baseline is not reconciled with the current approved revisions", errors)

    for doc in documents:
        doc_discipline = doc.get("discipline")
        if isinstance(doc_discipline, str) and doc_discipline != doc_discipline.strip():
            fail(
                f"baseline document {doc.get('id', 'UNKNOWN')} discipline must not contain leading or trailing whitespace",
                errors,
            )
        if doc_discipline not in discipline_set:
            fail(
                f"baseline document {doc.get('id', 'UNKNOWN')} uses discipline {doc_discipline} outside baseline.disciplines",
                errors,
            )
        if not _valid_sha256(doc.get("sha256")):
            fail(
                f"baseline document {doc.get('id', 'UNKNOWN')} sha256 must be exactly 64 hexadecimal characters",
                errors,
            )

    required_document_ids = set(baseline.get("required_document_ids", []))
    eligible_required_ids = {
        doc.get("id")
        for doc in documents
        if doc.get("id") in required_document_ids and doc.get("status") in eligible_statuses
    }
    computed_missing = required_document_ids - eligible_required_ids
    declared_missing = set(data.get("blocking_missing_documents", []))
    if computed_missing != declared_missing:
        fail(
            "blocking_missing_documents must exactly match missing or non-current baseline.required_document_ids; "
            f"computed={sorted(computed_missing)} declared={sorted(declared_missing)}",
            errors,
        )
    if declared_missing:
        fail(f"blocking mandatory documents are missing or non-current: {sorted(declared_missing)}", errors)

    records = list(data.get("assessment_records", []))
    record_ids = [record.get("id") for record in records]
    if len(record_ids) != len(set(record_ids)):
        fail("assessment_records contains duplicate ids", errors)

    content_fingerprints: dict[str, Any] = {}
    for record in records:
        rid = record.get("id", "UNKNOWN")
        fingerprint = _assessment_fingerprint(record)
        duplicate_of = content_fingerprints.get(fingerprint)
        if duplicate_of is not None:
            fail(
                f"assessment {rid} duplicates assessment content of {duplicate_of}; assessment identity is fixed "
                "by criterion and declared scope, not by id, outcome, evidence, or evidence-quality metadata",
                errors,
            )
        else:
            content_fingerprints[fingerprint] = rid

    derived_counts = {name: 0 for name in classifications}
    for record in records:
        rid = record.get("id", "UNKNOWN")
        classification = record.get("classification")
        if classification in derived_counts:
            derived_counts[classification] += 1
        else:
            fail(f"assessment {rid} has unsupported classification {classification}", errors)

        record_discipline_values = list(record.get("disciplines", []))
        record_disciplines = set(record_discipline_values)
        normalized_record_disciplines = _normalized_identifier_set(record_discipline_values)
        for discipline in record_discipline_values:
            if not isinstance(discipline, str) or not discipline.strip():
                fail(f"assessment {rid} discipline identifiers must be nonblank strings", errors)
            elif discipline != discipline.strip():
                fail(f"assessment {rid} discipline {discipline!r} must not contain leading or trailing whitespace", errors)
        if len(normalized_record_disciplines) != len(record_discipline_values):
            fail(
                f"assessment {rid} contains duplicate discipline identifiers after whitespace/case normalization",
                errors,
            )

        record_document_values = list(record.get("document_ids", []))
        record_documents = set(record_document_values)
        normalized_record_documents = _normalized_identifier_set(record_document_values)
        for document_id in record_document_values:
            if not isinstance(document_id, str) or not document_id.strip():
                fail(f"assessment {rid} document identifiers must be nonblank strings", errors)
            elif document_id != document_id.strip():
                fail(f"assessment {rid} document {document_id!r} must not contain leading or trailing whitespace", errors)
        if len(normalized_record_documents) != len(record_document_values):
            fail(
                f"assessment {rid} contains duplicate document identifiers after whitespace/case normalization",
                errors,
            )

        for discipline in record_disciplines:
            if discipline not in discipline_set:
                fail(f"assessment {rid} uses discipline {discipline} outside baseline.disciplines", errors)
        for document_id in record_documents:
            if document_id not in document_id_set:
                fail(f"assessment {rid} uses document {document_id} outside baseline.documents", errors)

        evidenced_disciplines, evidenced_documents = _validate_evidence(
            f"assessment {rid}",
            list(record.get("evidence", [])),
            document_by_id,
            thresholds,
            errors,
            allowed_document_ids=record_documents,
        )
        if not evidenced_disciplines.issubset(record_disciplines):
            extra = sorted(evidenced_disciplines - record_disciplines)
            fail(f"assessment {rid} evidence uses disciplines outside assessment.disciplines: {extra}", errors)
        missing_disciplines = sorted(record_disciplines - evidenced_disciplines)
        if missing_disciplines:
            fail(
                f"assessment {rid} evidence must cover every declared discipline; missing={missing_disciplines}",
                errors,
            )
        missing_documents = sorted(record_documents - evidenced_documents)
        if missing_documents:
            fail(
                f"assessment {rid} evidence must cover every declared document; missing={missing_documents}",
                errors,
            )

        interface_flag = record.get("interface")
        if len(normalized_record_disciplines) >= 2 and interface_flag is not True:
            fail(f"assessment {rid} is multidisciplinary and must set interface=true", errors)
        if interface_flag is True:
            if len(normalized_record_disciplines) < 2:
                fail(
                    f"assessment {rid} marked interface=true must include at least two distinct normalized disciplines",
                    errors,
                )
            if len(_normalized_identifier_set(list(evidenced_disciplines))) < 2:
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
            f"coverage {declared_coverage:.4f}% inconsistent with assessment_records computed {computed_coverage:.4f}%",
            errors,
        )
    minimum_coverage = release_thresholds["minimum_coverage_percent"]
    if computed_coverage is not None and minimum_coverage is not None and computed_coverage < minimum_coverage:
        fail(f"coverage {computed_coverage:.2f}% below minimum {minimum_coverage}%", errors)

    compatibility = data.get("compatibility", {})
    method = compatibility.get("method", {})
    if method.get("name") != FIXED_METHOD_NAME:
        fail(f"compatibility.method.name must be {FIXED_METHOD_NAME}", errors)
    if method.get("formula") != FIXED_METHOD_FORMULA:
        fail("compatibility.method.formula must match the canonical weighted-status formula", errors)
    if method.get("denominator_definition") != FIXED_DENOMINATOR_DEFINITION:
        fail("compatibility.method.denominator_definition must match the canonical denominator definition", errors)
    if method.get("exclude_not_applicable") is not True:
        fail("compatibility.method.exclude_not_applicable must be true", errors)
    if method.get("exclude_not_verifiable") is not True:
        fail("compatibility.method.exclude_not_verifiable must be true", errors)
    if method.get("status_weights") != FIXED_STATUS_WEIGHTS:
        fail(f"compatibility.method.status_weights must equal {FIXED_STATUS_WEIGHTS}", errors)
    weights = FIXED_STATUS_WEIGHTS

    global_compat = _assert_metric(
        "compatibility.global",
        compatibility.get("global"),
        _score(records, weights),
        tolerance,
        errors,
    )

    interface_records = [
        record
        for record in records
        if len(_normalized_identifier_set(record.get("disciplines", []))) >= 2
    ]
    if interface_records:
        interface_compat = _assert_metric(
            "compatibility.interface",
            compatibility.get("interface"),
            _scoped_score(interface_records, weights),
            tolerance,
            errors,
        )
    elif len(normalized_baseline_disciplines) <= 1:
        declared_interface = _finite_metric(
            compatibility.get("interface"),
            "compatibility.interface",
            errors,
        )
        interface_compat = VACUOUS_INTERFACE_COMPATIBILITY
        if declared_interface is not None and abs(declared_interface - VACUOUS_INTERFACE_COMPATIBILITY) > tolerance:
            fail(
                "compatibility.interface must be 100.0 when the project has no multidisciplinary interfaces",
                errors,
            )
    else:
        interface_compat = None
        fail(
            "multidisciplinary baseline requires at least one multidisciplinary interface assessment; "
            "do not use a vacuous interface score for multi-discipline projects",
            errors,
        )

    discipline_scores = compatibility.get("by_discipline", {})
    if set(discipline_scores) != discipline_set:
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
            _scoped_score(related, weights),
            tolerance,
            errors,
        )

    document_scores = compatibility.get("by_document", {})
    if set(document_scores) != document_id_set:
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
            _scoped_score(related, weights),
            tolerance,
            errors,
        )

    minimum_global = release_thresholds["minimum_global_compatibility_percent"]
    minimum_interface = release_thresholds["minimum_interface_compatibility_percent"]
    if global_compat is not None and minimum_global is not None and global_compat < minimum_global:
        fail(f"global compatibility {global_compat:.2f}% below minimum {minimum_global}%", errors)
    if interface_compat is not None and minimum_interface is not None and interface_compat < minimum_interface:
        fail(f"interface compatibility {interface_compat:.2f}% below minimum {minimum_interface}%", errors)

    record_by_id = {record.get("id"): record for record in records}
    open_critical: list[str] = []
    trusted_approvals = _trusted_approval_records(config)
    linked_assessment_ids: set[Any] = set()

    for finding in data.get("findings", []):
        fid = finding.get("id", "UNKNOWN")
        status = finding.get("status")
        if finding.get("severity") == "CRITICAL" and status in OPEN_STATUSES:
            open_critical.append(fid)

        assessment_id = finding.get("assessment_id")
        assessment = record_by_id.get(assessment_id)
        assessment_documents: set[Any] | None = None
        if assessment is None:
            fail(f"{fid}: assessment_id {assessment_id} is not in assessment_records", errors)
        else:
            linked_assessment_ids.add(assessment_id)
            assessment_documents = set(assessment.get("document_ids", []))
            if finding.get("classification") != assessment.get("classification"):
                fail(f"{fid}: classification must match assessment {assessment_id}", errors)
            if set(finding.get("disciplines", [])) != set(assessment.get("disciplines", [])):
                fail(f"{fid}: disciplines must match assessment {assessment_id}", errors)

        for discipline in finding.get("disciplines", []):
            if not isinstance(discipline, str) or not discipline.strip():
                fail(f"{fid}: discipline identifiers must be nonblank strings", errors)
            elif discipline != discipline.strip():
                fail(f"{fid}: discipline {discipline!r} must not contain leading or trailing whitespace", errors)
            if discipline not in discipline_set:
                fail(f"{fid}: discipline {discipline} is outside baseline.disciplines", errors)
        for field in ("comparison", "root_cause", "solution", "closure_criterion"):
            value = finding.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: {field} must be non-empty", errors)

        claim_basis = finding.get("claim_basis", {})
        if not isinstance(claim_basis, dict):
            fail(f"{fid}: claim_basis must be an object", errors)
            claim_basis = {}
        for field in REQUIRED_CLAIM_BASIS_FIELDS:
            if claim_basis.get(field) not in FIXED_CLAIM_BASIS_VALUES:
                fail(
                    f"{fid}: claim_basis.{field} must classify the narrative as "
                    "SOURCE_DERIVED, INFERENCE, or EXTERNAL_KNOWLEDGE",
                    errors,
                )

        for field in IMPACT_KEYS:
            value = finding.get("impacts", {}).get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{fid}: lifecycle impact {field} must be explicit or NONE", errors)

        primary_document = finding.get("primary_document")
        if primary_document not in document_id_set and primary_document not in declared_missing:
            fail(f"{fid}: primary_document {primary_document} is not in the baseline inventory", errors)
        if assessment_documents is not None and primary_document not in assessment_documents:
            fail(
                f"{fid}: primary_document {primary_document} is outside the linked assessment document scope",
                errors,
            )
        for secondary in finding.get("secondary_documents", []):
            if secondary not in document_id_set and secondary not in declared_missing:
                fail(f"{fid}: secondary document {secondary} is not in the baseline inventory", errors)

        finding_disciplines, finding_documents = _validate_evidence(
            fid,
            list(finding.get("evidence", [])),
            document_by_id,
            thresholds,
            errors,
            allowed_document_ids=assessment_documents,
        )
        if assessment is not None:
            expected_disciplines = set(assessment.get("disciplines", []))
            missing_finding_disciplines = sorted(expected_disciplines - finding_disciplines)
            if missing_finding_disciplines:
                fail(
                    f"{fid}: finding evidence must cover every linked assessment discipline; "
                    f"missing={missing_finding_disciplines}",
                    errors,
                )
            missing_finding_documents = sorted(assessment_documents - finding_documents)
            if missing_finding_documents:
                fail(
                    f"{fid}: finding evidence must cover every linked assessment document; "
                    f"missing={missing_finding_documents}",
                    errors,
                )

        if status == "WAIVED":
            waiver = finding.get("waiver", {})
            reason = waiver.get("reason")
            approval_record_id = waiver.get("approval_record_id")
            if not isinstance(reason, str) or not reason.strip():
                fail(f"{fid}: waived finding requires waiver.reason", errors)
            if not isinstance(approval_record_id, str) or not approval_record_id.strip():
                fail(f"{fid}: waived finding requires waiver.approval_record_id", errors)
            approval = trusted_approvals.get(approval_record_id)
            if not isinstance(approval, dict) or approval.get("human_approved") is not True:
                fail(f"{fid}: waiver approval_record_id must reference a trusted human approval record", errors)
            else:
                approver = approval.get("approver")
                approved_at = approval.get("approved_at")
                approval_evidence = approval.get("evidence")
                approval_project = approval.get("project")
                approval_finding_id = approval.get("finding_id")
                approval_assessment_id = approval.get("assessment_id")
                approval_subject_hash = approval.get("subject_hash")
                expected_subject_hash = _waiver_subject_hash(
                    data.get("project"),
                    finding,
                    baseline,
                    assessment,
                )
                if not isinstance(approver, str) or not approver.strip():
                    fail(f"{fid}: trusted waiver approval requires a named approver", errors)
                approval_timestamp = _parse_approval_timestamp(approved_at)
                if approval_timestamp is None:
                    fail(f"{fid}: trusted waiver approval requires an ISO-8601 timestamp with timezone", errors)
                elif approval_timestamp > datetime.now(timezone.utc) + MAX_APPROVAL_CLOCK_SKEW:
                    fail(
                        f"{fid}: trusted waiver approval timestamp cannot be in the future beyond the 5-minute clock-skew tolerance",
                        errors,
                    )
                if not isinstance(approval_evidence, str) or not approval_evidence.strip():
                    fail(f"{fid}: trusted waiver approval requires approval evidence/reference", errors)
                if approval_project != data.get("project"):
                    fail(f"{fid}: trusted waiver approval project does not match the current package", errors)
                if approval_finding_id != fid:
                    fail(f"{fid}: trusted waiver approval is not bound to this finding", errors)
                if approval_assessment_id != assessment_id:
                    fail(f"{fid}: trusted waiver approval is not bound to this assessment", errors)
                if not _valid_sha256(approval_subject_hash):
                    fail(f"{fid}: trusted waiver approval requires a 64-character subject_hash", errors)
                elif approval_subject_hash.lower() != expected_subject_hash.lower():
                    fail(
                        f"{fid}: trusted waiver approval subject_hash does not match the current "
                        "finding/assessment/baseline package",
                        errors,
                    )

        if finding.get("architecture_impact"):
            alternatives = finding.get("alternatives", [])
            if not alternatives:
                fail(f"{fid}: architecture finding requires at least one alternative", errors)
            for index, alternative in enumerate(alternatives, start=1):
                if not isinstance(alternative, dict):
                    fail(f"{fid}: alternative[{index}] must be an object", errors)
                    continue
                tradeoffs = alternative.get("tradeoffs")
                if not isinstance(tradeoffs, dict):
                    fail(
                        f"{fid}: alternative[{index}] requires structured tradeoffs for simplicity, safety, cost, and maintainability",
                        errors,
                    )
                    continue
                for dimension in ARCHITECTURE_TRADEOFF_DIMENSIONS:
                    dimension_result = tradeoffs.get(dimension)
                    if not isinstance(dimension_result, dict):
                        fail(f"{fid}: alternative[{index}].tradeoffs.{dimension} must be an object", errors)
                        continue
                    rating = dimension_result.get("assessment")
                    rationale = dimension_result.get("rationale")
                    if rating not in ARCHITECTURE_TRADEOFF_RATINGS:
                        fail(
                            f"{fid}: alternative[{index}].tradeoffs.{dimension}.assessment must be "
                            "IMPROVES, EQUIVALENT, or DEGRADES",
                            errors,
                        )
                    if not isinstance(rationale, str) or not rationale.strip():
                        fail(
                            f"{fid}: alternative[{index}].tradeoffs.{dimension}.rationale must be non-empty",
                            errors,
                        )
            viability = finding.get("viability")
            if not isinstance(viability, str) or not viability.strip():
                fail(f"{fid}: architecture finding requires viability analysis", errors)
            if claim_basis.get("viability") not in FIXED_CLAIM_BASIS_VALUES:
                fail(
                    f"{fid}: claim_basis.viability must classify the viability narrative as "
                    "SOURCE_DERIVED, INFERENCE, or EXTERNAL_KNOWLEDGE",
                    errors,
                )

    for record in records:
        if record.get("classification") in ISSUE_CLASSIFICATIONS and record.get("id") not in linked_assessment_ids:
            fail(
                f"assessment {record.get('id')} classified {record.get('classification')} requires a corresponding finding",
                errors,
            )

    if open_critical:
        fail(f"open CRITICAL findings: {', '.join(open_critical)}", errors)

    expected_gate = "BLOCK" if errors else "PASS"
    if data.get("release_gate") != expected_gate:
        fail(
            f"release_gate={data.get('release_gate')} inconsistent with computed gate {expected_gate}",
            errors,
        )
    return errors


def validate_data(data: Any, schema: dict[str, Any], config: dict[str, Any]) -> list[str]:
    try:
        canonical_schema = load_json(DEFAULT_SCHEMA)
        errors = schema_errors(data, canonical_schema)
        if errors:
            return errors
        if schema != canonical_schema:
            custom_errors = schema_errors(data, schema)
            if custom_errors:
                return custom_errors
        if not isinstance(data, dict):
            return ["schema:<root>: datasheet must be an object"]
        return validate_semantics(data, config)
    except Exception as exc:
        return [f"validation error: {type(exc).__name__}: {exc}"]


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
        config = _load_policy_config(Path(args.config))
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