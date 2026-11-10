#!/usr/bin/env python3
"""Fail-closed, Windows-only archival of authorized MCE documents.

This does not fetch ChatGPT attachments or provision storage. The source inbox,
vault, secondary root and the single MCE SQLite must exist on the private host.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import uuid

import mce_memory as memory

PRODUCT = "MCE_INDEPENDENTE"
MAX_FILE_BYTES = 512 * 1024 * 1024
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
SKIP_SUFFIXES = (".part", ".tmp", ".crdownload", ".download", ".lock")


def require_windows():
    if sys.platform != "win32":
        raise ValueError("WINDOWS_ONLY: use native Windows and Python 3.12+")


def safe_id(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or ".." in value:
        raise ValueError("Unsafe project/document/revision identifier")
    return value


def safe_path(raw, kind):
    path = Path(raw).absolute()
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
            raise ValueError("Links or junctions are forbidden")
        if part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
            raise ValueError("Reparse points are forbidden")
    if kind == "dir":
        if not path.is_dir():
            raise ValueError("Preexisting authorized directory required")
    elif kind == "file":
        if not path.is_file() or not stat.S_ISREG(path.lstat().st_mode) or path.stat().st_nlink != 1:
            raise ValueError("Regular file without hardlinks required")
    elif kind == "new":
        if path.exists() or not path.parent.is_dir():
            raise ValueError("New file and existing destination parent required")
    else:
        raise ValueError("Invalid path kind")
    return path


def sha_file(path):
    h, total = hashlib.sha256(), 0
    with path.open("rb") as source:
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > MAX_FILE_BYTES:
                raise ValueError("File exceeds approved size budget")
            h.update(block)
    return h.hexdigest(), total


def require_roots(inbox, vault, db, mirror=None):
    inbox = safe_path(inbox, "dir")
    vault = safe_path(vault, "dir")
    memory._path(vault / "_archive-root-check")
    db = memory._path(db)
    memory.verify(db)
    if inbox == vault or vault.is_relative_to(inbox) or inbox.is_relative_to(vault):
        raise ValueError("Inbox and vault must not overlap")
    if mirror is not None:
        mirror = safe_path(mirror, "dir")
        memory._path(mirror / "_archive-mirror-check")
        if mirror == vault or mirror.is_relative_to(vault) or vault.is_relative_to(mirror):
            raise ValueError("Primary vault and secondary backup must not overlap")
        if mirror == inbox or mirror.is_relative_to(inbox) or inbox.is_relative_to(mirror):
            raise ValueError("Inbox and backup must not overlap")
    return inbox, vault, db, mirror


def private_dir(parent, name):
    safe_id(name)
    safe_path(parent, "dir")
    dest = parent / name
    if dest.exists():
        return safe_path(dest, "dir")
    dest.mkdir(mode=0o700)
    return safe_path(dest, "dir")


def copy_immutable(source, dest, expected_sha=None):
    """Atomic no-overwrite copy; verified against both source and destination."""
    source = safe_path(source, "file")
    if dest.exists():
        dest = safe_path(dest, "file")
        actual, size = sha_file(dest)
        if expected_sha is None:
            expected_sha, _ = sha_file(source)
        if actual != expected_sha:
            raise ValueError("Immutable destination differs from source")
        return actual, size
    safe_path(dest.parent, "dir")
    tmp = dest.with_name("." + uuid.uuid4().hex + ".partial")
    before = source.stat()
    if before.st_size > MAX_FILE_BYTES:
        raise ValueError("File exceeds approved size budget")
    digest, total = hashlib.sha256(), 0
    try:
        with source.open("rb") as src, tmp.open("xb") as out:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_FILE_BYTES:
                    raise ValueError("File exceeds approved size budget")
                digest.update(chunk)
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        actual = digest.hexdigest()
        after = source.stat()
        if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
            raise ValueError("Source changed while archiving")
        if expected_sha and actual != expected_sha:
            raise ValueError("Unexpected source digest")
        if sha_file(source) != (actual, total) or sha_file(tmp) != (actual, total):
            raise ValueError("Source or staged copy changed")
        if dest.exists():
            if sha_file(safe_path(dest, "file")) != (actual, total):
                raise ValueError("Concurrent archive conflict")
        else:
            os.rename(tmp, dest)  # On Windows, rename never replaces existing files.
        if sha_file(safe_path(dest, "file")) != (actual, total):
            raise ValueError("Archived file verification failed")
        return actual, total
    finally:
        tmp.unlink(missing_ok=True)


def bytes_immutable(dest, payload):
    if dest.exists():
        if safe_path(dest, "file").read_bytes() != payload:
            raise ValueError("Immutable metadata conflict")
        return
    safe_path(dest.parent, "dir")
    tmp = dest.with_name("." + uuid.uuid4().hex + ".partial")
    try:
        with tmp.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if dest.exists():
            if safe_path(dest, "file").read_bytes() != payload:
                raise ValueError("Concurrent metadata conflict")
        else:
            os.rename(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)


def records(vault, project, document, revision, sha):
    recroot = private_dir(vault, "receipts")
    recroot = private_dir(recroot, project)
    recroot = private_dir(recroot, document)
    recroot = private_dir(recroot, revision)
    return recroot / (sha + ".json")


def object_path(vault, sha):
    objroot = private_dir(vault, "objects")
    folder = private_dir(objroot, sha[:2])
    return folder / sha


def ledged(db, subject, detail, sha):
    """Use only the existing append-only SQLite event ledger; no second database."""
    db = memory._path(db)
    memory.verify(db)
    with memory._session(db) as con:
        for (encoded,) in con.execute(
            "SELECT detail_json FROM memory_events "
            "WHERE kind='EVIDENCE' AND subject=? AND source_sha256=?",
            (subject, sha),
        ):
            if json.loads(encoded) == detail:
                return
    memory.append(db, "EVIDENCE", subject, detail, reference="DEC-MCE-030", source_sha256=sha)


def receipt_check(vault, db, project, document, revision, sha):
    rec = safe_path(records(vault, project, document, revision, sha), "file")
    data = json.loads(rec.read_text(encoding="utf-8"))
    if any(data.get(k) != v for k, v in {
        "product": PRODUCT, "project": project, "document": document,
        "revision": revision, "sha256": sha,
    }.items()):
        raise ValueError("Receipt identity mismatch")
    blob = safe_path(object_path(vault, sha), "file")
    if sha_file(blob) != (sha, data["size_bytes"]):
        raise ValueError("Archived bytes corrupt")
    detail = {"project": project, "document": document, "revision": revision,
              "size_bytes": data["size_bytes"], "sha256": sha}
    ledged(db, "DOCUMENT_ARCHIVED", detail, sha)
    return data, rec, blob


def archive(inbox, vault, db, project, document, revision, filename, mirror=None):
    require_windows()
    project, document, revision = map(safe_id, (project, document, revision))
    inbox, vault, db, mirror = require_roots(inbox, vault, db, mirror)
    if Path(filename).name != filename or filename in (".", ".."):
        raise ValueError("Only direct child filenames of the authorized inbox are accepted")
    source = safe_path(inbox / filename, "file")
    digest, size = sha_file(source)
    blob = object_path(vault, digest)
    if not blob.exists():
        copy_immutable(source, blob, digest)
    elif sha_file(safe_path(blob, "file")) != (digest, size):
        raise ValueError("Preexisting archive corrupted")
    rec = records(vault, project, document, revision, digest)
    if not rec.exists():
        manifest = {
            "product": PRODUCT, "project": project, "document": document,
            "revision": revision, "source_name": filename,
            "sha256": digest, "size_bytes": size,
            "archived_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        bytes_immutable(rec, (json.dumps(manifest, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    receipt_check(vault, db, project, document, revision, digest)
    result = {"product": PRODUCT, "status": "ARCHIVED_VERIFIED",
              "sha256": digest, "size_bytes": size, "backup_status": "PENDING",
              "production_complete": False}
    if mirror is not None:
        mirror_document(vault, mirror, db, project, document, revision, digest)
        result["backup_status"] = "SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED"
    return result


def mirror_document(vault, mirror, db, project, document, revision, sha):
    require_windows()
    vault, mirror = safe_path(vault, "dir"), safe_path(mirror, "dir")
    memory._path(vault / "_verify")
    memory._path(mirror / "_verify")
    if vault == mirror or mirror.is_relative_to(vault) or vault.is_relative_to(mirror):
        raise ValueError("Mirror overlaps the primary vault")
    _, rec, blob = receipt_check(vault, db, project, document, revision, sha)
    destblob = object_path(mirror, sha)
    copy_immutable(blob, destblob, sha)
    destrec = records(mirror, project, document, revision, sha)
    bytes_immutable(destrec, rec.read_bytes())
    if sha_file(safe_path(destblob, "file")) != sha_file(blob) or destrec.read_bytes() != rec.read_bytes():
        raise ValueError("Secondary copy verification failed")
    manifest = {"project": project, "document": document, "revision": revision, "sha256": sha}
    ledged(db, "DOCUMENT_BACKUP_VERIFIED", manifest, sha)


def verify_one(vault, db, project, document, revision, sha):
    require_windows()
    vault = safe_path(vault, "dir")
    memory._path(vault / "_verify")
    memory.verify(db)
    data, _, blob = receipt_check(vault, db, project, document, revision, sha)
    return {"status": "ARCHIVED_VERIFIED", "sha256": sha, "size_bytes": data["size_bytes"],
            "production_complete": False}


def restore_one(vault, db, project, document, revision, sha, output):
    require_windows()
    data, _, blob = receipt_check(safe_path(vault, "dir"), db, project, document, revision, sha)
    dest = memory._path(output)
    if dest.exists():
        raise ValueError("Restore cannot overwrite existing file")
    copy_immutable(blob, dest, sha)
    return {"status": "RESTORE_VERIFIED", "sha256": sha,
            "size_bytes": data["size_bytes"], "production_complete": False}



def catalogue(vault, db, project, mirror=None):
    """Read-only, fail-closed recovery inventory of a private project's receipts."""
    require_windows()
    project = safe_id(project)
    vault = safe_path(vault, "dir")
    db = memory._path(db)
    memory.verify(db)
    if mirror is not None:
        mirror = safe_path(mirror, "dir")
        if mirror == vault or mirror.is_relative_to(vault) or vault.is_relative_to(mirror):
            raise ValueError("Secondary archive overlaps primary")
    root = vault / "receipts" / project
    if not root.exists():
        return {"product": PRODUCT, "status": "CATALOG_EMPTY", "items": [],
                "production_complete": False}
    safe_path(root, "dir")
    items = []
    with memory._session(db) as connection:
        for docroot in sorted(root.iterdir()):
            document = safe_id(docroot.name)
            safe_path(docroot, "dir")
            for revroot in sorted(docroot.iterdir()):
                revision = safe_id(revroot.name)
                safe_path(revroot, "dir")
                for receipt in sorted(revroot.iterdir()):
                    if receipt.suffix != ".json":
                        raise ValueError("Unexpected receipt file")
                    sha = receipt.stem
                    if not re.fullmatch(r"[0-9a-f]{64}", sha):
                        raise ValueError("Malformed receipt digest")
                    safe_path(receipt, "file")
                    if receipt.stat().st_size > 4096:
                        raise ValueError("Oversized receipt")
                    data = json.loads(receipt.read_text(encoding="utf-8"))
                    identity = {"product": PRODUCT, "project": project,
                                "document": document, "revision": revision, "sha256": sha}
                    if any(data.get(key) != value for key, value in identity.items()):
                        raise ValueError("Invalid receipt identity")
                    size = data.get("size_bytes")
                    if type(size) is not int or size < 0 or size > MAX_FILE_BYTES:
                        raise ValueError("Invalid receipt size")
                    blob = safe_path(vault / "objects" / sha[:2] / sha, "file")
                    if sha_file(blob) != (sha, size):
                        raise ValueError("Primary archive integrity failure")
                    recorded = False
                    for (encoded,) in connection.execute(
                        "SELECT detail_json FROM memory_events "
                        "WHERE kind='EVIDENCE' AND subject='DOCUMENT_ARCHIVED' AND source_sha256=?",
                        (sha,),
                    ):
                        try:
                            detail = json.loads(encoded)
                        except json.JSONDecodeError as exc:
                            raise ValueError("Invalid evidence ledger") from exc
                        if detail == {"project": project, "document": document,
                                      "revision": revision, "size_bytes": size, "sha256": sha}:
                            recorded = True
                            break
                    if not recorded:
                        raise ValueError("Receipt lacks matching SQLite evidence")
                    backup = "BACKUP_NOT_VERIFIED"
                    if mirror is not None:
                        other_receipt = safe_path(
                            mirror / "receipts" / project / document / revision / (sha + ".json"),
                            "file")
                        other_blob = safe_path(mirror / "objects" / sha[:2] / sha, "file")
                        if other_receipt.read_bytes() != receipt.read_bytes() or sha_file(other_blob) != (sha, size):
                            raise ValueError("Secondary archive integrity failure")
                        backup = "SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED"
                    items.append({"document": document, "revision": revision,
                                  "sha256": sha, "size_bytes": size, "backup_status": backup})
                    if len(items) > 10000:
                        raise ValueError("Recovery catalogue budget exceeded")
    return {"product": PRODUCT, "status": "CATALOG_VERIFIED",
            "items": items, "production_complete": False}


