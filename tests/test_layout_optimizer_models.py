from __future__ import annotations
import json
from pipeline.layout_optimizer.models import LayoutMetrics, LayoutResult, LayoutStatus, RectMM

def test_status_contract_and_geometry():
    expected={"LAYOUT_FEASIBLE","LAYOUT_VALIDATED","HOLD_LAYOUT_INPUT","HOLD_LAYOUT_CAPACITY","HOLD_LAYOUT_SOLVER_TIMEOUT","HOLD_LAYOUT_THERMAL","HOLD_LAYOUT_EMC","HOLD_LAYOUT_CABLE_ENTRY","USER_DECISION_REQUIRED"}
    assert {x.value for x in LayoutStatus}==expected
    r=RectMM(10,20,30,40)
    assert r.right==40 and r.top==60 and r.area_mm2==1200

def test_layout_result_serializes_stably():
    m=LayoutMetrics(0,100,None,0,0,0,0,0)
    result=LayoutResult("P1","R1",LayoutStatus.LAYOUT_FEASIBLE,(),m,{"seed":1},(),())
    data=result.to_dict()
    assert data["panel_id"]=="P1" and data["status"]=="LAYOUT_FEASIBLE"
    assert json.dumps(data,sort_keys=True)
