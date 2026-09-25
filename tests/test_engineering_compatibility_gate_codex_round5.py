from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pipeline.engineering_compatibility_gate import (
    _waiver_subject_hash,
    load_json,
    validate_data,
    validate_semantics,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"


def config() -> dict:
    return load_json(CONFIG)


def example() -> dict:
    return load_json(EXAMPLE)


def _impacts() -> dict[str, str]:
    return {
        "design": "NONE",
        "procurement": "NONE",
        "fabrication": "NONE",
        "programming": "NONE",
        "commissioning": "NONE",
        "operation": "NONE",
        "maintenance": "NONE",
        "safety": "NONE",
        "cost": "NONE",
        "schedule": "NONE",
    }


def _waived_finding(data: dict) -> dict:
    assessment = data["assessment_records"][0]
    return {
        "id": "F-WAIVER-FUTURE-001",
        "assessment_id": assessment["id"],
        "severity": "CRITICAL",
        "classification": assessment["classification"],
        "status": "WAIVED",
        "disciplines": list(assessment["disciplines"]),
        "evidence": deepcopy(assessment["evidence"]),
        "evidence_quality": {
            "rating": "HIGH",
            "rationale": "Regression evidence is tied to the current package.",
        },
        "comparison": "Synthetic source comparison.",
        "problem": "Synthetic waiver regression condition.",
        "root_cause": "Synthetic root cause.",
        "claim_basis": {
            "comparison": "SOURCE_DERIVED",
            "problem": "INFERENCE",
            "root_cause": "INFERENCE",
            "solution": "INFERENCE",
        },
        "impacts": _impacts(),
        "solution": "Synthetic disposition.",
        "architecture_impact": False,
        "primary_document": assessment["document_ids"][0],
        "secondary_documents": [],
        "documents_involved": {
            "source_evidence": [
                {
                    "document_id": assessment["document_ids"][0],
                    "revision": "A",
                    "applicability": "APPLICABLE",
                    "note": "Synthetic regression source document.",
                }
            ],
            "project_correlated_or_conflicting": [],
            "normative_or_reference": [],
            "documents_to_correct": [
                {
                    "document_id": assessment["document_ids"][0],
                    "revision": "A",
                    "applicability": "APPLICABLE",
                    "note": "Synthetic document used for regression correction.",
                }
            ],
        },
        "proposed_text": "NONE",
        "owner": "HVAC",
        "dependencies": [],
        "closure_criterion": "Regression condition is objectively satisfied.",
        "confidence": "HIGH",
        "waiver": {
            "reason": "Synthetic authorized waiver used for regression testing.",
            "approval_record_id": "APR-FUTURE-001",
        },
    }


def test_assessment_identity_casefolds_criterion() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-CASEFOLD-CLONE"
    clone["criterion"] = clone["criterion"].swapcase()
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_future_dated_trusted_waiver_approval_is_rejected() -> None:
    data = example()
    finding = _waived_finding(data)
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"

    cfg = deepcopy(config())
    future = datetime.now(timezone.utc) + timedelta(days=1)
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-FUTURE-001"] = {
        "human_approved": True,
        "approver": "Chief Engineer",
        "approved_at": future.isoformat(),
        "evidence": "synthetic://approval/APR-FUTURE-001",
        "project": data["project"],
        "finding_id": finding["id"],
        "assessment_id": finding["assessment_id"],
        "subject_hash": _waiver_subject_hash(data["project"], finding, data["baseline"]),
    }

    errors = validate_semantics(data, cfg)
    assert any("timestamp cannot be in the future" in error for error in errors)


def test_evidence_requires_sheet_or_page_traceability_and_explicit_tag() -> None:
    data = example()
    evidence = data["assessment_records"][0]["evidence"][0]
    evidence.pop("tag")
    evidence["location"] = "x"
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("tag must be non-empty" in error for error in errors)
    assert any("location must identify a sheet/page/drawing/section" in error for error in errors)

    data = example()
    evidence = data["assessment_records"][0]["evidence"][0]
    evidence["tag"] = "NONE"
    assert validate_data(data, load_json(SCHEMA), config()) == []


def test_pinned_multidiscipline_project_cannot_be_reduced_to_single_discipline() -> None:
    data = example()
    data["baseline"]["disciplines"] = ["HVAC"]
    data["baseline"]["documents"] = [data["baseline"]["documents"][0]]
    data["baseline"]["required_document_ids"] = ["EX-HVAC-001"]
    data["assessment_records"] = [data["assessment_records"][0]]
    data["scope_summary"] = {
        "VERIFIED": 1,
        "PARTIAL": 0,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["compatibility"]["global"] = 100.0
    data["compatibility"]["by_discipline"] = {"HVAC": 100.0}
    data["compatibility"]["by_document"] = {"EX-HVAC-001": 100.0}
    data["compatibility"]["interface"] = 100.0
    data["findings"] = []
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("baseline.disciplines must include every discipline required" in error for error in errors)
    assert any("baseline.documents must include every document required" in error for error in errors)
    assert any("baseline.required_document_ids must include every document required" in error for error in errors)
    assert any("assessment_records must represent every repository-pinned criterion" in error for error in errors)
