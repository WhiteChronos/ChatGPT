from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "candidate_runner", ROOT / "pipeline/aut_panel_candidate_runner.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PIPELINE = {
    "sequence": [
        {"order": 10, "id": "LOAD_BALANCE"},
        {"order": 20, "id": "BOM"},
        {"order": 30, "id": "LAYOUT"},
        {"order": 40, "id": "RENDER_IMAGE"},
        {"order": 50, "id": "QA"},
        {"order": 60, "id": "MEMORY_SYNC"},
        {"order": 70, "id": "RELEASE"},
    ]
}


def test_enclosure_change_invalidates_ordered_downstream_without_release():
    runner = load_module()
    candidate = {
        "changes": [
            {
                "change_type": "ENCLOSURE_CHANGE",
                "invalidates": [
                    "LOAD_BALANCE",
                    "BOM",
                    "LAYOUT",
                    "RENDER_IMAGE",
                    "QA",
                    "MEMORY_SYNC",
                    "RELEASE",
                ],
            }
        ]
    }
    assert runner.build_candidate_execution_plan(candidate, PIPELINE) == [
        "LOAD_BALANCE",
        "BOM",
        "LAYOUT",
        "RENDER_IMAGE",
        "QA",
        "MEMORY_SYNC",
    ]


def test_io_change_runs_only_declared_downstream_and_never_release():
    runner = load_module()
    candidate = {
        "changes": [
            {
                "change_type": "IO_CHANGE",
                "invalidates": ["LAYOUT", "RENDER_IMAGE", "QA", "RELEASE"],
            }
        ]
    }
    assert runner.build_candidate_execution_plan(candidate, PIPELINE) == [
        "LAYOUT",
        "RENDER_IMAGE",
        "QA",
    ]


def test_unknown_invalidation_is_rejected():
    import pytest

    runner = load_module()
    candidate = {
        "changes": [{"change_type": "X", "invalidates": ["NO_SUCH_STAGE"]}]
    }
    with pytest.raises(ValueError):
        runner.build_candidate_execution_plan(candidate, PIPELINE)


def test_create_and_plan_candidate_applies_authorized_changes_without_mutating_source(tmp_path):
    import importlib.util
    runner = load_module()
    spec = importlib.util.spec_from_file_location("db_runner", ROOT / "pipeline/aut_panel_db.py")
    assert spec and spec.loader
    dbmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dbmod)
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    with dbmod.connect(db) as conn:
        conn.execute(
            "INSERT INTO panels(panel_id,revision,title,engineering_status,created_at) VALUES (?,?,?,?,?)",
            ("PN-AUT-01","R02","Panel","HOLD","2026-09-28T00:00:00+00:00"),
        )
    with dbmod.connect(db) as conn:
        before = tuple(conn.execute(
            "SELECT * FROM panels WHERE panel_id='PN-AUT-01' AND revision='R02'"
        ).fetchone())
    result = runner.create_and_plan_candidate(
        db_path=db,
        root=ROOT,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type":"CAPACITY"},
        canonical_inputs={"li":"abc"},
        changes=[{
            "change_type":"ENCLOSURE_CHANGE",
            "path":"panel.enclosure",
            "before":{"model":"A"},
            "after":{"model":"B"},
            "evidence":{"ref":"REF-001"},
            "invalidates":["LOAD_BALANCE","BOM","LAYOUT","RENDER_IMAGE","QA","MEMORY_SYNC","RELEASE"],
        }],
    )
    with dbmod.connect(db) as conn:
        after = tuple(conn.execute(
            "SELECT * FROM panels WHERE panel_id='PN-AUT-01' AND revision='R02'"
        ).fetchone())
    assert before == after
    assert result["source_revision"] == "R02"
    assert result["candidate_revision"] != "R02"
    assert result["planned_stages"] == ["LOAD_BALANCE","BOM","LAYOUT","RENDER_IMAGE","QA","MEMORY_SYNC"]
    assert result["release_executed"] is False
