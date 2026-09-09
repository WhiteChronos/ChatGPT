"""Agente de compilação e pré-verificação de comentários técnicos.

O agente interpreta a linguagem natural. Dúvidas permanecem em um canal interno de
pré-verificação e bloqueiam qualquer artefato até serem resolvidas. Integridade,
fechamento e persistência permanecem sob regras determinísticas e confirmação humana.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal

from agents import Agent, Runner
from pydantic import BaseModel, Field


Severity = Literal["GRAVE", "ALTO", "LEVE"]
ResolutionType = Literal["CONFIRMED_ERROR", "DISMISSED", "FORMAL_OBJECTIVE"]


class CommentRecord(BaseModel):
    comment_id: str = Field(pattern=r"^C\d{2,}$")
    severity: Severity
    document_code: str | None = None
    revision: str | None = None
    page_or_item: str | None = None
    original_comment: str = Field(min_length=1)
    compiled_action: str = Field(min_length=1)
    finding_basis: str | None = None
    source_location: str | None = None
    required_documents: list[str] = Field(default_factory=list)


class NewDivergence(BaseModel):
    severity: Severity = "ALTO"
    document_code: str | None = None
    revision: str | None = None
    page_or_item: str | None = None
    original_comment: str = Field(min_length=1)
    compiled_action: str = Field(min_length=1)
    finding_basis: str | None = None
    source_location: str | None = None
    required_documents: list[str] = Field(default_factory=list)


class ClarificationQuestion(BaseModel):
    question_id: str = Field(pattern=r"^Q\d{2,}$")
    topic: str = Field(min_length=1)
    question_text: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    related_documents: list[str] = Field(default_factory=list)


class CommentCompilation(BaseModel):
    project_id: str = Field(min_length=1)
    source_formal_comment_count: int = Field(ge=0)
    comments: list[CommentRecord] = Field(default_factory=list)
    new_divergences: list[NewDivergence] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)


FALLBACK_INSTRUCTIONS = """
Você é um Analista Sênior de Dados e Governança Documental.

REGRAS INVIOLÁVEIS:
1. Preserve 100% dos comentários formais e sua ordem.
2. Nunca marque comentário como atendido. O status começa UNCHECKED/☐.
3. Não funda comentários diferentes.
4. Mantenha novas divergências separadas dos comentários formais.
5. Use somente GRAVE, ALTO ou LEVE.
6. Em compiled_action escreva somente a ação objetiva que precisa ser executada.
7. Preserve documento, revisão, folha, item e tag quando existirem; não invente dados.
8. Antes de criar uma nova divergência, tente resolver qualquer incerteza usando todos os documentos fornecidos.
9. Se ainda faltar informação para concluir, coloque a questão em clarification_questions e NÃO a transforme em erro.
10. Perguntas e dúvidas nunca são conteúdo de planilha. Qualquer clarification_question aberta bloqueará a geração do artefato.
11. Se a divergência entre documentos for objetiva, registre-a como erro mesmo que ainda não se saiba qual valor deve prevalecer; a ação deve ser compatibilizar/corrigir, não perguntar.
12. Referências diferentes acompanhadas de “ou similar técnico” não são erro apenas por serem diferentes, salvo incompatibilidade técnica demonstrada.
13. Documentos de naturezas diferentes não precisam repetir todo o conteúdo uns dos outros.
14. A saída deve ser estruturada e auditável.
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
        "Analise o material abaixo. Preserve todos os comentários formais. "
        "Registre somente divergências confirmadas em new_divergences. "
        "Qualquer incerteza que não possa ser resolvida pelo próprio material deve ir para clarification_questions. "
        "Não escreva perguntas dentro dos comentários ou divergências.\n\n"
        f"MATERIAL:\n{report_text}"
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
    questions = []
    for item in compilation.clarification_questions:
        question = item.model_dump()
        question.update(
            {
                "status": "OPEN",
                "resolution": None,
                "resolution_type": None,
                "resolved_by": None,
                "resolved_at": None,
            }
        )
        questions.append(question)

    return {
        "project_id": compilation.project_id,
        "source_formal_comment_count": compilation.source_formal_comment_count,
        "comments": records,
        "new_divergences": divergences,
        "clarification_questions": questions,
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
