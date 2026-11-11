#!/usr/bin/env python3
"""Install/update GitHub Arena as a global Codex Skill and user instruction.

Python 3.8+, standard library only. Idempotent and non-destructive.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys

START = "<!-- GITHUB_ARENA_GLOBAL_START -->"
END = "<!-- GITHUB_ARENA_GLOBAL_END -->"
BLOCK = f"""{START}
## Global Arena quality layer

Apply the installed `github-arena` Skill before finalizing Codex work.

- Use Micro Arena by default: evidence-first, constraint-first, edge-cases-first, built-to-last.
- Escalate to Review Arena for complex or high-impact code, architecture, repository, CI/CD, security, governance, API, or production work.
- Use Full Arena only when explicitly requested.
- Preserve more specific project instructions.
{END}
"""


def codex_home_from(args) -> Path:
    if args.codex_home:
        return Path(args.codex_home).expanduser().resolve()
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def update_agents(path: Path, dry_run: bool) -> str:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if START in old and END in old:
        before, rest = old.split(START, 1)
        _old_block, after = rest.split(END, 1)
        new = before.rstrip() + "\n\n" + BLOCK + after.lstrip("\n")
        action = "updated"
    else:
        prefix = old.rstrip()
        new = (prefix + "\n\n" if prefix else "") + BLOCK
        action = "created" if not path.exists() else "appended"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding="utf-8")
    return action


def copy_skill(src: Path, dst: Path, dry_run: bool) -> str:
    if src.resolve() == dst.resolve():
        return "already-installed"
    if dry_run:
        return "would-copy"
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.parent / (dst.name + ".tmp-install")
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    if dst.exists():
        shutil.rmtree(dst)
    tmp.replace(dst)
    return "copied"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", help="Override CODEX_HOME for installation or testing")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without writing")
    args = parser.parse_args()

    source_skill = Path(__file__).resolve().parents[1]
    codex_home = codex_home_from(args)
    skill_dest = codex_home / "skills" / "github-arena"
    agents_file = codex_home / "AGENTS.md"

    try:
        skill_action = copy_skill(source_skill, skill_dest, args.dry_run)
        agents_action = update_agents(agents_file, args.dry_run)
    except Exception as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1

    print(f"CODEX_HOME={codex_home}")
    print(f"skill={skill_dest} ({skill_action})")
    print(f"agents={agents_file} ({agents_action})")
    if args.dry_run:
        print("dry-run: no files changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
