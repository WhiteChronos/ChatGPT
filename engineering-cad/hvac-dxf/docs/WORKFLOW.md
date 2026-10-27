# WORKFLOW — Hyper-realistic Technical Block

## Objective
Create a technical CAD package that depicts the real manufacturer object at the fidelity level demonstrated by the user-supplied reference DXFs, plus the real project symbol as a separate linked artifact.

## Canonical flow
1. Receive object/tag/photo/reference drawing.
2. Decide output: object, symbol, or both. Default to both when applicable.
3. Resolve identity: manufacturer, exact model, part number, revision/variant.
4. Gather technical evidence: catalog, datasheet PDF, dimensional drawing, CAD/BIM/STEP/DWG/DXF, supplier evidence.
5. Prefer native manufacturer geometry.
6. If native 3D exists: import -> clean -> orthographic projection -> ISO -> DXF.
7. If only dimensional evidence exists: reconstruct parametric 3D/2D -> project views -> ISO -> DXF.
8. Create symbol separately from the physical object.
9. Run hyper-realistic fidelity QA against manufacturer source and benchmark DXFs.
10. Publish DXF(s), manifest, QA, source list and confidence class.
11. Record lessons and regressions.

## Gates
### G0 — Input
Object family/function/tag known.

### G1 — Identity
Exact manufacturer/model/variant closed or explicitly BLOCKED.

### G2 — Source
Native CAD/BIM preferred. Reconstruction is allowed only from official technical evidence.

### G3 — Geometry fidelity
Reject generic boxes/prisms when the source exposes richer geometry. Preserve curves, interfaces, housings, probes, displays, mounting and connectors.

### G4 — View package
Include all available orthographic views and ISO. Views must be mutually consistent.

### G5 — Symbol
Use the real project symbol as a separate block, based on the project DWG/standard.

### G6 — QA
0 unresolved DXF structural errors; dimensions/interfaces/provenance verified; visual comparison passed.

### G7 — Publication
Publish only with manifest, sources, QA and confidence class.


### G4B — ISO visibility policy
- The final ISO must be a clean external-object view with visible edges only.
- Do not publish the ISO with hidden edges enabled by default.
- If a technical hidden-line ISO is needed, publish it as a secondary variant.
- MULTIVIEW must use the clean ISO.


### G3D — Preserve topology before projection
- Do not boolean-fuse assemblies/compounds only to remove line clutter.
- Preserve manufacturer component topology unless a fuse is technically required and verified.
- Validate shape before and after any boolean operation.

### G4D — True isometric face occlusion
- Use orthographic isometric projection with perspective disabled.
- Use surface/depth occlusion so the nearest face hides geometry behind it.
- The front cover/enclosure must remain visible when it is visible from the selected quadrant.
- Reject any ISO that looks like a section/x-ray/wireframe when no section was requested.
- Compare the DXF to a solid surface reference from the same geometry master.


### G4E — Curve continuity
- Final ISO_CLEAN must preserve complete continuous projected edges.
- Reject fragmented/pixel-clipped linework, open silhouettes caused by filtering, and exploded-looking geometry.
- Surface/depth-buffer may be used to validate occlusion, but final DXF linework should remain exact CAD curves from the projection kernel whenever possible.


### G4F — Isometric axis geometry
- Validate the isometric frame before geometry QA.
- Required default projected axes: X=30 degrees, Z=90 degrees, Y=150 degrees.
- Default true-length axis scale must equal 1.0.
- Reject arbitrary camera roll or visually rotated post-processing.
- Validate circles/conics on the correct Left/Top/Right isoplane.


### G4G — R9 regression baseline
- Use `engineering-cad/hvac-dxf/baselines/R9/` as the canonical regression baseline for the current isometric workflow.
- Before accepting changes to projector frame, HLR edge selection, true-length scaling, isoplane handling, layout, or DXF export, compare against the R9 baseline.
- Required default geometry remains X=30 degrees, Z=90 degrees, Y=150 degrees, with true-length projected axis scale 1.0.
- The four baseline models must retain zero layout collisions and zero DXF structural audit errors.
- R9 may be superseded only by a documented baseline revision with comparison evidence and human review.


### G2A — Brand/supplier authority
Before accepting supplier evidence:
- confirm the manufacturer/brand official domain;
- verify the supplier/partner through the manufacturer's own official locator, partner page, or official document;
- record supplier name, relationship, official verification URL, region, and checked date;
- if verification fails, classify the supplier as RESELLER/UNKNOWN and block it from supporting final geometry or supplier authorization;
- when no verified authorized channel is available, use manufacturer-direct sources only.

Examples already registered include WEG, Schneider Electric, Phoenix Contact, Rockwell Automation/Allen-Bradley, Daikin, Belimo and Vaisala. The registry is extensible and must be expanded from brand-owned evidence only.
