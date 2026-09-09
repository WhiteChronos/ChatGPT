"""Orquestração ponta a ponta do controle de comentários.

Fluxo normal:
material -> agente -> resolução interna -> gate de dúvidas -> validação determinística
-> Excel governado -> persistência -> analítica.

Fluxo de retomada:
preflight_payload.json + respostas -> aplicação determinística das respostas -> gate
-> geração dos artefatos.

Nenhum artefato de entrega é gerado enquanto existir dúvida aberta.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.comment_control_agent import compile_comments, to_storage_payload
from pipeline.comment_control_analytics import summarize
from pipeline.comment_control_clarification import apply_clarification_resolutions
from pipeline.comment_control_excel import export_excel
from pipeline.comment_control_export_powerbi import export as export_powerbi
from pipeline.comment_control_pipeline import ClarificationRequired, gate, open_clarification_questions


def _stamp_record_defaults(record: dict[str, Any], stamp: str) -> None:
    record.setdefault("created_at", stamp)
    record.setdefault("verified_at", None)
    record.setdefault("verified_documents", [])
    record.setdefault("required_documents", [])
    record.setdefault("reopened_count", 0)
    record.setdefault("responsible", None)
    record.setdefault("verifier", None)
    record.setdefault("due_date", None)
    record.setdefault("evidence_text", None)
    record.setdefault("evidence_document", None)
    record.setdefault("evidence_revision", None)
    record.setdefault("evidence_location", None)
    record.setdefault("finding_basis", None)
    record.setdefault("source_location", None)


def _stamp_missing_dates(payload: dict[str, Any]) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    for record in payload.get("comments", []):
        _stamp_record_defaults(record, stamp)
    for record in payload.get("new_divergences", []):
        _stamp_record_defaults(record, stamp)


def _normalize_new_divergences(payload: dict[str, Any]) -> None:
    normalized: list[dict[str, Any]] = []
    used_ids: set[str] = set()
    next_number = 1
    for item in payload.get("new_divergences", []):
        row = dict(item)
        cid = str(row.get("comment_id") or "")
        if not cid:
            while f"ND{next_number:02d}" in used_ids:
                next_number += 1
            cid = f"ND{next_number:02d}"
        used_ids.add(cid)
        row["comment_id"] = cid
        row.setdefault("project_id", payload["project_id"])
        row.setdefault("severity", "ALTO")
        row.setdefault("origin_type", "NEW_DIVERGENCE")
        row.setdefault("status_control", "UNCHECKED")
        row.setdefault("source_comment_id", None)
        row.setdefault("original_comment", row.get("description") or row.get("compiled_action") or "Nova divergência")
        row.setdefault("compiled_action", row.get("action") or row.get("original_comment"))
        row.setdefault("finding_basis", None)
        row.setdefault("source_location", None)
        normalized.append(row)
    payload["new_divergences"] = normalized


def _attach_source_identity(payload: dict[str, Any], report_path: Path, report_bytes: bytes) -> None:
    source_hash = hashlib.sha256(report_bytes).hexdigest()
    payload["source_name"] = report_path.name
    payload["source_hash"] = source_hash
    payload["batch_id"] = f"{payload['project_id']}:{source_hash[:20]}"


def build_full_record_set(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [*payload.get("comments", []), *payload.get("new_divergences", [])]


def _write_preflight(output_dir: Path, payload: dict[str, Any]) -> None:
    questions = open_clarification_questions(payload)
    (output_dir / "preflight_payload.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "clarification_questions.json").write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "preflight_status.json").write_text(
        json.dumps(
            {
                "project_id": payload["project_id"],
                "batch_id": payload["batch_id"],
                "status": "WAITING_CLARIFICATION",
                "open_question_count": len(questions),
                "artifact_generation": "BLOCKED",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _generate_artifacts(
    payload: dict[str, Any],
    output_dir: Path,
    *,
    source_report: str,
    persist_database: bool,
) -> dict[str, Any]:
    _normalize_new_divergences(payload)
    _stamp_missing_dates(payload)

    questions = open_clarification_questions(payload)
    if questions:
        payload["preflight_status"] = "WAITING_CLARIFICATION"
        _write_preflight(output_dir, payload)
        if persist_database:
            from pipeline.comment_control_db import persist_preflight

            persist_preflight(payload)
        raise ClarificationRequired(questions)

    payload["preflight_status"] = "READY_TO_GENERATE"
    gate(payload)

    records = build_full_record_set(payload)
    analytics = summarize(records)

    payload_path = output_dir / "comment_control.json"
    analytics_path = output_dir / "comment_analytics.json"
    audit_path = output_dir / "audit_log.json"
    excel_path = output_dir / "comment_control.xlsx"

    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    analytics_path.write_text(json.dumps(analytics, ensure_ascii=False, indent=2), encoding="utf-8")
    export_excel(payload, excel_path)
    export_powerbi(records, output_dir / "powerbi")

    payload["preflight_status"] = "GENERATED"
    audit = {
        "project_id": payload["project_id"],
        "batch_id": payload.get("batch_id"),
        "source_hash": payload.get("source_hash"),
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source_report": source_report,
        "formal_comment_count": payload["source_formal_comment_count"],
        "registered_formal_comment_count": len(payload.get("comments", [])),
        "new_divergence_count": len(payload.get("new_divergences", [])),
        "open_clarification_count": 0,
        "excel_output": str(excel_path),
        "status": "OK",
        "rules": [
            "preserve_all_formal_comments",
            "all_initial_status_unchecked",
            "clarifications_resolved_before_artifact",
            "questions_never_exported",
            "new_divergences_separate",
            "block_on_any_failure",
        ],
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    if persist_database:
        from pipeline.comment_control_db import persist_payload

        persist_payload({**payload, "comments": records})

    return {"payload": payload, "analytics": analytics, "audit": audit}


async def run(
    report_path: str | Path,
    project_id: str,
    output_dir: str | Path,
    *,
    persist_database: bool = False,
) -> dict[str, Any]:
    report_path = Path(report_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_bytes = report_path.read_bytes()
    report_text = report_bytes.decode("utf-8")
    compilation = await compile_comments(report_text, project_id)
    payload = to_storage_payload(compilation)
    _attach_source_identity(payload, report_path, report_bytes)
    _normalize_new_divergences(payload)
    _stamp_missing_dates(payload)

    questions = open_clarification_questions(payload)
    if questions:
        payload["preflight_status"] = "WAITING_CLARIFICATION"
        _write_preflight(output_dir, payload)
        if persist_database:
            from pipeline.comment_control_db import persist_preflight

            persist_preflight(payload)
        raise ClarificationRequired(questions)

    return _generate_artifacts(
        payload,
        output_dir,
        source_report=str(report_path),
        persist_database=persist_database,
    )


def resume(
    payload_path: str | Path,
    resolutions_path: str | Path,
    output_dir: str | Path,
    *,
    persist_database: bool = False,
    resolved_by: str | None = None,
) -> dict[str, Any]:
    payload_path = Path(payload_path)
    resolutions_path = Path(resolutions_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    resolutions = json.loads(resolutions_path.read_text(encoding="utf-8"))
    payload = apply_clarification_resolutions(payload, resolutions, resolved_by=resolved_by)

    (output_dir / "resolved_preflight_payload.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return _generate_artifacts(
        payload,
        output_dir,
        source_report=str(payload.get("source_name") or payload_path),
        persist_database=persist_database,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", nargs="?")
    parser.add_argument("--project")
    parser.add_argument("--output-dir", default="out/comment-control")
    parser.add_argument("--persist-db", action="store_true")
    parser.add_argument("--resume-payload")
    parser.add_argument("--resolutions")
    parser.add_argument("--resolved-by")
    args = parser.parse_args()

    try:
        if args.resume_payload:
            if not args.resolutions:
                parser.error("--resolutions é obrigatório com --resume-payload")
            resume(
                args.resume_payload,
                args.resolutions,
                args.output_dir,
                persist_database=args.persist_db,
                resolved_by=args.resolved_by,
            )
        else:
            if not args.report or not args.project:
                parser.error("report e --project são obrigatórios no fluxo inicial")
            asyncio.run(run(args.report, args.project, args.output_dir, persist_database=args.persist_db))
    except ClarificationRequired as exc:
        print(str(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
