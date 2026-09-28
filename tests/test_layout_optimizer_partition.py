from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance, RectMM
from pipeline.layout_optimizer.partition import build_dependency_graph, generate_split_candidates, validate_partition

def _items():
    return [
        PhysicalInstance("PLC","PLC","PLC","controller",30,30,10,"mounting_plate",ClearanceMM(),functional_group="control"),
        PhysicalInstance("IO","IO","IO","io",30,30,10,"mounting_plate",ClearanceMM(),functional_group="control"),
        PhysicalInstance("VFD","VFD","VFD","drive",30,30,10,"mounting_plate",ClearanceMM(),functional_group="power"),
    ]

def test_dependency_partition_preserves_mandatory_links():
    g=build_dependency_graph(_items(),[{"a":"PLC","b":"IO","kind":"controller_io","mandatory":True}])
    errors=validate_partition(g,{"P1":{"PLC"},"P2":{"IO","VFD"}})
    assert errors

def test_split_candidates_never_auto_select_winner():
    panel=PanelGeometry("P","R",RectMM("e","external",0,0,100,100),RectMM("m","mounting_plate",0,0,90,90),RectMM("d","door",0,0,100,100),0,0)
    alts=generate_split_candidates(panel,_items(),[],LayoutConfig(max_time_seconds=2))
    assert all(a.requires_user_decision for a in alts)
    assert all(a.status=="USER_DECISION_REQUIRED" for a in alts)
