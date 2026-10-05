from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


_SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_PROVIDER_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class LifecycleState(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUARANTINED = "QUARANTINED"
    VALIDATING = "VALIDATING"
    COMPATIBLE = "COMPATIBLE"
    PROMOTABLE = "PROMOTABLE"
    CANARY = "CANARY"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    REVALIDATION_REQUIRED = "REVALIDATION_REQUIRED"
    REGRESSED = "REGRESSED"
    ROLLED_BACK = "ROLLED_BACK"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"


def validate_capability_id(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("capability://"):
        raise ValueError("contract_id must start with capability://")
    remainder = value[len("capability://") :]
    if any(token in remainder for token in ("\\", "?", "#", "..")):
        raise ValueError(f"unsafe contract_id: {value!r}")
    if any(ch.isspace() for ch in remainder):
        raise ValueError(f"contract_id must not contain whitespace: {value!r}")
    parts = remainder.split("/")
    if len(parts) < 2 or any(not part for part in parts):
        raise ValueError(f"contract_id must be namespaced: {value!r}")
    return value


def validate_provider_id(value: str) -> str:
    if not isinstance(value, str) or not _PROVIDER_RE.fullmatch(value) or ".." in value:
        raise ValueError(f"invalid provider_id: {value!r}")
    return value


def validate_semver(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not _SEMVER_RE.fullmatch(value):
        raise ValueError(f"{label} must be a full SemVer value: {value!r}")
    return value


def _validate_digest(value: str) -> str:
    if not isinstance(value, str) or not _DIGEST_RE.fullmatch(value):
        raise ValueError("digest must be sha256:<64 lowercase hex>")
    return value


def _validate_timestamp(value: str) -> str:
    if not isinstance(value, str) or "T" not in value:
        raise ValueError(f"occurred_at must be an ISO-8601 timestamp: {value!r}")
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"occurred_at must be an ISO-8601 timestamp: {value!r}") from exc
    return value


@dataclass(frozen=True)
class ContractRef:
    contract_id: str
    version: str

    def __post_init__(self) -> None:
        validate_capability_id(self.contract_id)
        validate_semver(self.version, label="contract version")


@dataclass(frozen=True)
class ContractRequirement:
    contract_id: str
    version_range: str
    role: str

    def __post_init__(self) -> None:
        validate_capability_id(self.contract_id)
        if not isinstance(self.version_range, str) or not self.version_range.strip():
            raise ValueError("version_range must be non-empty")
        if self.role not in {"REQUIRED", "OPTIONAL", "ENHANCEMENT"}:
            raise ValueError(f"invalid requirement role: {self.role!r}")


@dataclass(frozen=True)
class CapabilityContract:
    contract_id: str
    version: str
    stability: str
    input_schema_ref: str | None
    output_schema_ref: str | None
    error_codes: tuple[str, ...]
    side_effect_class: str
    invariants: tuple[str, ...]

    def __post_init__(self) -> None:
        validate_capability_id(self.contract_id)
        validate_semver(self.version, label="contract version")
        if self.stability not in {"EXPERIMENTAL", "STABLE", "DEPRECATED"}:
            raise ValueError(f"invalid stability: {self.stability!r}")
        if self.side_effect_class not in {"PURE", "READ_ONLY", "LOCAL_MUTATING", "EXTERNAL_MUTATING", "CONTROL_PLANE"}:
            raise ValueError(f"invalid side_effect_class: {self.side_effect_class!r}")


@dataclass(frozen=True)
class RiskProfile:
    filesystem: str
    network: bool
    credentials: bool
    subprocess: bool
    background_execution: bool
    mutation_scope: str
    external_side_effects: bool
    sensitive_data: bool
    control_plane_impact: bool

    def __post_init__(self) -> None:
        if self.filesystem not in {"NONE", "READ", "WRITE"}:
            raise ValueError(f"invalid filesystem risk: {self.filesystem!r}")
        if self.mutation_scope not in {"NONE", "WORKSPACE", "EXTERNAL", "CONTROL_PLANE"}:
            raise ValueError(f"invalid mutation_scope: {self.mutation_scope!r}")
        for name in (
            "network", "credentials", "subprocess", "background_execution",
            "external_side_effects", "sensitive_data", "control_plane_impact",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be boolean")


@dataclass(frozen=True)
class CapabilityManifest:
    provider_id: str
    display_name: str
    implementation_version: str
    source_type: str
    source: str
    revision: str
    digest: str
    license_status: str
    provides: tuple[ContractRef, ...]
    requires: tuple[ContractRequirement, ...]
    risk_profile: RiskProfile
    extensions: dict[str, object]

    def __post_init__(self) -> None:
        validate_provider_id(self.provider_id)
        validate_semver(self.implementation_version, label="implementation_version")
        _validate_digest(self.digest)
        if not self.display_name or not self.source or not self.revision or not self.license_status:
            raise ValueError("manifest identity/source fields must be non-empty")
        if self.source_type not in {"local", "upstream_git", "external_reference", "official_plugin", "component_repository"}:
            raise ValueError(f"invalid source_type: {self.source_type!r}")


@dataclass(frozen=True)
class LifecycleEvent:
    event_id: str
    provider_id: str
    implementation_version: str
    state: LifecycleState
    occurred_at: str
    actor_type: str
    actor_id: str
    reason: str
    evidence_refs: tuple[str, ...]
    predecessor_event_id: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        validate_provider_id(self.provider_id)
        validate_semver(self.implementation_version, label="implementation_version")
        _validate_timestamp(self.occurred_at)
        if self.actor_type not in {"HUMAN", "SYSTEM", "WORKFLOW"}:
            raise ValueError(f"invalid actor_type: {self.actor_type!r}")
        if not self.actor_id or not self.reason:
            raise ValueError("actor_id and reason must be non-empty")
        if self.predecessor_event_id is not None and not self.predecessor_event_id:
            raise ValueError("predecessor_event_id must be null or non-empty")


@dataclass(frozen=True)
class ProviderLifecycleView:
    provider_id: str
    implementation_version: str
    current_state: LifecycleState
    last_event_id: str
    event_count: int


@dataclass(frozen=True)
class CapabilityRegistry:
    contracts: dict[tuple[str, str], CapabilityContract]
    providers: dict[tuple[str, str], CapabilityManifest]
    events: tuple[LifecycleEvent, ...]
    lifecycle: dict[tuple[str, str], ProviderLifecycleView]
