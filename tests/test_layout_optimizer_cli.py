from __future__ import annotations
import json
from pathlib import Path
from pipeline.layout_optimizer.cli import optimize_panel
from pipeline.layout_optimizer.models import LayoutStatus

def test_missing_dimension_returns_hold_input():
    li={"project_id":"P","revision":"R","status":"QUANTITY_FROZEN","lines":[{"tag":"A","catalog_id":"A","quantity":1,"unit":"un","render_required":True}]}
    bom={"lines":[{"li_tag":"A","catalog_id":"A","quantity":1,"unit":"un"}]}
    cat={"components":[{"catalog_id":"A","category":"device","dimensions_mm":None}]}
    project={"project":{"id":"P","revision":"R"},"enclosure":{"external_mm":{"width":100,"height":100,"depth":50},"mounting_plate_mm":{"width":90,"height":90},"minimum_free_reserve_percent":0},"layout":{"bottom_zone":{"cable_exit_height_mm":0,"lower_wireway_height_mm":0,"minimum_bend_clearance_mm":0,"terminal_zone_bottom_y_mm":0,"cable_glands_count":0}}}
    result=optimize_panel("P",li,bom,cat,project)
    assert result.status==LayoutStatus.HOLD_LAYOUT_INPUT
