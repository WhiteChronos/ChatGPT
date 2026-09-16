from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from pipeline.engineering_compatibility_gate import (
    _load_policy_config,
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
        "id": "F-WAIVER-ROUND6-001",
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
        "proposed_text": "NONE",
        "owner": "HVAC",
        "dependencies": [],
        "closure_criterion": "Regression condition is objectively satisfied.",
        "confidence": "HIGH",
        "waiver": {
            "reason": "Synthetic authorized waiver for regression testing.",
            "approval_record_id": "APR-ROUND6-001",
        },
    }


def test_waiver_subject_hash_includes_linked_assessment_payload() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    finding = _waived_finding(data)
    data["findings"] = [finding]
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-ROUND6-001"] = {
        "human_approved": True,
        "approver": "Chief Engineer",
        "approved_at": "2026-09-16T10:00:00Z",
        "evidence": "synthetic://approval/APR-ROUND6-001",
        "project": data["project"],
        "finding_id": finding["id"],
        "assessment_id": finding["assessment_id"],
        "subject_hash": _waiver_subject_hash(
            data["project"], finding, data["baseline"], assessment
        ),
    }

    assessment["criterion"] = "Materially changed criterion after approval"
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, cfg)
    assert any("subject_hash does not match" in error for error in errors)


def test_document_identifiers_cannot_alias_via_case_or_whitespace() -> None:
    data = example()
    alias = deepcopy(data["baseline"]["documents"][0])
    alias["id"] = "ex-hvac-001"
    data["baseline"]["documents"].append(alias)
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicate document ids after whitespace/case normalization" in error for error in errors)

    data = example()
    data["assessment_records"][0]["document_ids"] = ["EX-HVAC-001", "ex-hvac-001"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("duplicate document identifiers after whitespace/case normalization" in error for error in errors)


def test_traceable_location_requires_locator_after_keyword() -> None:
    data = example()
    data["assessment_records"][0]["evidence"][0]["location"] = "page"
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("with a locator value" in error for error in errors)

    data = example()
    data["assessment_records"][0]["evidence"][0]["location"] = "Page 7"
    assert validate_data(data, load_json(SCHEMA), config()) == []


def test_custom_config_cannot_inject_trusted_waiver_records(tmp_path: Path) -> None:
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["FAKE"] = {
        "human_approved": True,
        "approver": "Producer",
        "approved_at": "2026-09-16T10:00:00Z",
        "evidence": "synthetic://fabricated",
        "project": "Example Project",
        "finding_id": "FAKE",
        "assessment_id": "ASM-HVAC-001",
        "subject_hash": "0" * 64,
    }
    custom = tmp_path / "producer-config.json"
    custom.write_text(__import__("json").dumps(cfg), encoding="utf-8")

    with pytest.raises(ValueError, match="repository-pinned canonical trust source"):
        _load_policy_config(custom)


def test_multidisciplinary_baseline_requires_interface_assessment() -> None:
    data = example()
    data["assessment_records"] = [
        record for record in data["assessment_records"] if not record["interface"]
    ]
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 0,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("multidisciplinary baseline requires at least one multidisciplinary interface assessment" in error for error in errors)


def test_excluded_only_document_scope_uses_defined_zero_score() -> None:
    data = example()
    electrical = next(
        record for record in data["assessment_records"] if record["id"] == "ASM-ELE-001"
    )
    electrical["classification"] = "NOT_APPLICABLE"
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 0,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 1,
    }
    data["compatibility"]["by_discipline"]["ELECTRICAL"] = 0.0
    data["compatibility"]["by_document"]["EX-ELE-001"] = 0.0
    data["release_gate"] = "PASS"

    assert validate_data(data, load_json(SCHEMA), config()) == []
