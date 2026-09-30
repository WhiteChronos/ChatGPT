#!/usr/bin/env python3
import argparse, json, sys
DIM_TOL=0.10
SCALE_TOL=1e-6
def close(a,b,t): return abs(float(a)-float(b))<=t
def vec_close(a,b,t): return len(a)==len(b) and all(close(x,y,t) for x,y in zip(a,b))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("manifest"); a=ap.parse_args()
    with open(a.manifest,"r",encoding="utf-8") as f: m=json.load(f)
    e=[]; b=m.get("canonical",{}); views=m.get("views",[])
    for k in ["assembly_hash","h_mm","w_mm","d_mm","door_bbox_mm","enclosure_bbox_mm","hinge_axis_origin_mm","hinge_axis_direction"]:
        if k not in b: e.append("missing canonical."+k)
    for v in views:
        vid=v.get("view_id")
        if v.get("assembly_hash")!=b.get("assembly_hash"): e.append(f"{vid}: assembly_hash mismatch")
        for k in ("h_mm","w_mm","d_mm"):
            if k in b and not close(v.get(k,float("nan")),b[k],DIM_TOL): e.append(f"{vid}: {k} mismatch")
        if "door_bbox_mm" in b and not vec_close(v.get("door_bbox_mm",[]),b["door_bbox_mm"],DIM_TOL): e.append(f"{vid}: door bbox changed")
        if "enclosure_bbox_mm" in b and not vec_close(v.get("enclosure_bbox_mm",[]),b["enclosure_bbox_mm"],DIM_TOL): e.append(f"{vid}: enclosure bbox changed")
        if not vec_close(v.get("hinge_axis_origin_mm",[]),b.get("hinge_axis_origin_mm",[]),DIM_TOL): e.append(f"{vid}: hinge origin changed")
        if not vec_close(v.get("hinge_axis_direction",[]),b.get("hinge_axis_direction",[]),SCALE_TOL): e.append(f"{vid}: hinge direction changed")
        for o in v.get("object_scales",[]):
            s=o.get("scale",[])
            if len(s)!=3 or any(abs(float(x)-1.0)>SCALE_TOL for x in s): e.append(f"{vid}: object {o.get('id')} scale is not [1,1,1]")
    print(json.dumps({"status":"PASS" if not e else "FAIL","errors":e,"view_count":len(views)},indent=2))
    sys.exit(0 if not e else 2)
if __name__=="__main__": main()
