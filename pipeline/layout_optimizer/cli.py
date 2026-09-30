from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Mapping
from .infrastructure import build_cable_glands, build_din_rails, build_lower_zones, build_terminal_strips, build_wireways, validate_infrastructure_requirements
from .metrics import calculate_metrics, validate_layout_result
from .models import LayoutConfig, LayoutResult, LayoutStatus
from .normalize import normalize_inputs
from .partition import generate_split_candidates
from .capacity import find_larger_enclosure_candidates
from .solver import solve_single_panel
from .export import export_layout_result

def _enclosure_candidates(catalog: Mapping[str,Any]) -> list[Mapping[str,Any]]:
    out=[]
    for item in catalog.get("components",[]):
        if str(item.get("category") or "")!="enclosure":
            continue
        if item.get("external_mm") and item.get("mounting_plate_mm"):
            out.append(item)
    return out

def optimize_panel(panel_id: str, li: Mapping[str,Any], bom: Mapping[str,Any], catalog: Mapping[str,Any], project: Mapping[str,Any], config: LayoutConfig | None = None) -> LayoutResult:
    cfg=config or LayoutConfig()
    try:
        panel,instances,infra,diags=normalize_inputs(panel_id,li,bom,catalog,project,cfg)
    except ValueError as exc:
        from .models import LayoutMetrics
        return LayoutResult(panel_id,str((project.get("project") or {}).get("revision") or ""),LayoutStatus.HOLD_LAYOUT_INPUT,(),LayoutMetrics(0,0,None,0,0,0,0,0),{"engine":"PRECHECK"},(str(exc),),())
    if diags:
        from .models import LayoutMetrics
        return LayoutResult(panel.panel_id,panel.revision,LayoutStatus.HOLD_LAYOUT_INPUT,(),LayoutMetrics(0,0,None,0,0,0,0,0),{"engine":"PRECHECK"},tuple(diags),())
    zones=build_lower_zones(panel)
    reserved=[z for z in (zones["cable_exit"],zones["bend_clearance"],zones["lower_wireway"]) if z.width>0 and z.height>0]
    solved=solve_single_panel(panel,instances,reserved,cfg)
    if solved.status==LayoutStatus.HOLD_LAYOUT_CAPACITY:
        alternatives=[]
        alternatives.extend(find_larger_enclosure_candidates(panel,instances,_enclosure_candidates(catalog),cfg))
        links=((project.get("architecture") or {}).get("dependency_links") or [])
        alternatives.extend(generate_split_candidates(panel,instances,links,cfg))
        if alternatives:
            return LayoutResult(panel.panel_id,panel.revision,LayoutStatus.USER_DECISION_REQUIRED,(),solved.metrics,solved.solver_manifest,solved.diagnostics,tuple(alternatives))
        return solved
    if solved.status not in {LayoutStatus.LAYOUT_FEASIBLE,LayoutStatus.LAYOUT_VALIDATED}:
        return solved
    instance_map={x.instance_id:x for x in instances}
    infra_places=[]; infra_diags=[]
    if infra.get("din_rail"):
        r,d=build_din_rails(panel,solved.placements,instance_map,infra["din_rail"][0],cfg); infra_places+=r; infra_diags+=d
    for req in infra.get("wireway",[]):
        r,d=build_wireways(panel,req,cfg); infra_places+=r; infra_diags+=d
    t,d=build_terminal_strips(panel,solved.placements,instance_map,cfg); infra_places+=t; infra_diags+=d
    for req in infra.get("cable_gland",[]):
        r,d=build_cable_glands(panel,req,cfg); infra_places+=r; infra_diags+=d
    errors=validate_infrastructure_requirements(panel,solved.placements,infra_places,infra_diags)
    all_places=tuple(list(solved.placements)+infra_places)
    base=LayoutResult(panel.panel_id,panel.revision,LayoutStatus.LAYOUT_FEASIBLE,all_places,calculate_metrics(panel,all_places),solved.solver_manifest,tuple(errors),())
    if errors:
        status=LayoutStatus.HOLD_LAYOUT_CABLE_ENTRY if any("CABLE_GLAND" in x for x in errors) else LayoutStatus.HOLD_LAYOUT_INPUT
        return LayoutResult(base.panel_id,base.panel_revision,status,base.placements,base.metrics,base.solver_manifest,base.diagnostics,())
    return validate_layout_result(panel,base)

def _load(path:str)->dict[str,Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--panel-id",required=True); p.add_argument("--li",required=True); p.add_argument("--bom",required=True); p.add_argument("--catalog",required=True); p.add_argument("--project",required=True); p.add_argument("--output",required=True)
    a=p.parse_args()
    r=optimize_panel(a.panel_id,_load(a.li),_load(a.bom),_load(a.catalog),_load(a.project))
    export_layout_result(r,Path(a.output))
    print(json.dumps({"status":r.status.value,"output":a.output}))
    if r.status==LayoutStatus.LAYOUT_VALIDATED: return 0
    if r.status==LayoutStatus.USER_DECISION_REQUIRED: return 4
    return 3

if __name__=="__main__":
    raise SystemExit(main())
