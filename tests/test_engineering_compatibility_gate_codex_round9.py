from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from pipeline.engineering_compatibility_gate import (
    _load_policy_config,
    load_json,
    validate_semantics,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "datacenter" / "ENGINEERING_COMPATIBILITY_CONFIG.json"
EXAMPLE = ROOT / "datasheet" / "projects" / "example-project.json"
IMPL = ROOT / "pipeline" / "engineering_compatibility_gate_impl.py"


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


def _finding_for(assessment: dict, evidence: list[dict]) -> dict:
    return {
        "id": "F-ROUND9-001",
        "assessment_id": assessment["id"],
        "severity": "HIGH",
        "classification": assessment["classification"],
        "status": "CLOSED",
        "disciplines": list(assessment["disciplines"]),
        "evidence": deepcopy(evidence),
        "evidence_quality": {
            "rating": "HIGH",
            "rationale": "Regression evidence is tied to the linked assessment.",
        },
        "comparison": "Synthetic comparison for round-9 evidence preservation.",
        "problem": "Synthetic partial condition for regression testing.",
        "root_cause": "Synthetic root cause for regression testing.",
        "claim_basis": {
            "comparison": "SOURCE_DERIVED",
            "problem": "INFERENCE",
            "root_cause": "INFERENCE",
            "solution": "INFERENCE",
        },
        "impacts": _impacts(),
        "solution": "Synthetic disposition for regression testing.",
        "architecture_impact": False,
        "primary_document": assessment["document_ids"][0],
        "secondary_documents": [],
        "proposed_text": "NONE",
        "owner": "HVAC",
        "dependencies": [],
        "closure_criterion": "All authoritative assessment evidence is preserved in the finding.",
        "confidence": "HIGH",
    }


def test_criterion_id_must_come_from_repository_pinned_inventory() -> None:
    data = example()
    original = data["assessment_records"][0]
    original["classification"] = "DIVERGENT"

    clone = deepcopy(original)
    clone["id"] = "ASM-HVAC-PUNCT-CLONE"
    clone["criterion_id"] = "CRIT-HVAC-PUNCT-CLONE"
    clone["criterion"] = "HVAC baseline compatibility!"
    clone["classification"] = "VERIFIED"
    data["assessment_records"].append(clone)
    data["scope_summary"] = {
        "VERIFIED": 4,
        "PARTIAL": 0,
        "DIVERGENT": 1,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any(
        "is not in the repository-pinned canonical criterion inventory" in error
        for error in errors
    )


def test_custom_config_cannot_override_canonical_criterion_inventory(tmp_path: Path) -> None:
    cfg = deepcopy(config())
    cfg["criterion_inventories"]["Example Project"].append(
        {
            "criterion_id": "CRIT-PRODUCER-INJECTED",
            "criterion": "Producer injected scored criterion",
            "disciplines": ["HVAC"],
            "document_ids": ["EX-HVAC-001"],
            "interface": False,
        }
    )
    custom = tmp_path / "producer-config.json"
    custom.write_text(json.dumps(cfg), encoding="utf-8")

    with pytest.raises(ValueError, match="repository-pinned canonical criterion inventory"):
        _load_policy_config(custom)


def test_complete_pinned_inventory_is_required_independently_of_submitted_baseline() -> None:
    data = example()
    data["baseline"]["disciplines"].remove("ELECTRICAL")
    data["baseline"]["documents"] = [
        document
        for document in data["baseline"]["documents"]
        if document["id"] != "EX-ELE-001"
    ]
    data["baseline"]["required_document_ids"].remove("EX-ELE-001")
    data["assessment_records"] = [
        record
        for record in data["assessment_records"]
        if record["criterion_id"] != "CRIT-ELE-BASELINE"
    ]
    data["scope_summary"]["VERIFIED"] = 3
    data["compatibility"]["by_discipline"].pop("ELECTRICAL")
    data["compatibility"]["by_document"].pop("EX-ELE-001")

    errors = validate_semantics(data, config())
    assert any(
        "baseline.disciplines must include every discipline required by the repository-pinned criterion inventory" in error
        for error in errors
    )
    assert any(
        "baseline.documents must include every document required by the repository-pinned criterion inventory" in error
        for error in errors
    )
    assert any(
        "assessment_records must represent every repository-pinned criterion" in error
        and "crit-ele-baseline" in error.lower()
        for error in errors
    )


def test_finding_must_preserve_every_linked_assessment_evidence_record() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    assessment["classification"] = "PARTIAL"

    second = deepcopy(assessment["evidence"][0])
    second["location"] = "Page 2 / Contradictory source statement"
    second["statement"] = "Second authoritative evidence record that must not be hidden by the finding."
    assessment["evidence"].append(second)

    data["findings"] = [_finding_for(assessment, [assessment["evidence"][0]])]
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 1,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any(
        "finding evidence must preserve every linked assessment evidence record" in error
        for error in errors
    )


def test_singleton_assessment_evidence_must_be_preserved_exactly() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    assessment["classification"] = "PARTIAL"

    replacement = deepcopy(assessment["evidence"][0])
    replacement["location"] = "Page 9 / Rewritten finding-only location"
    replacement["statement"] = "Finding-only replacement that must not hide the assessment evidence record."
    data["findings"] = [_finding_for(assessment, [replacement])]
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 1,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any(
        "finding evidence must preserve every linked assessment evidence record exactly" in error
        for error in errors
    )


def test_finding_can_preserve_complete_linked_assessment_evidence() -> None:
    data = example()
    assessment = data["assessment_records"][0]
    assessment["classification"] = "PARTIAL"

    second = deepcopy(assessment["evidence"][0])
    second["location"] = "Page 2 / Additional source statement"
    second["statement"] = "Second authoritative evidence record preserved by the finding."
    assessment["evidence"].append(second)

    data["findings"] = [_finding_for(assessment, assessment["evidence"])]
    data["scope_summary"] = {
        "VERIFIED": 3,
        "PARTIAL": 1,
        "DIVERGENT": 0,
        "NOT_VERIFIABLE": 0,
        "NOT_APPLICABLE": 0,
    }
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert not any(
        "finding evidence must preserve every linked assessment evidence record" in error
        for error in errors
    )


def test_direct_impl_entrypoint_delegates_to_canonical_wrapper(tmp_path: Path) -> None:
    data = example()
    data["baseline"]["disciplines"].remove("ELECTRICAL")
    data["baseline"]["documents"] = [
        document
        for document in data["baseline"]["documents"]
        if document["id"] != "EX-ELE-001"
    ]
    data["baseline"]["required_document_ids"].remove("EX-ELE-001")
    data["assessment_records"] = [
        record
        for record in data["assessment_records"]
        if record["criterion_id"] != "CRIT-ELE-BASELINE"
    ]
    data["scope_summary"]["VERIFIED"] = 3
    data["compatibility"]["by_discipline"].pop("ELECTRICAL")
    data["compatibility"]["by_document"].pop("EX-ELE-001")
    data["release_gate"] = "PASS"

    bypass_candidate = tmp_path / "bypass-candidate.json"
    bypass_candidate.write_text(json.dumps(data), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(IMPL), str(bypass_candidate)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "RESULT: BLOCK" in result.stdout
    assert "repository-pinned criterion inventory" in result.stdout
