# Open-source CAD Toolchain

Recommended roles:

| Tool / upstream | Role |
|---|---|
| mozman/ezdxf | DXF parsing, writing, audit, entity/layer inspection |
| FreeCAD/FreeCAD | STEP/IGES/BREP import, TechDraw projections, geometry inspection |
| CadQuery/cadquery | deterministic parametric reconstruction from official dimensions |
| tpaviot/pythonocc-core | OpenCascade topology, STEP geometry, projections and BREP operations |
| fougue/mayo | open CAD viewer/converter for STEP/IGES/BREP inspection |
| LibreDWG/libredwg | DWG/DXF interoperability and DWG inspection |
| codelibs/libdxfrw | DXF/DWG reading/writing support |
| LibreCAD/LibreCAD | 2D visual QA and DXF inspection |
| solvespace/solvespace | constraint-based geometric reconstruction |

## Preferred pipeline
1. Native DXF/DWG available -> preserve and normalize with ezdxf / LibreDWG/libdxfrw as needed.
2. STEP/IGES/BREP available -> inspect/import in FreeCAD or pythonocc; generate orthographic projections using TechDraw/OpenCascade; export DXF.
3. Only dimensional PDF/drawing available -> reconstruct parametrically with CadQuery/FreeCAD/pythonocc.
4. QA -> ezdxf audit + visual comparison in FreeCAD/LibreCAD.

Do not copy third-party source into the project unless required. Prefer dependency, fork or submodule after license review.
