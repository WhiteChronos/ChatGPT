"""Agente de compilação e verificação de comentários técnicos.

O agente ajuda a interpretar texto; as regras de integridade permanecem determinísticas.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import Any

from agents import Agent, Runner
from pydantic import BaseModel, Field


class CommentRecord(BaseModel):
    comment_id: str = Field(pattern=r"^C\d{2,}$")
    severity: str
    document_code: str | None = None
    revision: str | None = None
    page_or_item: str | None = None
    original_comment: str
    compiled_action: str
    required_documents: list[str] = []


class CommentCompilation(BaseModel):
    project_id: str
    source_formal_comment_count: int = Field(ge=0)
    comments: list[CommentRecord]
    new_divergences: list[dict[str, Any]] = []


SYSTEM_INSTRUCTIONS = """
Você é um Analista Sênior de Dados e Governança Documental com experiência equivalente a décadas de prática em engenharia, qualidade, auditoria e controle de configuração.

Sua função é compilar comentários técnicos sem perder nenhum item.

REGRAS INVIOLÁVEIS:
1. Preserve 100% dos comentários formais e sua ordem.
2. Nunca marque comentário como atendido. O status de controle é externo ao agente e sempre começa UNCHECKED/☐.
3. Não funda comentários diferentes, mesmo quando semelhantes.
4. Mantenha novas divergências separadas dos comentários formais.
5. Use somente GRAVE, ALTO ou LEVE.
6. Em compiled_action escreva somente a ação objetiva que precisa ser executada ou confirmada.
7. Preserve documento, revisão, folha, item e tag quando existirem; não invente dados ausentes.
8. Se o relatório disser que um item está 100% atendido, mantenha o comentário e formule o requisito técnico que deve ser verificado no controle.
9. source_formal_comment_count deve refletir a quantidade explícita de comentários formais da origem.
10. A saída deve ser estruturada e auditável.
""".strip()


def build_agent() -> Agent:
    return Agent(
        name="CommentControlSeniorAnalyst",
        instructions=SYSTEM_INSTRUCTIONS,
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
    """Converte a saída do agente para o formato de persistência.

    Todos os comentários formais recebem UNCHECKED. O agente não controla fechamento.
    """
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
    return {
        "project_id": compilation.project_id,
        "source_formal_comment_count": compilation.source_formal_comment_count,
        "comments": records,
        "new_divergences": compilation.new_divergences,
    }


if __name__ == "__main__":
    import argparse
    import asyncio
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", default="comment_compilation.json")
    args = parser.parse_args()

    text = Path(args.report).read_text(encoding="utf-8")
    compiled = asyncio.run(compile_comments(text, args.project))
    payload = to_storage_payload(compiled)
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
