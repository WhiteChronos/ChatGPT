from pipeline.layout_optimizer.capacity import find_larger_enclosure_candidates
from pipeline.layout_optimizer.cli import choose_enclosure_candidate
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


def test_choose_enclosure_candidate_selects_smallest_feasible_without_mutating_source():
    panel=PanelGeometry("P","R",100,100,50,80,80)
    items=[
        PhysicalInstance("A","A","A",1,"mounting_plate",70,70,10,ClearanceMM()),
        PhysicalInstance("B","B","B",1,"mounting_plate",70,70,10,ClearanceMM())
    ]
    enclosures={"components":[
        {"category":"enclosure","catalog_id":"BIG2","external_mm":{"width":260,"height":140,"depth":100},"mounting_plate_mm":{"width":240,"height":120}},
        {"category":"enclosure","catalog_id":"BIG1","external_mm":{"width":220,"height":120,"depth":100},"mounting_plate_mm":{"width":200,"height":100}}
    ]}
    before=(panel.enclosure_width_mm,panel.enclosure_height_mm,panel.enclosure_depth_mm)
    result=choose_enclosure_candidate(panel,items,enclosures,LayoutConfig(max_time_seconds=2))
    assert result is not None
    assert result["change_type"]=="ENCLOSURE_CHANGE"
    assert result["enclosure_catalog_id"]=="BIG1"
    assert result["requires_candidate_revision"] is True
    assert (panel.enclosure_width_mm,panel.enclosure_height_mm,panel.enclosure_depth_mm)==before


def test_choose_enclosure_candidate_returns_none_without_validated_alternative():
    panel=PanelGeometry("P","R",100,100,50,80,80,minimum_free_reserve_percent=95)
    items=[PhysicalInstance("A","A","A",1,"mounting_plate",70,70,10,ClearanceMM())]
    enclosures={"components":[]}
    assert choose_enclosure_candidate(panel,items,enclosures,LayoutConfig(max_time_seconds=2)) is None
