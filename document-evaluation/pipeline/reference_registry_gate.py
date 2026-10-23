#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from document_evaluation.reference_registry import load_registry, validate_registry

DEFAULT = ROOT / "datacenter" / "ENGINEERING_REFERENCE_REGISTRY.json"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else DEFAULT
    try:
        data = load_registry(path)
    except Exception as exc:
        print(f"RESULT: BLOCK\nERROR: {exc}")
        return 1
    errors = validate_registry(data)
    if errors:
        print("RESULT: BLOCK")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
