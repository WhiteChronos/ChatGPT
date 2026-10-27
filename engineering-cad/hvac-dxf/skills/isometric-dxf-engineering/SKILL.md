---
name: isometric-dxf-engineering
description: Generate and validate accurate orthographic and isometric DXF views from real 3D CAD geometry. Use for STEP/BREP/CAD-based equipment blocks, hyper-realistic isometric views, hidden-line projections, non-overlapping multi-view layouts, DXF export, CAD toolchain selection, or when an isometric DXF is simplified, overlapping, inconsistent, or visually unlike the manufacturer model.
---

# Isometric DXF Engineering

## Goal
Generate engineering-grade DXF views from one authoritative 3D geometry master.

## Required rule
Never fabricate an isometric view as a generic cube/prism. Prefer native manufacturer STEP/BREP/CAD. If 3D is unavailable, return to the technical-block workflow and reconstruct the geometry master from official dimensional evidence before generating ISO.

## Toolchain
Read `references/toolchain.md` before selecting a backend.

Preferred execution order:
1. FreeCAD/TechDraw when FreeCAD is available.
2. CadQuery + OpenCascade HLR + ezdxf when available.
3. pythonocc/OpenCascade for custom BREP projection pipelines.
4. MeasureIt_ARCH/Blender only as a secondary documentation/presentation path.

## STEP -> DXF workflow
1. Verify the STEP belongs to the exact manufacturer/model/variant.
2. Run `scripts/check_toolchain.py`.
3. Run `scripts/step_to_multiview_dxf.py <model.step> --outdir <folder> --name <model>`.
4. The default/final ISO must use visible edges only.
5. Use `--iso-hidden` only to generate a secondary technical ISO with hidden edges.
6. Inspect `*_LAYOUT_QA.json`.
5. Reject if any layout collision exists or audit errors are nonzero.
6. Visually compare the ISO and orthographic views with the source CAD/manufacturer drawing.
7. Deliver individual view DXFs plus `*_MULTIVIEW.dxf`.

## View standard
Read `references/view-standard.md`.

## QA gates
- same geometry master for all views;
- no view overlap;
- ISO in a dedicated zone;
- hidden-line removal used for 3D projections;
- orthographic/ISO consistency;
- Model Space 1:1;
- meters;
- Arial text style;
- no unresolved DXF audit errors;
- no generic-box degradation relative to the source CAD.

## Continuous improvement
When a projection fails or loses geometry, record the model, source format, backend, failure class, expected result, actual result, and smallest reusable fix. Regression-test the fix on the failing model and at least one known-good reference model.


## ISO visibility policy
- Final/default ISO must be visible edges only.
- Hidden edges in the ISO are optional and must be exported only as a secondary technical variant or on a separate hidden layer that is turned off by default.
- The combined MULTIVIEW drawing must use the clean ISO, not the x-ray ISO.
- If a view appears as a transparent/radiographic object, the QA must reject it.


## True solid isometric gate
Before approving ISO_CLEAN, read `references/true-isometric-3d-standard.md` and `references/occlusion-backends.md`.

The final ISO must be an orthographic projection of the real 3D solid with face-based occlusion. A front/external face must hide geometry behind it. Do not approve a line-only result that removes the front cover or exposes internal parts.

Never boolean-fuse an assembly merely to reduce line clutter. Preserve the original compound/assembly and let the visibility engine perform occlusion unless a fuse is technically required and independently validated.

Generate a solid/depth reference with `scripts/render_iso_surface_reference.py` when using an edge-based backend and compare the DXF ISO against that reference before publication.


## Continuous-edge ISO rule
For the default ISO_CLEAN, preserve complete projected CAD edges/curves. Do not clip the isometric into many short independently visible segments.

Preferred OpenCascade HLR composition for ISO_CLEAN:
- `OutLineVCompound` for external contour;
- `VCompound` for visible hard edges/details;
- exclude `Rg1LineVCompound` by default unless a specific model requires it for external form recognition.

Reject ISO_CLEAN if curves are visibly fragmented, contours do not close, or the object looks exploded/disconnected.


## AutoCAD canonical isometric orientation
Before generating or approving an ISO view, read `references/autocad-isometric-standard.md`.

Default project convention:
- +X projects at 30 degrees;
- +Z projects vertically at 90 degrees;
- +Y projects at 150 degrees;
- the projector frame must include a fixed in-plane X direction so the CAD kernel cannot choose arbitrary roll;
- default output is an AutoCAD-style true-length isometric drawing; use the single uniform factor sqrt(3/2) after mathematical orthographic isometric projection;
- circles on isometric planes remain projected ellipses/isocircles.

Reject the ISO when the measured projected axes do not pass the 30/90/150 gate.
