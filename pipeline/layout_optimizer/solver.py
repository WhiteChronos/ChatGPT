from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import ortools
from ortools.sat.python import cp_model

from .models import (
    LayoutConfig,
    LayoutMetrics,
    LayoutResult,
    LayoutStatus,
    PanelGeometry,
    PhysicalInstance,
    Placement,
    RectMM,
)


def _to_units(value_mm: float, resolution_mm: float, *, ceil: bool = False) -> int:
    raw = float(value_mm) / float(resolution_mm)
    return int(math.ceil(raw - 1e-12)) if ceil else int(round(raw))


def _timeout_result(panel: PanelGeometry, config: LayoutConfig, reason: str) -> LayoutResult:
    return LayoutResult(
        panel_id=panel.panel_id,
        panel_revision=panel.revision,
        status=LayoutStatus.HOLD_LAYOUT_SOLVER_TIMEOUT,
        placements=(),
        metrics=LayoutMetrics(
            occupied_area_mm2=0.0,
            free_reserve_percent=0.0,
            minimum_clearance_mm=None,
            overlap_count=0,
            rail_count=0,
            wireway_count=0,
            terminal_count=0,
            gland_count=0,
        ),
        solver_manifest={
            "engine": "OR_TOOLS_CP_SAT",
            "ortools_version": getattr(ortools, "__version__", "unknown"),
            "seed": config.solver_seed,
            "max_time_seconds": config.max_time_seconds,
            "coordinate_resolution_mm": config.coordinate_resolution_mm,
            "status_name": "UNKNOWN",
        },
        diagnostics=(reason,),
        alternatives=(),
    )


def _empty_metrics(panel: PanelGeometry, instances: Sequence[PhysicalInstance]) -> LayoutMetrics:
    plate_area = panel.plate_width_mm * panel.plate_height_mm
    occupied = sum(
        i.width_mm * i.height_mm
        for i in instances
        if i.surface == "mounting_plate"
    )
    reserve = 100.0 if plate_area <= 0 else max(0.0, 100.0 * (plate_area - occupied) / plate_area)
    return LayoutMetrics(
        occupied_area_mm2=occupied,
        free_reserve_percent=reserve,
        minimum_clearance_mm=None,
        overlap_count=0,
        rail_count=0,
        wireway_count=0,
        terminal_count=0,
        gland_count=0,
        occupied_envelope_area_mm2=0.0,
        routing_complexity=0.0,
    )


