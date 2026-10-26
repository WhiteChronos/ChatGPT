# View and Isometric DXF Standard

- Derive all views from one 3D geometry master whenever possible.
- Use hidden-line removal, not a pseudo-isometric box.
- Required default views: FRONT, LEFT, RIGHT, TOP, BOTTOM, ISO.
- Export each view as its own DXF and create a combined MULTIVIEW DXF.
- Place ISO in a dedicated zone and reject any overlapping bounding boxes.
- Preserve curves as LINE/CIRCLE/ELLIPSE/SPLINE/ARC when the CAD kernel supports them.
- DXF final units: meters; Model Space 1:1; Arial text style.
- Do not generate a final ISO from a marketing photo.
