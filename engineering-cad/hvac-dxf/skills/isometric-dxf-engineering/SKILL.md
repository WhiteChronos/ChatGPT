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
