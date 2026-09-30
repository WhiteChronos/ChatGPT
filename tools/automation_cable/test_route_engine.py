from route_engine import *
a=Segment("A",1,50); b=Segment("B",.2,50); c=Segment("C",.3,50)
assert route_length([a,b])==60
assert physical_containment_total([[a,b],[a,c]])==75
assert cumulative_cable_total([[a,b],[a,c]])==125
assert hart_cable_count(["AT-001","TT-001"])==2
assert digital_cascade_length([a,b,c])==75
print("route_engine tests passed")
