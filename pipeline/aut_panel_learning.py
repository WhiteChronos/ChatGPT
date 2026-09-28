#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

MIN_LABELED_EXAMPLES = 25
FEATURE_SCHEMA_VERSION = "AUT-PANEL-ML-FEATURES-V1"

def fingerprint_examples(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def deterministic_risk(features: dict[str, float]) -> float:
    weights = {
        "source_uncertainty": 0.24, "lifecycle_uncertainty": 0.12, "quantity_mismatch": 0.28,
        "overlap_ratio": 0.16, "template_diff": 0.10, "unresolved_hold_ratio": 0.10,
    }
    score = 0.0
    for key, weight in weights.items():
        value = max(0.0, min(1.0, float(features.get(key, 0.0))))
        score += value * weight
    return round(min(1.0, score), 6)

def evaluate_dataset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reviewed = [r for r in rows if r.get("reviewed_by_human", True)]
    result: dict[str, Any] = {
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "dataset_fingerprint": fingerprint_examples(reviewed),
        "labeled_examples": len(reviewed),
        "minimum_required": MIN_LABELED_EXAMPLES,
        "advisory_only": True,
        "auto_apply_locked_changes": False,
    }
    if len(reviewed) < MIN_LABELED_EXAMPLES:
        result.update({"status": "LEARNING_COLD_START", "mode": "DETERMINISTIC_BASELINE",
                       "reason": "insufficient_human_reviewed_examples"})
        return result
    try:
        from river import compose, linear_model, metrics, preprocessing
    except Exception:
        result.update({"status": "HOLD", "mode": "ML_DEPENDENCY_UNAVAILABLE",
                       "reason": "install requirements-ml.txt to enable River online learning"})
        return result
    model = compose.Pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression())
    metric = metrics.Accuracy()
    usable = 0
    for row in reviewed:
        x = {k: float(v) for k, v in (row.get("features") or {}).items()}
        label = str(row.get("label", "")).lower()
        if label not in {"accepted", "rejected"} or not x:
            continue
        y = label == "rejected"
        pred = model.predict_one(x)
        if pred is not None:
            metric.update(y, pred)
        model.learn_one(x, y)
        usable += 1
    result.update({
        "status": "TRAINED" if usable >= MIN_LABELED_EXAMPLES else "HOLD",
        "mode": "RIVER_ONLINE_LOGISTIC_REGRESSION",
        "usable_examples": usable,
        "accuracy_prequential": float(metric.get()) if usable else 0.0,
        "model_persistence": "registry_metadata_only_until_human_approval",
    })
    return result

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dataset")
    args = p.parse_args()
    rows = [json.loads(line) for line in Path(args.dataset).read_text(encoding="utf-8").splitlines() if line.strip()]
    print(json.dumps(evaluate_dataset(rows), ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
