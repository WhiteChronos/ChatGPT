# 3D / DXF Toolchain

## Primary precision path
1. **FreeCAD/FreeCAD** — STEP/IGES/BREP import, TechDraw and engineering inspection. LGPL-2.1 repository license.
2. **CadQuery/cadquery** — parametric 3D and STEP import; Apache-2.0. CadQuery documents STEP import and DXF export of 2D sections/sketches.
3. **OpenCascade via OCP/pythonocc-core** — hidden-line removal (HLR), BREP topology and precise projections.
4. **mozman/ezdxf** — DXF writing, layers, blocks and audit; MIT.

## Secondary / complementary path
- **kevancress/MeasureIt_ARCH** — Blender technical-documentation add-on with DXF/vector export; GPL-3.0-or-later. Use for presentation/documentation, not as the dimensional master when BREP CAD exists.
- **fougue/mayo** — CAD inspection/conversion; BSD-2-Clause.
- **LibreDWG/libredwg** — DWG/DXF interoperability; GPL-3.0.
- **codelibs/libdxfrw** — DXF/DWG interoperability.
- **LibreCAD/LibreCAD** — 2D DXF QA.
- **solvespace/solvespace** — constraint CAD; GPL-3.0.
- **openscad/openscad** — deterministic constructive-solid geometry; useful for simple parametric fixtures, not the preferred reconstruction engine for complex manufacturer housings.

## Source platform
- **3Dfindit / CADENAS** — manufacturer-certified catalogs; useful for obtaining native/neutral 3D CAD when available. Manufacturer source remains the primary identity authority.
