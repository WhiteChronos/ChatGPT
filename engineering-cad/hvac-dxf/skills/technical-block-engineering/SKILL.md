---
name: technical-block-engineering
description: Research, identify, create, validate, and continuously improve hyper-realistic technical CAD blocks from real equipment evidence. Use when ChatGPT must find an exact manufacturer/model, official catalog/datasheet/dimensional drawing/CAD/BIM, suppliers, and deliver the real physical object DXF with all available orthographic views plus isometric view and its separate real project symbol. Also use when a block is too simplified, geometry fidelity must match manufacturer/reference DXFs, or the CAD workflow needs controlled improvement.
---

# Technical Block Engineering

## Purpose
Build technical blocks from evidence, not approximation. Every deliverable must clearly distinguish:
1. **physical object block** — the real manufacturer object; and
2. **project symbol block** — the schematic/instrumentation symbol.

Default to delivering both when applicable.

## Core rule
Never invent geometry, dimensions, mounting points, ports, service clearances, supplier identity, or project graphical conventions.

Use this evidence chain:
**project requirement -> object identity -> manufacturer -> exact model/part number -> catalog -> datasheet PDF -> dimensional drawing -> native CAD/BIM -> hyper-realistic DXF -> QA -> memory/improvement**

## Mandatory references
Before creating a final object block, read:
- `references/source-policy.md`
- `references/object-schema.md`
- `references/hyperrealistic-dxf-standard.md`
- `references/cad-toolchain.md`
- `references/qa-policy.md`

For project symbols also read `references/instrumentation-dwg-style.md`.

## Reference fidelity standard
The user-supplied DXFs `3D135205A0.dxf`, `3D135206A0.dxf`, and `FXAQ20~63AVM.dxf` are benchmark references for geometry richness and manufacturer-style drafting. Their entity density is diagnostic, not a blind threshold.

Reject final physical blocks that reduce a detailed manufacturer object to a rectangle, generic prism/cube, or low-detail silhouette.

## Required output modes
### Physical object
Deliver all views supported by evidence:
- FRONT
- LEFT
- RIGHT
- TOP
- BOTTOM when available
- SECTION when available
- ISO

### Project symbol
Deliver separately:
- real function symbol (e.g. LSH, LSL, PIT, TTU)
- project layer/style mapping
- source DWG/standard
- link to the physical object manifest

## Discovery workflow
1. Identify family/function/tag.
2. Resolve manufacturer, series, exact model, part number, variant/revision.
3. Search official product page, catalog, datasheet, manual, dimensional drawing, CAD/BIM portal.
4. Confirm identity with at least two independent technical discriminators.
5. Find suppliers separately from manufacturer identity.
6. If the input is a photo, use it only to generate candidates; never close exact identity from appearance alone.

## Physical block workflow
1. Prefer native manufacturer DXF/DWG/STEP/IGES/RFA/IFC.
2. Preserve native geometry and curve types.
3. If STEP/IGES/BREP exists, use FreeCAD/TechDraw or OpenCascade/pythonocc to derive orthographic views and ISO.
4. If only dimensional PDF/drawing exists, reconstruct parametrically with CadQuery/FreeCAD/pythonocc.
5. Preserve housing shape, covers, vents, display, fasteners, probes, floats, brackets, process connections, cable entries, connectors, mounting details and other visible engineering features when documented.
6. Normalize to Model Space 1:1, meters, Arial without altering geometry.
7. Create stable block names by manufacturer + model + view.

## Source classes
- `CAD_FABRICANTE`
- `RECONSTRUCAO_FICHA`
- `REFERENCIA_PROJETO`
- `BLOQUEADO`

## Symbol workflow
The symbol never substitutes the physical object.
- Base project DWG/standard controls symbol appearance.
- LSH and LSL must not be graphically identical.
- Keep colors/layers BYLAYER when exact native DWG properties are not verified.
- Preserve project code semantics such as PIT/TTU when explicitly specified.

## QA workflow
A physical block is usable only when:
1. exact identity is confirmed;
2. source/drawing is recorded;
3. units/scale are verified;
4. extents match official dimensions;
5. interfaces are checked;
6. DXF audit has no unresolved structural errors;
7. orthographic views are consistent;
8. ISO is consistent with orthographic views;
9. visual comparison against manufacturer source and reference DXFs passes;
10. provenance/conflicts are documented.

Use complexity metrics (entity count/type mix) only to detect suspicious oversimplification. Do not optimize toward a target count.

## Open-source CAD toolchain
Prefer:
- `mozman/ezdxf`
- `FreeCAD/FreeCAD`
- `CadQuery/cadquery`
- `tpaviot/pythonocc-core`
- `fougue/mayo`
- `LibreDWG/libredwg`
- `codelibs/libdxfrw`
- `LibreCAD/LibreCAD`
- `solvespace/solvespace`

Verify current license before adopting/redistributing. Prefer dependency/fork/submodule over copying source.

## Controlled evolution
Trigger improvement when:
- generated geometry is visibly simpler than manufacturer/reference CAD;
- curves/details are lost;
- ISO and orthographic views disagree;
- source quality improves;
- symbol and physical object are confused;
- user supplies a better benchmark.

For every event: capture evidence -> root cause -> smallest reusable fix -> regression test on failing + known-good cases -> record change -> require human review for geometry/source/units/tolerance policy changes.

## Required output
Deliver:
- hyper-realistic physical DXF package;
- separate symbol DXF when applicable;
- manifest;
- QA report;
- source/provenance list;
- confidence/source class;
- unresolved conflicts;
- evolution record when workflow changed.
