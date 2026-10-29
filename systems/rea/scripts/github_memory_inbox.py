#!/usr/bin/env python3
"""Read-only GitHub Issue inbox for REA public, unapproved decision records."""
from __future__ import annotations
import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import urllib.request

PRODUCT = "REA_INDEPENDENTE"
PREFIX = "REA"
ISSUE = 121
MARKER = "<!-- WC_MEMORY_EVENT_V1 -->"
FENCE = chr(96) * 3
KINDS = {"DECISION": "DEC", "PENDENCY": "PEND", "EVIDENCE": "EVID"}
FIELDS = {"schema", "system", "kind", "id", "date", "title", "summary", "origin", "approval"}
SENSITIVE = re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{24,}|Authorization:\s*Bearer\s+\S+", re.I)

class IntakeError(ValueError):
    pass

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise IntakeError("Duplicate JSON key")
        result[key] = value
    return result

def parse_comment(comment):
    body = comment.get("body") or ""
    if not isinstance(body, str):
        raise IntakeError("Wrong body type")
    if MARKER not in body:
        return None
    if len(body.encode("utf-8")) > 8192 or SENSITIVE.search(body):
        raise IntakeError("Sensitive or oversized public event")
    author = (comment.get("user") or {}).get("login", "")
    if not isinstance(author, str) or author.casefold() != "whitechronos":
        raise IntakeError("Untrusted GitHub author")
    cid = comment.get("id")
    if type(cid) is not int or cid <= 0:
        raise IntakeError("Invalid GitHub comment id")
    start = MARKER + "\n" + FENCE + "json\n"
    if not body.startswith(start) or "\n" + FENCE not in body[len(start):]:
        raise IntakeError("Invalid event block")
    payload = body[len(start):].split("\n" + FENCE, 1)[0]
    try:
        e = json.loads(payload, object_pairs_hook=_pairs,
                       parse_constant=lambda value: (_ for _ in ()).throw(IntakeError("Nonstandard JSON")))
    except (json.JSONDecodeError, TypeError) as exc:
        raise IntakeError("Invalid event JSON") from exc
    if type(e) is not dict or set(e) != FIELDS:
        raise IntakeError("Invalid event fields")
    if type(e["schema"]) is not int or e["schema"] != 1 or e["system"] != PRODUCT:
        raise IntakeError("Wrong product or schema")
    kind = e["kind"]
    if not isinstance(kind, str) or kind not in KINDS:
        raise IntakeError("Invalid kind")
    if not isinstance(e["id"], str) or not re.fullmatch(KINDS[kind] + "-" + PREFIX + r"-[0-9]{3,6}", e["id"]):
        raise IntakeError("Invalid event ID")
    stamp = e["date"]
    if not isinstance(stamp, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
        raise IntakeError("Invalid date")
    try:
        date.fromisoformat(stamp)
    except ValueError as exc:
        raise IntakeError("Invalid calendar date") from exc
    title, summary = e["title"], e["summary"]
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 160 or "\n" in title:
        raise IntakeError("Invalid title")
    if not isinstance(summary, str) or not 1 <= len(summary.strip()) <= 1210:
        raise IntakeError("Invalid summary")
    if e["origin"] not in ("USER_REQUEST", "CODEX_REVIEW", "CI_EVIDENCE", "GITHUB_PR") or e["approval"] != "NOT_ENG_APPROVED":
        raise IntakeError("Unapproved events only")
    return {"id": e["id"], "kind": kind, "date": stamp, "title": title.strip(),
            "summary": summary.strip(), "approval": "NOT_ENG_APPROVED",
            "url": "https://github.com/WhiteChronos/ChatGPT/issues/" + str(ISSUE) + "#issuecomment-" + str(cid)}

def inspect(comments, memory):
    saved = set(re.findall(r"^\|\s*((?:DEC|PEND|EVID)-" + PREFIX + r"-[0-9]{3,6})\s*\|", memory, re.M))
    seen = set()
    records = []
    for comment in comments:
        try:
            event = parse_comment(comment)
        except (IntakeError, TypeError, AttributeError) as exc:
            raise IntakeError("Invalid event requires manual review") from exc
        if event is None:
            continue
        if event["id"] in seen:
            raise IntakeError("Duplicate Issue event ID")
        seen.add(event["id"])
        event["state"] = "MIRRORED_IN_GIT" if event["id"] in saved else "ISSUE_ONLY_PENDING_MIRROR"
        records.append(event)
    return {"system": PRODUCT, "issue": ISSUE, "status": "VALIDATED_UNAPPROVED",
            "events": records, "pending_mirror": sum(e["state"] != "MIRRORED_IN_GIT" for e in records),
            "production_complete": False}

def fetch_live():
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise IntakeError("Redirect blocked")
    op = urllib.request.build_opener(NoRedirect())
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "WhiteChronos-memory-readonly"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    records = []
    for page in range(1, 11):
        url = "https://api.github.com/repos/WhiteChronos/ChatGPT/issues/" + str(ISSUE) + "/comments?per_page=100&page=" + str(page)
        with op.open(urllib.request.Request(url, headers=headers), timeout=15) as response:
            if response.geturl() != url:
                raise IntakeError("Unexpected API origin")
            payload = response.read(1048577)
        if len(payload) > 1048576:
            raise IntakeError("Oversized API response")
        chunk = json.loads(payload)
        if type(chunk) is not list:
            raise IntakeError("Invalid GitHub response")
        records.extend(chunk)
        if len(chunk) < 100:
            return records
    raise IntakeError("Issue pagination limit exceeded")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comments-json", type=Path)
    parser.add_argument("--memory", type=Path, default=Path(__file__).resolve().parents[1] / "spec" / "memoria.md")
    a = parser.parse_args()
    try:
        comments = json.loads(a.comments_json.read_text(encoding="utf-8")) if a.comments_json else fetch_live()
        if type(comments) is not list:
            raise IntakeError("Expected list of comments")
        print(json.dumps(inspect(comments, a.memory.read_text(encoding="utf-8")), ensure_ascii=False))
        return 0
    except (IntakeError, OSError, TypeError, json.JSONDecodeError):
        print(json.dumps({"system": PRODUCT, "status": "BLOCKED", "production_complete": False}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
