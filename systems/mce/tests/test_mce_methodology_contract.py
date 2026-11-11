"""Regressao documental: regras de completude funcional MCE, sem fontes industriais."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "EXECUCAO.md",
    ROOT / ".agents" / "skills" / "matriz-causa-efeito" / "SKILL.md",
    ROOT / ".agents" / "skills" / "matriz-causa-efeito" / "references" / "metodo-e-saidas.md",
]

def test_methodology_rule_is_mirrored_in_canonical_places():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for key in (
            "DEC-MCE-068", "Observacao por causa", "X seletivo e auditavel",
            "SP condicionado ao contrato", "PENDENTE_DE_EVIDENCIA",
            "AUTORIZO_ELABORACAO_MCE", "ANALISADO_AGUARDANDO_DECISAO",
        ):
            assert key in text, (str(path), key)

def test_engineering_skill_delegates_to_canonical_method():
    text = (ROOT / ".agents" / "skills" / "engenharia-mce-projeto" / "SKILL.md").read_text(encoding="utf-8")
    assert "DEC-MCE-068" in text
    assert "metodo-e-saidas.md" in text
    assert "nao usar texto generico" in text

def test_no_false_approval_claim_in_methodology():
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        block = text.split("## Contrato de completude funcional — DEC-MCE-068")[-1]
        assert "STOP" in block
        assert "nao editar mestre" in block.lower()
        assert "X em todas as colunas" in block
