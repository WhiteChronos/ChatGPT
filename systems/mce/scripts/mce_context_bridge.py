#!/usr/bin/env python3
"""Windows-only, read-only MCE handoff from GitHub pointers and private SQLite integrity."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

import mce_memory

PRODUCT = "MCE_INDEPENDENTE"
ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
MEMORY = ROOT / "spec" / "memoria.md"
IDENTIFIER = re.compile(r"^\|\s*((?:DEC|PEND)-MCE-[0-9]{3,6})\s*\|", re.M)
SHA = re.compile(r"^[0-9a-f]{40}$")


def _require_windows() -> None:
    if sys.platform != "win32":
        raise ValueError("WINDOWS_ONLY: MCE context requires native Windows")


def _checkout_head() -> str | None:
    """A local Git commit is not verification of the current remote PR head."""
    if not (REPO_ROOT / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--verify", "HEAD"],
            text=True, capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip().lower()
    return value if result.returncode == 0 and SHA.fullmatch(value) else None


def _public_memory() -> dict:
    if MEMORY.is_symlink() or not MEMORY.is_file():
        raise ValueError("Canonical GitHub memory is unavailable")
    raw = MEMORY.read_bytes()
    if len(raw) > 2_000_000:
        raise ValueError("Canonical memory exceeds the read-only snapshot limit")
    content = raw.decode("utf-8")
    if PRODUCT not in content or "PRODUCTION_COMPLETE=NO" not in content:
        raise ValueError("Canonical memory identity or production gate is missing")
    ids = IDENTIFIER.findall(content)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate decision or pending ID in canonical memory")
    return {
        "repository": "WhiteChronos/ChatGPT",
        "pr": 118,
        "issue": 120,
        "memory_path": "systems/mce/spec/memoria.md",
        "memory_sha256": hashlib.sha256(raw).hexdigest(),
        "decision_ids": [identifier for identifier in ids if identifier.startswith("DEC-")],
        "pending_ids": [identifier for identifier in ids if identifier.startswith("PEND-")],
        "local_checkout_commit": _checkout_head(),
        "remote_head_verified": False,
        "issue_event_content_verified": False,
    }


def _datacenter(db: str | None) -> dict:
    if db is None:
        return {"status": "PRIVATE_NOT_CONNECTED"}
    verified = mce_memory.verify(db)
    if verified["product"] != PRODUCT or verified["status"] != "INTEGRITY_PASS":
        raise ValueError("Unexpected product or failed DataCenter integrity")
    return {
        "status": "INTEGRITY_PASS",
        "event_count": verified["event_count"],
        "head_sha256": verified["head_sha256"],
        "by_kind": verified["by_kind"],
    }


def create_context(db: str | None = None) -> dict:
    """Metadata-only handoff: never copies SQLite events or engineering documents."""
    _require_windows()
    github = _public_memory()
    datacenter = _datacenter(db)
    return {
        "schema": "mce.context-handoff.v1",
        "product": PRODUCT,
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "CONTEXT_READY" if datacenter["status"] == "INTEGRITY_PASS" else "PUBLIC_CONTEXT_ONLY",
        "github": github,
        "datacenter": datacenter,
        "platform": "WINDOWS_NATIVE_ONLY",
        "chat_capture": "NOT_AUTOMATIC",
        "engineering_authorized": False,
        "recovery_phrase": (
            "Retomar MCE_INDEPENDENTE: verificar GitHub PR #118, Issue #120, "
            "systems/mce/spec/memoria.md, SHA e checks atuais; "
            "usar SQLite privado somente se a conexao Windows estiver autorizada."
        ),
        "review_required": [
            "Current remote PR head and checks must be verified separately by a GitHub connector",
            "GitHub Issue events may conflict semantically with matching Markdown IDs",
            "SQLite private contents, backups and engineering attachments are not in this handoff",
            "Any missing sources, approvals or revisions remain PENDING",
        ],
        "production_complete": False,
    }


def _write_private_snapshot(destination: str, result: dict) -> None:
    target = mce_memory._path(destination)
    mce_memory._new_file(target)
    try:
        target.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except Exception:
        target.unlink(missing_ok=True)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", help="Optional existing private MCE SQLite; never uploaded")
    parser.add_argument("--output", help="Optional NEW JSON file in authorized private Windows storage")
    args = parser.parse_args(argv)
    try:
        result = create_context(args.db)
        if args.output:
            _write_private_snapshot(args.output, result)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, sqlite3.Error):
        print(json.dumps({"product": PRODUCT, "status": "BLOCKED", "production_complete": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
