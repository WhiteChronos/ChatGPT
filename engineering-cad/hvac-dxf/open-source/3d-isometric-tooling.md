# 3D / Isometric DXF tooling registry

Primary precision tools:
- FreeCAD/FreeCAD
- CadQuery/cadquery
- tpaviot/pythonocc-core
- mozman/ezdxf

Complementary tools:
- kevancress/MeasureIt_ARCH
- fougue/mayo
- LibreDWG/libredwg
- codelibs/libdxfrw
- LibreCAD/LibreCAD
- solvespace/solvespace
- openscad/openscad

Policy: BREP/STEP geometry is preferred over mesh. Blender/MeasureIt_ARCH is presentation/documentation support, not the dimensional authority when manufacturer CAD exists.


Additional visibility/occlusion tooling:
- Open-Cascade-SAS/OCCT — exact BREP/HLR kernel.
- blender/blender — Freestyle visible-line rendering using view visibility/Z-depth.
- kevancress/MeasureIt_ARCH — Blender technical drawing + DXF/vector export.
- Kitware/VTK — surface depth-buffer and silhouette validation.
- pyvista/pyvista — higher-level VTK silhouette/feature tooling.
- blender/blender-addons render_freestyle_svg.py — vector SVG output from Freestyle.
