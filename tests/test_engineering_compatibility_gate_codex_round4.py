from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from pipeline.engineering_compatibility_gate import load_json, validate_data, validate_semantics

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
SCHEMA = ROOT / "schemas" / "engineering_compatibility.schema.json"
WRAPPER = ROOT / "pipeline" / "engineering_compatibility.py"


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


def _finding_for_assessment(data: dict, assessment: dict, *, primary_document: str) -> dict:
    evidence = deepcopy(assessment["evidence"])
    return {
        "id": "F-ROUND5-001",
        "assessment_id": assessment["id"],
        "severity": "HIGH",
        "classification": assessment["classification"],
        "status": "OPEN",
        "disciplines": list(assessment["disciplines"]),
        "evidence": evidence,
        "evidence_quality": {
            "rating": "HIGH",
            "rationale": "Regression evidence is tied to the linked assessment scope.",
        },
        "comparison": "Synthetic comparison for Codex regression coverage.",
        "problem": "Synthetic regression condition.",
        "root_cause": "Synthetic root cause.",
        "claim_basis": {
            "comparison": "SOURCE_DERIVED",
            "problem": "INFERENCE",
            "root_cause": "INFERENCE",
            "solution": "INFERENCE",
        },
        "impacts": _impacts(),
        "solution": "Synthetic solution.",
        "architecture_impact": False,
        "primary_document": primary_document,
        "secondary_documents": [],
        "proposed_text": "NONE",
        "owner": "AUTOMATION",
        "dependencies": [],
        "closure_criterion": "Regression condition is objectively satisfied.",
        "confidence": "HIGH",
    }


def test_duplicate_fingerprint_normalizes_sha256_case() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-CASE-CLONE"
    clone["evidence"][0]["source_hash"] = clone["evidence"][0]["source_hash"].upper()
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_classification_inventory_cannot_be_changed_by_custom_config() -> None:
    data = example()
    cfg = deepcopy(config())
    cfg["classifications"].remove("NOT_VERIFIABLE")
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    assert any("fixed classification inventory" in error for error in errors)


def test_required_document_status_policy_cannot_admit_draft() -> None:
    data = example()
    cfg = deepcopy(config())
    cfg["baseline_policy"]["eligible_required_document_statuses"].append("DRAFT")
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    assert any("must be exactly CURRENT and APPROVED" in error for error in errors)


def test_sha256_must_be_exactly_64_hex_characters() -> None:
    data = example()
    data["baseline"]["documents"][0]["sha256"] += "\n"
    data["assessment_records"][0]["evidence"][0]["source_hash"] += "\n"
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("sha256 must be exactly 64 hexadecimal characters" in error for error in errors)
    assert any("source_hash must be exactly 64 hexadecimal characters" in error for error in errors)


def test_finding_evidence_is_constrained_to_linked_assessment_scope() -> None:
    data = example()
    assessment = next(record for record in data["assessment_records"] if record["interface"])
    assessment["classification"] = "PARTIAL"
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 1,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["compatibility"]["global"] = 87.5
    data["compatibility"]["interface"] = 50.0
    data["compatibility"]["by_discipline"]["HVAC"] = 75.0
    data["compatibility"]["by_discipline"]["AUTOMATION"] = 75.0
    data["compatibility"]["by_document"]["EX-HVAC-001"] = 75.0
    data["compatibility"]["by_document"]["EX-AUT-001"] = 75.0
    data["findings"] = [
        {
            "id": "F-IF-001",
            "assessment_id": assessment["id"],
            "severity": "HIGH",
            "classification": "PARTIAL",
            "status": "OPEN",
            "disciplines": ["HVAC", "AUTOMATION"],
            "evidence": [
                {
                    "document_id": "EX-ELE-001",
                    "revision": "A",
                    "location": "Unrelated electrical evidence",
                    "statement": "This evidence is intentionally outside the linked assessment scope.",
                    "source_hash": data["baseline"]["documents"][1]["sha256"],
                }
            ],
            "comparison": "Interface comparison.",
            "root_cause": "Synthetic root cause.",
            "solution": "Synthetic solution.",
            "closure_criterion": "Synthetic closure criterion.",
            "impacts": _impacts(),
            "primary_document": "EX-HVAC-001",
            "secondary_documents": ["EX-AUT-001"],
            "architecture_impact": False,
        }
    ]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("outside the linked assessment document scope" in error for error in errors)
    assert any("finding evidence must cover every linked assessment document" in error for error in errors)


