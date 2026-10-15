#!/usr/bin/env python3
"""Read-only skill governance audit. No code generation, installation or network calls."""
import argparse
import json
from pathlib import Path

REQUIRED = ("name:", "description:")


def audit(root: Path) -> dict:
    findings = []
    checked = 0
    for path in sorted(root.rglob("SKILL.md")):
        if any(part in (".git", "node_modules", ".venv", "vendor") for part in path.parts):
            continue
        checked += 1
        body = path.read_text(encoding="utf-8")
        front = body.split("---", 2)
        if len(front) < 3 or front[0].strip():
            findings.append({"path": str(path.relative_to(root)), "problem": "missing YAML frontmatter"})
            continue
        for field in REQUIRED:
            if not any(line.startswith(field) for line in front[1].splitlines()):
                findings.append({"path": str(path.relative_to(root)), "problem": "missing " + field})
        if "TODO" in body:
            findings.append({"path": str(path.relative_to(root)), "problem": "unresolved TODO"})
    return {"checked_skills": checked, "findings": findings, "status": "PASS" if not findings else "REVIEW_REQUIRED"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("skill-audit.json"))
    args = parser.parse_args()
    result = audit(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    # Non-blocking until baseline has been reviewed; findings still captured.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
