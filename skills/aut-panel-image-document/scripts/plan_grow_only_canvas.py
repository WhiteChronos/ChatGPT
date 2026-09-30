#!/usr/bin/env python3
import argparse, json, sys

def main():
    ap=argparse.ArgumentParser(description="Plan a grow-only Step 6 engineering canvas")
    ap.add_argument("input_json"); ap.add_argument("output_json")
    a=ap.parse_args()
    with open(a.input_json,"r",encoding="utf-8") as f: data=json.load(f)
    margin=float(data.get("margin_px",40)); blocks=data.get("blocks",[])
    errors=[]; max_x=max_y=0.0
    for b in blocks:
        sx=float(b.get("scale_x",1.0)); sy=float(b.get("scale_y",1.0))
        if b.get("dimensional",False) and (abs(sx-1.0)>1e-9 or abs(sy-1.0)>1e-9):
            errors.append(f"{b.get('id')}: dimensional block scale must be 1.0")
        if abs(sx-sy)>1e-9:
            errors.append(f"{b.get('id')}: non-uniform scale forbidden")
        x=float(b.get("x",0)); y=float(b.get("y",0))
        w=float(b["width_px"])*sx; h=float(b["height_px"])*sy
        max_x=max(max_x,x+w); max_y=max(max_y,y+h)
    result={"status":"PASS" if not errors else "FAIL","canvas_width_px":int(max_x+margin),"canvas_height_px":int(max_y+margin),"errors":errors}
    with open(a.output_json,"w",encoding="utf-8") as f: json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
    sys.exit(0 if not errors else 2)
if __name__=="__main__": main()