def scan(inbox, vault, db, project, revision, mirror=None, min_age=3):
    require_windows()
    inbox, vault, db, mirror = require_roots(inbox, vault, db, mirror)
    safe_id(project)
    safe_id(revision)
    results, failures = [], []
    for p in sorted(inbox.iterdir(), key=lambda x: x.name):
        if p.suffix.lower() in SKIP_SUFFIXES or p.name.startswith("."):
            continue
        try:
            safe_path(p, "file")
            if time.time() - p.stat().st_mtime < min_age:
                continue
            doc = "DOC_" + hashlib.sha256(p.name.encode("utf-8")).hexdigest()[:20]
            results.append(archive(inbox, vault, db, project, doc, revision, p.name, mirror))
        except (ValueError, OSError):
            failures.append(hashlib.sha256(p.name.encode("utf-8")).hexdigest()[:12])
    return {"status": "ARCHIVE_BLOCKED" if failures else "SCAN_COMPLETE",
            "archived": len(results), "failures": len(failures),
            "failed_file_ids": failures, "production_complete": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inbox", required=True)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--revision", default="NOT_DECLARED")
    parser.add_argument("--mirror")
    sub = parser.add_subparsers(dest="operation", required=True)
    item = sub.add_parser("ingest")
    item.add_argument("--filename", required=True)
    item.add_argument("--document", required=True)
    batch = sub.add_parser("scan")
    batch.add_argument("--min-age", type=float, default=3)
    watch = sub.add_parser("watch")
    watch.add_argument("--interval", type=float, default=10)
    watch.add_argument("--min-age", type=float, default=3)
    sub.add_parser("catalog")
    check = sub.add_parser("verify")
    check.add_argument("--document", required=True)
    check.add_argument("--sha", required=True)
    recover = sub.add_parser("restore")
    recover.add_argument("--document", required=True)
    recover.add_argument("--sha", required=True)
    recover.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        require_windows()
        if args.operation in ("ingest", "scan", "watch"):
            require_roots(args.inbox, args.vault, args.db, args.mirror)
        if args.operation == "ingest":
            result = archive(args.inbox, args.vault, args.db, args.project,
                             args.document, args.revision, args.filename, args.mirror)
        elif args.operation == "scan":
            result = scan(args.inbox, args.vault, args.db, args.project, args.revision,
                          args.mirror, args.min_age)
        elif args.operation == "watch":
            if args.interval < 1 or args.min_age < 0:
                raise ValueError("Invalid watch interval")
            try:
                while True:
                    report = scan(args.inbox, args.vault, args.db, args.project, args.revision,
                                  args.mirror, args.min_age)
                    print(json.dumps(report, sort_keys=True), flush=True)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                return 0
        elif args.operation == "catalog":
            result = catalogue(args.vault, args.db, args.project, args.mirror)
        elif args.operation == "verify":
            result = verify_one(args.vault, args.db, args.project,
                                args.document, args.revision, args.sha)
        else:
            result = restore_one(args.vault, args.db, args.project,
                                 args.document, args.revision, args.sha, args.output)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 2 if result.get("status") == "ARCHIVE_BLOCKED" else 0
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError):
        print(json.dumps({"product": PRODUCT, "status": "ARCHIVE_BLOCKED",
                          "production_complete": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
