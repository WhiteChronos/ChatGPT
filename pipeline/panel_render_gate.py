#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ALLOWED_SURFACES = {"door", "backplate", "din", "enclosure", "other"}
OFFICIAL_GEOMETRY_SOURCE = "OFFICIAL_MANUFACTURER_DIMENSIONAL_DRAWING"


class RenderGateError(RuntimeError):
    pass


def _positive_dims(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    return all(isinstance(value.get(k), (int, float)) and value[k] > 0 for k in ("width", "height", "depth"))


def _rotated_dims(dims: dict[str, float], orientation: int) -> tuple[float, float, float]:
    if orientation % 180 == 90:
        return (float(dims["height"]), float(dims["width"]), float(dims["depth"]))
    return (float(dims["width"]), float(dims["height"]), float(dims["depth"]))


def _close(a: float, b: float, tolerance: float = 0.01) -> bool:
    if a == b:
        return True
    scale = max(abs(a), abs(b), 1.0)
    return abs(a - b) / scale <= tolerance


def validate_render_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    holds: list[str] = []

    bom_counts = manifest.get("bom_counts")
    instances = manifest.get("physical_instances")
    views = manifest.get("view_representations")
    if not isinstance(bom_counts, dict):
        errors.append("bom_counts missing or invalid")
        bom_counts = {}
    if not isinstance(instances, list):
        errors.append("physical_instances missing or invalid")
        instances = []
    if not isinstance(views, list):
        errors.append("view_representations missing or invalid")
        views = []

    px_per_mm = manifest.get("px_per_mm")
    if not isinstance(px_per_mm, (int, float)) or px_per_mm <= 0:
        errors.append("common px_per_mm must be positive")

    ids: set[str] = set()
    physical_keys: set[str] = set()
    actual_counts: Counter[str] = Counter()
    instance_by_id: dict[str, dict[str, Any]] = {}

    for item in instances:
        if not isinstance(item, dict):
            errors.append("physical instance is not an object")
            continue
        iid = str(item.get("instance_id") or "")
        catalog = str(item.get("catalog_id") or "")
        pkey = str(item.get("physical_instance_key") or iid)
        surface = str(item.get("mounting_surface") or "")
        cls = str(item.get("component_class") or "")
        official = item.get("official_dimensions_mm")
        layout = item.get("layout_dimensions_mm")
        source = item.get("geometry_source")
        orientation = int(item.get("orientation_deg") or 0)

        if not iid or iid in ids:
            errors.append(f"duplicate or missing instance_id: {iid}")
        ids.add(iid)
        instance_by_id[iid] = item

        if not pkey or pkey in physical_keys:
            errors.append(f"duplicate physical_instance_key: {pkey}")
        physical_keys.add(pkey)

        if not catalog:
            errors.append(f"{iid}: missing catalog_id")
        else:
            actual_counts[catalog] += 1

        if surface not in ALLOWED_SURFACES:
            errors.append(f"{iid}: invalid mounting_surface {surface}")

        if source != OFFICIAL_GEOMETRY_SOURCE:
            holds.append(f"{iid}: geometry source is not official manufacturer dimensional drawing")

        if not _positive_dims(official):
            holds.append(f"{iid}: official dimensions incomplete")
            continue
        if not _positive_dims(layout):
            errors.append(f"{iid}: layout dimensions incomplete")
            continue

        expected = _rotated_dims(official, orientation)
        observed = (float(layout["width"]), float(layout["height"]), float(layout["depth"]))
        if not all(_close(a, b) for a, b in zip(expected, observed)):
            errors.append(f"{iid}: layout dimensions do not match official dimensions/orientation")

        if cls == "HMI" and surface != "door":
            errors.append(f"{iid}: HMI must be mounted on door only")

    expected_counts = {str(k): int(v) for k, v in bom_counts.items()}
    if dict(actual_counts) != expected_counts:
        errors.append(f"physical instance counts {dict(actual_counts)} differ from BOM {expected_counts}")

    hmis = [x for x in instances if isinstance(x, dict) and x.get("component_class") == "HMI"]
    if len(hmis) != 1:
        errors.append(f"exactly one physical HMI required, found {len(hmis)}")

    for view in views:
        if not isinstance(view, dict):
            errors.append("view representation is not an object")
            continue
        iid = str(view.get("instance_id") or "")
        if iid not in instance_by_id:
            errors.append(f"view references unknown physical instance {iid}")
            continue
        role = str(view.get("representation_role") or "")
        if role not in {"front", "side", "backside", "internal", "external"}:
            errors.append(f"{iid}: invalid representation_role {role}")
        if instance_by_id[iid].get("component_class") == "HMI" and role == "internal":
            errors.append(f"{iid}: HMI internal representation would imply a duplicated device; use backside for the same door instance")

    cable = manifest.get("cable_exit") or {}
    actual = cable.get("actual_clearance_mm")
    required = cable.get("required_clearance_mm")
    if not isinstance(actual, (int, float)) or not isinstance(required, (int, float)):
        holds.append("cable exit clearance not quantified")
    elif actual < required:
        holds.append(f"cable exit clearance {actual} mm is below required {required} mm")
    if cable.get("bend_radius_validated") is not True:
        holds.append("bend radius not validated")
    if cable.get("gland_access_validated") is not True:
        holds.append("cable gland access not validated")

    if errors:
        status = "REPROVADO"
    elif holds:
        status = "HOLD"
    else:
        status = "PASS"

    return {
        "status": status,
        "errors": errors,
        "holds": holds,
        "physical_instance_count": len(instances),
        "view_representation_count": len(views),
        "bom_counts": expected_counts,
        "actual_counts": dict(actual_counts),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Validate AUT panel dimensional render manifest")
    p.add_argument("manifest")
    args = p.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_render_manifest(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
