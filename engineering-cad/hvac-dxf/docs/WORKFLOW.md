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
