# AUT Panel — controle pelo GitHub

## Estrutura

```text
.github/workflows/aut-panel-quality.yml   Gate de pull request
pipeline/aut_panel_control.py             Motor determinístico
pipeline/AUT_PANEL_PIPELINE.json          Pipeline legível por máquina
datasheet/AUT_PANEL_DATA_SHEET.json       Modelo canônico do painel
datacenter/AUT_PANEL_COMPONENT_CATALOG.json
schemas/aut_panel_project_v1.schema.json  Contrato do Data Sheet
governance/AUT_PANEL_CONTROL_STANDARD_v1_0.md
tests/test_aut_panel_control.py           Regressões
```

## Execução local

```bash
python pipeline/aut_panel_control.py pipeline \
  --project datasheet/AUT_PANEL_DATA_SHEET.json \
  --catalog datacenter/AUT_PANEL_COMPONENT_CATALOG.json \
  --pipeline pipeline/AUT_PANEL_PIPELINE.json \
  --schema schemas/aut_panel_project_v1.schema.json \
  --output-dir build/aut-panel \
  --allow-hold
```

## Artefatos

- `AUT_PANEL_DATASHEET.json` — Data Sheet consolidado com evidências e proveniência GitHub;
- `AUT_PANEL_DATACENTER.sqlite3` — Data Center consultável;
- `AUT_PANEL_LAYOUT.svg` — desenho proporcional sem distorção;
- `qa_report.json` e `qa_report.md` — resultado por regra;
- `manifest.json` — hashes SHA-256.

## Proteção de branch

No GitHub, exigir em `main`:

- pull request obrigatório;
- pelo menos uma aprovação;
- status check **AUT Panel Quality / Immutable geometry and engineering gates**;
- branch atualizada antes do merge.

A proteção de branch é configuração administrativa; o workflow e os testes ficam versionados no repositório.
