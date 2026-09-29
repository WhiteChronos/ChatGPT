from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_benchmark_dataset_covers_known_pn_aut_memory_failures():
    data = json.loads((ROOT / "memory/benchmark/pn_aut_memory_cases.json").read_text(encoding="utf-8"))
    cats = {c["category"] for c in data["cases"]}
    assert {
        "stale_revision", "cross_panel", "duplicate_door", "cable_entry_provenance",
        "removed_visual_blocks", "old_pass_reuse", "conflicting_instruction",
    }.issubset(cats)
    for case in data["cases"]:
        assert case["must_include_event_ids"] or case["must_exclude_event_ids"]


def test_benchmark_schema_requires_precision_fields():
    schema = json.loads((ROOT / "schemas/pn_aut_memory_benchmark_v1.schema.json").read_text(encoding="utf-8"))
    item = schema["properties"]["cases"]["items"]
    assert {
        "query", "panel_id", "panel_revision", "must_include_event_ids",
        "must_exclude_event_ids", "category",
    }.issubset(set(item["required"]))


def test_runner_scores_must_include_and_must_exclude_without_llm():
    mod = load_module("pipeline/aut_panel_memory_benchmark.py", "memory_benchmark")
    cases = [
        {
            "case_id": "ok",
            "query": "q1",
            "panel_id": "PN-AUT-01",
            "panel_revision": "R03",
            "must_include_event_ids": ["A"],
            "must_exclude_event_ids": ["B"],
            "category": "x",
        },
        {
            "case_id": "bad",
            "query": "q2",
            "panel_id": "PN-AUT-01",
            "panel_revision": "R03",
            "must_include_event_ids": ["A"],
            "must_exclude_event_ids": ["B"],
            "category": "x",
        },
    ]

    class Provider:
        def search(self, **kwargs):
            ids = ["A"] if kwargs["query"] == "q1" else ["A", "B"]
            return [{"metadata": {"event_id": event_id}} for event_id in ids]

    out = mod.run_retrieval_benchmark(cases, Provider())
    assert out["total_cases"] == 2
    assert out["passed_cases"] == 1
    assert out["active_pass_rate"] == 0.5
    assert out["llm_judge_used"] is False
    assert out["results"][1]["unexpected_event_ids"] == ["B"]
