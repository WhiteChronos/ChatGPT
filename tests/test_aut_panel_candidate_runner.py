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
