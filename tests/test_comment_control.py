import pytest

from pipeline.comment_control_clarification import apply_clarification_resolutions
from pipeline.comment_control_pipeline import ClarificationRequired, validate_payload
from pipeline.comment_control_analytics import summarize, risk_score_baseline
from pipeline.comment_control_excel import build_workbook


def base_payload():
    return {
        "project_id": "P1",
        "source_formal_comment_count": 2,
        "comments": [
            {
                "project_id": "P1",
                "comment_id": "C01",
                "severity": "GRAVE",
                "document_code": "MD-1",
                "original_comment": "Corrigir A",
                "compiled_action": "Corrigir A",
                "finding_basis": "Constatação A",
                "source_location": "MD-1 folha 1",
                "origin_type": "FORMAL_COMMENT",
                "status_control": "UNCHECKED",
                "required_documents": ["MD-1"],
                "verified_documents": [],
                "created_at": "2026-09-01T00:00:00+00:00",
            },
            {
                "project_id": "P1",
                "comment_id": "C02",
                "severity": "ALTO",
                "document_code": "ET-1",
                "original_comment": "Corrigir B",
                "compiled_action": "Corrigir B",
                "finding_basis": "Constatação B",
                "source_location": "ET-1 folha 2",
                "origin_type": "FORMAL_COMMENT",
                "status_control": "UNCHECKED",
                "required_documents": [],
                "verified_documents": [],
                "created_at": "2026-09-02T00:00:00+00:00",
            },
        ],
        "new_divergences": [],
        "clarification_questions": [],
    }


def with_open_question(payload=None):
    payload = payload or base_payload()
    payload["clarification_questions"] = [
        {
            "question_id": "Q01",
            "topic": "Escopo",
            "question_text": "Qual requisito deve prevalecer?",
            "why_needed": "Falta decisão de engenharia",
            "related_documents": ["MD-1", "ET-1"],
            "status": "OPEN",
            "resolution": None,
            "resolution_type": None,
            "resolved_by": None,
            "resolved_at": None,
        }
    ]
    return payload


def codes(payload):
    return {f.code for f in validate_payload(payload)}


def test_valid_initial_payload_has_no_findings():
    assert validate_payload(base_payload()) == []


def test_count_mismatch_blocks():
    payload = base_payload()
    payload["source_formal_comment_count"] = 3
    assert "CC-COUNT-INTEGRITY" in codes(payload)


def test_duplicate_comment_blocks():
    payload = base_payload()
    payload["comments"][1]["comment_id"] = "C01"
    assert "CC-DUPLICATE" in codes(payload)


def test_checked_without_evidence_blocks():
    payload = base_payload()
    payload["comments"][0]["status_control"] = "CHECKED"
    payload["comments"][0]["verified_at"] = "2026-09-09T12:00:00+00:00"
    assert "CC-CHECKED-EVIDENCE" in codes(payload)


def test_checked_multidocument_requires_all_documents():
    payload = base_payload()
    row = payload["comments"][0]
    row["status_control"] = "CHECKED"
    row["verified_at"] = "2026-09-09T12:00:00+00:00"
    row["evidence_text"] = "MD corrigido"
    row["verified_documents"] = []
    assert "CC-MULTIDOC-EVIDENCE" in codes(payload)


def test_open_clarification_blocks_generation():
    payload = with_open_question()
    assert "CC-CLARIFICATION-OPEN" in codes(payload)
    with pytest.raises(ClarificationRequired):
        build_workbook(payload)


def test_resolved_question_without_resolution_metadata_still_blocks():
    payload = with_open_question()
    payload["clarification_questions"][0]["status"] = "RESOLVED"
    assert "CC-CLARIFICATION-RESOLUTION" in codes(payload)
    with pytest.raises(ValueError):
        build_workbook(payload)


def test_dismissed_clarification_creates_no_export_row():
    payload = with_open_question()
    resolved = apply_clarification_resolutions(
        payload,
        {
            "resolved_by": "QA",
            "answers": [
                {
                    "question_id": "Q01",
                    "resolution": "A diferença é permitida pelo requisito do projeto.",
                    "resolution_type": "DISMISSED",
                }
            ],
        },
    )
    assert resolved["clarification_questions"][0]["status"] == "DISMISSED"
    assert resolved["new_divergences"] == []
    assert "CC-CLARIFICATION-OPEN" not in codes(resolved)
    wb = build_workbook(resolved)
    ws = wb["Controle_Geral"]
    assert ws.max_row == 6


