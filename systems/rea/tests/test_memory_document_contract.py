"""Protect REA canonical memory entrypoints."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_memory_preserves_identity_and_gates():
    memory = (ROOT / "spec/memoria.md").read_text(encoding="utf-8")
    assert "REA_INDEPENDENTE" in memory
    assert "DEC-REA-001" in memory
    assert "PEND-REA-001" in memory
    assert "PRODUCTION_COMPLETE=NO" in memory


def test_onboarding_links_canonical_memory():
    for name in ("AGENTS.md", "README.md"):
        assert "spec/memoria.md" in (ROOT / name).read_text(encoding="utf-8")
    assert "docs/DATACENTER_MEMORY.md" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
