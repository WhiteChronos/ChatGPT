from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeProbeSpec:
    plugin_root: str
    mcp_config: str
    mcp_server: str
    expected_tools: tuple[str, ...]
    required_for_broker_smoke: bool


@dataclass(frozen=True)
class IntegrationDescriptor:
    id: str
    display_name: str
    source_type: str
    source: str
    license_status: str
    execution_class: str
    status: str
    controller_plugin: str | None
    skill_paths: tuple[str, ...]
    mcp_servers: tuple[str, ...]
    runtime_probe: RuntimeProbeSpec | None
