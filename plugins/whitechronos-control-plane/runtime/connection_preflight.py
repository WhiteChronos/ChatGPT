from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
    target: str | None
    live_verification_required: bool
    live_operation: str | None


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
_PROCESS_LAYER_NAMES = {"SUPERPOWERS", "ARENA", "RUNTIME_DOCTOR", "MIRROR_PARITY"}
_PROCESS_LAYER_STATUSES = {status.value for status in ConnectionStatus}
_MIRROR_PARITY_STATUSES = {"HEALTHY", "FAIL", "DIVERGED", "STALE", "UNAVAILABLE", "NOT_APPLICABLE"}
_EVIDENCE_MAX_AGE = timedelta(minutes=15)
_EVIDENCE_FUTURE_SKEW = timedelta(minutes=5)
_SECRET_PATTERNS = (
    re.compile(r"\bauthorization\s*[:=]\s*(?:bearer|basic)\s+\S+", re.IGNORECASE),
    re.compile(
        r"\b(?:access[_-]?token|refresh[_-]?token|api[_-]?key|password|cookie|token|client_secret)\s*[:=]\s*\S+",
        re.IGNORECASE,
    ),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bya29\.[A-Za-z0-9._-]{10,}\b"),
)
_SAFE_IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9_.:-]{0,63}$")
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_PROCESS_LAYER_TRUSTED_SOURCES = {
    "SUPERPOWERS": {"superpowers-runtime"},
    "ARENA": {"github-arena"},
    "RUNTIME_DOCTOR": {"runtime-doctor"},
    "MIRROR_PARITY": {"canonical-mirror-parity"},
}
_PROCESS_LAYER_POSITIVE = {
    "SUPERPOWERS": {"PASS", "DEGRADED", "NOT_APPLICABLE"},
    "ARENA": {"PASS", "DEGRADED", "NOT_APPLICABLE"},
    "RUNTIME_DOCTOR": {"PASS", "DEGRADED", "NOT_APPLICABLE"},
    "MIRROR_PARITY": {"HEALTHY", "NOT_APPLICABLE"},
}


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


