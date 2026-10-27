# AutoCAD / Engineering Isometric Standard

## Canonical axes
For this project, default isometric DXF output must follow the standard AutoCAD engineering isometric axes:
- +X at 30 degrees;
- +Z vertical at 90 degrees;
- +Y at 150 degrees;
- all three axes separated by 120 degrees.

Standard AutoCAD isoplanes:
- Right: 30 + 90 degrees;
- Left: 90 + 150 degrees;
- Top: 30 + 150 degrees.

## True-length drawing vs foreshortened projection
Default to an AutoCAD-style true-length isometric drawing. A mathematical orthographic isometric projection foreshortens all axes equally by sqrt(2/3)=0.8164965809. Convert that projection to true-length isometric drawing by one uniform factor sqrt(3/2)=1.2247448714.

Never scale axes independently.

## Fixed projector frame
Use:
- view/projection normal: (-1,-1,+1)
- in-plane X direction: (+1,-1,0)

This frame yields:
- +X -> 30 deg
- +Y -> 150 deg
- +Z -> 90 deg

Do not let the CAD kernel choose arbitrary projector roll.

## Circles
Circles on an isometric plane must appear as projected ellipses/isocircles. Do not replace projected conics with screen-space circles.

## QA
Reject the ISO if:
- projected axes are not 30/90/150 degrees within tolerance;
- default true-length axis scale is not 1.0;
- the camera/projector roll is arbitrary;
- a finished DXF was visually rotated after projection instead of fixing the projector frame.

## Source basis
- Autodesk AutoCAD Help: ISODRAFT / About 2D Isometric Drawing.
- QualifiCAD: Desenho Isométrico, explaining 2D isometric drafting and Left/Right/Top isoplanes.
