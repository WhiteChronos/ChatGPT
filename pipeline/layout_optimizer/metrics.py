from __future__ import annotations
import math
from collections.abc import Sequence
from .geometry import overlaps
from .models import LayoutMetrics, LayoutResult, LayoutStatus, PanelGeometry, Placement

def _engineering_rects(placements: Sequence[Placement]) -> list[Placement]:
    return [p for p in placements if p.surface=="mounting_plate" and p.kind not in {"din_rail","wireway","cable_gland"}]

def _gap(a: Placement,b: Placement) -> float:
    if overlaps(a.rect,b.rect): return 0.0
    dx=max(a.x_mm-(b.x_mm+b.width_mm),b.x_mm-(a.x_mm+a.width_mm),0.0)
    dy=max(a.y_mm-(b.y_mm+b.height_mm),b.y_mm-(a.y_mm+a.height_mm),0.0)
    if dx and dy: return math.hypot(dx,dy)
    return max(dx,dy)

def calculate_metrics(panel: PanelGeometry, placements: Sequence[Placement]) -> LayoutMetrics:
    plate_area=max(1.0,panel.plate_width_mm*panel.plate_height_mm)
    occupied_items=[p for p in placements if p.surface=="mounting_plate" and p.kind!="din_rail"]
    occupied=sum(p.width_mm*p.height_mm for p in occupied_items)
    lower_reserved=panel.plate_width_mm*min(panel.plate_height_mm,max(0.0,panel.terminal_zone_bottom_y_mm))
    reserve=max(0.0,100.0*(plate_area-lower_reserved-occupied)/plate_area)
    rects=_engineering_rects(placements)
    overlap_count=0; gaps=[]
    for i,a in enumerate(rects):
        for b in rects[i+1:]:
            g=_gap(a,b)
            if g==0.0 and overlaps(a.rect,b.rect): overlap_count+=1
            else: gaps.append(g)
    min_clearance=0.0 if overlap_count else (min(gaps) if gaps else None)
    plate=[p for p in placements if p.surface=="mounting_plate"]
    if plate:
        min_x=min(p.x_mm for p in plate); min_y=min(p.y_mm for p in plate)
        max_x=max(p.x_mm+p.width_mm for p in plate); max_y=max(p.y_mm+p.height_mm for p in plate)
        envelope=max(0.0,(max_x-min_x)*(max_y-min_y))
    else: envelope=0.0
    terminal_count=sum(p.kind=="terminal_strip" or p.source_tag.startswith(("XT-","XPE-")) for p in placements if p.surface=="mounting_plate")
    return LayoutMetrics(
        occupied_area_mm2=occupied,
        free_reserve_percent=round(reserve,6),
        minimum_clearance_mm=None if min_clearance is None else round(min_clearance,6),
        overlap_count=overlap_count,
        rail_count=sum(p.kind=="din_rail" for p in placements),
        wireway_count=sum(p.kind=="wireway" for p in placements),
        terminal_count=terminal_count,
        gland_count=sum(p.kind=="cable_gland" for p in placements),
        occupied_envelope_area_mm2=envelope,
        routing_complexity=0.0,
    )

def validate_layout_result(panel: PanelGeometry, result: LayoutResult) -> LayoutResult:
    if result.status not in {LayoutStatus.LAYOUT_FEASIBLE,LayoutStatus.LAYOUT_VALIDATED}: return result
    m=calculate_metrics(panel,result.placements)
    diags=list(result.diagnostics)
    status=LayoutStatus.LAYOUT_VALIDATED
    if m.overlap_count:
        diags.append(f"OVERLAP_COUNT:{m.overlap_count}"); status=LayoutStatus.HOLD_LAYOUT_CAPACITY
    if m.free_reserve_percent+1e-9<panel.minimum_free_reserve_percent:
        diags.append(f"INSUFFICIENT_RESERVE:{m.free_reserve_percent:.3f}<{panel.minimum_free_reserve_percent:.3f}"); status=LayoutStatus.HOLD_LAYOUT_CAPACITY
    return LayoutResult(result.panel_id,result.panel_revision,status,result.placements,m,result.solver_manifest,tuple(diags),result.alternatives)
