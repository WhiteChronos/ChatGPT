from __future__ import annotations

from pipeline.layout_optimizer.models import (
    ClearanceMM,
    PanelGeometry,
    PhysicalInstance,
    Placement,
    RectMM,
)


def _panel() -> PanelGeometry:
    return PanelGeometry(
        panel_id="PN-TEST",
        revision="R01",
        enclosure_width_mm=600,
        enclosure_height_mm=800,
        enclosure_depth_mm=300,
        plate_width_mm=550,
        plate_height_mm=750,
        minimum_free_reserve_percent=20,
        terminal_zone_bottom_y_mm=120,
    )


def _instance(instance_id: str, surface: str = "mounting_plate") -> PhysicalInstance:
    return PhysicalInstance(
        instance_id=instance_id,
        source_tag=instance_id.split("#")[0],
        catalog_id="TEST",
        quantity_index=1,
        surface=surface,
        width_mm=50,
        height_mm=40,
        depth_mm=20,
        clearance=ClearanceMM(left=5, right=5, top=10, bottom=10),
    )


def _placement(instance_id: str, x: float, y: float, surface: str = "mounting_plate") -> Placement:
    return Placement(
        instance_id=instance_id,
        source_tag=instance_id.split("#")[0],
        catalog_id="TEST",
        surface=surface,
        x_mm=x,
        y_mm=y,
        width_mm=50,
        height_mm=40,
    )


def test_expanded_rect_and_exact_touch_do_not_overlap():
    from pipeline.layout_optimizer.geometry import expanded_rect, overlaps

    a = expanded_rect(RectMM(10, 20, 30, 40), ClearanceMM(left=2, right=3, top=5, bottom=7))
    assert a == RectMM(8, 13, 35, 52)

    assert overlaps(RectMM(0, 0, 10, 10), RectMM(9.99, 0, 10, 10))
    assert not overlaps(RectMM(0, 0, 10, 10), RectMM(10, 0, 10, 10))


def test_inside_accepts_boundary_and_rejects_escape():
    from pipeline.layout_optimizer.geometry import inside

    boundary = RectMM(0, 0, 100, 80)
    assert inside(RectMM(0, 0, 100, 80), boundary)
    assert inside(RectMM(10, 10, 20, 20), boundary)
    assert not inside(RectMM(-0.1, 0, 10, 10), boundary)
    assert not inside(RectMM(90, 70, 11, 10), boundary)


def test_validate_hard_geometry_uses_clearance_and_surface_boundaries():
    from pipeline.layout_optimizer.geometry import validate_hard_geometry

    instances = {
        "A#01": _instance("A#01"),
        "B#01": _instance("B#01"),
        "HMI#01": _instance("HMI#01", "door"),
    }
    placements = [
        _placement("A#01", 20, 150),
        _placement("B#01", 70, 150),
        _placement("HMI#01", 560, 700, "door"),
    ]

    errors = validate_hard_geometry(_panel(), placements, instances)
    assert "COLLISION:A#01:B#01" in errors
    assert "OUT_OF_BOUNDS:HMI#01:door" in errors


def test_validate_hard_geometry_rejects_reserved_lower_zone():
    from pipeline.layout_optimizer.geometry import validate_hard_geometry

    instances = {"A#01": _instance("A#01")}
    placements = [_placement("A#01", 20, 100)]
    reserved = [RectMM(0, 0, 550, 120)]

    errors = validate_hard_geometry(_panel(), placements, instances, reserved_zones=reserved)
    assert "RESERVED_ZONE:A#01" in errors
