from __future__ import annotations
import copy, json
from pathlib import Path
from typing import Any, Mapping
from .models import LayoutResult

def export_layout_result(result: LayoutResult, output: Path) -> Path:
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result.to_dict(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return output

def apply_layout_to_project(project: Mapping[str,Any], result: LayoutResult) -> dict[str,Any]:
    out=copy.deepcopy(project)
    by_tag={}
    for p in result.placements:
        if p.kind!="component": continue
        by_tag.setdefault(p.source_tag,p)
    for row in out.get("placements",[]):
        p=by_tag.get(str(row.get("li_tag") or ""))
        if not p: continue
        if str(row.get("catalog_id") or "")!=p.catalog_id: raise ValueError(f"CATALOG_ID_MISMATCH:{p.source_tag}")
        row["x_mm"]=p.x_mm; row["y_mm"]=p.y_mm; row["rotation_deg"]=p.rotation_deg
    out.setdefault("layout_optimizer",{})["result"]=result.to_dict()
    return out
