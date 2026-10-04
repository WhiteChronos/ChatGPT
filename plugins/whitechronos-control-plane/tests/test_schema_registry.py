from __future__ import annotations

import copy
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.registry import load_registry

ARENA_TOOLS = (
    "arena_plan",
    "arena_cards",
    "arena_rubric",
    "arena_review_checklist",
)
BROKER_TOOLS = (
    "subagent_spawn",
    "subagent_status",
    "subagent_wait",
    "subagent_result",
    "subagent_followup",
    "subagent_list",
    "subagent_cancel",
    "subagent_cleanup",
)


def _write_temp_registry(tmp_path: Path, descriptors: list[dict]) -> Path:
    repo = tmp_path / "repo"
    reg = repo / "registry" / "integrations"
    reg.mkdir(parents=True)
    shutil.copy(REPO / "registry" / "integrations" / "schema.json", reg / "schema.json")
    names = []
    for i, descriptor in enumerate(descriptors, start=1):
        name = f"entry-{i}.json"
        (reg / name).write_text(json.dumps(descriptor, indent=2) + "\n", encoding="utf-8")
        names.append(name)
    (reg / "index.json").write_text(
        json.dumps({"schema_version": 1, "descriptors": names}, indent=2) + "\n",
        encoding="utf-8",
    )
    return repo


def _valid_descriptor(integration_id: str = "sample") -> dict:
    return {
        "schema_version": 1,
        "id": integration_id,
        "display_name": integration_id.title(),
        "source_type": "local",
        "source": f"plugins/{integration_id}",
        "license_status": "MIT",
        "execution_class": "LOCAL_READ_ONLY",
        "status": "REGISTERED_PROJECT",
        "controller_plugin": integration_id,
        "skill_paths": [],
        "mcp_servers": [integration_id],
        "runtime_probe": {
            "plugin_root": f"plugins/{integration_id}",
            "mcp_config": ".mcp.json",
            "mcp_server": integration_id,
            "expected_tools": ["sample_tool"],
            "required_for_broker_smoke": False,
        },
    }


def test_registry_loads_arena_and_broker_descriptors():
    registry = load_registry(REPO)
    assert tuple(registry) == ("github-arena", "subagent-broker")
    assert registry["github-arena"].runtime_probe is not None
    assert registry["github-arena"].runtime_probe.expected_tools == ARENA_TOOLS
    assert registry["subagent-broker"].runtime_probe is not None
    assert registry["subagent-broker"].runtime_probe.expected_tools == BROKER_TOOLS


def test_registry_rejects_duplicate_ids(tmp_path):
    first = _valid_descriptor("duplicate")
    second = copy.deepcopy(first)
    second["display_name"] = "Duplicate Again"
    repo = _write_temp_registry(tmp_path, [first, second])
    with pytest.raises(ValueError, match=r"duplicate integration id.*duplicate"):
        load_registry(repo)


def test_registry_rejects_unknown_execution_class(tmp_path):
    descriptor = _valid_descriptor("bad-class")
    descriptor["execution_class"] = "DO_WHATEVER"
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"execution_class"):
        load_registry(repo)


def test_registry_rejects_runtime_probe_outside_declared_plugin_root(tmp_path):
    descriptor = _valid_descriptor("escape")
    descriptor["runtime_probe"]["mcp_config"] = "../subagent-broker/.mcp.json"
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"runtime_probe\.mcp_config.*plugin_root"):
        load_registry(repo)
