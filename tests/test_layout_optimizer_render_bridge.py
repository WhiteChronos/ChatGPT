from pipeline.layout_optimizer.export import apply_layout_to_project
from pipeline.layout_optimizer.models import LayoutMetrics, LayoutResult, LayoutStatus, Placement
from pipeline.render_panel_scaled import apply_validated_optimizer_layout

def test_render_bridge_accepts_only_validated_optimizer_result():
    project={"placements":[{"li_tag":"A","instance_id":"A","catalog_id":"C","quantity":1,"surface":"mounting_plate","x_mm":1,"y_mm":1,"rotation_deg":0}]}
    good=LayoutResult("P","R",LayoutStatus.LAYOUT_VALIDATED,(Placement("A#01","A","C","mounting_plate",10,20,30,40),),LayoutMetrics(0,100,None,0,0,0,0,0),{},(),()).to_dict()
    out=apply_validated_optimizer_layout(project,good)
    assert out["placements"][0]["x_mm"]==10
    bad=dict(good); bad["status"]="HOLD_LAYOUT_CAPACITY"
    try:
        apply_validated_optimizer_layout(project,bad)
    except RuntimeError as exc:
        assert "LAYOUT_VALIDATED" in str(exc)
    else:
        raise AssertionError("bridge accepted non-validated optimizer result")


def test_standard_pipeline_can_run_optimizer_after_bom(tmp_path):
    import json
    from pipeline import aut_panel_standard as std
    project={"project":{"id":"P","revision":"R"},"enclosure":{"external_mm":{"width":120,"height":120,"depth":60},"mounting_plate_mm":{"width":100,"height":100},"minimum_free_reserve_percent":0},"layout":{"bottom_zone":{"cable_exit_height_mm":0,"lower_wireway_height_mm":0,"minimum_bend_clearance_mm":0,"terminal_zone_bottom_y_mm":0,"cable_glands_count":0}}}
    li={"project_id":"P","revision":"R","status":"QUANTITY_FROZEN","lines":[{"tag":"A","catalog_id":"C","quantity":1,"unit":"un","render_required":True}]}
    bom_path=tmp_path/"bom.json"
    bom_path.write_text(json.dumps({"lines":[{"li_tag":"A","catalog_id":"C","quantity":1,"unit":"un"}]}),encoding="utf-8")
    cat={"components":[{"catalog_id":"C","category":"device","dimensions_mm":{"width":20,"height":20,"depth":10},"clearance_mm":{}}]}
    out=tmp_path/"optimizer.json"
    result=std.gerar_layout_otimizado(project,cat,li,bom_path,out)
    assert result.status.value=="LAYOUT_VALIDATED"
    assert out.exists()
