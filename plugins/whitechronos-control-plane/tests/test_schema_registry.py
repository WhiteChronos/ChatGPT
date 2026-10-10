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
    assert tuple(registry) == (
        "github-arena",
        "subagent-broker",
        "github-connector",
        "gitlab-connector",
        "tinyfish",
    )
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



def _connection(surface: str = "connector", *, target_probe: str | None = "provider.get_target") -> dict:
    return {
        "surfaces": [surface],
        "auth_required": True,
        "safe_probe": "provider.get_identity",
        "target_probe": target_probe,
        "trusted_evidence_sources": ["provider-connector"],
        "paid_probe_forbidden": True,
        "credential_storage": "provider_managed",
    }


def test_existing_v1_descriptors_still_load_without_connection_metadata(tmp_path):
    descriptor = _valid_descriptor("legacy")
    repo = _write_temp_registry(tmp_path, [descriptor])
    loaded = load_registry(repo)["legacy"]
    assert loaded.connection is None


def test_registry_loads_github_gitlab_and_tinyfish_connection_specs():
    registry = load_registry(REPO)

    github = registry["github-connector"]
    assert github.source_type == "official_plugin"
    assert github.execution_class == "MCP_OR_CONNECTOR"
    assert github.controller_plugin == "whitechronos-control-plane"
    assert github.connection is not None
    assert github.connection.surfaces == ("connector",)
    assert github.connection.auth_required is True
    assert github.connection.safe_probe == "github.get_profile"
    assert github.connection.target_probe == "github.get_repo"
    assert github.connection.trusted_evidence_sources == ("chatgpt-github-connector",)
    assert github.connection.paid_probe_forbidden is True
    assert github.connection.credential_storage == "provider_managed"

    gitlab = registry["gitlab-connector"]
    assert gitlab.connection is not None
    assert gitlab.connection.safe_probe == "gitlab.get_current_user"
    assert gitlab.connection.target_probe == "gitlab.get_project"
    assert gitlab.connection.trusted_evidence_sources == ("chatgpt-gitlab-connector",)

    tinyfish = registry["tinyfish"]
    assert tinyfish.source_type == "official_plugin"
    assert tinyfish.execution_class == "MCP_OR_CONNECTOR"
    assert tinyfish.controller_plugin == "tinyfish-controller"
    assert tinyfish.connection is not None
    assert tinyfish.connection.surfaces == ("chatgpt_plugin",)
    assert tinyfish.connection.safe_probe == "tinyfish.get_wallet"
    assert tinyfish.connection.target_probe is None
    assert tinyfish.connection.trusted_evidence_sources == ("chatgpt-tinyfish-app",)
    assert tinyfish.connection.paid_probe_forbidden is True
    assert tinyfish.connection.credential_storage == "provider_managed"


def test_connection_schema_rejects_unknown_surface(tmp_path):
    descriptor = _valid_descriptor("bad-surface")
    descriptor["connection"] = _connection("browser_magic")
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"connection.*surfaces"):
        load_registry(repo)


def test_connection_schema_rejects_extra_properties(tmp_path):
    descriptor = _valid_descriptor("extra")
    descriptor["connection"] = _connection()
    descriptor["connection"]["token"] = "must-not-be-accepted"
    repo = _write_temp_registry(tmp_path, [descriptor])
    with pytest.raises(ValueError, match=r"connection.*token.*additional property"):
        load_registry(repo)


def test_connection_target_probe_may_be_null(tmp_path):
    descriptor = _valid_descriptor("no-target")
    descriptor["connection"] = _connection(target_probe=None)
    repo = _write_temp_registry(tmp_path, [descriptor])
    loaded = load_registry(repo)["no-target"]
    assert loaded.connection is not None
    assert loaded.connection.target_probe is None
