#!/usr/bin/env python3
"""Document Evaluation orchestrator linked directly to main.

The subsystem owns Source Registry + Protocol Zero locally and integrates with
the mature parent Engineering Compatibility gate from main. This keeps both
tracks independently executable while preserving one compatibility authority.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBSYSTEM_ROOT = REPO_ROOT / "document-evaluation"
REFERENCE_GATE = SUBSYSTEM_ROOT / "pipeline" / "reference_registry_gate.py"
PROTOCOL_ZERO_GATE = SUBSYSTEM_ROOT / "pipeline" / "protocol_zero_gate.py"
PARENT_COMPATIBILITY_GATE = REPO_ROOT / "pipeline" / "engineering_compatibility_gate.py"


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python document-evaluation/pipeline/run_evaluation.py <project-datasheet.json>")
        return 2

    datasheet = args[0]
    commands = [
        [sys.executable, str(REFERENCE_GATE)],
        [sys.executable, str(PROTOCOL_ZERO_GATE), datasheet],
        [sys.executable, "-m", "pipeline.engineering_compatibility_gate", datasheet],
    ]

    failed = False
    for command in commands:
        rc = run(command)
        failed = failed or rc != 0

    print("DOCUMENT EVALUATION RESULT:", "BLOCK" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
