from pathlib import Path

from document_evaluation.reference_registry import load_registry, validate_registry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "datacenter" / "ENGINEERING_REFERENCE_REGISTRY.json"


def test_embedded_registry_is_valid():
    assert validate_registry(load_registry(REGISTRY)) == []


def test_open_source_is_never_normative():
    data = load_registry(REGISTRY)
    data["open_source_repositories"][0]["normative"] = True
    assert any("normative must be false" in error for error in validate_registry(data))
