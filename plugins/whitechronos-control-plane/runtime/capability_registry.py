from __future__ import annotations

import json
from pathlib import Path

from .capability_model import (
    CapabilityContract,
    CapabilityManifest,
    CapabilityRegistry,
    ContractRef,
    ContractRequirement,
    LifecycleEvent,
    LifecycleState,
    RiskProfile,
)
from .schema import validate_schema_subset
from .capability_adapter import CapabilityAdapter, ErrorMapping
from .capability_versioning import VersionRange
from .capability_lifecycle import derive_lifecycle_view


def _read_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing registry record: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"registry record must be an object: {path}")
    return value


def _ensure_under(root: Path, path: Path, *, label: str) -> Path:
    root_resolved = root.resolve()
    path_resolved = path.resolve()
    try:
        path_resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"{label} escapes registry v2 root: {path}") from exc
    return path_resolved


def _load_validated(path: Path, schema_path: Path) -> dict[str, object]:
    root = schema_path.parent.resolve()
    safe_schema = _ensure_under(root, schema_path, label="schema")
    safe_path = _ensure_under(root, path, label="record")
    schema = _read_object(safe_schema)
    data = _read_object(safe_path)
    validate_schema_subset(data, schema)
    return data


def load_contract(path: Path, schema_path: Path) -> CapabilityContract:
    data = _load_validated(Path(path), Path(schema_path))
    return CapabilityContract(
        contract_id=str(data["contract_id"]),
        version=str(data["version"]),
        stability=str(data["stability"]),
        input_schema_ref=None if data["input_schema_ref"] is None else str(data["input_schema_ref"]),
        output_schema_ref=None if data["output_schema_ref"] is None else str(data["output_schema_ref"]),
        error_codes=tuple(str(item) for item in data["error_codes"]),
        side_effect_class=str(data["side_effect_class"]),
        invariants=tuple(str(item) for item in data["invariants"]),
    )


def load_manifest(path: Path, schema_path: Path) -> CapabilityManifest:
    data = _load_validated(Path(path), Path(schema_path))
    risk_data = data["risk_profile"]
    assert isinstance(risk_data, dict)
    provides_data = data["provides"]
    requires_data = data["requires"]
    assert isinstance(provides_data, list)
    assert isinstance(requires_data, list)
    provides = tuple(
        ContractRef(str(item["contract_id"]), str(item["version"]))
        for item in provides_data
        if isinstance(item, dict)
    )
    requires = tuple(
        ContractRequirement(str(item["contract_id"]), str(item["version_range"]), str(item["role"]))
        for item in requires_data
        if isinstance(item, dict)
    )
    risk = RiskProfile(
        filesystem=str(risk_data["filesystem"]),
        network=bool(risk_data["network"]),
        credentials=bool(risk_data["credentials"]),
        subprocess=bool(risk_data["subprocess"]),
        background_execution=bool(risk_data["background_execution"]),
        mutation_scope=str(risk_data["mutation_scope"]),
        external_side_effects=bool(risk_data["external_side_effects"]),
        sensitive_data=bool(risk_data["sensitive_data"]),
        control_plane_impact=bool(risk_data["control_plane_impact"]),
    )
    extensions = data["extensions"]
    assert isinstance(extensions, dict)
    return CapabilityManifest(
        provider_id=str(data["provider_id"]),
        display_name=str(data["display_name"]),
        implementation_version=str(data["implementation_version"]),
        source_type=str(data["source_type"]),
        source=str(data["source"]),
        revision=str(data["revision"]),
        digest=str(data["digest"]),
        license_status=str(data["license_status"]),
        provides=provides,
        requires=requires,
        risk_profile=risk,
        extensions=dict(extensions),
    )


def load_adapter(path: Path, schema_path: Path) -> CapabilityAdapter:
    data = _load_validated(Path(path), Path(schema_path))
    mapping_data = data["error_mapping"]
    assert isinstance(mapping_data, list)
    extensions = data["extensions"]
    assert isinstance(extensions, dict)
    return CapabilityAdapter(
        adapter_id=str(data["adapter_id"]),
        version=str(data["version"]),
        implementation_provider_id=str(data["implementation_provider_id"]),
        implementation_version=str(data["implementation_version"]),
        source_contract_id=str(data["source_contract_id"]),
        source_version=str(data["source_version"]),
        target_contract_id=str(data["target_contract_id"]),
        target_version=str(data["target_version"]),
        transformation=str(data["transformation"]),
        lossiness=str(data["lossiness"]),
        information_loss=tuple(str(item) for item in data["information_loss"]),
        unsupported_cases=tuple(str(item) for item in data["unsupported_cases"]),
        error_mapping=tuple(
            ErrorMapping(str(item["source_error"]), str(item["target_error"]))
            for item in mapping_data
            if isinstance(item, dict)
        ),
        conformance_tests=tuple(str(item) for item in data["conformance_tests"]),
        extensions=dict(extensions),
    )


