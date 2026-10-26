#!/usr/bin/env python3
import argparse, json, sys
import ezdxf

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("dxf"); a=ap.parse_args()
    doc=ezdxf.readfile(a.dxf); audit=doc.audit(); styles=set()
    for layout in doc.layouts:
        for e in layout:
            if e.dxftype() in {"TEXT","MTEXT","ATTRIB","ATTDEF"}:
                styles.add(getattr(e.dxf,"style",""))
    print(json.dumps({
        "file":a.dxf,
        "dxfversion":doc.dxfversion,
        "insunits":int(doc.header.get("$INSUNITS",0) or 0),
        "modelspace_entities":len(list(doc.modelspace())),
        "audit_errors":len(audit.errors),
        "audit_fixes":len(audit.fixes),
        "text_styles":sorted(styles),
        "arial_style_present":"ARIAL" in doc.styles
    },indent=2,ensure_ascii=False))
    return 1 if audit.has_errors else 0

if __name__=="__main__": raise SystemExit(main())
