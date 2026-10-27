#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

ARTIFACT_PATTERNS = (
    r"VISTA_FRONTAL",
    r"VISTA_LATERAL_ESQUERDA",
    r"VISTA_LATERAL_DIREITA",
    r"VISTA_SUPERIOR",
    r"VISTA_INFERIOR",
    r"VISTA_ISOMETRICA",
    r"CONJUNTO_MULTIVISTAS",
    r"SECAO_[A-Z0-9_]+",
    r"SIMBOLOGIA_[A-Z0-9_]+",
)

ASCII_NAME = re.compile(r"^[A-Z0-9_]+\.dxf$")
REVISION = re.compile(r"_R[0-9]{2,}$", re.IGNORECASE)

def fail(msg):
    print(f"ERROR: {msg}")
    return 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--instrument", help="expected instrument/equipment slug")
    ap.add_argument("--manufacturer", help="expected manufacturer slug")
    ap.add_argument("--model", help="expected model slug")
    ap.add_argument("--revision", help="expected revision, e.g. R10")
    a=ap.parse_args()

    name=Path(a.file).name
    if not name.lower().endswith(".dxf"):
        return fail("file must end with .dxf")
    if not ASCII_NAME.fullmatch(name):
        return fail("filename must use uppercase ASCII letters, digits and underscores only")

    stem=name[:-4]
    if not REVISION.search(stem):
        return fail("filename must end with revision token such as _R10")

    if not any(re.search(rf"_{pat}(?:_R[0-9]+)$", stem) for pat in ARTIFACT_PATTERNS):
        return fail("filename must include a canonical artifact/view token")

    for label, value in (
        ("instrument",a.instrument),
        ("manufacturer",a.manufacturer),
        ("model",a.model),
        ("revision",a.revision),
    ):
        if value and value.upper() not in stem.upper():
            return fail(f"expected {label} token not found: {value}")

    parts=stem.split("_")
    if len(parts) < 6:
        return fail("filename is too short to identify instrument, manufacturer, model, artifact and revision")

    print("OK: descriptive DXF filename passes")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
