from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from pipeline.engineering_compatibility import summarize
from pipeline.engineering_compatibility_gate import (
    DEFAULT_DATA,
    load_json,
    validate_data,
    validate_semantics,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
TEMPLATE = ROOT / "datasheet" / "ENGINEERING_COMPATIBILITY_DATA_SHEET.json"
WORKFLOW = ROOT / ".github" / "workflows" / "engineering-compatibility-visualize.yml"


def schema_messages(data: dict) -> list[str]:
    schema = load_json(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(data)]


def config() -> dict:
    return load_json(CONFIG)


def example() -> dict:
    return load_json(EXAMPLE)


def template() -> dict:
    return load_json(TEMPLATE)


def make_example_finding(
    *,
    classification: str = "PARTIAL",
    severity: str = "HIGH",
    status: str = "CLOSED",
) -> dict:
    source_hash = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    return {
        "id": "TEST-001",
        "severity": severity,
        "classification": classification,
        "status": status,
        "disciplines": ["HVAC", "ELECTRICAL"],
        "evidence": [
            {
                "document_id": "EX-HVAC-001",
                "revision": "A",
                "location": "Sheet 1 / TAG TEST",
                "tag": "TEST",
                "statement": "Synthetic evidence for regression testing.",
                "source_hash": source_hash,
            }
        ],
        "comparison": "Synthetic comparison against the coordinated project baseline.",
        "problem": "Synthetic compatibility condition used only by the regression suite.",
        "root_cause": "Synthetic root cause for regression testing.",
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
        "solution": "Synthetic correction or accepted disposition.",
        "architecture_impact": False,
        "primary_document": "EX-HVAC-001",
        "secondary_documents": ["EX-ELE-001"],
        "proposed_text": "NONE",
        "owner": "HVAC",
        "dependencies": [],
        "closure_criterion": "Regression condition is objectively satisfied.",
        "confidence": "HIGH",
    }


def test_example_project_is_permanent_positive_regression_case() -> None:
    assert EXAMPLE.exists(), "Permanent positive example datasheet is missing"
    data = example()
    errors = validate_data(data, load_json(SCHEMA), config())
    assert errors == []
    assert data["release_gate"] == "PASS"
    assert data["visualization"]["model"] == "VISUALIZE_GOLDEN_RULE_v1_0"
    assert data["visualization"]["complete_not_summary"] is True


def test_template_is_schema_valid_but_semantically_blocked() -> None:
    data = template()
    assert schema_messages(data) == []
    errors = validate_semantics(data, config())
    assert errors
    assert data["release_gate"] == "BLOCK"


def test_workflow_keeps_no_project_datasheet_protection_and_covers_both_validators() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "shopt -s nullglob globstar" in workflow
    assert "files=(datasheet/projects/**/*.json)" in workflow
    assert "if [ ${#files[@]} -eq 0 ]; then" in workflow
    assert "No project compatibility datasheets found; semantic gate skipped." in workflow
    assert "exit 0" in workflow
    assert "pipeline/engineering_compatibility*.py" in workflow
    assert "python pipeline/engineering_compatibility_gate.py" in workflow
    assert "python pipeline/engineering_compatibility.py" in workflow


def test_no_argument_gate_defaults_to_known_good_fixture() -> None:
    assert DEFAULT_DATA == EXAMPLE


def test_unreconciled_baseline_blocks_release() -> None:
    data = example()
    data["baseline"]["reconciled"] = False
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("baseline is not reconciled" in error for error in errors)


def test_missing_required_document_inventory_is_computed_not_trusted() -> None:
    data = example()
    data["baseline"]["required_document_ids"].append("MISSING-DOC")
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("blocking_missing_documents must exactly match" in error for error in errors)


def test_interface_compatibility_has_its_own_release_threshold() -> None:
    data = example()
    data["compatibility"]["interface"] = 0
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("interface compatibility" in error for error in errors)


def test_not_verifiable_scope_reduces_coverage() -> None:
    data = example()
    data["scope_summary"] = {
        "VERIFIED": 19,
        "PARTIAL": 0,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 1,
        "NOT_APPLICABLE": 0,
    }
    data["coverage"] = 100.0
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("inconsistent with scope_summary" in error for error in errors)


def test_every_baseline_discipline_requires_a_score() -> None:
    data = example()
    del data["compatibility"]["by_discipline"]["AUTOMATION"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("by_discipline keys must exactly match" in error for error in errors)


def test_every_baseline_document_requires_a_score() -> None:
    data = example()
    del data["compatibility"]["by_document"]["EX-AUT-001"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("by_document keys must exactly match" in error for error in errors)


def test_severity_colors_are_schema_constants() -> None:
    data = example()
    data["visualization"]["severity_colors"]["CRITICAL"] = "green"
    assert any("'red' was expected" in message for message in schema_messages(data))


def test_source_hash_is_required_and_well_formed() -> None:
    data = example()
    del data["baseline"]["documents"][0]["sha256"]
    assert any("'sha256' is a required property" in message for message in schema_messages(data))

    data = example()
    data["baseline"]["documents"][0]["sha256"] = "not-a-hash"
    assert any("does not match" in message for message in schema_messages(data))


def test_evidence_identity_and_hash_cannot_be_empty() -> None:
    data = template()
    evidence = data["findings"][0]["evidence"][0]
    evidence["document_id"] = ""
    evidence["source_hash"] = ""
    messages = schema_messages(data)
    assert any("should be non-empty" in message or "is too short" in message for message in messages)
    assert any("does not match" in message for message in messages)


def test_waived_findings_require_recorded_approval() -> None:
    data = template()
    data["findings"][0]["status"] = "WAIVED"
    messages = schema_messages(data)
    assert any("'waiver' is a required property" in message for message in messages)


def test_valid_critical_waiver_is_not_treated_as_open_critical() -> None:
    data = example()
    finding = make_example_finding(severity="CRITICAL", status="WAIVED")
    finding["waiver"] = {
        "reason": "Accepted by authorized engineering approver for regression testing.",
        "approver": "Chief Engineer",
        "approved_at": "2026-09-14T21:00:00Z",
        "approval_evidence": "synthetic://approval/TEST-001",
    }
    data["findings"] = [finding]
    data["scope_summary"]["VERIFIED"] = 19
    data["scope_summary"]["PARTIAL"] = 1
    errors = validate_data(data, load_json(SCHEMA), config())
    assert errors == []


def test_open_critical_is_based_on_status_not_classification() -> None:
    data = example()
    data["findings"] = [make_example_finding(classification="PARTIAL", severity="CRITICAL", status="OPEN")]
    data["scope_summary"]["VERIFIED"] = 19
    data["scope_summary"]["PARTIAL"] = 1
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("open CRITICAL findings" in error for error in errors)


def test_architecture_findings_require_viability_and_alternatives() -> None:
    data = template()
    finding = data["findings"][0]
    finding.pop("viability")
    finding.pop("alternatives")
    messages = schema_messages(data)
    assert any("'alternatives' is a required property" in message for message in messages)
    assert any("'viability' is a required property" in message for message in messages)


def test_comparison_and_lifecycle_impacts_cannot_be_blank() -> None:
    data = template()
    data["findings"][0]["comparison"] = ""
    data["findings"][0]["impacts"]["safety"] = ""
    messages = schema_messages(data)
    assert sum("should be non-empty" in message or "is too short" in message for message in messages) >= 2


def test_calculation_method_requires_structured_denominator() -> None:
    data = example()
    data["compatibility"]["method"] = "x"
    messages = schema_messages(data)
    assert messages


def test_non_finite_metrics_are_rejected_semantically() -> None:
    data = example()
    data["coverage"] = math.nan
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("coverage must be finite" in error for error in errors)


def test_evidence_hash_must_match_baseline_hash() -> None:
    data = example()
    finding = make_example_finding(status="CLOSED")
    finding["evidence"][0]["source_hash"] = "0" * 64
    data["findings"] = [finding]
    data["scope_summary"]["VERIFIED"] = 19
    data["scope_summary"]["PARTIAL"] = 1
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("source_hash does not match baseline sha256" in error for error in errors)


def test_failed_validation_summary_can_never_report_pass() -> None:
    data = example()
    data["compatibility"]["global"] = 75.0
    data["release_gate"] = "BLOCK"
    errors = validate_data(data, load_json(SCHEMA), config())
    assert errors
    result = summarize(data, errors)
    assert result["release_gate"] == "BLOCK"
    assert result["validation_error_count"] == len(errors)
