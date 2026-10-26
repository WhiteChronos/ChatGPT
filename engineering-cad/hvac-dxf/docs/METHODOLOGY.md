# METHODOLOGY — Hyper-realistic DXF

## Reference standard
Use the user-supplied DXFs `3D135205A0.dxf`, `3D135206A0.dxf`, and `FXAQ20~63AVM.dxf` as fidelity benchmarks. Read `references/hyperrealistic-dxf-standard.md`.

## Physical object methodology
1. Identify exact model.
2. Acquire the highest-authority geometry source available.
3. Prefer native CAD/BIM/STEP/DWG/DXF over tracing PDFs.
4. Preserve manufacturer geometry and curve types.
5. Generate FRONT, LEFT, RIGHT, TOP, BOTTOM/SECTION when available, and ISO.
6. Preserve engineering-relevant detail: housing, covers, fasteners, display, cable glands, process connections, probes, floats, brackets, vents and mounting interfaces.
7. Keep object and symbol separate.
8. Normalize to Model Space 1:1, meters, Arial without changing geometry.

## Reconstruction methodology
When no native CAD exists:
- reconstruct from explicit official dimensions;
- use parametric CAD where possible;
- create a consistent 3D or geometric master before deriving views;
- do not guess hidden dimensions;
- mark `RECONSTRUCAO_FICHA`.

## Fidelity rejection rule
Reject the output if the manufacturer/reference drawing shows substantial curved/detail geometry and the generated block collapses it into a generic rectangle, cube or low-detail silhouette.
