#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import cadquery as cq
import ezdxf
from cadquery.occ_impl.shapes import Shape, Compound, TOLERANCE
from cadquery.occ_impl.exporters.dxf import DxfDocument
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCP.BRepLib import BRepLib
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.HLRAlgo import HLRAlgo_Projector

VIEWS={
 "FRONT":(0.0,-1.0,0.0),"BACK":(0.0,1.0,0.0),"RIGHT":(1.0,0.0,0.0),
 "LEFT":(-1.0,0.0,0.0),"TOP":(0.0,0.0,1.0),"BOTTOM":(0.0,0.0,-1.0),
 "ISO":(1.0,-1.0,1.0),
}
def flatten_edges(s):
    if s.IsNull(): return []
    BRepLib.BuildCurves3d_s(s,TOLERANCE)
    return Shape(s).Edges()
def project(shape,view_spec,clean_iso=False):
    direction=view_spec["direction"]; xdir=view_spec["xdir"]
    hlr=HLRBRep_Algo(); hlr.Add(shape.wrapped)
    ax2=gp_Ax2(gp_Pnt(),gp_Dir(*direction),gp_Dir(*xdir))
    hlr.Projector(HLRAlgo_Projector(ax2))
    hlr.Update(); hlr.Hide(); hs=HLRBRep_HLRToShape(hlr)
    visible=[]; hidden=[]
    visible_getters=("VCompound","OutLineVCompound") if clean_iso else ("VCompound","Rg1LineVCompound","OutLineVCompound")
    for getter in visible_getters:
        visible.extend(flatten_edges(getattr(hs,getter)()))
    for getter in ("HCompound","OutLineHCompound"):
        hidden.extend(flatten_edges(getattr(hs,getter)()))
    return Compound.makeCompound(visible) if visible else None, Compound.makeCompound(hidden) if hidden else None
def bb2(shape):
    b=shape.BoundingBox()
    return {"xmin":b.xmin,"xmax":b.xmax,"ymin":b.ymin,"ymax":b.ymax,"width":b.xlen,"height":b.ylen}
def shifted(shape,dx,dy):
    return shape.translate((dx,dy,0.0)) if shape else None
def new_doc():
    d=DxfDocument(dxfversion="AC1027",setup=["linetypes","styles"],doc_units=6)
    d.document.header["$INSUNITS"]=6
    if "ARIAL" not in d.document.styles: d.document.styles.add("ARIAL",font="Arial.ttf")
    return d
def add_layers(doc,view):
    for suffix,color,ltype in (("VISIBLE",7,"CONTINUOUS"),("HIDDEN",8,"DASHED")):
        name=f"{view}_{suffix}"
        if name not in doc.document.layers: doc.document.layers.add(name,dxfattribs={"color":color,"linetype":ltype})
def add_shapes(doc,view,visible,hidden):
    add_layers(doc,view)
    if visible: doc.add_shape(cq.Workplane("XY").newObject([visible]),f"{view}_VISIBLE")
    if hidden: doc.add_shape(cq.Workplane("XY").newObject([hidden]),f"{view}_HIDDEN")
def save_single(path,view,vis,hid):
    d=new_doc(); add_shapes(d,view,vis,hid); d.document.saveas(path)
def arrange(view_data,gap):
    fb=view_data["FRONT"][2]; raw={"FRONT":(0,0)}
    if "TOP" in view_data: raw["TOP"]=(0,fb["height"]+gap)
    if "BOTTOM" in view_data: raw["BOTTOM"]=(0,-(view_data["BOTTOM"][2]["height"]+gap))
    if "RIGHT" in view_data: raw["RIGHT"]=(fb["width"]+gap,0)
    if "LEFT" in view_data: raw["LEFT"]=(-(view_data["LEFT"][2]["width"]+gap),0)
    if "BACK" in view_data: raw["BACK"]=(fb["width"]+gap,-(view_data["BACK"][2]["height"]+gap))
    if "ISO" in view_data:
        right_w=view_data.get("RIGHT",(None,None,{"width":0}))[2]["width"]
        raw["ISO"]=(fb["width"]+right_w+2*gap,fb["height"]+gap)
    placed={}
    for v,(tx,ty) in raw.items():
        b=view_data[v][2]; dx=tx-b["xmin"]; dy=ty-b["ymin"]
        placed[v]={"dx":dx,"dy":dy,"bbox":{"xmin":b["xmin"]+dx,"xmax":b["xmax"]+dx,"ymin":b["ymin"]+dy,"ymax":b["ymax"]+dy}}
    minx=min(p["bbox"]["xmin"] for p in placed.values()); miny=min(p["bbox"]["ymin"] for p in placed.values())
    sx=gap-minx if minx<gap else 0; sy=gap-miny if miny<gap else 0
    for p in placed.values():
        p["dx"]+=sx; p["dy"]+=sy
        for k in ("xmin","xmax"): p["bbox"][k]+=sx
        for k in ("ymin","ymax"): p["bbox"][k]+=sy
    return placed
