from __future__ import annotations

from pipeline.layout_optimizer.models import (
    LayoutConfig,
    PanelGeometry,
    PhysicalInstance,
    Placement,
)


def _panel(width: float = 300, height: float = 300, reserve: float = 20) -> PanelGeometry:
    return PanelGeometry(
        panel_id="PN-INFRA",
        revision="R01",
        enclosure_width_mm=width + 50,
        enclosure_height_mm=height + 50,
        enclosure_depth_mm=250,
        plate_width_mm=width,
        plate_height_mm=height,
        minimum_free_reserve_percent=reserve,
        cable_exit_height_mm=40,
        lower_wireway_height_mm=40,
        minimum_bend_clearance_mm=20,
        terminal_zone_bottom_y_mm=120,
        cable_glands_count=4,
    )


def _instance(name: str) -> PhysicalInstance:
    return PhysicalInstance(
        instance_id=name,
        source_tag=name.split("#")[0],
        catalog_id="CAT",
        quantity_index=1,
        surface="mounting_plate",
        width_mm=30,
        height_mm=60,
        depth_mm=40,
        rail_required=True,
    )


def _placement(name: str, x: float, y: float, width: float = 30, height: float = 60, kind: str = "component") -> Placement:
    return Placement(
        instance_id=name,
        source_tag=name.split("#")[0],
        catalog_id="CAT",
        surface="mounting_plate",
        x_mm=x,
        y_mm=y,
        width_mm=width,
        height_mm=height,
        kind=kind,
    )


def test_din_rail_length_is_derived_from_real_component_span():
    from pipeline.layout_optimizer.infrastructure import build_din_rails

    placements = [
        _placement("A#01", 50, 150),
        _placement("B#01", 90, 150),
    ]
    instances = {x.instance_id: _instance(x.instance_id) for x in placements}

    rails, diagnostics = build_din_rails(
        _panel(), placements, instances,
        {"kind": "din_rail", "source_tag": "DIN-01..02", "catalog_id": "DIN", "quantity": 2, "unit": "un"},
        LayoutConfig(rail_edge_allowance_mm=10),
    )

    assert diagnostics == []
    assert len(rails) == 1
    assert rails[0].kind == "din_rail"
    assert rails[0].x_mm == 40
    assert rails[0].width_mm == 90
    assert rails[0].metadata["member_instance_ids"] == ["A#01", "B#01"]


def test_lower_zones_are_distinct_and_ordered():
    from pipeline.layout_optimizer.infrastructure import build_lower_zones
    from pipeline.layout_optimizer.geometry import overlaps

    zones = build_lower_zones(_panel())

    assert zones["cable_exit"].y == 0
    assert zones["cable_exit"].height == 40
    assert zones["bend_clearance"].y == 40
    assert zones["bend_clearance"].height == 20
    assert zones["lower_wireway"].y == 60
    assert zones["lower_wireway"].height == 40
    assert zones["terminal_access"].y == 100
    assert zones["terminal_access"].height == 20
    assert not overlaps(zones["cable_exit"], zones["bend_clearance"])
    assert not overlaps(zones["bend_clearance"], zones["lower_wireway"])
    assert not overlaps(zones["lower_wireway"], zones["terminal_access"])


def test_cable_gland_overcrowding_returns_hold_diagnostic():
    from pipeline.layout_optimizer.infrastructure import build_cable_glands

    panel = _panel(width=100)
    request = {
        "kind": "cable_gland",
        "source_tag": "CG-01..10",
        "catalog_id": "GLAND",
        "quantity": 10,
        "unit": "un",
        "dimensions_mm": {"width": 20, "height": 20},
    }

    glands, diagnostics = build_cable_glands(
        panel, request, LayoutConfig(infrastructure_gap_mm=5)
    )

    assert glands == []
    assert diagnostics == ["CABLE_GLAND_OVERCROWDING:CG-01..10"]


def test_low_reserve_layout_is_not_ready_for_render():
    from pipeline.layout_optimizer.infrastructure import validate_infrastructure_requirements

    panel = _panel(width=100, height=100, reserve=20)
    components = [
        _placement("BIG#01", 0, 20, width=95, height=80),
    ]

    diagnostics = validate_infrastructure_requirements(
        panel, components, infrastructure_placements=(), diagnostics=()
    )

    assert any(x.startswith("INSUFFICIENT_RESERVE:") for x in diagnostics)
