# Power BI — Modelo de Controle de Comentários

## Fonte de verdade

Preferir conexão direta ao PostgreSQL usando as views:

- `vw_comment_control_powerbi`
- `vw_comment_integrity`

CSV produzido por `pipeline/comment_control_export_powerbi.py` é somente alternativa de intercâmbio.

## Modelo recomendado

### Fato

`FactComments`

Campos principais:

- project_id
- comment_id
- origin_type
- severity
- document_code
- revision
- page_or_item
- compiled_action
- status_control
- responsible
- verifier
- created_at
- verified_at
- reopened_count
- age_days
- risk_score

### Dimensões

- `DimProject`
- `DimDocument`
- `DimSeverity`
- `DimStatus`
- `DimResponsible`
- `DimDate`

## Medidas DAX sugeridas

```DAX
Comentarios Formais =
CALCULATE(
    COUNTROWS(FactComments),
    FactComments[origin_type] = "FORMAL_COMMENT"
)

Pendentes =
CALCULATE(
    [Comentarios Formais],
    FactComments[status_control] = "UNCHECKED"
)

Atendidos Confirmados =
CALCULATE(
    [Comentarios Formais],
    FactComments[status_control] = "CHECKED"
)

Taxa de Fechamento =
DIVIDE([Atendidos Confirmados], [Comentarios Formais], 0)

Aging Medio =
AVERAGE(FactComments[age_days])

Risco Medio =
AVERAGE(FactComments[risk_score])

Comentarios Graves Pendentes =
CALCULATE(
    [Comentarios Formais],
    FactComments[severity] = "GRAVE",
    FactComments[status_control] = "UNCHECKED"
)
```

## Visuais mínimos

1. cartões: formais, pendentes, confirmados, taxa de fechamento;
2. barras: pendências por grau e documento;
3. matriz: projeto × documento × status;
4. aging: histograma/faixas de dias;
5. risco: ranking de comentários por `risk_score`;
6. evidência: comentários `CHECKED` versus cobertura documental;
7. recorrência: reaberturas por documento, tipo e projeto.

## Regras de qualidade

- `CHECKED` sem evidência deve resultar sempre em zero registros no dashboard de produção.
- novas divergências não entram na medida `Comentarios Formais`.
- o dashboard não altera status; apenas lê a fonte de verdade.
- Power BI nunca deve substituir a trilha de auditoria do banco.
