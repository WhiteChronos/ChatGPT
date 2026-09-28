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
