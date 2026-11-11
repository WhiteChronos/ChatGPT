#!/usr/bin/env python3
"""Governança de revisão de Memorial Descritivo (MD) de Automação.

Princípios:
- edição textual cirúrgica;
- layout e espaçamento imutáveis;
- remoção do D9D9D9 de revisões antigas;
- D9D9D9 somente na revisão corrente;
- marcação contínua em todos os runs textuais do parágrafo revisado.

O patcher atua apenas em word/document.xml e não reserializa o restante do pacote DOCX.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

GRAY = "D9D9D9"
P_RE = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.S)
R_RE = re.compile(r"<w:r\b[^>]*>.*?</w:r>", re.S)
RPR_RE = re.compile(r"<w:rPr\b[^>]*>.*?</w:rPr>", re.S)
TEXT_RE = re.compile(r"<w:t\b[^>]*>(.*?)</w:t>", re.S)
SHD_D9_RE = re.compile(r"<w:shd\b(?=[^>]*\bw:fill=[\"']D9D9D9[\"'])[^>]*/>", re.I)
SHD_ANY_RE = re.compile(r"<w:shd\b[^>]*/>", re.I)


@dataclass(frozen=True)
class MDFinding:
    code: str
    severity: str
    message: str
    item_id: str | None = None


def paragraph_text(xml_fragment: str) -> str:
    parts = [html.unescape(re.sub(r"<[^>]+>", "", x)) for x in TEXT_RE.findall(xml_fragment)]
    return "".join(parts).replace("\u00a0", " ")


def clear_legacy_gray_from_paragraph(p_xml: str) -> tuple[str, int]:
    count = 0

    def clean_rpr(match: re.Match[str]) -> str:
        nonlocal count
        block = match.group(0)
        block2, n = SHD_D9_RE.subn("", block)
        count += n
        return block2

    return RPR_RE.sub(clean_rpr, p_xml), count


def _shade_run(run_xml: str) -> str:
    if not TEXT_RE.search(run_xml):
        return run_xml
    texts = TEXT_RE.findall(run_xml)
    if not any(re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", t))) for t in texts):
        # A run containing only spaces is still shaded if it carries visible inter-word spacing.
        if not any(html.unescape(re.sub(r"<[^>]+>", "", t)) for t in texts):
            return run_xml

    marker = f'<w:shd w:val="clear" w:color="auto" w:fill="{GRAY}"/>'
    m = RPR_RE.search(run_xml)
    if m:
        rpr = SHD_ANY_RE.sub("", m.group(0))
        rpr = rpr.replace("</w:rPr>", marker + "</w:rPr>", 1)
        return run_xml[:m.start()] + rpr + run_xml[m.end():]

    open_end = run_xml.find(">")
    if open_end < 0:
        return run_xml
    return run_xml[:open_end + 1] + f"<w:rPr>{marker}</w:rPr>" + run_xml[open_end + 1:]


def shade_current_revision_paragraph(p_xml: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        original = match.group(0)
        updated = _shade_run(original)
        if updated != original:
            count += 1
        return updated

    return R_RE.sub(repl, p_xml), count


def _selected(index: int, text: str, change_map: dict[str, Any]) -> bool:
    indexes = {int(v) for v in change_map.get("paragraph_indices", [])}
    if index in indexes:
        return True
    normalized = " ".join(text.split())
    exact = {" ".join(str(v).split()) for v in change_map.get("paragraph_texts", [])}
    if normalized in exact:
        return True
    contains = [" ".join(str(v).split()) for v in change_map.get("paragraph_contains", [])]
    return any(token and token in normalized for token in contains)


def normalize_revision_gray(document_xml: str, change_map: dict[str, Any]) -> tuple[str, dict[str, int]]:
    paragraphs = list(P_RE.finditer(document_xml))
    out: list[str] = []
    cursor = 0
    removed = 0
    shaded = 0
    selected_count = 0

    for idx, match in enumerate(paragraphs):
        out.append(document_xml[cursor:match.start()])
        p = match.group(0)
        p, n = clear_legacy_gray_from_paragraph(p)
        removed += n
        text = paragraph_text(p)
        if _selected(idx, text, change_map):
            p, n = shade_current_revision_paragraph(p)
            shaded += n
            selected_count += 1
        out.append(p)
        cursor = match.end()
    out.append(document_xml[cursor:])
    return "".join(out), {
        "legacy_gray_removed": removed,
        "current_revision_runs_shaded": shaded,
        "current_revision_paragraphs": selected_count,
    }


def _structural_extract(xml: str) -> dict[str, list[str]]:
    tags = ["pPr", "tblPr", "trPr", "tcPr", "sectPr"]
    result: dict[str, list[str]] = {}
    for tag in tags:
        blocks = re.findall(fr"<w:{tag}\b[^>]*>.*?</w:{tag}>", xml, flags=re.S)
        if tag == "pPr":
            cleaned = []
            for block in blocks:
                block = re.sub(r"<w:rPr\b[^>]*>.*?</w:rPr>", lambda m: SHD_D9_RE.sub("", m.group(0)), block, flags=re.S)
                cleaned.append(block)
            blocks = cleaned
        result[tag] = blocks
    return result


def validate_structure(before_xml: str, after_xml: str) -> list[MDFinding]:
    findings: list[MDFinding] = []
    before = _structural_extract(before_xml)
    after = _structural_extract(after_xml)
    labels = {
        "pPr": "MD_PARAGRAPH_SPACING_MUTATION",
        "tblPr": "MD_LAYOUT_MUTATION",
        "trPr": "MD_LAYOUT_MUTATION",
        "tcPr": "MD_LAYOUT_MUTATION",
        "sectPr": "MD_LAYOUT_MUTATION",
    }
    for tag in before:
        if before[tag] != after[tag]:
            findings.append(MDFinding(labels[tag], "CRITICAL", f"Propriedade estrutural {tag} foi alterada"))
    return findings


def validate_md_document_metadata(doc: dict[str, Any]) -> list[MDFinding]:
    if str(doc.get("document_type", "")).upper() != "MD":
        return []
    findings: list[MDFinding] = []
    did = str(doc.get("id", "UNKNOWN"))
    required_true = {
        "layout_immutable": "MD_LAYOUT_MUTATION",
        "paragraph_spacing_immutable": "MD_PARAGRAPH_SPACING_MUTATION",
        "font_immutable": "MD_FONT_MUTATION",
        "legacy_gray_cleared": "MD_LEGACY_GRAY_PRESENT",
        "current_revision_gray_continuous": "MD_CURRENT_GRAY_GAP",
        "current_changes_marked": "MD_UNMARKED_CURRENT_CHANGE",
        "toc_revision_marking_consistent": "MD_TOC_REVISION_MARK_MISMATCH",
        "render_all_pages": "MD_VISUAL_QA_REQUIRED",
        "inspect_all_pages": "MD_VISUAL_QA_REQUIRED",
    }
    for field, code in required_true.items():
        if doc.get(field) is not True:
            findings.append(MDFinding(code, "CRITICAL", f"MD exige {field}=true", did))
    if doc.get("final_page_count") is not None and doc.get("declared_total_pages") != doc.get("final_page_count"):
        findings.append(MDFinding("MD_PAGINATION_MISMATCH", "CRITICAL", "Paginação declarada difere da quantidade final renderizada", did))
    if not doc.get("current_revision_change_map"):
        findings.append(MDFinding("MD_CURRENT_REVISION_TRACEABILITY", "CRITICAL", "Revisão atual sem mapa explícito de alterações", did))
    return findings


def patch_docx(source: Path, output: Path, change_map: dict[str, Any]) -> dict[str, Any]:
    with zipfile.ZipFile(source, "r") as zin:
        before_xml = zin.read("word/document.xml").decode("utf-8")
        after_xml, stats = normalize_revision_gray(before_xml, change_map)
        findings = validate_structure(before_xml, after_xml)
        if any(f.severity == "CRITICAL" for f in findings):
            raise RuntimeError("; ".join(f.message for f in findings))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp_path = Path(tmp.name)
        try:
            with zipfile.ZipFile(tmp_path, "w") as zout:
                for info in zin.infolist():
                    data = after_xml.encode("utf-8") if info.filename == "word/document.xml" else zin.read(info.filename)
                    zout.writestr(info, data)
            shutil.move(str(tmp_path), output)
        finally:
            tmp_path.unlink(missing_ok=True)
    return {"output": str(output), **stats, "critical_findings": 0}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--change-map", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    change_map = json.loads(args.change_map.read_text(encoding="utf-8"))
    report = patch_docx(args.source, args.output, change_map)
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
