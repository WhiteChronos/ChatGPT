from pipeline.layout_optimizer.infrastructure import build_cable_glands, build_din_rails, build_lower_zones, build_wireways
from pipeline.layout_optimizer.models import LayoutConfig, PanelGeometry, PhysicalInstance, Placement, ClearanceMM

def _panel():
    return PanelGeometry("P","R",400,500,250,350,450,20,40,30,20,100,4)

def test_lower_bands_are_distinct():
    z=build_lower_zones(_panel())
    assert z["cable_exit"].top<=z["bend_clearance"].y
    assert z["bend_clearance"].top<=z["lower_wireway"].y
    assert z["lower_wireway"].top<=z["terminal_access"].top

def test_din_rail_covers_devices():
    p=_panel(); cfg=LayoutConfig()
    inst={x.instance_id:x for x in [
        PhysicalInstance("A","A","A",1,"mounting_plate",40,40,10,ClearanceMM(),rail_required=True),
        PhysicalInstance("B","B","B",1,"mounting_plate",40,40,10,ClearanceMM(),rail_required=True)]}
    dev=[Placement("A","A","A","mounting_plate",20,200,40,40),Placement("B","B","B","mounting_plate",80,200,40,40)]
    rails,diags=build_din_rails(p,dev,inst,{"source_tag":"DIN","catalog_id":"DIN","quantity":2,"dimensions_mm":{"height":7.5}},cfg)
    assert not diags and rails and max(r.width_mm for r in rails)>=100

def test_cable_gland_overcrowding_is_diagnostic():
    glands,diags=build_cable_glands(_panel(),{"source_tag":"CG","catalog_id":"CG","quantity":50,"dimensions_mm":{"width":20,"height":20}},LayoutConfig())
    assert not glands and any("CABLE_GLAND_OVERCROWDING" in x for x in diags)
