# DXF Descriptive Filename Standard

## Objective
Every final DXF filename must identify the instrument/equipment without opening the file.

## Canonical pattern

`TIPO_INSTRUMENTO_FABRICANTE_MODELO_ARTEFATO_REVISAO.dxf`

Use ASCII uppercase only, digits, and underscores. Do not use spaces, accents, slashes, parentheses, or punctuation other than the final `.dxf`.

## Required semantic fields
1. `TIPO_INSTRUMENTO` — descriptive equipment/instrument class, not only the tag.
2. `FABRICANTE` — real manufacturer/brand.
3. `MODELO` — exact model/part family used by the block.
4. `ARTEFATO` — view, multiview set, section, or symbol.
5. `REVISAO` — revision token, normally `R01`, `R02`, ... `R10`.

## Canonical artifact tokens
- `VISTA_FRONTAL`
- `VISTA_LATERAL_ESQUERDA`
- `VISTA_LATERAL_DIREITA`
- `VISTA_SUPERIOR`
- `VISTA_INFERIOR`
- `VISTA_ISOMETRICA`
- `CONJUNTO_MULTIVISTAS`
- `SECAO_<IDENTIFICADOR>`
- `SIMBOLOGIA_<CODIGO>`

## Examples
- `CHAVE_NIVEL_LATERAL_EICOS_LA32N2_40_VISTA_ISOMETRICA_R10.dxf`
- `CHAVE_NIVEL_LATERAL_EICOS_LA32N2_40_SIMBOLOGIA_LSH_R10.dxf`
- `TRANSMISSOR_PRESSAO_EMERSON_ROSEMOUNT_3051T_VISTA_FRONTAL_R10.dxf`
- `TRANSMISSOR_TEMPERATURA_UMIDADE_EE_EE300EX_M1_T1_CONJUNTO_MULTIVISTAS_R10.dxf`
- `TRANSMISSOR_TEMPERATURA_UMIDADE_VAISALA_HMT370EX_HMP374_SIMBOLOGIA_TTU_R10.dxf`

## Rules
- The filename must remain descriptive even when copied outside its original folder.
- Do not use a model-only filename such as `3051T_ISO.dxf`.
- Do not use ambiguous names such as `BLOCK1.dxf`, `ISO.dxf`, `FRONT.dxf`, or `FINAL.dxf`.
- Keep manufacturer/model spelling traceable to the technical-object manifest.
- Keep the instrument type semantically aligned with the project function and symbol code.
- A project tag may be appended before the artifact token when needed, but it must not replace instrument/manufacturer/model identification.
- Keep revision in the filename and manifest consistent.

## Package index
Every published package must include:
- `INDICE_DXF_NOMES_DESCRITIVOS.csv`
- a human-readable `INDICE_DXF_NOMES_DESCRITIVOS.txt`

The index must map filename -> instrument -> manufacturer/model -> function/symbol -> artifact/view -> revision.
