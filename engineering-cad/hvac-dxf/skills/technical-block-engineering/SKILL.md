---
name: technical-block-engineering
description: Research, identify, reconstruct, validate, and continuously improve technical CAD blocks from real equipment evidence. Use when ChatGPT must find an exact manufacturer/model, suppliers, official catalogs, technical datasheet PDFs, dimensional drawings, CAD/BIM files, or create/normalize/validate DXF blocks from those sources for HVAC, automation, electrical, instrumentation, mechanical, or industrial equipment. Also use when a block is too simplified, a project model is ambiguous, dimensions conflict, provenance must be audited, or the block-generation workflow should learn from verified failures without silently changing rules.
---

# Technical Block Engineering

Build technical blocks from evidence, not visual approximation.

## Evidence chain
project tag / requirement -> object identity -> manufacturer -> exact model / part number -> official catalog -> official datasheet PDF -> dimensional drawing -> native CAD/BIM -> normalized DXF -> QA -> memory / improvement record

Never invent geometry, dimensions, mounting points, ports, service clearances, or supplier identity.

## Modes
1. Discovery: identify exact manufacturer/model, official PDF/catalog/CAD and suppliers.
2. Block: prefer native CAD/BIM; otherwise reconstruct only from official dimensional evidence.
3. QA: verify identity, units, scale, extents, interfaces, DXF audit, visual match and provenance.
4. Controlled evolution: record verified failures, root cause, smallest reusable improvement, regression tests and human review where required.

## Source classes
- CAD_FABRICANTE
- RECONSTRUCAO_FICHA
- REFERENCIA_PROJETO
- BLOQUEADO

## Default DXF standard
- Model Space 1:1
- meters
- ARIAL text style
- preserve original manufacturer geometry and orthographic views
- preserve mounting holes, panels, grilles, fans, louvers, piping/drain/electrical points, bases and flanges

## Controlled evolution
Never self-modify silently. Record failures and improvements. Require human review before changing source authority, geometry acceptance criteria, units, confidence classification, tolerances, or automatic model-matching thresholds.
