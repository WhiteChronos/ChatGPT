from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_agent_registry_has_isolated_namespaces():
    data = yaml.safe_load((ROOT / "agents/AUT_PANEL_AGENT_SYSTEM.yaml").read_text(encoding="utf-8"))
    agents = data["agents"]
    assert len(agents) >= 14
    dc = [x["datacenter_namespace"] for x in agents]
    mem = [x["memory_namespace"] for x in agents]
    assert len(dc) == len(set(dc))
    assert len(mem) == len(set(mem))
    assert data["policy"]["autoevolution_mode"] == "PROPOSAL_ONLY"
    assert data["policy"]["ml_is_advisory_only"] is True


def test_database_schema_and_memory_event(tmp_path):
    dbmod = load_module("aut_panel_db", "pipeline/aut_panel_db.py")
    db = tmp_path / "aut_panel.sqlite3"
    dbmod.init_db(db)
    event_id = dbmod.record_memory_event(
        db,
        agent_id="QA",
        event_type="TEST",
        summary="regression",
        panel_id="PN-AUT-01",
        panel_revision="R02",
    )
    assert event_id.startswith("MEM-")
    with sqlite3.connect(db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0]
    assert count == 1


def test_learning_starts_cold_and_is_advisory():
    ml = load_module("aut_panel_learning", "pipeline/aut_panel_learning.py")
    result = ml.evaluate_dataset([
        {"features": {"quantity_mismatch": 0.0}, "label": "accepted", "reviewed_by_human": True}
    ])
    assert result["status"] == "LEARNING_COLD_START"
    assert result["advisory_only"] is True
    assert result["auto_apply_locked_changes"] is False


def test_evolution_never_auto_applies_locked_change():
    evo = load_module("evolution_engine", "pipeline/evolution_engine.py")
    proposal = evo.build_proposal({
        "problem": "repeated quantity mismatch",
        "affected_files": ["governance/golden_rules.yaml"],
        "candidate_change": {"type": "threshold_change"},
        "tests": ["pytest"],
    })
    assert proposal["touches_locked_contract"] is True
    assert proposal["requires_human_approval"] is True
    assert proposal["auto_apply_allowed"] is False


def test_open_source_registry_excludes_archived_core_candidates():
    data = json.loads((ROOT / "plugins/aut_panel_open_source_registry.json").read_text(encoding="utf-8"))
    repos = {x["repository"]: x for x in data["repositories"]}
    assert repos["google/or-tools"]["archived"] is False
    assert repos["online-ml/river"]["archived"] is False
    excluded = {x["repository"] for x in data["excluded_from_new_core_dependency"]}
    assert "mozman/svgwrite" in excluded


def test_panel_render_contract_blocks_duplicate_hmi_and_requires_dimensions():
    pipeline = yaml.safe_load((ROOT / "pipeline/pipeline.yaml").read_text(encoding="utf-8"))
    template = yaml.safe_load((ROOT / "templates/panel_template.yaml").read_text(encoding="utf-8"))
    golden = yaml.safe_load((ROOT / "governance/golden_rules.yaml").read_text(encoding="utf-8"))
    prompt = (ROOT / "prompts/PROMPT_MASTER_AUT_PANEL.md").read_text(encoding="utf-8")

    layout = next(x for x in pipeline["sequence"] if x["id"] == "LAYOUT")
    render = next(x for x in pipeline["sequence"] if x["id"] == "RENDER_IMAGE")

    assert "hmi_unique_physical_instance" in layout["gate"]
    assert "door_components_not_duplicated_on_mounting_plate" in layout["gate"]
    assert "component_dimensional_evidence_complete" in layout["gate"]
    assert "cable_exit_clearance_validated" in layout["gate"]
    assert "no_duplicate_visual_instances" in render["gate"]
    assert "dimensional_closure_passed" in render["gate"]
    assert "render_derived_from_validated_layout" in render["gate"]

    fixed = template["image_standard"]["fixed_rules"]
    assert fixed["hmi_quantity_physical_instance"] == 1
    assert fixed["hmi_internal_duplicate_forbidden"] is True
    assert fixed["component_geometry_source"] == "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING"
    assert fixed["common_physical_scale_unit"] == "mm"

    ids = {x["id"] for x in golden["required_rules"]}
    for rule_id in {"GR-067", "GR-068", "GR-069", "GR-070", "GR-071", "GR-072", "GR-073"}:
        assert rule_id in ids

    assert "uma única instância física" in prompt
    assert "HOLD_DIMENSIONAL_DATA" in prompt
    assert "HOLD_LAYOUT_CAPACITY" in prompt


