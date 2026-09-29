from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_candidate_revision_tables_and_schema_exist(tmp_path):
    dbmod = load_module("aut_panel_db_candidate_contract", "pipeline/aut_panel_db.py")
    db = tmp_path / "aut_panel.sqlite3"
    dbmod.init_db(db)

    with sqlite3.connect(db) as conn:
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "candidate_revisions" in tables
        assert "candidate_revision_changes" in tables

        candidate_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(candidate_revisions)")
        }
        assert {
            "candidate_id",
            "panel_id",
            "source_revision",
            "candidate_revision",
            "status",
            "trigger_type",
            "created_at",
            "rollback_target",
        }.issubset(candidate_cols)

        change_cols = {
            row[1] for row in conn.execute("PRAGMA table_info(candidate_revision_changes)")
        }
        assert {
            "change_id",
            "candidate_id",
            "change_type",
            "path",
            "before_json",
            "after_json",
            "evidence_json",
            "invalidates_json",
        }.issubset(change_cols)

    schema_path = ROOT / "schemas/aut_panel_candidate_revision_v1.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert {
        "candidate_id",
        "panel_id",
        "source_revision",
        "candidate_revision",
        "status",
        "trigger",
        "canonical_inputs",
        "rollback_target",
        "changes",
    }.issubset(required)


def test_candidate_schema_requires_append_only_change_records():
    schema = json.loads(
        (ROOT / "schemas/aut_panel_candidate_revision_v1.schema.json").read_text(encoding="utf-8")
    )
    change = schema["properties"]["changes"]["items"]
    assert {
        "change_id",
        "change_type",
        "path",
        "before",
        "after",
        "evidence",
        "invalidates",
    }.issubset(set(change["required"]))
    assert schema["properties"]["historical_source_mutation_allowed"]["const"] is False


def seed_panel(dbmod, db, revision="R02"):
    with dbmod.connect(db) as conn:
        conn.execute(
            "INSERT INTO panels(panel_id,revision,title,engineering_status,created_at) VALUES (?,?,?,?,?)",
            ("PN-AUT-01", revision, "Panel", "HOLD", "2026-09-28T00:00:00+00:00"),
        )


def panel_snapshot(dbmod, db):
    with dbmod.connect(db) as conn:
        return tuple(
            conn.execute(
                "SELECT * FROM panels WHERE panel_id='PN-AUT-01' AND revision='R02'"
            ).fetchone()
        )


def test_create_candidate_preserves_source_and_creates_unique_revisions(tmp_path):
    dbmod = load_module("dbsvc", "pipeline/aut_panel_db.py")
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    seed_panel(dbmod, db)
    svc = load_module("candidate", "pipeline/aut_panel_candidate_revision.py")
    before = panel_snapshot(dbmod, db)
    first = svc.create_candidate(
        db,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type": "CAPACITY"},
        canonical_inputs={"li": "abc"},
    )
    second = svc.create_candidate(
        db,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type": "CAPACITY"},
        canonical_inputs={"li": "abc"},
    )
    assert panel_snapshot(dbmod, db) == before
    assert first["candidate_id"] != second["candidate_id"]
    assert first["candidate_revision"] != second["candidate_revision"]
    assert first["rollback_target"] == "R02"


def test_apply_change_is_append_only_and_records_invalidations(tmp_path):
    dbmod = load_module("dbsvc2", "pipeline/aut_panel_db.py")
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    seed_panel(dbmod, db)
    svc = load_module("candidate2", "pipeline/aut_panel_candidate_revision.py")
    cand = svc.create_candidate(
        db,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type": "CAPACITY"},
        canonical_inputs={"li": "abc"},
    )
    result = svc.apply_change(
        db,
        candidate_id=cand["candidate_id"],
        change={
            "change_type": "ENCLOSURE_CHANGE",
            "path": "panel.enclosure",
            "before": {"model": "A"},
            "after": {"model": "B"},
            "evidence": {"ref": "REF-001"},
            "invalidates": ["LAYOUT", "RENDER_IMAGE", "QA"],
        },
    )
    assert result["invalidates"] == ["LAYOUT", "RENDER_IMAGE", "QA"]
    with dbmod.connect(db) as conn:
        rows = conn.execute(
            "SELECT change_type,path,before_json,after_json,invalidates_json "
            "FROM candidate_revision_changes WHERE candidate_id=?",
            (cand["candidate_id"],),
        ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "ENCLOSURE_CHANGE"


def test_invalid_change_writes_nothing(tmp_path):
    import pytest

    dbmod = load_module("dbsvc3", "pipeline/aut_panel_db.py")
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    seed_panel(dbmod, db)
    svc = load_module("candidate3", "pipeline/aut_panel_candidate_revision.py")
    cand = svc.create_candidate(
        db,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type": "CAPACITY"},
        canonical_inputs={"li": "abc"},
    )
    with pytest.raises(ValueError):
        svc.apply_change(db, candidate_id=cand["candidate_id"], change={"path": "x"})
    with dbmod.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM candidate_revision_changes").fetchone()[0] == 0


def test_rollback_candidate_marks_abandoned_without_deleting_history(tmp_path):
    dbmod = load_module("dbsvc4", "pipeline/aut_panel_db.py")
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    seed_panel(dbmod, db)
    svc = load_module("candidate4", "pipeline/aut_panel_candidate_revision.py")
    cand = svc.create_candidate(
        db,
        panel_id="PN-AUT-01",
        source_revision="R02",
        trigger={"type": "CAPACITY"},
        canonical_inputs={"li": "abc"},
    )
    svc.apply_change(
        db,
        candidate_id=cand["candidate_id"],
        change={
            "change_type": "LAYOUT_CHANGE",
            "path": "layout",
            "before": {},
            "after": {"x": 1},
            "evidence": {},
            "invalidates": ["RENDER_IMAGE", "QA"],
        },
    )
    out = svc.rollback_candidate(
        db, candidate_id=cand["candidate_id"], reason="test rollback"
    )
    assert out["status"] == "ABANDONED"
    with dbmod.connect(db) as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM candidate_revision_changes"
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT status FROM candidate_revisions WHERE candidate_id=?",
            (cand["candidate_id"],),
        ).fetchone()[0] == "ABANDONED"
