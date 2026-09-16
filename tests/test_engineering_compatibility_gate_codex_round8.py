from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from pipeline.engineering_compatibility_gate import (
    _valid_traceable_location,
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


def test_waiver_subject_hash_binds_complete_baseline_provenance() -> None:
    data = example()
    finding = {
        "id": "F-ROUND8-HASH",
        "assessment_id": data["assessment_records"][0]["id"],
        "waiver": {
            "reason": "Synthetic risk acceptance.",
            "approval_record_id": "APR-ROUND8-HASH",
        },
    }
    assessment = data["assessment_records"][0]
    original = _waiver_subject_hash(data["project"], finding, data["baseline"], assessment)

    changed_source = deepcopy(data["baseline"])
    changed_source["documents"][0]["source"] = "synthetic://changed-source"
    assert _waiver_subject_hash(data["project"], finding, changed_source, assessment) != original

    changed_reconciliation = deepcopy(data["baseline"])
    changed_reconciliation["reconciliation_note"] = "Different reconciliation basis."
    assert _waiver_subject_hash(data["project"], finding, changed_reconciliation, assessment) != original


def test_criterion_id_is_schema_required_and_homoglyph_clone_is_rejected() -> None:
    data = example()
    data["assessment_records"][0].pop("criterion_id")
    errors = validate_data(data, load_json(SCHEMA), config())
    assert any("'criterion_id' is a required property" in error for error in errors)

    data = example()
    clone = deepcopy(data["assessment_records"][0])
    clone["id"] = "ASM-HVAC-HOMOGLYPH-001"
    clone["criterion_id"] = "CRIT-HVAC-HOMOGLYPH"
    clone["criterion"] = "\u041dVAC baseline compatibility"  # Cyrillic En looks like Latin H.
    data["assessment_records"].append(clone)
    data["scope_summary"]["VERIFIED"] = 5
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any("spoof-normalized criterion/scope" in error for error in errors)


def test_unicode_compatibility_normalization_rejects_fullwidth_discipline_alias() -> None:
    data = example()
    data["baseline"]["disciplines"].append("ＨＶＡＣ")
    data["release_gate"] = "BLOCK"

    errors = validate_semantics(data, config())
    assert any(
        "duplicate identifiers after Unicode compatibility/whitespace/case normalization" in error
        for error in errors
    )


def test_locator_roman_numerals_must_be_canonical() -> None:
    assert _valid_traceable_location("Page IV")
    assert _valid_traceable_location("Section MCMXCIV")
    assert not _valid_traceable_location("Page civil")
    assert not _valid_traceable_location("Section IIV")

    data = example()
    data["assessment_records"][0]["evidence"][0]["location"] = "Page civil"
    data["release_gate"] = "BLOCK"
    errors = validate_semantics(data, config())
    assert any("with a locator value" in error for error in errors)
