from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GateStatus(StrEnum):
    PASS = "PASS"
    BLOCK = "BLOCK"


class Classification(StrEnum):
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    DIVERGENT = "DIVERGENT"
    NOT_VERIFIABLE = "NOT_VERIFIABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ClaimBasis(StrEnum):
    SOURCE_DERIVED = "SOURCE_DERIVED"
    INFERENCE = "INFERENCE"
    EXTERNAL_KNOWLEDGE = "EXTERNAL_KNOWLEDGE"


@dataclass(frozen=True)
class GateResult:
    name: str
    status: GateStatus
    errors: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status is GateStatus.PASS


def aggregate_gate_results(results: list[GateResult]) -> GateResult:
    errors = tuple(error for result in results for error in result.errors)
    status = GateStatus.PASS if results and all(result.passed for result in results) else GateStatus.BLOCK
    return GateResult(name="DOCUMENT_EVALUATION", status=status, errors=errors)
