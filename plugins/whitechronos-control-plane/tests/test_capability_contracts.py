from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_model import (
    CapabilityManifest,
    ContractRef,
    LifecycleEvent,
    LifecycleState,
    RiskProfile,
    validate_capability_id,
    validate_provider_id,
    validate_semver,
)
from runtime.schema import validate_schema_subset


@pytest.mark.parametrize(
    "value",
    [
        "capability://knowledge/search",
        "capability://engineering/bim",
        "capability://agent/delegate",
    ],
)
def test_validate_capability_id_accepts_namespaced_ids(value):
    assert validate_capability_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "knowledge/search",
        "capability://single",
        "capability://knowledge/../secret",
        "capability://knowledge/search?x=1",
        "capability://knowledge/search#frag",
        "capability://knowledge\\search",
        "capability://knowledge/white space",
    ],
)
def test_validate_capability_id_rejects_unsafe_or_non_namespaced_ids(value):
    with pytest.raises(ValueError):
        validate_capability_id(value)


@pytest.mark.parametrize("value", ["0.1.0", "1.0.0", "2.7.3-alpha.1", "2.7.3+build.5"])
def test_validate_semver_accepts_full_semver(value):
    assert validate_semver(value, label="version") == value


@pytest.mark.parametrize("value", ["1", "1.2", "01.2.3", "v1.2.3", "1.2.x", ""])
def test_validate_semver_rejects_non_semver(value):
    with pytest.raises(ValueError, match="version"):
        validate_semver(value, label="version")


@pytest.mark.parametrize("value", ["test-provider", "vendor.plugin_1", "a"])
def test_validate_provider_id_accepts_lowercase_slug(value):
    assert validate_provider_id(value) == value


@pytest.mark.parametrize("value", ["", "Test-Provider", "test provider", "../escape", "a..b", "ümlaut"])
def test_validate_provider_id_rejects_unsafe_slug(value):
    with pytest.raises(ValueError):
        validate_provider_id(value)


def _valid_manifest_dict() -> dict[str, object]:
    return {
        "schema_version": 2,
        "record_type": "capability_manifest",
        "provider_id": "test-echo-provider",
        "display_name": "Test Echo Provider",
        "implementation_version": "1.0.0",
        "source_type": "local",
        "source": "plugins/test-echo-provider",
        "revision": "0123456789abcdef",
        "digest": "sha256:" + "a" * 64,
        "license_status": "MIT",
        "provides": [{"contract_id": "capability://test/echo", "version": "1.0.0"}],
        "requires": [],
        "risk_profile": {
            "filesystem": "WRITE",
            "network": True,
            "credentials": True,
            "subprocess": False,
            "background_execution": True,
            "mutation_scope": "WORKSPACE",
            "external_side_effects": True,
            "sensitive_data": False,
            "control_plane_impact": False,
        },
        "extensions": {"vendor.example/v1": {"mode": "echo"}},
    }


def test_manifest_schema_accepts_multidimensional_risk_profile():
    schema = json.loads((REPO / "registry/capabilities/v2/manifest.schema.json").read_text())
    validate_schema_subset(_valid_manifest_dict(), schema)


def test_manifest_schema_rejects_unknown_risk_key():
    schema = json.loads((REPO / "registry/capabilities/v2/manifest.schema.json").read_text())
    data = _valid_manifest_dict()
    data["risk_profile"] = dict(data["risk_profile"], trust_me=True)
    with pytest.raises(ValueError, match=r"risk_profile\.trust_me"):
        validate_schema_subset(data, schema)


def test_manifest_model_rejects_non_normalized_digest():
    risk = RiskProfile("NONE", False, False, False, False, "NONE", False, False, False)
    with pytest.raises(ValueError, match="digest"):
        CapabilityManifest(
            provider_id="test-echo-provider",
            display_name="Test Echo",
            implementation_version="1.0.0",
            source_type="local",
            source="plugins/test-echo-provider",
            revision="abc123",
            digest="SHA256:" + "A" * 64,
            license_status="MIT",
            provides=(ContractRef("capability://test/echo", "1.0.0"),),
            requires=(),
            risk_profile=risk,
            extensions={},
        )


def test_lifecycle_event_rejects_non_timestamp_occurred_at():
    with pytest.raises(ValueError, match="occurred_at"):
        LifecycleEvent(
            event_id="evt-001",
            provider_id="test-echo-provider",
            implementation_version="1.0.0",
            state=LifecycleState.DISCOVERED,
            occurred_at="not-a-timestamp",
            actor_type="SYSTEM",
            actor_id="test",
            reason="test",
            evidence_refs=(),
            predecessor_event_id=None,
        )
