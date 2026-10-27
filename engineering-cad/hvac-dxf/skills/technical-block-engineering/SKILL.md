---
name: technical-block-engineering
description: Research, identify, create, validate, and continuously improve hyper-realistic technical CAD blocks from real equipment evidence. Use when ChatGPT must find an exact manufacturer/model, official catalog/datasheet/dimensional drawing/CAD/BIM, manufacturer-direct or manufacturer-verified authorized suppliers, and deliver the real physical object DXF with all available orthographic views plus isometric view and its separate real project symbol. Also use when supplier authority must be verified by brand, a block is too simplified, geometry fidelity must match manufacturer/reference DXFs, or the CAD workflow needs controlled improvement.
---

# Technical Block Engineering

## Purpose
Build technical blocks from evidence, not approximation. Every deliverable must clearly distinguish:
1. **physical object block** — the real manufacturer object; and
2. **project symbol block** — the schematic/instrumentation symbol.

Default to delivering both when applicable.

## Core rule
Never invent geometry, dimensions, mounting points, ports, service clearances, supplier identity, supplier authorization, or project graphical conventions. Never use a marketplace, reseller, or self-declared distributor as final technical authority unless the manufacturer itself verifies that relationship.

Use this evidence chain:
**project requirement -> object identity -> manufacturer -> exact model/part number -> catalog -> datasheet PDF -> dimensional drawing -> native CAD/BIM -> hyper-realistic DXF -> QA -> memory/improvement**

## Mandatory references
Before creating a final object block, read:
- `references/source-policy.md`
- `references/object-schema.md`
- `references/hyperrealistic-dxf-standard.md`
- `references/cad-toolchain.md`
- `references/qa-policy.md`
- `references/dxf-filename-standard.md`
- `references/preferred-sources-and-suppliers.md`
- `assets/brand-authority-registry.yaml`

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
3. Lock the brand authority chain: official manufacturer domain first; distributor/partner only after validation in the manufacturer's own locator/page.
4. Search official product page, catalog, datasheet, manual, dimensional drawing, CAD/BIM portal.
5. Confirm identity with at least two independent technical discriminators.
6. Record supplier authority evidence in the manifest. If authorization is unverified, use manufacturer-direct sources only and set the supplier source to blocked for final geometry.
7. If the input is a photo, use it only to generate candidates; never close exact identity from appearance alone.

## Physical block workflow
1. Prefer native manufacturer DXF/DWG/STEP/IGES/RFA/IFC.
2. Preserve native geometry and curve types.
3. If STEP/IGES/BREP exists, use FreeCAD/TechDraw or OpenCascade/pythonocc to derive orthographic views and ISO.
4. If only dimensional PDF/drawing exists, reconstruct parametrically with CadQuery/FreeCAD/pythonocc.
5. Preserve housing shape, covers, vents, display, fasteners, probes, floats, brackets, process connections, cable entries, connectors, mounting details and other visible engineering features when documented.
6. Normalize to Model Space 1:1, meters, Arial without altering geometry.
7. Name every final DXF using `references/dxf-filename-standard.md`: instrument/equipment type + manufacturer + exact model + artifact/view + revision. A model-only or generic filename is not acceptable.

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


## 3D / isometric specialization
For STEP/BREP-based view generation and isometric DXF creation, route through the dedicated `isometric-dxf-engineering` workflow. It must derive FRONT/LEFT/RIGHT/TOP/BOTTOM/ISO from one geometry master, use hidden-line projection, create separate view DXFs plus a non-overlapping MULTIVIEW DXF, and reject pseudo-isometric cubes or overlapping layouts.


## ISO presentation rule
The final package must present the isometric view as a solid external-object representation, not as a radiographic/x-ray view.
- Default ISO: visible edges only.
- Hidden ISO edges: optional and secondary.
- MULTIVIEW must use the clean ISO.
- If the ISO looks transparent because hidden edges are visible, the package fails QA.


## True isometric solid-visibility rule
For final manufacturer-style ISO blocks, require face-based occlusion, not edge filtering alone. The nearest enclosure/cover surface must hide internal/back geometry. Preserve original assembly/compound topology; do not fuse components just to clean linework unless the fused topology is validated against the source.


## Brand-locked supplier authority
Every technical source and commercial supplier must be validated against the real manufacturer brand.

Before using a distributor/partner as evidence, read:
- `references/source-policy.md`
- `references/preferred-sources-and-suppliers.md`
- `assets/brand-authority-registry.yaml`

Rules:
- manufacturer official sources are primary;
- a distributor/partner is accepted only when authorization is verifiable from the manufacturer's own official locator/page;
- reseller/marketplace/self-declared distributor sources are lead-only;
- if authorization is not verifiable, use manufacturer-direct technical sources only and mark the supplier source blocked for final geometry;
- for new brands, add the official manufacturer domain and authorized-channel evidence to the brand registry before relying on that channel.

## Descriptive DXF filename rule
Every published DXF filename must identify the instrument/equipment without opening the file.

Canonical pattern:
`TIPO_INSTRUMENTO_FABRICANTE_MODELO_ARTEFATO_REVISAO.dxf`

Requirements:
- ASCII uppercase, digits and underscores only;
- no spaces or accents;
- include instrument/equipment type, real manufacturer, exact model, artifact/view and revision;
- symbol files must use `SIMBOLOGIA_<CODIGO>`;
- multiview files must use `CONJUNTO_MULTIVISTAS`;
- packages must include `INDICE_DXF_NOMES_DESCRITIVOS.csv` and `INDICE_DXF_NOMES_DESCRITIVOS.txt`;
- run `scripts/validate_dxf_filename.py` before publication.
