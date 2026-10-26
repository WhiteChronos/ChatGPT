# Hyper-realistic DXF Standard

## Reference DXFs supplied by the user

These files define the minimum fidelity pattern for technical blocks:
- `3D135205A0.dxf` — SHA256 `82542c95950c0bef71542b7dcc38d325f35676b836a175ac0287c40404dc5341`
- `3D135206A0.dxf` — SHA256 `81dab5867947638b441f1235afad0a1fd24dbd8edfbf493330cfbbf96a8bf6e8`
- `FXAQ20~63AVM.dxf` — SHA256 `d37b55ad732b26904cb246de800f7e7ff043107c9bee967df78001c4f022b687`

Measured structure:
- 3D135205A0: 4,384 model-space entities; LINE 3,037; ARC 768; CIRCLE 265; ELLIPSE 248; SPLINE 58; 0 audit errors.
- 3D135206A0: 5,234 entities; LINE 3,672; ARC 920; CIRCLE 334; ELLIPSE 243; SPLINE 58; 0 audit errors.
- FXAQ20~63AVM: 1,472 entities; LINE 998; ARC 462; ELLIPSE 3; 0 audit errors.

The reference DXFs use dense curve/detail geometry. Entity count is a benchmark only, never a blind acceptance threshold.

## Fidelity rule
A block is hyper-realistic only when:
1. it is native manufacturer CAD/BIM, or a faithful reconstruction from official dimensional/technical drawings;
2. real housing shape, covers, vents, display, fasteners, probes, floats, brackets, ports, cable entries, connectors, mounting interfaces and other visible engineering features are preserved when documented;
3. curves remain curves (ARC/ELLIPSE/SPLINE/POLYLINE as appropriate) rather than being reduced to boxes;
4. all available orthographic views are included;
5. an isometric view is included and is geometrically consistent with the orthographic set;
6. the DXF is compared visually against the manufacturer source and the supplied benchmark DXFs;
7. the symbol is separate and linked to the physical block.

## Prohibited shortcuts
- generic rectangular envelope presented as the real object;
- arbitrary 3D prism/cube ISO;
- symbol-only delivery when the user asked for the object;
- guessed ports, fasteners, probe lengths or mounting details;
- declaring “manufacturer model” from photo resemblance without technical closure.

## QA
Use geometry fidelity, source provenance, dimensional agreement and view consistency as primary gates. Complexity metrics are diagnostic only.
