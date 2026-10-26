# Backend selection

## Current runtime verified
- CadQuery 2.8.0: available
- OpenCascade OCP 7.9.3.1: available
- ezdxf 1.4.4: available
- trimesh 4.11.1: available
- OpenSCAD executable: available
- FreeCAD executable: not currently installed
- Blender executable: not currently installed

## Selection policy
1. If FreeCAD is installed and manufacturer STEP/IGES/BREP is available, FreeCAD TechDraw is a preferred high-level path.
2. If CadQuery + OCP + ezdxf are available, use `step_to_multiview_dxf.py` for precise STEP hidden-line projection and DXF export.
3. Use MeasureIt_ARCH only when Blender is actually available and presentation/documentation advantages justify it.
4. Never downgrade from BREP/STEP to STL/mesh unless the source has no BREP equivalent and the loss of precision is documented.
