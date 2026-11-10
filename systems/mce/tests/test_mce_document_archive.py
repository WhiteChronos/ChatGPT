"""Windows-only synthetic regression for versioned document archival."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "mce_document_archive.py"
MEMORY = ROOT / "scripts" / "mce_memory.py"


def setup(tmp_path):
    inbox, vault, mirror = (tmp_path / x for x in ("inbox", "vault", "mirror"))
    for folder in (inbox, vault, mirror):
        folder.mkdir()
    spec = importlib.util.spec_from_file_location("mce_memory_archive_test", MEMORY)
    mem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mem)
    db = tmp_path / "mce-private.sqlite3"
    mem.init(db)
    return inbox, vault, mirror, db, mem


def call(inbox, vault, db, operation, *args, mirror=None):
    cmd = [sys.executable, str(SCRIPT), "--inbox", str(inbox),
           "--vault", str(vault), "--db", str(db), "--project", "ADM_GAMBOA",
           "--revision", "REV_A"]
    if mirror is not None:
        cmd += ["--mirror", str(mirror)]
    cmd += [operation, *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return result.returncode, json.loads(result.stdout)


def test_archive_idempotence_immutable_original_and_ledger(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    source = inbox / "MD.pdf"
    source.write_bytes(b"synthetic document A")
    before = source.read_bytes()
    code, data = call(inbox, vault, db, "ingest", "--filename", source.name, "--document", "MD-001")
    assert code == 0 and data["status"] == "ARCHIVED_VERIFIED"
    sha = hashlib.sha256(before).hexdigest()
    assert data["sha256"] == sha
    archived = vault / "objects" / sha[:2] / sha
    assert archived.read_bytes() == before
    assert source.read_bytes() == before
    code, _ = call(inbox, vault, db, "ingest", "--filename", source.name, "--document", "MD-001")
    assert code == 0
    assert mem.verify(db)["event_count"] == 1
    code, checked = call(inbox, vault, db, "verify", "--document", "MD-001", "--sha", sha)
    assert code == 0 and checked["status"] == "ARCHIVED_VERIFIED"


def test_new_bytes_create_new_version_without_overwriting_old(tmp_path):
    inbox, vault, _, db, mem = setup(tmp_path)
    source = inbox / "ET.docx"
    source.write_bytes(b"revision 1")
    assert call(inbox, vault, db, "ingest", "--filename", source.name, "--document", "ET")[0] == 0
    sha1 = hashlib.sha256(b"revision 1").hexdigest()
    source.write_bytes(b"revision 2")
    assert call(inbox, vault, db, "ingest", "--filename", source.name, "--document", "ET")[0] == 0
    sha2 = hashlib.sha256(b"revision 2").hexdigest()
    assert (vault / "objects" / sha1[:2] / sha1).read_bytes() == b"revision 1"
    assert (vault / "objects" / sha2[:2] / sha2).read_bytes() == b"revision 2"
    assert mem.verify(db)["event_count"] == 2


def test_secondary_copy_and_restore_to_new_path(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    original = b"private synthetic matrix"
    (inbox / "matrix.xlsx").write_bytes(original)
    code, data = call(inbox, vault, db, "ingest", "--filename", "matrix.xlsx",
                      "--document", "MCE", mirror=mirror)
    sha = hashlib.sha256(original).hexdigest()
    assert code == 0 and data["backup_status"] == "SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED"
    assert (mirror / "objects" / sha[:2] / sha).read_bytes() == original
    target = tmp_path / "restored.xlsx"
    code, restored = call(inbox, vault, db, "restore", "--document", "MCE",
                          "--sha", sha, "--output", str(target))
    assert code == 0 and restored["status"] == "RESTORE_VERIFIED"
    assert target.read_bytes() == original
    assert call(inbox, vault, db, "restore", "--document", "MCE",
                "--sha", sha, "--output", str(target))[0] == 2
    assert mem.verify(db)["event_count"] == 2


def test_archive_detects_corruption_before_claiming_success(tmp_path):
    inbox, vault, _, db, _ = setup(tmp_path)
    (inbox / "IO.txt").write_bytes(b"synthetic list")
    _, result = call(inbox, vault, db, "ingest", "--filename", "IO.txt", "--document", "IO")
    sha = result["sha256"]
    (vault / "objects" / sha[:2] / sha).write_bytes(b"tampered content")
    code, result = call(inbox, vault, db, "verify", "--document", "IO", "--sha", sha)
    assert code == 2 and result["status"] == "ARCHIVE_BLOCKED"
    code, result = call(inbox, vault, db, "ingest", "--filename", "IO.txt", "--document", "IO")
    assert code == 2 and result["status"] == "ARCHIVE_BLOCKED"


def test_uninitialized_database_and_path_escape_are_blocked(tmp_path):
    inbox, vault, _, db, _ = setup(tmp_path)
    (inbox / "file.txt").write_bytes(b"x")
    code, _ = call(inbox, vault, tmp_path / "absent.sqlite3", "ingest",
                   "--filename", "file.txt", "--document", "DOC")
    assert code == 2
    code, _ = call(inbox, vault, db, "ingest", "--filename", "../file.txt", "--document", "DOC")
    assert code == 2
    code, _ = call(inbox, vault, db, "ingest", "--filename", "file.txt", "--document", "bad/ID")
    assert code == 2
    code, _ = call(inbox, vault, db, "ingest", "--filename", "file.txt",
                   "--document", "DOC", mirror=vault)
    assert code == 2


def test_hardlink_and_symlink_sources_are_rejected(tmp_path):
    inbox, vault, _, db, _ = setup(tmp_path)
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"not an authorized upload")
    linked = inbox / "hard.bin"
    os.link(outside, linked)
    assert call(inbox, vault, db, "ingest", "--filename", linked.name,
                "--document", "DOC")[0] == 2
    sym = inbox / "shortcut.bin"
    try:
        sym.symlink_to(outside)
    except OSError:
        return
    assert call(inbox, vault, db, "ingest", "--filename", sym.name,
                "--document", "DOC")[0] == 2


def test_scan_skips_unfinished_files_without_creating_dummy_records(tmp_path):
    inbox, vault, _, db, mem = setup(tmp_path)
    (inbox / "README.pdf").write_bytes(b"ready")
    (inbox / "unfinished.part").write_bytes(b"partial")
    code, result = call(inbox, vault, db, "scan", "--min-age", "0")
    assert code == 0 and result["archived"] == 1 and result["failures"] == 0
    assert mem.verify(db)["event_count"] == 1


def test_backup_no_overwrite_and_no_mirror_overlap(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    (inbox / "source.pdf").write_bytes(b"test")
    assert call(inbox, vault, db, "ingest", "--filename", "source.pdf",
                "--document", "S", mirror=mirror)[0] == 0
    sha = hashlib.sha256(b"test").hexdigest()
    target = mirror / "objects" / sha[:2] / sha
    target.write_bytes(b"tampered")
    code, payload = call(inbox, vault, db, "ingest", "--filename", "source.pdf",
                         "--document", "S", mirror=mirror)
    assert code == 2 and payload["status"] == "ARCHIVE_BLOCKED"
    assert mem.verify(db)["event_count"] == 2


def test_catalogue_readonly_recovers_existing_project_and_secondary_proof(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    original = b"synthetic MCE data"
    (inbox / "mce.xlsx").write_bytes(original)
    sha = hashlib.sha256(original).hexdigest()
    assert call(inbox, vault, db, "ingest", "--filename", "mce.xlsx",
                "--document", "MCE", mirror=mirror)[0] == 0
    before = mem.verify(db)["event_count"]
    code, report = call(inbox, vault, db, "catalog", mirror=mirror)
    assert code == 0 and report["status"] == "CATALOG_VERIFIED"
    assert report["items"] == [{
        "document": "MCE", "revision": "REV_A", "sha256": sha,
        "size_bytes": len(original),
        "backup_status": "SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED",
    }]
    assert mem.verify(db)["event_count"] == before
    target = tmp_path / "recovered.xlsx"
    code, result = call(inbox, vault, db, "restore", "--document", "MCE",
                        "--sha", report["items"][0]["sha256"],
                        "--output", str(target))
    assert code == 0 and result["status"] == "RESTORE_VERIFIED"
    assert target.read_bytes() == original


def test_catalogue_fails_closed_on_corruption_and_missing_ledger(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    code, result = call(inbox, vault, db, "catalog", mirror=mirror)
    assert code == 0 and result["status"] == "CATALOG_EMPTY"
    (inbox / "md.pdf").write_bytes(b"document")
    code, result = call(inbox, vault, db, "ingest", "--filename", "md.pdf",
                        "--document", "MD", mirror=mirror)
    assert code == 0
    sha = result["sha256"]
    secondary = mirror / "objects" / sha[:2] / sha
    secondary.write_bytes(b"corrupt")
    code, result = call(inbox, vault, db, "catalog", mirror=mirror)
    assert code == 2 and result["status"] == "ARCHIVE_BLOCKED"
    secondary.write_bytes(b"document")
    receipt = vault / "receipts" / "ADM_GAMBOA" / "MD" / "REV_A" / (sha + ".json")
    receipt.write_text('{"product":"MCE_INDEPENDENTE","project":"ADM_GAMBOA","document":"MD","revision":"REV_A","sha256":"broken","size_bytes":8}', encoding="utf-8")
    code, result = call(inbox, vault, db, "catalog", mirror=mirror)
    assert code == 2 and result["status"] == "ARCHIVE_BLOCKED"


def test_catalogue_requires_initialized_sqlite_and_rejects_invalid_scope(tmp_path):
    inbox, vault, mirror, db, mem = setup(tmp_path)
    assert call(inbox, vault, tmp_path / "missing.sqlite3", "catalog")[0] == 2
    cmd = [sys.executable, str(SCRIPT), "--inbox", str(inbox),
           "--vault", str(vault), "--db", str(db), "--project", "../OTHER",
           "catalog"]
    attempt = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    assert attempt.returncode == 2
    assert json.loads(attempt.stdout)["status"] == "ARCHIVE_BLOCKED"
