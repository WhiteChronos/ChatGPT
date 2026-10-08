from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


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
class ConnectionSpec:
    surfaces: tuple[str, ...]
    auth_required: bool
    safe_probe: str
    target_probe: str | None
    paid_probe_forbidden: bool
    credential_storage: str


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
    connection: ConnectionSpec | None = None


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


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    detail: str
    evidence: dict[str, object]


@dataclass(frozen=True)
class DoctorInput:
    repo_root: Path
    expected_commit: str | None
    codex_path: str
    host_tools: frozenset[str]
    runtime_kind: str
    host_inventory_observed: bool = False


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[CheckResult, ...]
    selected_subagent_path: str
    live_smoke_ready: bool
    blockers: tuple[str, ...]
