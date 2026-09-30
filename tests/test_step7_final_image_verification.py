import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("skills/aut-panel-final-image-verification/scripts/verify_final_image_manifest.py")


def _manifest(side_width=600):
    return {
        "canonical": {
            "project_number": "P-001",
            "panel_id": "PN-001",
            "revision": "R1",
            "assembly_hash": "abc",
            "h_mm": 1200,
            "w_mm": 800,
            "d_mm": 300,
        },
        "thresholds": {
            "aspect_error_percent": 0.25,
            "axis_scale_error_percent": 0.25,
            "common_scale_error_percent": 0.50,
            "minimum_margin_px": 20,
            "center_margin_imbalance_fraction": 0.05,
        },
        "views": [
            {
                "view_id": "FRONT_CLOSED",
                "projection": "orthographic",
                "expected_axes": ["w_mm", "h_mm"],
                "canvas_px": [1800, 2600],
                "panel_bbox_px": [100, 100, 1600, 2400],
                "framing_mode": "centered",
                "assembly_hash": "abc",
                "dimension_labels_mm": {"H": 1200, "W": 800},
                "object_scales": [{"id": "ENC", "scale": [1, 1, 1]}],
            },
            {
                "view_id": "SIDE",
                "projection": "orthographic",
                "expected_axes": ["d_mm", "h_mm"],
                "canvas_px": [800, 2600],
                "panel_bbox_px": [100, 100, side_width, 2400],
                "framing_mode": "centered",
                "assembly_hash": "abc",
                "dimension_labels_mm": {"H": 1200, "D": 300},
                "object_scales": [{"id": "ENC", "scale": [1, 1, 1]}],
            },
        ],
    }


def test_step7_valid_manifest_passes(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps(_manifest()), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
    assert cp.returncode == 0
    result = json.loads(cp.stdout)
    assert result["status"] == "PASS"
    assert result["common_px_per_mm"] == 2.0


def test_step7_bad_side_proportion_fails(tmp_path):
    p = tmp_path / "m.json"
    p.write_text(json.dumps(_manifest(side_width=650)), encoding="utf-8")
    cp = subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
    assert cp.returncode == 2
    result = json.loads(cp.stdout)
    assert result["status"] == "FAIL"
    assert any("aspect error" in e for e in result["errors"])
