"""TDD red: MCE must ship as standalone engineering product without REA machinery."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]

def test_no_rea_runtime_or_server():
    assert not (root/'integrations').exists()
    assert not (root/'docs/rea').exists()
    assert not (root/'scripts/rea_native_doctor.py').exists()
    assert not (root/'.agents/skills/engenharia-mce-projeto/references/rea-mcp-runtime.md').exists()

def test_mce_skill_contains_no_rea_dependency():
    skill=(root/'.agents/skills/engenharia-mce-projeto/SKILL.md').read_text().lower()
    assert re.search(r'\brea\b|rea[-_/]', skill) is None
    wf=(root/'workflow-mce.yaml').read_text().lower()
    assert re.search(r'\brea\b|rea[-_/]', wf) is None

def test_mce_own_workflow_present():
    assert (root/'scripts/mce_system.py').is_file()
    assert (root/'.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py').is_file()
    assert (root/'.agents/skills/padronizacao-mce/SKILL.md').is_file()
