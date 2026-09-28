from pipeline.layout_optimizer.geometry import expanded_rect, inside, overlaps
from pipeline.layout_optimizer.models import ClearanceMM, RectMM

def test_geometry_exact_touch_is_not_overlap():
    a=RectMM("a","mounting_plate",0,0,10,10)
    b=RectMM("b","mounting_plate",10,0,10,10)
    assert not overlaps(a,b)
    assert inside(a,RectMM("bound","mounting_plate",0,0,20,20))

def test_clearance_expansion():
    r=RectMM("a","mounting_plate",10,10,10,10)
    e=expanded_rect(r,ClearanceMM(left=2,right=3,bottom=4,top=5))
    assert (e.x,e.y,e.width,e.height)==(8,6,15,19)
