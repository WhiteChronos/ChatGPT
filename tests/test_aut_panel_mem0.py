from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("mem0adapter", ROOT / "pipeline/aut_panel_mem0.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_disabled_config_returns_null_backend_without_mem0_import():
    mod = load_module()
    backend = mod.build_memory_backend({"enabled": False})
    assert backend.name == "null"
    assert backend.search(query="x", panel_id="PN-AUT-01", panel_revision="R02", limit=5) == []


def test_null_backend_add_event_is_stable_noop():
    mod = load_module()
    assert mod.NullMemoryBackend().add_event({"event_id": "MEM-1"}) == "MEM-1"


def test_enabled_backend_uses_injected_memory_and_panel_metadata():
    mod = load_module()

    class Fake:
        def __init__(self):
            self.added = []

        def add(self, **kwargs):
            self.added.append(kwargs)
            return {"results": [{"id": "m1"}]}

        def search(self, *args, **kwargs):
            return {
                "results": [
                    {
                        "id": "m1",
                        "memory": "door regression",
                        "metadata": {
                            "event_id": "MEM-1",
                            "panel_id": "PN-AUT-01",
                            "panel_revision": "R02",
                        },
                    }
                ]
            }

    fake = Fake()
    backend = mod.Mem0MemoryBackend(memory=fake)
    event = {
        "event_id": "MEM-1",
        "summary": "door regression",
        "panel_id": "PN-AUT-01",
        "panel_revision": "R02",
        "event_type": "REGRESSION",
        "evidence": {"sha256": "a" * 64},
    }
    assert backend.add_event(event) == "MEM-1"
    assert fake.added[0]["metadata"]["event_id"] == "MEM-1"
    rows = backend.search(query="door", panel_id="PN-AUT-01", panel_revision="R02", limit=5)
    assert rows[0]["metadata"]["panel_id"] == "PN-AUT-01"


def _load_db_module():
    spec = importlib.util.spec_from_file_location("mem0_db", ROOT / "pipeline/aut_panel_db.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _seed_event(dbmod, db):
    with dbmod.connect(db) as conn:
        conn.execute(
            """INSERT INTO memory_events
            (event_id,agent_id,panel_id,panel_revision,event_type,event_at,summary,evidence_json,immutable_history)
            VALUES (?,?,?,?,?,?,?,?,1)""",
            (
                "MEM-1",
                "QA",
                "PN-AUT-01",
                "R02",
                "REGRESSION",
                "2026-09-28T00:00:00+00:00",
                "door regression",
                '{"sha256":"' + "a" * 64 + '"}',
            ),
        )


def test_mirror_is_idempotent_and_preserves_canonical_event(tmp_path):
    dbmod = _load_db_module()
    mod = load_module()
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    _seed_event(dbmod, db)

    class Backend:
        name = "mem0"

        def __init__(self):
            self.calls = 0

        def add_event(self, event):
            self.calls += 1
            assert event["panel_id"] == "PN-AUT-01"
            return "MEM-1"

    backend = Backend()
    first = mod.mirror_memory_event("MEM-1", db_path=db, backend=backend)
    second = mod.mirror_memory_event("MEM-1", db_path=db, backend=backend)
    assert first["status"] == "PASS"
    assert second["status"] == "ALREADY_MIRRORED"
    assert backend.calls == 1
    with dbmod.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0] == 1
        assert conn.execute("SELECT status FROM memory_mirrors").fetchone()[0] == "PASS"


def test_mem0_failure_does_not_remove_canonical_event(tmp_path):
    dbmod = _load_db_module()
    mod = load_module()
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)
    _seed_event(dbmod, db)

    class Backend:
        name = "mem0"

        def add_event(self, event):
            raise RuntimeError("offline")

    out = mod.mirror_memory_event("MEM-1", db_path=db, backend=Backend())
    assert out["status"] == "FAILED"
    with dbmod.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM memory_events").fetchone()[0] == 1
        assert conn.execute("SELECT status FROM memory_mirrors").fetchone()[0] == "FAILED"


def test_record_memory_event_optionally_mirrors_after_canonical_commit(tmp_path):
    dbmod = _load_db_module()
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)

    class Backend:
        name = "mem0"
        def __init__(self):
            self.calls = []
        def add_event(self, event):
            self.calls.append(event)
            return event["event_id"]

    backend = Backend()
    event_id = dbmod.record_memory_event(
        db,
        agent_id="QA",
        event_type="REGRESSION",
        summary="door regression",
        panel_id="PN-AUT-01",
        panel_revision="R02",
        evidence={"sha256": "a" * 64},
        mirror_backend=backend,
    )
    assert backend.calls and backend.calls[0]["event_id"] == event_id
    with dbmod.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM memory_events WHERE event_id=?", (event_id,)).fetchone()[0] == 1
        assert conn.execute("SELECT status FROM memory_mirrors WHERE event_id=?", (event_id,)).fetchone()[0] == "PASS"


def test_record_memory_event_survives_auxiliary_mirror_failure(tmp_path):
    dbmod = _load_db_module()
    db = tmp_path / "db.sqlite3"
    dbmod.init_db(db)

    class Backend:
        name = "mem0"
        def add_event(self, event):
            raise RuntimeError("offline")

    event_id = dbmod.record_memory_event(
        db,
        agent_id="QA",
        event_type="TEST",
        summary="canonical first",
        mirror_backend=Backend(),
    )
    with dbmod.connect(db) as conn:
        assert conn.execute("SELECT COUNT(*) FROM memory_events WHERE event_id=?", (event_id,)).fetchone()[0] == 1
        assert conn.execute("SELECT status FROM memory_mirrors WHERE event_id=?", (event_id,)).fetchone()[0] == "FAILED"