def test_panel_render_gate_accepts_single_door_hmi_and_backside_view():
    gate = load_module("panel_render_gate", "pipeline/panel_render_gate.py")
    manifest = {
        "panel_id": "PN-AUT-01",
        "panel_revision": "R02",
        "px_per_mm": 1.0,
        "bom_counts": {"HMI-01": 1, "PLC-01": 1},
        "physical_instances": [
            {
                "instance_id": "HMI-01-001",
                "physical_instance_key": "HMI-01-001",
                "catalog_id": "HMI-01",
                "component_class": "HMI",
                "mounting_surface": "door",
                "geometry_source": "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING",
                "orientation_deg": 0,
                "official_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
                "layout_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
            },
            {
                "instance_id": "PLC-01-001",
                "physical_instance_key": "PLC-01-001",
                "catalog_id": "PLC-01",
                "component_class": "PLC",
                "mounting_surface": "din",
                "geometry_source": "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING",
                "orientation_deg": 0,
                "official_dimensions_mm": {"width": 35, "height": 147, "depth": 129},
                "layout_dimensions_mm": {"width": 35, "height": 147, "depth": 129},
            },
        ],
        "view_representations": [
            {"instance_id": "HMI-01-001", "representation_role": "front"},
            {"instance_id": "HMI-01-001", "representation_role": "backside"},
            {"instance_id": "PLC-01-001", "representation_role": "internal"},
        ],
        "cable_exit": {
            "actual_clearance_mm": 150,
            "required_clearance_mm": 150,
            "bend_radius_validated": True,
            "gland_access_validated": True,
        },
    }
    result = gate.validate_render_manifest(manifest)
    assert result["status"] == "PASS"
    assert result["physical_instance_count"] == 2
    assert result["view_representation_count"] == 3


def test_panel_render_gate_rejects_duplicate_hmi_and_fake_scale():
    gate = load_module("panel_render_gate_bad", "pipeline/panel_render_gate.py")
    hmi = {
        "catalog_id": "HMI-01",
        "component_class": "HMI",
        "geometry_source": "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING",
        "orientation_deg": 0,
        "official_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
    }
    manifest = {
        "panel_id": "PN-AUT-01",
        "panel_revision": "R02",
        "px_per_mm": 1.0,
        "bom_counts": {"HMI-01": 1},
        "physical_instances": [
            dict(hmi, instance_id="HMI-DOOR", physical_instance_key="HMI-DOOR", mounting_surface="door",
                 layout_dimensions_mm={"width": 273, "height": 203, "depth": 47}),
            dict(hmi, instance_id="HMI-INTERNAL", physical_instance_key="HMI-INTERNAL", mounting_surface="backplate",
                 layout_dimensions_mm={"width": 180, "height": 140, "depth": 47}),
        ],
        "view_representations": [],
        "cable_exit": {
            "actual_clearance_mm": 80,
            "required_clearance_mm": 150,
            "bend_radius_validated": False,
            "gland_access_validated": False,
        },
    }
    result = gate.validate_render_manifest(manifest)
    assert result["status"] == "REPROVADO"
    assert any("HMI must be mounted on door only" in x for x in result["errors"])
    assert any("differ from BOM" in x for x in result["errors"])
    assert any("layout dimensions do not match official dimensions" in x for x in result["errors"])


def test_panel_render_gate_accepts_real_scale_side_open_and_image6():
    gate = load_module("panel_render_gate_side_ok", "pipeline/panel_render_gate.py")
    manifest = {
        "panel_id": "PN-AUT-01",
        "panel_revision": "R03",
        "px_per_mm": 1.0,
        "bom_counts": {"HMI-01": 1},
        "physical_instances": [{
            "instance_id": "HMI-01-001",
            "physical_instance_key": "HMI-01-001",
            "catalog_id": "HMI-01",
            "component_class": "HMI",
            "mounting_surface": "door",
            "geometry_source": "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING",
            "orientation_deg": 0,
            "official_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
            "layout_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
        }],
        "view_representations": [{"instance_id": "HMI-01-001", "representation_role": "front"}],
        "panel_views": [
            {
                "view_id": "right_side_open_depth_section",
                "physical_dimensions_mm": {"width": 300, "height": 800},
                "rendered_dimensions_px": {"width": 300, "height": 800},
                "dimensional": True,
                "annotations": ["external_depth", "usable_depth", "component_depths", "ducts", "clearances", "bend_radius", "cable_glands"],
            },
            {
                "view_id": "image_6",
                "physical_dimensions_mm": {"width": 300, "height": 800},
                "rendered_dimensions_px": {"width": 300, "height": 800},
                "dimensional": True,
                "annotations": ["external_depth", "usable_depth", "component_depths", "ducts", "clearances", "bend_radius", "cable_glands"],
            },
        ],
        "cable_exit": {
            "actual_clearance_mm": 150,
            "required_clearance_mm": 150,
            "bend_radius_validated": True,
            "gland_access_validated": True,
        },
    }
    result = gate.validate_render_manifest(manifest)
    assert result["status"] == "PASS"
    assert result["panel_view_count"] == 2


