from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConnectionStatus(str, Enum):
    PASS = "PASS"
    DEGRADED = "DEGRADED"
    FAIL = "FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    HOST_RELOAD_REQUIRED = "HOST_RELOAD_REQUIRED"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"
    HOST_POLICY_BLOCKED = "HOST_POLICY_BLOCKED"
    SECURITY_REVIEW_REQUIRED = "SECURITY_REVIEW_REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ConnectionEvidence:
    source: str
    operation: str
    observed_at: str
    target: str | None
    summary: str


@dataclass(frozen=True)
class ConnectionSignals:
    configured: bool
    host_visible: bool | None
    authenticated: bool | None
    target_accessible: bool | None
    live_verified: bool | None
    authentication_required: bool
    target_required: bool
    live_verification_required: bool
    host_absence_status: ConnectionStatus
    required_blocker: ConnectionStatus | None
    optional_degradations: tuple[str, ...]


@dataclass(frozen=True)
class ConnectionObservation:
    integration_id: str
    configured: bool
    host_visible: bool | None
    authenticated: bool | None
    target_accessible: bool | None
    live_verified: bool | None
    status: ConnectionStatus
    detail: str
    evidence: tuple[ConnectionEvidence, ...]
