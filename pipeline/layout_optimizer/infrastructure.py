from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from .geometry import overlaps
from .models import LayoutConfig, PanelGeometry, PhysicalInstance, Placement, RectMM


def build_lower_zones(panel: PanelGeometry) -> dict[str, RectMM]:
    y = 0.0
    cable_exit = RectMM(0.0, y, panel.plate_width_mm, panel.cable_exit_height_mm)
    y += panel.cable_exit_height_mm
    bend = RectMM(0.0, y, panel.plate_width_mm, panel.minimum_bend_clearance_mm)
    y += panel.minimum_bend_clearance_mm
    wireway = RectMM(0.0, y, panel.plate_width_mm, panel.lower_wireway_height_mm)
    y += panel.lower_wireway_height_mm
    terminal_height = max(0.0, panel.terminal_zone_bottom_y_mm - y)
    terminal_access = RectMM(0.0, y, panel.plate_width_mm, terminal_height)
    return {
        "cable_exit": cable_exit,
        "bend_clearance": bend,
        "lower_wireway": wireway,
        "terminal_access": terminal_access,
    }


def _vertical_overlap(a: Placement, b: Placement) -> bool:
    return not (
        a.y_mm + a.height_mm <= b.y_mm
        or b.y_mm + b.height_mm <= a.y_mm
    )


def build_din_rails(
    panel: PanelGeometry,
    component_placements: Sequence[Placement],
    instances: Mapping[str, PhysicalInstance],
    request: Mapping[str, Any],
    config: LayoutConfig,
) -> tuple[list[Placement], list[str]]:
    eligible = [
        p
        for p in component_placements
        if p.surface == "mounting_plate"
        and instances.get(p.instance_id) is not None
        and instances[p.instance_id].rail_required
    ]
    eligible.sort(key=lambda p: (p.y_mm, p.x_mm, p.instance_id))
    groups: list[list[Placement]] = []
    for placement in eligible:
        for group in groups:
            if any(_vertical_overlap(placement, member) for member in group):
                group.append(placement)
                break
        else:
            groups.append([placement])

    requested = int(request.get("quantity", 0) or 0)
    diagnostics: list[str] = []
    if len(groups) > requested:
        diagnostics.append(
            f"DIN_RAIL_CAPACITY_REQUEST:{request.get('source_tag')}:"
            f"needed={len(groups)}:available={requested}"
        )

    rails: list[Placement] = []
    edge = float(config.rail_edge_allowance_mm)
    rail_height = float(((request.get("dimensions_mm") or {}).get("height", 7.5)) or 7.5)
    for index, group in enumerate(groups, start=1):
        min_x = min(p.x_mm for p in group)
        max_x = max(p.x_mm + p.width_mm for p in group)
        x = max(0.0, min_x - edge)
        right = min(panel.plate_width_mm, max_x + edge)
        y = min(p.y_mm for p in group)
        rails.append(
            Placement(
                instance_id=f"{request.get('source_tag')}#RAIL{index:02d}",
                source_tag=str(request.get("source_tag") or ""),
                catalog_id=str(request.get("catalog_id") or ""),
                surface="mounting_plate",
                x_mm=x,
                y_mm=y,
                width_mm=max(0.0, right - x),
                height_mm=rail_height,
                rotation_deg=0,
                kind="din_rail",
                quantity_index=index,
                metadata={
                    "member_instance_ids": [p.instance_id for p in sorted(group, key=lambda p: p.instance_id)],
                    "derived": True,
                },
            )
        )
    return rails, diagnostics


def build_wireways(
    panel: PanelGeometry,
    request: Mapping[str, Any],
    config: LayoutConfig,
) -> tuple[list[Placement], list[str]]:
    quantity = int(request.get("quantity", 0) or 0)
    if quantity < 1:
        return [], [f"INVALID_INFRA_QUANTITY:{request.get('source_tag')}"]

    dims = request.get("dimensions_mm") or {}
    nominal_width = float(dims.get("width", 40) or 40)
    lower_height = float(
        dims.get("height", panel.lower_wireway_height_mm)
        or panel.lower_wireway_height_mm
        or 40
    )
    zones = build_lower_zones(panel)
    lower = zones["lower_wireway"]
    placements = [
        Placement(
            instance_id=f"{request.get('source_tag')}#WD01",
            source_tag=str(request.get("source_tag") or ""),
            catalog_id=str(request.get("catalog_id") or ""),
            surface="mounting_plate",
            x_mm=0.0,
            y_mm=lower.y,
            width_mm=panel.plate_width_mm,
            height_mm=lower_height,
            kind="wireway",
            quantity_index=1,
            metadata={"role": "lower_wireway", "derived": True},
        )
    ]

    usable_y = panel.terminal_zone_bottom_y_mm
    usable_height = max(0.0, panel.plate_height_mm - usable_y)
    gap = float(config.infrastructure_gap_mm)
    for index in range(2, quantity + 1):
        if usable_height <= 0:
            return placements, [f"WIREWAY_NO_USABLE_HEIGHT:{request.get('source_tag')}"]
        side = "left" if index % 2 == 0 else "right"
        x = gap if side == "left" else max(0.0, panel.plate_width_mm - nominal_width - gap)
        placements.append(
            Placement(
                instance_id=f"{request.get('source_tag')}#WD{index:02d}",
                source_tag=str(request.get("source_tag") or ""),
                catalog_id=str(request.get("catalog_id") or ""),
                surface="mounting_plate",
                x_mm=x,
                y_mm=usable_y,
                width_mm=nominal_width,
                height_mm=usable_height,
                kind="wireway",
                quantity_index=index,
                metadata={"role": f"vertical_{side}", "derived": True},
            )
        )
    return placements, []


