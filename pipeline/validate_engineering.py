#!/usr/bin/env python3
"""Validador determinístico para regras de engenharia do projeto AUTOMAÇÃO.

O objetivo não é substituir revisão de engenharia. O script impede regressões conhecidas,
força rastreabilidade e bloqueia representações que violem a Regra de Ouro.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipeline.li_io_standard import validate_li_io_document
from pipeline.md_revision_standard import validate_md_document_metadata

ALLOWED_FAMILIES = {"DISCRETE", "SHARED_DISPLAY", "COMPUTER", "PLC"}
ALLOWED_LOCATIONS = {"FIELD", "MAIN_PANEL", "BEHIND_PANEL", "LOCAL_PANEL"}
ALLOWED_STATUSES = {
    "CONFIRMADO",
    "CONFIRMADO_COM_RESSALVA",
    "PROPOSTO",
    "CONFLITANTE",
    "TBD",
    "NÃO_APLICÁVEL",
}
CRITICAL_SIGNAL_ROLES = {"CMD", "RUN", "FAULT", "AVAILABLE"}
CONTROLLED_DOCUMENT_TYPES = {"MD", "ET", "LI", "FD"}
ALLOWED_DOCUMENT_CHANGES = {
    "TEXT",
    "TECHNICAL_VALUES",
    "TEXTUAL_QUANTITIES",
    "AUTHORIZED_FORMULAS",
    "APPROVED_IMAGES",
}
DYNAMIC_PAGINATION_CHANGES = {"PAGE_NUMBER", "TOTAL_PAGES", "TOC_PAGE_REFERENCE"}
FORBIDDEN_LAYOUT_CHANGES = {
    "MARGINS",
    "TABLE_GEOMETRY",
    "COLUMN_WIDTHS",
    "ROW_HEIGHTS",
    "MERGES",
    "BORDERS",
    "FILLS",
    "STYLES",
    "FONTS",
    "FONT_SIZES",
    "STRUCTURAL_ALIGNMENT",
    "HEADERS",
    "FOOTERS",
    "LOGO",
    "SIGNATURE",
    "PRINT_AREA",
    "PAGE_ORIENTATION",
    "PAGE_SCALE",
    "SECTION_STRUCTURE",
    "TEMPLATE_SHEET_COUNT_COPY",
    "PARAGRAPH_SPACING",
    "LINE_SPACING",
    "INDENTS",
    "TABS",
}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    message: str
    item_id: str | None = None


def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return None


def validate_symbol(symbol: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    sid = str(symbol.get("id", "UNKNOWN"))
    family = symbol.get("family")
    location = symbol.get("location")

    if family not in ALLOWED_FAMILIES:
        findings.append(Finding("DM-FAMILY", "CRITICAL", f"Família inválida: {family!r}", sid))
    if location not in ALLOWED_LOCATIONS:
        findings.append(Finding("DM-LOCATION", "CRITICAL", f"Localização inválida: {location!r}", sid))

    w = _num(symbol.get("external_width_mm"))
    h = _num(symbol.get("external_height_mm"))
    d = _num(symbol.get("external_diameter_mm"))
    if family == "DISCRETE":
        if d != 12.0:
            findings.append(Finding("DM-12MM", "CRITICAL", f"Círculo deve possuir Ø12 mm; recebido {d!r}", sid))
    elif w != 12.0 or h != 12.0:
        findings.append(Finding("DM-12MM", "CRITICAL", f"Envoltória deve ser 12 x 12 mm; recebido {w!r} x {h!r}", sid))

    if w is not None and h is not None and abs(w - h) > 1e-9:
        findings.append(Finding("DM-DISTORTION", "CRITICAL", "Símbolo achatado/alongado: proporção externa não é 1:1", sid))

    expected_lines = {
        "FIELD": "NONE",
        "MAIN_PANEL": "SINGLE_SOLID",
        "BEHIND_PANEL": "SINGLE_DASHED",
        "LOCAL_PANEL": "DOUBLE_SOLID",
    }
    if location in expected_lines and symbol.get("location_line") != expected_lines[location]:
        findings.append(Finding("DM-LOCATION-LINE", "CRITICAL", f"Linha de localização incompatível. Esperado {expected_lines[location]}", sid))

    if not symbol.get("source_document") and symbol.get("status") in {"CONFIRMADO", "CONFIRMADO_COM_RESSALVA"}:
        findings.append(Finding("TRACE-SOURCE", "HIGH", "Símbolo confirmado sem documento-fonte", sid))
    return findings


def validate_signal(signal: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    sid = str(signal.get("id", "UNKNOWN"))
    for field in ("origin", "destination", "signal_type", "direction", "purpose"):
        if not signal.get(field):
            findings.append(Finding("SIG-ORPHAN", "CRITICAL", f"Sinal sem {field}", sid))
    if signal.get("status") not in ALLOWED_STATUSES:
        findings.append(Finding("STATUS", "HIGH", f"Status inválido: {signal.get('status')!r}", sid))
    return findings


def validate_equipment_logic(equipment: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    eid = str(equipment.get("id", "UNKNOWN"))
    if equipment.get("redundant_pair"):
        roles = set(equipment.get("signal_roles", []))
        missing = CRITICAL_SIGNAL_ROLES - roles
        if missing:
            findings.append(Finding("REDUNDANCY-SIGNALS", "CRITICAL", f"Equipamento redundante sem sinais independentes: {', '.join(sorted(missing))}", eid))
        if not equipment.get("transfer_logic"):
            findings.append(Finding("REDUNDANCY-TRANSFER", "CRITICAL", "Falta lógica de transferência A/B", eid))
    return findings


def validate_interlock(item: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    iid = str(item.get("id", "UNKNOWN"))
    required = ("cause", "condition", "affected_equipment", "effect", "feedback", "reset", "safe_state", "evidence")
    missing = [field for field in required if not item.get(field)]
    if missing:
        findings.append(Finding("INT-INCOMPLETE", "CRITICAL", f"Intertravamento incompleto: {', '.join(missing)}", iid))
    return findings


def validate_document_layout(doc: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    did = str(doc.get("id", "UNKNOWN"))
    doc_type = str(doc.get("document_type", "")).upper()
    if doc_type not in CONTROLLED_DOCUMENT_TYPES:
        return findings

    if doc.get("layout_immutable") is not True:
        findings.append(Finding("DOC-LAYOUT-LOCK", "CRITICAL", "Documento controlado sem layout_immutable=true", did))
    if not doc.get("template_fingerprint"):
        findings.append(Finding("DOC-TEMPLATE-FINGERPRINT", "CRITICAL", "Documento controlado sem fingerprint do padrão visual", did))

    changes = set(doc.get("changes", []))
    forbidden = changes & FORBIDDEN_LAYOUT_CHANGES
    if forbidden:
        findings.append(Finding("DOC-LAYOUT-MUTATION", "CRITICAL", f"Alteração de layout proibida: {', '.join(sorted(forbidden))}", did))

    unknown = changes - ALLOWED_DOCUMENT_CHANGES - DYNAMIC_PAGINATION_CHANGES - FORBIDDEN_LAYOUT_CHANGES
    if unknown:
        findings.append(Finding("DOC-CHANGE-TYPE", "HIGH", f"Tipo de alteração não governado: {', '.join(sorted(unknown))}", did))

    if doc.get("final_page_count") is not None and doc.get("declared_total_pages") != doc.get("final_page_count"):
        findings.append(Finding("DOC-PAGINATION", "CRITICAL", "Total declarado não corresponde à quantidade final renderizada", did))

    if doc_type in {"LI", "FD"} and doc.get("datasheet_layout_immutable") is not True:
        findings.append(Finding("DATASHEET-LAYOUT-LOCK", "CRITICAL", "LI/FD sem bloqueio explícito do layout interno", did))
    if doc_type in {"LI", "FD"} and doc.get("reference_validation_required") is not True:
        findings.append(Finding("DATASHEET-REFERENCE", "HIGH", "LI/FD sem validação obrigatória contra documentos de referência", did))

    if doc_type == "LI" and doc.get("sheet_count_source") == "VISUAL_TEMPLATE":
        findings.append(Finding("DOC-TEMPLATE-SHEET-COUNT", "CRITICAL", "Quantidade de abas copiada indevidamente do modelo visual", did))

    return findings


def validate_document(doc: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if doc.get("understanding_status") not in {"APROVADO", "APROVADO_COM_RESSALVAS"}:
        findings.append(Finding("DOC-UNDERSTANDING", "CRITICAL", "Entendimento do documento ainda não aprovado", str(doc.get("id", "UNKNOWN"))))
    findings.extend(validate_document_layout(doc))
    for finding in validate_li_io_document(doc):
        findings.append(Finding(finding.code, finding.severity, finding.message, finding.item_id))
    for finding in validate_md_document_metadata(doc):
        findings.append(Finding(finding.code, finding.severity, finding.message, finding.item_id))
    return findings


def validate_project(data: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for doc in data.get("documents", []):
        findings.extend(validate_document(doc))
    for symbol in data.get("symbols", []):
        findings.extend(validate_symbol(symbol))
    for signal in data.get("signals", []):
        findings.extend(validate_signal(signal))
    for equipment in data.get("equipment", []):
        findings.extend(validate_equipment_logic(equipment))
    for interlock in data.get("interlocks", []):
        findings.extend(validate_interlock(interlock))
    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: validate_engineering.py <arquivo.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = validate_project(data)
    for finding in findings:
        item = f" [{finding.item_id}]" if finding.item_id else ""
        print(f"{finding.severity} {finding.code}{item}: {finding.message}")
    critical = [finding for finding in findings if finding.severity == "CRITICAL"]
    print(f"findings={len(findings)} critical={len(critical)}")
    return 1 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
