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
    assert tuple(registry) == ("github-arena", "subagent-broker", "arena-2.0")
    assert registry["github-arena"].runtime_probe is not None
    assert registry["github-arena"].runtime_probe.expected_tools == ARENA_TOOLS
    assert registry["subagent-broker"].runtime_probe is not None
    assert registry["subagent-broker"].runtime_probe.expected_tools == BROKER_TOOLS


def test_local_adapters_keep_local_runtime_sources_and_record_upstream_bindings():
    registry = load_registry(REPO)

    arena = registry["github-arena"]
    assert arena.source_type == "local"
    assert arena.source == "plugins/github-arena"
    assert arena.upstream is not None
    assert arena.upstream.repository == "https://github.com/Jakeschincariol/arena-skill.git"
    assert arena.upstream.relationship == "methodology_adaptation"
    assert arena.upstream.commit == "df07b8e518e10cdecd8cd7712d9958b6f396250e"

    broker = registry["subagent-broker"]
    assert broker.source_type == "local"
    assert broker.source == "plugins/subagent-broker"
    assert broker.upstream is not None
    assert broker.upstream.repository == "https://github.com/Shubhamsaboo/awesome-llm-apps.git"
    assert broker.upstream.relationship == "agent_ecosystem_reference"
    assert broker.upstream.commit == "4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2"


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


@pytest.mark.parametrize("commit", ["x" * 40, "a" * 39, "a" * 41])
def test_registry_rejects_malformed_upstream_commit(tmp_path, commit):
    descriptor = _valid_descriptor("bad-upstream")
    descriptor["upstream"] = {
        "repository": "https://github.com/example/project.git",
        "ref": "main",
        "commit": commit,
        "license_status": "MIT",
        "relationship": "reference",
    }
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"upstream\.commit.*40-character hexadecimal"):
        load_registry(repo)


def test_schema_version_boolean_is_not_numeric_const(tmp_path):
    descriptor = _valid_descriptor("bool-version")
    descriptor["schema_version"] = True
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"schema_version.*const"):
        load_registry(repo)


def test_schema_validator_rejects_unsupported_keyword(tmp_path):
    repo = tmp_path / "repo"
    reg = repo / "registry/integrations"
    reg.mkdir(parents=True)
    schema = json.loads((REPO / "registry/integrations/schema.json").read_text())
    schema["properties"]["id"]["pattern"] = "^[a-z]+$"
    (reg / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
    descriptor = _valid_descriptor("sample")
    (reg / "entry.json").write_text(json.dumps(descriptor), encoding="utf-8")
    (reg / "index.json").write_text(json.dumps({"schema_version":1,"descriptors":["entry.json"]}), encoding="utf-8")
    with pytest.raises(ValueError, match=r"unsupported schema keyword.*pattern"):
        load_registry(repo)


def test_arena2_external_reference_is_non_executable_and_isolated():
    registry = load_registry(REPO)
    entry = registry["arena-2.0"]
    assert entry.display_name == "ARENA 2.0 Research Curriculum"
    assert entry.source_type == "external_reference"
    assert entry.source == "https://github.com/callummcdougall/ARENA_2.0.git"
    assert entry.license_status == "UNVERIFIED"
    assert entry.execution_class == "REFERENCE_ONLY"
    assert entry.status == "ACTIVATION_GATED"
    assert entry.controller_plugin is None
    assert entry.skill_paths == ()
    assert entry.mcp_servers == ()
    assert entry.runtime_probe is None
    routing = (REPO / "runbooks" / "arena2-research-reference.md").read_text(encoding="utf-8")
    assert "e805ad8772b81fa44252ab3b7590ac614aa29376" in routing
    assert "GitHub Arena" in routing and "Subagent Broker" in routing
