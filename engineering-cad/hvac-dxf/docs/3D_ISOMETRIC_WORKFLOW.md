# 3D Isometric DXF Workflow

## Goal
Convert authoritative 3D CAD geometry into engineering-grade orthographic and isometric DXF views without overlap or pseudo-3D approximations.

## Preferred sources
1. Manufacturer STEP/BREP/native CAD.
2. Manufacturer-certified CAD catalog such as 3Dfindit when it preserves model identity.
3. Parametric reconstruction from official dimensional drawings only when native 3D CAD is unavailable.

## Backend order
1. FreeCAD + TechDraw when installed.
2. CadQuery + OpenCascade HLR + ezdxf.
3. pythonocc/OpenCascade custom workflow.
4. MeasureIt_ARCH/Blender only for secondary presentation/documentation.

## Execution
1. Validate manufacturer/model/variant.
2. Import STEP/BREP.
3. Generate FRONT, LEFT, RIGHT, TOP, BOTTOM and ISO from the same master.
4. Apply hidden-line removal.
5. Export each view to DXF.
6. Build MULTIVIEW DXF with automatic bounding-box spacing.
7. Reject any overlapping views.
8. Audit DXF and compare with manufacturer/reference geometry.

## Current verified runtime
CadQuery 2.8.0 + OCP 7.9.3.1 + ezdxf 1.4.4 are available and the bundled generator passed a regression test with 6 views, MULTIVIEW, zero collisions and zero DXF audit errors.
