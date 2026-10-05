from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.capability_adapter import CapabilityAdapter, ErrorMapping
from runtime.schema import validate_schema_subset


def _adapter(**overrides) -> dict[str, object]:
    data: dict[str, object] = {
        "schema_version": 2,
        "record_type": "capability_adapter",
        "adapter_id": "test-search-v1-v2",
        "version": "1.0.0",
        "implementation_provider_id": "test-adapter-provider",
        "implementation_version": "1.0.0",
        "source_contract_id": "capability://demo/search",
        "source_version": "1.0.0",
        "target_contract_id": "capability://demo/search",
        "target_version": "2.0.0",
        "transformation": "Translate search request v1 into v2 and map the response back.",
        "lossiness": "LOSSLESS",
        "information_loss": [],
        "unsupported_cases": [],
        "error_mapping": [{"source_error": "NOT_FOUND", "target_error": "MISSING"}],
        "conformance_tests": ["tests/contracts/search_adapter_v1_v2.py"],
        "extensions": {},
    }
    data.update(overrides)
    return data


def test_adapter_schema_accepts_lossless_record():
    schema = json.loads((REPO / "registry/capabilities/v2/adapter.schema.json").read_text())
    validate_schema_subset(_adapter(), schema)


def test_adapter_model_accepts_lossless_with_no_declared_loss():
    adapter = CapabilityAdapter(
        adapter_id="test-search-v1-v2",
        version="1.0.0",
        implementation_provider_id="test-adapter-provider",
        implementation_version="1.0.0",
        source_contract_id="capability://demo/search",
        source_version="1.0.0",
        target_contract_id="capability://demo/search",
        target_version="2.0.0",
        transformation="Translate v1 to v2",
        lossiness="LOSSLESS",
        information_loss=(),
        unsupported_cases=(),
        error_mapping=(ErrorMapping("NOT_FOUND", "MISSING"),),
        conformance_tests=("tests/contracts/search_adapter_v1_v2.py",),
        extensions={},
    )
    assert adapter.lossiness == "LOSSLESS"


def test_adapter_model_accepts_lossy_with_declared_loss():
    adapter = CapabilityAdapter(
        adapter_id="test-search-v1-v2",
        version="1.0.0",
        implementation_provider_id="test-adapter-provider",
        implementation_version="1.0.0",
        source_contract_id="capability://demo/search",
        source_version="1.0.0",
        target_contract_id="capability://demo/search",
        target_version="2.0.0",
        transformation="Drop unsupported ranking hints",
        lossiness="LOSSY",
        information_loss=("ranking_hint",),
        unsupported_cases=(),
        error_mapping=(),
        conformance_tests=("tests/contracts/search_adapter_v1_v2.py",),
        extensions={},
    )
    assert adapter.information_loss == ("ranking_hint",)


def _model(**overrides) -> CapabilityAdapter:
    data = {
        "adapter_id": "test-search-v1-v2",
        "version": "1.0.0",
        "implementation_provider_id": "test-adapter-provider",
        "implementation_version": "1.0.0",
        "source_contract_id": "capability://demo/search",
        "source_version": "1.0.0",
        "target_contract_id": "capability://demo/search",
        "target_version": "2.0.0",
        "transformation": "Translate v1 to v2",
        "lossiness": "LOSSLESS",
        "information_loss": (),
        "unsupported_cases": (),
        "error_mapping": (),
        "conformance_tests": ("tests/contracts/search_adapter_v1_v2.py",),
        "extensions": {},
    }
    data.update(overrides)
    return CapabilityAdapter(**data)


def test_lossless_adapter_rejects_declared_information_loss():
    with pytest.raises(ValueError, match="LOSSLESS"):
        _model(information_loss=("field",))


def test_lossy_adapter_requires_declared_information_loss():
    with pytest.raises(ValueError, match="LOSSY"):
        _model(lossiness="LOSSY", information_loss=())


def test_adapter_rejects_exact_self_loop():
    with pytest.raises(ValueError, match="self-loop"):
        _model(target_version="1.0.0")


@pytest.mark.parametrize(
    ("field", "value"),
    [("adapter_id", "Bad Adapter"), ("version", "v1")],
)
def test_adapter_rejects_malformed_identity(field, value):
    with pytest.raises(ValueError):
        _model(**{field: value})
