"""Windows CI red-green tests for MCE cross-chat continuity snapshots."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "mce_context_bridge.py"
MEMORY_SCRIPT = ROOT / "scripts" / "mce_memory.py"


def run_bridge(*args):
    return subprocess.run(
        [sys.executable, str(BRIDGE), *map(str, args)],
        capture_output=True, text=True, timeout=45,
    )


def memory_module():
    spec = importlib.util.spec_from_file_location("mce_memory_handoff_test", MEMORY_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_handoff_identifies_sources_without_claiming_private_data():
    proc = run_bridge()
    assert proc.returncode == 0, proc.stderr or proc.stdout
    data = json.loads(proc.stdout)
    assert data["schema"] == "mce.context-handoff.v1"
    assert data["product"] == "MCE_INDEPENDENTE"
    assert data["status"] == "PUBLIC_CONTEXT_ONLY"
    assert data["github"]["repository"] == "WhiteChronos/ChatGPT"
    assert data["github"]["issue"] == 120
    assert data["github"]["pr"] == 118
    assert data["github"]["remote_head_verified"] is False
    assert len(data["github"]["memory_sha256"]) == 64
    assert data["datacenter"] == {"status": "PRIVATE_NOT_CONNECTED"}
    assert data["chat_capture"] == "NOT_AUTOMATIC"
    assert data["engineering_authorized"] is False
    assert data["production_complete"] is False
    assert "retomar MCE" in data["recovery_phrase"].lower()


def test_private_datacenter_integrity_uses_only_redacted_metadata(tmp_path):
    memory = memory_module()
    db = tmp_path / "private-mce.sqlite3"
    memory.init(db)
    memory.append(db, "NOTE", "P_AND_ID_SECRET", {"internal_note": "TOP_SECRET_TAG_3841"})
    proc = run_bridge("--db", db)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    data = json.loads(proc.stdout)
    assert data["status"] == "CONTEXT_READY"
    assert data["datacenter"]["status"] == "INTEGRITY_PASS"
    assert data["datacenter"]["event_count"] == 1
    assert data["datacenter"]["head_sha256"] == memory.verify(db)["head_sha256"]
    assert "P_AND_ID_SECRET" not in proc.stdout
    assert "TOP_SECRET_TAG_3841" not in proc.stdout
    assert str(db) not in proc.stdout
    assert "source_documents" not in proc.stdout


def test_corrupt_database_fails_closed_without_leaking_paths(tmp_path):
    db = tmp_path / "broken.sqlite3"
    db.write_bytes(b"not sqlite")
    proc = run_bridge("--db", db)
    assert proc.returncode == 2
    data = json.loads(proc.stdout)
    assert data["status"] == "BLOCKED"
    assert data["production_complete"] is False
    assert str(db) not in proc.stdout


def test_versioned_private_output_and_nonoverwrite(tmp_path):
    output = tmp_path / "MCE_CONTEXT_PRIVATE.json"
    proc = run_bridge("--output", output)
    assert proc.returncode == 0
    assert output.is_file()
    assert json.loads(output.read_text(encoding="utf-8"))["schema"] == "mce.context-handoff.v1"
    again = run_bridge("--output", output)
    assert again.returncode == 2
    assert json.loads(again.stdout)["status"] == "BLOCKED"


def test_new_chat_docs_and_skill_bind_all_three_layers():
    doc = (ROOT / "docs" / "RETOMADA_ENTRE_CHATS.md").read_text(encoding="utf-8")
    for token in ("Issue #120", "spec/memoria.md", "SQLite", "DataCenter",
                  "Windows", "retomar MCE", "PRODUCTION_COMPLETE=NO"):
        assert token in doc
    local = ROOT / ".agents" / "skills" / "matriz-causa-efeito" / "SKILL.md"
    mirror = ROOT.parents[1] / ".agents" / "skills" / "matriz-causa-efeito" / "SKILL.md"
    assert local.read_bytes() == mirror.read_bytes()
    instructions = local.read_text(encoding="utf-8")
    assert "mce_context_bridge.py" in instructions
    assert "RETOMADA_ENTRE_CHATS.md" in instructions
    assert "Windows" in instructions
