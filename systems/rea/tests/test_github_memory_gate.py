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
    assert not GATE.owned("systems/mce/scripts/mce_workflow.py")
    GATE.verify_document(text(), text(), ["systems/mce/scripts/mce_workflow.py"])


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
