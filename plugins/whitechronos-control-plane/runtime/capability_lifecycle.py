from __future__ import annotations

from collections import defaultdict

from .capability_model import CapabilityManifest, LifecycleEvent, ProviderLifecycleView


def derive_lifecycle_view(
    providers: dict[tuple[str, str], CapabilityManifest],
    events: tuple[LifecycleEvent, ...],
) -> dict[tuple[str, str], ProviderLifecycleView]:
    by_id = {event.event_id: event for event in events}
    if len(by_id) != len(events):
        raise ValueError("duplicate lifecycle event id")

    grouped: dict[tuple[str, str], list[LifecycleEvent]] = defaultdict(list)
    for event in events:
        key = (event.provider_id, event.implementation_version)
        if key not in providers:
            raise ValueError(f"lifecycle event references missing provider: {event.provider_id}@{event.implementation_version}")
        grouped[key].append(event)

    for event in events:
        predecessor_id = event.predecessor_event_id
        if predecessor_id is None:
            continue
        predecessor = by_id.get(predecessor_id)
        if predecessor is None:
            raise ValueError(f"missing predecessor event: {predecessor_id}")
        if (predecessor.provider_id, predecessor.implementation_version) != (
            event.provider_id,
            event.implementation_version,
        ):
            raise ValueError(f"cross-provider predecessor link: {predecessor_id} -> {event.event_id}")

    result: dict[tuple[str, str], ProviderLifecycleView] = {}
    for key, provider_events in grouped.items():
        roots = [event for event in provider_events if event.predecessor_event_id is None]
        if len(roots) != 1:
            raise ValueError(f"provider lifecycle must have exactly one root: {key!r}")

        successors: dict[str, LifecycleEvent] = {}
        for event in provider_events:
            predecessor_id = event.predecessor_event_id
            if predecessor_id is None:
                continue
            if predecessor_id in successors:
                raise ValueError(f"branching lifecycle history after {predecessor_id}")
            successors[predecessor_id] = event

        visited: set[str] = set()
        current = roots[0]
        while True:
            if current.event_id in visited:
                raise ValueError(f"cycle in lifecycle history at {current.event_id}")
            visited.add(current.event_id)
            next_event = successors.get(current.event_id)
            if next_event is None:
                break
            current = next_event

        if len(visited) != len(provider_events):
            unreachable = sorted(event.event_id for event in provider_events if event.event_id not in visited)
            raise ValueError(f"cycle or unreachable lifecycle events: {', '.join(unreachable)}")

        result[key] = ProviderLifecycleView(
            provider_id=key[0],
            implementation_version=key[1],
            current_state=current.state,
            last_event_id=current.event_id,
            event_count=len(provider_events),
        )

    return result
