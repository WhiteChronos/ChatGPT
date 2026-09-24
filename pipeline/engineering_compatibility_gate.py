#!/usr/bin/env python3
"""Canonical Engineering Compatibility /visualize CI gate v1.1.

Round-9/10 hardening is layered over the frozen v1.1 implementation so the
new Codex controls remain small and independently reviewable:

* assessment criteria must come from a repository-pinned project inventory;
* the pinned inventory defines required baseline scope independently of the
  producer-submitted baseline;
* findings must preserve every authoritative assessment evidence record
  exactly, including singleton source records.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any

try:
    from pipeline import engineering_compatibility_gate_impl as _impl
except ImportError:  # direct execution: python pipeline/engineering_compatibility_gate.py
    import engineering_compatibility_gate_impl as _impl


_original_load_policy_config = _impl._load_policy_config
_original_validate_semantics = _impl.validate_semantics


def _canonical_criterion_inventories(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    inventories = config.get("criterion_inventories")
    return inventories if isinstance(inventories, dict) else {}


def _load_policy_config(path: Path) -> dict[str, Any]:
    """Load policy while pinning criterion inventories to repository policy."""
    requested = _original_load_policy_config(path)
    canonical = _impl.load_json(_impl.DEFAULT_CONFIG)
    if _canonical_criterion_inventories(requested) != _canonical_criterion_inventories(canonical):
        raise ValueError(
            "config.criterion_inventories cannot override the repository-pinned canonical criterion inventory"
        )
    for pinned_key in ("finding_contract", "automation_report_model", "protocol_zero", "automation_evidence_research"):
        if requested.get(pinned_key) != canonical.get(pinned_key):
            raise ValueError(
                f"config.{pinned_key} cannot override repository-pinned Automation compatibility policy"
            )
    return requested


def _normalized_scope(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {
        normalized
        for value in values
        if (normalized := _impl._normalized_identifier(value)) is not None
    }


def _applicable_inventory_entries(data: dict[str, Any], canonical_config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the complete pinned project inventory.

    Applicability is intentionally independent of the producer-submitted
    baseline. Otherwise a producer could remove a failed discipline/document
    from the baseline and silently remove the corresponding criterion from the
    release calculation.
    """
    project = data.get("project")
    inventories = _canonical_criterion_inventories(canonical_config)
    inventory = inventories.get(project)
    if not isinstance(inventory, list):
        return []
    return [entry for entry in inventory if isinstance(entry, dict)]


def _evidence_fingerprint(item: Any) -> str:
    canonical = _impl._canonicalize_fingerprint_value(item)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _evidence_source_key(item: Any) -> str:
    if not isinstance(item, dict):
        return _evidence_fingerprint(item)
    source = {
        "document_id": item.get("document_id"),
        "revision": item.get("revision"),
        "source_hash": item.get("source_hash"),
    }
    canonical = _impl._canonicalize_fingerprint_value(source)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _validate_finding_evidence_preservation(
    fid: Any,
    assessment_evidence: Any,
    finding_evidence: Any,
    errors: list[str],
) -> None:
    required_items = assessment_evidence if isinstance(assessment_evidence, list) else []
    supplied_items = finding_evidence if isinstance(finding_evidence, list) else []

    required_by_source: dict[str, list[str]] = defaultdict(list)
    supplied_by_source: dict[str, list[str]] = defaultdict(list)
    for item in required_items:
        required_by_source[_evidence_source_key(item)].append(_evidence_fingerprint(item))
    for item in supplied_items:
        supplied_by_source[_evidence_source_key(item)].append(_evidence_fingerprint(item))

    for source_key, required_records in required_by_source.items():
        supplied_records = supplied_by_source.get(source_key, [])
        if not supplied_records:
            _impl.fail(
                f"{fid}: finding evidence must account for every linked assessment evidence source",
                errors,
            )
            continue
        missing = Counter(required_records) - Counter(supplied_records)
        if missing:
            _impl.fail(
                f"{fid}: finding evidence must preserve every linked assessment evidence record exactly; missing={sum(missing.values())}",
                errors,
            )