def load_lifecycle_event(path: Path, schema_path: Path) -> LifecycleEvent:
    data = _load_validated(Path(path), Path(schema_path))
    return LifecycleEvent(
        event_id=str(data["event_id"]),
        provider_id=str(data["provider_id"]),
        implementation_version=str(data["implementation_version"]),
        state=LifecycleState(str(data["state"])),
        occurred_at=str(data["occurred_at"]),
        actor_type=str(data["actor_type"]),
        actor_id=str(data["actor_id"]),
        reason=str(data["reason"]),
        evidence_refs=tuple(str(item) for item in data["evidence_refs"]),
        predecessor_event_id=None if data["predecessor_event_id"] is None else str(data["predecessor_event_id"]),
    )


def _record_paths(root: Path) -> tuple[Path, ...]:
    if not root.exists():
        return ()
    v2_root = root.parent.resolve()
    found: list[tuple[str, Path]] = []
    for path in root.rglob("*.json"):
        _ensure_under(v2_root, path, label="record")
        found.append((path.relative_to(v2_root).as_posix(), path))
    return tuple(path for _, path in sorted(found, key=lambda item: item[0]))


def load_capability_registry(repo_root: Path) -> CapabilityRegistry:
    repo = Path(repo_root).resolve()
    root = repo / "registry" / "capabilities" / "v2"
    contract_schema = root / "contract.schema.json"
    manifest_schema = root / "manifest.schema.json"
    event_schema = root / "lifecycle-event.schema.json"
    adapter_schema = root / "adapter.schema.json"

    contracts: dict[tuple[str, str], CapabilityContract] = {}
    for path in _record_paths(root / "contracts"):
        contract = load_contract(path, contract_schema)
        key = (contract.contract_id, contract.version)
        if key in contracts:
            raise ValueError(f"duplicate contract identity: {contract.contract_id}@{contract.version}")
        contracts[key] = contract

    providers: dict[tuple[str, str], CapabilityManifest] = {}
    for path in _record_paths(root / "providers"):
        provider = load_manifest(path, manifest_schema)
        key = (provider.provider_id, provider.implementation_version)
        if key in providers:
            raise ValueError(f"duplicate provider version: {provider.provider_id}@{provider.implementation_version}")
        providers[key] = provider

    for provider in providers.values():
        for provided in provider.provides:
            key = (provided.contract_id, provided.version)
            if key not in contracts:
                raise ValueError(
                    f"provided contract is missing: {provided.contract_id}@{provided.version} "
                    f"for {provider.provider_id}@{provider.implementation_version}"
                )
        for requirement in provider.requires:
            try:
                version_range = VersionRange.parse(requirement.version_range)
            except ValueError as exc:
                raise ValueError(
                    f"invalid version range for requirement {requirement.contract_id}: "
                    f"{requirement.version_range!r}: {exc}"
                ) from exc
            matching_versions = [
                version
                for (contract_id, version) in contracts
                if contract_id == requirement.contract_id and version_range.matches(version)
            ]
            if not matching_versions:
                raise ValueError(
                    f"requirement has no matching contract version: {requirement.contract_id} "
                    f"{requirement.version_range!r} for "
                    f"{provider.provider_id}@{provider.implementation_version}"
                )

    adapters: dict[tuple[str, str], CapabilityAdapter] = {}
    for path in _record_paths(root / "adapters"):
        adapter = load_adapter(path, adapter_schema)
        key = (adapter.adapter_id, adapter.version)
        if key in adapters:
            raise ValueError(f"duplicate adapter identity: {adapter.adapter_id}@{adapter.version}")
        source_key = (adapter.source_contract_id, adapter.source_version)
        if source_key not in contracts:
            raise ValueError(
                f"adapter source contract is missing: {adapter.source_contract_id}@{adapter.source_version}"
            )
        target_key = (adapter.target_contract_id, adapter.target_version)
        if target_key not in contracts:
            raise ValueError(
                f"adapter target contract is missing: {adapter.target_contract_id}@{adapter.target_version}"
            )
        provider_key = (adapter.implementation_provider_id, adapter.implementation_version)
        if provider_key not in providers:
            raise ValueError(
                f"adapter implementation provider is missing: "
                f"{adapter.implementation_provider_id}@{adapter.implementation_version}"
            )
        adapters[key] = adapter

    events: list[LifecycleEvent] = []
    event_ids: set[str] = set()
    for path in _record_paths(root / "events"):
        event = load_lifecycle_event(path, event_schema)
        if event.event_id in event_ids:
            raise ValueError(f"duplicate lifecycle event id: {event.event_id}")
        event_ids.add(event.event_id)
        provider_key = (event.provider_id, event.implementation_version)
        if provider_key not in providers:
            raise ValueError(
                f"lifecycle event references missing provider: "
                f"{event.provider_id}@{event.implementation_version}"
            )
        events.append(event)

    event_tuple = tuple(events)
    lifecycle = derive_lifecycle_view(providers, event_tuple)
    return CapabilityRegistry(
        contracts=contracts,
        providers=providers,
        events=event_tuple,
        lifecycle=lifecycle,
        adapters=adapters,
    )
