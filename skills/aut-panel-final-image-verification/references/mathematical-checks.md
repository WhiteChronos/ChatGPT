# Mathematical Checks

Orthographic front/open:
expected_ratio = W_mm / H_mm
observed_ratio = bbox_width_px / bbox_height_px

Orthographic side/depth:
expected_ratio = D_mm / H_mm

Error_percent = abs(observed/expected - 1) * 100.

Pixel scale:
front/open px_per_mm_x=bbox_width_px/W_mm; px_per_mm_y=bbox_height_px/H_mm.
side/depth px_per_mm_x=bbox_width_px/D_mm; px_per_mm_y=bbox_height_px/H_mm.
Compare both axes and all dimensional views against the common scale.

Reprojection:
For a 3x4 projection matrix P and homogeneous point X=[x,y,z,1], q=P*X, u=q0/q2, v=q1/q2. Compare against observed image landmarks and calculate RMSE in pixels.

Framing:
Require all content within canvas with frozen minimum margins. Centered views also compare left/right and top/bottom margin balance.

Suggested default internal QA tolerances:
aspect error <=0.25%; per-axis scale mismatch <=0.25%; cross-view scale deviation <=0.50%; reprojection RMSE <=1.5 px; CAD/model dimension tolerance <=0.10 mm; centered margin imbalance <=5%.

These are internal defaults, not technical-standard limits. Do not loosen a frozen tolerance to obtain PASS.
