#!/usr/bin/env python3
"""Source-fidelity probe for engineering documents.

The probe intentionally separates native document metadata from external
renderer observations. It never treats a re-rendered Word page count as the
authoritative source page count.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import xml.etree.ElementTree as ET


def _docx_probe(path: Path) -> dict:
    result = {
        "format": "DOCX",
        "native_page_count": None,
        "native_count_method": None,
        "authoring_application": None,
        "requested_fonts": [],
    }
    fonts = set()
    with zipfile.ZipFile(path) as zf:
        if "docProps/app.xml" in zf.namelist():
            root = ET.fromstring(zf.read("docProps/app.xml"))
            for child in root:
                local = child.tag.rsplit("}", 1)[-1]
                if local == "Pages" and child.text and child.text.isdigit():
                    result["native_page_count"] = int(child.text)
                    result["native_count_method"] = "DOCX_APP_XML_PAGES"
                elif local == "Application":
                    result["authoring_application"] = child.text
        font_re = re.compile(rb'w:(?:ascii|hAnsi|eastAsia|cs)="([^"]+)"')
        for name in zf.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                for match in font_re.findall(zf.read(name)):
                    fonts.add(match.decode("utf-8", "replace"))
    result["requested_fonts"] = sorted(fonts, key=str.casefold)
    return result


def _doc_probe(path: Path) -> dict:
    result = {
        "format": "DOC",
        "native_page_count": None,
        "native_count_method": None,
        "authoring_application": None,
        "requested_fonts": [],
    }
    try:
        import olefile  # optional dependency for legacy Word
    except ImportError:
        result["probe_warning"] = "olefile is required for native legacy DOC metadata"
        return result
    with olefile.OleFileIO(str(path)) as ole:
        meta = ole.get_metadata()
        pages = getattr(meta, "num_pages", None)
        if isinstance(pages, int) and pages >= 0:
            result["native_page_count"] = pages
            result["native_count_method"] = "OLE_SUMMARYINFO_PAGE_COUNT"
        app = getattr(meta, "creating_application", None)
        if app:
            result["authoring_application"] = str(app)
    return result


def _pdf_probe(path: Path) -> dict:
    result = {
        "format": "PDF",
        "native_page_count": None,
        "native_count_method": None,
        "authoring_application": None,
        "requested_fonts": [],
    }
    try:
        import fitz  # PyMuPDF
        with fitz.open(path) as doc:
            result["native_page_count"] = doc.page_count
            result["native_count_method"] = "PDF_NATIVE_PAGE_TREE_PYMUPDF"
        return result
    except Exception:
        pass
    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        proc = subprocess.run([pdfinfo, str(path)], text=True, capture_output=True, check=False)
        match = re.search(r"^Pages:\s*(\d+)\s*$", proc.stdout, re.MULTILINE)
        if match:
            result["native_page_count"] = int(match.group(1))
            result["native_count_method"] = "PDF_NATIVE_PAGE_TREE_PDFINFO"
    return result


def _font_substitutions(fonts: list[str]) -> list[dict]:
    fc_match = shutil.which("fc-match")
    if not fc_match:
        return []
    rows = []
    for requested in fonts:
        proc = subprocess.run(
            [fc_match, "-f", "%{family}\n", requested],
            text=True,
            capture_output=True,
            check=False,
        )
        matched = (proc.stdout.splitlines() or [""])[0].strip()
        normalized_requested = requested.casefold()
        normalized_matched = matched.casefold()
        substituted = bool(matched) and normalized_requested not in normalized_matched
        rows.append({
            "requested": requested,
            "matched": matched or None,
            "substituted": substituted,
        })
    return rows


def probe(path: Path, rendered_page_count: int | None = None, renderer: str | None = None, check_fonts: bool = False) -> dict:
    suffix = path.suffix.casefold()
    if suffix == ".docx":
        result = _docx_probe(path)
    elif suffix == ".doc":
        result = _doc_probe(path)
    elif suffix == ".pdf":
        result = _pdf_probe(path)
    else:
        raise ValueError(f"unsupported document format: {suffix}")

    result["rendered_page_count"] = rendered_page_count
    result["renderer"] = renderer
    native = result.get("native_page_count")
    if native is not None and rendered_page_count is not None:
        result["pagination_status"] = "MATCH" if native == rendered_page_count else "RENDER_MISMATCH"
    elif native is not None:
        result["pagination_status"] = "NATIVE_COUNT_AVAILABLE"
    else:
        result["pagination_status"] = "NOT_VERIFIABLE"

    substitutions = _font_substitutions(result.get("requested_fonts", [])) if check_fonts else []
    result["font_matches"] = substitutions
    result["font_substitution_detected"] = any(row["substituted"] for row in substitutions)
    result["render_count_is_source_authority"] = result["format"] == "PDF"
    result["confidence"] = "HIGH" if native is not None else "LOW"
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--rendered-pages", type=int)
    parser.add_argument("--renderer")
    parser.add_argument("--check-fonts", action="store_true")
    args = parser.parse_args()
    print(json.dumps(
        probe(args.document, args.rendered_pages, args.renderer, args.check_fonts),
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
