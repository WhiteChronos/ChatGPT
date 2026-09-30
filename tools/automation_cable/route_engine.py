from dataclasses import dataclass
from typing import Iterable, Sequence
@dataclass(frozen=True)
class Segment:
    segment_id:str; drawing_length:float; scale_denominator:float=1.0
    @property
    def real_length(self):
        if self.drawing_length<0 or self.scale_denominator<=0: raise ValueError("invalid length or scale")
        return self.drawing_length*self.scale_denominator
def route_length(segments:Iterable[Segment]): return sum(s.real_length for s in segments)
def physical_containment_total(routes):
    seen={}
    for route in routes:
        for s in route:
            if s.segment_id in seen and abs(seen[s.segment_id].real_length-s.real_length)>1e-9: raise ValueError("conflicting segment")
            seen[s.segment_id]=s
    return sum(s.real_length for s in seen.values())
def cumulative_cable_total(cable_routes): return sum(route_length(r) for r in cable_routes)
def hart_cable_count(endpoint_ids):
    if len(set(endpoint_ids))!=len(endpoint_ids): raise ValueError("endpoint ids must be unique")
    return len(endpoint_ids)
def digital_cascade_length(chain_segments): return route_length(chain_segments)
