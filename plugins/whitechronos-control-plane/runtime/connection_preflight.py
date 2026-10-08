from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .connection_models import (
    ConnectionEvidence,
    ConnectionObservation,
    ConnectionSignals,
    ConnectionStatus,
)
from .connections import evaluate_connection
from .registry import load_registry


@dataclass(frozen=True)
class ConnectionRequirement:
    integration_id: str
    target_required: bool
    live_verification_required: bool


@dataclass(frozen=True)
class ConnectionReport:
    observations: tuple[ConnectionObservation, ...]
    required_task_connections_pass: bool
    blockers: tuple[str, ...]


_NON_BLOCKING = {
    ConnectionStatus.PASS,
    ConnectionStatus.DEGRADED,
    ConnectionStatus.NOT_APPLICABLE,
}
_BLOCKING_STATUSES = {
    ConnectionStatus.FAIL,
    ConnectionStatus.UNAVAILABLE,
    ConnectionStatus.HOST_RELOAD_REQUIRED,
    ConnectionStatus.USER_ACTION_REQUIRED,
    ConnectionStatus.HOST_POLICY_BLOCKED,
    ConnectionStatus.SECURITY_REVIEW_REQUIRED,
}
_PROCESS_LAYER_NAMES = {"SUPERPOWERS", "ARENA", "RUNTIME_DOCTOR"}
_PROCESS_LAYER_STATUSES = {status.value for status in ConnectionStatus}
_SECRET_PATTERNS = (
    re.compile(r"\bauthorization\s*[:=]\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(
        r"\b(?:access[_-]?token|refresh[_-]?token|api[_-]?key|password|cookie)\s*[:=]\s*\S+",
        re.IGNORECASE,
    ),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
)


def _bool_or_none(value: object, label: str) -> bool | None:
    if value is None or isinstance(value, bool):
        return value
    raise ValueError(f"{label} must be boolean or null")


