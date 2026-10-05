#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


_RECORD_PREFIXES = (
    "registry/capabilities/v2/contracts/",
    "registry/capabilities/v2/providers/",
    "registry/capabilities/v2/events/",
)


@dataclass(frozen=True)
class RegistryChange:
    status: str
    old_path: str | None
    new_path: str | None


def _normalize(path: str) -> str:
    value = path.replace("\\", "/").strip()
    if not value:
        raise ValueError("unsafe empty path")
    if value.startswith("/") or re.match(r"^[A-Za-z]:/", value):
        raise ValueError(f"absolute path is unsafe: {path}")
    parts = PurePosixPath(value).parts
    if any(part == ".." for part in parts):
        raise ValueError(f"parent traversal is unsafe: {path}")
    normalized = "/".join(part for part in parts if part not in ("", "."))
    if not normalized:
        raise ValueError("unsafe empty path")
    return normalized


def parse_name_status(lines: list[str]) -> tuple[RegistryChange, ...]:
    changes: list[RegistryChange] = []
    for raw in lines:
        line = raw.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        status = parts[0]
        if not status:
            raise ValueError(f"invalid git name-status line: {raw!r}")
        code = status[0]
        if code in {"R", "C"}:
            if len(parts) != 3:
                raise ValueError(f"invalid rename/copy line: {raw!r}")
            old_path = _normalize(parts[1])
            new_path = _normalize(parts[2])
        else:
            if len(parts) != 2:
                raise ValueError(f"invalid git name-status line: {raw!r}")
            path = _normalize(parts[1])
            if code == "A":
                old_path, new_path = None, path
            elif code == "D":
                old_path, new_path = path, None
            else:
                old_path = new_path = path
        changes.append(RegistryChange(status=status, old_path=old_path, new_path=new_path))
    return tuple(changes)


def _is_record_path(path: str | None) -> bool:
    if path is None or not path.endswith(".json"):
        return False
    return any(path.startswith(prefix) and len(path) > len(prefix) for prefix in _RECORD_PREFIXES)


def validate_registry_changes(changes: tuple[RegistryChange, ...]) -> tuple[str, ...]:
    violations: list[str] = []
    for change in changes:
        code = change.status[0]
        touched_record = _is_record_path(change.old_path) or _is_record_path(change.new_path)
        if not touched_record:
            continue
        if code == "A" and change.old_path is None and _is_record_path(change.new_path):
            continue
        paths = " -> ".join(path for path in (change.old_path, change.new_path) if path is not None)
        violations.append(
            f"append-only registry violation: status {change.status} is not allowed for accepted record {paths}"
        )
    return tuple(sorted(violations))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enforce append-only WhiteChronos capability registry records.")
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [
            "git", "diff", "--name-status", "--find-renames", "--find-copies-harder",
            f"{args.base}...{args.head}", "--", "registry/capabilities",
        ],
        cwd=repo_root,
        shell=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        print(f"CAPABILITY_REGISTRY_POLICY=FAIL: {completed.stderr.strip()}", file=sys.stderr)
        return 1
    try:
        changes = parse_name_status(completed.stdout.splitlines())
        violations = validate_registry_changes(changes)
    except ValueError as exc:
        print(f"CAPABILITY_REGISTRY_POLICY=FAIL: {exc}", file=sys.stderr)
        return 1
    if violations:
        print("CAPABILITY_REGISTRY_POLICY=FAIL")
        for violation in violations:
            print(violation)
        return 1
    print("CAPABILITY_REGISTRY_POLICY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