def build_terminal_strips(
    panel: PanelGeometry,
    component_placements: Sequence[Placement],
    instances: Mapping[str, PhysicalInstance],
    config: LayoutConfig,
) -> tuple[list[Placement], list[str]]:
    del panel, config
    grouped: dict[str, list[Placement]] = defaultdict(list)
    for placement in component_placements:
        instance = instances.get(placement.instance_id)
        category = str((instance.metadata if instance else {}).get("category") or "")
        if (
            category in {"terminal", "terminal_block", "pe_terminal"}
            or placement.source_tag.startswith(("XT-", "XPE-"))
        ):
            grouped[placement.source_tag].append(placement)

    strips: list[Placement] = []
    for index, (source_tag, members) in enumerate(sorted(grouped.items()), start=1):
        x = min(p.x_mm for p in members)
        y = min(p.y_mm for p in members)
        right = max(p.x_mm + p.width_mm for p in members)
        top = max(p.y_mm + p.height_mm for p in members)
        strips.append(
            Placement(
                instance_id=f"{source_tag}#STRIP",
                source_tag=source_tag,
                catalog_id="DERIVED-TERMINAL-STRIP",
                surface="mounting_plate",
                x_mm=x,
                y_mm=y,
                width_mm=right - x,
                height_mm=top - y,
                kind="terminal_strip",
                quantity_index=index,
                metadata={
                    "member_instance_ids": [p.instance_id for p in sorted(members, key=lambda p: p.instance_id)],
                    "derived": True,
                },
            )
        )
    return strips, []


def build_cable_glands(
    panel: PanelGeometry,
    request: Mapping[str, Any],
    config: LayoutConfig,
) -> tuple[list[Placement], list[str]]:
    quantity = int(request.get("quantity", 0) or 0)
    if quantity < 1:
        return [], [f"INVALID_INFRA_QUANTITY:{request.get('source_tag')}"]

    dims = request.get("dimensions_mm")
    if not isinstance(dims, Mapping):
        return [], [f"MISSING_INFRA_DIMENSIONS:{request.get('source_tag')}"]
    width = dims.get("width")
    height = dims.get("height")
    if not isinstance(width, (int, float)) or width <= 0 or not isinstance(height, (int, float)) or height <= 0:
        return [], [f"MISSING_INFRA_DIMENSIONS:{request.get('source_tag')}"]

    gap = float(config.infrastructure_gap_mm)
    required = quantity * float(width) + max(0, quantity - 1) * gap
    if required > panel.enclosure_width_mm:
        return [], [f"CABLE_GLAND_OVERCROWDING:{request.get('source_tag')}"]

    start_x = (panel.enclosure_width_mm - required) / 2.0
    glands: list[Placement] = []
    for index in range(quantity):
        glands.append(
            Placement(
                instance_id=f"{request.get('source_tag')}#CG{index + 1:02d}",
                source_tag=str(request.get("source_tag") or ""),
                catalog_id=str(request.get("catalog_id") or ""),
                surface="cable_entry",
                x_mm=start_x + index * (float(width) + gap),
                y_mm=0.0,
                width_mm=float(width),
                height_mm=float(height),
                kind="cable_gland",
                quantity_index=index + 1,
                metadata={"derived": True},
            )
        )
    return glands, []


def validate_infrastructure_requirements(
    panel: PanelGeometry,
    component_placements: Sequence[Placement],
    infrastructure_placements: Sequence[Placement],
    diagnostics: Sequence[str],
) -> list[str]:
    errors = list(diagnostics)
    lower_required = (
        panel.cable_exit_height_mm
        + panel.minimum_bend_clearance_mm
        + panel.lower_wireway_height_mm
    )
    if panel.terminal_zone_bottom_y_mm < lower_required:
        errors.append(
            f"LOWER_ZONE_CONTRACT_INVALID:required={lower_required}:"
            f"terminal_bottom={panel.terminal_zone_bottom_y_mm}"
        )

    lower_zone = RectMM(
        0.0,
        0.0,
        panel.plate_width_mm,
        min(panel.plate_height_mm, panel.terminal_zone_bottom_y_mm),
    )
    for placement in component_placements:
        if placement.surface != "mounting_plate":
            continue
        is_terminal = (
            placement.kind in {"terminal", "terminal_block", "terminal_strip"}
            or placement.source_tag.startswith(("XT-", "XPE-"))
        )
        if not is_terminal and overlaps(placement.rect, lower_zone):
            errors.append(f"LOWER_ZONE_COMPONENT:{placement.instance_id}")

    plate_area = panel.plate_width_mm * panel.plate_height_mm
    fixed_lower_area = lower_zone.area_mm2
    component_area = sum(
        p.width_mm * p.height_mm
        for p in component_placements
        if p.surface == "mounting_plate"
    )
    outside_lower_infra_area = sum(
        p.width_mm * p.height_mm
        for p in infrastructure_placements
        if p.surface == "mounting_plate" and p.y_mm >= lower_zone.top
    )
    free_area = max(
        0.0,
        plate_area - fixed_lower_area - component_area - outside_lower_infra_area,
    )
    reserve = 100.0 if plate_area <= 0 else 100.0 * free_area / plate_area
    if reserve + 1e-9 < panel.minimum_free_reserve_percent:
        errors.append(
            f"INSUFFICIENT_RESERVE:{reserve:.3f}<"
            f"{panel.minimum_free_reserve_percent:.3f}"
        )
    return errors