def _required_bool(value: object, label: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{label} must be boolean")


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _status_or_none(value: object, label: str) -> ConnectionStatus | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a status string or null")
    try:
        return ConnectionStatus(value)
    except ValueError as exc:
        raise ValueError(f"{label} has unknown status {value!r}") from exc


def _blocking_status_or_none(value: object, label: str) -> ConnectionStatus | None:
    parsed = _status_or_none(value, label)
    if parsed is not None and parsed not in _BLOCKING_STATUSES:
        raise ValueError(f"{label} must be a blocking status")
    return parsed


def _status_with_default(
    value: object,
    label: str,
    default: ConnectionStatus,
) -> ConnectionStatus:
    parsed = _status_or_none(value, label)
    return default if parsed is None else parsed


def _string_tuple(value: object, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_nonempty_string(item, f"{label}[{index}]"))
    return tuple(result)


def _timestamp(value: object, label: str) -> str:
    text = _nonempty_string(value, label)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include timezone")
    return text


def _reject_secret_like(value: str | None, label: str) -> None:
    if value is None:
        return
    if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
        raise ValueError(f"{label}: evidence contains secret-like content")


def _evidence_tuple(value: object, label: str) -> tuple[ConnectionEvidence, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    result: list[ConnectionEvidence] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{label}[{index}] must be an object")
        item_label = f"{label}[{index}]"
        source = _nonempty_string(item.get("source"), f"{item_label}.source")
        operation = _nonempty_string(item.get("operation"), f"{item_label}.operation")
        observed_at = _timestamp(item.get("observed_at"), f"{item_label}.observed_at")
        target = item.get("target")
        if target is not None and not isinstance(target, str):
            raise ValueError(f"{item_label}.target must be a string or null")
        summary = _nonempty_string(item.get("summary"), f"{item_label}.summary")
        for evidence_value, field in (
            (source, "source"),
            (operation, "operation"),
            (target, "target"),
            (summary, "summary"),
        ):
            _reject_secret_like(evidence_value, f"{item_label}.{field}")
        result.append(
            ConnectionEvidence(
                source=source,
                operation=operation,
                observed_at=observed_at,
                target=target,
                summary=summary,
            )
        )
    return tuple(result)


def _requirements(payload: dict[str, object]) -> tuple[ConnectionRequirement, ...]:
    raw = payload.get("requirements")
    if not isinstance(raw, list):
        raise ValueError("requirements must be a list")
    seen: set[str] = set()
    result: list[ConnectionRequirement] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"requirements[{index}] must be an object")
        integration_id = _nonempty_string(
            item.get("integration_id"),
            f"requirements[{index}].integration_id",
        )
        if integration_id in seen:
            raise ValueError(f"duplicate integration requirement: {integration_id}")
        seen.add(integration_id)
        result.append(
            ConnectionRequirement(
                integration_id=integration_id,
                target_required=_required_bool(
                    item.get("target_required"),
                    f"requirements[{index}].target_required",
                ),
                live_verification_required=_required_bool(
                    item.get("live_verification_required"),
                    f"requirements[{index}].live_verification_required",
                ),
            )
        )
    return tuple(result)


def _require_probe_evidence(
    evidence: tuple[ConnectionEvidence, ...],
    probe: str,
    label: str,
) -> None:
    if not any(item.operation == probe for item in evidence):
        raise ValueError(f"{label} requires evidence for registered probe {probe}")


def build_connection_report(
    repo_root: Path,
    payload: dict[str, object],
) -> ConnectionReport:
    if not isinstance(payload, dict):
        raise ValueError("preflight payload must be an object")

    registry = load_registry(Path(repo_root))
    requirements = _requirements(payload)
    integrations = payload.get("integrations", {})
    if not isinstance(integrations, dict):
        raise ValueError("integrations must be an object")

    observations: list[ConnectionObservation] = []
    blockers: list[str] = []

    for requirement in requirements:
        descriptor = registry.get(requirement.integration_id)
        if descriptor is None:
            raise ValueError(f"unknown integration id: {requirement.integration_id}")

        raw_signal = integrations.get(requirement.integration_id, {})
        if not isinstance(raw_signal, dict):
            raise ValueError(f"integrations.{requirement.integration_id} must be an object")

        connection = descriptor.connection
        label = f"integrations.{requirement.integration_id}"
        authenticated = _bool_or_none(
            raw_signal.get("authenticated"),
            f"{label}.authenticated",
        )
        target_accessible = _bool_or_none(
            raw_signal.get("target_accessible"),
            f"{label}.target_accessible",
        )
        evidence = _evidence_tuple(raw_signal.get("evidence"), f"{label}.evidence")

        if connection is not None and connection.auth_required and authenticated is not None:
            _require_probe_evidence(
                evidence,
                connection.safe_probe,
                f"{label}.safe_probe",
            )

        if requirement.target_required:
            if connection is None or connection.target_probe is None:
                raise ValueError(
                    f"{label}.target_required cannot be true: descriptor has no target_probe"
                )
            if target_accessible is not None:
                _require_probe_evidence(
                    evidence,
                    connection.target_probe,
                    f"{label}.target_probe",
                )

        signals = ConnectionSignals(
            configured=connection is not None,
            host_visible=_bool_or_none(
                raw_signal.get("host_visible"),
                f"{label}.host_visible",
            ),
            authenticated=authenticated,
            target_accessible=target_accessible,
            live_verified=_bool_or_none(
                raw_signal.get("live_verified"),
                f"{label}.live_verified",
            ),
            authentication_required=bool(connection and connection.auth_required),
            target_required=requirement.target_required,
            live_verification_required=requirement.live_verification_required,
            host_absence_status=_status_with_default(
                raw_signal.get("host_absence_status"),
                f"{label}.host_absence_status",
                ConnectionStatus.UNAVAILABLE,
            ),
            required_blocker=_blocking_status_or_none(
                raw_signal.get("required_blocker"),
                f"{label}.required_blocker",
            ),
            optional_degradations=_string_tuple(
                raw_signal.get("optional_degradations"),
                f"{label}.optional_degradations",
            ),
        )
        observation = evaluate_connection(
            requirement.integration_id,
            signals,
            evidence,
        )
        observations.append(observation)
        if observation.status not in _NON_BLOCKING:
            blockers.append(f"{observation.integration_id}:{observation.status.value}")

    return ConnectionReport(
        observations=tuple(observations),
        required_task_connections_pass=not blockers,
        blockers=tuple(blockers),
    )


def _process_layers_to_json(process_layers: object) -> dict[str, str]:
    if process_layers is None:
        return {}
    if not isinstance(process_layers, dict):
        raise ValueError("process_layers must be an object")
    result: dict[str, str] = {}
    for name in sorted(_PROCESS_LAYER_NAMES):
        if name not in process_layers:
            continue
        raw = process_layers[name]
        if not isinstance(raw, str) or raw not in _PROCESS_LAYER_STATUSES:
            raise ValueError(f"process_layers.{name} has unknown status")
        result[name] = raw
    return result


def report_to_json(
    report: ConnectionReport,
    *,
    process_layers: object = None,
) -> dict[str, object]:
    observations: list[dict[str, object]] = []
    for item in report.observations:
        observations.append(
            {
                "integration_id": item.integration_id,
                "configured": item.configured,
                "host_visible": item.host_visible,
                "authenticated": item.authenticated,
                "target_accessible": item.target_accessible,
                "live_verified": item.live_verified,
                "status": item.status.value,
                "detail": item.detail,
                "evidence": [
                    {
                        "source": evidence.source,
                        "operation": evidence.operation,
                        "observed_at": evidence.observed_at,
                        "target": evidence.target,
                        "summary": evidence.summary,
                    }
                    for evidence in item.evidence
                ],
            }
        )
    return {
        "observations": observations,
        "process_layers": _process_layers_to_json(process_layers),
        "required_task_connections_pass": report.required_task_connections_pass,
        "blockers": list(report.blockers),
    }
