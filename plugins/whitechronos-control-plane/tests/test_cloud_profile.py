from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

PROFILE = REPO / "datacenter" / "WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json"


def _api():
    cloud_profile = importlib.import_module("runtime.cloud_profile")
    return cloud_profile.load_cloud_profile


def _valid_profile() -> dict:
    return {
        "schema_version": "whitechronos-codex-cloud/v1",
        "environment_name": "whitechronos-control-plane",
        "runtime_kind": "codex_cloud",
        "repositories": [
            {
                "full_name": "WhiteChronos/ChatGPT",
                "role": "consumer",
                "required": True,
            },
            {
                "full_name": "WhiteChronos/subagent-broker-runtime",
                "role": "broker",
                "required": True,
            },
        ],
        "toolchain": {
            "python_min": [3, 11],
            "node_major": 22,
            "require_git": True,
            "require_npm": True,
            "require_codex_exec": True,
            "require_codex_json": True,
            "require_codex_resume": True,
        },
        "network": {
            "mode": "explicit_allowlist",
            "allowed_hosts": [
                "registry.npmjs.org",
                "pypi.org",
                "files.pythonhosted.org",
            ],
        },
        "required_secret_names": [],
    }


def _write_profile(tmp_path: Path, payload: dict) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    (repo / "datacenter").mkdir(parents=True)
    (repo / "schemas").mkdir(parents=True)
    schema_src = REPO / "schemas" / "whitechronos_codex_cloud_environment_v1.schema.json"
    if schema_src.exists():
        (repo / "schemas" / schema_src.name).write_text(
            schema_src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    profile = repo / "datacenter" / "WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json"
    profile.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return repo, profile


def test_profile_loads_exact_initial_repositories():
    load_cloud_profile = _api()
    profile = load_cloud_profile(REPO, PROFILE)
    assert tuple(repo.full_name for repo in profile.repositories) == (
        "WhiteChronos/ChatGPT",
        "WhiteChronos/subagent-broker-runtime",
    )
    assert tuple(repo.role for repo in profile.repositories) == ("consumer", "broker")
    assert profile.runtime_kind == "codex_cloud"
    assert profile.toolchain.python_min == (3, 11)
    assert profile.toolchain.node_major == 22
    assert profile.required_secret_names == ()


def test_profile_rejects_unknown_top_level_field(tmp_path):
    load_cloud_profile = _api()
    payload = _valid_profile()
    payload["unexpected"] = True
    repo, profile = _write_profile(tmp_path, payload)
    with pytest.raises(ValueError, match=r"additional|unexpected"):
        load_cloud_profile(repo, profile)


def test_profile_rejects_secret_value_field(tmp_path):
    load_cloud_profile = _api()
    payload = _valid_profile()
    payload["secrets"] = {"OPENAI_API_KEY": "should-never-be-here"}
    repo, profile = _write_profile(tmp_path, payload)
    with pytest.raises(ValueError, match=r"additional|secrets"):
        load_cloud_profile(repo, profile)


@pytest.mark.parametrize(
    "host",
    (
        "*",
        "*.github.com",
        "https://github.com",
        "github.com/path",
        "github.com:443",
        "",
    ),
)
def test_profile_rejects_wildcard_or_url_allowed_host(tmp_path, host):
    load_cloud_profile = _api()
    payload = _valid_profile()
    payload["network"]["allowed_hosts"] = [host]
    repo, profile = _write_profile(tmp_path, payload)
    with pytest.raises(ValueError, match=r"host|allowed_hosts"):
        load_cloud_profile(repo, profile)


def test_profile_rejects_duplicate_repository_or_host(tmp_path):
    load_cloud_profile = _api()

    duplicate_repo = _valid_profile()
    duplicate_repo["repositories"].append(dict(duplicate_repo["repositories"][0]))
    repo, profile = _write_profile(tmp_path / "repo-case", duplicate_repo)
    with pytest.raises(ValueError, match=r"duplicate repository"):
        load_cloud_profile(repo, profile)

    duplicate_host = _valid_profile()
    duplicate_host["network"]["allowed_hosts"].append("pypi.org")
    repo, profile = _write_profile(tmp_path / "host-case", duplicate_host)
    with pytest.raises(ValueError, match=r"duplicate allowed host"):
        load_cloud_profile(repo, profile)


def test_profile_accepts_secret_names_only(tmp_path):
    load_cloud_profile = _api()
    payload = _valid_profile()
    payload["required_secret_names"] = ["OPENAI_API_KEY", "CODEX_ACCESS_TOKEN"]
    repo, profile = _write_profile(tmp_path, payload)
    loaded = load_cloud_profile(repo, profile)
    assert loaded.required_secret_names == ("OPENAI_API_KEY", "CODEX_ACCESS_TOKEN")


@pytest.mark.parametrize("name", ("lowercase", "9PREFIX", "BAD-NAME", "HAS SPACE"))
def test_profile_rejects_invalid_secret_names(tmp_path, name):
    load_cloud_profile = _api()
    payload = _valid_profile()
    payload["required_secret_names"] = [name]
    repo, profile = _write_profile(tmp_path, payload)
    with pytest.raises(ValueError, match=r"secret name"):
        load_cloud_profile(repo, profile)
