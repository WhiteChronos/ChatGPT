from __future__ import annotations

from dataclasses import FrozenInstanceError
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def test_layout_status_contract_and_rect_geometry():
    from pipeline.layout_optimizer.models import LayoutStatus, RectMM

    assert {x.value for x in LayoutStatus} == {
        "LAYOUT_FEASIBLE",
        "LAYOUT_VALIDATED",
        "HOLD_LAYOUT_INPUT",
        "HOLD_LAYOUT_CAPACITY",
        "HOLD_LAYOUT_SOLVER_TIMEOUT",
        "HOLD_LAYOUT_THERMAL",
        "HOLD_LAYOUT_EMC",
        "HOLD_LAYOUT_CABLE_ENTRY",
        "USER_DECISION_REQUIRED",
    }

    rect = RectMM(x=10.0, y=20.0, width=30.0, height=40.0)
    assert rect.right == 40.0
    assert rect.top == 60.0
    assert rect.area_mm2 == 1200.0

    with pytest.raises(FrozenInstanceError):
        rect.x = 99.0


def test_layout_result_serialization_matches_schema():
    from pipeline.layout_optimizer.models import (
        LayoutMetrics,
        LayoutResult,
        LayoutStatus,
    )

    result = LayoutResult(
        panel_id="PN-TEST",
        panel_revision="R01",
        status=LayoutStatus.LAYOUT_FEASIBLE,
        placements=(),
        metrics=LayoutMetrics(
            occupied_area_mm2=0.0,
            free_reserve_percent=100.0,
            minimum_clearance_mm=None,
            overlap_count=0,
            rail_count=0,
            wireway_count=0,
            terminal_count=0,
            gland_count=0,
        ),
        solver_manifest={"engine": "test", "seed": 1},
        diagnostics=(),
        alternatives=(),
    )
    data = result.to_dict()

    schema = json.loads(
        (ROOT / "schemas/layout_optimizer_result_v1.schema.json").read_text(encoding="utf-8")
    )
    errors = list(Draft202012Validator(schema).iter_errors(data))
    assert not errors, [e.message for e in errors]
    assert data["panel_id"] == "PN-TEST"
    assert data["panel_revision"] == "R01"
    assert data["status"] == "LAYOUT_FEASIBLE"
    assert data["placements"] == []
    assert data["alternatives"] == []
