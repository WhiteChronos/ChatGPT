"""Agente de compilação e verificação de comentários técnicos.

O agente interpreta a linguagem natural. Integridade, fechamento e persistência
permanecem sob regras determinísticas e confirmação humana.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

from agents import Agent, Runner
from pydantic import BaseModel, Field


Severity = Literal["GRAVE", "ALTO", "LEVE"]


class CommentRecord(BaseModel):
    comment_id: str = Field(pattern=r"^C\d{2,}$")
    severity: Severity
    document_code: str | None = None
    revision: str | None = None
    page_or_item: str | None = None
    original_comment: str = Field(min_length=1)
    compiled_action: str = Field(min_length=1)
    required_documents: list[str] = Field(default_factory=list)


class NewDivergence(BaseModel):
    severity: Severity = "ALTO"
    document_code: str | None = None
    revision: str | None = None
    page_or_item: str | None = None
    original_comment: str = Field(min_length=1)
    compiled_action: str = Field(min_length=1)
    required_documents: list[str] = Field(default_factory=list)


class CommentCompilation(BaseModel):
    project_id: str = Field(min_length=1)
    source_formal_comment_count: int = Field(ge=0)
    comments: list[CommentRecord] = Field(default_factory=list)
    new_divergences: list[NewDivergence] = Field(default_factory=list)


FALLBACK_INSTRUCTIONS = """
Você é um Analista Sênior de Dados e Governança Documental com experiência equivalente a décadas de prática em engenharia, qualidade, auditoria, estatística e controle de configuração.

REGRAS INVIOLÁVEIS:
1. Preserve 100% dos comentários formais e sua ordem.
2. Nunca marque comentário como atendido. O status de controle é externo ao agente e começa UNCHECKED/☐.
3. Não funda comentários diferentes, mesmo quando semelhantes.
4. Mantenha novas divergências separadas dos comentários formais.
5. Use somente GRAVE, ALTO ou LEVE.
6. Em compiled_action escreva somente a ação objetiva que precisa ser executada ou confirmada.
7. Preserve documento, revisão, folha, item e tag quando existirem; não invente dados ausentes.
8. Se o relatório disser que um item está 100% atendido, mantenha o comentário e formule o requisito técnico que deve ser verificado no controle.
9. source_formal_comment_count deve refletir a quantidade explícita de comentários formais da origem.
10. A saída deve ser estruturada e auditável.
""".strip()


def _instructions() -> str:
    prompt_path = Path(__file__).resolve().parents[1] / "docs" / "comment-control-agent-prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return FALLBACK_INSTRUCTIONS


def build_agent() -> Agent:
    return Agent(
        name="CommentControlSeniorAnalyst",
        instructions=_instructions(),
        output_type=CommentCompilation,
    )


async def compile_comments(report_text: str, project_id: str) -> CommentCompilation:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY ausente")
    agent = build_agent()
    prompt = (
        f"PROJETO: {project_id}\n\n"
        "Analise o relatório abaixo e devolva todos os comentários formais no contrato estruturado. "
        "Novas divergências devem permanecer separadas.\n\n"
        f"RELATÓRIO:\n{report_text}"
    )
    result = await Runner.run(agent, prompt)
    output = result.final_output
    if not isinstance(output, CommentCompilation):
        output = CommentCompilation.model_validate(output)
    return output


def to_storage_payload(compilation: CommentCompilation) -> dict[str, Any]:
    """Converte a saída do agente para persistência com status inicial obrigatório UNCHECKED."""
    records: list[dict[str, Any]] = []
    for item in compilation.comments:
        row = item.model_dump()
        row.update(
            {
                "project_id": compilation.project_id,
                "source_comment_id": item.comment_id,
                "origin_type": "FORMAL_COMMENT",
                "status_control": "UNCHECKED",
                "evidence_text": None,
                "evidence_document": None,
                "evidence_revision": None,
                "evidence_location": None,
            }
        )
        records.append(row)

    divergences = [item.model_dump() for item in compilation.new_divergences]
    return {
        "project_id": compilation.project_id,
        "source_formal_comment_count": compilation.source_formal_comment_count,
        "comments": records,
        "new_divergences": divergences,
    }


if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", default="comment_compilation.json")
    args = parser.parse_args()

    text = Path(args.report).read_text(encoding="utf-8")
    compiled = asyncio.run(compile_comments(text, args.project))
    payload = to_storage_payload(compiled)
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
