from pipeline.layout_optimizer.models import ClearanceMM, LayoutConfig, LayoutStatus, PanelGeometry, PhysicalInstance
from pipeline.layout_optimizer.solver import solve_single_panel

def _panel():
    return PanelGeometry("P1","R1",120,120,60,100,100)

def _item(name,w=20,h=20):
    return PhysicalInstance(name,name,name,1,"mounting_plate",w,h,10,ClearanceMM())

def test_easy_fit_is_deterministic():
    cfg=LayoutConfig(solver_seed=7,max_time_seconds=2,coordinate_resolution_mm=1)
    r1=solve_single_panel(_panel(),[_item("A"),_item("B")],[],cfg)
    r2=solve_single_panel(_panel(),[_item("A"),_item("B")],[],cfg)
    assert r1.status in {LayoutStatus.LAYOUT_FEASIBLE,LayoutStatus.LAYOUT_VALIDATED}
    assert [(p.instance_id,p.x_mm,p.y_mm) for p in r1.placements]==[(p.instance_id,p.x_mm,p.y_mm) for p in r2.placements]

def test_proven_infeasible_is_capacity_hold():
    r=solve_single_panel(_panel(),[_item("A",80,80),_item("B",80,80)],[],LayoutConfig(max_time_seconds=2))
    assert r.status==LayoutStatus.HOLD_LAYOUT_CAPACITY

def test_zero_time_is_timeout_not_capacity():
    r=solve_single_panel(_panel(),[_item("A")],[],LayoutConfig(max_time_seconds=0))
    assert r.status==LayoutStatus.HOLD_LAYOUT_SOLVER_TIMEOUT
