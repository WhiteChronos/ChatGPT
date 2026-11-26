#!/usr/bin/env python3
"""Read-only SHA-bound REA/MCE evidence inventory; never a release approval."""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys

REPO = "WhiteChronos/ChatGPT"
TARGETS = {
    118: ("MCE", {"github-memory", "mce-regression", "security", "github-control-plane-policy"}),
    119: ("REA", {"github-memory", "rea-regression (windows-latest)", "security", "github-control-plane-policy"}),
}
SHA = re.compile(r"^[0-9a-f]{40}$")


class EvidenceError(RuntimeError):
    pass


def request_json(path: str, token: str) -> dict | list:
    """Fixed HTTPS API host; sanitized errors; no redirects or token logging."""
    if not token:
        raise EvidenceError("READ_ONLY_GITHUB_TOKEN_MISSING")
    if not path.startswith("/repos/" + REPO + "/") or any(
        value in path for value in ("\r", "\n", "..", "//", "#", "@")
    ):
        raise EvidenceError("OUT_OF_SCOPE_API_PATH")
    conn = http.client.HTTPSConnection("api.github.com", timeout=20)
    try:
        conn.request("GET", path, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + token,
            "User-Agent": "rea-mce-readonly-review-inventory",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        response = conn.getresponse()
        if response.status != 200:
            raise EvidenceError("GITHUB_API_HTTP_" + str(response.status))
        body = response.read(1_048_577)
        if len(body) > 1_048_576:
            raise EvidenceError("GITHUB_RESPONSE_TOO_LARGE")
        value = json.loads(body)
        if not isinstance(value, (dict, list)):
            raise EvidenceError("GITHUB_RESPONSE_WRONG_TYPE")
        return value
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise EvidenceError("GITHUB_READ_UNAVAILABLE") from exc
    finally:
        conn.close()


def inspect_one(fetch, pr_number: int) -> dict:
    if pr_number not in TARGETS:
        raise EvidenceError("UNSUPPORTED_PR")
    product, required = TARGETS[pr_number]
    prefix = "/repos/" + REPO
    pr = fetch(prefix + "/pulls/" + str(pr_number))
    if not isinstance(pr, dict):
        raise EvidenceError("INVALID_PR_RESPONSE")
    head = pr.get("head", {}).get("sha", "")
    if not isinstance(head, str) or not SHA.fullmatch(head):
        raise EvidenceError("INVALID_HEAD_SHA")
    checks_response = fetch(prefix + "/commits/" + head + "/check-runs?per_page=100")
    if not isinstance(checks_response, dict):
        raise EvidenceError("INVALID_CHECK_RESPONSE")
    checks = checks_response.get("check_runs", [])
    total = checks_response.get("total_count", 0)
    if not isinstance(checks, list) or not checks or total != len(checks):
        raise EvidenceError("CHECKS_EMPTY_OR_PAGINATED")
    if not all(isinstance(item, dict) for item in checks):
        raise EvidenceError("INVALID_CHECK_ITEM")
    observed = {item.get("name") for item in checks}
    ci_pass = required.issubset(observed) and all(
        item.get("head_sha") == head
        and item.get("status") == "completed"
        and item.get("conclusion") == "success"
        for item in checks
    )
    reviews = fetch(prefix + "/pulls/" + str(pr_number) + "/reviews?per_page=100")
    if not isinstance(reviews, list):
        raise EvidenceError("INVALID_REVIEW_RESPONSE")
    # If exactly 100 reviews are returned, pagination may hide a later review.
    if len(reviews) >= 100:
        raise EvidenceError("REVIEWS_PAGINATION_NOT_EXHAUSTED")
    author = pr.get("user", {}).get("login")
    approvals = sorted(set(
        item.get("user", {}).get("login", "")
        for item in reviews
        if isinstance(item, dict)
        and item.get("state") == "APPROVED"
        and item.get("commit_id") == head
        and item.get("user", {}).get("login")
        and item.get("user", {}).get("login") != author
        and not item.get("user", {}).get("login", "").lower().endswith("[bot]")
        and item.get("user", {}).get("type", "User") == "User"
    ))
    latest_pr = fetch(prefix + "/pulls/" + str(pr_number))
    if (not isinstance(latest_pr, dict)
            or latest_pr.get("head", {}).get("sha") != head):
        raise EvidenceError("HEAD_CHANGED_DURING_REVIEW")
    eligible = pr.get("state") == "open" and not bool(pr.get("draft"))
    return {
        "system": product,
        "pr_number": pr_number,
        "head_sha": head,
        "pr_open_ready_for_review": eligible,
        "code_ci": "PASS" if ci_pass else "BLOCKED",
        "check_count": len(checks),
        "missing_required_checks": sorted(required.difference(observed)),
        "sha_bound_formal_approvals": len(approvals),
        "review": "SHA_BOUND_APPROVAL_RECORDED" if approvals else "PENDING",
        "review_threads": "NOT_VERIFIED_BY_REST",
        "host_live": "NOT_VERIFIED",
        "merge_authorized": False,
        "production_complete": False,
    }


def render(results: list[dict]) -> str:
    rows = ["## REA/MCE evidence inventory — NOT approval",
            "", "This report is read-only; success of this workflow means inventory generated, not readiness for production.",
            "", "| System | PR | HEAD | CI | SHA-bound review | Host live |",
            "|---|---|---|---|---|---|"]
    for item in results:
        rows.append("| {system} | #{pr_number} | {head_sha} | {code_ci} | {review} | {host_live} |".format(**item))
    rows += ["", "Review threads, protected private-vault operation, target-host identity and human engineering acceptance still need independent evidence.",
             "**No merge, deploy or PRODUCTION_COMPLETE is authorized by this report.**"]
    return "\n".join(rows) + "\n"


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--pr", nargs="+", type=int, required=True)
    args.add_argument("--repo", default=REPO)
    opt = args.parse_args()
    if opt.repo != REPO or len(set(opt.pr)) != len(opt.pr) or any(n not in TARGETS for n in opt.pr):
        print("INVALID_REVIEW_TARGET", file=sys.stderr)
        return 2
    token = os.environ.get("GH_TOKEN", "")
    try:
        result = [inspect_one(lambda path: request_json(path, token), n) for n in opt.pr]
    except EvidenceError as exc:
        print("EVIDENCE_INCOMPLETE: " + str(exc), file=sys.stderr)
        return 2
    report = render(result)
    print(report, end="")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(report)
    # A complete evidence inventory may truthfully contain pending approvals.
    # It is NOT a green production, safety, review or release gate.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
