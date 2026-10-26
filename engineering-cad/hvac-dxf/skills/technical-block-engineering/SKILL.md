---
name: technical-block-engineering
description: Research, identify, reconstruct, validate, and continuously improve technical CAD blocks from real equipment evidence. Use when ChatGPT must find an exact manufacturer/model, suppliers, official catalogs, technical datasheet PDFs, dimensional drawings, CAD/BIM files, or create/normalize/validate DXF blocks from those sources for HVAC, automation, electrical, instrumentation, mechanical, or industrial equipment. Also use when a block is too simplified, a project model is ambiguous, dimensions conflict, provenance must be audited, or the block-generation workflow should learn from verified failures without silently changing rules.
---

# Technical Block Engineering

## Purpose
Build technical blocks from evidence, not visual approximation. Treat the technical object as a traceable engineering record: manufacturer, exact model/part number, official technical sources, geometry, dimensions, interfaces, provenance, confidence class, and validation history.

## Core rule
Never invent geometry, dimensions, mounting points, ports, service clearances, supplier identity, or project layer colors.

Use this evidence chain:
**project tag / requirement -> object identity -> manufacturer -> exact model / part number -> official catalog -> official datasheet PDF -> dimensional drawing -> native CAD/BIM -> normalized DXF -> QA -> memory / improvement record**

## Workflow decision tree
1. Find object -> Discovery.
2. Create/improve physical block -> Block workflow.
3. Validate existing block -> QA workflow.
4. Learn from verified defect/better source -> Controlled evolution.
5. If a DWG/DXF is supplied as project symbology reference -> Project instrumentation-symbol mode.

## Source classes
- CAD_FABRICANTE
- RECONSTRUCAO_FICHA
- REFERENCIA_PROJETO
- BLOQUEADO

## DXF standard
- Model Space 1:1
- meters
- ARIAL text style
- preserve manufacturer geometry and available views
- preserve mounting, connections, clearances and interfaces supported by evidence
- convert coordinates numerically when changing units

## Project instrumentation-symbol mode
Read `references/instrumentation-dwg-style.md` before generating or revising schematic symbols from a user-supplied base DWG/DXF.
- Base drawing controls project symbol presentation: layer names, colors, linetypes, text style, tag layout and marker placement.
- Manufacturer evidence controls physical equipment geometry only.
- Preserve confirmed layer/block names, Arial and ByLayer behavior.
- If native DWG layer-table extraction is unavailable, never claim exact color indices. Keep entities BYLAYER, centralize provisional mapping in the layer table, and mark it pending.
- Never make LSH and LSL graphically identical when the project distinguishes high/low function. Differentiate by tag and marker/position while preserving project convention.
- Use PIT for pressure indicating transmitter only when project convention supports it.
- Preserve project code TTU when explicitly requested for temperature/humidity transmission; do not reinterpret it as a manufacturer identity.

## QA
Before calling a physical block usable:
1. exact object identity confirmed;
2. source/drawing recorded;
3. units and scale checked;
4. extents checked;
5. interfaces checked when available;
6. DXF audit has no unresolved errors;
7. visual comparison complete;
8. conflicts documented.

For schematic symbols from a base DWG, also verify:
- project layer name;
- ByLayer/ByBlock behavior;
- text style;
- high/low functional distinction;
- source DWG revision;
- color mapping status (confirmed vs provisional).

## Controlled evolution
Never self-modify silently. Record failure, root cause, smallest reusable improvement and regression result. Human review is mandatory before changing source authority, geometry acceptance, units, confidence classes, tolerances, automatic matching thresholds, or project color/layer conventions.

## Files
- `references/source-policy.md`
- `references/object-schema.md`
- `references/qa-policy.md`
- `references/evolution-policy.md`
- `references/open-source-tooling.md`
- `references/instrumentation-dwg-style.md`
- `assets/technical_object_manifest.yaml`
- `assets/evolution_record.yaml`
- `assets/instrumentation_style.json`
- `scripts/validate_manifest.py`
- `scripts/validate_dxf.py`
