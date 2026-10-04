#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.cloud_model import CloudPreflightInput
from runtime.cloud_preflight import (
    cloud_report_to_json,
    render_cloud_report,
    run_cloud_preflight,
)
from runtime.cloud_profile import load_cloud_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate WhiteChronos Codex Cloud environment readiness "
            "without claiming live runtime capability."
        )
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--profile")
    parser.add_argument(
        "--repo-path",
        action="append",
        default=[],
        metavar="OWNER/NAME=PATH",
    )
    parser.add_argument("--codex-path", default="codex")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--require-ready", action="store_true")
    return parser


def _repo_paths(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(
                f"invalid --repo-path {value!r}; expected OWNER/NAME=PATH"
            )
        full_name, raw_path = value.split("=", 1)
        if not full_name or "/" not in full_name or not raw_path:
            raise ValueError(
                f"invalid --repo-path {value!r}; expected OWNER/NAME=PATH"
            )
        if full_name in result:
            raise ValueError(f"duplicate --repo-path for {full_name}")
        result[full_name] = Path(raw_path)
    return result


def _payload(profile_path: Path, profile, report) -> dict[str, object]:
    base = cloud_report_to_json(report)
    return {
        "profile": str(profile_path),
        "environment_name": profile.environment_name,
        "runtime_kind": profile.runtime_kind,
        "checks": base["checks"],
        "ready": base["ready"],
        "blockers": base["blockers"],
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        repo_root = Path(args.repo_root).resolve()
        profile_path = (
            Path(args.profile)
            if args.profile
            else repo_root
            / "datacenter"
            / "WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json"
        )
        mappings = _repo_paths(args.repo_path)
        profile = load_cloud_profile(repo_root, profile_path)
        report = run_cloud_preflight(
            CloudPreflightInput(profile, mappings, args.codex_path)
        )
    except Exception as exc:
        print(f"Cloud preflight failed: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(_payload(profile_path, profile, report), indent=2))
    else:
        print(f"PROFILE\t{profile_path}")
        print(f"ENVIRONMENT\t{profile.environment_name}")
        print(f"RUNTIME_KIND\t{profile.runtime_kind}")
        sys.stdout.write(render_cloud_report(report))

    if args.require_ready and not report.ready:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
