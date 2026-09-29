from pipeline.layout_optimizer.export import apply_layout_to_project
from pipeline.layout_optimizer.models import LayoutMetrics, LayoutResult, LayoutStatus, Placement

def test_apply_layout_changes_coordinates_not_engineering_identity():
    project={"enclosure":{"external_mm":{"width":100,"height":100,"depth":50}},"render":{"visual_template_id":"LOCKED"},"placements":[{"li_tag":"A","instance_id":"A","catalog_id":"C","quantity":1,"surface":"mounting_plate","x_mm":1,"y_mm":1,"rotation_deg":0}]}
    result=LayoutResult("P","R",LayoutStatus.LAYOUT_VALIDATED,(Placement("A#01","A","C","mounting_plate",10,20,30,40),),LayoutMetrics(0,100,None,0,0,0,0,0),{},(),())
    out=apply_layout_to_project(project,result)
    assert out["placements"][0]["x_mm"]==10
    assert out["placements"][0]["catalog_id"]=="C"
    assert out["placements"][0]["quantity"]==1
    assert out["enclosure"]==project["enclosure"]
    assert out["render"]["visual_template_id"]=="LOCKED"
