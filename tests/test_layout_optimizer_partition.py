from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance
from pipeline.layout_optimizer.partition import build_dependency_graph, generate_split_candidates, validate_partition

def _items():
    return [
        PhysicalInstance("PLC","PLC","PLC",1,"mounting_plate",30,30,10,ClearanceMM(),functional_group="control"),
        PhysicalInstance("IO","IO","IO",1,"mounting_plate",30,30,10,ClearanceMM(),functional_group="control"),
        PhysicalInstance("VFD","VFD","VFD",1,"mounting_plate",30,30,10,ClearanceMM(),functional_group="power"),
    ]

def test_dependency_partition_preserves_mandatory_links():
    g=build_dependency_graph(_items(),[{"a":"PLC","b":"IO","kind":"controller_io","mandatory":True}])
    assert validate_partition(g,{"P1":{"PLC"},"P2":{"IO","VFD"}})

def test_split_candidates_never_auto_select_winner():
    panel=PanelGeometry("P","R",100,100,50,90,90)
    alts=generate_split_candidates(panel,_items(),[],LayoutConfig(max_time_seconds=2))
    assert alts
    assert all(a.requires_user_decision for a in alts)
    assert all(a.status.value=="USER_DECISION_REQUIRED" for a in alts)


def test_split_candidate_contains_solved_child_panel_status():
    panel=PanelGeometry("P","R",100,100,50,80,80)
    alts=generate_split_candidates(panel,_items(),[],LayoutConfig(max_time_seconds=2))
    assert alts
    assert all(all(p["layout_status"]=="LAYOUT_VALIDATED" for p in a.panels) for a in alts)
