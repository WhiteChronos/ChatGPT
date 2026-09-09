"""Estatística descritiva e score preditivo baseline para comentários técnicos.

O score é heurístico, auditável e NÃO deve ser apresentado como modelo treinado
até existir histórico suficiente e validação estatística formal.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

SEVERITY_WEIGHT = {"LEVE": 0.25, "ALTO": 0.60, "GRAVE": 1.00}


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def age_days(record: dict[str, Any], now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    created = _parse_dt(record.get("created_at"))
    if not created:
        return 0.0
    end = _parse_dt(record.get("verified_at")) or now
    return max(0.0, (end - created).total_seconds() / 86400.0)


def risk_score_baseline(record: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    """Retorna probabilidade relativa 0..1 de atraso/recorrência.

    Variáveis: criticidade, idade, reabertura, multidocumento e falta de evidência.
    Coeficientes são explícitos para auditoria e posterior substituição por modelo treinado.
    """
    sev = SEVERITY_WEIGHT.get(record.get("severity"), 0.5)
    age = min(age_days(record, now) / 90.0, 1.5)
    reopen = min(float(record.get("reopened_count") or 0) / 3.0, 1.0)
    required_docs = len(record.get("required_documents") or [])
    multidoc = min(required_docs / 4.0, 1.0)
    evidence_gap = 1.0 if record.get("status_control") == "CHECKED" and not record.get("evidence_text") else 0.0

    z = -2.20 + (1.40 * sev) + (1.10 * age) + (1.25 * reopen) + (0.80 * multidoc) + (2.00 * evidence_gap)
    score = 1.0 / (1.0 + math.exp(-z))
    return {
        "model_name": "RISK_SCORE_BASELINE",
        "model_version": "1.0",
        "score": round(score, 6),
        "features": {
            "severity_weight": sev,
            "age_norm": age,
            "reopen_norm": reopen,
            "multidoc_norm": multidoc,
            "evidence_gap": evidence_gap,
        },
    }


def summarize(records: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    formal = [r for r in records if r.get("origin_type") == "FORMAL_COMMENT"]
    checked = [r for r in formal if r.get("status_control") == "CHECKED"]
    unchecked = [r for r in formal if r.get("status_control") == "UNCHECKED"]
    ages = [age_days(r, now) for r in formal]
    close_days = [age_days(r, now) for r in checked if r.get("verified_at")]
    reopens = [int(r.get("reopened_count") or 0) for r in formal]
    evidence_gaps = [r for r in checked if not r.get("evidence_text")]
    scores = [risk_score_baseline(r, now)["score"] for r in formal]

    return {
        "formal_comment_count": len(formal),
        "checked_count": len(checked),
        "unchecked_count": len(unchecked),
        "checked_rate": (len(checked) / len(formal)) if formal else 0.0,
        "severity_distribution": dict(Counter(r.get("severity") for r in formal)),
        "mean_age_days": mean(ages) if ages else 0.0,
        "median_age_days": median(ages) if ages else 0.0,
        "mean_close_days": mean(close_days) if close_days else 0.0,
        "reopen_rate": (sum(1 for x in reopens if x > 0) / len(formal)) if formal else 0.0,
        "evidence_gap_rate": (len(evidence_gaps) / len(checked)) if checked else 0.0,
        "mean_risk_score": mean(scores) if scores else 0.0,
        "high_risk_count": sum(1 for s in scores if s >= 0.70),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default="comment_analytics.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    records = payload.get("comments", payload if isinstance(payload, list) else [])
    report = summarize(records)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
