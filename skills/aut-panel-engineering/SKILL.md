---
name: aut-panel-engineering
description: Governed engineering workflow for industrial automation panels, including technical research, source validation, per-panel Data Center/Data Sheet control, LI/BOM, PLC/RTU I/O, load balance, deterministic layout/rendering, QA, database persistence, agent memory, and machine-learning-assisted improvement proposals. Use when creating, reviewing, revising, validating, or evolving automation-panel deliverables that must remain traceable to official sources and approved baselines.
---

# AUT Panel Engineering

Operate as a governed multi-agent engineering system. Preserve approved standards and require explicit authorization before changing locked geometry, templates, quantities, pipeline order, or Golden Rules.

## Canonical workflow

1. Bootstrap rules, panel memory, Data Center, Data Sheet, LI baseline, and approved visual template.
2. Ingest project drawings, manuals, datasheets, I/O lists, LI/BOM, and official manufacturer sources.
3. Validate sources and register reference metadata.
4. Select exact components only when compatibility and lifecycle are supported by evidence.
5. Freeze LI quantities.
6. Calculate 24 Vdc, 127 Vac, and 220 Vac load balance.
7. Generate BOM strictly from frozen LI.
8. Produce layout from BOM and real dimensions.
9. Render one image per panel without distortion.
10. Run structural, semantic, visual, source, and cross-artifact QA.
11. Update memory/database after QA.
12. Release only with no critical HOLD or REPROVADO.

Never derive engineering quantity from a generated image.

## Evidence hierarchy

Use manufacturer site, official manual/datasheet, manufacturer technical portal, official standards, authorized distributor, official representative/integrator, approved internal engineering documents, then secondary sources only as labeled support.

Register document code/revision/date, page or section, official link, consultation date, lifecycle, project application, and validation status.

## Multi-agent model

Use the repository registry `agents/AUT_PANEL_AGENT_SYSTEM.yaml`. Keep each agent inside its declared read/write scope and logical Data Center/memory namespace. Source validation A and B must remain independent.

## Learning loop

Use:

`OBSERVE -> FEATURE_EXTRACT -> TRAIN/EVALUATE -> PROPOSE -> SANDBOX_SIMULATE -> QA -> HUMAN_GATE -> APPLY -> VERSION`

ML is advisory. Deterministic gates always have precedence. Never let ML alter Golden Rules, locked templates, LI baselines, or exact component selections automatically. Use `LEARNING_COLD_START` until enough human-reviewed labels exist.

## Database

Use SQLite as the offline baseline via `database/aut_panel_schema.sql` and `pipeline/aut_panel_db.py`. PostgreSQL/Supabase may be optional deployment targets without changing the logical schema. Keep released history append-only.

## Image quality

Use `datacenter/AUT_PANEL_VISUAL_STANDARD_V3.yaml` as the active composition reference for new panel revisions. Prefer deterministic vector generation and constraint optimization before generative images. Keep real component dimensions, no distortion, and no item outside the validated BOM. The required composition includes internal front, external front, right side, material list, load schedule, electrical architecture, communication architecture, field equipment, enclosure dimensions, technical notes, and the parity footer `LI = BOM = CARGA = LAYOUT = IMAGEM`.

The visual reference is not an engineering-data source: numeric values visible in the reference must be independently validated before use.

### Geometry-first 3D workflow

Read `plugins/AUT_PANEL_3D_GEOMETRY_TOOLCHAIN_V1.json`. Use manufacturer STEP/IGES first, then native CAD/DXF, then deterministic parametric reconstruction from official dimensional drawings. Normalize all geometry to millimetres and create one 3D physical assembly. Generate front, side and depth-section orthographic views from that same assembly. Validate each component bounding box against its official datasheet before rendering.

FreeCAD/OpenCascade/CadQuery/build123d are geometry tools; trimesh/Open3D are geometry-QA tools; Blender is a photorealistic renderer. Blender or a generative image model may change materials, lighting and presentation, but must not change geometry, component count, coordinates, scale or dimensions.

