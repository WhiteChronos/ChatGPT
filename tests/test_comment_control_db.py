from __future__ import annotations

import os
from pathlib import Path

import psycopg
import pytest

DB_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DB_URL, reason="TEST_DATABASE_URL ausente")
SCHEMA = Path("datacenter/comment_control_schema.sql")
CLARIFICATION_MIGRATION = Path("datacenter/migrations/20260909_clarification_resolution_integrity.sql")


def reset_schema(conn):
    with conn.cursor() as cur:
        cur.execute("drop schema public cascade; create schema public;")
        cur.execute(SCHEMA.read_text(encoding="utf-8"))
        cur.execute(CLARIFICATION_MIGRATION.read_text(encoding="utf-8"))
    conn.commit()


def seed_comment(conn, *, batch_id="B1", expected_count=1, required_doc=None, preflight_status="READY_TO_GENERATE"):
    with conn.cursor() as cur:
        cur.execute("insert into projects(project_id, project_name) values ('P1', 'Projeto 1')")
        cur.execute(
            """
            insert into comment_batches(batch_id, project_id, source_formal_comment_count, preflight_status)
            values (%s, 'P1', %s, %s)
            """,
            (batch_id, expected_count, preflight_status),
        )
        cur.execute(
            """
            insert into comments(
              batch_id, project_id, comment_id, severity, original_comment,
              compiled_action, origin_type, status_control
            ) values (%s, 'P1', 'C01', 'GRAVE', 'Original', 'Corrigir', 'FORMAL_COMMENT', 'UNCHECKED')
            returning comment_pk
            """,
            (batch_id,),
        )
        comment_pk = cur.fetchone()[0]
        if required_doc:
            cur.execute(
                "insert into comment_required_documents(comment_pk, document_code) values (%s, %s)",
                (comment_pk, required_doc),
            )
    conn.commit()
    return comment_pk


def test_batch_integrity_accepts_exact_count():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, expected_count=1)
        with conn.cursor() as cur:
            cur.execute("select assert_comment_batch_integrity('B1')")
        conn.commit()


def test_batch_integrity_rejects_missing_comment():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, expected_count=2)
        with pytest.raises(psycopg.Error):
            with conn.cursor() as cur:
                cur.execute("select assert_comment_batch_integrity('B1')")


def test_preflight_rejects_open_question():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, preflight_status="WAITING_CLARIFICATION")
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into clarification_questions(
                  batch_id, question_id, topic, question_text, why_needed, status
                ) values ('B1', 'Q01', 'Escopo', 'Qual requisito prevalece?', 'Falta decisão', 'OPEN')
                """
            )
        conn.commit()

        with pytest.raises(psycopg.Error):
            with conn.cursor() as cur:
                cur.execute("select assert_preflight_resolved('B1')")


def test_resolved_question_without_metadata_is_rejected_by_datacenter():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, preflight_status="READY_TO_GENERATE")
        with pytest.raises(psycopg.Error):
            with conn.cursor() as cur:
                cur.execute(
                    """
                    insert into clarification_questions(
                      batch_id, question_id, topic, question_text, why_needed, status
                    ) values ('B1', 'Q01', 'Escopo', 'Qual requisito prevalece?', 'Falta decisão', 'RESOLVED')
                    """
                )


def test_preflight_accepts_resolved_question():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, preflight_status="READY_TO_GENERATE")
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into clarification_questions(
                  batch_id, question_id, topic, question_text, why_needed,
                  status, resolution, resolution_type, resolved_by, resolved_at
                ) values (
                  'B1', 'Q01', 'Escopo', 'Qual requisito prevalece?', 'Falta decisão',
                  'RESOLVED', 'Compatibilizar como erro', 'CONFIRMED_ERROR', 'USER', now()
                )
                """
            )
            cur.execute("select assert_preflight_resolved('B1')")
        conn.commit()


def test_preflight_accepts_dismissed_question_with_complete_resolution():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        seed_comment(conn, preflight_status="READY_TO_GENERATE")
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into clarification_questions(
                  batch_id, question_id, topic, question_text, why_needed,
                  status, resolution, resolution_type, resolved_by, resolved_at
                ) values (
                  'B1', 'Q01', 'Referência comercial', 'Os modelos são equivalentes?', 'Falta decisão',
                  'DISMISSED', 'Ambos são válidos conforme o equipamento existente', 'DISMISSED', 'USER', now()
                )
                """
            )
            cur.execute("select assert_preflight_resolved('B1')")
        conn.commit()


def test_checked_without_evidence_is_rejected():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        pk = seed_comment(conn)
        with pytest.raises(psycopg.Error):
            with conn.cursor() as cur:
                cur.execute(
                    "update comments set status_control='CHECKED', verifier='QA', verified_at=now() where comment_pk=%s",
                    (pk,),
                )
            conn.commit()


def test_checked_requires_all_required_documents():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        pk = seed_comment(conn, required_doc="MD-001")
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into comment_evidence(comment_pk, evidence_document, evidence_text, verified_by)
                values (%s, 'ET-001', 'ET corrigida', 'QA')
                """,
                (pk,),
            )
        conn.commit()

        with pytest.raises(psycopg.Error):
            with conn.cursor() as cur:
                cur.execute(
                    "update comments set status_control='CHECKED', verifier='QA', verified_at=now() where comment_pk=%s",
                    (pk,),
                )
            conn.commit()


def test_checked_with_complete_evidence_is_accepted():
    with psycopg.connect(DB_URL) as conn:
        reset_schema(conn)
        pk = seed_comment(conn, required_doc="MD-001")
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into comment_evidence(comment_pk, evidence_document, evidence_text, verified_by)
                values (%s, 'MD-001', 'MD corrigido na folha 9', 'QA')
                """,
                (pk,),
            )
            cur.execute(
                "update comments set status_control='CHECKED', verifier='QA', verified_at=now() where comment_pk=%s",
                (pk,),
            )
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("select status_control from comments where comment_pk=%s", (pk,))
            assert cur.fetchone()[0] == "CHECKED"
