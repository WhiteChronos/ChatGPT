# AUT Panel — controle pelo GitHub

## Estrutura

```text
.github/workflows/aut-panel-quality.yml   Gate LI/BOM/layout/desenho
pipeline/aut_panel_control.py             Motor determinístico base
pipeline/aut_panel_standard.py            Pipeline padrão LI-first
pipeline/AUT_PANEL_PIPELINE.json          Pipeline legível por máquina
li/PN-AUT-01_LI.json                      LI quantitativa PN-AUT-01
li/PN-AUT-02_LI.json                      LI quantitativa PN-AUT-02
datasheet/AUT_PANEL_DATA_SHEET.json       Data Sheet PN-AUT-01
datasheet/PN-AUT-02_DATA_SHEET.json       Data Sheet PN-AUT-02
datacenter/AUT_PANEL_COMPONENT_CATALOG_V2.json
datacenter/AUT_PANEL_PANEL_QUANTITIES.json
datacenter/AUT_PANEL_GOLDEN_RULES.json
schemas/aut_panel_project_v1.schema.json
governance/AUT_PANEL_CONTROL_STANDARD_v1_0.md
tests/test_aut_panel_control.py
```

## Regras de Ouro quantitativas

- `GR-034`: LI quantitativa congelada antes da BOM e do desenho.
- `GR-035`: quantidade e `catalog_id` iguais em LI, BOM, Data Sheet/layout e desenho.
- `GR-036`: alteração da LI invalida os artefatos posteriores.
- `GR-037`: IHM na porta/tampa.
- `GR-038`: componentes nunca são distorcidos para caber.

Sequência obrigatória:

```text
DATACENTER -> DATASHEET -> SELECT -> LI_QUANTITY -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> RELEASE
```

## Execução local padrão

PN-AUT-01:

```bash
python pipeline/aut_panel_standard.py \
  --project datasheet/AUT_PANEL_DATA_SHEET.json \
  --catalog datacenter/AUT_PANEL_COMPONENT_CATALOG_V2.json \
  --pipeline pipeline/AUT_PANEL_PIPELINE.json \
  --schema schemas/aut_panel_project_v1.schema.json \
  --li li/PN-AUT-01_LI.json \
  --quantity-standard datacenter/AUT_PANEL_PANEL_QUANTITIES.json \
  --output-dir build/aut-panel/PN-AUT-01 \
  --allow-hold
```

PN-AUT-02:

```bash
python pipeline/aut_panel_standard.py \
  --project datasheet/PN-AUT-02_DATA_SHEET.json \
  --catalog datacenter/AUT_PANEL_COMPONENT_CATALOG_V2.json \
  --pipeline pipeline/AUT_PANEL_PIPELINE.json \
  --schema schemas/aut_panel_project_v1.schema.json \
  --li li/PN-AUT-02_LI.json \
  --quantity-standard datacenter/AUT_PANEL_PANEL_QUANTITIES.json \
  --output-dir build/aut-panel/PN-AUT-02 \
  --allow-hold
```

## Artefatos e ordem auditável

`AUT_PANEL_LI.json` -> `AUT_PANEL_BOM.json`/`.csv` -> `AUT_PANEL_LAYOUT.svg`, além de Data Sheet consolidado, Data Center SQLite, QA e manifesto SHA-256.

A proteção de branch deve exigir pull request e o status check `AUT Panel Quality` antes do merge.
