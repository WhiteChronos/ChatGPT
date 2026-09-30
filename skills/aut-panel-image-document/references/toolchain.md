# Step 6 Toolchain

Physical image authority:
- Step 5 canonical assembly/render only.

Vector engineering diagrams:
- QElectroTech for electrical/control schematic support.
- SchemDraw for deterministic vector schematic support.
- NetworkX plus SVG for communication topology.
- CairoSVG for controlled SVG conversion.
- ezdxf when DXF exchange is required.

Composition/math/QA:
- Wolfram for dimension/canvas arithmetic cross-checks.
- OpenCV for image-regression checks.
- ImageHash for supplementary fingerprinting.
- Blender is not used to change Step 5 geometry in Step 6.
- Adobe/ImageGen may only perform presentation cleanup that cannot change geometry, labels, dimensions or topology.

Review plugins:
B&A Diagrams, tldraw and Miro may be used for review/annotation. Their output is not engineering authority unless reconstructed from controlled data through the deterministic document pipeline.
