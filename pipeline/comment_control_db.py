"""Persistência PostgreSQL para o sistema de controle de comentários.

A fonte de verdade é o banco. Dúvidas são persistidas no pré-flight e nunca são
misturadas aos comentários exportáveis.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator


def _psycopg():
    try:
        import psycopg  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Instale psycopg[binary] para persistência PostgreSQL") from exc
    return psycopg


@contextmanager
def connect(database_url: str | None = None) -> Iterator[Any]:
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL ausente")
    psycopg = _psycopg()
    with psycopg.connect(url) as conn:
        yield conn


def upsert_project(conn: Any, project_id: str, project_name: str | None = None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into projects(project_id, project_name)
            values (%s, %s)
            on conflict(project_id) do update set project_name = excluded.project_name
            """,
            (project_id, project_name or project_id),
        )


def upsert_batch(conn: Any, payload: dict[str, Any]) -> str:
    batch_id = payload.get("batch_id")
    if not batch_id:
        raise ValueError("batch_id obrigatório para persistência")

    with conn.cursor() as cur:
        cur.execute(
            """
            insert into comment_batches(
              batch_id, project_id, source_name, source_hash,
              source_formal_comment_count, preflight_status, updated_at
            ) values (%s, %s, %s, %s, %s, %s, now())
            on conflict(batch_id) do update set
              source_name = excluded.source_name,
              source_hash = excluded.source_hash,
              source_formal_comment_count = excluded.source_formal_comment_count,
              preflight_status = excluded.preflight_status,
              updated_at = now()
            """,
            (
                batch_id,
                payload["project_id"],
                payload.get("source_name"),
                payload.get("source_hash"),
                payload["source_formal_comment_count"],
                payload.get("preflight_status", "ANALYZING"),
            ),
        )
    return str(batch_id)


def replace_clarification_questions(conn: Any, batch_id: str, questions: list[dict[str, Any]]) -> None:
    with conn.cursor() as cur:
        cur.execute("delete from clarification_questions where batch_id = %s", (batch_id,))
        for question in questions:
            cur.execute(
                """
                insert into clarification_questions(
                  batch_id, question_id, topic, question_text, why_needed,
                  related_documents, status, resolution, resolution_type,
                  resolved_by, resolved_at
                ) values (
                  %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s::timestamptz
                )
                """,
                (
                    batch_id,
                    question.get("question_id"),
                    question.get("topic"),
                    question.get("question_text"),
                    question.get("why_needed"),
                    __import__("json").dumps(question.get("related_documents") or []),
                    question.get("status", "OPEN"),
                    question.get("resolution"),
                    question.get("resolution_type"),
                    question.get("resolved_by"),
                    question.get("resolved_at"),
                ),
            )


def insert_comment(conn: Any, batch_id: str, record: dict[str, Any]) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into comments(
              batch_id, project_id, comment_id, source_comment_id, severity, document_code,
              revision, page_or_item, original_comment, compiled_action,
              finding_basis, source_location, origin_type, status_control,
              responsible, verifier, created_at, verified_at, reopened_count, due_date
            ) values (
              %(batch_id)s, %(project_id)s, %(comment_id)s, %(source_comment_id)s, %(severity)s,
              %(document_code)s, %(revision)s, %(page_or_item)s,
              %(original_comment)s, %(compiled_action)s,
              %(finding_basis)s, %(source_location)s, %(origin_type)s,
              %(status_control)s, %(responsible)s, %(verifier)s,
              coalesce(%(created_at)s::timestamptz, now()),
              %(verified_at)s::timestamptz, coalesce(%(reopened_count)s, 0),
              %(due_date)s::date
            )
            on conflict(batch_id, comment_id, origin_type) do update set
              severity = excluded.severity,
              document_code = excluded.document_code,
              revision = excluded.revision,
              page_or_item = excluded.page_or_item,
              original_comment = excluded.original_comment,
              compiled_action = excluded.compiled_action,
              finding_basis = excluded.finding_basis,
              source_location = excluded.source_location,
              responsible = excluded.responsible,
              due_date = excluded.due_date
            returning comment_pk
            """,
            {
                "batch_id": batch_id,
                "project_id": record.get("project_id"),
                "comment_id": record.get("comment_id"),
                "source_comment_id": record.get("source_comment_id"),
                "severity": record.get("severity"),
                "document_code": record.get("document_code"),
                "revision": record.get("revision"),
                "page_or_item": record.get("page_or_item"),
                "original_comment": record.get("original_comment"),
                "compiled_action": record.get("compiled_action"),
                "finding_basis": record.get("finding_basis"),
                "source_location": record.get("source_location"),
                "origin_type": record.get("origin_type"),
                "status_control": record.get("status_control", "UNCHECKED"),
                "responsible": record.get("responsible"),
                "verifier": record.get("verifier"),
                "created_at": record.get("created_at"),
                "verified_at": record.get("verified_at"),
                "reopened_count": record.get("reopened_count", 0),
                "due_date": record.get("due_date"),
            },
        )
        return int(cur.fetchone()[0])


def replace_required_documents(conn: Any, comment_pk: int, documents: list[str]) -> None:
    with conn.cursor() as cur:
        cur.execute("delete from comment_required_documents where comment_pk = %s", (comment_pk,))
        for code in sorted(set(documents)):
            cur.execute(
                "insert into comment_required_documents(comment_pk, document_code) values (%s, %s)",
                (comment_pk, code),
            )


def assert_preflight_resolved(conn: Any, batch_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("select assert_preflight_resolved(%s)", (batch_id,))


def assert_batch_integrity(conn: Any, batch_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("select assert_comment_batch_integrity(%s)", (batch_id,))


def persist_preflight(payload: dict[str, Any], database_url: str | None = None) -> None:
    """Persiste lote e dúvidas sem gerar/persistir comentários exportáveis."""
    with connect(database_url) as conn:
        upsert_project(conn, payload["project_id"])
        batch_id = upsert_batch(conn, payload)
        replace_clarification_questions(conn, batch_id, payload.get("clarification_questions", []))
        conn.commit()


def persist_payload(payload: dict[str, Any], database_url: str | None = None) -> None:
    with connect(database_url) as conn:
        upsert_project(conn, payload["project_id"])
        batch_id = upsert_batch(conn, payload)
        replace_clarification_questions(conn, batch_id, payload.get("clarification_questions", []))
        assert_preflight_resolved(conn, batch_id)
        for record in payload.get("comments", []):
            pk = insert_comment(conn, batch_id, record)
            replace_required_documents(conn, pk, record.get("required_documents") or [])
        assert_batch_integrity(conn, batch_id)
        conn.commit()
