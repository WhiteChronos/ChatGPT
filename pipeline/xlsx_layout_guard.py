#!/usr/bin/env python3
"""Compara a estrutura visual de dois arquivos XLSX/XLSM sem comparar conteúdo.

O guardião remove valores, fórmulas, textos inline e caches de cálculo das planilhas,
mas preserva estilos de célula, dimensões, mesclagens, bordas, impressão, desenhos,
imagens, cabeçalhos, rodapés e estrutura de abas.

Uso:
    python -m pipeline.xlsx_layout_guard baseline.xlsx candidate.xlsx
    python -m pipeline.xlsx_layout_guard baseline.xlsx candidate.xlsx --json-out report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

CONTENT_TAGS = {
    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v",
    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}f",
    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is",
    "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t",
}

CONTENT_ATTRIBUTES = {
    "t",
    "cm",
    "vm",
}

IGNORED_PACKAGE_PARTS = {
    "docProps/core.xml",
    "docProps/app.xml",
    "xl/calcChain.xml",
    "xl/sharedStrings.xml",
}


@dataclass(frozen=True)
class LayoutReport:
    baseline: str
    candidate: str
    baseline_signature: str
    candidate_signature: str
    match: bool
    differing_parts: list[str]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _canonical_xml(data: bytes, strip_cell_content: bool) -> bytes:
    root = ET.fromstring(data)

    if strip_cell_content:
        for parent in root.iter():
            for child in list(parent):
                if child.tag in CONTENT_TAGS:
                    parent.remove(child)
            if _local_name(parent.tag) == "c":
                for attr in list(parent.attrib):
                    if _local_name(attr) in CONTENT_ATTRIBUTES:
                        del parent.attrib[attr]

    def normalize(node: ET.Element) -> None:
        if node.attrib:
            attrs = sorted(node.attrib.items())
            node.attrib.clear()
            node.attrib.update(attrs)
        if node.text is not None and not node.text.strip():
            node.text = None
        if node.tail is not None and not node.tail.strip():
            node.tail = None
        for child in node:
            normalize(child)

    normalize(root)
    return ET.tostring(root, encoding="utf-8", xml_declaration=False)


def _part_signature(name: str, data: bytes) -> str:
    strip_content = name.startswith("xl/worksheets/") and name.endswith(".xml")
    if name.endswith(".xml") or name.endswith(".rels"):
        try:
            data = _canonical_xml(data, strip_cell_content=strip_content)
        except ET.ParseError:
            pass
    return hashlib.sha256(data).hexdigest()


def package_layout_map(path: str | Path) -> dict[str, str]:
    path = Path(path)
    result: dict[str, str] = {}
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith("/") or name in IGNORED_PACKAGE_PARTS:
                continue
            result[name] = _part_signature(name, archive.read(name))
    return result


def package_layout_signature(path: str | Path) -> str:
    layout = package_layout_map(path)
    payload = json.dumps(layout, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def compare_layout(baseline: str | Path, candidate: str | Path) -> LayoutReport:
    baseline_map = package_layout_map(baseline)
    candidate_map = package_layout_map(candidate)
    all_parts = sorted(set(baseline_map) | set(candidate_map))
    differing = [part for part in all_parts if baseline_map.get(part) != candidate_map.get(part)]
    return LayoutReport(
        baseline=str(baseline),
        candidate=str(candidate),
        baseline_signature=package_layout_signature(baseline),
        candidate_signature=package_layout_signature(candidate),
        match=not differing,
        differing_parts=differing,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("candidate")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)

    report = compare_layout(args.baseline, args.candidate)
    payload = asdict(report)
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0 if report.match else 1


if __name__ == "__main__":
    raise SystemExit(main())
