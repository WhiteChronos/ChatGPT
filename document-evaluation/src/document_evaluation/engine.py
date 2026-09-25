from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from .contracts import GateResult, GateStatus, aggregate_gate_results


@dataclass(frozen=True)
class EvaluationContext:
    datasheet_path: Path
    reference_registry_path: Path


class EvaluationEngine:
    """Core orchestration shell.

    Incubation v0.1 validates local structural preconditions and exposes the
    stable interface that future ingestion/evidence/agent modules will use.
    Release-critical repository gates remain delegated by the wrapper while
    this package is incubated inside the parent repository.
    """

    def load_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def validate_context(self, context: EvaluationContext) -> GateResult:
        errors: list[str] = []
        for label, path in (
            ("datasheet", context.datasheet_path),
            ("reference_registry", context.reference_registry_path),
        ):
            if not path.is_file():
                errors.append(f"{label} does not exist: {path}")
        if errors:
            return GateResult("CONTEXT", GateStatus.BLOCK, tuple(errors))

        try:
            datasheet = self.load_json(context.datasheet_path)
            registry = self.load_json(context.reference_registry_path)
        except (OSError, json.JSONDecodeError) as exc:
            return GateResult("CONTEXT", GateStatus.BLOCK, (str(exc),))

        if not isinstance(datasheet.get("project"), str) or not datasheet["project"].strip():
            errors.append("datasheet.project must be nonblank")
        if registry.get("registry_id") != "ENGINEERING_REFERENCE_REGISTRY_V1_0":
            errors.append("reference registry identity is not canonical")

        return GateResult(
            "CONTEXT",
            GateStatus.PASS if not errors else GateStatus.BLOCK,
            tuple(errors),
        )

    def evaluate_context(self, context: EvaluationContext) -> GateResult:
        return aggregate_gate_results([self.validate_context(context)])