def solve_single_panel(
    panel: PanelGeometry,
    instances: Sequence[PhysicalInstance],
    reserved_zones: Sequence[RectMM],
    config: LayoutConfig,
) -> LayoutResult:
    if config.coordinate_resolution_mm <= 0:
        raise ValueError("coordinate_resolution_mm must be > 0")
    if config.max_time_seconds <= 0:
        return _timeout_result(panel, config, "SOLVER_TIMEOUT_OR_UNKNOWN")

    unsupported = sorted(
        i.instance_id
        for i in instances
        if i.surface not in {"mounting_plate", "door"}
    )
    if unsupported:
        return LayoutResult(
            panel_id=panel.panel_id,
            panel_revision=panel.revision,
            status=LayoutStatus.HOLD_LAYOUT_INPUT,
            placements=(),
            metrics=_empty_metrics(panel, instances),
            solver_manifest={
                "engine": "OR_TOOLS_CP_SAT",
                "ortools_version": getattr(ortools, "__version__", "unknown"),
                "seed": config.solver_seed,
                "max_time_seconds": config.max_time_seconds,
                "coordinate_resolution_mm": config.coordinate_resolution_mm,
                "status_name": "INPUT_HOLD",
            },
            diagnostics=tuple(f"INVALID_SURFACE:{x}" for x in unsupported),
            alternatives=(),
        )

    resolution = float(config.coordinate_resolution_mm)
    model = cp_model.CpModel()
    ordered = sorted(instances, key=lambda i: i.instance_id)

    records: dict[str, dict[str, Any]] = {}
    x_intervals_by_surface: dict[str, list[Any]] = {"mounting_plate": [], "door": []}
    y_intervals_by_surface: dict[str, list[Any]] = {"mounting_plate": [], "door": []}
    end_x_by_surface: dict[str, list[Any]] = {"mounting_plate": [], "door": []}
    end_y_by_surface: dict[str, list[Any]] = {"mounting_plate": [], "door": []}

    def boundary_units(surface: str) -> tuple[int, int]:
        if surface == "mounting_plate":
            return (
                _to_units(panel.plate_width_mm, resolution),
                _to_units(panel.plate_height_mm, resolution),
            )
        return (
            _to_units(panel.enclosure_width_mm, resolution),
            _to_units(panel.enclosure_height_mm, resolution),
        )

    for idx, instance in enumerate(ordered):
        max_w, max_h = boundary_units(instance.surface)
        orientations = tuple(dict.fromkeys(int(x) % 360 for x in instance.allowed_orientations))
        if not orientations:
            orientations = (0,)

        orientation_index = model.NewIntVar(0, len(orientations) - 1, f"ori_{idx}")
        width_eff = model.NewIntVar(1, max_w, f"we_{idx}")
        height_eff = model.NewIntVar(1, max_h, f"he_{idx}")

        allowed_sizes: list[tuple[int, int, int]] = []
        physical_sizes: dict[int, tuple[float, float]] = {}
        for oi, rotation in enumerate(orientations):
            width_mm, height_mm = instance.dimensions_for_rotation(rotation)
            physical_sizes[oi] = (width_mm, height_mm)
            w_eff = _to_units(
                width_mm + instance.clearance.left + instance.clearance.right,
                resolution,
                ceil=True,
            )
            h_eff = _to_units(
                height_mm + instance.clearance.bottom + instance.clearance.top,
                resolution,
                ceil=True,
            )
            if w_eff <= max_w and h_eff <= max_h:
                allowed_sizes.append((oi, w_eff, h_eff))

        if not allowed_sizes:
            return LayoutResult(
                panel_id=panel.panel_id,
                panel_revision=panel.revision,
                status=LayoutStatus.HOLD_LAYOUT_CAPACITY,
                placements=(),
                metrics=_empty_metrics(panel, instances),
                solver_manifest={
                    "engine": "OR_TOOLS_CP_SAT",
                    "ortools_version": getattr(ortools, "__version__", "unknown"),
                    "seed": config.solver_seed,
                    "max_time_seconds": config.max_time_seconds,
                    "coordinate_resolution_mm": config.coordinate_resolution_mm,
                    "status_name": "INFEASIBLE_PRECHECK",
                },
                diagnostics=(f"INSTANCE_TOO_LARGE:{instance.instance_id}",),
                alternatives=(),
            )

        model.AddAllowedAssignments(
            [orientation_index, width_eff, height_eff],
            allowed_sizes,
        )

        x_start = model.NewIntVar(0, max_w, f"x_{idx}")
        y_start = model.NewIntVar(0, max_h, f"y_{idx}")
        x_end = model.NewIntVar(0, max_w, f"xe_{idx}")
        y_end = model.NewIntVar(0, max_h, f"ye_{idx}")
        model.Add(x_end == x_start + width_eff)
        model.Add(y_end == y_start + height_eff)
        model.Add(x_end <= max_w)
        model.Add(y_end <= max_h)

        x_interval = model.NewIntervalVar(x_start, width_eff, x_end, f"xi_{idx}")
        y_interval = model.NewIntervalVar(y_start, height_eff, y_end, f"yi_{idx}")
        x_intervals_by_surface[instance.surface].append(x_interval)
        y_intervals_by_surface[instance.surface].append(y_interval)
        end_x_by_surface[instance.surface].append(x_end)
        end_y_by_surface[instance.surface].append(y_end)

        records[instance.instance_id] = {
            "instance": instance,
            "orientation_index": orientation_index,
            "orientations": orientations,
            "physical_sizes": physical_sizes,
            "x_start": x_start,
            "y_start": y_start,
            "x_end": x_end,
            "y_end": y_end,
        }

    for surface in ("mounting_plate", "door"):
        x_intervals = list(x_intervals_by_surface[surface])
        y_intervals = list(y_intervals_by_surface[surface])

        if surface == "mounting_plate":
            plate_w = _to_units(panel.plate_width_mm, resolution)
            plate_h = _to_units(panel.plate_height_mm, resolution)
            for ridx, zone in enumerate(reserved_zones):
                zx = _to_units(zone.x, resolution)
                zy = _to_units(zone.y, resolution)
                zw = _to_units(zone.width, resolution, ceil=True)
                zh = _to_units(zone.height, resolution, ceil=True)
                if zx < 0 or zy < 0 or zx + zw > plate_w or zy + zh > plate_h:
                    return LayoutResult(
                        panel_id=panel.panel_id,
                        panel_revision=panel.revision,
                        status=LayoutStatus.HOLD_LAYOUT_INPUT,
                        placements=(),
                        metrics=_empty_metrics(panel, instances),
                        solver_manifest={
                            "engine": "OR_TOOLS_CP_SAT",
                            "ortools_version": getattr(ortools, "__version__", "unknown"),
                            "seed": config.solver_seed,
                            "max_time_seconds": config.max_time_seconds,
                            "coordinate_resolution_mm": config.coordinate_resolution_mm,
                            "status_name": "INPUT_HOLD",
                        },
                        diagnostics=(f"RESERVED_ZONE_OUT_OF_BOUNDS:{ridx}",),
                        alternatives=(),
                    )
                x_intervals.append(model.NewFixedSizeIntervalVar(zx, zw, f"rxi_{ridx}"))
                y_intervals.append(model.NewFixedSizeIntervalVar(zy, zh, f"ryi_{ridx}"))

        if x_intervals:
            model.AddNoOverlap2D(x_intervals, y_intervals)

    objective_terms: list[Any] = []
    envelope_weight = int(config.objective_weights.get("occupied_envelope", 100))
    connection_weight = int(config.objective_weights.get("connection_distance", 10))
    bottom_weight = int(config.objective_weights.get("bottom_zone_margin", 1))

    for surface in ("mounting_plate", "door"):
        if end_x_by_surface[surface]:
            bound_w, bound_h = boundary_units(surface)
            max_x = model.NewIntVar(0, bound_w, f"max_x_{surface}")
            max_y = model.NewIntVar(0, bound_h, f"max_y_{surface}")
            model.AddMaxEquality(max_x, end_x_by_surface[surface])
            model.AddMaxEquality(max_y, end_y_by_surface[surface])
            objective_terms.append(envelope_weight * (max_x + max_y))

    # Deterministic tie-break: stable instance order favors lower coordinates.
    for idx, instance in enumerate(ordered):
        rec = records[instance.instance_id]
        objective_terms.append((idx + 1) * (rec["x_start"] + rec["y_start"]))

    if connection_weight:
        seen_pairs: set[tuple[str, str]] = set()
        for instance in ordered:
            left = records.get(instance.instance_id)
            if left is None:
                continue
            for target_id in instance.connections:
                if target_id not in records:
                    continue
                pair = tuple(sorted((instance.instance_id, target_id)))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                right = records[target_id]
                max_w = max(
                    boundary_units(instance.surface)[0],
                    boundary_units(records[target_id]["instance"].surface)[0],
                )
                max_h = max(
                    boundary_units(instance.surface)[1],
                    boundary_units(records[target_id]["instance"].surface)[1],
                )
                dx = model.NewIntVar(0, max_w, f"dx_{len(seen_pairs)}")
                dy = model.NewIntVar(0, max_h, f"dy_{len(seen_pairs)}")
                model.AddAbsEquality(dx, left["x_start"] - right["x_start"])
                model.AddAbsEquality(dy, left["y_start"] - right["y_start"])
                objective_terms.append(connection_weight * (dx + dy))

    if bottom_weight and ordered:
        plate_y = [
            records[x.instance_id]["y_start"]
            for x in ordered
            if x.surface == "mounting_plate"
        ]
        if plate_y:
            plate_h = _to_units(panel.plate_height_mm, resolution)
            min_y = model.NewIntVar(0, plate_h, "min_plate_y")
            model.AddMinEquality(min_y, plate_y)
            objective_terms.append(-bottom_weight * min_y)

    model.Minimize(sum(objective_terms) if objective_terms else 0)

    solver = cp_model.CpSolver()
    solver.parameters.random_seed = int(config.solver_seed)
    solver.parameters.max_time_in_seconds = float(config.max_time_seconds)
    solver.parameters.num_search_workers = 1
    solver.parameters.log_search_progress = False

    status = solver.Solve(model)
    status_name = solver.StatusName(status)
    manifest = {
        "engine": "OR_TOOLS_CP_SAT",
        "ortools_version": getattr(ortools, "__version__", "unknown"),
        "seed": config.solver_seed,
        "max_time_seconds": config.max_time_seconds,
        "coordinate_resolution_mm": config.coordinate_resolution_mm,
        "num_search_workers": 1,
        "objective_weights": dict(config.objective_weights),
        "status_name": status_name,
    }

    if status == cp_model.INFEASIBLE:
        return LayoutResult(
            panel_id=panel.panel_id,
            panel_revision=panel.revision,
            status=LayoutStatus.HOLD_LAYOUT_CAPACITY,
            placements=(),
            metrics=_empty_metrics(panel, instances),
            solver_manifest=manifest,
            diagnostics=("CP_SAT_INFEASIBLE",),
            alternatives=(),
        )

    if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
        return LayoutResult(
            panel_id=panel.panel_id,
            panel_revision=panel.revision,
            status=LayoutStatus.HOLD_LAYOUT_SOLVER_TIMEOUT,
            placements=(),
            metrics=_empty_metrics(panel, instances),
            solver_manifest=manifest,
            diagnostics=("SOLVER_TIMEOUT_OR_UNKNOWN",),
            alternatives=(),
        )

    placements: list[Placement] = []
    for instance in ordered:
        rec = records[instance.instance_id]
        oi = solver.Value(rec["orientation_index"])
        rotation = rec["orientations"][oi]
        physical_width, physical_height = rec["physical_sizes"][oi]
        x_eff_mm = solver.Value(rec["x_start"]) * resolution
        y_eff_mm = solver.Value(rec["y_start"]) * resolution
        placements.append(
            Placement(
                instance_id=instance.instance_id,
                source_tag=instance.source_tag,
                catalog_id=instance.catalog_id,
                surface=instance.surface,
                x_mm=x_eff_mm + instance.clearance.left,
                y_mm=y_eff_mm + instance.clearance.bottom,
                width_mm=physical_width,
                height_mm=physical_height,
                rotation_deg=rotation,
                kind="component",
                quantity_index=instance.quantity_index,
                metadata={"functional_group": instance.functional_group},
            )
        )

    metrics = _empty_metrics(panel, instances)
    if placements:
        min_x = min(p.x_mm for p in placements)
        min_y = min(p.y_mm for p in placements)
        max_x = max(p.x_mm + p.width_mm for p in placements)
        max_y = max(p.y_mm + p.height_mm for p in placements)
        metrics = LayoutMetrics(
            occupied_area_mm2=metrics.occupied_area_mm2,
            free_reserve_percent=metrics.free_reserve_percent,
            minimum_clearance_mm=None,
            overlap_count=0,
            rail_count=0,
            wireway_count=0,
            terminal_count=0,
            gland_count=0,
            occupied_envelope_area_mm2=max(0.0, (max_x - min_x) * (max_y - min_y)),
            routing_complexity=0.0,
        )

    return LayoutResult(
        panel_id=panel.panel_id,
        panel_revision=panel.revision,
        status=LayoutStatus.LAYOUT_FEASIBLE,
        placements=tuple(placements),
        metrics=metrics,
        solver_manifest=manifest,
        diagnostics=(),
        alternatives=(),
    )
