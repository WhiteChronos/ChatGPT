from __future__ import annotations

import copy

import pytest

from pipeline.layout_optimizer.models import LayoutConfig


def _catalog():
    return {
        "components": [
            {
                "catalog_id": "ENC-1",
                "category": "enclosure",
                "dimensions_mm": {"width": 600, "height": 800, "depth": 300},
                "clearance_mm": {},
            },
            {
                "catalog_id": "BAT-1",
                "category": "battery",
                "dimensions_mm": {"width": 100, "height": 120, "depth": 80},
                "clearance_mm": {"left": 2, "right": 2, "top": 3, "bottom": 3},
            },
            {
                "catalog_id": "HMI-1",
                "category": "hmi",
                "dimensions_mm": {"width": 150, "height": 100, "depth": 40},
                "clearance_mm": {},
            },
            {
                "catalog_id": "PLC-1",
                "category": "plc_controller",
                "dimensions_mm": {"width": 80, "height": 140, "depth": 70},
                "clearance_mm": {},
            },
            {
                "catalog_id": "DIN-REF",
                "category": "din_rail",
                "dimensions_mm": None,
                "clearance_mm": {},
            },
            {
                "catalog_id": "DUCT-REF",
                "category": "wireway",
                "dimensions_mm": None,
                "clearance_mm": {},
            },
            {
                "catalog_id": "GLAND-REF",
                "category": "cable_gland",
                "dimensions_mm": None,
                "clearance_mm": {},
            },
        ]
    }


def _li():
    return {
        "project_id": "PN-TEST",
        "revision": "R01",
        "status": "QUANTITY_FROZEN",
        "lines": [
            {"tag": "BAT-01A/B", "catalog_id": "BAT-1", "quantity": 2, "unit": "un", "render_required": True},
            {"tag": "PLC-01", "catalog_id": "PLC-1", "quantity": 1, "unit": "un", "render_required": True},
            {"tag": "HMI-01", "catalog_id": "HMI-1", "quantity": 1, "unit": "un", "render_required": True},
            {"tag": "DIN-01..02", "catalog_id": "DIN-REF", "quantity": 2, "unit": "un", "render_required": True},
            {"tag": "WD-01..03", "catalog_id": "DUCT-REF", "quantity": 3, "unit": "un", "render_required": True},
            {"tag": "CG-01..04", "catalog_id": "GLAND-REF", "quantity": 4, "unit": "un", "render_required": True},
        ],
    }


def _bom(li=None):
    li = li or _li()
    return {
        "project_id": "PN-TEST",
        "revision": "R01",
        "lines": [
            {
                "li_tag": x["tag"],
                "catalog_id": x["catalog_id"],
                "quantity": x["quantity"],
                "unit": x["unit"],
            }
            for x in li["lines"]
        ],
    }


def _project():
    return {
        "project": {"id": "PN-TEST", "revision": "R01"},
        "enclosure": {
            "external_mm": {"width": 600, "height": 800, "depth": 300},
            "mounting_plate_mm": {"width": 550, "height": 750},
            "minimum_free_reserve_percent": 20,
        },
        "layout": {
            "bottom_zone": {
                "cable_exit_height_mm": 40,
                "lower_wireway_height_mm": 40,
                "minimum_bend_clearance_mm": 20,
                "terminal_zone_bottom_y_mm": 120,
                "cable_glands_count": 4,
            }
        },
    }


def test_normalize_expands_grouped_quantity_and_preserves_surfaces():
    from pipeline.layout_optimizer.normalize import normalize_inputs

    panel, instances, diagnostics = normalize_inputs(
        "PN-TEST", _li(), _bom(), _catalog(), _project(), LayoutConfig()
    )

    assert diagnostics == []
    assert panel.panel_id == "PN-TEST"
    assert panel.revision == "R01"
    assert panel.plate_width_mm == 550
    assert panel.plate_height_mm == 750
    assert panel.minimum_free_reserve_percent == 20

    ids = [x.instance_id for x in instances]
    assert ids == [
        "BAT-01A/B#01",
        "BAT-01A/B#02",
        "PLC-01#01",
        "HMI-01#01",
    ]
    assert [x.source_tag for x in instances[:2]] == ["BAT-01A/B", "BAT-01A/B"]
    assert instances[0].quantity_index == 1
    assert instances[1].quantity_index == 2
    assert instances[0].surface == "mounting_plate"
    assert next(x for x in instances if x.source_tag == "HMI-01").surface == "door"


def test_infrastructure_lines_are_classified_not_solver_rectangles():
    from pipeline.layout_optimizer.normalize import extract_infrastructure_requests, normalize_inputs

    _, instances, diagnostics = normalize_inputs(
        "PN-TEST", _li(), _bom(), _catalog(), _project(), LayoutConfig()
    )
    requests = extract_infrastructure_requests(_li(), _bom(), _catalog())

    assert diagnostics == []
    assert {x.source_tag for x in instances}.isdisjoint({"DIN-01..02", "WD-01..03", "CG-01..04"})
    assert [(x["kind"], x["source_tag"], x["quantity"]) for x in requests] == [
        ("din_rail", "DIN-01..02", 2),
        ("wireway", "WD-01..03", 3),
        ("cable_gland", "CG-01..04", 4),
    ]


def test_missing_component_dimensions_returns_hold_diagnostic_and_skips_instance():
    from pipeline.layout_optimizer.normalize import normalize_inputs

    catalog = _catalog()
    plc = next(x for x in catalog["components"] if x["catalog_id"] == "PLC-1")
    plc["dimensions_mm"] = None

    _, instances, diagnostics = normalize_inputs(
        "PN-TEST", _li(), _bom(), catalog, _project(), LayoutConfig()
    )

    assert "MISSING_DIMENSIONS:PLC-1" in diagnostics
    assert not any(x.catalog_id == "PLC-1" for x in instances)


def test_li_bom_quantity_or_catalog_mismatch_is_rejected():
    from pipeline.layout_optimizer.normalize import normalize_inputs

    bom = _bom()
    bom["lines"][0]["quantity"] = 1

    with pytest.raises(ValueError, match="LI_BOM_PARITY"):
        normalize_inputs("PN-TEST", _li(), bom, _catalog(), _project(), LayoutConfig())
