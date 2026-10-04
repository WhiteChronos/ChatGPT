#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
import ezdxf

ap=argparse.ArgumentParser()
ap.add_argument("dxf", nargs="+")
ap.add_argument("--json", action="store_true")
args=ap.parse_args()
rows=[]; bad=0
for item in args.dxf:
    p=Path(item); rec={"file":str(p),"ok":False}
    try:
        doc=ezdxf.readfile(p); auditor=doc.audit()
        rec.update(ok=not auditor.has_errors,dxfversion=doc.dxfversion,
                   insunits=int(doc.header.get("$INSUNITS",0) or 0),
                   modelspace_entities=len(list(doc.modelspace())),
                   audit_errors=len(auditor.errors),audit_fixes=len(auditor.fixes),
                   blocks=len(doc.blocks))
        bad += int(auditor.has_errors)
    except Exception as e:
        rec["error"]=str(e); bad+=1
    rows.append(rec)
print(json.dumps(rows,indent=2,ensure_ascii=False) if args.json else "\n".join(map(str,rows)))
sys.exit(1 if bad else 0)
