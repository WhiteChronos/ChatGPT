from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
import networkx as nx
from .metrics import validate_layout_result
from .models import CapacityAlternative, LayoutConfig, LayoutStatus, PanelGeometry, PhysicalInstance
from .solver import solve_single_panel

def build_dependency_graph(instances: Sequence[PhysicalInstance], links: Sequence[Mapping[str,Any]]) -> nx.Graph:
    g=nx.Graph()
    for i in instances:
        g.add_node(i.instance_id,source_tag=i.source_tag,group=i.functional_group)
    for l in links:
        a=str(l.get("a")); b=str(l.get("b"))
        if a in g and b in g:
            g.add_edge(a,b,kind=str(l.get("kind") or ""),mandatory=bool(l.get("mandatory")))
    return g

def validate_partition(graph: nx.Graph, partitions: Mapping[str,set[str]]) -> list[str]:
    owner={n:p for p,nodes in partitions.items() for n in nodes}
    errors=[]
    for a,b,d in graph.edges(data=True):
        if d.get("mandatory") and owner.get(a)!=owner.get(b):
            errors.append(f"MANDATORY_LINK_SEVERED:{a}:{b}")
    return errors

def _solve_groups(panel: PanelGeometry, groups: Mapping[str,list[PhysicalInstance]], graph: nx.Graph, config: LayoutConfig, kind: str) -> CapacityAlternative | None:
    parts={k:{i.instance_id for i in v} for k,v in groups.items() if v}
    errors=validate_partition(graph,parts)
    if errors:
        return None
    child_panels=[]
    for key,items in sorted(groups.items()):
        if not items:
            continue
        solved=solve_single_panel(panel,items,[],config)
        validated=validate_layout_result(panel,solved)
        if validated.status!=LayoutStatus.LAYOUT_VALIDATED:
            return None
        child_panels.append({
            "panel_key":key,
            "instance_ids":[i.instance_id for i in items],
            "layout_status":validated.status.value,
            "metrics":validated.metrics.__dict__,
        })
    owner={n:p for p,nodes in parts.items() for n in nodes}
    crossings=[]
    for a,b,d in graph.edges(data=True):
        if owner.get(a)!=owner.get(b):
            crossings.append({"a":a,"b":b,"kind":d.get("kind"),"mandatory":bool(d.get("mandatory"))})
    return CapacityAlternative(
        alternative_id=f"SPLIT-{kind}",
        alternative_type=kind,
        status=LayoutStatus.USER_DECISION_REQUIRED,
        panels=tuple(child_panels),
        metrics={"panel_count":len(child_panels),"inter_panel_link_count":len(crossings)},
        impacts={"requires_new_li_revision":True,"inter_panel_links":crossings},
        diagnostics=(),
        requires_user_decision=True,
    )

def generate_split_candidates(panel: PanelGeometry, instances: Sequence[PhysicalInstance], links: Sequence[Mapping[str,Any]], config: LayoutConfig) -> list[CapacityAlternative]:
    g=build_dependency_graph(instances,links)
    candidates=[]
    by_group={}
    for i in instances:
        by_group.setdefault(i.functional_group or "other",[]).append(i)
    if len(by_group)>=2:
        groups={f"GROUP-{k}":v for k,v in sorted(by_group.items())}
        alt=_solve_groups(panel,groups,g,config,"FUNCTIONAL_GROUP")
        if alt: candidates.append(alt)
    control=[i for i in instances if (i.functional_group or "") in {"control","controller","io","automation"}]
    power=[i for i in instances if i not in control]
    if control and power:
        alt=_solve_groups(panel,{"CONTROL":control,"POWER":power},g,config,"POWER_CONTROL")
        if alt and all(x.alternative_id!=alt.alternative_id for x in candidates):
            candidates.append(alt)
    return candidates
