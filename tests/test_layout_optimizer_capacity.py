from pipeline.layout_optimizer.capacity import find_larger_enclosure_candidates
from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance

def test_larger_enclosure_candidates_require_user_decision():
    panel=PanelGeometry("P","R",100,100,50,80,80)
    items=[
        PhysicalInstance("A","A","A",1,"mounting_plate",70,70,10,ClearanceMM()),
        PhysicalInstance("B","B","B",1,"mounting_plate",70,70,10,ClearanceMM())
    ]
    enclosures=[{"catalog_id":"BIG","external_mm":{"width":220,"height":120,"depth":100},"mounting_plate_mm":{"width":200,"height":100}}]
    alts=find_larger_enclosure_candidates(panel,items,enclosures,LayoutConfig(max_time_seconds=2))
    assert alts
    assert all(a.requires_user_decision for a in alts)
    assert all(a.status.value=="USER_DECISION_REQUIRED" for a in alts)


def test_larger_enclosure_candidate_must_satisfy_reserve():
    panel=PanelGeometry("P","R",100,100,50,80,80,minimum_free_reserve_percent=60)
    items=[PhysicalInstance("A","A","A",1,"mounting_plate",70,70,10,ClearanceMM())]
    enclosures=[{"catalog_id":"TIGHT","external_mm":{"width":120,"height":120,"depth":100},"mounting_plate_mm":{"width":100,"height":100}}]
    alts=find_larger_enclosure_candidates(panel,items,enclosures,LayoutConfig(max_time_seconds=2))
    assert alts==[]
