#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from document_evaluation.protocol_zero import validate_protocol_zero


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: protocol_zero_gate.py <project-datasheet.json>")
        return 2
    path = Path(args[0])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"RESULT: BLOCK\nERROR: {exc}")
        return 1
    errors = validate_protocol_zero(data)
    if errors:
        print("RESULT: BLOCK")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
