"""CI contract for curated, non-automatically activated third-party capabilities."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "whitechronos-control-plane"))
from runtime.registry import load_registry  # noqa: E402

EXPECTED = {
    "superpowers-official": {
        "source": "superpowers@openai-curated",
        "source_type": "official_plugin",
        "controller": "superpowers-controller",
        "execution_class": "LOCAL_MUTATING",
        "status": "REGISTERED_PROJECT",
        "license": "MIT",
        "mode": "OFFICIAL_PLUGIN_PREFERRED",
        "lock": "plugins/superpowers-controller/upstream.lock.json",
        "commit_path": ("upstream", "observed_sha"),
    },
    "ecc-specialists": {
        "source": "https://github.com/affaan-m/ECC.git",
        "source_type": "upstream_git",
        "controller": "ecc-controller",
        "execution_class": "LOCAL_MUTATING",
        "status": "ACTIVATION_GATED",
        "license": "MIT",
        "mode": "EXPLICIT_SPECIALIST_ONLY",
        "lock": "plugins/ecc-controller/upstream.lock.json",
        "commit_path": ("upstream", "observed_sha"),
    },
    "matt-pocock-stable": {
        "source": "plugins/matt-pocock-controller",
        "source_type": "local",
        "controller": "matt-pocock-controller",
        "execution_class": "LOCAL_MUTATING",
        "status": "REGISTERED_PROJECT",
        "license": "MIT",
        "mode": "STABLE_PROJECT_SKILLS",
        "lock": "plugins/matt-pocock-controller/upstream.lock.json",
        "commit_path": ("upstream", "observed_sha"),
    },
    "awesome-llm-apps-curated": {
        "source": "plugins/awesome-llm-apps-controller",
        "source_type": "local",
        "controller": "awesome-llm-apps-controller",
        "execution_class": "REFERENCE_ONLY",
        "status": "ACTIVATION_GATED",
        "license": "Apache-2.0",
        "mode": "READ_ONLY_CATALOG",
        "lock": "plugins/awesome-llm-apps-controller/upstream.lock.json",
        "commit_path": ("commit",),
    },
}


def _load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_exact_curated_registry_and_existing_runtime_routes():
    registry = load_registry(ROOT)
    assert tuple(registry) == (
        "github-arena", "subagent-broker", "arena-2.0", *EXPECTED
    )
    assert registry["github-arena"].runtime_probe is not None
    assert registry["subagent-broker"].runtime_probe is not None
    arena2 = registry["arena-2.0"]
    assert arena2.execution_class == "REFERENCE_ONLY"
    assert arena2.status == "ACTIVATION_GATED"
    assert arena2.mcp_servers == ()
    assert arena2.runtime_probe is None


def test_every_curated_provider_is_pinned_not_host_activated():
    registry = load_registry(ROOT)
    for identifier, expected in EXPECTED.items():
        provider = registry[identifier]
        assert provider.source == expected["source"]
        assert provider.source_type == expected["source_type"]
        assert provider.controller_plugin == expected["controller"]
        assert provider.execution_class == expected["execution_class"]
        assert provider.status == expected["status"]
        assert provider.license_status == expected["license"]
        assert provider.runtime_probe is None, identifier
        assert provider.mcp_servers == (), identifier
        assert provider.upstream is not None
        assert provider.upstream.license_status == expected["license"]
        lock = _load(expected["lock"])
        pinned = lock
        for field in expected["commit_path"]:
            pinned = pinned[field]
        assert provider.upstream.commit == pinned, identifier
        assert (ROOT / "plugins" / expected["controller"] / "SKILL.md").is_file()
        assert provider.skill_paths == (
            f"plugins/{expected['controller']}/SKILL.md",
        )


def test_selection_policy_denies_all_automatic_execution_and_credential_crossing():
    policy = _load("registry/integrations/selection-policy.json")
    assert policy["schema_version"] == "whitechronos-selective-integration/v1"
    assert policy["authority_repository"] == "WhiteChronos/ChatGPT"
    assert policy["coordination_issue"] == "https://github.com/WhiteChronos/ChatGPT/issues/95"
    assert policy["default_activation"] == "DENY"
    selected = policy["selected_capabilities"]
    assert [item["id"] for item in selected] == list(EXPECTED)
    for item in selected:
        expected = EXPECTED[item["id"]]
        assert item["mode"] == expected["mode"]
        assert item["upstream_lock"] == expected["lock"]
        assert item["requires"] == [
            "explicit_scope", "current_sha_review", "runtime_evidence"
        ]
    assert policy["security"] == {
        "auto_install": False,
        "auto_execute": False,
        "cross_provider_credentials": False,
        "automatic_external_network_calls": False,
        "automatic_merge": False,
        "automatic_deploy": False,
        "automatic_live_inference": False,
    }


def test_sensitive_services_remain_isolated_and_not_selected():
    policy = _load("registry/integrations/selection-policy.json")
    deferred = {item["id"]: item for item in policy["deferred_services"]}
    assert set(deferred) == {"typesafe-jev", "sponsoredtokens-laya"}
    assert deferred["typesafe-jev"]["tracking"] == (
        "https://github.com/WhiteChronos/ChatGPT/pull/91"
    )
    assert deferred["sponsoredtokens-laya"]["tracking"] == (
        "https://github.com/WhiteChronos/ChatGPT/issues/94"
    )
    assert all(item["status"] == "DEFERRED" for item in deferred.values())
    assert "arena-2.0" == policy["reference_only"][0]
    selected = {item["id"] for item in policy["selected_capabilities"]}
    assert selected.isdisjoint(deferred)
    assert "arena-2.0" not in selected
