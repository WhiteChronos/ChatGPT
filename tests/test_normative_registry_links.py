from pathlib import Path

import yaml

from pipeline.aut_panel_normative_control import merge_normative_registries

ROOT = Path(__file__).resolve().parents[1]


def test_normative_supplement_is_linked_in_datacenter_pipeline_datasheet_and_memory():
    dc = yaml.safe_load((ROOT / "datacenter/datacenter.yaml").read_text(encoding="utf-8"))
    pipe = yaml.safe_load((ROOT / "pipeline/pipeline.yaml").read_text(encoding="utf-8"))
    ds = yaml.safe_load((ROOT / "datasheet/datasheet.yaml").read_text(encoding="utf-8"))
    mem = yaml.safe_load((ROOT / "memory/AUT_PANEL_NORMATIVE_MEMORY.yaml").read_text(encoding="utf-8"))

    expected = "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml"
    assert dc["canonical_sources"]["normative_supplement"] == expected
    assert dc["normative_control"]["supplemental_registry_path"] == expected
    assert pipe["contracts"]["normative_supplement"] == expected
    assert ds["production_contract"]["normative_supplement"] == expected
    assert mem["supplemental_registry_path"] == expected


def test_normative_supplement_merges_without_replacing_primary_registry():
    primary = yaml.safe_load((ROOT / "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    supplement = yaml.safe_load((ROOT / "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml").read_text(encoding="utf-8"))
    merged = merge_normative_registries(primary, supplement)

    primary_ids = {x["id"] for x in primary["standards"]}
    merged_ids = {x["id"] for x in merged["standards"]}
    supplement_ids = {x["id"] for x in supplement["references"]}

    assert primary_ids <= merged_ids
    assert supplement_ids <= merged_ids
    assert merged["supplemental_registry_id"] == "AUT-PANEL-NORMATIVE-SUPPLEMENT-2026-V1"
    assert "NORM-S077" in merged["application_matrix"]["plc_software"]["activate"]


def test_registry_does_not_claim_universal_exhaustiveness():
    primary = yaml.safe_load((ROOT / "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    supplement = yaml.safe_load((ROOT / "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml").read_text(encoding="utf-8"))

    assert primary["coverage_policy"]["universal_exhaustiveness_claimed"] is False
    assert supplement["coverage_policy"]["universal_exhaustiveness_claimed"] is False
