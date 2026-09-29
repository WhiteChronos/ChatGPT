from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from .models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance

INFRASTRUCTURE_CATEGORIES={"din_rail":"din_rail","wireway":"wireway","cable_gland":"cable_gland"}
INFRASTRUCTURE_TAG_PREFIXES={"DIN-":"din_rail","WD-":"wireway","CG-":"cable_gland"}

def _catalog_index(catalog: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(x.get("catalog_id")):x for x in catalog.get("components",[]) if x.get("catalog_id")}

def _line_tag(line: Mapping[str, Any]) -> str:
    return str(line.get("tag") or line.get("li_tag") or "")

def _assert_li_bom_parity(li: Mapping[str, Any], bom: Mapping[str, Any]) -> None:
    lm={_line_tag(x):(str(x.get("catalog_id") or ""),x.get("quantity"),str(x.get("unit") or "")) for x in li.get("lines",[])}
    bm={_line_tag(x):(str(x.get("catalog_id") or ""),x.get("quantity"),str(x.get("unit") or "")) for x in bom.get("lines",[])}
    if lm!=bm:
        raise ValueError("LI_BOM_PARITY")

def classify_line_kind(line: Mapping[str, Any], item: Mapping[str, Any] | None) -> str:
    cat=str((item or {}).get("category") or "")
    if cat in INFRASTRUCTURE_CATEGORIES: return INFRASTRUCTURE_CATEGORIES[cat]
    tag=_line_tag(line)
    for p,k in INFRASTRUCTURE_TAG_PREFIXES.items():
        if tag.startswith(p): return k
    return "component"

def _positive(v: Any) -> bool:
    return isinstance(v,(int,float)) and not isinstance(v,bool) and v>0

def _clearance(item: Mapping[str, Any]) -> ClearanceMM:
    r=item.get("clearance_mm") or {}
    return ClearanceMM(float(r.get("left",0) or 0),float(r.get("right",0) or 0),float(r.get("top",0) or 0),float(r.get("bottom",0) or 0))

def _orientations(item: Mapping[str, Any]) -> tuple[int,...]:
    r=item.get("allowed_orientations_deg")
    if not isinstance(r,Sequence) or isinstance(r,(str,bytes)): return (0,)
    out=tuple(int(x)%360 for x in r if int(x)%360 in {0,90,180,270})
    return out or (0,)

def _panel(panel_id: str, project: Mapping[str, Any]) -> PanelGeometry:
    pm=project.get("project") or {}
    if str(pm.get("id") or panel_id)!=panel_id: raise ValueError("PANEL_ID_MISMATCH")
    e=project.get("enclosure") or {}; ext=e.get("external_mm") or {}; plate=e.get("mounting_plate_mm") or {}
    vals=[ext.get("width"),ext.get("height"),ext.get("depth"),plate.get("width"),plate.get("height")]
    if not all(_positive(v) for v in vals): raise ValueError("PANEL_GEOMETRY_INVALID")
    b=((project.get("layout") or {}).get("bottom_zone") or {})
    return PanelGeometry(panel_id,str(pm.get("revision") or ""),float(ext["width"]),float(ext["height"]),float(ext["depth"]),float(plate["width"]),float(plate["height"]),float(e.get("minimum_free_reserve_percent",0) or 0),float(b.get("cable_exit_height_mm",0) or 0),float(b.get("lower_wireway_height_mm",0) or 0),float(b.get("minimum_bend_clearance_mm",0) or 0),float(b.get("terminal_zone_bottom_y_mm",0) or 0),int(b.get("cable_glands_count",0) or 0))

def extract_infrastructure_requests(li: Mapping[str, Any], bom: Mapping[str, Any], catalog: Mapping[str, Any]) -> dict[str,list[dict[str,Any]]]:
    _assert_li_bom_parity(li,bom)
    idx=_catalog_index(catalog); out:dict[str,list[dict[str,Any]]]=defaultdict(list)
    for line in li.get("lines",[]):
        cid=str(line.get("catalog_id") or ""); item=idx.get(cid); kind=classify_line_kind(line,item)
        if kind=="component": continue
        out[kind].append({"kind":kind,"source_tag":_line_tag(line),"catalog_id":cid,"quantity":int(line.get("quantity") or 0),"unit":str(line.get("unit") or ""),"dimensions_mm":(item or {}).get("dimensions_mm")})
    return dict(out)

def normalize_inputs(panel_id: str, li: Mapping[str, Any], bom: Mapping[str, Any], catalog: Mapping[str, Any], project: Mapping[str, Any], config: LayoutConfig) -> tuple[PanelGeometry,list[PhysicalInstance],dict[str,list[dict[str,Any]]],list[str]]:
    del config
    _assert_li_bom_parity(li,bom)
    if str(li.get("project_id") or "")!=panel_id: raise ValueError("LI_PROJECT_MISMATCH")
    if li.get("status")!="QUANTITY_FROZEN": raise ValueError("LI_NOT_FROZEN")
    panel=_panel(panel_id,project)
    if str(li.get("revision") or "")!=panel.revision: raise ValueError("REVISION_MISMATCH")
    idx=_catalog_index(catalog); diagnostics=[]; instances=[]
    infrastructure=extract_infrastructure_requests(li,bom,catalog)
    for line in li.get("lines",[]):
        if line.get("render_required") is not True: continue
        tag=_line_tag(line); cid=str(line.get("catalog_id") or ""); item=idx.get(cid)
        if classify_line_kind(line,item)!="component": continue
        if item is None:
            diagnostics.append(f"MISSING_CATALOG:{cid}"); continue
        dims=item.get("dimensions_mm")
        if not isinstance(dims,Mapping) or not all(_positive((dims or {}).get(k)) for k in ("width","height","depth")):
            diagnostics.append(f"MISSING_DIMENSIONS:{cid}"); continue
        qty=line.get("quantity")
        if not isinstance(qty,int) or isinstance(qty,bool) or qty<1: raise ValueError(f"INVALID_QUANTITY:{tag}")
        cat=str(item.get("category") or "")
        surface=str(line.get("surface") or item.get("surface") or ("door" if cat=="hmi" or tag.startswith("HMI-") else "mounting_plate"))
        rail=bool(item.get("rail_required", cat not in {"battery","hmi","enclosure","mounting_plate"}))
        for qi in range(1,qty+1):
            instances.append(PhysicalInstance(f"{tag}#{qi:02d}",tag,cid,qi,surface,float(dims["width"]),float(dims["height"]),float(dims["depth"]),_clearance(item),_orientations(item),str(item.get("functional_group") or cat or "") or None,rail,float(item["heat_loss_w"]) if _positive(item.get("heat_loss_w")) else None,tuple(str(x) for x in item.get("connections",[]) if x),{"category":cat}))
    return panel,instances,infrastructure,list(dict.fromkeys(diagnostics))
