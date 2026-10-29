"""Regression: canonical REA memory must not depend on chat history."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "github_memory_gate.py"
SPEC = importlib.util.spec_from_file_location("rea_memory_git_gate_test", SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
MEM = "systems/rea/spec/memoria.md"


def text():
    return (ROOT / "spec/memoria.md").read_text(encoding="utf-8")


def test_current_checkpoint():
    result = GATE.verify_document(text(), text(), [])
    assert result["status"] == "PASS" and result["decisions"] >= 12
    assert result["pending"] >= 7 and result["production_complete"] is False


def test_code_without_memory_update_rejected():
    with pytest.raises(GATE.MemoryGateError, match="same commit"):
        GATE.verify_document(text(), text(), ["systems/rea/scripts/change.py"])


def test_skill_without_memory_update_rejected():
    with pytest.raises(GATE.MemoryGateError, match="same commit"):
        GATE.verify_document(text(), text(), [".agents/skills/rea-engenharia-reversa-evolutiva/SKILL.md"])


def test_unrelated_product_does_not_modify_rea_requirement():
    assert not GATE.owned("systems/mce/scripts/change.py")
    GATE.verify_document(text(), text(), ["systems/mce/scripts/change.py"])


def test_previous_history_must_be_prefix():
    with pytest.raises(GATE.MemoryGateError, match="exact prefix"):
        GATE.verify_document(text()[:-30], text(), [MEM])


def test_undated_appendix_is_rejected():
    with pytest.raises(GATE.MemoryGateError, match="dated"):
        GATE.verify_document(text() + "\nUntracked change", text(), [MEM])


def test_dated_appendix_and_source_change_pass():
    newer = text() + "\n2026-10-29 - DEC-REA retained with source\n"
    result = GATE.verify_document(newer, text(), [MEM, "systems/rea/scripts/change.py"])
    assert result["memory_updated"]


def test_duplicate_id_rejected():
    row = next(x for x in text().splitlines() if x.startswith("| DEC-REA-001 |"))
    with pytest.raises(GATE.MemoryGateError, match="duplicate"):
        GATE.verify_document(text() + "\n" + row, None, [MEM])


def test_secret_rejected():
    with pytest.raises(GATE.MemoryGateError, match="credential"):
        GATE.verify_document(text() + "\nAuthorization: Bearer confidential", None, [MEM])


def test_entrypoints_are_on_github():
    for name in ("AGENTS.md", "README.md"):
        assert "spec/memoria.md" in (ROOT / name).read_text(encoding="utf-8")
    assert "https://github.com/WhiteChronos/ChatGPT/issues/121" in text()


def _git_fixture(tmp_path):
    import subprocess
    root = tmp_path / "git-history"
    root.mkdir()
    memory = root / "systems" / "rea" / "spec" / "memoria.md"
    memory.parent.mkdir(parents=True)
    memory.write_text(text(), encoding="utf-8")
    def cmd(*args):
        return subprocess.run(["git", "-C", str(root), *args], check=True,
                              text=True, capture_output=True).stdout.strip()
    cmd("init", "-q")
    cmd("config", "user.name", "Test")
    cmd("config", "user.email", "test@example.invalid")
    cmd("add", ".")
    cmd("commit", "-qm", "baseline")
    return root, memory, cmd, cmd("rev-parse", "HEAD")

def test_history_detects_late_memory_after_unrecorded_code(tmp_path):
    root, memory, cmd, baseline = _git_fixture(tmp_path)
    (root / "systems" / "rea" / "change.py").write_text("changed=True\n")
    cmd("add", ".")
    cmd("commit", "-qm", "code without memory")
    memory.write_text(memory.read_text() + "\n2026-10-29 - late repair\n")
    cmd("add", ".")
    cmd("commit", "-qm", "late memory")
    with pytest.raises(GATE.MemoryGateError, match="same commit"):
        GATE.audit_commit_range(root, baseline, cmd("rev-parse", "HEAD"))

def test_history_accepts_atomic_code_and_memory(tmp_path):
    root, memory, cmd, baseline = _git_fixture(tmp_path)
    (root / "systems" / "rea" / "change.py").write_text("changed=True\n")
    memory.write_text(memory.read_text() + "\n2026-10-29 - atomic record\n")
    cmd("add", ".")
    cmd("commit", "-qm", "atomic")
    assert GATE.audit_commit_range(root, baseline, cmd("rev-parse", "HEAD")) == 1

def test_missing_baseline_is_blocked(tmp_path):
    root, memory, cmd, baseline = _git_fixture(tmp_path)
    with pytest.raises(GATE.MemoryGateError, match="baseline"):
        GATE.audit_commit_range(root, "0" * 40, cmd("rev-parse", "HEAD"))
