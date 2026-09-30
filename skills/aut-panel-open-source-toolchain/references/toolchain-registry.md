# Toolchain Registry Reference

## Geometry / CAD
- FreeCAD/FreeCAD — open-source CAD platform; candidate geometry authoring/review.
- Open-Cascade-SAS/OCCT — geometry kernel; candidate deterministic solid modeling foundation.
- CadQuery/cadquery — Python parametric CAD.
- gumyr/build123d — Python parametric CAD.
- mikedh/trimesh — mesh/bounding-box/scene QA.
- isl-org/Open3D — 3D geometry/point-cloud QA.
- IfcOpenShell/IfcOpenShell — IFC/BIM interchange.
- blender/blender — rendering only after geometry lock.
- pyrevitlabs/pyRevit — Revit automation bridge; requires authorized Autodesk environment.

## Optimization / diagrams / graphs
- google/or-tools — constraint/layout optimization.
- cdelker/schemdraw — electrical/vector schematic rendering.
- networkx/networkx — topology/dependency graphs.
- opencv/opencv — visual regression and image QA.

## Agent / orchestration references
- microsoft/autogen — multi-agent framework reference.
- langchain-ai/langgraph — stateful graph orchestration reference.
- crewAIInc/crewAI — multi-agent workflow reference.
- openai/openai-cookbook — implementation patterns/reference only.

## Governance
Do not promote based only on popularity. Pin versions/commits, verify license, review security, run sandbox/regression tests, and require human approval before core-pipeline adoption.
