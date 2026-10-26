# True Isometric 3D Standard

## Definition
A true isometric technical view is an orthographic/parallel projection of a 3D solid. Perspective must be disabled. For the default engineering orientation use viewing direction `(1,-1,1)` unless a different documented quadrant is required.

The final result must read as a solid external object: nearest surfaces occlude geometry behind them.

## Mandatory visibility logic
1. Preserve the original BREP/STEP assembly or compound.
2. Use face-aware occlusion / depth information.
3. Keep external silhouette/contour edges.
4. Keep exposed hard/crease edges that define the real form.
5. Keep only selected seam/smooth edges when they improve recognition.
6. Remove hidden/back-side/internal edges from the final ISO.
7. Never expose internal geometry through an opaque front cover/enclosure.

## Boolean-fuse prohibition
Do not fuse components merely to reduce line clutter. Boolean union may remove/split covers, flanges, panels, bosses or coplanar faces and can change the visible exterior.

A fuse is allowed only when technically required and after validating the fused topology/envelope against the original assembly and manufacturer reference.

## Acceptance
Reject the ISO if the front/external wall disappears, internal parts show through opaque covers, the view looks like a section/x-ray/wireframe, the camera quadrant is wrong, or the DXF does not match a surface/depth reference from the same geometry master.

## Output variants
- `ISO_CLEAN`: solid external appearance; silhouette + selected exposed feature edges only.
- `ISO_TECHNICAL`: optional engineering view with additional visible/hidden information on controlled layers.
