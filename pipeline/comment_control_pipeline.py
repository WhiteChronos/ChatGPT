"""Pipeline determinístico de validação, memória e exportação de comentários."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ALLOWED_SEVERITY = {"GRAVE", "ALTO", "LEVE"}
ALLOWED_STATUS = {"UNCHECKED", "CHECKED"}
ALLOWED_ORIGIN = {"FORMAL_COMMENT", "NEW_DIVERGENCE"}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    item_id: str | None = None


def _formal_comments(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in payload.get("comments", []) if r.get("origin_type") == "FORMAL_COMMENT"]


def validate_record(record: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    cid = str(record.get("comment_id", "UNKNOWN"))
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

    if record.get("status_control") == "CHECKED":
        if not record.get("evidence_text"):
            findings.append(Finding("CC-CHECKED-EVIDENCE", "CRITICAL", "☑ sem evidência documental", cid))
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

    automatically_checked = [r.get("comment_id") for r in comments if r.get("status_control") == "CHECKED" and not r.get("verified_at")]
    if automatically_checked:
        findings.append(
            Finding(
                "CC-AUTO-CHECK",
                "CRITICAL",
                "Status CHECKED sem registro explícito de verificação humana: " + ", ".join(map(str, automatically_checked)),
            )
        )

    return findings


def gate(payload: dict[str, Any]) -> None:
    findings = validate_payload(payload)
    critical = [f for f in findings if f.severity == "CRITICAL"]
    if critical:
        text = "\n".join(f"{f.code}: {f.message}" for f in critical)
        raise ValueError(f"BLOCK_ON_ANY_FAILURE\n{text}")


def append_memory_event(memory_path: Path, *, category: str, description: str, origin: str, regression_test: str | None = None) -> None:
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
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "formal_comment_count": len(_formal_comments(payload)),
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
