#!/usr/bin/env python3
"""Validate all MCE Skill mirrors without relying on Bash."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "systems" / "mce" / ".agents" / "skills"
MIRROR = ROOT / ".agents" / "skills"

def verify() -> int:
    if not SOURCE.is_dir() or not MIRROR.is_dir():
        raise ValueError("Missing MCE Skill roots")
    count = 0
    for source in sorted(SOURCE.rglob("*")):
        if source.is_dir():
            continue
        if "__pycache__" in source.parts or ".pytest_cache" in source.parts or source.suffix in (".pyc", ".pyo"):
            continue
        if source.is_symlink() or not source.is_file():
            raise ValueError("Unsafe Skill source")
        target = MIRROR / source.relative_to(SOURCE)
        if target.is_symlink() or not target.is_file() or target.read_bytes() != source.read_bytes():
            raise ValueError("Skill mirror mismatch: " + source.relative_to(SOURCE).as_posix())
        count += 1
    if count < 4:
        raise ValueError("Incomplete Skill inventory")
    return count

if __name__ == "__main__":
    try:
        n = verify()
    except (ValueError, OSError) as exc:
        print("MCE_SKILLS_SYNC=BLOCKED: " + str(exc))
        raise SystemExit(2)
    print("MCE_SKILLS_SYNC=PASS: " + str(n) + " files")
