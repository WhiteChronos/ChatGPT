#!/usr/bin/env python3
import argparse, json
from pathlib import Path

ALLOWED = {
    "MANUFACTURER_STEP_OR_IGES",
    "MANUFACTURER_DXF_OR_NATIVE_CAD",
    "PARAMETRIC_RECONSTRUCTION_FROM_OFFICIAL_DIMENSIONAL_DRAWING",
    "OFFICIAL_DIMENSIONAL_BBOX_PROXY",
}

def close(a, b, tol_pct=1.0):
    scale=max(abs(float(a)), abs(float(b)), 1.0)
    return abs(float(a)-float(b))/scale*100 <= tol_pct

def validate(data):
    errors=[]; holds=[]
    if data.get("units") != "mm": errors.append("units must be mm")
    if data.get("canvas_policy") != "GROW_CANVAS_KEEP_SCALE": errors.append("canvas must grow; geometry must not shrink")
    if data.get("generative_geometry_authority") is not False: errors.append("generative geometry authority must be false")
    assembly=data.get("assembly_id")
    if not assembly: errors.append("assembly_id required")
    for comp in data.get("components", []):
        cid=comp.get("instance_id", "?")
        if comp.get("geometry_authority") not in ALLOWED: holds.append(f"{cid}: unverified geometry authority")
        official=comp.get("official_bbox_mm", {}); model=comp.get("model_bbox_mm", {})
        for axis in ("width","height","depth"):
            if not isinstance(official.get(axis),(int,float)) or official[axis] <= 0: holds.append(f"{cid}: official {axis} missing"); continue
            if not isinstance(model.get(axis),(int,float)) or model[axis] <= 0: errors.append(f"{cid}: model {axis} missing"); continue
            if not close(official[axis], model[axis]): errors.append(f"{cid}: {axis} bbox mismatch >1%")
    for view in data.get("views", []):
        vid=view.get("view_id","?")
        if view.get("assembly_id") != assembly: errors.append(f"{vid}: different assembly")
        if view.get("projection") != "ORTHOGRAPHIC": errors.append(f"{vid}: dimensional view must be orthographic")
        if view.get("independent_scale") is True: errors.append(f"{vid}: independent scale forbidden")
    forbidden={"door_internal_hmi_detail","bottom_cable_exit_view","item_4","item_8"}
    present=forbidden.intersection(set(data.get("visual_blocks", [])))
    if present: errors.append(f"removed visual blocks present: {sorted(present)}")
    status="REPROVADO" if errors else ("HOLD" if holds else "PASS")
    return {"status":status,"errors":errors,"holds":holds}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("manifest")
    args=ap.parse_args(); data=json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result=validate(data); print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__": raise SystemExit(main())
