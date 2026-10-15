from pathlib import Path
import json

from document_evaluation.contracts import GateResult, GateStatus, aggregate_gate_results
from document_evaluation.engine import EvaluationContext, EvaluationEngine


def test_aggregate_is_fail_closed():
    result = aggregate_gate_results([
        GateResult("A", GateStatus.PASS),
        GateResult("B", GateStatus.BLOCK, ("blocked",)),
    ])
    assert result.status is GateStatus.BLOCK
    assert result.errors == ("blocked",)


def test_context_requires_canonical_registry(tmp_path: Path):
    datasheet = tmp_path / "project.json"
    registry = tmp_path / "registry.json"
    datasheet.write_text(json.dumps({"project": "P"}), encoding="utf-8")
    registry.write_text(json.dumps({"registry_id": "WRONG"}), encoding="utf-8")
    result = EvaluationEngine().validate_context(EvaluationContext(datasheet, registry))
    assert result.status is GateStatus.BLOCK
