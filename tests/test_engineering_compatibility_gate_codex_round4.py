from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from pipeline.engineering_compatibility_gate import load_json, validate_semantics

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
