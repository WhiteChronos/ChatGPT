# View and Isometric DXF Standard

- Derive all views from one 3D geometry master whenever possible.
- Use hidden-line removal, not a pseudo-isometric box.
- Required default views: FRONT, LEFT, RIGHT, TOP, BOTTOM, ISO.
- Export each view as its own DXF and create a combined MULTIVIEW DXF.
- Place ISO in a dedicated zone and reject any overlapping bounding boxes.
- Preserve curves as LINE/CIRCLE/ELLIPSE/SPLINE/ARC when the CAD kernel supports them.
- DXF final units: meters; Model Space 1:1; Arial text style.
- Do not generate a final ISO from a marketing photo.


## ISO visibility standard
- Default/final ISO = visible edges only.
- Hidden ISO edges are optional and must not be shown in the final default package unless explicitly requested.
- If hidden ISO edges are exported, they must be a separate technical variant or a hidden layer turned off by default.
- MULTIVIEW.dxf must include the clean ISO.


## Curve continuity rule
- Preserve full HLR edges and analytic curves whenever possible.
- Do not publish per-pixel/per-segment depth clipping as final DXF when it produces broken curves.
- Use exact HLR edge classification for final linework, and surface/depth rendering as QA/reference.
- Default ISO_CLEAN should use `OutLineVCompound + VCompound`; keep `Rg1LineVCompound` out unless justified.


## 30/90/150 canonical axes
- X axis: 30 degrees.
- Z axis: 90 degrees vertical.
- Y axis: 150 degrees.
- Default is true-length isometric drawing scale.
- Mathematical foreshortened projection is optional only when explicitly requested.
- Do not rotate a finished DXF as a substitute for setting the correct projector frame.
