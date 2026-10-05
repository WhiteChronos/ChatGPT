from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_registry import load_capability_registry, load_contract
from runtime.registry import load_registry


def _contract(contract_id: str = "capability://test/echo", version: str = "1.0.0") -> dict[str, object]:
    return {
        "schema_version": 2,
        "record_type": "capability_contract",
        "contract_id": contract_id,
        "version": version,
        "stability": "STABLE",
        "input_schema_ref": None,
        "output_schema_ref": None,
        "error_codes": [],
        "side_effect_class": "PURE",
        "invariants": ["returns an echo response"],
        "extensions": {},
    }


def _provider(
    provider_id: str = "test-echo-provider",
    version: str = "1.0.0",
    provided_contract: str = "capability://test/echo",
    contract_version: str = "1.0.0",
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "record_type": "capability_manifest",
        "provider_id": provider_id,
        "display_name": "Test Echo Provider",
        "implementation_version": version,
        "source_type": "local",
        "source": "plugins/test-echo-provider",
        "revision": "deadbeef",
        "digest": "sha256:" + "a" * 64,
        "license_status": "MIT",
        "provides": [{"contract_id": provided_contract, "version": contract_version}],
        "requires": [],
        "risk_profile": {
            "filesystem": "NONE",
            "network": False,
            "credentials": False,
            "subprocess": False,
            "background_execution": False,
            "mutation_scope": "NONE",
            "external_side_effects": False,
            "sensitive_data": False,
            "control_plane_impact": False,
        },
        "extensions": {},
    }



def _adapter(
    adapter_id: str = "test-echo-v1-v2",
    version: str = "1.0.0",
    implementation_provider_id: str = "test-adapter-provider",
    implementation_version: str = "1.0.0",
    source_contract: str = "capability://test/echo",
    source_version: str = "1.0.0",
    target_contract: str = "capability://test/echo",
    target_version: str = "2.0.0",
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "record_type": "capability_adapter",
        "adapter_id": adapter_id,
        "version": version,
        "implementation_provider_id": implementation_provider_id,
        "implementation_version": implementation_version,
        "source_contract_id": source_contract,
        "source_version": source_version,
        "target_contract_id": target_contract,
        "target_version": target_version,
        "transformation": "Translate test echo v1 to v2",
        "lossiness": "LOSSLESS",
        "information_loss": [],
        "unsupported_cases": [],
        "error_mapping": [],
        "conformance_tests": ["tests/contracts/test_echo_v1_v2.py"],
        "extensions": {},
    }


def _event(event_id: str = "evt-001", provider_id: str = "test-echo-provider", version: str = "1.0.0") -> dict[str, object]:
    return {
        "schema_version": 2,
        "record_type": "capability_lifecycle_event",
        "event_id": event_id,
        "provider_id": provider_id,
        "implementation_version": version,
        "state": "DISCOVERED",
        "occurred_at": "2026-10-05T00:00:00Z",
        "actor_type": "SYSTEM",
        "actor_id": "test-suite",
        "reason": "fixture",
        "evidence_refs": [],
        "predecessor_event_id": None,
        "extensions": {},
    }


