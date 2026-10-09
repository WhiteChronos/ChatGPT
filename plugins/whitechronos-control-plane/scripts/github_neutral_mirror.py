from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.github_neutral_mirror import NeutralMirrorRequest, run_neutral_mirror


class _UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError("invalid command line")


def _parser() -> argparse.ArgumentParser:
    parser = _UsageParser(description="Run the trusted GitHub-to-GitLab neutral mirror worker.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--subject-ref", required=True)
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--worker-revision", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--trusted-ref", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        workflow_ref = os.environ.get("GITHUB_REF", "")
        workflow_sha = os.environ.get("GITHUB_SHA", "")
        request = NeutralMirrorRequest(
            subject_ref=args.subject_ref,
            subject_sha=args.subject_sha,
            worker_revision=args.worker_revision,
            target_url=args.target_url,
            receipt_path=Path(args.receipt),
        )
        receipt = run_neutral_mirror(
            Path(args.repo_root),
            request,
            workflow_ref=workflow_ref,
            workflow_sha=workflow_sha,
            trusted_ref=args.trusted_ref,
        )
    except Exception:
        print("Neutral mirror failed: invalid input", file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
