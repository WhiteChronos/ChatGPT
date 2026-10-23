"""Explicit, synthetic-only TypeSafe + DefAPI live proof; never called by CI."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

TARGETS = {
    "typesafe": ("https://api.typesafe.ai/v1/systemone", "jev-1.13.0", "TYPESAFE_API_KEY"),
    "defapi": ("https://api.defapi.org/api/v1/decisions", "typesafe/jev-1.13", "DEFAPI_API_KEY"),
}
QUESTION = {"urgent": {"type": "noul", "instructions": "Does this fictional issue express urgency?"}}

class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def check_https(url: str) -> dict[str, object]:
    """No credentials; 401/405 is reachable HTTPS, NOT authenticated success."""
    try:
        request = Request(url, method="HEAD")
        with build_opener(_NoRedirect()).open(request, timeout=7) as response:
            code = response.getcode()
    except HTTPError as exc:
        code = exc.code
        exc.close()
    except (URLError, TimeoutError, OSError):
        return {"status": "NETWORK_UNAVAILABLE"}
    if code in (301, 302, 303, 307, 308) or code == 407 or code >= 500:
        return {"status": "NETWORK_UNAVAILABLE"}
    return {"status": "HTTPS_RESPONDED", "unauthenticated_status": code}


def _check_response(result: object, provider: str) -> dict[str, object]:
    _, model, _ = TARGETS[provider]
    if not isinstance(result, dict) or result.get("model") != model:
        raise ValueError("invalid model")
    answers, usage = result.get("answers"), result.get("usage")
    if not isinstance(answers, dict) or set(answers) != {"urgent"} or not isinstance(usage, dict):
        raise ValueError("invalid response")
    answer = answers["urgent"]
    if not isinstance(answer, dict) or answer.get("type") != "noul":
        raise ValueError("invalid type")
    probability = answer.get("noul")
    if type(probability) not in (int, float) or not (0 <= probability <= 1):
        raise ValueError("invalid probability")
    for name in ("input_tokens", "output_tokens"):
        value = usage.get(name)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("invalid usage")
        if provider == "defapi" and value is None:
            raise ValueError("missing usage")
    evidence = {"status": "AUTHENTICATED_INFERENCE_PASS", "model": model,
                "answer_type": "noul", "probability": probability,
                "usage": {name: usage.get(name) for name in ("input_tokens", "output_tokens")}}
    if provider == "defapi":
        task_id = result.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError("missing task")
        evidence["task_id_hash"] = hashlib.sha256(task_id.encode()).hexdigest()[:16]
    return evidence


def verify(*, live=False, env=None, probe=check_https, evaluators=None) -> dict[str, object]:
    """Tests inject fake probe/evaluators; CLI uses real transports only."""
    env = os.environ if env is None else env
    report = {"schema": "whitechronos/jev-live/v1", "time_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "live" if live else "preflight", "results": {}}
    if live:
        if env.get("JEV_LIVE_SMOKE_APPROVED") != "YES":
            report["overall"] = "BLOCKED_APPROVAL"
            return report
        missing = [p for p, (_, _, key) in TARGETS.items() if not env.get(key, "").strip()]
        if missing:
            report.update(overall="BLOCKED_CREDENTIALS", missing_providers=missing)
            return report
    for provider, (url, _, _) in TARGETS.items():
        try:
            observation = probe(url)
            if observation.get("status") not in ("HTTPS_RESPONDED", "NETWORK_UNAVAILABLE"):
                observation = {"status": "NETWORK_UNAVAILABLE"}
            observation = {k: observation[k] for k in ("status", "unauthenticated_status") if k in observation}
        except Exception:
            observation = {"status": "NETWORK_UNAVAILABLE"}
        report["results"][provider] = {"network": observation}
    if not all(item["network"]["status"] == "HTTPS_RESPONDED" for item in report["results"].values()):
        report["overall"] = "BLOCKED_HTTPS"
        return report
    if not live:
        report["overall"] = "UNAUTHENTICATED_HTTPS_ONLY"
        return report
    if evaluators is None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from defapi_jev import decide
        from typesafe_bridge import evaluate_jev
        evaluators = {"typesafe": evaluate_jev, "defapi": decide}
    state = {"test": "fictional", "text": "Please fix my imaginary report urgently.", "nonce": secrets.token_hex(12)}
    report["input_hash"] = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
    success = True
    for provider in TARGETS:
        start = time.monotonic()
        try:
            checked = _check_response(evaluators[provider](state, QUESTION), provider)
        except Exception:
            checked = {"status": "INFERENCE_FAILED"}
            success = False
        checked["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        report["results"][provider]["inference"] = checked
    report["overall"] = "LIVE_VERIFIED_BOTH" if success else "LIVE_NOT_VERIFIED"
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="One synthetic evaluation per provider; may incur fees")
    parser.add_argument("--output", type=Path, help="Write a new private JSON evidence file")
    args = parser.parse_args(argv)
    result = verify(live=args.execute)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(text)
        except OSError:
            print('{"overall":"BLOCKED_OUTPUT"}')
            return 2
    print(text, end="")
    return 0 if result["overall"] in ("LIVE_VERIFIED_BOTH", "UNAUTHENTICATED_HTTPS_ONLY") else 2


if __name__ == "__main__":
    raise SystemExit(main())