def _round9_errors(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        canonical_config = _impl.load_json(_impl.DEFAULT_CONFIG)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"canonical criterion inventory load error: {exc}"]

    canonical_inventories = _canonical_criterion_inventories(canonical_config)
    configured_inventories = _canonical_criterion_inventories(config)
    if configured_inventories != canonical_inventories:
        _impl.fail(
            "config.criterion_inventories must equal the repository-pinned canonical criterion inventory",
            errors,
        )

    project = data.get("project")
    if project not in canonical_inventories:
        _impl.fail(
            f"project {project!r} has no repository-pinned canonical criterion inventory",
            errors,
        )
        applicable_inventory: list[dict[str, Any]] = []
    else:
        applicable_inventory = _applicable_inventory_entries(data, canonical_config)

    pinned_disciplines: set[str] = set()
    pinned_documents: set[str] = set()
    for entry in applicable_inventory:
        pinned_disciplines.update(_normalized_scope(entry.get("disciplines", [])))
        pinned_documents.update(_normalized_scope(entry.get("document_ids", [])))

    baseline = data.get("baseline", {})
    if not isinstance(baseline, dict):
        baseline = {}
    baseline_disciplines = _normalized_scope(baseline.get("disciplines", []))
    baseline_documents = _normalized_scope(
        [doc.get("id") for doc in baseline.get("documents", []) if isinstance(doc, dict)]
        if isinstance(baseline.get("documents", []), list)
        else []
    )
    required_document_ids = _normalized_scope(baseline.get("required_document_ids", []))

    missing_pinned_disciplines = sorted(pinned_disciplines - baseline_disciplines)
    if missing_pinned_disciplines:
        _impl.fail(
            "baseline.disciplines must include every discipline required by the repository-pinned criterion inventory; "
            f"missing={missing_pinned_disciplines}",
            errors,
        )
    missing_pinned_documents = sorted(pinned_documents - baseline_documents)
    if missing_pinned_documents:
        _impl.fail(
            "baseline.documents must include every document required by the repository-pinned criterion inventory; "
            f"missing={missing_pinned_documents}",
            errors,
        )
    unrequired_pinned_documents = sorted(pinned_documents - required_document_ids)
    if unrequired_pinned_documents:
        _impl.fail(
            "baseline.required_document_ids must include every document required by the repository-pinned criterion inventory; "
            f"missing={unrequired_pinned_documents}",
            errors,
        )

    inventory_by_id: dict[str, dict[str, Any]] = {}
    for entry in applicable_inventory:
        criterion_id = entry.get("criterion_id")
        normalized_id = _impl._normalized_identifier(criterion_id)
        if normalized_id is None:
            _impl.fail(
                f"canonical criterion inventory contains invalid criterion_id {criterion_id!r}",
                errors,
            )
            continue
        if normalized_id in inventory_by_id:
            _impl.fail(
                f"canonical criterion inventory contains duplicate criterion_id {criterion_id}",
                errors,
            )
            continue
        inventory_by_id[normalized_id] = entry

    records = data.get("assessment_records", [])
    seen_inventory_ids: set[str] = set()
    if isinstance(records, list):
        for record in records:
            if not isinstance(record, dict):
                continue
            rid = record.get("id", "UNKNOWN")
            criterion_id = record.get("criterion_id")
            normalized_id = _impl._normalized_identifier(criterion_id)
            expected = inventory_by_id.get(normalized_id) if normalized_id is not None else None
            if expected is None:
                _impl.fail(
                    f"assessment {rid} criterion_id {criterion_id!r} is not in the repository-pinned canonical criterion inventory for project {project!r}",
                    errors,
                )
                continue
            seen_inventory_ids.add(normalized_id)

            if _impl._criterion_display_skeleton(record.get("criterion")) != _impl._criterion_display_skeleton(expected.get("criterion")):
                _impl.fail(
                    f"assessment {rid} criterion text must match canonical inventory entry {expected.get('criterion_id')}",
                    errors,
                )
            if _normalized_scope(record.get("disciplines", [])) != _normalized_scope(expected.get("disciplines", [])):
                _impl.fail(
                    f"assessment {rid} disciplines must match canonical criterion inventory entry {expected.get('criterion_id')}",
                    errors,
                )
            if _normalized_scope(record.get("document_ids", [])) != _normalized_scope(expected.get("document_ids", [])):
                _impl.fail(
                    f"assessment {rid} document_ids must match canonical criterion inventory entry {expected.get('criterion_id')}",
                    errors,
                )
            if record.get("interface") is not expected.get("interface"):
                _impl.fail(
                    f"assessment {rid} interface flag must match canonical criterion inventory entry {expected.get('criterion_id')}",
                    errors,
                )

    missing_inventory_ids = sorted(set(inventory_by_id) - seen_inventory_ids)
    if missing_inventory_ids:
        _impl.fail(
            "assessment_records must represent every repository-pinned criterion; "
            f"missing={missing_inventory_ids}",
            errors,
        )

    record_by_id = {
        record.get("id"): record
        for record in records
        if isinstance(record, dict)
    } if isinstance(records, list) else {}
    findings = data.get("findings", [])
    if isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            fid = finding.get("id", "UNKNOWN")
            assessment = record_by_id.get(finding.get("assessment_id"))
            if not isinstance(assessment, dict):
                continue
            _validate_finding_evidence_preservation(
                fid,
                assessment.get("evidence", []),
                finding.get("evidence", []),
                errors,
            )
    return errors


