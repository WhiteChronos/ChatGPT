"""Orquestração ponta a ponta do controle de comentários.

Fluxo:
relatório -> agente -> normalização -> gate determinístico -> persistência opcional
-> estatística -> exportação Power BI -> memória/log.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline.comment_control_agent import compile_comments, to_storage_payload
from pipeline.comment_control_analytics import summarize
from pipeline.comment_control_export_powerbi import export as export_powerbi
from pipeline.comment_control_pipeline import gate


def _stamp_missing_dates(payload: dict[str, Any]) -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    for record in payload.get("comments", []):
        record.setdefault("created_at", stamp)
        record.setdefault("verified_at", None)
        record.setdefault("verified_documents", [])
        record.setdefault("required_documents", [])
        record.setdefault("reopened_count", 0)
        record.setdefault("responsible", None)
        record.setdefault("verifier", None)
        record.setdefault("due_date", None)


def _normalize_new_divergences(payload: dict[str, Any]) -> None:
    normalized: list[dict[str, Any]] = []
    for idx, item in enumerate(payload.get("new_divergences", []), start=1):
        row = dict(item)
        row.setdefault("comment_id", f"ND{idx:02d}")
        row.setdefault("project_id", payload["project_id"])
        row.setdefault("severity", "ALTO")
        row.setdefault("origin_type", "NEW_DIVERGENCE")
        row.setdefault("status_control", "UNCHECKED")
        row.setdefault("original_comment", row.get("description") or row.get("compiled_action") or "Nova divergência")
        row.setdefault("compiled_action", row.get("action") or row.get("original_comment"))
        row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        row.setdefault("required_documents", [])
        row.setdefault("verified_documents", [])
        row.setdefault("evidence_text", None)
        normalized.append(row)
    payload["new_divergences"] = normalized


def build_full_record_set(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [*payload.get("comments", []), *payload.get("new_divergences", [])]


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

    compilation = await compile_comments(report_path.read_text(encoding="utf-8"), project_id)
    payload = to_storage_payload(compilation)
    _normalize_new_divergences(payload)
    _stamp_missing_dates(payload)

    # Somente comentários formais entram no gate de contagem principal.
    gate(payload)

    records = build_full_record_set(payload)
    analytics = summarize(records)

    payload_path = output_dir / "comment_control.json"
    analytics_path = output_dir / "comment_analytics.json"
    audit_path = output_dir / "audit_log.json"

    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    analytics_path.write_text(json.dumps(analytics, ensure_ascii=False, indent=2), encoding="utf-8")
    export_powerbi(records, output_dir / "powerbi")

    audit = {
        "project_id": project_id,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(report_path),
        "formal_comment_count": payload["source_formal_comment_count"],
        "registered_formal_comment_count": len(payload.get("comments", [])),
        "new_divergence_count": len(payload.get("new_divergences", [])),
        "status": "OK",
        "rules": [
            "preserve_all_formal_comments",
            "all_initial_status_unchecked",
            "checked_requires_human_evidence",
            "new_divergences_separate",
            "block_on_any_failure",
        ],
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    if persist_database:
        from pipeline.comment_control_db import persist_payload

        persist_payload({**payload, "comments": records})

    return {"payload": payload, "analytics": analytics, "audit": audit}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output-dir", default="out/comment-control")
    parser.add_argument("--persist-db", action="store_true")
    args = parser.parse_args()

    asyncio.run(run(args.report, args.project, args.output_dir, persist_database=args.persist_db))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
