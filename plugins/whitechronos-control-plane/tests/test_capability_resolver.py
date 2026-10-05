from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_adapter import CapabilityAdapter
from runtime.capability_model import (
    CapabilityContract,
    CapabilityManifest,
    CapabilityRegistry,
    ContractRef,
    LifecycleState,
    ProviderLifecycleView,
    RiskProfile,
)
from runtime.capability_resolver import (
    NoCompatibleProvider,
    PinnedProviderUnavailable,
    ResolutionRequest,
    resolve_capability,
)


def _risk() -> RiskProfile:
    return RiskProfile("NONE", False, False, False, False, "NONE", False, False, False)


def _provider(provider_id: str, implementation_version: str, contract_version: str) -> CapabilityManifest:
    return CapabilityManifest(
        provider_id=provider_id,
        display_name=provider_id,
        implementation_version=implementation_version,
        source_type="local",
        source=f"plugins/{provider_id}",
        revision="deadbeef",
        digest="sha256:" + "a" * 64,
        license_status="MIT",
        provides=(ContractRef("capability://demo/search", contract_version),),
        requires=(),
        risk_profile=_risk(),
        extensions={},
    )


def _view(provider_id: str, implementation_version: str, state: LifecycleState) -> ProviderLifecycleView:
    return ProviderLifecycleView(
        provider_id=provider_id,
        implementation_version=implementation_version,
        current_state=state,
        last_event_id=f"evt-{provider_id}-{implementation_version}",
        event_count=1,
    )


def _registry(provider_specs, *, reverse: bool = False) -> CapabilityRegistry:
    items = list(provider_specs)
    if reverse:
        items.reverse()
    providers = {}
    lifecycle = {}
    for provider_id, implementation_version, contract_version, state in items:
        key = (provider_id, implementation_version)
        providers[key] = _provider(provider_id, implementation_version, contract_version)
        if state is not None:
            lifecycle[key] = _view(provider_id, implementation_version, state)
    return CapabilityRegistry(contracts={}, providers=providers, events=(), lifecycle=lifecycle, adapters={})


def _contract(version: str) -> CapabilityContract:
    return CapabilityContract(
        contract_id="capability://demo/search",
        version=version,
        stability="STABLE",
        input_schema_ref=None,
        output_schema_ref=None,
        error_codes=(),
        side_effect_class="PURE",
        invariants=(),
    )


def _adapter(
    adapter_id: str,
    source_version: str,
    target_version: str,
    *,
    implementation_provider_id: str,
    lossiness: str = "LOSSLESS",
) -> CapabilityAdapter:
    return CapabilityAdapter(
        adapter_id=adapter_id,
        version="1.0.0",
        implementation_provider_id=implementation_provider_id,
        implementation_version="1.0.0",
        source_contract_id="capability://demo/search",
        source_version=source_version,
        target_contract_id="capability://demo/search",
        target_version=target_version,
        transformation=f"{source_version} to {target_version}",
        lossiness=lossiness,
        information_loss=() if lossiness == "LOSSLESS" else ("ranking_hint",),
        unsupported_cases=(),
        error_mapping=(),
        conformance_tests=("tests/contracts/search_adapter.py",),
        extensions={},
    )


def _adapter_registry(
    *,
    contracts: tuple[str, ...],
    target_providers: tuple[tuple[str, str, str, LifecycleState], ...],
    adapters: tuple[CapabilityAdapter, ...],
    adapter_states: dict[str, LifecycleState],
    reverse: bool = False,
) -> CapabilityRegistry:
    provider_specs = list(target_providers)
    adapter_list = list(adapters)
    if reverse:
        provider_specs.reverse()
        adapter_list.reverse()
    providers = {}
    lifecycle = {}
    for provider_id, implementation_version, contract_version, state in provider_specs:
        key = (provider_id, implementation_version)
        providers[key] = _provider(provider_id, implementation_version, contract_version)
        lifecycle[key] = _view(provider_id, implementation_version, state)
    for adapter in adapter_list:
        key = (adapter.implementation_provider_id, adapter.implementation_version)
        if key not in providers:
            providers[key] = CapabilityManifest(
                provider_id=adapter.implementation_provider_id,
                display_name=adapter.implementation_provider_id,
                implementation_version=adapter.implementation_version,
                source_type="local",
                source=f"plugins/{adapter.implementation_provider_id}",
                revision="deadbeef",
                digest="sha256:" + "b" * 64,
                license_status="MIT",
                provides=(),
                requires=(),
                risk_profile=_risk(),
                extensions={},
            )
        lifecycle[key] = _view(
            adapter.implementation_provider_id,
            adapter.implementation_version,
            adapter_states[adapter.adapter_id],
        )
    return CapabilityRegistry(
        contracts={("capability://demo/search", v): _contract(v) for v in contracts},
        providers=providers,
        events=(),
        lifecycle=lifecycle,
        adapters={(a.adapter_id, a.version): a for a in adapter_list},
    )


