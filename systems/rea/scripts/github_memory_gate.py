#!/usr/bin/env python3
"""Read-only gate: canonical REA memory is versioned exclusively in GitHub."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PRODUCT = "REA_INDEPENDENTE"
SLUG = "rea"
MEMORY_PATH = "systems/rea/spec/memoria.md"
EXTRA_PATHS = (".agents/skills/rea-engenharia-reversa-evolutiva/",)
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{24,}|Authorization:\s*Bearer\s+\S+", re.I)


class MemoryGateError(ValueError):
    pass


def owned(path: str) -> bool:
    return path.startswith("systems/rea/") or path.startswith(".github/workflows/rea-") or path.startswith(EXTRA_PATHS)


def identifiers(text: str, kind: str) -> list[str]:
    return re.findall(r"^\|\s*(" + kind + r"-REA-[0-9]{3})\s*\|", text, re.M)


def verify_document(current: str, previous: str | None, changed_files: list[str]) -> dict:
    if PRODUCT not in current or "PRODUCTION_COMPLETE=NO" not in current:
        raise MemoryGateError("Missing product identity or safety gate")
    if SECRET.search(current):
        raise MemoryGateError("Potential credential in public memory")
    counts = {}
    for kind, minimum in (("DEC", 12), ("PEND", 7)):
        found = identifiers(current, kind)
        if len(found) < minimum or len(set(found)) != len(found):
            raise MemoryGateError("Missing or duplicate " + kind + " identifiers")
        counts[kind] = len(found)
    if previous is not None:
        if not current.startswith(previous):
            raise MemoryGateError("Previous GitHub memory must remain an exact prefix")
        for kind in ("DEC", "PEND"):
            if not set(identifiers(previous, kind)).issubset(set(identifiers(current, kind))):
                raise MemoryGateError("Historical IDs disappeared")
    touched = [p for p in changed_files if owned(p) and p != MEMORY_PATH]
    changed = MEMORY_PATH in changed_files
    if touched and not changed:
        raise MemoryGateError("REA files changed without memory in same commit")
    if previous is None and not changed:
        raise MemoryGateError("Missing bootstrap memory change")
    if previous is not None and changed:
        appendix = current[len(previous):]
        if not appendix.strip() or not re.search(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", appendix):
            raise MemoryGateError("Append a dated memory record")
    return {"product": PRODUCT, "status": "PASS", "decisions": counts["DEC"],
            "pending": counts["PEND"], "memory_updated": changed,
            "owned_files_changed": len(touched),
            "memory_sha256": hashlib.sha256(current.encode("utf-8")).hexdigest(),
            "production_complete": False}


def git(root: Path, *args: str, allow_error: bool = False) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                       text=True, encoding="utf-8", timeout=30, check=False)
    if p.returncode and not allow_error:
        raise MemoryGateError("Git parent history missing: " + " ".join(args[:2]))
    return p



ENFORCEMENT_BASELINE_SHA = "88413a907366512169b6b0812296c64a8ee11ee5"

def audit_commit_range(root: Path, baseline: str, head: str) -> int:
    """Audit every commit since the first canonical-memory gate, not only HEAD."""
    if not re.fullmatch(r"[0-9a-f]{40}", baseline) or not re.fullmatch(r"[0-9a-f]{40}", head):
        raise MemoryGateError("Invalid Git commit identifier")
    if git(root, "merge-base", "--is-ancestor", baseline, head, allow_error=True).returncode:
        raise MemoryGateError("Memory baseline missing or shallow history")
    commits = git(root, "rev-list", "--reverse", "--first-parent", baseline + ".." + head).stdout.splitlines()
    if len(commits) > 250:
        raise MemoryGateError("History audit limit exceeded")
    for commit in commits:
        parents = git(root, "rev-list", "--parents", "-n", "1", commit).stdout.strip().split()
        if len(parents) != 2 or parents[0] != commit:
            raise MemoryGateError("Nonlinear history requires human review")
        parent = parents[1]
        old = git(root, "show", parent + ":" + MEMORY_PATH).stdout
        new = git(root, "show", commit + ":" + MEMORY_PATH).stdout
        changed = [x for x in git(root, "diff", "--name-only", "-z", parent, commit).stdout.split("\0") if x]
        try:
            verify_document(new, old, changed)
        except MemoryGateError as exc:
            raise MemoryGateError("Commit " + commit[:12] + ": " + str(exc)) from exc
    return len(commits)


def audit(root: Path) -> dict:
    root = root.resolve()
    memory = root / MEMORY_PATH
    if not memory.is_file() or memory.is_symlink():
        raise MemoryGateError("Missing canonical memory or unsafe symlink")
    current = memory.read_text(encoding="utf-8")
    head = git(root, "rev-parse", "--verify", "HEAD").stdout.strip()
    parent = git(root, "rev-parse", "--verify", "HEAD^").stdout.strip()
    present = git(root, "cat-file", "-e", "HEAD^:" + MEMORY_PATH, allow_error=True).returncode == 0
    previous = git(root, "show", "HEAD^:" + MEMORY_PATH).stdout if present else None
    changed = [p for p in git(root, "diff", "--name-only", "-z", "HEAD^", "HEAD").stdout.split("\0") if p]
    result = verify_document(current, previous, changed)
    audited = audit_commit_range(root, ENFORCEMENT_BASELINE_SHA, head)
    for entry in ("AGENTS.md", "README.md"):
        p = root / "systems" / SLUG / entry
        if p.is_symlink() or not p.is_file() or "spec/memoria.md" not in p.read_text(encoding="utf-8"):
            raise MemoryGateError("Missing entrypoint: " + entry)
    result.update({"audited_commits": audited, "head_sha": head, "parent_sha": parent,
                   "canonical_path": MEMORY_PATH,
                   "github_issue": "https://github.com/WhiteChronos/ChatGPT/issues/121"})
    return result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    args = p.parse_args()
    try:
        print(json.dumps(audit(args.repo_root), ensure_ascii=False, sort_keys=True))
        return 0
    except (MemoryGateError, OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"product": PRODUCT, "status": "BLOCKED", "reason": str(exc),
                          "production_complete": False}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
