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
