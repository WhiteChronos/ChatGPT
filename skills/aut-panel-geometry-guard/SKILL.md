---
name: aut-panel-geometry-guard
description: Enforce dimensionally faithful 3D/CAD geometry, scale, proportions, orthographic views, and grow-only composition for industrial automation-panel images. Use whenever ChatGPT creates, edits, reviews, renders, lays out, or improves a panel image, CAD/BIM model, Blender/Revit/IFC workflow, dimensional poster, front/side/depth view, or any output where components must preserve official manufacturer dimensions and LI/BOM quantities without squeeze, stretch, per-view scaling, or fit-to-canvas distortion.
---

# AUT Panel Geometry Guard

Treat geometry as engineering data. Never use a generative image as the authority for size, shape, quantity, placement, or 3D proportions.

## Mandatory invariant

**Grow the canvas; never shrink the geometry.**

For every physical component and every view:

- Work in millimetres.
- Use one physical 3D instance per LI/BOM instance.
- Prefer manufacturer STEP/IGES; then native CAD/DXF; then deterministic reconstruction from official dimensional drawings.
- Validate model bounding boxes against official width × height × depth before rendering.
- Generate front, side, depth-section, and open-door views from the same 3D assembly and coordinates.
- Use orthographic cameras for dimensional views.
- Forbid independent per-view scaling, stretch, squeeze, perspective compensation, or fit-to-canvas resizing.
- Increase output canvas/page size whenever content does not fit at the required scale.
- Keep the HMI as one door-mounted physical instance. A backside view is the same instance, not a second device.
- Keep cable-exit, gland-access, bend-radius, ducts, rails, and service clearances dimensionally explicit.
- Treat missing manufacturer geometry/dimensions as `HOLD_DIMENSIONAL_DATA`.
- Treat a geometric mismatch, squeeze, duplicate component, or independent scale as `REPROVADO`.

## Workflow

1. Load LI/BOM and exact component identities.
2. Load official dimensional/CAD evidence for every drawable item.
3. Normalize all geometry to millimetres.
4. Build/import one 3D physical assembly.
5. Validate every component bounding box with the repository geometry gate.
6. Freeze coordinates, orientation, mounting surface, and clearances.
7. Generate orthographic engineering views from the frozen assembly.
8. Render realistic materials/lights in Blender without editing geometry.
9. Use Revit only through authorized BIM/CAD interchange. Preserve units, coordinates, IDs, and bounding boxes.
10. Compose the poster on a grow-only canvas. Never resize a physical block to make it fit.
11. Run scale/proportion QA before release.

## Blender

Use Blender as a renderer, not a geometric authority. Import frozen STEP/IFC/mesh geometry or a validated conversion. Lock object scale at 1,1,1 after verified import; do not non-uniformly scale objects. Use orthographic cameras for measured views. Materials, lighting, background, anti-aliasing, and camera framing may change; physical geometry and coordinates may not.

## Revit/BIM

Revit is proprietary and requires an authorized Autodesk environment. When available, use pyRevit/RevitPythonShell/IFC export workflows only as an interoperability layer. Do not claim Revit validation unless an actual Revit/IFC export was executed and checked. Prefer IFC for open interchange and verify the exported bounding boxes against the official component dimensions.

## Agent guard sequence

Require these guards before a render is accepted:

1. `CAD_GEOMETRY_GUARDIAN`
2. `REVIT_BIM_INTEROP_GUARDIAN` when applicable
3. `SCALE_PROPORTION_GUARDIAN`
4. `BLENDER_RENDER_GUARDIAN`
5. `CANVAS_COMPOSITION_GUARDIAN`
6. `QA`

Any guardian can stop the pipeline. Never bypass a geometric failure to obtain a prettier image.

## Visual-standard constraints

Follow `datacenter/AUT_PANEL_VISUAL_STANDARD_V3.yaml`.

- Use a large canvas and enlarge it as necessary.
- Dedicated visual items 4 and 8 are removed.
- Preserve their engineering information inside the main open-door/depth-section views.
- Maintain: `LI = BOM = CARGA = LAYOUT = GEOMETRIA 3D = IMAGEM`.

## References

Read `references/geometry-contract.md` for the exact geometry-source hierarchy, Blender/Revit responsibilities, and failure matrix.