Use a grow-only canvas. Never shrink a physical view, component or engineering block to fit a fixed poster. Visual Standard V3 removes dedicated blocks 4 and 8; their engineering information remains integrated into the main open-door and depth-section views.

### Dimensional closure before render

Do not create a dimensionally authoritative panel render until every drawable BOM item has official manufacturer width, height, depth, mounting method, and required clearance recorded. Use one common millimetre scale for enclosure, mounting plate, DIN devices, ducts, terminals, door devices and cable-exit zones. A missing official dimension is HOLD_DIMENSIONAL_DATA.

The HMI is one physical device mounted on the front door only. Never place a second HMI on the internal mounting plate. In an open-door view, the rear body/connectors of the same door-mounted HMI may be shown only when geometrically visible and must never increment the LI/BOM quantity.

Before render, execute duplicate-instance, door-vs-backplate, cable-exit, gland-access and bend-radius checks. A failed fit is HOLD_LAYOUT_CAPACITY; never solve it by scaling components down.

## GitHub toolchain

Read `references/github-toolchain.md` and `plugins/AUT_PANEL_GITHUB_TOOLCHAIN_V2.json` when selecting repositories, tools or plugins. New tools require version/commit pinning, license review, security review, sandbox validation and regression coverage before promotion to active use.

## Status

Use `VALIDADO`, `REFERENCIA`, `HOLD`, and `REPROVADO`. Software CI success does not clear an engineering HOLD.

## Final QA

Verify source traceability, dual validation when required, LI/BOM/layout/render parity, exact model/lifecycle, load traceability, geometry, database/memory consistency, artifact hashes, ML provenance when used, and absence of unauthorized standard mutation.

Read `references/architecture.md`, `references/quality-contract.md`, `references/database-schema.md`, and `references/github-toolchain.md` when those topics are needed. Use `scripts/validate_bundle.py` for lightweight local manifest checks.


## Permanent geometry guardians

For every panel image, dimensional poster, CAD/BIM export, Blender render, Revit/IFC exchange, or layout revision, enforce the following guardian order before QA:

1. **CAD_GEOMETRY_GUARDIAN** — validates official manufacturer geometry, bounding boxes, millimetre units, component identity, and a single frozen 3D assembly.
2. **REVIT_BIM_INTEROP_GUARDIAN** — when Revit/BIM is involved, validates IFC/CAD exchange, IDs, units, coordinates, and bounding boxes. Revit execution requires an authorized Autodesk environment.
3. **SCALE_PROPORTION_GUARDIAN** — validates one global scale, orthographic dimensional views, real width/height/depth ratios, and prohibits per-view scaling.
4. **BLENDER_RENDER_GUARDIAN** — allows Blender to change materials, lighting, anti-aliasing, and framing only; geometry, coordinates, scale, count, and bounding boxes are locked.
5. **CANVAS_COMPOSITION_GUARDIAN** — uses `GROW_CANVAS_KEEP_SCALE`; the canvas grows until everything fits. Never shrink a component, view, table, or engineering block to fit the poster.
6. **QA** — verifies LI/BOM/layout/3D/render parity and rejects any geometric regression.

Any guardian may stop the pipeline. Never bypass a geometric failure for visual convenience.

### Local deterministic fallback

When Blender/Revit are not available, use CadQuery for parametric solids and trimesh for bounding-box/scene QA. This fallback can validate geometry but does not count as Blender or Revit execution.

### Revit open-source support

Use pyRevit, RevitPythonShell, IFC/IfcOpenShell, or other approved bridges only after version pinning, license/security review, and integration tests. Revit itself remains proprietary and must not be claimed as executed unless an Autodesk environment actually ran the model/export.

### Absolute no-squeeze rule

- Never fit the panel into a fixed poster by rescaling the physical geometry.
- Never change object X/Y/Z scale independently.
- Never use perspective projection for a dimensional view.
- Never reconstruct each view separately.
- Never reduce components, the enclosure, the mounting plate, cable zones, or the depth section to make the page look balanced.
- Increase page/canvas width or height instead.
- All engineering views must derive from the same 3D assembly and use the same unit system in millimetres.
