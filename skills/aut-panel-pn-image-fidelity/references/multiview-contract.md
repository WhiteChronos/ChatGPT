# Multiview Consistency Contract

Canonical scene fields:
PROJECT_NUMBER, PANEL_ID, REVISION, ASSEMBLY_HASH, UNIT=mm, H_MM/W_MM/D_MM, enclosure_object_id, door_object_id, door_bbox_mm, enclosure_bbox_mm, hinge_axis_origin_mm, hinge_axis_direction, component_instances[], camera_views[].

Invariants:
1. ASSEMBLY_HASH identical for every view.
2. Every object model-space scale = [1,1,1].
3. Door local bounding box identical in every view.
4. Door pose only rigid transform about same hinge axis.
5. Enclosure H/W/D identical across all manifests.
6. Component instance IDs/quantities match frozen LI.
7. Door-mounted devices remain at same door-local coordinates.
8. Internal devices remain on same mounting surfaces.

View classes:
FRONT_CLOSED orthographic; FRONT_OPEN orthographic; SIDE orthographic; ISO_3Q orthographic-isometric preferred with controlled perspective allowed for non-dimensional realism; DEPTH_SECTION orthographic.

Tolerance for imported CAD numeric noise: <=0.10 mm dimensions, <=1e-6 transform orthonormality/object-scale deviation. Pixel checks are secondary.
