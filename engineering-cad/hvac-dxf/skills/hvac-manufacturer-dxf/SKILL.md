---
name: hvac-manufacturer-dxf
description: Research HVAC/automation equipment by manufacturer and exact model, find official catalogs/datasheets/CAD/BIM, preserve source provenance, and produce or normalize accurate DXF blocks in meters at 1:1 with Arial text. Use when creating CAD blocks from project equipment lists, vendor datasheets, manufacturer drawings, DXF/DWG/STEP/IFC/BIM sources, or when validating and improving an engineering CAD block library.
---

# HVAC Manufacturer DXF

Never invent equipment geometry.

## Resolution order
1. exact manufacturer + exact model/part number
2. official manufacturer catalog/product page
3. official datasheet/dimensional drawing
4. native CAD/BIM from manufacturer or authorized technical catalog
5. reconstruct only when native CAD is unavailable; label `RECONSTRUCAO_FICHA`

## DXF standard
- Model Space 1:1
- meters
- ARIAL text style
- preserve source geometry and all available orthographic views
- preserve mounting holes, panels, grilles, fans, louvers, piping/drain/electrical points, bases and flanges
- never replace complex geometry with a rectangle

## Confidence
- `CAD_FABRICANTE`
- `RECONSTRUCAO_FICHA`
- `REFERENCIA_PROJETO`

## QA
Run the repository scripts, compare extents with official dimensions, and keep a source manifest. Write reusable corrections to `memory/HVAC_DXF_MEMORY.md`.