def test_resolver_uses_only_active_providers():
    registry = _registry([
        ("active-provider", "1.0.0", "1.5.0", LifecycleState.ACTIVE),
        ("quarantined-provider", "9.0.0", "1.9.0", LifecycleState.QUARANTINED),
    ])
    decision = resolve_capability(registry, ResolutionRequest("capability://demo/search", ">=1 <2"))
    assert decision.provider_id == "active-provider"
    assert decision.adapter_chain == ()


def test_provider_without_lifecycle_state_is_ineligible():
    registry = _registry([("missing-state", "1.0.0", "1.5.0", None)])
    with pytest.raises(NoCompatibleProvider):
        resolve_capability(registry, ResolutionRequest("capability://demo/search", ">=1 <2"))


def test_exact_pin_is_fail_closed():
    registry = _registry([
        ("provider-a", "1.2.0", "1.5.0", LifecycleState.ACTIVE),
        ("provider-b", "9.0.0", "1.9.0", LifecycleState.ACTIVE),
    ])
    decision = resolve_capability(
        registry,
        ResolutionRequest("capability://demo/search", ">=1 <2", provider_pin=("provider-a", "1.2.0")),
    )
    assert (decision.provider_id, decision.implementation_version) == ("provider-a", "1.2.0")
    with pytest.raises(PinnedProviderUnavailable):
        resolve_capability(
            registry,
            ResolutionRequest("capability://demo/search", ">=1 <2", provider_pin=("provider-a", "9.0.0")),
        )


def test_preference_only_ranks_compatible_active_candidates():
    registry = _registry([
        ("preferred-but-incompatible", "9.0.0", "2.0.0", LifecycleState.ACTIVE),
        ("provider-a", "2.0.0", "1.5.0", LifecycleState.ACTIVE),
        ("provider-b", "1.0.0", "1.9.0", LifecycleState.ACTIVE),
    ])
    decision = resolve_capability(
        registry,
        ResolutionRequest(
            "capability://demo/search",
            ">=1 <2",
            preferred_provider_ids=("preferred-but-incompatible", "provider-a"),
        ),
    )
    assert decision.provider_id == "provider-a"


def test_direct_resolution_is_deterministic_across_insertion_order():
    specs = [
        ("provider-z", "1.0.0", "1.5.0", LifecycleState.ACTIVE),
        ("provider-a", "2.0.0", "1.5.0", LifecycleState.ACTIVE),
    ]
    request = ResolutionRequest("capability://demo/search", ">=1 <2")
    first = resolve_capability(_registry(specs), request)
    second = resolve_capability(_registry(specs, reverse=True), request)
    assert first == second
    assert first.provider_id == "provider-a"


def test_equal_semver_precedence_uses_exact_version_tie_breaker():
    specs = [
        ("provider-a", "1.0.0+build.2", "1.5.0", LifecycleState.ACTIVE),
        ("provider-a", "1.0.0+build.1", "1.5.0", LifecycleState.ACTIVE),
    ]
    request = ResolutionRequest("capability://demo/search", ">=1 <2")
    first = resolve_capability(_registry(specs), request)
    second = resolve_capability(_registry(specs, reverse=True), request)
    assert first == second
    assert first.implementation_version == "1.0.0+build.1"


def test_single_adapter_route_resolves_source_to_target():
    adapter = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-provider")
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0"),
        target_providers=(("target-provider", "1.0.0", "2.0.0", LifecycleState.ACTIVE),),
        adapters=(adapter,),
        adapter_states={"search-v1-v2": LifecycleState.ACTIVE},
    )
    decision = resolve_capability(registry, ResolutionRequest("capability://demo/search", ">=1 <2"))
    assert decision.provider_id == "target-provider"
    assert decision.selected_consumer_contract_version == "1.0.0"
    assert decision.provider_contract_version == "2.0.0"
    assert decision.adapter_chain == (("search-v1-v2", "1.0.0"),)


def test_disabling_adapters_blocks_adapter_only_route():
    adapter = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-provider")
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0"),
        target_providers=(("target-provider", "1.0.0", "2.0.0", LifecycleState.ACTIVE),),
        adapters=(adapter,),
        adapter_states={"search-v1-v2": LifecycleState.ACTIVE},
    )
    with pytest.raises(NoCompatibleProvider):
        resolve_capability(
            registry,
            ResolutionRequest("capability://demo/search", ">=1 <2", allow_adapters=False),
        )


def test_two_adapter_chain_and_cycle_handling_are_explicit():
    a = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-a")
    back = _adapter("search-v2-v1", "2.0.0", "1.0.0", implementation_provider_id="adapter-back")
    b = _adapter("search-v2-v3", "2.0.0", "3.0.0", implementation_provider_id="adapter-b")
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0", "3.0.0"),
        target_providers=(("target-provider", "1.0.0", "3.0.0", LifecycleState.ACTIVE),),
        adapters=(a, back, b),
        adapter_states={
            "search-v1-v2": LifecycleState.ACTIVE,
            "search-v2-v1": LifecycleState.ACTIVE,
            "search-v2-v3": LifecycleState.ACTIVE,
        },
    )
    decision = resolve_capability(registry, ResolutionRequest("capability://demo/search", "1.0.0"))
    assert decision.adapter_chain == (
        ("search-v1-v2", "1.0.0"),
        ("search-v2-v3", "1.0.0"),
    )


