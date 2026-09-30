# Step 7 Manifest Schema

Canonical fields: PROJECT_NUMBER, PANEL_ID, REVISION, assembly_hash, h_mm, w_mm, d_mm.
Thresholds: aspect_error_percent, axis_scale_error_percent, common_scale_error_percent, reprojection_rmse_px, minimum_margin_px, center_margin_imbalance_fraction.
Each view records view_id, projection, expected_axes, canvas_px, panel_bbox_px, framing_mode, assembly_hash, dimension_labels_mm and object_scales.
Calibrated 3/4 views may add projection_matrix_3x4 and landmarks with model_point_mm and image_point_px.
