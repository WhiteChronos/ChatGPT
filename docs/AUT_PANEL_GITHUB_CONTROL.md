# AUT Panel — controle pelo GitHub

## Estrutura

```text
.github/workflows/aut-panel-quality.yml   Gate de pull request
pipeline/aut_panel_control.py             Motor determinístico base
pipeline/aut_panel_standard.py            Pipeline padrão com GR-034
pipeline/AUT_PANEL_PIPELINE.json          Pipeline legível por máquina
datasheet/AUT_PANEL_DATA_SHEET.json       Modelo canônico PN-AUT-01
datasheet/PN-AUT-02_DATA_SHEET.json       Modelo canônico PN-AUT-02
datacenter/AUT_PANEL_COMPONENT_CATALOG.json
datacenter/AUT_PANEL_GOLDEN_RULES.json    Registro das Regras de Ouro
schemas/aut_panel_project_v1.schema.json  Contrato do Data Sheet
governance/AUT_PANEL_CONTROL_STANDARD_v1_0.md
tests/test_aut_panel_control.py           Regressões
```

## Regra de Ouro GR-034

A Lista de Material é elaborada antes da imagem do quadro.

Sequência obrigatória:

```text
DATACENTER -> DATASHEET -> SELECT -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> RELEASE
```

A imagem somente pode usar instâncias e `catalog_id` presentes na BOM vigente. Alteração da BOM invalida a imagem anterior e exige nova renderização e novo QA.

## Execução local padrão

PN-AUT-01:

```bash
python pipeline/aut_panel_standard.py \
  --project datasheet/AUT_PANEL_DATA_SHEET.json \
  --catalog datacenter/AUT_PANEL_COMPONENT_CATALOG.json \
  --pipeline pipeline/AUT_PANEL_PIPELINE.json \
  --schema schemas/aut_panel_project_v1.schema.json \
  --output-dir build/aut-panel/PN-AUT-01 \
  --allow-hold
```

PN-AUT-02:

```bash
python pipeline/aut_panel_standard.py \
  --project datasheet/PN-AUT-02_DATA_SHEET.json \
  --catalog datacenter/AUT_PANEL_COMPONENT_CATALOG.json \
  --pipeline pipeline/AUT_PANEL_PIPELINE.json \
  --schema schemas/aut_panel_project_v1.schema.json \
  --output-dir build/aut-panel/PN-AUT-02 \
  --allow-hold
```

## Artefatos e ordem

- `AUT_PANEL_DATASHEET.json` — Data Sheet consolidado;
- `AUT_PANEL_DATACENTER.sqlite3` — Data Center consultável;
- `AUT_PANEL_BOM.json` — BOM canônica, criada antes da imagem;
- `AUT_PANEL_BOM.csv` — exportação tabular da BOM;
- `AUT_PANEL_LAYOUT.svg` — imagem/layout gerado somente após validar a BOM;
- `qa_report.json` e `qa_report.md` — resultado por regra;
- `manifest.json` — hashes SHA-256 e ordem auditável dos artefatos.

## Proteção de branch

No GitHub, exigir em `main`:

- pull request obrigatório;
- pelo menos uma aprovação;
- status check **AUT Panel Quality / Immutable geometry, power chain, BOM-before-image**;
- branch atualizada antes do merge.

A proteção de branch é configuração administrativa; o workflow e os testes ficam versionados no repositório.
