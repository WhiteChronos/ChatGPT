from __future__ import annotations

import json
from pathlib import Path

from .model import ConnectionSpec, IntegrationDescriptor, RuntimeProbeSpec
from .schema import validate_schema_subset


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing registry file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at {path}: {exc}") from exc


def _relative_under(base: Path, relative: str, label: str) -> Path:
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} must stay within plugin_root") from exc
    return candidate


def _descriptor_from_data(repo_root: Path, data: dict[str, object]) -> IntegrationDescriptor:
    probe_data = data.get("runtime_probe")
    probe = None
    if isinstance(probe_data, dict):
        plugin_root = str(probe_data["plugin_root"])
        plugin_abs = _relative_under(repo_root, plugin_root, "runtime_probe.plugin_root")
        mcp_config = str(probe_data["mcp_config"])
        _relative_under(plugin_abs, mcp_config, "runtime_probe.mcp_config")
        probe = RuntimeProbeSpec(
            plugin_root=plugin_root,
            mcp_config=mcp_config,
            mcp_server=str(probe_data["mcp_server"]),
            expected_tools=tuple(str(item) for item in probe_data["expected_tools"]),
            required_for_broker_smoke=bool(probe_data["required_for_broker_smoke"]),
        )
    connection_data = data.get("connection")
    connection = None
    if isinstance(connection_data, dict):
        target_probe = connection_data.get("target_probe")
        connection = ConnectionSpec(
            surfaces=tuple(str(item) for item in connection_data["surfaces"]),
            auth_required=bool(connection_data["auth_required"]),
            safe_probe=str(connection_data["safe_probe"]),
            target_probe=None if target_probe is None else str(target_probe),
            paid_probe_forbidden=bool(connection_data["paid_probe_forbidden"]),
            credential_storage=str(connection_data["credential_storage"]),
        )
    controller = data.get("controller_plugin")
    return IntegrationDescriptor(
        id=str(data["id"]),
        display_name=str(data["display_name"]),
        source_type=str(data["source_type"]),
        source=str(data["source"]),
        license_status=str(data["license_status"]),
        execution_class=str(data["execution_class"]),
        status=str(data["status"]),
        controller_plugin=None if controller is None else str(controller),
        skill_paths=tuple(str(item) for item in data["skill_paths"]),
        mcp_servers=tuple(str(item) for item in data["mcp_servers"]),
        connection=connection,
        runtime_probe=probe,
    )


def load_descriptor(repo_root: Path, descriptor_path: Path) -> IntegrationDescriptor:
    repo_root = Path(repo_root).resolve()
    schema_path = repo_root / "registry" / "integrations" / "schema.json"
    schema = _load_json(schema_path)
    if not isinstance(schema, dict):
        raise ValueError(f"registry schema must be an object: {schema_path}")
    data = _load_json(descriptor_path)
    if not isinstance(data, dict):
        raise ValueError(f"descriptor must be an object: {descriptor_path}")
    validate_schema_subset(data, schema)
    return _descriptor_from_data(repo_root, data)


def load_registry(repo_root: Path) -> dict[str, IntegrationDescriptor]:
    repo_root = Path(repo_root).resolve()
    registry_root = repo_root / "registry" / "integrations"
    index = _load_json(registry_root / "index.json")
    if not isinstance(index, dict) or index.get("schema_version") != 1:
        raise ValueError("registry index must declare schema_version 1")
    names = index.get("descriptors")
    if not isinstance(names, list) or not all(isinstance(name, str) and name for name in names):
        raise ValueError("registry index descriptors must be a list of filenames")
    result: dict[str, IntegrationDescriptor] = {}
    for name in names:
        path = _relative_under(registry_root, name, "registry index descriptor")
        descriptor = load_descriptor(repo_root, path)
        if descriptor.id in result:
            raise ValueError(f"duplicate integration id: {descriptor.id}")
        result[descriptor.id] = descriptor
    return result
