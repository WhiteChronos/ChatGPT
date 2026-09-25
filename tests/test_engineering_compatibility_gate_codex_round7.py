from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pipeline.engineering_compatibility_gate import (
    _valid_traceable_location,
    _waiver_subject_hash,
    load_json,
    validate_semantics,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"


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
        "id": "F-WAIVER-ROUND7-001",
        "assessment_id": assessment["id"],
        "severity": "CRITICAL",
        "classification": assessment["classification"],
        "status": "WAIVED",
        "disciplines": list(assessment["disciplines"]),
        "evidence": deepcopy(assessment["evidence"]),
        "evidence_quality": {
            "rating": "HIGH",
            "rationale": "Regression evidence is tied to the current assessment and package.",
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
            "reason": "Temporary risk acceptance for regression testing.",
            "approval_record_id": "APR-ROUND7-001",
        },
    }


def test_assessment_identity_strips_default_ignorable_unicode() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-ZWSP-001"
    clone["criterion"] = "HVAC baseline\u200b compatibility"
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_waiver_subject_hash_binds_waiver_reason() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    finding = _waived_finding(data)
    data["findings"] = [finding]

    approved_hash = _waiver_subject_hash(
        data["project"], finding, data["baseline"], assessment
    )
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-ROUND7-001"] = {
        "human_approved": True,
        "approver": "Chief Engineer",
        "approved_at": "2026-09-16T10:00:00Z",
        "evidence": "synthetic://approval/APR-ROUND7-001",
        "project": data["project"],
        "finding_id": finding["id"],
        "assessment_id": finding["assessment_id"],
        "subject_hash": approved_hash,
    }

    finding["waiver"]["reason"] = "Materially different permanent risk acceptance rationale."
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, cfg)
    assert any("subject_hash does not match" in error for error in errors)


def test_traceable_location_rejects_generic_following_words() -> None:
    assert _valid_traceable_location("Page 7")
    assert _valid_traceable_location("Sheet A1")
    assert _valid_traceable_location("Drawing PN-3501.00-2001")
    assert _valid_traceable_location("Section A")

    assert not _valid_traceable_location("See page for details")
    assert not _valid_traceable_location("Page TAG")
    assert not _valid_traceable_location("Drawing details")
    assert not _valid_traceable_location("Section summary")

    data = example()
    data["assessment_records"][0]["evidence"][0]["location"] = "See page for details"
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("with a locator value" in error for error in errors)
