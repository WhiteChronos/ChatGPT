# Occlusion and Isometric Backends

## Tier A — FreeCAD TechDraw
Preferred when installed.
- Direction `(1,-1,1)` unless another quadrant is justified.
- Perspective off.
- Hidden Hard/Smooth/Seam/Iso off for ISO_CLEAN.
- Smooth Visible normally off.
- Seam Visible off unless externally meaningful.
- Iso Visible off unless surface isoparametric curves are wanted.
- Detect faces on when needed.
- Show All Edges off.
- Precise HLR for final output; coarse/polygon mode only for preview.
- Export page/view to DXF.

## Tier B — Blender Freestyle + MeasureIt_ARCH
Use when view-dependent visibility and manufacturer-style line presentation are important.
- Orthographic camera.
- Freestyle Visibility = Visible only.
- Contour / External Contour + selected Crease edges.
- Hidden lines off for ISO_CLEAN.
- Z-depth is the authority for occlusion.
- MeasureIt_ARCH can export technical/vector drawings to DXF.

## Tier C — OpenCascade/CadQuery + VTK validation
Use OpenCascade HLR for technical line generation, but do not approve ISO_CLEAN from edge data alone.
- preserve original compound; do not fuse for cleanup;
- create HLR visible/hidden sets;
- render a VTK surface/depth reference from the same STEP;
- compare the line result to the solid surface reference;
- reject if a front face/enclosure does not occlude geometry behind it.

VTK/PyVista silhouette tools are useful for camera-dependent silhouette and feature-edge validation.

## DXF writer
Use ezdxf for layers, units, blocks, metadata and audit.
