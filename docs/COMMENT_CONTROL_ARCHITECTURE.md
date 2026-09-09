# Arquitetura — Sistema Inteligente de Controle de Comentários

## Princípio

O agente interpreta; o pipeline determinístico governa; o banco preserva; o humano confirma.

## Fluxo

```text
Relatório técnico
  -> CommentControlSeniorAnalyst
  -> saída estruturada Pydantic
  -> normalização
  -> JSON Schema
  -> gates determinísticos
  -> comentários formais + novas divergências separadas
  -> PostgreSQL / Datacenter
  -> memória técnica + trilha de eventos
  -> estatística descritiva
  -> RISK_SCORE_BASELINE
  -> Excel governado
  -> dataset Power BI
  -> revisão humana
  -> evidência documental
  -> UNCHECKED -> CHECKED
```

## Componentes

### Data Sheet

`datasheet/COMMENT_CONTROL_DATA_SHEET.json`

Contrato funcional e visual do controle.

### Schema

`schemas/comment_control_v1.schema.json`

Valida os registros, domínios, formatos e requisitos adicionais de fechamento.

### Agente

`pipeline/comment_control_agent.py`

Responsável exclusivamente pela interpretação e compilação objetiva. Não possui autoridade para fechar comentários.

### Pipeline

`pipeline/comment_control_pipeline.py`

Gates:

- quantidade formal;
- unicidade;
- schema;
- criticidade;
- status;
- evidência;
- cobertura multi-documento;
- confirmação humana.

### Runner

`pipeline/comment_control_runner.py`

Orquestra o fluxo completo e gera os artefatos derivados.

### Datacenter / Banco

`datacenter/comment_control_schema.sql`

PostgreSQL com:

- projetos;
- documentos;
- comentários;
- documentos requeridos;
- evidências;
- memória técnica;
- eventos de auditoria;
- scores de modelos;
- views para Power BI e integridade.

### Excel

`pipeline/comment_control_excel.py`

Gera o formato de controle aprovado:

- todos os comentários;
- status inicial ☐;
- quadrado centralizado em 22 pt;
- evidência da verificação;
- borda externa preta grossa;
- bordas internas pretas finas;
- texto quebrado e linhas dimensionadas;
- divergências em aba separada;
- aba VERIFICAÇÃO.

### Analítica

`pipeline/comment_control_analytics.py`

Calcula estatística descritiva e score heurístico auditável. O baseline não é apresentado como modelo treinado.

### Power BI

`pipeline/comment_control_export_powerbi.py`

`docs/COMMENT_CONTROL_POWERBI.md`

O banco é a fonte de verdade. CSV é somente camada de intercâmbio.

### Memória

`memory/`

Erros relevantes devem possuir ocorrência + regra + teste de regressão.

### Qualidade

- `tests/test_comment_control.py`
- `evals/`
- `.github/workflows/comment-control.yml`
- `.gitlab-ci.yml`

## Autoridade

1. documento contratual/normativo aprovado;
2. evidência documental do projeto;
3. regras de governança versionadas;
4. memória técnica;
5. inferência do agente.

Em conflito, a camada de menor autoridade nunca deve sobrescrever a de maior autoridade.
