#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.doctor import render_report, report_to_json, run_doctor
from runtime.model import CheckStatus, DoctorInput


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Diagnose WhiteChronos Codex runtime readiness without mutating source.")
    p.add_argument("--repo", default=".", help="Repository root (default: current directory)")
    p.add_argument("--json", action="store_true", dest="as_json", help="Emit deterministic JSON")
    p.add_argument("--expected-commit")
    p.add_argument("--codex-path", default="codex")
    p.add_argument("--runtime-kind", choices=("unknown", "trusted_remote", "codex_cloud"), default="unknown")
    p.add_argument("--host-tool", action="append", default=[], help="Current host tool name; repeatable")
    p.add_argument("--require-live-smoke-ready", action="store_true")
    return p


def _exit_code(report, require_live: bool) -> int:
    hard = {CheckStatus.FAIL, CheckStatus.SECURITY_REVIEW_REQUIRED}
    if any(item.status in hard for item in report.checks):
        return 1
    if require_live and not report.live_smoke_ready:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = run_doctor(
            DoctorInput(
                repo_root=Path(args.repo),
                expected_commit=args.expected_commit,
                codex_path=args.codex_path,
                host_tools=frozenset(args.host_tool),
                runtime_kind=args.runtime_kind,
            )
        )
    except Exception as exc:
        print(f"Runtime Doctor failed: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(report_to_json(report), indent=2, sort_keys=True))
    else:
        sys.stdout.write(render_report(report))
    return _exit_code(report, args.require_live_smoke_ready)


if __name__ == "__main__":
    raise SystemExit(main())
