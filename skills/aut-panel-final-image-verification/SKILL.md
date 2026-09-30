---
name: aut-panel-final-image-verification
description: Verify the final Step 7 engineering image for each industrial automation panel PN after the Step 6 document is frozen. Use when ChatGPT must mathematically check framing, cross-view agreement, real H/W/D proportions, common px-per-mm scale, door/enclosure consistency, camera projection, reprojection error, clipping, canvas fit, dimensional labels, visual regression, and final image fidelity against the canonical Step 5/6 geometry before release.
---

# AUT Panel Step 7 - Final Image Verification

Execute only after `STEP6_ENGINEERING_IMAGE_DOCUMENT_FROZEN` for the same PROJECT_NUMBER, PANEL_ID and revision.

Step 7 verifies only. Do not repair geometry or composition here.

## Workflow
1. Load Step 4 LI/load fingerprints, Step 5 canonical assembly/render manifests, Step 6 document manifest, controlled H/W/D, MODEL 001 revision and final image files.
2. Run `scripts/verify_final_image_manifest.py`.
3. If an approved same-view baseline exists, run `scripts/verify_visual_regression.py` as secondary QA.
4. Review mathematical findings using `references/mathematical-checks.md`.
5. Route failures using `references/failure-routing.md`.
6. Freeze only when all release-critical checks pass.

## Verification layers
- Canonical identity: same project/panel/revision/assembly/fingerprints.
- Multiview geometry: same H/W/D, door/enclosure bbox, hinge axis, instances and object scale.
- Orthographic proportion: physical ratio versus pixel ratio.
- Common scale: px/mm equality on both axes and across dimensional views.
- Calibrated 3/4: camera projection plus 3D/2D landmark reprojection RMSE.
- Framing: clipping, minimum margins, centered balance and canvas fit.
- Dimension labels: displayed H/W/D must equal controlled values.
- Visual regression: SSIM/hash/edge checks are supplementary only.

## Tool routing
Use Wolfram for independent arithmetic; OpenCV for camera/reprojection/registration; scikit-image for SSIM; pytransform3d for rigid transforms; trimesh/Open3D for geometry QA; Blender metadata for render reproducibility; FreeCAD/CadQuery/build123d/OpenCascade for controlled geometry; ImageHash and visual-regression tools only as secondary checks.

Remote Desktop Commander may execute authorized local verification tools. Adobe/ImageGen/to3D/Miro/tldraw cannot prove dimensions.

## Outputs
- FINAL_IMAGE_QA_MANIFEST
- MATHEMATICAL_IMAGE_PRECISION_REPORT
- MULTIVIEW_CONSISTENCY_REPORT
- FRAMING_AND_CANVAS_REPORT
- VISUAL_REGRESSION_REPORT when applicable
- STEP7_FINAL_IMAGE_VERIFIED

## Failure routing
- LI/load/quantity error -> Step 4.
- Geometry/H/W/D/door/camera/reprojection error -> Step 5.
- Canvas/framing/labels/document composition error -> Step 6.

Pass only as `STEP7_FINAL_IMAGE_VERIFIED`.
