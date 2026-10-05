from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
MODULE = REPO / "pipeline" / "capability_registry_policy.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("capability_registry_policy", MODULE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load capability registry policy module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_new_contract_provider_and_event_files_are_allowed():
    module = _load_module()
    changes = module.parse_name_status([
        "A\tregistry/capabilities/v2/contracts/test/1.0.0.json",
        "A\tregistry/capabilities/v2/providers/test-provider/1.0.0.json",
        "A\tregistry/capabilities/v2/events/test-provider/evt-001.json",
    ])
    assert module.validate_registry_changes(changes) == ()


@pytest.mark.parametrize(
    "path",
    [
        "registry/capabilities/v2/contracts/test/1.0.0.json",
        "registry/capabilities/v2/providers/test-provider/1.0.0.json",
        "registry/capabilities/v2/events/test-provider/evt-001.json",
        "registry/capabilities/v2/adapters/test-adapter/1.0.0.json",
    ],
)
def test_modifying_existing_records_is_rejected(path):
    module = _load_module()
    changes = module.parse_name_status([f"M\t{path}"])
    violations = module.validate_registry_changes(changes)
    assert violations and "append-only" in violations[0]


def test_modifying_existing_contract_is_rejected():
    module = _load_module()
    changes = module.parse_name_status(["M\tregistry/capabilities/v2/contracts/test/1.0.0.json"])
    assert module.validate_registry_changes(changes)


def test_modifying_existing_provider_version_is_rejected():
    module = _load_module()
    changes = module.parse_name_status(["M\tregistry/capabilities/v2/providers/test-provider/1.0.0.json"])
    assert module.validate_registry_changes(changes)


def test_modifying_existing_event_is_rejected():
    module = _load_module()
    changes = module.parse_name_status(["M\tregistry/capabilities/v2/events/test-provider/evt-001.json"])
    assert module.validate_registry_changes(changes)


def test_deleting_or_renaming_accepted_record_is_rejected():
    module = _load_module()
    changes = module.parse_name_status([
        "D\tregistry/capabilities/v2/contracts/test/1.0.0.json",
        "R100\tregistry/capabilities/v2/providers/test-provider/1.0.0.json\tregistry/capabilities/v2/providers/test-provider/1.0.1.json",
    ])
    violations = module.validate_registry_changes(changes)
    assert len(violations) == 2


def test_copying_accepted_record_is_rejected():
    module = _load_module()
    changes = module.parse_name_status([
        "C100\tregistry/capabilities/v2/events/test-provider/evt-001.json\tregistry/capabilities/v2/events/test-provider/evt-002.json"
    ])
    assert module.validate_registry_changes(changes)


def test_schema_and_readme_changes_are_not_treated_as_append_only_records():
    module = _load_module()
    changes = module.parse_name_status([
        "M\tregistry/capabilities/v2/manifest.schema.json",
        "M\tregistry/capabilities/README.md",
    ])
    assert module.validate_registry_changes(changes) == ()


def test_cli_rejects_copy_of_accepted_record_from_unchanged_source(tmp_path):
    import shutil
    import subprocess
    import sys

    repo = tmp_path / "repo"
    source = repo / "registry/capabilities/v2/events/test-provider/evt-001.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"event_id":"evt-001"}\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "policy@test"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Policy Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=repo, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

    target = source.with_name("evt-002.json")
    shutil.copy2(source, target)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "copy"], cwd=repo, check=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

    policy = repo / "pipeline/capability_registry_policy.py"
    policy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MODULE, policy)

    completed = subprocess.run(
        [sys.executable, str(policy), "--base", base, "--head", head],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 1
    assert "append-only registry violation" in completed.stdout

def test_modifying_existing_adapter_is_rejected():
    module = _load_module()
    changes = module.parse_name_status([
        "M\tregistry/capabilities/v2/adapters/test-adapter/1.0.0.json"
    ])
    assert module.validate_registry_changes(changes)


def test_deleting_or_copying_existing_adapter_is_rejected():
    module = _load_module()
    changes = module.parse_name_status([
        "D\tregistry/capabilities/v2/adapters/test-adapter/1.0.0.json",
        "C100\tregistry/capabilities/v2/adapters/test-adapter/1.0.0.json\tregistry/capabilities/v2/adapters/test-adapter/1.0.1.json",
    ])
    assert len(module.validate_registry_changes(changes)) == 2

