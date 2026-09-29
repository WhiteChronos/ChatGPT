# Geometry Contract

## Source authority

1. Manufacturer STEP/IGES.
2. Manufacturer native CAD/DXF.
3. Deterministic parametric reconstruction from an official dimensional drawing.
4. Official dimensional bounding-box proxy when full geometry is unavailable.
5. Generative imagery only as non-dimensional visual reference.

## Tools

- FreeCAD / OpenCascade: STEP/IGES/BREP import, assembly, technical views.
- CadQuery / build123d: deterministic parametric reconstruction.
- trimesh / Open3D: bounds, mesh and scene-graph QA.
- Blender: photorealistic render of frozen geometry.
- Revit + pyRevit / RevitPythonShell / IFC: BIM interoperability in an authorized Autodesk environment.
- IfcOpenShell: open IFC geometry inspection and interchange.

## Geometry rules

- Units: mm.
- Object scale: 1:1 physical model.
- Bounding-box tolerance: <= 1% unless the manufacturer publishes a different envelope rule.
- One physical object per BOM instance.
- One common assembly coordinate system.
- Orthographic projection for measured views.
- No independent view scale.
- No non-uniform object scaling.
- No fit-to-canvas physical scaling.
- Canvas/page may grow without limit required to preserve engineering scale and legibility.

## Failure matrix

| Condition | Status |
| --- | --- |
| Missing official dimensions/CAD | HOLD_DIMENSIONAL_DATA |
| Missing Revit environment when Revit execution is requested | HOLD_TOOL_ENVIRONMENT |
| BBox mismatch > tolerance | REPROVADO |
| Different assembly/coordinates between views | REPROVADO |
| Perspective camera used as dimensional view | REPROVADO |
| Squeeze/stretch/non-uniform scaling | REPROVADO |
| Component downscaled to fit poster | REPROVADO |
| Canvas enlarged to preserve scale | PASS |
| Blender changes only materials/lights | PASS |
