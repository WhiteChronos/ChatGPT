"""Exporta datasets tabulares estáveis para Power BI ou ferramentas equivalentes."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from pipeline.comment_control_analytics import risk_score_baseline


FACT_FIELDS = [
    "project_id",
    "comment_id",
    "origin_type",
    "severity",
    "document_code",
    "revision",
    "page_or_item",
    "compiled_action",
    "status_control",
    "responsible",
    "verifier",
    "created_at",
    "verified_at",
    "reopened_count",
    "risk_score",
    "risk_model",
]


def export(records: list[dict[str, Any]], output_dir: str | Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fact_path = output_dir / "fact_comments.csv"
    with fact_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FACT_FIELDS)
        writer.writeheader()
        for r in records:
            risk = risk_score_baseline(r)
            writer.writerow(
                {
                    "project_id": r.get("project_id"),
                    "comment_id": r.get("comment_id"),
                    "origin_type": r.get("origin_type"),
                    "severity": r.get("severity"),
                    "document_code": r.get("document_code"),
                    "revision": r.get("revision"),
                    "page_or_item": r.get("page_or_item"),
                    "compiled_action": r.get("compiled_action"),
                    "status_control": r.get("status_control"),
                    "responsible": r.get("responsible"),
                    "verifier": r.get("verifier"),
                    "created_at": r.get("created_at"),
                    "verified_at": r.get("verified_at"),
                    "reopened_count": r.get("reopened_count", 0),
                    "risk_score": risk["score"],
                    "risk_model": risk["model_name"],
                }
            )

    evidence_path = output_dir / "fact_comment_evidence.csv"
    with evidence_path.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["project_id", "comment_id", "evidence_document", "evidence_revision", "evidence_location", "evidence_text"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in records:
            if r.get("evidence_text"):
                writer.writerow({k: r.get(k) for k in fields})

    return [fact_path, evidence_path]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", default="powerbi")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    records = payload.get("comments", payload if isinstance(payload, list) else [])
    for path in export(records, args.output_dir):
        print(path)
