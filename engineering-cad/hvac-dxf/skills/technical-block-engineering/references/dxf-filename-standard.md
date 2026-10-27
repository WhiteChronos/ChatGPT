# DXF Compact Filename Standard

## Objective
Keep DXF filenames short enough for Windows/AutoCAD paths while still identifying the instrument.

## Canonical pattern

`TIPO_FAB_MODELO_ARTEFATO_REV.dxf`

Recommended basename length: **<= 64 characters including .dxf**. Do not exceed 80 characters.

Use ASCII uppercase letters, digits and underscores only.

## Required fields
1. `TIPO` — short readable instrument/equipment class.
2. `FAB` — short manufacturer/brand token.
3. `MODELO` — exact model or compact exact model token.
4. `ARTEFATO` — short view/symbol token.
5. `REV` — revision token such as `R10`.

## Standard type tokens
- `NIVEL` — level switch/instrument
- `PRESS` — pressure transmitter/instrument
- `TEMPUMID` — temperature + humidity transmitter
- add another short readable token only when needed.

## Standard artifact tokens
- `FRT` — front
- `ESQ` — left
- `DIR` — right
- `SUP` — top
- `INF` — bottom
- `ISO` — isometric
- `MV` — multiview
- `SEC_<ID>` — section
- `SYM_<CODIGO>` — project symbol

## Examples
- `NIVEL_EICOS_LA32N2_40_ISO_R10.dxf`
- `NIVEL_EICOS_LA32N2_40_SYM_LSH_R10.dxf`
- `PRESS_ROSEMOUNT_3051T_FRT_R10.dxf`
- `PRESS_ROSEMOUNT_3051T_SYM_PIT_R10.dxf`
- `TEMPUMID_EE_EE300EX_M1T1_MV_R10.dxf`
- `TEMPUMID_VAISALA_HMT370EX_HMP374_ISO_R10.dxf`
- `TEMPUMID_VAISALA_HMT370EX_HMP374_SYM_TTU_R10.dxf`

## Rules
- Keep the full human-readable description in the package index and manifest, not in the filename.
- Do not repeat words such as `TRANSMISSOR`, `INSTRUMENTO`, `VISTA`, `FABRICANTE` in the filename.
- Do not use generic names such as `ISO.dxf`, `FRONT.dxf`, `BLOCK1.dxf`, or `FINAL.dxf`.
- The filename must remain traceable to the manifest.
- A project tag may be added only if the resulting basename remains <=64 characters; otherwise keep the tag in the index/manifest.
- Prefer short package/subfolder names as well to reduce the total Windows path length.

## Package index
Every package must include:
- `INDICE_DXF.csv`
- `INDICE_DXF.txt`

The index carries the complete description:
filename -> full instrument description -> manufacturer/model -> function/symbol -> artifact/view -> revision.
