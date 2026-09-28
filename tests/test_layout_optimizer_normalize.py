from pipeline.layout_optimizer.models import LayoutConfig
from pipeline.layout_optimizer.normalize import normalize_inputs

def _base():
    li={"project_id":"P1","revision":"R1","status":"QUANTITY_FROZEN","lines":[
        {"tag":"BAT-01A/B","catalog_id":"BAT","quantity":2,"unit":"un","render_required":True},
        {"tag":"HMI-01","catalog_id":"HMI","quantity":1,"unit":"un","render_required":True},
        {"tag":"DIN-01..02","catalog_id":"DIN","quantity":2,"unit":"un","render_required":True}]}
    bom={"lines":[
        {"li_tag":"BAT-01A/B","catalog_id":"BAT","quantity":2,"unit":"un"},
        {"li_tag":"HMI-01","catalog_id":"HMI","quantity":1,"unit":"un"},
        {"li_tag":"DIN-01..02","catalog_id":"DIN","quantity":2,"unit":"un"}]}
    cat={"components":[
        {"catalog_id":"BAT","category":"battery","dimensions_mm":{"width":50,"height":80,"depth":40},"clearance_mm":{}},
        {"catalog_id":"HMI","category":"hmi","dimensions_mm":{"width":100,"height":70,"depth":30},"clearance_mm":{}},
        {"catalog_id":"DIN","category":"din_rail","dimensions_mm":{"width":100,"height":8,"depth":7.5},"clearance_mm":{}}]}
    project={"project":{"id":"P1","revision":"R1"},"enclosure":{"external_mm":{"width":400,"height":500,"depth":250},"mounting_plate_mm":{"width":350,"height":450},"minimum_free_reserve_percent":20},"layout":{"bottom_zone":{"cable_exit_height_mm":40,"lower_wireway_height_mm":30,"minimum_bend_clearance_mm":20,"terminal_zone_bottom_y_mm":100,"cable_glands_count":4}}}
    return li,bom,cat,project

def test_grouped_quantity_expands_and_hmi_stays_door():
    li,bom,cat,project=_base()
    panel,instances,infra,diags=normalize_inputs("P1",li,bom,cat,project,LayoutConfig())
    assert not diags
    ids=[x.instance_id for x in instances]
    assert "BAT-01A/B#01" in ids and "BAT-01A/B#02" in ids
    assert next(x for x in instances if x.source_tag=="HMI-01").surface=="door"
    assert infra["din_rail"][0]["source_tag"]=="DIN-01..02"
    assert panel.plate_width_mm==350

def test_missing_dimensions_is_hold_input():
    li,bom,cat,project=_base(); cat["components"][0]["dimensions_mm"]=None
    _,instances,_,diags=normalize_inputs("P1",li,bom,cat,project,LayoutConfig())
    assert "MISSING_DIMENSIONS:BAT" in diags
    assert all(x.catalog_id!="BAT" for x in instances)
