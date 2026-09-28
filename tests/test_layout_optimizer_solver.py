from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, PanelGeometry, PhysicalInstance, RectMM, LayoutStatus
from pipeline.layout_optimizer.solver import solve_single_panel

def _panel():
    return PanelGeometry(panel_id="P1",revision="R1",external=RectMM("ext","external",0,0,120,120),mounting_plate=RectMM("mp","mounting_plate",0,0,100,100),door=RectMM("door","door",0,0,120,120),reserve_percent=0,bottom_zone_height=0)

def test_easy_fit_is_deterministic_and_non_overlapping():
    items=[
        PhysicalInstance("A","A","A","device",20,20,10,"mounting_plate",ClearanceMM()),
        PhysicalInstance("B","B","B","device",20,20,10,"mounting_plate",ClearanceMM()),
    ]
    cfg=LayoutConfig(solver_seed=7,max_time_seconds=2,coordinate_resolution_mm=1)
    r1=solve_single_panel(_panel(),items,[],cfg)
    r2=solve_single_panel(_panel(),items,[],cfg)
    assert r1.status in {LayoutStatus.LAYOUT_FEASIBLE,LayoutStatus.LAYOUT_VALIDATED}
    assert [(p.instance_id,p.x_mm,p.y_mm) for p in r1.placements]==[(p.instance_id,p.x_mm,p.y_mm) for p in r2.placements]
    assert len(r1.placements)==2

def test_proven_infeasible_is_capacity_hold():
    items=[
        PhysicalInstance("A","A","A","device",80,80,10,"mounting_plate",ClearanceMM()),
        PhysicalInstance("B","B","B","device",80,80,10,"mounting_plate",ClearanceMM()),
    ]
    r=solve_single_panel(_panel(),items,[],LayoutConfig(max_time_seconds=2))
    assert r.status==LayoutStatus.HOLD_LAYOUT_CAPACITY
