"""Validate the MCE-only GitHub skill and its synchronized local/global copies."""
from pathlib import Path
import yaml
import json
ROOT = Path(__file__).resolve().parents[1]
TOP = ROOT.parents[1]
LOCAL = ROOT / ".agents" / "skills" / "matriz-causa-efeito"
GLOBAL = TOP / ".agents" / "skills" / "matriz-causa-efeito"
MUST = ("SKILL.md", "agents/openai.yaml", "references/repositorios-github.md", "references/metodo-e-saidas.md", "references/operacao-ferramenta.md")

def test_skill_files_and_metadata():
    for name in MUST:
        assert (LOCAL/name).is_file()
        assert (GLOBAL/name).is_file()
        assert (LOCAL/name).read_bytes()==(GLOBAL/name).read_bytes()
    content=(LOCAL/"SKILL.md").read_text(encoding="utf-8")
    front=yaml.safe_load(content.split("---",2)[1])
    assert front["name"]=="matriz-causa-efeito"
    assert set(front)=={"name","description"}
    assert "MCE" in front["description"]
    assert len(front["description"])<1024
    assert "ANALISADO_AGUARDANDO_DECISAO" in content
    assert "AUTORIZO_ELABORACAO_MCE" in content
    assert "D9D9D9" in content
    assert "matriz_causa_efeito_tool.py" in content
    assert "MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json" in content

def test_no_independent_xlsx_editor_or_unsafe_references():
    paths=[p.relative_to(LOCAL).as_posix() for p in LOCAL.rglob("*") if p.is_file()]
    assert paths==sorted(MUST) or set(paths)==set(MUST)
    core=(LOCAL/"SKILL.md").read_text()
    assert "mce_workflow.py" in core
    assert "PRODUCTION_COMPLETE=YES" in core and "Sem merge/deploy" in core
    assert "REA" in core and "Nao usar" in core

def test_github_sources_are_references_not_engineering_authority():
    catalog=(LOCAL/"references/repositorios-github.md").read_text()
    for fragment in ("Azure-Samples/digitization-of-piping-and-instrument-diagrams","S-Houston/digitised-pid-mlops","process-intelligence-research/pyDEXPI","WhiteChronos/ChatGPT"):
        assert fragment in catalog
    assert "AGPL-3.0" in catalog
    assert "S-Houston/digitised-pid-mlops" in catalog
    assert "ZzzJjt/Industrial-Control" in catalog

def test_mce_onboarding_and_memory():
    manifest=json.loads((ROOT/"plugin.json").read_text(encoding="utf-8"))
    assert manifest["extensions"]["com.openai"]["onboardingSkill"]=="./.agents/skills/matriz-causa-efeito/SKILL.md"
    memory=(ROOT/"spec/memoria.md").read_text(encoding="utf-8")
    assert "DEC-MCE-016" in memory
    assert "PEND-MCE-011" in memory
    assert "DEC-MCE-015" in memory
