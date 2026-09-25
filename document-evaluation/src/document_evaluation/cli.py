from __future__ import annotations

import argparse
from pathlib import Path

from .engine import EvaluationContext, EvaluationEngine


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Governed engineering document evaluation")
    p.add_argument("datasheet", type=Path)
    p.add_argument(
        "--reference-registry",
        type=Path,
        default=Path("datacenter/ENGINEERING_REFERENCE_REGISTRY.json"),
    )
    return p


def main() -> int:
    args = parser().parse_args()
    result = EvaluationEngine().evaluate_context(
        EvaluationContext(
            datasheet_path=args.datasheet,
            reference_registry_path=args.reference_registry,
        )
    )
    print(f"RESULT: {result.status.value}")
    for error in result.errors:
        print(f"- {error}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
