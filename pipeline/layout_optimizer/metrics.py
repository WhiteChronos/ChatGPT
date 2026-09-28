from __future__ import annotations
from collections.abc import Sequence
from .models import LayoutMetrics, PanelGeometry, Placement

def calculate_metrics(panel: PanelGeometry, placements: Sequence[Placement]) -> LayoutMetrics:
    comps=[p for p in placements if p.surface=="mounting_plate" and p.kind=="component"]
    occupied=sum(p.width_mm*p.height_mm for p in comps)
    plate=max(1.0,panel.plate_width_mm*panel.plate_height_mm)
    reserve=max(0.0,100.0*(plate-occupied)/plate)
    return LayoutMetrics(occupied,reserve,None,0,sum(p.kind=="din_rail" for p in placements),sum(p.kind=="wireway" for p in placements),sum(p.kind=="terminal_strip" for p in placements),sum(p.kind=="cable_gland" for p in placements),0.0,0.0)
