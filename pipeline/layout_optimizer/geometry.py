from __future__ import annotations

from collections.abc import Mapping, Sequence

from .models import ClearanceMM, PanelGeometry, PhysicalInstance, Placement, RectMM


def expanded_rect(rect: RectMM, clearance: ClearanceMM) -> RectMM:
    return RectMM(
        x=rect.x - clearance.left,
        y=rect.y - clearance.bottom,
        width=rect.width + clearance.left + clearance.right,
        height=rect.height + clearance.bottom + clearance.top,
    )


def overlaps(a: RectMM, b: RectMM) -> bool:
    return not (
        a.right <= b.x
        or b.right <= a.x
        or a.top <= b.y
        or b.top <= a.y
    )


def inside(rect: RectMM, boundary: RectMM) -> bool:
    return (
        rect.x >= boundary.x
        and rect.y >= boundary.y
        and rect.right <= boundary.right
        and rect.top <= boundary.top
    )


def _surface_boundary(panel: PanelGeometry, surface: str) -> RectMM | None:
    if surface == "mounting_plate":
        return panel.plate_rect
    if surface == "door":
        return panel.door_rect
    return None


def validate_hard_geometry(
    panel: PanelGeometry,
    placements: Sequence[Placement],
    instances: Mapping[str, PhysicalInstance],
    *,
    reserved_zones: Sequence[RectMM] = (),
) -> list[str]:
    errors: list[str] = []
    expanded_by_id: dict[str, RectMM] = {}

    for placement in placements:
        instance = instances.get(placement.instance_id)
        if instance is None:
            errors.append(f"MISSING_INSTANCE:{placement.instance_id}")
            continue
        if placement.surface != instance.surface:
            errors.append(
                f"SURFACE_MISMATCH:{placement.instance_id}:{placement.surface}:{instance.surface}"
            )

        boundary = _surface_boundary(panel, placement.surface)
        if boundary is None:
            errors.append(f"INVALID_SURFACE:{placement.instance_id}:{placement.surface}")
            continue

        effective = expanded_rect(placement.rect, instance.clearance)
        expanded_by_id[placement.instance_id] = effective
        if not inside(effective, boundary):
            errors.append(f"OUT_OF_BOUNDS:{placement.instance_id}:{placement.surface}")

        if placement.surface == "mounting_plate":
            for zone in reserved_zones:
                if overlaps(effective, zone):
                    errors.append(f"RESERVED_ZONE:{placement.instance_id}")
                    break

    for index, first in enumerate(placements):
        a = expanded_by_id.get(first.instance_id)
        if a is None:
            continue
        for second in placements[index + 1 :]:
            if first.surface != second.surface:
                continue
            b = expanded_by_id.get(second.instance_id)
            if b is None:
                continue
            if overlaps(a, b):
                errors.append(f"COLLISION:{first.instance_id}:{second.instance_id}")

    return errors