_ROOT = Path(__file__).resolve().parents[1]
_REFERENCE_LIBRARY_PATH = _ROOT / "datacenter" / "AUTOMATION_REFERENCE_LIBRARY.json"
_REPORT_MODEL_PATH = _ROOT / "datacenter" / "AUTOMATION_COMPATIBILITY_REPORT_MODEL.json"


def _canonical_reference_map() -> dict[str, dict[str, Any]]:
    library = _impl.load_json(_REFERENCE_LIBRARY_PATH)
    standards = library.get("standards", []) if isinstance(library, dict) else []
    return {
        str(item.get("id")): item
        for item in standards
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _round10_errors(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    """Enforce the reusable Automation report model and applicability controls."""
    errors: list[str] = []
    baseline = data.get("baseline", {})
    disciplines = _normalized_scope(baseline.get("disciplines", [])) if isinstance(baseline, dict) else set()
    automation_scope = any(str(value).casefold() == "automation" for value in disciplines)

    try:
        canonical_refs = _canonical_reference_map()
        canonical_model = _impl.load_json(_REPORT_MODEL_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"Automation report-model policy load error: {exc}"]

    report_model = data.get("report_model")
    if not isinstance(report_model, dict):
        _impl.fail("report_model is required", errors)
    else:
        if report_model.get("model") != canonical_model.get("model_id"):
            _impl.fail(
                f"report_model.model must be {canonical_model.get('model_id')!r}",
                errors,
            )
        if report_model.get("question_visual_contract_required") is not True:
            _impl.fail("report_model.question_visual_contract_required must be true", errors)
        if report_model.get("evidence_before_assumption_required") is not True:
            _impl.fail("report_model.evidence_before_assumption_required must be true", errors)

    analysis_profile = data.get("analysis_profile", {})
    if not isinstance(analysis_profile, dict) or analysis_profile.get("evidence_before_assumption_required") is not True:
        _impl.fail("analysis_profile.evidence_before_assumption_required must be true", errors)

    visualization = data.get("visualization", {})
    if not isinstance(visualization, dict) or visualization.get("question_batches_are_visualize_artifacts") is not True:
        _impl.fail("visualization.question_batches_are_visualize_artifacts must be true", errors)

    if automation_scope:
        ref_record = data.get("reference_library")
        if not isinstance(ref_record, dict):
            _impl.fail("reference_library is required for Automation scope", errors)
            project_refs: dict[str, dict[str, Any]] = {}
        else:
            records = ref_record.get("standards", [])
            project_refs = {
                str(item.get("id")): item
                for item in records
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            } if isinstance(records, list) else {}
            missing = sorted(set(canonical_refs) - set(project_refs))
            if missing:
                _impl.fail(
                    f"reference_library must assess every pinned Automation reference; missing={missing}",
                    errors,
                )
            for sid, canonical in canonical_refs.items():
                current = project_refs.get(sid)
                if not isinstance(current, dict):
                    continue
                if current.get("revision") != canonical.get("revision"):
                    _impl.fail(
                        f"reference_library {sid}: revision must match repository-pinned reference {canonical.get('revision')!r}",
                        errors,
                    )
                applicability = current.get("applicability")
                if current.get("project_invoked") is True and applicability != "APPLICABLE":
                    _impl.fail(
                        f"reference_library {sid}: project_invoked=true requires applicability=APPLICABLE",
                        errors,
                    )

    else:
        project_refs = {}

    pz = data.get("protocol_zero", {})
    questions = pz.get("questions", []) if isinstance(pz, dict) else []
    if isinstance(questions, list):
        for question in questions:
            if not isinstance(question, dict):
                continue
            qid = question.get("id", "UNKNOWN")
            if question.get("pre_escalation_search_completed") is not True:
                _impl.fail(f"{qid}: pre_escalation_search_completed must be true", errors)
            checks = question.get("source_checks", [])
            if not isinstance(checks, list) or not checks:
                _impl.fail(f"{qid}: source_checks must be non-empty", errors)
                continue
            source_types = {
                item.get("source_type")
                for item in checks
                if isinstance(item, dict)
            }
            if not source_types.intersection({"PROJECT_DOCUMENT", "CONTRACT_OR_PROJECT_BASIS"}):
                _impl.fail(
                    f"{qid}: source_checks must include project source or project-basis review",
                    errors,
                )
            if question.get("status") == "UNANSWERED":
                external_types = {
                    "APPLICABLE_STANDARD",
                    "REFERENCE_STANDARD",
                    "OFFICIAL_AUTHORITY",
                    "OFFICIAL_MANUFACTURER",
                    "SPECIALIST_REFERENCE",
                }
                if not source_types.intersection(external_types):
                    _impl.fail(
                        f"{qid}: unanswered question requires normative/official/specialist pre-escalation source check",
                        errors,
                    )

    finding_contract = config.get("finding_contract", {}) if isinstance(config, dict) else {}
    require_docs = finding_contract.get("require_documents_involved") is True
    findings = data.get("findings", [])
    if require_docs and isinstance(findings, list):
        for finding in findings:
            if not isinstance(finding, dict):
                continue
            fid = finding.get("id", "UNKNOWN")
            docs = finding.get("documents_involved")
            if not isinstance(docs, dict):
                _impl.fail(f"{fid}: documents_involved is required", errors)
                continue
            source_docs = docs.get("source_evidence", [])
            fix_docs = docs.get("documents_to_correct", [])
            if not isinstance(source_docs, list) or not source_docs:
                _impl.fail(f"{fid}: documents_involved.source_evidence must be non-empty", errors)
            if not isinstance(fix_docs, list) or not fix_docs:
                _impl.fail(f"{fid}: documents_involved.documents_to_correct must be non-empty", errors)

            evidence_ids = {
                item.get("document_id")
                for item in finding.get("evidence", [])
                if isinstance(item, dict)
            }
            declared_source_ids = {
                item.get("document_id")
                for item in source_docs
                if isinstance(item, dict)
            }
            missing_sources = sorted(
                str(value) for value in evidence_ids - declared_source_ids if value is not None
            )
            if missing_sources:
                _impl.fail(
                    f"{fid}: documents_involved.source_evidence must include every finding evidence document; missing={missing_sources}",
                    errors,
                )

            primary = finding.get("primary_document")
            declared_fix_ids = {
                item.get("document_id")
                for item in fix_docs
                if isinstance(item, dict)
            }
            if isinstance(primary, str) and primary and primary not in declared_fix_ids:
                _impl.fail(
                    f"{fid}: primary_document must appear in documents_involved.documents_to_correct",
                    errors,
                )

            normative = docs.get("normative_or_reference", [])
            if isinstance(normative, list):
                for ref in normative:
                    if not isinstance(ref, dict):
                        continue
                    sid = ref.get("document_id")
                    applicability = ref.get("applicability")
                    project_ref = project_refs.get(str(sid))
                    if project_ref is not None and applicability != project_ref.get("applicability"):
                        _impl.fail(
                            f"{fid}: normative/reference applicability for {sid} must match reference_library assessment",
                            errors,
                        )
                    if applicability == "NOT_APPLICABLE" and finding.get("classification") == "DIVERGENT":
                        _impl.fail(
                            f"{fid}: NOT_APPLICABLE normative/reference source cannot support a DIVERGENT finding",
                            errors,
                        )
    return errors


def validate_semantics(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors = _original_validate_semantics(data, config)
    errors.extend(_round9_errors(data, config))
    errors.extend(_round10_errors(data, config))
    return errors


# Patch the implementation module so its existing validate_data()/main() resolve
# the strengthened functions through the module globals they already use.
_impl._load_policy_config = _load_policy_config
_impl.validate_semantics = validate_semantics

# Preserve the public/import surface expected by existing tests and the report
# wrapper without duplicating the mature v1.1 validator implementation.
for _name in dir(_impl):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_impl, _name)

# Re-assert the two patched names after exporting the implementation namespace.
globals()["_load_policy_config"] = _load_policy_config
globals()["validate_semantics"] = validate_semantics


if __name__ == "__main__":
    sys.exit(_impl.main())