def test_panel_render_gate_rejects_squeezed_side_open_view():
    gate = load_module("panel_render_gate_side_bad", "pipeline/panel_render_gate.py")
    manifest = {
        "panel_id": "PN-AUT-01",
        "panel_revision": "R03",
        "px_per_mm": 1.0,
        "bom_counts": {"HMI-01": 1},
        "physical_instances": [{
            "instance_id": "HMI-01-001",
            "physical_instance_key": "HMI-01-001",
            "catalog_id": "HMI-01",
            "component_class": "HMI",
            "mounting_surface": "door",
            "geometry_source": "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING",
            "orientation_deg": 0,
            "official_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
            "layout_dimensions_mm": {"width": 273, "height": 203, "depth": 47},
        }],
        "view_representations": [{"instance_id": "HMI-01-001", "representation_role": "front"}],
        "panel_views": [{
            "view_id": "image_6",
            "physical_dimensions_mm": {"width": 300, "height": 800},
            "rendered_dimensions_px": {"width": 500, "height": 500},
            "dimensional": True,
            "annotations": ["external_depth", "usable_depth", "component_depths", "ducts", "clearances", "bend_radius", "cable_glands"],
        }],
        "cable_exit": {
            "actual_clearance_mm": 150,
            "required_clearance_mm": 150,
            "bend_radius_validated": True,
            "gland_access_validated": True,
        },
    }
    result = gate.validate_render_manifest(manifest)
    assert result["status"] == "REPROVADO"
    assert any("rendered aspect ratio" in x for x in result["errors"])
    assert any("common px_per_mm" in x for x in result["errors"])


def test_3d_geometry_gate_accepts_common_orthographic_assembly():
    gate = load_module("panel_3d_geometry_gate_ok", "pipeline/panel_3d_geometry_gate.py")
    manifest = {
        "units": "mm",
        "canvas_policy": "GROW_CANVAS_KEEP_SCALE",
        "generative_geometry_authority": False,
        "assembly_id": "PN-AUT-01-R03-ASM",
        "components": [{
            "instance_id": "HMI-01",
            "geometry_authority": "MANUFACTURER_STEP_OR_IGES",
            "official_bbox_mm": {"width": 273, "height": 203, "depth": 47},
            "model_bbox_mm": {"width": 273, "height": 203, "depth": 47},
        }],
        "views": [
            {"view_id":"front_internal","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
            {"view_id":"front_external","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
            {"view_id":"right_side","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
            {"view_id":"depth_section","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
        ],
        "visual_blocks":["front_internal_door_open","front_external_door_closed","right_side_view","right_side_open_depth_section"],
    }
    result=gate.validate_geometry_manifest(manifest)
    assert result["status"] == "PASS"


def test_3d_geometry_gate_rejects_independent_view_scaling_and_removed_blocks():
    gate = load_module("panel_3d_geometry_gate_bad", "pipeline/panel_3d_geometry_gate.py")
    manifest = {
        "units": "mm",
        "canvas_policy": "FIT_TO_FIXED_POSTER",
        "generative_geometry_authority": True,
        "assembly_id": "PN-AUT-01-R03-ASM",
        "components": [{
            "instance_id": "HMI-01",
            "geometry_authority": "MANUFACTURER_STEP_OR_IGES",
            "official_bbox_mm": {"width": 273, "height": 203, "depth": 47},
            "model_bbox_mm": {"width": 200, "height": 150, "depth": 47},
        }],
        "views": [
            {"view_id":"front_internal","assembly_id":"OTHER","projection":"PERSPECTIVE","independent_scale":True},
            {"view_id":"front_external","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
            {"view_id":"right_side","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
            {"view_id":"depth_section","assembly_id":"PN-AUT-01-R03-ASM","projection":"ORTHOGRAPHIC","independent_scale":False},
        ],
        "visual_blocks":["door_internal_hmi_detail","bottom_cable_exit_view"],
    }
    result=gate.validate_geometry_manifest(manifest)
    assert result["status"] == "REPROVADO"
    assert any("independent per-view scaling" in x for x in result["errors"])
    assert any("removed visual blocks present" in x for x in result["errors"])
