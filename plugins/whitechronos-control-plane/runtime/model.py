from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    HOST_RELOAD_REQUIRED = "HOST_RELOAD_REQUIRED"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"
    SECURITY_REVIEW_REQUIRED = "SECURITY_REVIEW_REQUIRED"


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


@dataclass(frozen=True)
class McpProbeResult:
    server_name: str
    status: CheckStatus
    server_info: dict[str, object]
    tools: tuple[str, ...]
    missing_tools: tuple[str, ...]
    unexpected_tools: tuple[str, ...]
    stderr_tail: str


@dataclass(frozen=True)
class CodexCapabilities:
    version: str
    exec: bool
    json: bool
    resume: bool
    sandbox_read_only: bool
    sandbox_workspace_write: bool
    approval_never: bool
