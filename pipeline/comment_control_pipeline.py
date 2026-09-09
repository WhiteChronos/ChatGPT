"""Pipeline determinístico de validação, pré-verificação, memória e exportação."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ALLOWED_SEVERITY = {"GRAVE", "ALTO", "LEVE"}
ALLOWED_STATUS = {"UNCHECKED", "CHECKED"}
ALLOWED_ORIGIN = {"FORMAL_COMMENT", "NEW_DIVERGENCE"}
ALLOWED_QUESTION_STATUS = {"OPEN", "RESOLVED", "DISMISSED"}
PROHIBITED_EXPORT_MARKERS = ("DÚVIDA", "DUVIDA", "A CONFIRMAR", "PERGUNTA")
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "comment_control_v1.schema.json"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    item_id: str | None = None


class ClarificationRequired(RuntimeError):
    """Sinaliza que o lote não pode gerar artefatos até as perguntas serem resolvidas."""

    def __init__(self, questions: list[dict[str, Any]]):
        self.questions = questions
        text = "\n".join(
            f"{q.get('question_id', 'Q?')}: {q.get('question_text', '')}" for q in questions
        )
        super().__init__(f"WAITING_CLARIFICATION\n{text}")


def _formal_comments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in payload.get("comments", []) if r.get("origin_type") == "FORMAL_COMMENT"]


def open_clarification_questions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        q
        for q in payload.get("clarification_questions", [])
        if str(q.get("status", "OPEN")).upper() == "OPEN"
    ]


def assert_preflight_resolved(payload: dict[str, Any]) -> None:
    questions = open_clarification_questions(payload)
    if questions:
        raise ClarificationRequired(questions)


def _schema_validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def validate_schema(record: dict[str, Any]) -> list[Finding]:
    cid = str(record.get("comment_id", "UNKNOWN"))
    findings: list[Finding] = []
    for error in sorted(_schema_validator().iter_errors(record), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "record"
        findings.append(Finding("CC-SCHEMA", "CRITICAL", f"{location}: {error.message}", cid))
    return findings


def _contains_internal_question_marker(record: dict[str, Any]) -> bool:
    if record.get("origin_type") != "NEW_DIVERGENCE":
        return False
    texts = [str(record.get("original_comment") or ""), str(record.get("compiled_action") or "")]
    upper = " ".join(texts).upper()
    return any(marker in upper for marker in PROHIBITED_EXPORT_MARKERS) or "?" in upper


def validate_record(record: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    cid = str(record.get("comment_id", "UNKNOWN"))
    findings.extend(validate_schema(record))

    if record.get("severity") not in ALLOWED_SEVERITY:
        findings.append(Finding("CC-SEVERITY", "CRITICAL", "Grau inválido", cid))
    if record.get("status_control") not in ALLOWED_STATUS:
        findings.append(Finding("CC-STATUS", "CRITICAL", "Status inválido", cid))
    if record.get("origin_type") not in ALLOWED_ORIGIN:
        findings.append(Finding("CC-ORIGIN", "CRITICAL", "Origem inválida", cid))
    if not record.get("original_comment"):
        findings.append(Finding("CC-ORIGINAL", "CRITICAL", "Comentário original ausente", cid))
    if not record.get("compiled_action"):
        findings.append(Finding("CC-ACTION", "CRITICAL", "Ação compilada ausente", cid))
    if _contains_internal_question_marker(record):
        findings.append(
            Finding(
                "CC-QUESTION-IN-EXPORT",
                "CRITICAL",
                "Nova divergência contém dúvida/pergunta interna e não pode ser exportada",
                cid,
            )
        )

    if record.get("status_control") == "CHECKED":
        if not record.get("evidence_text"):
            findings.append(Finding("CC-CHECKED-EVIDENCE", "CRITICAL", "☑ sem evidência documental", cid))
        if not record.get("verified_at") or not record.get("verifier"):
            findings.append(Finding("CC-HUMAN-VERIFY", "CRITICAL", "☑ sem registro do verificador/data", cid))
        required = set(record.get("required_documents") or [])
        verified = set(record.get("verified_documents") or [])
        missing = required - verified
        if missing:
            findings.append(
                Finding(
                    "CC-MULTIDOC-EVIDENCE",
                    "CRITICAL",
                    f"☑ sem evidência para todos os documentos: {', '.join(sorted(missing))}",
                    cid,
                )
            )
    return findings


def validate_payload(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    comments = payload.get("comments", [])
    for record in comments:
        findings.extend(validate_record(record))

    for question in payload.get("clarification_questions", []):
        status = str(question.get("status", "OPEN")).upper()
        if status not in ALLOWED_QUESTION_STATUS:
            findings.append(
                Finding(
                    "CC-QUESTION-STATUS",
                    "CRITICAL",
                    f"Status de dúvida inválido: {status}",
                    str(question.get("question_id", "Q?")),
                )
            )
        if status == "OPEN":
            findings.append(
                Finding(
                    "CC-CLARIFICATION-OPEN",
                    "CRITICAL",
                    "Existe dúvida não sanada; a elaboração deve ser interrompida antes de gerar artefatos",
                    str(question.get("question_id", "Q?")),
                )
            )

    formal = _formal_comments(payload)
    source_count = payload.get("source_formal_comment_count")
    if source_count != len(formal):
        findings.append(
            Finding(
                "CC-COUNT-INTEGRITY",
                "CRITICAL",
                f"Quantidade da origem={source_count!r}; registrada={len(formal)}",
            )
        )

    ids = [r.get("comment_id") for r in formal]
    duplicate_ids = [cid for cid, count in Counter(ids).items() if count > 1]
    if duplicate_ids:
        findings.append(
            Finding("CC-DUPLICATE", "CRITICAL", f"Comentários duplicados: {', '.join(map(str, duplicate_ids))}")
        )

    automatically_checked = [
        r.get("comment_id")
        for r in comments
        if r.get("status_control") == "CHECKED" and (not r.get("verified_at") or not r.get("verifier"))
    ]
    if automatically_checked:
        findings.append(
            Finding(
                "CC-AUTO-CHECK",
                "CRITICAL",
                "Status CHECKED sem verificação humana explícita: " + ", ".join(map(str, automatically_checked)),
            )
        )

    return findings


def gate(payload: dict[str, Any]) -> None:
    findings = validate_payload(payload)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    if critical:
        questions = open_clarification_questions(payload)
        if questions:
            raise ClarificationRequired(questions)
        text = "\n".join(f"{f.code}: {f.message}" for f in critical)
        raise ValueError(f"BLOCK_ON_ANY_FAILURE\n{text}")


def append_memory_event(
    memory_path: Path,
    *,
    category: str,
    description: str,
    origin: str,
    regression_test: str | None = None,
) -> None:
    event = {
        "id": f"MEM-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "description": description,
        "status": "ACTIVE",
        "origin": origin,
        "regression_test": regression_test,
    }
    existing: list[dict[str, Any]] = []
    if memory_path.exists():
        existing = json.loads(memory_path.read_text(encoding="utf-8"))
    existing.append(event)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def run(input_path: str | Path, output_path: str | Path | None = None) -> dict[str, Any]:
    input_path = Path(input_path)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    gate(payload)
    payload["pipeline_validation"] = {
        "status": "OK",
        "preflight_status": "READY_TO_GENERATE",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "formal_comment_count": len(_formal_comments(payload)),
        "open_clarification_count": 0,
    }
    if output_path:
        Path(output_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    run(args.input, args.output)
