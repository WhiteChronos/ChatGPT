from __future__ import annotations

import json
from pipeline.layout_optimizer.models import (
    LayoutResult, LayoutStatus, RectMM, LayoutMetrics
)

def test_status_contract_and_geometry():
    expected = {
        "LAYOUT_FEASIBLE","LAYOUT_VALIDATED","HOLD_LAYOUT_INPUT",
        "HOLD_LAYOUT_CAPACITY","HOLD_LAYOUT_SOLVER_TIMEOUT",
        "HOLD_LAYOUT_THERMAL","HOLD_LAYOUT_EMC","HOLD_LAYOUT_CABLE_ENTRY",
        "USER_DECISION_REQUIRED",
    }
    assert {x.value for x in LayoutStatus} == expected
    r = RectMM("A","mounting_plate",10,20,30,40)
    assert r.right == 40
    assert r.top == 60
    assert r.area_mm2 == 1200

def test_layout_result_serializes_stably():
    result = LayoutResult(
        panel_id="P1", revision="R1", status=LayoutStatus.LAYOUT_FEASIBLE,
        placements=[], metrics=LayoutMetrics(), solver_manifest={"seed": 1},
        diagnostics=[], alternatives=[]
    )
    data = result.to_dict()
    assert data["panel_id"] == "P1"
    assert data["status"] == "LAYOUT_FEASIBLE"
    assert json.dumps(data, sort_keys=True)
