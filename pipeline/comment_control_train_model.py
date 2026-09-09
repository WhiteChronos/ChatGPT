"""Treina modelo preditivo somente quando houver histórico suficiente.

Alvo recomendado: comentário que ultrapassou SLA, reabriu ou gerou regressão.
O treinamento é bloqueado com amostra insuficiente para evitar falsa precisão.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

MIN_ROWS = 200
MIN_POSITIVES = 30
FEATURES = [
    "severity_weight",
    "age_days_at_snapshot",
    "required_document_count",
    "reopened_count",
    "prior_document_regressions",
]


def _load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _num(row: dict[str, Any], key: str) -> float:
    value = row.get(key)
    return float(value or 0)


def train(input_csv: str | Path, output_json: str | Path) -> dict[str, Any]:
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import brier_score_loss, roc_auc_score
        from sklearn.model_selection import StratifiedKFold, cross_val_predict
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("Instale requirements-analytics.txt para treinar o modelo") from exc

    rows = _load_rows(Path(input_csv))
    if len(rows) < MIN_ROWS:
        raise ValueError(f"Amostra insuficiente: {len(rows)} < {MIN_ROWS}")

    y = [int(row.get("target_delay_or_regression") or 0) for row in rows]
    positives = sum(y)
    if positives < MIN_POSITIVES or (len(y) - positives) < MIN_POSITIVES:
        raise ValueError("Classes insuficientes para validação estatística")

    X = [[_num(row, feature) for feature in FEATURES] for row in rows]
    model = Pipeline(
        [
            ("scale", StandardScaler()),
            ("logit", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    probabilities = cross_val_predict(model, X, y, cv=cv, method="predict_proba")[:, 1]
    auc = float(roc_auc_score(y, probabilities))
    brier = float(brier_score_loss(y, probabilities))

    model.fit(X, y)
    logit = model.named_steps["logit"]
    artifact = {
        "model_name": "COMMENT_DELAY_REGRESSION_LOGIT",
        "model_version": "1.0",
        "training_rows": len(rows),
        "positive_rows": positives,
        "features": FEATURES,
        "cross_validation": {
            "folds": 5,
            "roc_auc": round(auc, 6),
            "brier_score": round(brier, 6),
        },
        "standardized_coefficients": {
            feature: round(float(value), 8)
            for feature, value in zip(FEATURES, logit.coef_[0], strict=True)
        },
        "intercept": round(float(logit.intercept_[0]), 8),
        "decision_policy": {
            "prediction_is_advisory_only": True,
            "human_review_required": True,
            "never_changes_comment_status": True,
        },
    }
    Path(output_json).write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("--output", default="comment_predictive_model.json")
    args = parser.parse_args()
    result = train(args.input_csv, args.output)
    print(json.dumps(result["cross_validation"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
