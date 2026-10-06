from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO / ".github" / "workflows"
USES_RE = re.compile(r"\buses:\s+(actions/[^@\s]+)@([^\s#]+)")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def test_official_github_actions_are_pinned_to_full_commit_shas():
    violations: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = USES_RE.search(line)
            if match and not SHA_RE.fullmatch(match.group(2)):
                violations.append(f"{path.relative_to(REPO)}:{line_number}: {match.group(0)}")
    assert violations == []