def test_confirmed_error_resolution_creates_new_divergence_not_question_row():
    payload = with_open_question()
    resolved = apply_clarification_resolutions(
        payload,
        {
            "resolved_by": "QA",
            "answers": [
                {
                    "question_id": "Q01",
                    "resolution": "O requisito deve estar presente nos dois documentos.",
                    "resolution_type": "CONFIRMED_ERROR",
                    "confirmed_error": {
                        "severity": "ALTO",
                        "document_code": "ET-1 × FD-1",
                        "original_comment": "ERRO — requisito incompatível entre documentos.",
                        "compiled_action": "Compatibilizar os dois documentos conforme a decisão aprovada.",
                        "finding_basis": "A decisão do solicitante confirmou que ambos deveriam ser coerentes.",
                        "source_location": "ET-1 e FD-1",
                    },
                }
            ],
        },
    )
    question = resolved["clarification_questions"][0]
    assert question["status"] == "RESOLVED"
    assert question["resolution_type"] == "CONFIRMED_ERROR"
    assert len(resolved["new_divergences"]) == 1
    assert resolved["new_divergences"][0]["comment_id"] == "ND01"
    assert "?" not in resolved["new_divergences"][0]["original_comment"]
    wb = build_workbook(resolved)
    ws = wb["Controle_Geral"]
    assert ws.max_row == 7
    assert ws["A7"].value == "ND01"


def test_question_marker_in_new_divergence_is_forbidden():
    payload = base_payload()
    payload["comments"].append(
        {
            "project_id": "P1",
            "comment_id": "ND01",
            "severity": "ALTO",
            "original_comment": "DÚVIDA — qual valor usar?",
            "compiled_action": "Confirmar antes de corrigir",
            "origin_type": "NEW_DIVERGENCE",
            "status_control": "UNCHECKED",
            "created_at": "2026-09-03T00:00:00+00:00",
        }
    )
    assert "CC-QUESTION-IN-EXPORT" in codes(payload)


def test_analytics_counts_only_formal_comments():
    payload = base_payload()
    payload["comments"].append(
        {
            "project_id": "P1",
            "comment_id": "ND01",
            "severity": "LEVE",
            "original_comment": "ERRO — nova divergência",
            "compiled_action": "Corrigir",
            "origin_type": "NEW_DIVERGENCE",
            "status_control": "UNCHECKED",
            "created_at": "2026-09-03T00:00:00+00:00",
        }
    )
    result = summarize(payload["comments"])
    assert result["formal_comment_count"] == 2


def test_risk_score_is_bounded():
    score = risk_score_baseline(base_payload()["comments"][0])["score"]
    assert 0 <= score <= 1


def test_excel_uses_approved_columns_and_no_verification_sheet():
    wb = build_workbook(base_payload())
    assert wb.sheetnames == ["Controle_Geral", "Listas", "Fontes_e_Regras"]
    ws = wb["Controle_Geral"]
    headers = [ws.cell(4, c).value for c in range(1, 9)]
    assert headers == [
        "ID",
        "Grau",
        "Documento(s)",
        "Objetivo / Erro",
        "O que precisa ser verificado / atendido",
        "Evidência / constatação na revisão analisada",
        "Fonte / localização",
        "Comentário atendido",
    ]
    forbidden = {"Tipo", "Evidência de atendimento", "Responsável", "Data verificação"}
    assert not forbidden.intersection(headers)
    assert "Verificacao" not in wb.sheetnames
    assert "VERIFICAÇÃO" not in wb.sheetnames
    assert "Confronto_IO" not in wb.sheetnames


def test_excel_preserves_count_and_checkbox_style():
    wb = build_workbook(base_payload())
    ws = wb["Controle_Geral"]
    assert ws.max_row == 6
    assert ws["A5"].value == "C01"
    assert ws["A6"].value == "C02"
    assert ws["H5"].value == "☐"
    assert ws["H6"].value == "☐"
    assert ws["H5"].alignment.horizontal == "center"
    assert ws["H5"].alignment.vertical == "center"
    assert ws["H5"].font.sz == 22
    assert ws.column_dimensions["H"].width >= 20
    assert ws["A4"].border.top.style == "thick"
    assert ws["H6"].border.bottom.style == "thick"
