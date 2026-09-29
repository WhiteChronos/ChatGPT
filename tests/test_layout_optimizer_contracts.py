from __future__ import annotations
from pathlib import Path
import json, yaml

ROOT=Path(__file__).resolve().parents[1]

def test_layout_stage_registers_optimizer_without_reordering():
    pipe=yaml.safe_load((ROOT/"pipeline/pipeline.yaml").read_text(encoding="utf-8"))
    ids=[x["id"] for x in pipe["sequence"]]
    assert ids==["BOOTSTRAP_CONTEXT","DATACENTER","DATASHEET","SELECT","LI_QUANTITY","LOAD_BALANCE","BOM","LAYOUT","RENDER_IMAGE","QA","MEMORY_SYNC","RELEASE"]
    layout=next(x for x in pipe["sequence"] if x["id"]=="LAYOUT")
    opt=layout["optimizer"]
    assert opt["id"]=="LAYOUT-OPTIMIZER-V1"
    assert opt["implementation"]=="pipeline/layout_optimizer/cli.py"
    assert opt["result_schema"]=="schemas/layout_optimizer_result_v1.schema.json"
    assert opt["locked_enclosure_auto_change"] is False
    assert opt["split_auto_select"] is False

def test_agent_registry_points_layout_optimizer_to_contract():
    agents=yaml.safe_load((ROOT/"agents/AUT_PANEL_AGENT_SYSTEM.yaml").read_text(encoding="utf-8"))
    agent=next(x for x in agents["agents"] if x["id"]=="LAYOUT_OPTIMIZER")
    assert agent["implementation"]=="pipeline/layout_optimizer/cli.py"
    assert agent["config"]=="configs/layout_optimizer_v1.yaml"
    assert agent["result_schema"]=="schemas/layout_optimizer_result_v1.schema.json"
    assert agent["decision_policy"]=="AUTO_CANDIDATE_REVISION_FOR_ENCLOSURE_OR_SPLIT"
    coordinator=next(x for x in agents["agents"] if x["id"]=="AUTO_ENGINEERING_COORDINATOR")
    assert coordinator["release_authority"] is False
    assert coordinator["policy"]=="configs/auto_engineering_v1.yaml"

def test_json_pipeline_registers_optimizer_metadata():
    pipe=json.loads((ROOT/"pipeline/AUT_PANEL_PIPELINE.json").read_text(encoding="utf-8"))
    opt=pipe["layout_optimizer"]
    assert opt["id"]=="LAYOUT-OPTIMIZER-V1"
    assert opt["stage"]=="LAYOUT"
    assert opt["canonical_sequence_unchanged"] is True
