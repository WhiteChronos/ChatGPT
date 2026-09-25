from copy import deepcopy
from pathlib import Path
import json

from pipeline.reference_registry_gate import validate_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datacenter" / "ENGINEERING_REFERENCE_REGISTRY.json"


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def test_canonical_registry_is_valid():
    assert validate_registry(registry()) == []


def test_open_source_cannot_be_normative():
    data = registry()
    data["open_source_repositories"][0]["normative"] = True
    assert any("normative must be false" in e for e in validate_registry(data))


def test_duplicate_ids_are_rejected():
    data = registry()
    clone = deepcopy(data["authoritative_sources"][0])
    data["authoritative_sources"].append(clone)
    assert any("duplicate registry id" in e for e in validate_registry(data))


def test_repository_must_remain_reference_only():
    data = registry()
    data["open_source_repositories"][0]["adoption_status"] = "APPROVED_DEPENDENCY"
    assert any("REFERENCE_ONLY" in e for e in validate_registry(data))
