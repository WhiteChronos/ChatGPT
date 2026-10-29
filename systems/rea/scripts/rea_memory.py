#!/usr/bin/env python3
"""Independent append-only REA_INDEPENDENTE continuity memory. No automatic approvals."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "REA_INDEPENDENTE"
SCHEMA = ROOT / "datacenter" / "schema.sql"
GENESIS = "0" * 64
KINDS = ("DECISION", "EVIDENCE", "PENDENCY", "STATUS", "NOTE")
SHA = re.compile(r"^[a-fA-F0-9]{64}$")
SENSITIVE_KEY = re.compile(r"(password|passwd|secret|token|api.?key|private.?key|credential)", re.I)
SENSITIVE_VALUE = re.compile(r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|authorization:\s*bearer\s+\S+)", re.I)
MAX_BYTES = 65536


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _path(raw: str | Path) -> Path:
    path = Path(raw).expanduser().absolute()
    if path.is_relative_to(ROOT.resolve()):
        raise ValueError("Operational storage inside source checkout is forbidden")
    if not path.parent.is_dir():
        raise ValueError("An existing private destination directory is required")
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("Symlink paths are forbidden")
    if path.exists() and not path.is_file():
        raise ValueError("Expected a regular file")
    return path


def _new_file(path: Path) -> None:
    if path.exists():
        raise ValueError("Existing file cannot be overwritten")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    os.close(fd)


def _connect(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise ValueError("Database must first be initialized explicitly")
    if os.name == "posix" and (stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise ValueError("Database must be owner-only (0600)")
    con = sqlite3.connect(str(path), timeout=15)
    con.execute("PRAGMA busy_timeout=15000")
    con.execute("PRAGMA synchronous=FULL")
    con.execute("PRAGMA foreign_keys=ON")
    return con


@contextmanager
def _session(path: Path):
    con = _connect(path)
    try:
        with con:
            yield con
    finally:
        con.close()


def _digest(event: dict) -> str:
    return hashlib.sha256(_canonical(event).encode("utf-8")).hexdigest()


def _verify(con: sqlite3.Connection) -> dict:
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise ValueError("SQLite integrity check failed")
    meta = dict(con.execute("SELECT key,value FROM system_meta"))
    if meta.get("product") != PRODUCT or meta.get("schema_version") != "1":
        raise ValueError("Database belongs to another product or schema")
    triggers = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
    if not {"events_no_update", "events_no_delete"}.issubset(triggers):
        raise ValueError("Append-only triggers are missing")
    head = GENESIS
    count = 0
    by_kind = {name: 0 for name in KINDS}
    for row in con.execute(
        "SELECT seq,event_id,created_utc,kind,subject,detail_json,reference,"
        "source_sha256,prev_digest,digest FROM memory_events ORDER BY seq"
    ):
        seq, event_id, created_utc, kind, subject, detail_json, reference, source_sha256, prev_digest, digest = row
        count += 1
        if seq != count or kind not in KINDS or prev_digest != head:
            raise ValueError("Memory chain sequence or link mismatch")
        payload = json.loads(detail_json)
        if not isinstance(payload, dict) or _canonical(payload) != detail_json:
            raise ValueError("Noncanonical payload")
        signed = dict(seq=seq, event_id=event_id, created_utc=created_utc, kind=kind,
                      subject=subject, detail_json=detail_json, reference=reference,
                      source_sha256=source_sha256, prev_digest=prev_digest)
        if _digest(signed) != digest:
            raise ValueError("Memory digest mismatch")
        head = digest
        by_kind[kind] += 1
    return {"product": PRODUCT, "schema_version": 1, "status": "INTEGRITY_PASS",
            "event_count": count, "head_sha256": head, "by_kind": by_kind,
            "production_complete": False,
            "note": "SHA chain is not a trusted signature or engineering acceptance"}


def _reject_sensitive(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or SENSITIVE_KEY.search(key):
                raise ValueError("Sensitive or invalid field key")
            _reject_sensitive(item)
    elif isinstance(value, list):
        for item in value:
            _reject_sensitive(item)
    elif isinstance(value, str) and SENSITIVE_VALUE.search(value):
        raise ValueError("Potential credential detected; refuse storage")


def init(db: str | Path) -> dict:
    path = _path(db)
    if path.exists():
        with _session(path) as con:
            return _verify(con)
    _new_file(path)
    try:
        with _session(path) as con:
            con.executescript(SCHEMA.read_text(encoding="utf-8"))
            con.executemany("INSERT INTO system_meta (key,value) VALUES (?,?)",
                            [("product", PRODUCT), ("schema_version", "1")])
            return _verify(con)
    except Exception:
        path.unlink(missing_ok=True)
        raise


def verify(db: str | Path) -> dict:
    with _session(_path(db)) as con:
        return _verify(con)


def append(db: str | Path, kind: str, subject: str, detail: dict,
           reference: str = "", source_sha256: str = "") -> dict:
    if kind not in KINDS or not isinstance(subject, str) or not 1 <= len(subject.strip()) <= 200:
        raise ValueError("Invalid event kind or subject")
    if not isinstance(detail, dict) or not isinstance(reference, str) or len(reference) > 300:
        raise ValueError("Invalid payload or reference")
    if source_sha256 and (not isinstance(source_sha256, str) or not SHA.fullmatch(source_sha256)):
        raise ValueError("Expected 64-character hexadecimal SHA-256")
    _reject_sensitive({"subject": subject, "reference": reference, "detail": detail})
    encoded = _canonical(detail)
    if len(encoded.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Memory event exceeds size limit")
    with _session(_path(db)) as con:
        con.execute("BEGIN IMMEDIATE")
        prior = _verify(con)
        row = dict(seq=prior["event_count"] + 1, event_id=str(uuid.uuid4()),
                   created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   kind=kind, subject=subject.strip(), detail_json=encoded, reference=reference,
                   source_sha256=source_sha256.lower(), prev_digest=prior["head_sha256"])
        digest = _digest(row)
        con.execute("INSERT INTO memory_events "
                    "(seq,event_id,created_utc,kind,subject,detail_json,reference,source_sha256,prev_digest,digest) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)", (*row.values(), digest))
        return {"product": PRODUCT, "seq": row["seq"], "event_sha256": digest,
                "production_complete": False}


def datasheet(db: str | Path, output: str | Path, *, full: bool = False) -> dict:
    path = _path(output)
    if path.exists():
        raise ValueError("DataSheet already exists; use a versioned destination")
    with _session(_path(db)) as con:
        status = _verify(con)
        records = []
        for row in con.execute("SELECT seq,created_utc,kind,subject,detail_json,reference,"
                               "source_sha256,digest FROM memory_events ORDER BY seq"):
            seq, created, kind, subject, details, reference, source_sha, digest = row
            entry = {"seq": seq, "created_utc": created, "kind": kind, "subject": subject,
                     "reference": reference, "source_sha256": source_sha, "digest": digest}
            if full:
                entry["detail"] = json.loads(details)
            records.append(entry)
    sheet = {"product": PRODUCT, "schema_version": 1,
             "exported_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "integrity": "INTEGRITY_PASS", "event_count": status["event_count"],
             "head_sha256": status["head_sha256"], "by_kind": status["by_kind"],
             "events": records, "production_complete": False}
    _new_file(path)
    try:
        path.write_text(json.dumps(sheet, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return {"product": PRODUCT, "export_path": str(path), "full_export": full,
            "event_count": len(records), "production_complete": False}


def search(db: str | Path, text: str, limit: int = 50) -> dict:
    """Find prior events by content, return metadata only (no private payloads)."""
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 120:
        raise ValueError("Search text must be 1-120 characters")
    if not 1 <= limit <= 100:
        raise ValueError("Search limit out of bounds")
    with _session(_path(db)) as con:
        _verify(con)
        pattern = '%' + text.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        rows = con.execute(
            "SELECT seq,kind,subject,created_utc,digest FROM memory_events "
            "WHERE subject LIKE ? ESCAPE '\\' OR detail_json LIKE ? ESCAPE '\\' "
            "ORDER BY seq DESC LIMIT ?", (pattern, pattern, limit)
        ).fetchall()
    return {"product": PRODUCT, "query": text, "matches": [
        {"seq": seq, "kind": kind, "subject": subject, "created_utc": created,
         "digest": digest} for seq, kind, subject, created, digest in rows],
        "production_complete": False}


def backup(db: str | Path, output: str | Path) -> dict:
    source, dest = _path(db), _path(output)
    _new_file(dest)
    try:
        with _session(source) as con, _connect(dest) as target:
            _verify(con)
            con.backup(target)
            result = _verify(target)
        return {"product": PRODUCT, "event_count": result["event_count"],
                "backup_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
                "production_complete": False}
    except Exception:
        dest.unlink(missing_ok=True)
        raise


def restore(source: str | Path, db: str | Path) -> dict:
    backup_path, dest = _path(source), _path(db)
    if dest.exists():
        raise ValueError("Restore never overwrites an existing database")
    with _session(backup_path) as con:
        _verify(con)
    _new_file(dest)
    try:
        with _session(backup_path) as con, _connect(dest) as target:
            con.backup(target)
            return _verify(target)
    except Exception:
        dest.unlink(missing_ok=True)
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="External private SQLite file")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("verify")
    find = commands.add_parser("search")
    find.add_argument("--text", required=True)
    find.add_argument("--limit", type=int, default=50)
    record = commands.add_parser("record")
    record.add_argument("--kind", required=True, choices=KINDS)
    record.add_argument("--subject", required=True)
    record.add_argument("--detail", default="{}")
    record.add_argument("--reference", default="")
    record.add_argument("--source-sha256", default="")
    data = commands.add_parser("datasheet")
    data.add_argument("--output", required=True)
    data.add_argument("--full", action="store_true")
    back = commands.add_parser("backup")
    back.add_argument("--output", required=True)
    recovery = commands.add_parser("restore")
    recovery.add_argument("--backup", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = init(args.db)
        elif args.command == "verify":
            result = verify(args.db)
        elif args.command == "search":
            result = search(args.db, args.text, args.limit)
        elif args.command == "record":
            result = append(args.db, args.kind, args.subject, json.loads(args.detail),
                            args.reference, args.source_sha256)
        elif args.command == "datasheet":
            result = datasheet(args.db, args.output, full=args.full)
        elif args.command == "backup":
            result = backup(args.db, args.output)
        else:
            result = restore(args.backup, args.db)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (ValueError, OSError, sqlite3.Error, TypeError, json.JSONDecodeError):
        print(json.dumps({"product": PRODUCT, "status": "BLOCKED", "production_complete": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
