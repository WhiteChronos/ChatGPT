# LESSON — Status de comentário não pode ser herdado do relatório

Data: 2026-09-09
Categoria: REGRESSION
Status: ACTIVE

## Ocorrência

Durante a elaboração de uma planilha de controle, comentários que apareciam como “100% atendidos” no relatório de auditoria foram marcados automaticamente como `☑`.

## Falha conceitual

O status histórico do relatório foi confundido com o status operacional do controle de execução.

## Regra preventiva

- Todo comentário formal deve ser incorporado ao controle.
- Todo comentário nasce como `UNCHECKED` / `☐`.
- Nunca converter automaticamente “atendido”, “100%”, “encerrado” ou equivalente para `CHECKED` / `☑`.
- `CHECKED` só é válido com confirmação humana e evidência documental suficiente.
- A quantidade formal da origem deve ser igual à quantidade formal registrada.

## Testes de regressão

- `test_checked_without_evidence_blocks`
- `test_count_mismatch_blocks`
- `test_duplicate_comment_blocks`
- `test_checked_multidocument_requires_all_documents`

## Impacto

Evita falso encerramento, perda de rastreabilidade e exclusão de comentários que precisam permanecer no checklist de verificação.

## Artefatos relacionados

- `governance/COMMENT_CONTROL_STANDARD_v1_0.md`
- `datasheet/COMMENT_CONTROL_DATA_SHEET.json`
- `pipeline/comment_control_pipeline.py`
- `tests/test_comment_control.py`
