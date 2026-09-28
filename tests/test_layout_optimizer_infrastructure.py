from pipeline.layout_optimizer.infrastructure import build_cable_glands, build_din_rails, build_terminal_strips, build_wireways
from pipeline.layout_optimizer.models import LayoutStatus, PanelGeometry, Placement, RectMM

def _panel():
    return PanelGeometry(panel_id="P",revision="R",external=RectMM("e","external",0,0,400,500),mounting_plate=RectMM("m","mounting_plate",0,0,350,450),door=RectMM("d","door",0,0,400,500),reserve_percent=20,bottom_zone_height=100)

def test_infrastructure_uses_distinct_lower_bands():
    panel=_panel()
    terms,td=build_terminal_strips(panel,{"terminal":[{"source_tag":"XT","quantity":8}]})
    ways,wd=build_wireways(panel,{"wireway":[{"source_tag":"WD","quantity":2}]})
    glands,gd,status=build_cable_glands(panel,{"cable_gland":[{"source_tag":"CG","quantity":4}]})
    assert status is None
    assert terms and ways and glands
    assert min(x.y_mm for x in terms) > max(x.y_mm for x in glands)

def test_din_rails_cover_mounted_devices():
    panel=_panel()
    devices=[Placement("A","A","mounting_plate",20,200,40,40),Placement("B","B","mounting_plate",80,200,40,40)]
    rails=build_din_rails(panel,devices,{"din_rail":[{"source_tag":"DIN","quantity":2}]})
    assert rails and max(r.width_mm for r in rails)>=100