def overlaps(a,b,eps=1e-9):
    return not (a["xmax"]<=b["xmin"]+eps or b["xmax"]<=a["xmin"]+eps or a["ymax"]<=b["ymin"]+eps or b["ymax"]<=a["ymin"]+eps)
def _norm(v):
    n=math.sqrt(sum(x*x for x in v)); return tuple(x/n for x in v)
def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def _dot(a,b):
    return sum(x*y for x,y in zip(a,b))
def canonical_iso_axis_qa(true_length=True):
    spec=VIEWS["ISO"]; zdir=_norm(spec["direction"]); xdir=_norm(spec["xdir"]); ydir=_norm(_cross(zdir,xdir))
    scale=ISO_TRUE_LENGTH_SCALE if true_length else 1.0
    basis={"X":(1.0,0.0,0.0),"Y":(0.0,1.0,0.0),"Z":(0.0,0.0,1.0)}
    expected={"X":30.0,"Y":150.0,"Z":90.0}; axes={}
    for name,axis in basis.items():
        sx=_dot(axis,xdir)*scale; sy=_dot(axis,ydir)*scale
        axes[name]={"angle_deg":math.degrees(math.atan2(sy,sx))%360.0,"projected_axis_length":math.hypot(sx,sy)}
    passed=all(abs(axes[k]["angle_deg"]-expected[k])<1e-6 for k in expected)
    if true_length: passed=passed and all(abs(axes[k]["projected_axis_length"]-1.0)<1e-6 for k in expected)
    return {"mode":"true_length" if true_length else "projection","axes":axes,"expected_angles_deg":expected,"pass":passed}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("--outdir",required=True); ap.add_argument("--name",default=None)
    ap.add_argument("--gap",type=float,default=None)
    ap.add_argument("--views",default="FRONT,LEFT,RIGHT,TOP,BOTTOM,ISO")
    ap.add_argument("--no-hidden",action="store_true"); args=ap.parse_args()
    src=Path(args.step); outdir=Path(args.outdir); outdir.mkdir(parents=True,exist_ok=True); name=args.name or src.stem
    model=cq.importers.importStep(str(src)).val().scale(0.001)
    requested=[v.strip().upper() for v in args.views.split(",") if v.strip()]
    view_data={}
    for v in requested:
        if v not in VIEWS: raise SystemExit(f"unknown view: {v}")
        vis,hid=project(model,VIEWS[v],clean_iso=(v=="ISO" and not args.iso_hidden))
        if not vis: raise SystemExit(f"projection produced no visible geometry: {v}")
        if args.no_hidden:
            hid=None
        elif v == "ISO" and not args.iso_hidden:
            hid=None
        view_data[v]=(vis,hid,bb2(vis)); save_single(outdir/f"{name}_{v}.dxf",v,vis,hid)
    maxdim=max(max(d[2]["width"],d[2]["height"]) for d in view_data.values())
    gap=args.gap if args.gap is not None else max(maxdim*0.20,0.01)
    placed=arrange(view_data,gap); names=list(placed); collisions=[]
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if overlaps(placed[a]["bbox"],placed[b]["bbox"]): collisions.append([a,b])
    if collisions: raise SystemExit(f"layout overlap detected: {collisions}")
    master=new_doc(); msp=master.document.modelspace(); text_h=max(maxdim*0.04,0.002)
    for v in names:
        vis,hid,_=view_data[v]; p=placed[v]
        add_shapes(master,v,shifted(vis,p["dx"],p["dy"]),shifted(hid,p["dx"],p["dy"]))
        box=p["bbox"]
        msp.add_text(v,dxfattribs={"layer":"0","style":"ARIAL","height":text_h}).set_placement((box["xmin"],box["ymax"]+text_h*0.4))
    master_path=outdir/f"{name}_MULTIVIEW.dxf"; master.document.saveas(master_path)
    qa={"source":str(src),"name":name,"gap_m":gap,"views":{},"collisions":collisions,"master":str(master_path),"layout":placed}
    for pth in sorted(outdir.glob(f"{name}_*.dxf")):
        d=ezdxf.readfile(pth); au=d.audit(); qa["views"][pth.name]={"entities":len(list(d.modelspace())),"audit_errors":len(au.errors)}
    (outdir/f"{name}_LAYOUT_QA.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    print(json.dumps(qa,indent=2))
if __name__=="__main__": main()