def test_inactive_adapter_implementation_makes_edge_unusable():
    adapter = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-provider")
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0"),
        target_providers=(("target-provider", "1.0.0", "2.0.0", LifecycleState.ACTIVE),),
        adapters=(adapter,),
        adapter_states={"search-v1-v2": LifecycleState.QUARANTINED},
    )
    with pytest.raises(NoCompatibleProvider):
        resolve_capability(registry, ResolutionRequest("capability://demo/search", "1.0.0"))


def test_direct_route_beats_preferred_adapted_route():
    adapter = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-provider")
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0"),
        target_providers=(
            ("direct-provider", "1.0.0", "1.0.0", LifecycleState.ACTIVE),
            ("adapted-provider", "9.0.0", "2.0.0", LifecycleState.ACTIVE),
        ),
        adapters=(adapter,),
        adapter_states={"search-v1-v2": LifecycleState.ACTIVE},
    )
    decision = resolve_capability(
        registry,
        ResolutionRequest(
            "capability://demo/search",
            "1.0.0",
            preferred_provider_ids=("adapted-provider",),
        ),
    )
    assert decision.provider_id == "direct-provider"
    assert decision.adapter_chain == ()


def test_fewer_hops_and_lossless_routes_win():
    direct_adapter = _adapter("search-v1-v3", "1.0.0", "3.0.0", implementation_provider_id="adapter-direct")
    a = _adapter("search-v1-v2", "1.0.0", "2.0.0", implementation_provider_id="adapter-a")
    b = _adapter("search-v2-v3", "2.0.0", "3.0.0", implementation_provider_id="adapter-b")
    lossy = _adapter(
        "search-v1-v4-lossy", "1.0.0", "4.0.0",
        implementation_provider_id="adapter-lossy", lossiness="LOSSY",
    )
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0", "3.0.0", "4.0.0"),
        target_providers=(
            ("provider-v3", "1.0.0", "3.0.0", LifecycleState.ACTIVE),
            ("provider-v4", "9.0.0", "4.0.0", LifecycleState.ACTIVE),
        ),
        adapters=(a, b, direct_adapter, lossy),
        adapter_states={
            "search-v1-v2": LifecycleState.ACTIVE,
            "search-v2-v3": LifecycleState.ACTIVE,
            "search-v1-v3": LifecycleState.ACTIVE,
            "search-v1-v4-lossy": LifecycleState.ACTIVE,
        },
    )
    decision = resolve_capability(
        registry,
        ResolutionRequest("capability://demo/search", "1.0.0", allow_lossy_adapters=True),
    )
    assert decision.adapter_chain == (("search-v1-v3", "1.0.0"),)
    assert decision.provider_id == "provider-v3"


def test_lossy_route_requires_explicit_opt_in():
    lossy = _adapter(
        "search-v1-v2-lossy", "1.0.0", "2.0.0",
        implementation_provider_id="adapter-lossy", lossiness="LOSSY",
    )
    registry = _adapter_registry(
        contracts=("1.0.0", "2.0.0"),
        target_providers=(("target-provider", "1.0.0", "2.0.0", LifecycleState.ACTIVE),),
        adapters=(lossy,),
        adapter_states={"search-v1-v2-lossy": LifecycleState.ACTIVE},
    )
    with pytest.raises(NoCompatibleProvider):
        resolve_capability(registry, ResolutionRequest("capability://demo/search", "1.0.0"))
    decision = resolve_capability(
        registry,
        ResolutionRequest("capability://demo/search", "1.0.0", allow_lossy_adapters=True),
    )
    assert decision.adapter_chain == (("search-v1-v2-lossy", "1.0.0"),)


def test_adapter_resolution_is_deterministic_across_insertion_order():
    a = _adapter("z-adapter", "1.0.0", "2.0.0", implementation_provider_id="adapter-z")
    b = _adapter("a-adapter", "1.0.0", "2.0.0", implementation_provider_id="adapter-a")
    specs = (("target-provider", "1.0.0", "2.0.0", LifecycleState.ACTIVE),)
    states = {"z-adapter": LifecycleState.ACTIVE, "a-adapter": LifecycleState.ACTIVE}
    request = ResolutionRequest("capability://demo/search", "1.0.0")
    first = resolve_capability(
        _adapter_registry(
            contracts=("1.0.0", "2.0.0"), target_providers=specs,
            adapters=(a, b), adapter_states=states,
        ),
        request,
    )
    second = resolve_capability(
        _adapter_registry(
            contracts=("1.0.0", "2.0.0"), target_providers=specs,
            adapters=(a, b), adapter_states=states, reverse=True,
        ),
        request,
    )
    assert first == second
    assert first.adapter_chain == (("a-adapter", "1.0.0"),)
