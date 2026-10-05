from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_lifecycle import derive_lifecycle_view
from runtime.capability_model import (
    CapabilityManifest,
    LifecycleEvent,
    LifecycleState,
    RiskProfile,
)


def _provider(provider_id: str = "test-echo-provider", version: str = "1.0.0") -> CapabilityManifest:
    return CapabilityManifest(
        provider_id=provider_id,
        display_name=provider_id,
        implementation_version=version,
        source_type="local",
        source=f"plugins/{provider_id}",
        revision="deadbeef",
        digest="sha256:" + "a" * 64,
        license_status="MIT",
        provides=(),
        requires=(),
        risk_profile=RiskProfile("NONE", False, False, False, False, "NONE", False, False, False),
        extensions={},
    )


def _event(
    event_id: str,
    state: LifecycleState,
    predecessor: str | None,
    *,
    provider_id: str = "test-echo-provider",
    version: str = "1.0.0",
) -> LifecycleEvent:
    return LifecycleEvent(
        event_id=event_id,
        provider_id=provider_id,
        implementation_version=version,
        state=state,
        occurred_at="2026-10-05T00:00:00Z",
        actor_type="SYSTEM",
        actor_id="test-suite",
        reason="fixture",
        evidence_refs=(),
        predecessor_event_id=predecessor,
    )


def test_lifecycle_derives_current_state_from_linear_chain():
    key = ("test-echo-provider", "1.0.0")
    providers = {key: _provider()}
    events = (
        _event("evt-001", LifecycleState.DISCOVERED, None),
        _event("evt-002", LifecycleState.QUARANTINED, "evt-001"),
        _event("evt-003", LifecycleState.VALIDATING, "evt-002"),
        _event("evt-004", LifecycleState.COMPATIBLE, "evt-003"),
    )
    view = derive_lifecycle_view(providers, events)
    assert view[key].current_state is LifecycleState.COMPATIBLE
    assert view[key].last_event_id == "evt-004"
    assert view[key].event_count == 4


def test_lifecycle_rejects_missing_predecessor():
    key = ("test-echo-provider", "1.0.0")
    with pytest.raises(ValueError, match="missing predecessor"):
        derive_lifecycle_view({key: _provider()}, (_event("evt-002", LifecycleState.QUARANTINED, "evt-404"),))


def test_lifecycle_rejects_cross_provider_predecessor():
    key_a = ("test-echo-provider", "1.0.0")
    key_b = ("other-provider", "1.0.0")
    events = (
        _event("evt-a", LifecycleState.DISCOVERED, None),
        _event("evt-b", LifecycleState.QUARANTINED, "evt-a", provider_id="other-provider"),
    )
    with pytest.raises(ValueError, match="cross-provider"):
        derive_lifecycle_view({key_a: _provider(), key_b: _provider("other-provider")}, events)


def test_lifecycle_rejects_multiple_roots_for_one_provider():
    key = ("test-echo-provider", "1.0.0")
    events = (
        _event("evt-001", LifecycleState.DISCOVERED, None),
        _event("evt-002", LifecycleState.QUARANTINED, None),
    )
    with pytest.raises(ValueError, match="root"):
        derive_lifecycle_view({key: _provider()}, events)


def test_lifecycle_rejects_branching_history():
    key = ("test-echo-provider", "1.0.0")
    events = (
        _event("evt-001", LifecycleState.DISCOVERED, None),
        _event("evt-002", LifecycleState.QUARANTINED, "evt-001"),
        _event("evt-003", LifecycleState.REVOKED, "evt-001"),
    )
    with pytest.raises(ValueError, match="branch"):
        derive_lifecycle_view({key: _provider()}, events)


def test_lifecycle_rejects_cycle():
    key = ("test-echo-provider", "1.0.0")
    events = (
        _event("evt-001", LifecycleState.DISCOVERED, "evt-002"),
        _event("evt-002", LifecycleState.QUARANTINED, "evt-001"),
    )
    with pytest.raises(ValueError, match="cycle|root"):
        derive_lifecycle_view({key: _provider()}, events)


def test_provider_without_events_has_no_materialized_lifecycle_entry():
    key = ("test-echo-provider", "1.0.0")
    assert derive_lifecycle_view({key: _provider()}, ()) == {}
