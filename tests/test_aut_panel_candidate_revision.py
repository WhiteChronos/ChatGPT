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
