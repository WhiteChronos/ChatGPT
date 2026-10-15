#!/usr/bin/env python3
"""Read-only audit of first-party skill metadata, with fail-closed exit status."""
import argparse
import json
from pathlib import Path

EXCLUDED = {".git", "node_modules", ".venv", "vendor", "__pycache__"}


def audit(root: Path) -> dict:
    findings = []
    checked = 0
    for path in sorted(root.rglob("SKILL.md")):
        relative_parts = path.relative_to(root).parts
        if any(part in EXCLUDED for part in relative_parts):
            continue
        # Test inputs are not installed entrypoints. Match the adjacent path
        # components, not unrelated directories named tests and fixtures.
        if any(pair == ("tests", "fixtures") for pair in zip(relative_parts, relative_parts[1:])):
            continue
        checked += 1
        relative = str(path.relative_to(root))
        try:
            body = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            findings.append({"path": relative, "problem": "unreadable file: " + type(exc).__name__})
            continue
        if not body.startswith("---\n"):
            findings.append({"path": relative, "problem": "missing YAML frontmatter"})
            continue
        parts = body.split("---", 2)
        if len(parts) < 3:
            findings.append({"path": relative, "problem": "unterminated YAML frontmatter"})
            continue
        headers = {}
        for line in parts[1].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip().strip('"').strip("'")
        for field in ("name", "description"):
            if not headers.get(field):
                findings.append({"path": relative, "problem": "missing " + field})
        if not parts[2].strip():
            findings.append({"path": relative, "problem": "empty instructions"})
    return {"checked_skills": checked, "findings": findings, "status": "PASS" if not findings else "REVIEW_REQUIRED"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("skill-audit.json"))
    args = parser.parse_args()
    result = audit(args.root.resolve())
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