def _write(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_temp_registry(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(REPO / "registry/integrations", repo / "registry/integrations")
    root = repo / "registry/capabilities/v2"
    root.mkdir(parents=True)
    for name in ("contract.schema.json", "manifest.schema.json", "lifecycle-event.schema.json", "adapter.schema.json"):
        shutil.copy2(REPO / "registry/capabilities/v2" / name, root / name)
    for name in ("contracts", "providers", "events", "adapters"):
        (root / name).mkdir()
    return repo


def test_empty_v2_registry_loads_without_affecting_v1(tmp_path):
    repo = _write_temp_registry(tmp_path)
    v2 = load_capability_registry(repo)
    assert v2.contracts == {}
    assert v2.providers == {}
    assert v2.events == ()
    assert v2.lifecycle == {}
    legacy = load_registry(repo)
    assert tuple(legacy) == ("github-arena", "subagent-broker")


def test_registry_loads_contract_and_provider_independent_of_filename_order(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/z-contract.json", _contract())
    _write(root / "providers/a-provider.json", _provider())
    registry = load_capability_registry(repo)
    assert list(registry.contracts) == [("capability://test/echo", "1.0.0")]
    assert list(registry.providers) == [("test-echo-provider", "1.0.0")]
    assert registry.providers[("test-echo-provider", "1.0.0")].provides[0].contract_id == "capability://test/echo"


def test_registry_rejects_duplicate_contract_identity(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2/contracts"
    _write(root / "a.json", _contract())
    _write(root / "b.json", _contract())
    with pytest.raises(ValueError, match="duplicate contract"):
        load_capability_registry(repo)


def test_registry_rejects_duplicate_provider_version(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/contract.json", _contract())
    _write(root / "providers/a.json", _provider())
    _write(root / "providers/b.json", _provider())
    with pytest.raises(ValueError, match="duplicate provider"):
        load_capability_registry(repo)


def test_registry_rejects_provider_that_claims_missing_provided_contract(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2/providers"
    _write(root / "provider.json", _provider(provided_contract="capability://missing/echo"))
    with pytest.raises(ValueError, match="provided contract.*missing"):
        load_capability_registry(repo)


def test_registry_rejects_json_record_outside_expected_record_type(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2/contracts"
    _write(root / "wrong.json", _provider())
    with pytest.raises(ValueError, match=r"record_type|const|required property"):
        load_capability_registry(repo)


def test_registry_rejects_path_escape_and_symlink_escape(tmp_path):
    repo = _write_temp_registry(tmp_path)
    v2 = repo / "registry/capabilities/v2"
    outside = tmp_path / "outside.json"
    _write(outside, _contract())
    with pytest.raises(ValueError, match="outside|root|escape"):
        load_contract(outside, v2 / "contract.schema.json")

    link = v2 / "contracts/escape.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(ValueError, match="outside|root|escape"):
        load_capability_registry(repo)


def test_registry_rejects_lifecycle_event_for_missing_provider(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2/events"
    _write(root / "event.json", _event())
    with pytest.raises(ValueError, match="lifecycle event.*provider"):
        load_capability_registry(repo)


def test_v1_registry_remains_unchanged_when_v2_exists():
    legacy = load_registry(REPO)
    assert tuple(legacy) == ("github-arena", "subagent-broker")
    assert legacy["github-arena"].execution_class == "MCP_OR_CONNECTOR"
    assert legacy["subagent-broker"].execution_class == "LOCAL_MUTATING"


def test_repository_v2_source_records_are_valid_and_unindexed():
    registry = load_capability_registry(REPO)
    assert isinstance(registry.contracts, dict)
    assert isinstance(registry.providers, dict)
    assert isinstance(registry.lifecycle, dict)
    assert not (REPO / "registry/capabilities/v2/index.json").exists()

def test_registry_loads_adapter_references_independent_of_filename_order(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/z-v1.json", _contract(version="1.0.0"))
    _write(root / "contracts/a-v2.json", _contract(version="2.0.0"))
    _write(root / "providers/z-target.json", _provider(provider_id="test-target-provider", provided_contract="capability://test/echo", contract_version="2.0.0"))
    _write(root / "providers/a-adapter.json", _provider(provider_id="test-adapter-provider", provided_contract="capability://test/echo", contract_version="1.0.0"))
    _write(root / "adapters/m-adapter.json", _adapter())
    registry = load_capability_registry(repo)
    assert list(registry.adapters) == [("test-echo-v1-v2", "1.0.0")]
    adapter = registry.adapters[("test-echo-v1-v2", "1.0.0")]
    assert adapter.implementation_provider_id == "test-adapter-provider"
    assert adapter.source_version == "1.0.0"
    assert adapter.target_version == "2.0.0"


def test_registry_rejects_duplicate_adapter_identity(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/v1.json", _contract(version="1.0.0"))
    _write(root / "contracts/v2.json", _contract(version="2.0.0"))
    _write(root / "providers/adapter-provider.json", _provider(provider_id="test-adapter-provider"))
    _write(root / "adapters/a.json", _adapter())
    _write(root / "adapters/b.json", _adapter())
    with pytest.raises(ValueError, match="duplicate adapter"):
        load_capability_registry(repo)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"source_contract": "capability://missing/source"}, "source contract"),
        ({"target_contract": "capability://missing/target"}, "target contract"),
        ({"implementation_provider_id": "missing-provider"}, "implementation provider"),
    ],
)
def test_registry_rejects_adapter_missing_exact_reference(tmp_path, overrides, message):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/v1.json", _contract(version="1.0.0"))
    _write(root / "contracts/v2.json", _contract(version="2.0.0"))
    _write(root / "providers/adapter-provider.json", _provider(provider_id="test-adapter-provider"))
    _write(root / "adapters/adapter.json", _adapter(**overrides))
    with pytest.raises(ValueError, match=message):
        load_capability_registry(repo)


def test_registry_rejects_malformed_requirement_range(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/v1.json", _contract(version="1.0.0"))
    provider = _provider()
    provider["requires"] = [{"contract_id": "capability://test/echo", "version_range": "^1.0.0", "role": "REQUIRED"}]
    _write(root / "providers/provider.json", provider)
    with pytest.raises(ValueError, match="version range|unsupported"):
        load_capability_registry(repo)


def test_registry_rejects_requirement_without_matching_contract_version(tmp_path):
    repo = _write_temp_registry(tmp_path)
    root = repo / "registry/capabilities/v2"
    _write(root / "contracts/v1.json", _contract(version="1.0.0"))
    provider = _provider()
    provider["requires"] = [{"contract_id": "capability://test/echo", "version_range": ">=2 <3", "role": "REQUIRED"}]
    _write(root / "providers/provider.json", provider)
    with pytest.raises(ValueError, match="requirement.*matching contract"):
        load_capability_registry(repo)

