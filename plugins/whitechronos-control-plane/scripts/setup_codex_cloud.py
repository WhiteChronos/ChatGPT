#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.cloud_bootstrap import build_bootstrap_plan, execute_bootstrap_plan
from runtime.cloud_profile import load_cloud_profile


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare WhiteChronos Codex Cloud dependencies using a "
            "bounded role-based plan."
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
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
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


def _result_payload(
    profile_path: Path,
    profile,
    apply: bool,
    results,
) -> dict[str, object]:
    return {
        "profile": str(profile_path),
        "environment_name": profile.environment_name,
        "runtime_kind": profile.runtime_kind,
        "apply": apply,
        "steps": [
            {
                "repository": item.step.repository,
                "cwd": str(item.step.cwd),
                "argv": list(item.step.argv),
                "returncode": item.returncode,
                "stdout_tail": item.stdout_tail,
                "stderr_tail": item.stderr_tail,
            }
            for item in results
        ],
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
        steps = build_bootstrap_plan(profile, mappings)
        results = execute_bootstrap_plan(steps, apply=args.apply)
    except Exception as exc:
        print(f"Codex Cloud setup failed: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(
            json.dumps(
                _result_payload(profile_path, profile, args.apply, results),
                indent=2,
            )
        )
    else:
        print(f"PROFILE\t{profile_path}")
        print(f"ENVIRONMENT\t{profile.environment_name}")
        print(f"APPLY\t{'YES' if args.apply else 'NO'}")
        for result in results:
            print(
                f"STEP\t{result.step.repository}\t{result.returncode}\t"
                f"{' '.join(result.step.argv)}"
            )

    return 1 if any(result.returncode != 0 for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