def test_wrapper_overwrites_stale_pass_summary_on_malformed_config(tmp_path: Path) -> None:
    bad_config = tmp_path / "bad-config.json"
    bad_config.write_text("{}", encoding="utf-8")
    summary_path = tmp_path / "summary.json"
    summary_path.write_text('{"release_gate":"PASS"}', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(WRAPPER),
            str(EXAMPLE),
            "--schema",
            str(SCHEMA),
            "--config",
            str(bad_config),
            "--summary",
            str(summary_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["release_gate"] == "BLOCK"
    assert summary["validation_error_count"] >= 1


def test_duplicate_fingerprint_normalizes_whitespace() -> None:
    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-WHITESPACE-CLONE"
    clone["criterion"] += "   \n\t"
    clone["evidence"][0]["statement"] += "   \n"
    clone["evidence_quality"]["rationale"] += "\t  "
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_wrapper_overwrites_stale_pass_summary_for_non_object_datasheet(tmp_path: Path) -> None:
    bad_data = tmp_path / "bad-data.json"
    bad_data.write_text("[]", encoding="utf-8")
    summary_path = tmp_path / "summary.json"
    summary_path.write_text('{"release_gate":"PASS"}', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(WRAPPER),
            str(bad_data),
            "--summary",
            str(summary_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["release_gate"] == "BLOCK"
    assert summary["validation_error_count"] >= 1


def test_visualization_mandatory_sections_cannot_be_reduced_by_custom_config() -> None:
    data = example()
    cfg = deepcopy(config())
    cfg["visualization"]["mandatory_sections"] = ["executive_gate"]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    assert any("fixed mandatory section inventory" in error for error in errors)


def test_multidisciplinary_assessment_is_always_scored_as_interface() -> None:
    data = example()
    assessment = next(record for record in data["assessment_records"] if record["interface"])
    assessment["classification"] = "DIVERGENT"
    assessment["interface"] = False
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 0,
        "DIVERGENT": 1,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("is multidisciplinary and must set interface=true" in error for error in errors)
    assert any("compatibility.interface" in error and "computed 0.0000%" in error for error in errors)


def test_custom_schema_cannot_replace_canonical_schema() -> None:
    data = example()
    data["assessment_records"][0].pop("evidence_quality")
    data["release_gate"] = "BLOCK"

    errors = validate_data(data, {}, config())
    assert any("'evidence_quality' is a required property" in error for error in errors)


def test_primary_document_must_belong_to_linked_assessment_scope() -> None:
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
    data["findings"] = [
        _finding_for_assessment(data, assessment, primary_document="EX-ELE-001")
    ]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("primary_document EX-ELE-001 is outside the linked assessment document scope" in error for error in errors)


def test_disclosed_compatibility_formula_must_match_canonical_method() -> None:
    data = example()
    data["compatibility"]["method"]["formula"] = "100 * arbitrary producer-defined score"
    data["compatibility"]["method"]["denominator_definition"] = "Include every record regardless of status."
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("formula must match the canonical weighted-status formula" in error for error in errors)
    assert any("denominator_definition must match the canonical denominator definition" in error for error in errors)


def test_duplicate_identity_excludes_classification_outcome() -> None:
    data = example()
    divergent = data["assessment_records"][0]
    divergent["classification"] = "DIVERGENT"
    clone = deepcopy(divergent)
    clone["id"] = "ASM-HVAC-OUTCOME-CLONE"
    clone["classification"] = "VERIFIED"
    data["assessment_records"].append(clone)
    data["scope_summary"] = {
        "VERIFIED": 4,
        "PARTIAL": 0,
        "DIVERGENT": 1,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["findings"] = [
        _finding_for_assessment(data, divergent, primary_document="EX-HVAC-001")
    ]
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("duplicates assessment content" in error for error in errors)


def test_release_percentage_thresholds_reject_negative_values() -> None:
    data = example()
    cfg = deepcopy(config())
    for key in (
        "minimum_coverage_percent",
        "minimum_global_compatibility_percent",
        "minimum_interface_compatibility_percent",
    ):
        cfg["thresholds"][key] = -1
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, cfg)
    for key in (
        "minimum_coverage_percent",
        "minimum_global_compatibility_percent",
        "minimum_interface_compatibility_percent",
    ):
        assert any(f"config.thresholds.{key} must be between 0 and 100" in error for error in errors)


def test_discipline_identifiers_cannot_alias_via_whitespace() -> None:
    data = example()
    data["baseline"]["disciplines"].append("HVAC ")
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("must not contain leading or trailing whitespace" in error for error in errors)
    assert any("duplicate identifiers after Unicode compatibility/whitespace/case normalization" in error for error in errors)


def test_load_json_rejects_exponent_overflow_infinity(tmp_path: Path) -> None:
    bad_data = tmp_path / "overflow.json"
    bad_data.write_text('{"evidence":{"value":1e999}}', encoding="utf-8")

    try:
        load_json(bad_data)
    except ValueError as exc:
        assert "non-finite JSON number is not allowed" in str(exc)
    else:
        raise AssertionError("load_json accepted exponent-overflow infinity")
