from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from .capability_model import CapabilityRegistry, LifecycleState, validate_capability_id, validate_provider_id, validate_semver
from .capability_versioning import SemVer, VersionRange


ProviderKey = tuple[str, str]
AdapterKey = tuple[str, str]
ContractKey = tuple[str, str]


class ResolutionError(ValueError):
    pass


class NoCompatibleProvider(ResolutionError):
    pass


class PinnedProviderUnavailable(ResolutionError):
    pass


@dataclass(frozen=True)
class ResolutionRequest:
    contract_id: str
    version_range: str
    provider_pin: ProviderKey | None = None
    preferred_provider_ids: tuple[str, ...] = ()
    allow_adapters: bool = True
    allow_lossy_adapters: bool = False

    def __post_init__(self) -> None:
        validate_capability_id(self.contract_id)
        VersionRange.parse(self.version_range)
        if self.provider_pin is not None:
            validate_provider_id(self.provider_pin[0])
            validate_semver(self.provider_pin[1], label="provider pin implementation_version")
        for provider_id in self.preferred_provider_ids:
            validate_provider_id(provider_id)


@dataclass(frozen=True)
class ResolutionDecision:
    requested_contract_id: str
    requested_version_range: str
    selected_consumer_contract_version: str
    provider_id: str
    implementation_version: str
    provider_contract_id: str
    provider_contract_version: str
    adapter_chain: tuple[AdapterKey, ...]
    candidate_count: int
    selection_reason: str


@dataclass(frozen=True)
class _Candidate:
    provider_id: str
    implementation_version: str
    consumer_contract_version: str
    provider_contract_id: str
    provider_contract_version: str
    adapter_chain: tuple[AdapterKey, ...] = ()
    lossy_count: int = 0


def _is_active(registry: CapabilityRegistry, key: ProviderKey) -> bool:
    view = registry.lifecycle.get(key)
    return view is not None and view.current_state is LifecycleState.ACTIVE


def _preferred_rank(request: ResolutionRequest, provider_id: str) -> int:
    try:
        return request.preferred_provider_ids.index(provider_id)
    except ValueError:
        return len(request.preferred_provider_ids) + 1


def _order_candidates(candidates: list[_Candidate], request: ResolutionRequest) -> list[_Candidate]:
    ordered = list(candidates)
    # Stable sorts, from least-significant tie breaker to most significant.
    # Exact version strings break ties when SemVer precedence is equal (for example, build metadata).
    ordered.sort(
        key=lambda item: (
            item.consumer_contract_version,
            item.provider_contract_version,
            item.implementation_version,
        )
    )
    ordered.sort(key=lambda item: item.provider_id)
    ordered.sort(key=lambda item: item.adapter_chain)
    ordered.sort(key=lambda item: SemVer.parse(item.implementation_version), reverse=True)
    ordered.sort(key=lambda item: SemVer.parse(item.provider_contract_version), reverse=True)
    ordered.sort(key=lambda item: SemVer.parse(item.consumer_contract_version), reverse=True)
    ordered.sort(key=lambda item: _preferred_rank(request, item.provider_id))
    ordered.sort(key=lambda item: item.lossy_count)
    ordered.sort(key=lambda item: len(item.adapter_chain))
    ordered.sort(key=lambda item: 0 if not item.adapter_chain else 1)
    return ordered


def _direct_candidates(registry: CapabilityRegistry, request: ResolutionRequest) -> list[_Candidate]:
    version_range = VersionRange.parse(request.version_range)
    candidates: list[_Candidate] = []
    for provider_key, manifest in registry.providers.items():
        if not _is_active(registry, provider_key):
            continue
        for provided in manifest.provides:
            if provided.contract_id != request.contract_id:
                continue
            if not version_range.matches(provided.version):
                continue
            candidates.append(
                _Candidate(
                    provider_id=manifest.provider_id,
                    implementation_version=manifest.implementation_version,
                    consumer_contract_version=provided.version,
                    provider_contract_id=provided.contract_id,
                    provider_contract_version=provided.version,
                )
            )
    return candidates


