# Isometric QA checklist
- [ ] ISO is in a dedicated zone
- [ ] ISO bounding box does not intersect any orthographic view bounding box
- [ ] ISO bounding box does not intersect symbol bounding box
- [ ] ISO uses the same geometry master as orthographic views
- [ ] ISO preserves documented visible features
- [ ] No pseudo-cube placeholder remains
- [ ] ISO visible edges only by default
- [ ] ISO hidden edges absent from default package or turned off by default
- [ ] MULTIVIEW uses clean ISO rather than x-ray ISO


- [ ] Isometric camera uses orthographic/parallel projection
- [ ] Selected camera quadrant is verified against the intended manufacturer view
- [ ] Front/external faces occlude geometry behind them
- [ ] No internal components appear through opaque covers
- [ ] Original assembly/compound was not fused merely for line cleanup
- [ ] Solid/depth reference from the same STEP/BREP matches the DXF ISO


- [ ] Curves/edges are continuous and not fragmented by visibility sampling
- [ ] External silhouette closes coherently where geometry requires it
- [ ] Object does not look exploded/disconnected


- [ ] X axis projects at 30 degrees
- [ ] Z axis projects vertically at 90 degrees
- [ ] Y axis projects at 150 degrees
- [ ] Default true-length projected axis scale is 1.0
- [ ] Isometric circles/conics follow the correct isoplane
