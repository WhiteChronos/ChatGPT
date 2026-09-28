from __future__ import annotations

from pipeline.layout_optimizer.geometry import validate_hard_geometry
from pipeline.layout_optimizer.models import (
    ClearanceMM,
    LayoutConfig,
    LayoutStatus,
    PanelGeometry,
    PhysicalInstance,
    RectMM,
)


def _panel(width: float = 300, height: float = 220) -> PanelGeometry:
    return PanelGeometry(
        panel_id="PN-SOLVER",
        revision="R01",
        enclosure_width_mm=width + 50,
        enclosure_height_mm=height + 50,
        enclosure_depth_mm=250,
        plate_width_mm=width,
        plate_height_mm=height,
        minimum_free_reserve_percent=10,
        terminal_zone_bottom_y_mm=40,
    )


def _instance(name: str, width: float, height: float, *, connections=()) -> PhysicalInstance:
    return PhysicalInstance(
        instance_id=name,
        source_tag=name.split("#")[0],
        catalog_id=f"CAT-{name}",
        quantity_index=1,
        surface="mounting_plate",
        width_mm=width,
        height_mm=height,
        depth_mm=60,
        clearance=ClearanceMM(left=5, right=5, top=5, bottom=5),
        allowed_orientations=(0, 90),
        functional_group="control",
        rail_required=True,
        connections=tuple(connections),
    )


def test_single_panel_solver_places_each_instance_once_without_overlap():
    from pipeline.layout_optimizer.solver import solve_single_panel

    panel = _panel()
    instances = [
        _instance("PLC#01", 70, 90, connections=("IO#01",)),
        _instance("IO#01", 50, 90, connections=("PLC#01",)),
        _instance("PS#01", 60, 70),
    ]
    reserved = [RectMM(0, 0, panel.plate_width_mm, 40)]

    result = solve_single_panel(
        panel,
        instances,
        reserved,
        LayoutConfig(solver_seed=7, max_time_seconds=5, coordinate_resolution_mm=1),
    )

    assert result.status == LayoutStatus.LAYOUT_FEASIBLE
    assert sorted(x.instance_id for x in result.placements) == sorted(x.instance_id for x in instances)
    mapping = {x.instance_id: x for x in instances}
    assert validate_hard_geometry(panel, result.placements, mapping, reserved_zones=reserved) == []
    assert result.solver_manifest["engine"] == "OR_TOOLS_CP_SAT"
    assert result.solver_manifest["seed"] == 7
    assert result.solver_manifest["coordinate_resolution_mm"] == 1


def test_same_seed_and_inputs_produce_same_placements():
    from pipeline.layout_optimizer.solver import solve_single_panel

    panel = _panel()
    instances = [
        _instance("A#01", 80, 60),
        _instance("B#01", 80, 60),
        _instance("C#01", 60, 80),
    ]
    config = LayoutConfig(solver_seed=11, max_time_seconds=5, coordinate_resolution_mm=1)

    first = solve_single_panel(panel, instances, (), config)
    second = solve_single_panel(panel, instances, (), config)

    assert first.status == LayoutStatus.LAYOUT_FEASIBLE
    assert second.status == LayoutStatus.LAYOUT_FEASIBLE
    assert [
        (x.instance_id, x.x_mm, x.y_mm, x.rotation_deg)
        for x in first.placements
    ] == [
        (x.instance_id, x.x_mm, x.y_mm, x.rotation_deg)
        for x in second.placements
    ]


def test_zero_time_limit_is_timeout_not_capacity_failure():
    from pipeline.layout_optimizer.solver import solve_single_panel

    result = solve_single_panel(
        _panel(),
        [_instance("A#01", 80, 60)],
        (),
        LayoutConfig(solver_seed=1, max_time_seconds=0, coordinate_resolution_mm=1),
    )

    assert result.status == LayoutStatus.HOLD_LAYOUT_SOLVER_TIMEOUT
    assert result.status != LayoutStatus.HOLD_LAYOUT_CAPACITY
    assert "SOLVER_TIMEOUT_OR_UNKNOWN" in result.diagnostics
