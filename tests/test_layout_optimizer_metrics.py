from __future__ import annotations

from pipeline.layout_optimizer.models import (
    LayoutMetrics,
    LayoutResult,
    LayoutStatus,
    PanelGeometry,
    Placement,
)


def _panel(width=200, height=200, reserve=20, terminal_bottom=40):
    return PanelGeometry(
        panel_id="PN-METRICS",
        revision="R01",
        enclosure_width_mm=width + 50,
        enclosure_height_mm=height + 50,
        enclosure_depth_mm=250,
        plate_width_mm=width,
        plate_height_mm=height,
        minimum_free_reserve_percent=reserve,
        terminal_zone_bottom_y_mm=terminal_bottom,
    )


def _p(name, x, y, width, height, *, kind="component", surface="mounting_plate", source_tag=None):
    return Placement(
        instance_id=name,
        source_tag=source_tag or name.split("#")[0],
        catalog_id=f"CAT-{name}",
        surface=surface,
        x_mm=x,
        y_mm=y,
        width_mm=width,
        height_mm=height,
        kind=kind,
    )


def test_calculate_metrics_counts_physical_artifacts_and_reserve():
    from pipeline.layout_optimizer.metrics import calculate_metrics

    panel = _panel()
    placements = [
        _p("A#01", 10, 50, 50, 50),
        _p("B#01", 100, 50, 40, 50),
        _p("DIN#01", 0, 48, 150, 7.5, kind="din_rail"),
        _p("WD#01", 0, 40, 200, 10, kind="wireway"),
        _p("XT#01", 10, 120, 10, 40, source_tag="XT-01"),
        _p("CG#01", 10, 0, 20, 20, kind="cable_gland", surface="cable_entry"),
        _p("CG#02", 40, 0, 20, 20, kind="cable_gland", surface="cable_entry"),
    ]

    metrics = calculate_metrics(panel, placements)

    assert metrics.occupied_area_mm2 == 50 * 50 + 40 * 50 + 10 * 40 + 200 * 10
    assert metrics.free_reserve_percent == 67.75
    assert metrics.minimum_clearance_mm == 40
    assert metrics.overlap_count == 0
    assert metrics.rail_count == 1
    assert metrics.wireway_count == 1
    assert metrics.terminal_count == 1
    assert metrics.gland_count == 2
    assert metrics.occupied_envelope_area_mm2 > 0


def test_calculate_metrics_detects_component_overlap():
    from pipeline.layout_optimizer.metrics import calculate_metrics

    metrics = calculate_metrics(
        _panel(),
        [
            _p("A#01", 20, 60, 50, 50),
            _p("B#01", 60, 80, 50, 50),
        ],
    )

    assert metrics.overlap_count == 1
    assert metrics.minimum_clearance_mm == 0


def test_validate_layout_promotes_only_when_reserve_and_geometry_pass():
    from pipeline.layout_optimizer.metrics import calculate_metrics, validate_layout_result

    panel = _panel()
    placements = (
        _p("A#01", 20, 60, 40, 40),
        _p("B#01", 100, 60, 40, 40),
    )
    feasible = LayoutResult(
        panel_id=panel.panel_id,
        panel_revision=panel.revision,
        status=LayoutStatus.LAYOUT_FEASIBLE,
        placements=placements,
        metrics=calculate_metrics(panel, placements),
        solver_manifest={"engine": "test"},
        diagnostics=(),
        alternatives=(),
    )

    validated = validate_layout_result(panel, feasible)

    assert validated.status == LayoutStatus.LAYOUT_VALIDATED
    assert validated.diagnostics == ()


def test_validate_layout_below_reserve_remains_hold():
    from pipeline.layout_optimizer.metrics import calculate_metrics, validate_layout_result

    panel = _panel(width=100, height=100, reserve=30, terminal_bottom=20)
    placements = (_p("BIG#01", 10, 20, 80, 80),)
    feasible = LayoutResult(
        panel_id=panel.panel_id,
        panel_revision=panel.revision,
        status=LayoutStatus.LAYOUT_FEASIBLE,
        placements=placements,
        metrics=calculate_metrics(panel, placements),
        solver_manifest={"engine": "test"},
        diagnostics=(),
        alternatives=(),
    )

    result = validate_layout_result(panel, feasible)

    assert result.status == LayoutStatus.HOLD_LAYOUT_CAPACITY
    assert any(x.startswith("INSUFFICIENT_RESERVE:") for x in result.diagnostics)
