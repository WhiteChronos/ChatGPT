"""Windows workflow contract: read-only helper skills and three documented forks."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
TOP = ROOT.parents[1]
SKILLS = {
    "mce-restic-backup": ("WhiteChronos/restic", "restic/restic", "BSD-2-Clause"),
    "mce-kopia-backup": ("WhiteChronos/kopia", "kopia/kopia", "Apache-2.0"),
    "mce-watchdog-ingest": ("WhiteChronos/watchdog", "gorakhargosh/watchdog", "Apache-2.0"),
}

def test_three_skills_have_valid_metadata_and_mirror():
    for slug, (fork, upstream, license_name) in SKILLS.items():
        local = ROOT / ".agents/skills" / slug
        global_skill = TOP / ".agents/skills" / slug
        content = (local / "SKILL.md").read_text(encoding="utf-8")
        fm = yaml.safe_load(content.split("---", 2)[1])
        assert fm["name"] == slug
        assert set(fm) == {"name", "description"}
        assert 0 < len(fm["description"]) < 1024
        assert fork in content and upstream in content and license_name in content
        assert "main" in content and "master" in content
        assert "Windows" in content and "PRODUCTION_COMPLETE" in content
        for relative in ("SKILL.md", "agents/openai.yaml"):
            assert (local / relative).read_bytes() == (global_skill / relative).read_bytes()

def test_only_one_existing_mce_engine_and_archive():
    parent = (ROOT / ".agents/skills/matriz-causa-efeito/SKILL.md").read_text(encoding="utf-8")
    adapter = (ROOT / "scripts/mce_web.py").read_text(encoding="utf-8")
    for slug in SKILLS:
        assert slug in parent
        assert slug in adapter
    assert "mce_document_archive.py" in parent
    assert "mce_memory.py" in parent
    assert "backup/monitoramento" in parent

def test_helpers_have_no_executable_code():
    for slug in SKILLS:
        root = ROOT / ".agents/skills" / slug
        assert {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} == {
            "SKILL.md", "agents/openai.yaml"
        }
