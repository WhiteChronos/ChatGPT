"""Gera o Excel de controle de comentários no padrão aprovado.

Regras visuais principais:
- todos os comentários formais são preservados;
- status inicial ☐;
- coluna de status centralizada e 22 pt;
- borda externa preta grossa e bordas internas pretas finas;
- texto com quebra automática e altura confortável;
- novas divergências em aba separada.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

from pipeline.comment_control_pipeline import gate

HEADERS = [
    "Nº / Comentário",
    "Grau",
    "Documento / Local",
    "O que precisa ser atendido",
    "Evidência da verificação",
    "Comentário atendido",
]

THIN = Side(style="thin", color="000000")
THICK = Side(style="thick", color="000000")
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
BODY_FONT = Font(color="000000", size=11)
CHECK_FONT = Font(color="000000", size=22, bold=True)


def document_location(record: dict[str, Any]) -> str:
    parts = [record.get("document_code"), record.get("revision"), record.get("page_or_item")]
    return " — ".join(str(p).strip() for p in parts if p)


def evidence_text(record: dict[str, Any]) -> str:
    parts = [
        record.get("evidence_document"),
        record.get("evidence_revision"),
        record.get("evidence_location"),
        record.get("evidence_text"),
    ]
    return " — ".join(str(p).strip() for p in parts if p)


def visual_status(record: dict[str, Any]) -> str:
    return "☑" if record.get("status_control") == "CHECKED" else "☐"


def _apply_table_border(ws, min_row: int, max_row: int, min_col: int, max_col: int) -> None:
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cell in row:
            top = THICK if cell.row == min_row else THIN
            bottom = THICK if cell.row == max_row else THIN
            left = THICK if cell.column == min_col else THIN
            right = THICK if cell.column == max_col else THIN
            cell.border = Border(top=top, bottom=bottom, left=left, right=right)


def _row_height(action: str, location: str, evidence: str) -> float:
    longest = max(len(action or ""), len(location or ""), len(evidence or ""))
    approx_lines = max(2, min(9, (longest // 70) + 1))
    return max(34.0, approx_lines * 18.0)


def _setup_sheet(ws, title: str, records: list[dict[str, Any]]) -> None:
    ws.title = title
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"
    ws.append(HEADERS)

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 34

    status_validation = DataValidation(type="list", formula1='"☐,☑"', allow_blank=False)
    status_validation.error = "Selecione somente ☐ ou ☑."
    status_validation.errorTitle = "Status inválido"
    status_validation.prompt = "☐ = não confirmado | ☑ = confirmado com evidência"
    status_validation.promptTitle = "Comentário atendido"
    ws.add_data_validation(status_validation)

    for record in records:
        location = document_location(record)
        evidence = evidence_text(record)
        action = str(record.get("compiled_action") or "")
        ws.append([
            record.get("comment_id"),
            record.get("severity"),
            location,
            action,
            evidence,
            visual_status(record),
        ])
        r = ws.max_row
        ws.row_dimensions[r].height = _row_height(action, location, evidence)

        for c in range(1, 6):
            ws.cell(r, c).font = BODY_FONT
            ws.cell(r, c).alignment = Alignment(vertical="top", wrap_text=True)

        status_cell = ws.cell(r, 6)
        status_cell.font = CHECK_FONT
        status_cell.alignment = Alignment(horizontal="center", vertical="center")
        status_validation.add(status_cell)

    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 43
    ws.column_dimensions["D"].width = 86
    ws.column_dimensions["E"].width = 50
    ws.column_dimensions["F"].width = 23

    if ws.max_row >= 2:
        _apply_table_border(ws, 1, ws.max_row, 1, 6)

    ws.auto_filter.ref = f"A1:F{ws.max_row}"
    ws.print_title_rows = "1:1"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.center.text = "Controle de Comentários Técnicos"


def _verification_sheet(wb: Workbook, payload: dict[str, Any]) -> None:
    ws = wb.create_sheet("VERIFICAÇÃO")
    formal = payload.get("comments", [])
    checked = [r for r in formal if r.get("status_control") == "CHECKED"]
    checked_without_evidence = [r for r in checked if not r.get("evidence_text")]

    rows = [
        ("Controle", "Resultado"),
        ("Comentários formais na origem", payload.get("source_formal_comment_count", 0)),
        ("Comentários formais registrados", len(formal)),
        ("Comentários atendidos ☑", len(checked)),
        ("Comentários pendentes ☐", len(formal) - len(checked)),
        ("☑ sem evidência", len(checked_without_evidence)),
        (
            "Integridade da quantidade",
            "OK" if payload.get("source_formal_comment_count") == len(formal) else "ERRO",
        ),
        ("Integridade da verificação", "OK" if not checked_without_evidence else "ERRO"),
    ]
    for row in rows:
        ws.append(row)

    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row in ws.iter_rows(min_row=2):
        row[0].alignment = Alignment(vertical="top", wrap_text=True)
        row[1].alignment = Alignment(horizontal="center", vertical="center")

    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 24
    _apply_table_border(ws, 1, ws.max_row, 1, 2)


def build_workbook(payload: dict[str, Any]) -> Workbook:
    gate(payload)
    wb = Workbook()
    ws = wb.active
    _setup_sheet(ws, "COMENTÁRIOS", payload.get("comments", []))

    divergences = payload.get("new_divergences", [])
    if divergences:
        ws_div = wb.create_sheet()
        _setup_sheet(ws_div, "NOVAS DIVERGÊNCIAS", divergences)

    _verification_sheet(wb, payload)
    return wb


def export_excel(payload: dict[str, Any], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb = build_workbook(payload)
    wb.save(output_path)
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    print(export_excel(payload, args.output))