def _providers_for_node(registry: CapabilityRegistry, node: ContractKey) -> list[tuple[ProviderKey, object]]:
    matches: list[tuple[ProviderKey, object]] = []
    for provider_key, manifest in registry.providers.items():
        if not _is_active(registry, provider_key):
            continue
        if any((provided.contract_id, provided.version) == node for provided in manifest.provides):
            matches.append((provider_key, manifest))
    return matches


def _adapter_candidates(registry: CapabilityRegistry, request: ResolutionRequest) -> list[_Candidate]:
    if not request.allow_adapters:
        return []

    requested_range = VersionRange.parse(request.version_range)
    start_nodes = sorted(
        (
            key
            for key in registry.contracts
            if key[0] == request.contract_id and requested_range.matches(key[1])
        ),
        key=lambda key: (key[0], SemVer.parse(key[1])),
    )
    if not start_nodes:
        return []

    adjacency: dict[ContractKey, list[tuple[AdapterKey, object]]] = {}
    for adapter_key, adapter in registry.adapters.items():
        implementation_key = (adapter.implementation_provider_id, adapter.implementation_version)
        if not _is_active(registry, implementation_key):
            continue
        if adapter.is_lossy and not request.allow_lossy_adapters:
            continue
        adjacency.setdefault(adapter.source_key, []).append((adapter_key, adapter))
    for edges in adjacency.values():
        edges.sort(key=lambda item: item[0])

    candidates: list[_Candidate] = []
    for start_node in start_nodes:
        queue = deque([(start_node, (), 0, frozenset({start_node}))])
        while queue:
            node, chain, lossy_count, visited = queue.popleft()
            if chain:
                for _provider_key, manifest in _providers_for_node(registry, node):
                    candidates.append(
                        _Candidate(
                            provider_id=manifest.provider_id,
                            implementation_version=manifest.implementation_version,
                            consumer_contract_version=start_node[1],
                            provider_contract_id=node[0],
                            provider_contract_version=node[1],
                            adapter_chain=chain,
                            lossy_count=lossy_count,
                        )
                    )
            for adapter_key, adapter in adjacency.get(node, ()):
                target = adapter.target_key
                if target in visited:
                    continue
                queue.append(
                    (
                        target,
                        chain + (adapter_key,),
                        lossy_count + (1 if adapter.is_lossy else 0),
                        visited | {target},
                    )
                )
    return candidates


def resolve_capability(
    registry: CapabilityRegistry,
    request: ResolutionRequest,
) -> ResolutionDecision:
    candidates = _direct_candidates(registry, request)
    candidates.extend(_adapter_candidates(registry, request))

    if request.provider_pin is not None:
        candidates = [
            candidate
            for candidate in candidates
            if (candidate.provider_id, candidate.implementation_version) == request.provider_pin
        ]
        if not candidates:
            raise PinnedProviderUnavailable(
                f"pinned provider is not structurally eligible: {request.provider_pin[0]}@{request.provider_pin[1]}"
            )

    if not candidates:
        raise NoCompatibleProvider(
            f"no ACTIVE provider satisfies {request.contract_id} {request.version_range!r}"
        )

    ordered = _order_candidates(candidates, request)
    winner = ordered[0]
    preferred_rank = _preferred_rank(request, winner.provider_id)
    route_class = "DIRECT" if not winner.adapter_chain else "ADAPTED"
    return ResolutionDecision(
        requested_contract_id=request.contract_id,
        requested_version_range=request.version_range,
        selected_consumer_contract_version=winner.consumer_contract_version,
        provider_id=winner.provider_id,
        implementation_version=winner.implementation_version,
        provider_contract_id=winner.provider_contract_id,
        provider_contract_version=winner.provider_contract_version,
        adapter_chain=winner.adapter_chain,
        candidate_count=len(candidates),
        selection_reason=(
            f"{route_class} "
            f"hops={len(winner.adapter_chain)} "
            f"lossy={winner.lossy_count} "
            f"preferred_rank={preferred_rank} "
            f"consumer_contract={winner.consumer_contract_version} "
            f"provider_contract={winner.provider_contract_version} "
            f"implementation={winner.implementation_version} "
            f"provider={winner.provider_id}"
        ),
    )
