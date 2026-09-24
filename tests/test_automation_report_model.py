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
TECHNICAL_KNOWLEDGE_BASE = ROOT / "datacenter" / "AUTOMATION_TECHNICAL_KNOWLEDGE_BASE.json"
EVIDENCE_RESEARCH_RULE = ROOT / "governance" / "AUTOMATION_EVIDENCE_RESEARCH_GOLDEN_RULE_v1_0.md"
GOVERNANCE_MODEL = ROOT / "governance" / "AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md"
EXPORT_PROFILES = ROOT / "datacenter" / "AUTOMATION_REPORT_EXPORT_PROFILES.json"
COMPACT_XLSX_RULE = ROOT / "governance" / "AUTOMATION_COMPACT_EXCEL_EXPORT_MODEL_v1_0.md"
ELABORATION_EXECUTION_MODEL = ROOT / "datacenter" / "AUTOMATION_ELABORATION_EXECUTION_CONTROL.json"
ELABORATION_EXECUTION_RULE = ROOT / "governance" / "AUTOMATION_ELABORATION_EXECUTION_CONTROL_GOLDEN_RULE_v1_0.md"


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


def test_do_relay_invariant_is_repository_pinned() -> None:
    kb = load_json(TECHNICAL_KNOWLEDGE_BASE)
    statements = " ".join(item["statement"] for item in kb["invariants"])
    consequences = " ".join(item["consequence"] for item in kb["invariants"])
    assert "digital output (DO/DQ)" in statements
    assert "external interposing relay" in statements
    assert "Do not derive relay count from DO count" in consequences
    rule = EVIDENCE_RESEARCH_RULE.read_text(encoding="utf-8")
    assert "relay quantity SHALL NOT be derived from DO quantity" in rule
    assert "quantity, naming similarity" in rule


def test_report_model_requires_evidence_before_assumption() -> None:
    model = load_json(REPORT_MODEL)
    assert model["evidence_research"]["required"] is True
    assert model["evidence_research"]["forbid_quantity_only_mapping"] is True
    assert model["evidence_research"]["github_open_source_support"] is True
    assert model["evidence_research"]["research_plugin_discovery"] is True


def test_custom_config_cannot_disable_evidence_research(tmp_path: Path) -> None:
    cfg = deepcopy(config())
    cfg["automation_evidence_research"]["forbid_quantity_only_mapping"] = False
    path = tmp_path / "custom-evidence.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot override repository-pinned Automation compatibility policy"):
        _load_policy_config(path)


def test_owning_document_routing_is_mandatory_before_user_question() -> None:
    model = load_json(REPORT_MODEL)
    er = model["evidence_research"]
    assert er["document_routing_before_user_question"] is True
    assert er["user_pointed_document_must_be_rechecked"] is True
    assert er["project_source_resolution_removes_user_question"] is True
    rule = EVIDENCE_RESEARCH_RULE.read_text(encoding="utf-8")
    assert "Document-routing gate before user questions" in rule
    assert "network topology" in rule
    assert "A question that can be answered from its owning project document is NOT a user question" in rule


def test_compact_xlsx_export_profile_is_pinned() -> None:
    profile = load_json(EXPORT_PROFILES)
    assert profile["profile_id"] == "AUTOMATION_COMPACT_XLSX_V1"
    assert profile["default_for_external_review"] is True
    names = [sheet["name"] for sheet in profile["sheets"]]
    assert names == [
        "00_Resumo",
        "01_Documentos_e_Acoes",
        "02_Pendencias",
        "03_Perguntas_Respondidas",
    ]
    assert profile["rules"]["findings_grouped_by_document_action"] is True
    assert profile["rules"]["owner_column_default"] is False
    assert profile["rules"]["external_review_fields_default"] is False


def test_compact_xlsx_rule_keeps_traceability_without_sheet_sprawl() -> None:
    text = COMPACT_XLSX_RULE.read_text(encoding="utf-8")
    assert "Decisions and Release Gate belong in the Summary sheet" in text
    assert "Findings are consolidated into the Documents & Actions sheet" in text
    assert "Never delete a superseded user answer" in text


def test_elaboration_execution_control_is_pinned() -> None:
    model = load_json(ELABORATION_EXECUTION_MODEL)
    assert model["model_id"] == "AUTOMATION_ELABORATION_EXECUTION_CONTROL_V1_0"
    assert model["mandatory"] is True
    assert model["action_record"]["owning_document_required"] is True
    assert model["action_record"]["closed_requires_recheck"] is True
    assert model["execution_control"]["closure_on_revision_statement_only"] is False
    assert model["network_ip_cybersecurity"]["iec_62443_universal_nonconformity"] is False
    assert model["network_ip_cybersecurity"]["design_stage_deferral_requires_deliverable_and_closure_criterion"] is True


def test_elaboration_execution_rule_covers_network_ip_and_recheck() -> None:
    rule_text = ELABORATION_EXECUTION_RULE.read_text(encoding="utf-8")
    assert "Automation network / IP / cybersecurity elaboration" in rule_text
    assert "port map" in rule_text
    assert "VLAN/subnet segmentation" in rule_text
    assert "zones and conduits" in rule_text
    assert "firewall/DMZ" in rule_text
    assert "IEC 62443" in rule_text
    assert "`CLOSED` is allowed only after" in rule_text


def test_custom_config_cannot_disable_elaboration_execution_control(tmp_path: Path) -> None:
    cfg = deepcopy(config())
    cfg["elaboration_execution_control"]["revised_document_recheck_required"] = False
    path = tmp_path / "custom-elaboration.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot override repository-pinned Automation compatibility policy"):
        _load_policy_config(path)