def _safe_identifier_tuple(value: object, label: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    result: list[str] = []
    for index, item in enumerate(value):
        item_text = _nonempty_string(item, f"{label}[{index}]")
        if not _SAFE_IDENTIFIER_RE.fullmatch(item_text):
            raise ValueError(f"{label}[{index}] must be a safe identifier")
        result.append(item_text)
    return tuple(result)


def _timestamp(value: object, label: str) -> tuple[str, datetime]:
    text = _nonempty_string(value, label)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp with timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{label} must include timezone")
    return text, parsed.astimezone(timezone.utc)


def _require_fresh_timestamp(observed_at: datetime, label: str, now: datetime) -> None:
    if observed_at < now - _EVIDENCE_MAX_AGE:
        raise ValueError(f"{label}: evidence is stale")
    if observed_at > now + _EVIDENCE_FUTURE_SKEW:
        raise ValueError(f"{label}: evidence timestamp is implausibly future-dated")


def _reject_secret_like(value: str | None, label: str) -> None:
    if value is None:
        return
    if any(pattern.search(value) for pattern in _SECRET_PATTERNS):
        raise ValueError(f"{label}: evidence contains secret-like content")


def _evidence_tuple(
    value: object,
    label: str,
    *,
    now: datetime,
) -> tuple[ConnectionEvidence, ...]:
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
        observed_at, observed_dt = _timestamp(item.get("observed_at"), f"{item_label}.observed_at")
        _require_fresh_timestamp(observed_dt, f"{item_label}.observed_at", now)
        target = item.get("target")
        if target is not None and not isinstance(target, str):
            raise ValueError(f"{item_label}.target must be a string or null")
        outcome = _nonempty_string(item.get("outcome"), f"{item_label}.outcome")
        if outcome not in {"success", "failure"}:
            raise ValueError(f"{item_label}.outcome must be success or failure")
        raw_summary = item.get("summary")
        if raw_summary is not None and not isinstance(raw_summary, str):
            raise ValueError(f"{item_label}.summary must be a string or null")
        for evidence_value, field in (
            (source, "source"),
            (operation, "operation"),
            (target, "target"),
        ):
            _reject_secret_like(evidence_value, f"{item_label}.{field}")
        result.append(
            ConnectionEvidence(
                source=source,
                operation=operation,
                observed_at=observed_at,
                target=target,
                outcome=outcome,
                summary="provider evidence normalized",
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
        target_required = _required_bool(
            item.get("target_required"),
            f"requirements[{index}].target_required",
        )
        target = item.get("target")
        if target is not None:
            target = _nonempty_string(target, f"requirements[{index}].target")
        if target_required and target is None:
            raise ValueError(f"requirements[{index}].target is required when target_required is true")

        live_verification_required = _required_bool(
            item.get("live_verification_required"),
            f"requirements[{index}].live_verification_required",
        )
        live_operation = item.get("live_operation")
        if live_operation is not None:
            live_operation = _nonempty_string(
                live_operation,
                f"requirements[{index}].live_operation",
            )
        if live_verification_required and live_operation is None:
            raise ValueError(
                f"requirements[{index}].live_operation is required when live_verification_required is true"
            )

        result.append(
            ConnectionRequirement(
                integration_id=integration_id,
                target_required=target_required,
                target=target,
                live_verification_required=live_verification_required,
                live_operation=live_operation,
            )
        )
    return tuple(result)


def _require_probe_evidence(
    evidence: tuple[ConnectionEvidence, ...],
    probe: str,
    label: str,
    *,
    trusted_sources: tuple[str, ...],
    expected_target: str | None = None,
) -> None:
    candidates = [
        item
        for item in evidence
        if item.operation == probe
        and (expected_target is None or item.target == expected_target)
    ]
    if not candidates:
        if expected_target is None:
            raise ValueError(f"{label} requires evidence for registered probe {probe}")
        raise ValueError(
            f"{label} requires evidence for registered probe {probe} on target {expected_target}"
        )
    if not any(item.source in trusted_sources for item in candidates):
        raise ValueError(f"{label} requires evidence from a trusted source")
    if not any(
        item.source in trusted_sources and item.outcome == "success"
        for item in candidates
    ):
        raise ValueError(f"{label} requires a successful probe outcome")


def build_connection_report(
    repo_root: Path,
    payload: dict[str, object],
) -> ConnectionReport:
    if not isinstance(payload, dict):
        raise ValueError("preflight payload must be an object")

    registry = load_registry(Path(repo_root))
    requirements = _requirements(payload)
    now = datetime.now(timezone.utc)
    subject_sha = payload.get("subject_sha")
    process_layers = _process_layers_to_json(
        payload.get("process_layers"),
        now=now,
        subject_sha=subject_sha,
    )
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
        evidence = _evidence_tuple(
            raw_signal.get("evidence"),
            f"{label}.evidence",
            now=now,
        )

        if connection is not None and connection.auth_required and authenticated is not None:
            _require_probe_evidence(
                evidence,
                connection.safe_probe,
                f"{label}.safe_probe",
                trusted_sources=connection.trusted_evidence_sources,
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
                    trusted_sources=connection.trusted_evidence_sources,
                    expected_target=requirement.target,
                )

        live_verified = _bool_or_none(
            raw_signal.get("live_verified"),
            f"{label}.live_verified",
        )
        if requirement.live_verification_required and live_verified is True:
            _require_probe_evidence(
                evidence,
                requirement.live_operation or "",
                f"{label}.live_verification",
                trusted_sources=connection.trusted_evidence_sources if connection else (),
                expected_target=requirement.target,
            )

        signals = ConnectionSignals(
            configured=connection is not None,
            host_visible=_bool_or_none(
                raw_signal.get("host_visible"),
                f"{label}.host_visible",
            ),
            authenticated=authenticated,
            target_accessible=target_accessible,
            live_verified=live_verified,
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
            optional_degradations=_safe_identifier_tuple(
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

    for name, status in process_layers.items():
        if name == "MIRROR_PARITY":
            if status not in {"HEALTHY", "NOT_APPLICABLE"}:
                blockers.append(f"{name}:{status}")
        elif status not in {
            ConnectionStatus.PASS.value,
            ConnectionStatus.DEGRADED.value,
            ConnectionStatus.NOT_APPLICABLE.value,
        }:
            blockers.append(f"{name}:{status}")

    return ConnectionReport(
        observations=tuple(observations),
        required_task_connections_pass=not blockers,
        blockers=tuple(blockers),
    )


def _process_layers_to_json(
    process_layers: object,
    *,
    now: datetime | None = None,
    subject_sha: object = None,
) -> dict[str, str]:
    if process_layers is None:
        return {}
    if not isinstance(process_layers, dict):
        raise ValueError("process_layers must be an object")
    unknown = sorted(set(process_layers) - _PROCESS_LAYER_NAMES)
    if unknown:
        raise ValueError(f"unknown process layer: {unknown[0]}")
    evaluated_at = now or datetime.now(timezone.utc)
    result: dict[str, str] = {}
    for name in sorted(_PROCESS_LAYER_NAMES):
        if name not in process_layers:
            continue
        raw = process_layers[name]
        allowed = _MIRROR_PARITY_STATUSES if name == "MIRROR_PARITY" else _PROCESS_LAYER_STATUSES
        if isinstance(raw, str):
            if raw not in allowed:
                raise ValueError(f"process_layers.{name} has unknown status")
            if raw in _PROCESS_LAYER_POSITIVE[name]:
                raise ValueError(
                    f"process_layers.{name} positive status requires structured authoritative evidence"
                )
            result[name] = raw
            continue
        if not isinstance(raw, dict):
            raise ValueError(f"process_layers.{name} must be a status string or structured evidence")
        permitted = {"status", "source", "observed_at", "subject_sha", "evidence_eligible"}
        extras = sorted(set(raw) - permitted)
        if extras:
            raise ValueError(f"process_layers.{name} has unknown field {extras[0]}")
        status = _nonempty_string(raw.get("status"), f"process_layers.{name}.status")
        if status not in allowed:
            raise ValueError(f"process_layers.{name} has unknown status")
        source = _nonempty_string(raw.get("source"), f"process_layers.{name}.source")
        _, observed_dt = _timestamp(
            raw.get("observed_at"),
            f"process_layers.{name}.observed_at",
        )
        _require_fresh_timestamp(
            observed_dt,
            f"process_layers.{name}.observed_at",
            evaluated_at,
        )
        if status in _PROCESS_LAYER_POSITIVE[name]:
            allowed_sources = (
                {"task-scope"}
                if status == "NOT_APPLICABLE"
                else _PROCESS_LAYER_TRUSTED_SOURCES[name]
            )
            if source not in allowed_sources:
                raise ValueError(f"process_layers.{name} requires an authoritative source")
        _reject_secret_like(source, f"process_layers.{name}.source")
        if name == "MIRROR_PARITY" and status == "HEALTHY":
            mirror_sha = _nonempty_string(
                raw.get("subject_sha"),
                "process_layers.MIRROR_PARITY.subject_sha",
            )
            expected_sha = _nonempty_string(subject_sha, "subject_sha")
            if not _SHA_RE.fullmatch(mirror_sha) or not _SHA_RE.fullmatch(expected_sha):
                raise ValueError("process_layers.MIRROR_PARITY subject SHA must be 40 hex characters")
            if mirror_sha.lower() != expected_sha.lower():
                raise ValueError("process_layers.MIRROR_PARITY subject SHA mismatch")
            if raw.get("evidence_eligible") is not True:
                raise ValueError("process_layers.MIRROR_PARITY requires evidence_eligible=true")
        result[name] = status
    return result

def report_to_json(
    report: ConnectionReport,
    *,
    process_layers: object = None,
    subject_sha: object = None,
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
                        "outcome": evidence.outcome,
                        "summary": evidence.summary,
                    }
                    for evidence in item.evidence
                ],
            }
        )
    return {
        "observations": observations,
        "process_layers": _process_layers_to_json(
            process_layers,
            subject_sha=subject_sha,
        ),
        "required_task_connections_pass": report.required_task_connections_pass,
        "blockers": list(report.blockers),
    }
