from __future__ import annotations
from typing import Any, Mapping, Sequence
from .models import CapacityAlternative, LayoutConfig, LayoutStatus, PanelGeometry, PhysicalInstance
from .solver import solve_single_panel

def diagnose_capacity(panel: PanelGeometry, instances: Sequence[PhysicalInstance]) -> list[str]:
    area=sum(i.width_mm*i.height_mm for i in instances if i.surface=="mounting_plate")
    plate=panel.plate_width_mm*panel.plate_height_mm
    return [f"PLATE_AREA_MM2:{plate:.1f}",f"COMPONENT_AREA_MM2:{area:.1f}",f"AREA_RATIO:{(area/plate if plate else 1):.4f}"]

def find_larger_enclosure_candidates(panel: PanelGeometry, instances: Sequence[PhysicalInstance], enclosures: Sequence[Mapping[str,Any]], config: LayoutConfig) -> list[CapacityAlternative]:
    out=[]
    ordered=sorted(enclosures,key=lambda e:(float((e.get("mounting_plate_mm") or {}).get("width",0))*float((e.get("mounting_plate_mm") or {}).get("height",0)),str(e.get("catalog_id") or "")))
    for e in ordered:
        ext=e.get("external_mm") or {}; plate=e.get("mounting_plate_mm") or {}
        try:
            cand=PanelGeometry(panel.panel_id,panel.revision,float(ext["width"]),float(ext["height"]),float(ext["depth"]),float(plate["width"]),float(plate["height"]),panel.minimum_free_reserve_percent,panel.cable_exit_height_mm,panel.lower_wireway_height_mm,panel.minimum_bend_clearance_mm,panel.terminal_zone_bottom_y_mm,panel.cable_glands_count)
        except Exception:
            continue
        r=solve_single_panel(cand,instances,[],config)
        if r.status not in {LayoutStatus.LAYOUT_FEASIBLE,LayoutStatus.LAYOUT_VALIDATED}: continue
        out.append(CapacityAlternative(f"ENC-{e.get('catalog_id')}","LARGER_ENCLOSURE",LayoutStatus.USER_DECISION_REQUIRED,({"panel_id":panel.panel_id,"enclosure_catalog_id":e.get("catalog_id"),"external_mm":ext,"mounting_plate_mm":plate},),{"free_reserve_percent":r.metrics.free_reserve_percent},{"requires_new_li_revision":True},tuple(diagnose_capacity(panel,instances)),True))
    return out
