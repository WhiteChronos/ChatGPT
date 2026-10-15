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


REFERENCE_REGISTRY = Path("datacenter/ENGINEERING_REFERENCE_REGISTRY.json")
HYPERFOCUS_STAGES = {
    "PROCESS_REQUIREMENT",
    "EQUIPMENT_TAG",
    "POWER",
    "COMMAND_FEEDBACK",
    "IO",
    "PLC_RTU",
    "CONTROL_LOGIC",
    "NETWORK_PROTOCOL",
    "DATA_QUALITY",
    "HMI_SCADA",
    "ALARM_HISTORY",
    "FAT_SAT",
}


def _source_governance_errors(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        registry = _impl.load_json(REFERENCE_REGISTRY)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"engineering reference registry load error: {exc}"]

    authority_ids = {
        item.get("id")
        for item in registry.get("authoritative_sources", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    repository_ids = {
        item.get("id")
        for item in registry.get("open_source_repositories", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    context = data.get("reference_context")
    if not isinstance(context, dict):
        return ["reference_context is required"]
    if context.get("registry_id") != registry.get("registry_id"):
        _impl.fail(
            "reference_context.registry_id must match the canonical engineering reference registry",
            errors,
        )

    try:
        canonical_config = _impl.load_json(_impl.DEFAULT_CONFIG)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return errors + [f"canonical source profile load error: {exc}"]
    profiles = canonical_config.get("reference_profiles", {})
    profile_id = context.get("profile_id")
    if not isinstance(profiles, dict) or profile_id not in profiles:
        _impl.fail(
            f"reference_context.profile_id {profile_id!r} is not a repository-pinned reference profile",
            errors,
        )

    declared_authorities = context.get("authoritative_source_ids", [])
    declared_repositories = context.get("open_source_repository_ids", [])
    if not isinstance(declared_authorities, list):
        declared_authorities = []
    if not isinstance(declared_repositories, list):
        declared_repositories = []

    unknown_authorities = sorted(set(declared_authorities) - authority_ids)
    if unknown_authorities:
        _impl.fail(
            f"reference_context contains unknown authoritative source ids: {unknown_authorities}",
            errors,
        )
    unknown_repositories = sorted(set(declared_repositories) - repository_ids)
    if unknown_repositories:
        _impl.fail(
            f"reference_context contains unknown open-source repository ids: {unknown_repositories}",
            errors,
        )

    for record in data.get("assessment_records", []):
        if not isinstance(record, dict):
            continue
        rid = record.get("id", "UNKNOWN")
        refs = record.get("reference_ids", [])
        if not isinstance(refs, list):
            continue
        invalid = sorted(set(refs) - authority_ids)
        if invalid:
            _impl.fail(
                f"assessment {rid} reference_ids must resolve to authoritative registry entries; unknown={invalid}",
                errors,
            )
        undeclared = sorted(set(refs) - set(declared_authorities))
        if undeclared:
            _impl.fail(
                f"assessment {rid} uses authoritative references not declared in reference_context: {undeclared}",
                errors,
            )

    for finding in data.get("findings", []):
        if not isinstance(finding, dict):
            continue
        fid = finding.get("id", "UNKNOWN")
        refs = finding.get("external_reference_ids", [])
        if not isinstance(refs, list):
            refs = []
        invalid = sorted(set(refs) - authority_ids)
        if invalid:
            _impl.fail(
                f"{fid}: external_reference_ids must resolve to authoritative registry entries; unknown={invalid}",
                errors,
            )
        undeclared = sorted(set(refs) - set(declared_authorities))
        if undeclared:
            _impl.fail(
                f"{fid}: external references must be declared in reference_context: {undeclared}",
                errors,
            )
        claim_basis = finding.get("claim_basis", {})
        if isinstance(claim_basis, dict) and "EXTERNAL_KNOWLEDGE" in claim_basis.values() and not refs:
            _impl.fail(
                f"{fid}: EXTERNAL_KNOWLEDGE claim basis requires at least one authoritative external_reference_id",
                errors,
            )

    profile = data.get("analysis_profile", {})
    checks = profile.get("hyperfocus_checks", []) if isinstance(profile, dict) else []
    stages = [item.get("stage") for item in checks if isinstance(item, dict)]
    if set(stages) != HYPERFOCUS_STAGES or len(stages) != len(HYPERFOCUS_STAGES):
        missing = sorted(HYPERFOCUS_STAGES - set(stages))
        duplicate = sorted({stage for stage in stages if stages.count(stage) > 1})
        _impl.fail(
            f"analysis_profile.hyperfocus_checks must cover each canonical stage exactly once; missing={missing}, duplicate={duplicate}",
            errors,
        )
    for item in checks:
        if not isinstance(item, dict):
            continue
        if not isinstance(item.get("evidence"), str) or not item.get("evidence", "").strip():
            _impl.fail(
                f"hyperfocus stage {item.get('stage', 'UNKNOWN')} requires nonblank evidence",
                errors,
            )
        stage_refs = item.get("reference_ids", [])
        if not isinstance(stage_refs, list):
            stage_refs = []
        invalid_stage_refs = sorted(set(stage_refs) - authority_ids)
        if invalid_stage_refs:
            _impl.fail(
                f"hyperfocus stage {item.get('stage', 'UNKNOWN')} contains unknown authoritative reference ids: {invalid_stage_refs}",
                errors,
            )
        undeclared_stage_refs = sorted(set(stage_refs) - set(declared_authorities))
        if undeclared_stage_refs:
            _impl.fail(
                f"hyperfocus stage {item.get('stage', 'UNKNOWN')} uses references not declared in reference_context: {undeclared_stage_refs}",
                errors,
            )

    return errors


def validate_semantics(data: dict[str, Any], config: dict[str, Any]) -> list[str]:
    errors = _original_validate_semantics(data, config)
    errors.extend(_round9_errors(data, config))
    errors.extend(_source_governance_errors(data))
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