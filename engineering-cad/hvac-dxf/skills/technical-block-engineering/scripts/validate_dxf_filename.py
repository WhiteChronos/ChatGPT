#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

MAX_RECOMMENDED=64
MAX_HARD=80
ASCII_NAME=re.compile(r"^[A-Z0-9_]+\.dxf$")
REVISION=re.compile(r"_R[0-9]{2,}$")
ARTIFACT_PATTERNS=(
    r"FRT",r"ESQ",r"DIR",r"SUP",r"INF",r"ISO",r"MV",
    r"SEC_[A-Z0-9_]+",r"SYM_[A-Z0-9_]+",
)

def fail(msg):
    print(f"ERROR: {msg}")
    return 1

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--type-token")
    ap.add_argument("--manufacturer")
    ap.add_argument("--model")
    ap.add_argument("--revision")
    a=ap.parse_args()

    name=Path(a.file).name
    if len(name)>MAX_HARD:
        return fail(f"filename exceeds hard limit of {MAX_HARD} characters")
    if not name.lower().endswith(".dxf"):
        return fail("file must end with .dxf")
    if not ASCII_NAME.fullmatch(name):
        return fail("filename must use uppercase ASCII letters, digits and underscores only")

    stem=name[:-4]
    if not REVISION.search(stem):
        return fail("filename must end with revision token such as _R10")
    if not any(re.search(rf"_{pat}_R[0-9]+$", stem) for pat in ARTIFACT_PATTERNS):
        return fail("filename must include a compact canonical artifact token")

    for label,value in (
        ("type",a.type_token),("manufacturer",a.manufacturer),
        ("model",a.model),("revision",a.revision),
    ):
        if value and value.upper() not in stem.upper():
            return fail(f"expected {label} token not found: {value}")

    if len(name)>MAX_RECOMMENDED:
        print(f"WARNING: filename exceeds recommended {MAX_RECOMMENDED} characters: {len(name)}")

    print(f"OK: compact DXF filename passes ({len(name)} chars)")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
