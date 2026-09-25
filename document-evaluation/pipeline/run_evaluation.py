#!/usr/bin/env python3
"""Document Evaluation subsystem orchestrator.

Incubation version: delegates critical validation to repository-root canonical gates.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_GATE = ROOT / "pipeline" / "reference_registry_gate.py"
COMPATIBILITY_GATE = ROOT / "pipeline" / "engineering_compatibility_gate.py"
PROTOCOL_ZERO_GATE = ROOT / "pipeline" / "protocol_zero_gate.py"


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python document-evaluation/pipeline/run_evaluation.py <project-datasheet.json>")
        return 2

    datasheet = args[0]
    commands = [
        [sys.executable, str(REFERENCE_GATE)],
        [sys.executable, str(COMPATIBILITY_GATE), datasheet],
        [sys.executable, str(PROTOCOL_ZERO_GATE), datasheet],
    ]
    failed = False
    for command in commands:
        rc = run(command)
        failed = failed or rc != 0
    print("DOCUMENT EVALUATION RESULT:", "BLOCK" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
