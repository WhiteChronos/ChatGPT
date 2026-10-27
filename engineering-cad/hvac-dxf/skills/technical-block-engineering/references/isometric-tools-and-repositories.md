# Isometric 3D tools and repositories

## Geometry / technical drawing
- https://github.com/FreeCAD/FreeCAD — TechDraw, precise HLR, isometric projection and DXF export. LGPL-2.1.
- https://github.com/Open-Cascade-SAS/OCCT — BREP kernel, topology and HLR. LGPL-2.1 with OCCT exception.
- https://github.com/CadQuery/cadquery — parametric BREP/STEP and HLR access. Apache-2.0.
- https://github.com/mozman/ezdxf — DXF writer/audit. MIT.

## Surface visibility / visual validation
- https://github.com/blender/blender — orthographic camera + Freestyle; visibility can be selected by occlusion/Z-depth. GPL.
- https://github.com/kevancress/MeasureIt_ARCH — Blender design documentation and DXF/vector export. GPL-3.0-or-later.
- https://github.com/Kitware/VTK — surface rendering, depth buffer and vtkPolyDataSilhouette. BSD-style.
- https://github.com/pyvista/pyvista — high-level VTK surface/silhouette tooling. MIT.

## Vector export helpers
- Blender Freestyle SVG Exporter (`blender/blender-addons/render_freestyle_svg.py`) — vector SVG export from Freestyle.
- https://github.com/Ibrahim-3d/blender-dxf-exporter — Blender curve/Grease Pencil DXF/DWG export; use only after release/license review.

## Policy
The verified BREP/STEP model remains the dimensional authority. Blender/VTK/mesh workflows are visibility and presentation helpers unless derived from the same verified geometry master.
