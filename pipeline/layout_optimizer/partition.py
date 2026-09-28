from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
import networkx as nx
from .models import CapacityAlternative, LayoutConfig, LayoutStatus, PanelGeometry, PhysicalInstance

def build_dependency_graph(instances: Sequence[PhysicalInstance], links: Sequence[Mapping[str,Any]]) -> nx.Graph:
    g=nx.Graph()
    for i in instances: g.add_node(i.instance_id,source_tag=i.source_tag,group=i.functional_group)
    for l in links:
        a=str(l.get("a")); b=str(l.get("b"))
        if a in g and b in g: g.add_edge(a,b,kind=str(l.get("kind") or ""),mandatory=bool(l.get("mandatory")))
    return g

def validate_partition(graph: nx.Graph, partitions: Mapping[str,set[str]]) -> list[str]:
    owner={n:p for p,nodes in partitions.items() for n in nodes}
    errors=[]
    for a,b,d in graph.edges(data=True):
        if d.get("mandatory") and owner.get(a)!=owner.get(b):
            errors.append(f"MANDATORY_LINK_SEVERED:{a}:{b}")
    return errors

def _alt(kind:str,groups:Mapping[str,list[PhysicalInstance]],diagnostics:Sequence[str]=()) -> CapacityAlternative:
    panels=tuple({"panel_key":k,"instance_ids":[i.instance_id for i in v]} for k,v in groups.items() if v)
    return CapacityAlternative(f"SPLIT-{kind}",kind,LayoutStatus.USER_DECISION_REQUIRED,panels,{"panel_count":len(panels)},{"requires_new_li_revision":True,"inter_panel_links_required":True},tuple(diagnostics),True)

def generate_split_candidates(panel: PanelGeometry, instances: Sequence[PhysicalInstance], links: Sequence[Mapping[str,Any]], config: LayoutConfig) -> list[CapacityAlternative]:
    del panel,config
    g=build_dependency_graph(instances,links)
    out=[]
    by_group={}
    for i in instances: by_group.setdefault(i.functional_group or "other",[]).append(i)
    if len(by_group)>=2:
        groups={f"P{n+1}":vals for n,vals in enumerate(by_group.values())}
        parts={k:{i.instance_id for i in v} for k,v in groups.items()}
        errs=validate_partition(g,parts)
        if not errs: out.append(_alt("FUNCTIONAL_GROUP",groups))
    control=[i for i in instances if (i.functional_group or "") in {"control","controller","io","automation"}]
    power=[i for i in instances if i not in control]
    if control and power:
        groups={"CONTROL":control,"POWER":power}; errs=validate_partition(g,{k:{i.instance_id for i in v} for k,v in groups.items()})
        if not errs: out.append(_alt("POWER_CONTROL",groups))
    return out
