#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import PurePosixPath


CLASS_ORDER = (
    "CONTROL_PLANE_CRITICAL",
    "RUNTIME_CONTROL",
    "DURABLE_STATE",
    "DOCUMENTATION",
    "OTHER",
)


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


def classify_path(path: str) -> str:
    value = _normalize(path)

    if (
        value == ".github/CODEOWNERS"
        or value == "AGENTS.md"
        or value.startswith(".github/workflows/")
        or value.startswith("governance/")
        or value.startswith("pipeline/")
        or value.startswith("schemas/")
    ):
        return "CONTROL_PLANE_CRITICAL"

    if (
        value.startswith("plugins/whitechronos-control-plane/")
        or value.startswith("plugins/subagent-broker/")
        or value.startswith(".codex/")
        or value.startswith(".agents/")
    ):
        return "RUNTIME_CONTROL"

    if (
        value.startswith("memory/")
        or value.startswith("history/")
        or value.startswith("registry/")
        or value.startswith("datacenter/")
        or value.startswith("datasheet/")
    ):
        return "DURABLE_STATE"

    if value == "mkdocs.yml" or value.startswith("docs/"):
        return "DOCUMENTATION"

    return "OTHER"


def classify_paths(paths: list[str]) -> dict[str, list[str]]:
    result = {name: [] for name in CLASS_ORDER}
    for path in paths:
        normalized = _normalize(path)
        result[classify_path(normalized)].append(normalized)
    for name in CLASS_ORDER:
        result[name] = sorted(set(result[name]))
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify WhiteChronos repository paths by control-plane risk."
    )
    parser.add_argument("--paths-file")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.paths_file:
            with open(args.paths_file, "r", encoding="utf-8") as handle:
                paths = [line.rstrip("\n") for line in handle if line.strip()]
        else:
            paths = [line.rstrip("\n") for line in sys.stdin if line.strip()]
        print(json.dumps(classify_paths(paths), indent=2, sort_keys=False))
    except (OSError, ValueError) as exc:
        print(f"PATH_POLICY=FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
