"""Aplica respostas do solicitante às dúvidas do pré-flight.

Perguntas são resolvidas antes da emissão. Este módulo converte respostas em
estado resolvido e, quando aplicável, em erro confirmado ou objetivo formal.
Nenhuma pergunta é exportada para Excel/Word/PDF/Power BI.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_RESOLUTION_TYPES = {"CONFIRMED_ERROR", "DISMISSED", "FORMAL_OBJECTIVE"}
ALLOWED_SEVERITY = {"GRAVE", "ALTO", "LEVE"}


def _next_nd_id(payload: dict[str, Any]) -> str:
    used: set[int] = set()
    for item in payload.get("new_divergences", []):
        cid = str(item.get("comment_id") or "")
        if cid.startswith("ND") and cid[2:].isdigit():
            used.add(int(cid[2:]))
    candidate = 1
    while candidate in used:
        candidate += 1
    return f"ND{candidate:02d}"


def _require_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field} obrigatório")
    return text


def _build_confirmed_error(payload: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    source = dict(answer.get("confirmed_error") or {})
    severity = str(source.get("severity") or "ALTO").upper()
    if severity not in ALLOWED_SEVERITY:
        raise ValueError("confirmed_error.severity inválido")

    return {
        "comment_id": source.get("comment_id") or _next_nd_id(payload),
        "project_id": payload["project_id"],
        "source_comment_id": None,
        "severity": severity,
        "document_code": source.get("document_code"),
        "revision": source.get("revision"),
        "page_or_item": source.get("page_or_item"),
        "original_comment": _require_text(source.get("original_comment"), "confirmed_error.original_comment"),
        "compiled_action": _require_text(source.get("compiled_action"), "confirmed_error.compiled_action"),
        "finding_basis": source.get("finding_basis"),
        "source_location": source.get("source_location"),
        "required_documents": list(source.get("required_documents") or []),
        "verified_documents": [],
        "origin_type": "NEW_DIVERGENCE",
        "status_control": "UNCHECKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verified_at": None,
        "responsible": None,
        "verifier": None,
        "reopened_count": 0,
        "due_date": None,
        "evidence_text": None,
        "evidence_document": None,
        "evidence_revision": None,
        "evidence_location": None,
    }


def _build_formal_objective(payload: dict[str, Any], answer: dict[str, Any]) -> dict[str, Any]:
    source = dict(answer.get("formal_objective") or {})
    cid = _require_text(source.get("comment_id"), "formal_objective.comment_id")
    if not cid.startswith("C") or not cid[1:].isdigit():
        raise ValueError("formal_objective.comment_id deve seguir Cxx")
    severity = str(source.get("severity") or "ALTO").upper()
    if severity not in ALLOWED_SEVERITY:
        raise ValueError("formal_objective.severity inválido")
    return {
        "comment_id": cid,
        "project_id": payload["project_id"],
        "source_comment_id": cid,
        "severity": severity,
        "document_code": source.get("document_code"),
        "revision": source.get("revision"),
        "page_or_item": source.get("page_or_item"),
        "original_comment": _require_text(source.get("original_comment"), "formal_objective.original_comment"),
        "compiled_action": _require_text(source.get("compiled_action"), "formal_objective.compiled_action"),
        "finding_basis": source.get("finding_basis"),
        "source_location": source.get("source_location"),
        "required_documents": list(source.get("required_documents") or []),
        "verified_documents": [],
        "origin_type": "FORMAL_COMMENT",
        "status_control": "UNCHECKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verified_at": None,
        "responsible": None,
        "verifier": None,
        "reopened_count": 0,
        "due_date": None,
        "evidence_text": None,
        "evidence_document": None,
        "evidence_revision": None,
        "evidence_location": None,
    }


def apply_clarification_resolutions(
    payload: dict[str, Any],
    resolution_payload: dict[str, Any],
    *,
    resolved_by: str | None = None,
) -> dict[str, Any]:
    """Aplica respostas sem exportar a pergunta original.

    `resolution_payload` deve conter `answers`, cada uma com `question_id`,
    `resolution`, `resolution_type` e, quando aplicável, `confirmed_error` ou
    `formal_objective`.
    """
    updated = deepcopy(payload)
    answers = resolution_payload.get("answers") or []
    if not isinstance(answers, list):
        raise ValueError("answers deve ser uma lista")

    answer_by_id: dict[str, dict[str, Any]] = {}
    for answer in answers:
        qid = _require_text(answer.get("question_id"), "question_id")
        if qid in answer_by_id:
            raise ValueError(f"Resposta duplicada para {qid}")
        answer_by_id[qid] = dict(answer)

    actor = resolved_by or resolution_payload.get("resolved_by") or "solicitante"
    now = datetime.now(timezone.utc).isoformat()

    for question in updated.get("clarification_questions", []):
        if str(question.get("status", "OPEN")).upper() != "OPEN":
            continue
        qid = str(question.get("question_id") or "")
        answer = answer_by_id.get(qid)
        if not answer:
            continue

        resolution = _require_text(answer.get("resolution"), f"{qid}.resolution")
        resolution_type = str(answer.get("resolution_type") or "").upper()
        if resolution_type not in ALLOWED_RESOLUTION_TYPES:
            raise ValueError(f"{qid}.resolution_type inválido")

        question["resolution"] = resolution
        question["resolution_type"] = resolution_type
        question["resolved_by"] = actor
        question["resolved_at"] = now

        if resolution_type == "DISMISSED":
            question["status"] = "DISMISSED"
        elif resolution_type == "CONFIRMED_ERROR":
            question["status"] = "RESOLVED"
            updated.setdefault("new_divergences", []).append(_build_confirmed_error(updated, answer))
        elif resolution_type == "FORMAL_OBJECTIVE":
            question["status"] = "RESOLVED"
            updated.setdefault("comments", []).append(_build_formal_objective(updated, answer))
            updated["source_formal_comment_count"] = len(
                [r for r in updated.get("comments", []) if r.get("origin_type") == "FORMAL_COMMENT"]
            )

    open_count = sum(
        1
        for question in updated.get("clarification_questions", [])
        if str(question.get("status", "OPEN")).upper() == "OPEN"
    )
    updated["preflight_status"] = "READY_TO_GENERATE" if open_count == 0 else "WAITING_CLARIFICATION"
    return updated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("resolutions")
    parser.add_argument("--output", default="resolved_payload.json")
    parser.add_argument("--resolved-by")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    resolutions = json.loads(Path(args.resolutions).read_text(encoding="utf-8"))
    resolved = apply_clarification_resolutions(payload, resolutions, resolved_by=args.resolved_by)
    Path(args.output).write_text(json.dumps(resolved, ensure_ascii=False, indent=2), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
