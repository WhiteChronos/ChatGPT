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


def test_mce_excel_is_only_primary_output_regression():
    """Incident regression: PDF/MD must never replace the P09 Excel MCE."""
    skill = (LOCAL / "SKILL.md").read_text(encoding="utf-8")
    rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    execution = (ROOT / "docs" / "EXECUCAO.md").read_text(encoding="utf-8")
    for content in (skill, rules, execution):
        assert "DEC-MCE-032" in content
        assert "MCE_XLSX" in content
        assert "NAO_EMITIDO_BLOQUEADO" in content
        assert "FAIL_FORMAT_CONTRACT" in content
    assert "P09_L50_APROVADO_VISUALMENTE" in skill
    assert "FOLHA N" in skill
    assert "43 causas" in skill
    assert "35" in skill
    assert "PDF" in skill and "Markdown" in skill
    assert "AUTORIZO_ELABORACAO_MCE" in skill
    assert (LOCAL / "SKILL.md").read_bytes() == (GLOBAL / "SKILL.md").read_bytes()


def test_p09_l50_progressive_layout_rule_persists_in_all_mce_skills():
    main=(LOCAL/'SKILL.md').read_text(encoding='utf-8')
    engineering=(ROOT/'.agents/skills/engenharia-mce-projeto/SKILL.md').read_text(encoding='utf-8')
    standard=(ROOT/'.agents/skills/padronizacao-mce/SKILL.md').read_text(encoding='utf-8')
    execution=(ROOT/'docs/EXECUCAO.md').read_text(encoding='utf-8')
    agents=(ROOT/'AGENTS.md').read_text(encoding='utf-8')
    for content in (main,engineering,standard,execution,agents):
        assert 'DEC-MCE-034' in content
        assert '40' in content and '50' in content and '20' in content
        assert 'P09_L50_20261110' in content
    assert '43' in main and 'B=25' in main and 'C=56' in main and 'F=34' in main


def test_p09_l50_single_visual_line_must_stay_20pt_policy():
    """DEC-MCE-035: prevent an oversized 30pt row for single-line text."""
    primary=(LOCAL / "SKILL.md").read_text(encoding="utf-8")
    main_rules=(ROOT / "AGENTS.md").read_text(encoding="utf-8")
    execution=(ROOT / "docs" / "EXECUCAO.md").read_text(encoding="utf-8")
    for doc in (primary,main_rules,execution):
        assert "DEC-MCE-035" in doc
        assert "20 pt" in doc and "30 pt" in doc
        assert "F:G" in doc
    assert "18 pixels" in primary
    assert "QA_VISUAL_WINDOWS=NOT_RUN" in primary
    assert "sem spawn" in primary  # real agent requires verified lifecycle evidence


def test_column_width_2_correction_reverts_medium_borders():
    """DEC-MCE-037 supersedes DEC-MCE-036: border thin preserved."""
    documents=[(LOCAL/'SKILL.md').read_text(encoding='utf-8'),
       (ROOT/'AGENTS.md').read_text(encoding='utf-8'),
       (ROOT/'docs/EXECUCAO.md').read_text(encoding='utf-8'),
       (ROOT/'.agents/skills/padronizacao-mce/SKILL.md').read_text(encoding='utf-8'),
       (ROOT/'.agents/skills/engenharia-mce-projeto/SKILL.md').read_text(encoding='utf-8')]
    for s in documents:
        assert 'DEC-MCE-037' in s
        assert 'P09_L50_ALL_COLUMNS_2' in s
        assert 'thin' in s
    assert 'I:AQ' in documents[0] and 'A:AR' in documents[0]
    assert (LOCAL/'SKILL.md').read_bytes()==(GLOBAL/'SKILL.md').read_bytes()


def test_mce_g_ar_column_and_no_empty_effect_policy():
    """DEC-MCE-038: preserve original A:F; pending records remain outside the MCE."""
    main=(LOCAL/'SKILL.md').read_text(encoding='utf-8')
    execution=(ROOT/'docs/EXECUCAO.md').read_text(encoding='utf-8')
    agents=(ROOT/'AGENTS.md').read_text(encoding='utf-8')
    standard=(ROOT/'.agents/skills/padronizacao-mce/SKILL.md').read_text(encoding='utf-8')
    for document in (main,execution,agents,standard):
        assert 'DEC-MCE-038' in document
        assert 'P09_L50_G_AR_2' in document
        assert 'G:AR' in document
        assert 'thin' in document
        assert 'X' in document
    assert '76' in main and '142' in main and '175' in main
    assert (LOCAL/'SKILL.md').read_bytes()==(GLOBAL/'SKILL.md').read_bytes()
