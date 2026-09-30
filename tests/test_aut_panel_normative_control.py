from pathlib import Path
import json
import yaml

ROOT=Path(__file__).resolve().parents[1]

def test_resolver_activates_baseline_and_condition_groups():
    from pipeline.aut_panel_normative_control import resolve_applicable_norms
    registry=yaml.safe_load((ROOT/"datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    memory=yaml.safe_load((ROOT/"memory/AUT_PANEL_NORMATIVE_MEMORY.yaml").read_text(encoding="utf-8"))
    profile={
        "baseline_group":"panel_general",
        "detected_conditions":["industrial_network","dc_ups_present","spd_present"],
        "conditional_group_review_required":True,
        "applicability_status":"HOLD_UNTIL_NORMATIVE_REVIEW",
    }
    result=resolve_applicable_norms("PN-AUT-01","R02",profile,registry,memory)
    ids={x["id"] for x in result["references"]}
    assert "NORM-001" in ids
    assert "NORM-031" in ids
    assert "NORM-029" in ids
    assert "NORM-018" in ids
    assert result["status"]=="HOLD"
    assert result["hold_reasons"]

def test_resolver_does_not_activate_untriggered_machine_safety_group():
    from pipeline.aut_panel_normative_control import resolve_applicable_norms
    registry=yaml.safe_load((ROOT/"datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    memory=yaml.safe_load((ROOT/"memory/AUT_PANEL_NORMATIVE_MEMORY.yaml").read_text(encoding="utf-8"))
    profile={
        "baseline_group":"panel_general",
        "detected_conditions":["industrial_network"],
        "conditional_group_review_required":True,
        "applicability_status":"HOLD_UNTIL_NORMATIVE_REVIEW",
    }
    result=resolve_applicable_norms("PN-X","R00",profile,registry,memory)
    ids={x["id"] for x in result["references"]}
    assert "NORM-003" not in ids
    assert "NORM-036" not in ids

def test_standard_pipeline_writes_normative_applicability_manifest(tmp_path):
    from pipeline.aut_panel_normative_control import write_normative_manifest
    registry=yaml.safe_load((ROOT/"datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    memory=yaml.safe_load((ROOT/"memory/AUT_PANEL_NORMATIVE_MEMORY.yaml").read_text(encoding="utf-8"))
    project=json.loads((ROOT/"datasheet/AUT_PANEL_DATA_SHEET.json").read_text(encoding="utf-8"))
    out=tmp_path/"AUT_PANEL_NORMATIVE_APPLICABILITY.json"
    result=write_normative_manifest(project,registry,memory,out)
    assert out.exists()
    data=json.loads(out.read_text(encoding="utf-8"))
    assert data["panel_id"]=="PN-AUT-01"
    assert data["registry_id"]=="AUT-PANEL-NORMATIVE-REFERENCES-V1"
    assert data["status"] in {"HOLD","VALIDATED"}
    assert result==data


def test_standard_pipeline_normative_gate_returns_hold_and_artifact(tmp_path):
    from pipeline import aut_panel_standard as std
    registry=yaml.safe_load((ROOT/"datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml").read_text(encoding="utf-8"))
    memory=yaml.safe_load((ROOT/"memory/AUT_PANEL_NORMATIVE_MEMORY.yaml").read_text(encoding="utf-8"))
    project=json.loads((ROOT/"datasheet/AUT_PANEL_DATA_SHEET.json").read_text(encoding="utf-8"))
    result,path=std.avaliar_normas(project,registry,memory,tmp_path)
    assert path.name=="AUT_PANEL_NORMATIVE_APPLICABILITY.json"
    assert path.exists()
    assert result.resultado=="HOLD"
    assert result.severidade=="HOLD"
