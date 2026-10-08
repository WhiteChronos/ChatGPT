#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.connection_preflight import build_connection_report, report_to_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize WhiteChronos connection evidence without invoking provider tools."
    )
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--input", required=True, help="UTF-8 JSON evidence file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("input must contain a JSON object")
        report = build_connection_report(Path(args.repo), payload)
        data = report_to_json(report, process_layers=payload.get("process_layers"))
    except Exception as exc:
        print(f"Connection preflight failed: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        for item in data["observations"]:
            print(f"{item['integration_id']}: {item['status']}")
        print(
            "REQUIRED_TASK_CONNECTIONS="
            + ("PASS" if data["required_task_connections_pass"] else "FAIL")
        )
    return 0 if report.required_task_connections_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
