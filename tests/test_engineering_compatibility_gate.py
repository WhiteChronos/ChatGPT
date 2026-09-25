from __future__ import annotations

from copy import deepcopy
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from pipeline.engineering_compatibility import summarize
from pipeline.engineering_compatibility_gate import (
    DEFAULT_DATA,
    _waiver_subject_hash,
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
    validator = Draft202012Validator(load_json(SCHEMA), format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(data)]


def config() -> dict:
    return load_json(CONFIG)


def example() -> dict:
    return load_json(EXAMPLE)


def template() -> dict:
    return load_json(TEMPLATE)


def make_tradeoffs() -> dict:
    return {
        "simplicity": {"assessment": "IMPROVES", "rationale": "Synthetic alternative is simpler."},
        "safety": {"assessment": "EQUIVALENT", "rationale": "Synthetic safety performance is equivalent."},
        "cost": {"assessment": "IMPROVES", "rationale": "Synthetic lifecycle cost is lower."},
        "maintainability": {"assessment": "IMPROVES", "rationale": "Synthetic maintenance burden is lower."},
    }


def make_example_finding(*, status: str = "CLOSED", severity: str = "HIGH") -> dict:
    return {
        "id": "TEST-001",
        "assessment_id": "ASM-HVAC-001",
        "severity": severity,
        "classification": "VERIFIED",
        "status": status,
        "disciplines": ["HVAC"],
        "evidence": [
            {
                "document_id": "EX-HVAC-001",
                "revision": "A",
                "location": "Sheet 1 / TAG TEST",
                "tag": "TEST",
                "statement": "Synthetic evidence for regression testing.",
                "source_hash": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
            }
        ],
        "evidence_quality": {
            "rating": "HIGH",
            "rationale": "Synthetic evidence is tied to the immutable regression source.",
        },
        "comparison": "Synthetic comparison against the coordinated project baseline.",
        "problem": "Synthetic compatibility condition used only by the regression suite.",
        "root_cause": "Synthetic root cause for regression testing.",
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
        "solution": "Synthetic correction or accepted disposition.",
        "architecture_impact": False,
        "primary_document": "EX-HVAC-001",
        "secondary_documents": [],
        "documents_involved": {
            "source_evidence": [
                {
                    "document_id": "EX-HVAC-001",
                    "revision": "A",
                    "applicability": "APPLICABLE",
                    "note": "Synthetic regression source document.",
                }
            ],
            "project_correlated_or_conflicting": [],
            "normative_or_reference": [],
            "documents_to_correct": [
                {
                    "document_id": "EX-HVAC-001",
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
    }


def test_example_project_is_permanent_positive_regression_case() -> None:
    data = example()
    assert validate_data(data, load_json(SCHEMA), config()) == []
    assert data["release_gate"] == "PASS"


def test_template_is_schema_valid_but_semantically_blocked() -> None:
    data = template()
    assert schema_messages(data) == []
    errors = validate_semantics(data, config())
    assert errors
    assert any("non-current" in error or "not reconciled" in error for error in errors)


def test_workflow_covers_both_validators_and_positive_fixture() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "pipeline/engineering_compatibility*.py" in workflow
    assert "python pipeline/engineering_compatibility_gate.py" in workflow
    assert "pytest -q tests/test_engineering_compatibility_gate.py" in workflow


def test_no_argument_gate_defaults_to_known_good_fixture() -> None:
    assert DEFAULT_DATA == EXAMPLE


def test_scope_summary_is_derived_from_assessment_records() -> None:
    data = example()
    data["scope_summary"]["VERIFIED"] = 100
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("scope_summary must equal counts derived" in error for error in errors)


def test_declared_compatibility_cannot_ignore_status_weights() -> None:
    data = example()
    for record in data["assessment_records"]:
        record["classification"] = "DIVERGENT"
    data["scope_summary"] = {"VERIFIED": 0, "PARTIAL": 0, "DIVERGENT": 4, "NOT_VERIFIABLE": 0, "NOT_APPLICABLE": 0}
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("compatibility.global" in error and "computed 0.0000%" in error for error in errors)
    assert any("compatibility.interface" in error and "computed 0.0000%" in error for error in errors)


def test_not_verifiable_scope_reduces_coverage_and_cannot_be_diluted() -> None:
    data = example()
    data["assessment_records"][0]["classification"] = "NOT_VERIFIABLE"
    data["scope_summary"] = {"VERIFIED": 3, "PARTIAL": 0, "DIVERGENT": 0, "NOT_VERIFIABLE": 1, "NOT_APPLICABLE": 0}
    data["coverage"] = 100.0
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("coverage" in error and "computed 75.0000%" in error for error in errors)


def test_assessment_records_require_provenance_evidence_and_quality() -> None:
    data = example()
    data["assessment_records"][0].pop("evidence")
    messages = schema_messages(data)
    assert any("'evidence' is a required property" in message for message in messages)

    data = example()
    data["assessment_records"][0].pop("evidence_quality")
    messages = schema_messages(data)
    assert any("'evidence_quality' is a required property" in message for message in messages)


def test_assessment_evidence_hash_is_semantically_verified() -> None:
    data = example()
    data["assessment_records"][0]["evidence"][0]["source_hash"] = "0" * 64
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("assessment ASM-HVAC-001" in error and "source_hash" in error for error in errors)


def test_issue_classified_assessment_requires_corresponding_finding() -> None:
    data = example()
    data["assessment_records"][0]["classification"] = "DIVERGENT"
    data["scope_summary"] = {"VERIFIED": 3, "PARTIAL": 0, "DIVERGENT": 1, "NOT_VERIFIABLE": 0, "NOT_APPLICABLE": 0}
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("ASM-HVAC-001 classified DIVERGENT requires a corresponding finding" in error for error in errors)


def test_interface_assessment_requires_at_least_two_disciplines() -> None:
    data = example()
    data["assessment_records"][0]["interface"] = True
    assert schema_messages(data)


def test_interface_assessment_requires_multidiscipline_evidence() -> None:
    data = example()
    interface_record = next(record for record in data["assessment_records"] if record["interface"])
    interface_record["evidence"] = [interface_record["evidence"][0]]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("interface evidence must cover at least two distinct baseline disciplines" in error for error in errors)


def test_uppercase_and_lowercase_sha256_are_equivalent() -> None:
    data = example()
    finding = make_example_finding()
    data["baseline"]["documents"][0]["sha256"] = finding["evidence"][0]["source_hash"].upper()
    data["findings"] = [finding]
    assert validate_data(data, load_json(SCHEMA), config()) == []


def test_mismatched_sha256_is_rejected() -> None:
    data = example()
    finding = make_example_finding()
    finding["evidence"][0]["source_hash"] = "0" * 64
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("source_hash does not match baseline sha256" in error for error in errors)


def test_required_draft_document_is_treated_as_missing() -> None:
    data = example()
    data["baseline"]["documents"][0]["status"] = "DRAFT"
    data["blocking_missing_documents"] = ["EX-HVAC-001"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("missing or non-current" in error for error in errors)


def test_required_draft_document_cannot_be_declared_present() -> None:
    data = example()
    data["baseline"]["documents"][0]["status"] = "DRAFT"
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("blocking_missing_documents must exactly match" in error for error in errors)


def test_finding_discipline_outside_baseline_is_rejected() -> None:
    data = example()
    finding = make_example_finding()
    finding["disciplines"] = ["NUCLEAR"]
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("outside baseline.disciplines" in error for error in errors)


def test_assessment_discipline_and_document_must_be_in_baseline() -> None:
    data = example()
    data["assessment_records"][0]["disciplines"] = ["NUCLEAR"]
    data["assessment_records"][0]["document_ids"] = ["UNKNOWN-DOC"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("assessment ASM-HVAC-001 uses discipline" in error for error in errors)
    assert any("assessment ASM-HVAC-001 uses document" in error for error in errors)


def test_finding_must_link_to_matching_assessment_record() -> None:
    data = example()
    finding = make_example_finding()
    finding["classification"] = "PARTIAL"
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("classification must match assessment" in error for error in errors)


def test_evidence_quality_is_mandatory() -> None:
    data = example()
    finding = make_example_finding()
    finding.pop("evidence_quality")
    data["findings"] = [finding]
    assert any("'evidence_quality' is a required property" in message for message in schema_messages(data))


def test_not_verifiable_color_mapping_is_mandatory_and_blue() -> None:
    data = example()
    del data["visualization"]["severity_colors"]["NOT_VERIFIABLE"]
    assert any("'NOT_VERIFIABLE' is a required property" in message for message in schema_messages(data))

    data = example()
    data["visualization"]["severity_colors"]["NOT_VERIFIABLE"] = "red"
    assert any("'blue' was expected" in message for message in schema_messages(data))


def test_whitespace_only_required_finding_text_is_rejected() -> None:
    for field in ("comparison", "root_cause", "solution", "closure_criterion"):
        data = example()
        finding = make_example_finding()
        finding[field] = "   "
        data["findings"] = [finding]
        assert schema_messages(data), field


def test_waiver_cannot_self_authorize() -> None:
    data = example()
    finding = make_example_finding(status="WAIVED", severity="CRITICAL")
    finding["waiver"] = {"reason": "Synthetic waiver", "approval_record_id": "FAKE-APPROVAL"}
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("trusted human approval record" in error for error in errors)


def test_trusted_human_approval_record_allows_waiver() -> None:
    data = example()
    finding = make_example_finding(status="WAIVED", severity="CRITICAL")
    finding["waiver"] = {"reason": "Authorized synthetic waiver", "approval_record_id": "APR-TEST-001"}
    data["findings"] = [finding]
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-TEST-001"] = {
        "human_approved": True,
        "approver": "Chief Engineer",
        "approved_at": "2026-09-14T21:00:00Z",
        "evidence": "synthetic://approval/APR-TEST-001",
        "project": data["project"],
        "finding_id": finding["id"],
        "assessment_id": finding["assessment_id"],
        "subject_hash": _waiver_subject_hash(data["project"], finding, data["baseline"]),
    }
    assert validate_data(data, load_json(SCHEMA), cfg) == []


def test_open_critical_blocks_release() -> None:
    data = example()
    data["findings"] = [make_example_finding(status="OPEN", severity="CRITICAL")]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("open CRITICAL findings" in error for error in errors)


def test_architecture_findings_require_viability_and_alternatives() -> None:
    data = example()
    finding = make_example_finding()
    finding["architecture_impact"] = True
    data["findings"] = [finding]
    messages = schema_messages(data)
    assert any("'alternatives' is a required property" in message for message in messages)
    assert any("'viability' is a required property" in message for message in messages)


def test_non_finite_metrics_are_rejected_semantically() -> None:
    data = example()
    data["coverage"] = math.nan
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("coverage must be finite" in error for error in errors)


def test_failed_validation_summary_can_never_report_pass() -> None:
    data = example()
    data["compatibility"]["global"] = 75.0
    data["release_gate"] = "BLOCK"
    errors = validate_data(data, load_json(SCHEMA), config())
    assert errors
    result = summarize(data, errors)
    assert result["release_gate"] == "BLOCK"
    assert result["validation_error_count"] == len(errors)


def test_duplicate_assessment_content_cannot_inflate_scores() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-CLONE"
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_assessment_evidence_must_cover_every_declared_scope() -> None:
    data = example()
    record = data["assessment_records"][0]
    record["disciplines"] = ["HVAC", "ELECTRICAL"]
    record["document_ids"] = ["EX-HVAC-001", "EX-ELE-001"]
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("evidence must cover every declared discipline" in error for error in errors)
    assert any("evidence must cover every declared document" in error for error in errors)


def test_release_threshold_uses_recomputed_compatibility_not_declared_value() -> None:
    data = example()
    cfg = deepcopy(config())
    cfg["thresholds"]["minimum_global_compatibility_percent"] = 87.54

    data["assessment_records"][0]["classification"] = "PARTIAL"
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 1,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["compatibility"]["global"] = 87.54
    data["compatibility"]["by_discipline"]["HVAC"] = 75.0
    data["compatibility"]["by_document"]["EX-HVAC-001"] = 75.0
    finding = make_example_finding()
    finding["classification"] = "PARTIAL"
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    assert not any("compatibility.global 87.5400% inconsistent" in error for error in errors)
    assert any("global compatibility 87.50% below minimum 87.54%" in error for error in errors)


def test_mandatory_governance_controls_cannot_be_disabled_by_config() -> None:
    data = example()
    cfg = deepcopy(config())
    for flag in (
        "block_on_open_critical",
        "block_on_missing_mandatory_document",
        "block_on_unreconciled_baseline",
        "require_provenance_hash",
    ):
        cfg["thresholds"][flag] = False

    data["baseline"]["reconciled"] = False
    data["baseline"]["documents"][0]["status"] = "DRAFT"
    data["blocking_missing_documents"] = ["EX-HVAC-001"]
    data["assessment_records"][0]["evidence"][0]["source_hash"] = "0" * 64
    data["findings"] = [make_example_finding(status="OPEN", severity="CRITICAL")]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    assert any("mandatory governance controls cannot be disabled" in error for error in errors)
    assert any("baseline is not reconciled" in error for error in errors)
    assert any("blocking mandatory documents are missing or non-current" in error for error in errors)
    assert any("source_hash does not match baseline sha256" in error for error in errors)
    assert any("open CRITICAL findings" in error for error in errors)


def test_duplicate_identity_excludes_evidence_quality_metadata() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-QUALITY-CLONE"
    clone["evidence_quality"] = {
        "rating": "LOW",
        "rationale": "Alternate quality metadata must not create a new criterion identity.",
    }
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_metric_tolerance_is_canonical_and_cannot_be_weakened() -> None:
    data = example()
    cfg = deepcopy(config())
    cfg["thresholds"]["metric_tolerance_percent"] = 100
    data["compatibility"]["by_discipline"]["HVAC"] = 0
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, cfg)
    assert any("metric_tolerance_percent must equal canonical 0.05" in error for error in errors)
    assert any("compatibility.by_discipline.HVAC" in error and "inconsistent" in error for error in errors)


def test_trusted_waiver_approval_requires_complete_metadata() -> None:
    data = example()
    finding = make_example_finding(status="WAIVED", severity="CRITICAL")
    finding["waiver"] = {"reason": "Incomplete approval must block", "approval_record_id": "APR-INCOMPLETE"}
    data["findings"] = [finding]
    data["release_gate"] = "BLOCK"
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-INCOMPLETE"] = {
        "human_approved": True,
    }
    errors = validate_semantics(data, cfg)
    assert any("requires a named approver" in error for error in errors)
    assert any("requires an ISO-8601 timestamp with timezone" in error for error in errors)
    assert any("requires approval evidence/reference" in error for error in errors)


def test_finding_narratives_require_structured_claim_basis() -> None:
    data = example()
    finding = make_example_finding()
    finding.pop("claim_basis")
    data["findings"] = [finding]
    assert any("'claim_basis' is a required property" in message for message in schema_messages(data))

    data = example()
    finding = make_example_finding()
    finding["architecture_impact"] = True
    finding["alternatives"] = [
        {
            "name": "Synthetic alternative",
            "feasibility": "HIGH",
            "pros": ["Simple"],
            "cons": ["Synthetic only"],
            "recommended": True,
            "tradeoffs": make_tradeoffs(),
        }
    ]
    finding["viability"] = "Synthetic viability analysis."
    data["findings"] = [finding]
    assert any("'viability' is a required property" in message for message in schema_messages(data))


def test_duplicate_identity_excludes_evidence_payloads() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-EVIDENCE-CLONE"
    clone["evidence"][0]["location"] = "Different sheet / same criterion"
    clone["evidence"][0]["statement"] = "Alternate wording for the same scored criterion."
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_trusted_waiver_approval_is_bound_to_current_finding_and_package() -> None:
    data = example()
    finding = make_example_finding(status="WAIVED", severity="CRITICAL")
    finding["waiver"] = {"reason": "Authorized synthetic waiver", "approval_record_id": "APR-BOUND"}
    data["findings"] = [finding]
    cfg = deepcopy(config())
    cfg["waiver_authorization"]["trusted_approval_records"]["APR-BOUND"] = {
        "human_approved": True,
        "approver": "Chief Engineer",
        "approved_at": "2026-09-16T06:30:00Z",
        "evidence": "synthetic://approval/APR-BOUND",
        "project": data["project"],
        "finding_id": finding["id"],
        "assessment_id": finding["assessment_id"],
        "subject_hash": _waiver_subject_hash(data["project"], finding, data["baseline"]),
    }

    finding["root_cause"] = "Changed after the approval was issued."
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, cfg)
    assert any("subject_hash does not match the current finding/baseline package" in error for error in errors)


def test_architecture_alternatives_require_structured_tradeoffs() -> None:
    data = example()
    finding = make_example_finding()
    finding["architecture_impact"] = True
    finding["claim_basis"]["viability"] = "INFERENCE"
    finding["viability"] = "Synthetic architecture viability analysis."
    finding["alternatives"] = [
        {
            "name": "Synthetic alternative",
            "feasibility": "HIGH",
            "pros": ["Simple"],
            "cons": ["Synthetic only"],
            "recommended": True,
        }
    ]
    data["findings"] = [finding]
    assert any("'tradeoffs' is a required property" in message for message in schema_messages(data))

    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("requires structured tradeoffs" in error for error in errors)

    finding["alternatives"][0]["tradeoffs"] = make_tradeoffs()
    data["release_gate"] = "PASS"
    assert validate_data(data, load_json(SCHEMA), config()) == []
