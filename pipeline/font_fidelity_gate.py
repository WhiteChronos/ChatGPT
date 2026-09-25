#!/usr/bin/env python3
"""Font fidelity gate for engineering-document review.

The gate inventories fonts named by a source document and compares them with
fonts available to the current runtime and, optionally, a caller-supplied
licensed private-font directory.

It never downloads or redistributes proprietary fonts.
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


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "datacenter" / "DOCUMENT_FONT_FIDELITY_MANIFEST.json"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def known_families(manifest: dict) -> list[str]:
    return [str(item["family"]) for item in manifest.get("sources", []) if isinstance(item, dict) and item.get("family")]


def _docx_fonts(path: Path) -> set[str]:
    fonts: set[str] = set()
    with zipfile.ZipFile(path) as zf:
        for part in ("word/document.xml", "word/styles.xml", "word/fontTable.xml"):
            if part not in zf.namelist():
                continue
            root = ET.fromstring(zf.read(part))
            if part.endswith("fontTable.xml"):
                for el in root.iter(f"{{{W_NS}}}font"):
                    name = el.attrib.get(f"{{{W_NS}}}name")
                    if name:
                        fonts.add(name.strip())
            else:
                for el in root.iter(f"{{{W_NS}}}rFonts"):
                    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
                        value = el.attrib.get(f"{{{W_NS}}}{attr}")
                        if value and not value.startswith("+"):
                            fonts.add(value.strip())
    return fonts


def _legacy_doc_fonts(path: Path, manifest: dict) -> set[str]:
    data = path.read_bytes()
    candidates = known_families(manifest)
    found: set[str] = set()
    decoded_variants = [
        data.decode("utf-16le", errors="ignore"),
        data.decode("latin-1", errors="ignore"),
    ]
    for family in candidates:
        for decoded in decoded_variants:
            if re.search(re.escape(family), decoded, flags=re.IGNORECASE):
                found.add(family)
                break
    return found


def document_fonts(path: Path, manifest: dict) -> set[str]:
    suffix = path.suffix.casefold()
    if suffix == ".docx":
        return _docx_fonts(path)
    if suffix == ".doc":
        return _legacy_doc_fonts(path, manifest)
    raise ValueError(f"font inventory not implemented for {suffix}; use DOC/DOCX source for Word fidelity checks")


def _fc_list_families() -> set[str]:
    exe = shutil.which("fc-list")
    if not exe:
        return set()
    proc = subprocess.run([exe, ":", "family"], text=True, capture_output=True, check=False)
    families: set[str] = set()
    for line in proc.stdout.splitlines():
        for family in line.split(","):
            if family.strip():
                families.add(family.strip())
    return families


def _fc_scan_private_dir(path: Path) -> set[str]:
    exe = shutil.which("fc-scan")
    if not exe or not path.exists():
        return set()
    families: set[str] = set()
    for font_file in sorted(path.rglob("*")):
        if font_file.suffix.casefold() not in {".ttf", ".otf", ".ttc"}:
            continue
        proc = subprocess.run(
            [exe, "-f", "%{family}\n", str(font_file)],
            text=True,
            capture_output=True,
            check=False,
        )
        for line in proc.stdout.splitlines():
            for family in line.split(","):
                if family.strip():
                    families.add(family.strip())
    return families


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def evaluate_fonts(used_fonts: set[str], available_fonts: set[str], manifest: dict) -> dict:
    available_norm = {_norm(x) for x in available_fonts}
    source_by_norm = {_norm(str(item.get("family"))): item for item in manifest.get("sources", []) if isinstance(item, dict)}
    rows = []
    missing_exact = []
    unmanaged = []
    for family in sorted(used_fonts, key=str.casefold):
        item = source_by_norm.get(_norm(family))
        exact = _norm(family) in available_norm
        if item is None:
            unmanaged.append(family)
            rows.append({
                "family": family,
                "managed": False,
                "exact_available": exact,
                "status": "UNMANAGED_FONT_REFERENCE" if not exact else "EXACT_AVAILABLE_UNMANAGED",
            })
            continue
        support = item.get("support_fallback")
        support_family = support.get("family") if isinstance(support, dict) else None
        support_available = bool(support_family and _norm(str(support_family)) in available_norm)
        exact_required = bool(item.get("exact_required"))
        status = "EXACT_AVAILABLE" if exact else ("MISSING_EXACT" if exact_required else "OPTIONAL_MISSING")
        if exact_required and not exact:
            missing_exact.append(family)
        rows.append({
            "family": family,
            "managed": True,
            "classification": item.get("classification"),
            "exact_required": exact_required,
            "exact_available": exact,
            "support_fallback": support_family,
            "support_fallback_available": support_available,
            "status": status,
            "official_source": item.get("official_source"),
        })
    return {
        "fonts": rows,
        "missing_exact_fonts": missing_exact,
        "unmanaged_font_references": unmanaged,
        "layout_fidelity_status": "READY" if not missing_exact and not unmanaged else "NOT_VERIFIABLE_FROM_RENDER",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--font-dir", type=Path, action="append", default=[])
    parser.add_argument("--layout-sensitive", action="store_true")
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    used = document_fonts(args.document, manifest)
    available = _fc_list_families()
    for font_dir in args.font_dir:
        available.update(_fc_scan_private_dir(font_dir))
    result = {
        "document": str(args.document),
        "used_fonts": sorted(used, key=str.casefold),
        "available_font_count": len(available),
        **evaluate_fonts(used, available, manifest),
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.output_json:
        args.output_json.write_text(payload + "\n", encoding="utf-8")
    if args.layout_sensitive and result["layout_fidelity_status"] != "READY":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
