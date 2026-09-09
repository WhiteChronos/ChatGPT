from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evals.graders import grade
from pipeline.comment_control_agent import compile_comments, to_storage_payload


async def main() -> int:
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY ausente", file=sys.stderr)
        return 2

    cases_path = Path(__file__).with_name("comment_control_cases.jsonl")
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = []
    failed = 0

    for case in cases:
        compiled = await compile_comments(case["report"], case["project_id"])
        payload = to_storage_payload(compiled)
        errors = grade(case, payload)
        ok = not errors
        failed += int(not ok)
        results.append({"id": case["id"], "ok": ok, "errors": errors, "payload": payload})
        print(case["id"], "PASS" if ok else "FAIL", errors)

    results_dir = Path(__file__).with_name("results")
    results_dir.mkdir(exist_ok=True)
    (results_dir / "latest.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
