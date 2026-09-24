from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from pipeline.engineering_compatibility_gate import (
    _load_policy_config,
    load_json,
    validate_semantics,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
REFERENCE_LIBRARY = ROOT / "datacenter" / "AUTOMATION_REFERENCE_LIBRARY.json"
REPORT_MODEL = ROOT / "datacenter" / "AUTOMATION_COMPATIBILITY_REPORT_MODEL.json"
GOVERNANCE_MODEL = ROOT / "governance" / "AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md"


def config() -> dict:
    return load_json(CONFIG)


def example() -> dict:
    return load_json(EXAMPLE)


def test_reference_library_contains_pinned_automation_references() -> None:
    library = load_json(REFERENCE_LIBRARY)
    ids = {item["id"] for item in library["standards"]}
    assert {"PETROBRAS-N-1882", "PETROBRAS-N-1883", "PETROBRAS-N-2833"} <= ids

    n1883 = next(item for item in library["standards"] if item["id"] == "PETROBRAS-N-1883")
    assert "HVAC automation" in n1883["scope_exclusions"]
    assert n1883["default_applicability"] == "REFERENCE_ONLY_UNLESS_INVOKED"


def test_report_model_is_pinned_and_visualize_first() -> None:
    model = load_json(REPORT_MODEL)
    assert model["model_id"] == "AUTOMATION_COMPATIBILITY_REPORT_MODEL_V1_0"
    assert model["renderer"]["primary"] == "Visualize"
    assert model["renderer"]["progressive_enhancement"] is True
    assert model["protocol_zero"]["official_or_normative_source_check_required_before_user_question"] is True
    assert "documents_to_correct" in GOVERNANCE_MODEL.read_text(encoding="utf-8").lower()


def test_automation_finding_requires_documents_involved() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    assessment["classification"] = "DIVERGENT"
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 0,
        "DIVERGENT": 1,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"
    data["findings"] = [{
        "id": "F-MODEL-001",
        "assessment_id": assessment["id"],
        "severity": "HIGH",
        "classification": "DIVERGENT",
        "status": "OPEN",
        "disciplines": list(assessment["disciplines"]),
        "evidence": deepcopy(assessment["evidence"]),
        "evidence_quality": deepcopy(assessment["evidence_quality"]),
        "comparison": "Synthetic comparison.",
        "problem": "Synthetic divergent condition.",
        "root_cause": "Synthetic cause.",
        "claim_basis": {
            "comparison": "SOURCE_DERIVED",
            "problem": "INFERENCE",
            "root_cause": "INFERENCE",
            "solution": "INFERENCE",
        },
        "impacts": {
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
        },
        "solution": "Synthetic correction.",
        "architecture_impact": False,
        "primary_document": assessment["document_ids"][0],
        "secondary_documents": [],
        "proposed_text": "NONE",
        "owner": "HVAC",
        "dependencies": [],
        "closure_criterion": "Synthetic closure.",
        "confidence": "HIGH",
    }]

    errors = validate_semantics(data, config())
    assert any("documents_involved is required" in error for error in errors)


def test_unanswered_question_requires_external_pre_escalation_check() -> None:
    data = example()
    q = data["protocol_zero"]["questions"][0]
    q["status"] = "UNANSWERED"
    q["answer"] = ""
    q["promotes_to_finding"] = False
    q["source_checks"] = [{
        "source_type": "PROJECT_DOCUMENT",
        "source_id": "EX-AUT-001",
        "result": "PARTIAL",
        "note": "Only project evidence was checked.",
    }]
    data["protocol_zero"]["unresolved_count"] = 1
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("normative/official/specialist pre-escalation source check" in error for error in errors)


def test_project_invoked_reference_must_be_applicable() -> None:
    data = example()
    record = next(item for item in data["reference_library"]["standards"] if item["id"] == "PETROBRAS-N-1882")
    record["project_invoked"] = True
    record["applicability"] = "REFERENCE_ONLY"
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("project_invoked=true requires applicability=APPLICABLE" in error for error in errors)


def test_custom_config_cannot_disable_report_model_controls(tmp_path: Path) -> None:
    cfg = deepcopy(config())
    cfg["finding_contract"]["require_documents_involved"] = False
    path = tmp_path / "custom.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")

    with pytest.raises(ValueError, match="cannot override repository-pinned Automation compatibility policy"):
        _load_policy_config(path)


def test_question_batches_are_visualize_artifacts() -> None:
    model = load_json(REPORT_MODEL)
    qp = model["question_presentation"]
    assert qp["required"] is True
    assert qp["renderer"] == "Visualize"
    assert qp["plain_markdown_batch_allowed_when_interactive_available"] is False
    assert qp["require_answer_field"] is True
    assert qp["require_response_block_generator"] is True
    assert qp["retain_resolved_questions"] is True
    assert qp["rerun_protocol_zero_after_answer"] is True
    assert {
        "question_id",
        "severity_or_priority",
        "discipline_or_area",
        "question",
        "rationale",
        "project_documents_involved",
        "source_checks",
        "status",
        "answer_field",
    } <= set(qp["required_fields"])


def test_question_format_is_part_of_golden_rule() -> None:
    text = GOVERNANCE_MODEL.read_text(encoding="utf-8")
    assert "Question presentation contract" in text
    assert "plain Markdown/list-only" in text
    assert "answer field" in text
