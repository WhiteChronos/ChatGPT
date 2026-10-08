from __future__ import annotations

from .connection_models import (
    ConnectionEvidence,
    ConnectionObservation,
    ConnectionSignals,
    ConnectionStatus,
)


def evaluate_connection(
    integration_id: str,
    signals: ConnectionSignals,
    evidence: tuple[ConnectionEvidence, ...] = (),
) -> ConnectionObservation:
    def result(status: ConnectionStatus, detail: str) -> ConnectionObservation:
        return ConnectionObservation(
            integration_id=integration_id,
            configured=signals.configured,
            host_visible=signals.host_visible,
            authenticated=signals.authenticated,
            target_accessible=signals.target_accessible,
            live_verified=signals.live_verified,
            status=status,
            detail=detail,
            evidence=evidence,
        )

    if signals.required_blocker is not None:
        return result(signals.required_blocker, "required capability is blocked")

    if not signals.configured:
        return result(ConnectionStatus.FAIL, "integration is not configured")

    if signals.host_visible is None:
        return result(ConnectionStatus.UNAVAILABLE, "host visibility has not been observed")

    if signals.host_visible is False:
        return result(signals.host_absence_status, "integration is not visible in the current host")

    if signals.authentication_required:
        if signals.authenticated is None:
            return result(ConnectionStatus.UNAVAILABLE, "authentication has not been observed")
        if signals.authenticated is False:
            return result(ConnectionStatus.USER_ACTION_REQUIRED, "provider authentication is unavailable")

    if signals.target_required:
        if signals.target_accessible is None:
            return result(ConnectionStatus.UNAVAILABLE, "target access has not been observed")
        if signals.target_accessible is False:
            return result(ConnectionStatus.FAIL, "required target is not accessible")

    if signals.live_verification_required:
        if signals.live_verified is None:
            return result(ConnectionStatus.UNAVAILABLE, "live verification has not been observed")
        if signals.live_verified is False:
            return result(ConnectionStatus.FAIL, "required live verification did not pass")

    if signals.optional_degradations:
        return result(
            ConnectionStatus.DEGRADED,
            "optional capability degraded: " + ", ".join(signals.optional_degradations),
        )

    return result(ConnectionStatus.PASS, "required connection evidence passed")
