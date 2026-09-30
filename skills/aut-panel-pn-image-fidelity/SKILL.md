---
name: aut-panel-pn-image-fidelity
description: Build and validate the Step 5 physical image set for each industrial automation panel PN from one canonical real-scale 3D assembly. Use after the LI/load workbook is frozen and before composing the final engineering document. Enforce identical enclosure and door geometry across every view, rigid hinge transforms, real H/W/D dimensions, one physical instance per component, consistent camera/scale rules, realistic materials, and deterministic multiview QA. Never use image generation as dimensional authority.
---

# AUT Panel Step 5 — PN Image Fidelity

Execute only after `STEP4_LI_LOAD_FROZEN`.

The Step 5 output is the clean physical image set for one PANEL_ID at a time. Do not add legends, electrical architecture, communication architecture, command diagrams, or engineering data blocks here; those belong to Step 6.

## Canonical geometry
1. Load frozen LI/load, current Data Sheet, component dimensions, mounting clearances, cable routes, enclosure requirements and MODEL 001 visual rules.
2. Build one canonical assembly in millimetres. Prefer manufacturer STEP/IGES/DXF. If unavailable, reconstruct deterministically from official dimensional drawings with FreeCAD/CadQuery/build123d/OpenCascade.
3. Assign immutable object IDs and bounding boxes to enclosure, door, mounting plate, DIN rails, ducts, devices and accessories.
4. Use the same assembly hash for every rendered angle.
5. Never rebuild the door or enclosure independently for another view.

Read `references/multiview-contract.md` before rendering.

## Door/tampa invariance
The door is one rigid object.
- Width, height, thickness, cutouts, HMI position, hinges and accessories are invariant across all views.
- Open/closed states may only change by rigid-body rotation around the declared hinge axis.
- Per-view scaling, stretching, mirroring or manual redrawing of the door is forbidden.
- A 3/4 view changes the camera or door hinge angle; it never changes physical dimensions.

Use `scripts/validate_multiview_manifest.py` before accepting the image set.

## Camera rules
- Dimensional front/side/open-door views use orthographic or calibrated engineering projection.
- A realistic 3/4/isometric render may use orthographic/isometric or controlled perspective, but carries no inferred dimensions.
- Camera changes must not alter scene object scale.
- Record camera transform, projection type, focal/ortho scale and output size in the render manifest.

## Fidelity and realism
Use physical materials, lighting and shadows only after geometry is locked.
- Blender is the preferred renderer for realistic output from frozen geometry.
- Adobe/ImageGen/to3D or other generative tools may assist presentation only; they cannot alter or validate geometry.
- Preserve real component count and mounting surfaces.
- Do not create decorative parts that do not exist in the LI.
- Use manufacturer assembly references and Step 3 evidence to reproduce realistic mounting and cable-management practice.

## Mathematical/visual QA
Use Wolfram for dimension/area/volume/transform checks; trimesh/Open3D for geometry QA; OpenCV for visual regression; ImageHash only as a supplementary fingerprint; FreeCAD/CadQuery/build123d for deterministic geometry; Blender for rendering without geometry changes.

Visual similarity never overrides geometric checks.

## Canvas/image sizing
Do not resize the engineering assembly to fit a predefined image. Keep declared model scale, increase image/canvas dimensions as needed, and forbid non-uniform/per-view dimensional scaling.

## Required outputs
For each PANEL_ID produce:
- CANONICAL_3D_ASSEMBLY_MANIFEST;
- MULTIVIEW_RENDER_MANIFEST;
- clean front closed view;
- clean internal/open-door view;
- clean lateral/3-4 view;
- optional depth/section view when required;
- STEP5_MULTIVIEW_QA_REPORT;
- STEP5_PN_IMAGE_FIDELITY_FROZEN.

Each PN has its own files and geometry state.

## Release gates
Reject when assembly hash, enclosure/door bounding boxes, H/W/D, hinge axis, component quantities, or object scale differ between views, or when raster/generative edits alter geometry.

Pass only as `STEP5_PN_IMAGE_FIDELITY_FROZEN`.
