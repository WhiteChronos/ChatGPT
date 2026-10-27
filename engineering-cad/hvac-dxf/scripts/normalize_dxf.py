#!/usr/bin/env python3
import argparse
from pathlib import Path
import ezdxf
from ezdxf import units
from ezdxf.transform import inplace
from ezdxf.math import Matrix44

ap=argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--source-units",choices=["m","mm","cm","in"])
a=ap.parse_args()
doc=ezdxf.readfile(a.src)
factor={"m":1.0,"mm":0.001,"cm":0.01,"in":0.0254}.get(a.source_units)
if factor and factor != 1.0:
    M=Matrix44.scale(factor,factor,factor)
    inplace(doc.modelspace(),M)
    for block in doc.blocks:
        if not block.name.startswith("*"): inplace(block,M)
doc.header["$INSUNITS"]=units.M
if "ARIAL" not in doc.styles: doc.styles.add("ARIAL",font="Arial.ttf")
for layout in doc.layouts:
    for e in layout:
        if e.dxftype() in {"TEXT","MTEXT","ATTRIB","ATTDEF"}:
            try: e.dxf.style="ARIAL"
            except Exception: pass
Path(a.dst).parent.mkdir(parents=True,exist_ok=True)
doc.saveas(a.dst)
