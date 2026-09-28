#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_AUTHORITIES = {
    "MANUFACTURER_STEP_OR_IGES",
    "MANUFACTURER_DXF_OR_NATIVE_CAD",
    "PARAMETRIC_RECONSTRUCTION_FROM_OFFICIAL_DIMENSIONAL_DRAWING",
    "OFFICIAL_DIMENSIONAL_BBOX_PROXY",
}

def _close(a: float, b: float, tolerance_percent: float = 1.0) -> bool:
    if a == b:
        return True
    scale = max(abs(a), abs(b), 1.0)
    return abs(a - b) / scale * 100.0 <= tolerance_percent

def validate_geometry_manifest(data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    holds: list[str] = []

    if data.get("units") != "mm":
        errors.append("geometry units must be mm")
    if data.get("canvas_policy") != "GROW_CANVAS_KEEP_SCALE":
        errors.append("canvas policy must be GROW_CANVAS_KEEP_SCALE")
    if data.get("generative_geometry_authority") is not False:
        errors.append("generative geometry authority must be false")

    assembly_id = str(data.get("assembly_id") or "")
    if not assembly_id:
        errors.append("assembly_id is required")

    components = data.get("components") or []
    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty list")
        components = []

    ids: set[str] = set()
    for comp in components:
        cid = str(comp.get("instance_id") or "")
        if not cid or cid in ids:
            errors.append(f"duplicate or missing component instance_id: {cid}")
        ids.add(cid)
        authority = comp.get("geometry_authority")
        if authority not in ALLOWED_AUTHORITIES:
            holds.append(f"{cid}: unsupported/unverified geometry authority {authority}")
        official = comp.get("official_bbox_mm") or {}
        model = comp.get("model_bbox_mm") or {}
        for axis in ("width","height","depth"):
            ov=official.get(axis); mv=model.get(axis)
            if not isinstance(ov,(int,float)) or ov <= 0:
                holds.append(f"{cid}: official {axis} missing")
                continue
            if not isinstance(mv,(int,float)) or mv <= 0:
                errors.append(f"{cid}: model {axis} missing")
                continue
            if not _close(float(ov),float(mv),1.0):
                errors.append(f"{cid}: model {axis} differs from official bbox by more than 1%")

    views = data.get("views") or []
    if not isinstance(views,list):
        errors.append("views must be a list")
        views=[]
    required={"front_internal","front_external","right_side","depth_section"}
    seen=set()
    for view in views:
        vid=str(view.get("view_id") or "")
        if vid: seen.add(vid)
        if view.get("assembly_id") != assembly_id:
            errors.append(f"{vid}: view must reference common assembly_id")
        if view.get("projection") != "ORTHOGRAPHIC":
            errors.append(f"{vid}: dimensional view must be ORTHOGRAPHIC")
        if view.get("independent_scale") is True:
            errors.append(f"{vid}: independent per-view scaling is forbidden")
    missing=sorted(required-seen)
    if missing:
        errors.append(f"missing required assembly views: {missing}")

    blocks=set(data.get("visual_blocks") or [])
    forbidden={"door_internal_hmi_detail","bottom_cable_exit_view","item_4","item_8"}
    present=sorted(blocks & forbidden)
    if present:
        errors.append(f"removed visual blocks present: {present}")

    status="REPROVADO" if errors else ("HOLD" if holds else "PASS")
    return {"status":status,"errors":errors,"holds":holds,"assembly_id":assembly_id,"component_count":len(components),"views":sorted(seen)}

def main() -> int:
    p=argparse.ArgumentParser(description="Validate AUT panel CAD-first 3D geometry manifest")
    p.add_argument("manifest")
    args=p.parse_args()
    data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result=validate_geometry_manifest(data)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="PASS" else 2

if __name__=="__main__":
    raise SystemExit(main())
