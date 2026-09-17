import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_li_material_contract_is_wired() -> None:
    pipeline = _yaml("pipeline/pipeline.yaml")
    datacenter = _yaml("datacenter/datacenter.yaml")
    datasheet = _yaml("datasheet/datasheet.yaml")
    golden = _yaml("governance/golden_rules.yaml")
    pipesheets = _yaml("pipesheets/LI_MATERIAL_PIPE_SHEETS.yaml")
    control = _json("datacenter/LI_MATERIAL_CONTROL.json")
    li_ds = _json("datasheet/LI_MATERIAL_DATA_SHEET.json")
    memory = _yaml("memory/LI_MATERIAL_CONTROL_MEMORY.yaml")
    tools = _json("plugins/li_material_qa_registry.json")

    contracts = pipeline["contracts"]
    assert contracts["li_material_prompt"] == "prompts/PROMPT_MASTER_LI_MATERIAL.md"
    assert contracts["li_material_pipesheets"] == "pipesheets/LI_MATERIAL_PIPE_SHEETS.yaml"
    assert contracts["li_material_script"] == "pipeline/li_material_control.py"
    assert contracts["li_material_memory"] == "memory/LI_MATERIAL_CONTROL_MEMORY.yaml"

    assert datacenter["li_material_revision_standard"]["preserve_rev_0"] is True
    assert datacenter["li_material_revision_standard"]["overwrite_historical_revision_forbidden"] is True
    assert datasheet["li_material_revision_contract"]["new_revision_adjacent_right"] is True
    assert control["revision_contract"]["preserve_all_previous_revision_columns"] is True
    assert li_ds["revision_behavior"]["previous_revision_values_must_not_be_corrected_in_place"] is True
    assert pipesheets["revision_model"]["historical_columns_immutable"] is True
    assert memory["immutable_rules"]["previous_revision_columns_immutable"] is True

    rules = {item["id"] for item in golden["required_rules"]}
    for rule_id in ("GR-050", "GR-051", "GR-052", "GR-053", "GR-054", "GR-055", "GR-056", "GR-057", "GR-058"):
        assert rule_id in rules

    repos = {item["repository"] for item in tools["tools"]}
    assert "chenweixin123/workbooklens" in repos
    assert "Atomics-hub/sheetparity" in repos
    assert "LibreOffice/core" in repos
