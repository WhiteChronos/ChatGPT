from pipeline.layout_optimizer.capacity import find_larger_enclosure_candidates
from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance, RectMM

def test_larger_enclosure_candidates_require_user_decision():
    panel=PanelGeometry("P","R",RectMM("e","external",0,0,100,100),RectMM("m","mounting_plate",0,0,80,80),RectMM("d","door",0,0,100,100),0,0)
    items=[PhysicalInstance("A","A","A","device",70,70,10,"mounting_plate",ClearanceMM()),PhysicalInstance("B","B","B","device",70,70,10,"mounting_plate",ClearanceMM())]
    enclosures=[{"catalog_id":"BIG","external_mm":{"width":220,"height":120,"depth":100},"mounting_plate_mm":{"width":200,"height":100}}]
    alts=find_larger_enclosure_candidates(panel,items,enclosures,LayoutConfig(max_time_seconds=2))
    assert alts
    assert all(a.requires_user_decision for a in alts)
    assert all(a.status=="USER_DECISION_REQUIRED" for a in alts)
