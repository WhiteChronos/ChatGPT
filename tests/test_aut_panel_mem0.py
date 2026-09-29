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
