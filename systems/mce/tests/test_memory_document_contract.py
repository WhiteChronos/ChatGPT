"""Prevent silent loss of MCE continuity entrypoints."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_memory_document_is_present_and_identifies_its_product():
    content = (ROOT / "spec" / "memoria.md").read_text(encoding="utf-8")
    assert "DEC-MCE-001" in content
    assert "PEND-MCE-001" in content
    assert "PRODUCTION_COMPLETE=NO" in content
    assert "2026-10-29" in content
    assert "não" in content.lower() or "nao" in content.lower()


def test_entrypoints_link_to_memory():
    for name in ("AGENTS.md", "README.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "spec/memoria.md" in text
    assert "docs/DATACENTER_MEMORY.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
