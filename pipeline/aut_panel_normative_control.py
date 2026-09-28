#!/usr/bin/env python3
"""Controlled normative applicability resolver for AUT panels.

This module never copies normative text. It resolves metadata references from the
canonical registry, activates conditional groups from reviewed project conditions,
and fails closed whenever an applicable edition/source is not release-verified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required") from exc

RELEASE_VERIFIED_STATUSES = {
    "OFFICIAL_VERIFIED",
    "OFFICIAL_CATALOG_VERIFIED",
    "OFFICIAL_VERIFIED_TRANSITION",
}


def _index_standards(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(item.get("id")): item
        for item in registry.get("standards", [])
        if item.get("id")
    }


def _active_groups(
    profile: Mapping[str, Any],
    registry: Mapping[str, Any],
    memory: Mapping[str, Any],
) -> list[str]:
    matrix = registry.get("application_matrix") or {}
    baseline = str(profile.get("baseline_group") or "panel_general")
    groups: list[str] = [baseline]

    detected = {str(x) for x in profile.get("detected_conditions", []) if x}
    activation = ((memory.get("application_logic") or {}).get("conditional_activation") or {})

    for group, rule in activation.items():
        if group not in matrix:
            continue
        triggers = {str(x) for x in (rule or {}).get("triggers", []) if x}
        if str(group) in detected or detected.intersection(triggers):
            groups.append(str(group))

    # A project may explicitly name a registry group as a detected condition.
    for group in matrix:
        if group != baseline and str(group) in detected:
            groups.append(str(group))

    return list(dict.fromkeys(groups))


def resolve_applicable_norms(
    panel_id: str,
    panel_revision: str,
    profile: Mapping[str, Any],
    registry: Mapping[str, Any],
    memory: Mapping[str, Any],
) -> dict[str, Any]:
    """Resolve reference metadata for a panel without deciding engineering compliance."""
    if registry.get("registry_id") != "AUT-PANEL-NORMATIVE-REFERENCES-V1":
        raise ValueError("NORMATIVE_REGISTRY_ID_INVALID")
    if memory.get("registry_path") != "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml":
        raise ValueError("NORMATIVE_MEMORY_LINK_INVALID")

    matrix = registry.get("application_matrix") or {}
    index = _index_standards(registry)
    active_groups = _active_groups(profile, registry, memory)

    ids: list[str] = []
    for group in active_groups:
        group_data = matrix.get(group) or {}
        for ref_id in group_data.get("always_review", []) or group_data.get("activate", []):
            ref_id = str(ref_id)
            if ref_id not in ids:
                ids.append(ref_id)

    missing = [ref_id for ref_id in ids if ref_id not in index]
    if missing:
        raise ValueError(f"NORMATIVE_REFERENCE_MISSING:{','.join(missing)}")

    references: list[dict[str, Any]] = []
    hold_reasons: list[str] = []
    for ref_id in ids:
        item = index[ref_id]
        record = {
            "id": ref_id,
            "reference": item.get("reference"),
            "title": item.get("title"),
            "publisher": item.get("publisher"),
            "jurisdiction": item.get("jurisdiction"),
            "category": item.get("category"),
            "applicability": item.get("applicability"),
            "use_in_elaboration": item.get("use_in_elaboration"),
            "mandatory_when": item.get("mandatory_when"),
            "source_status": item.get("source_status"),
            "official_url": item.get("official_url"),
            "registry_verified_at": item.get("verified_at"),
            "applicability_decision": "REVIEW_REQUIRED",
        }
        references.append(record)
        if str(item.get("source_status") or "") not in RELEASE_VERIFIED_STATUSES:
            hold_reasons.append(f"UNVERIFIED_APPLICABLE_EDITION:{ref_id}")

    profile_status = str(profile.get("applicability_status") or "")
    if profile_status not in {"REVIEWED", "VALIDATED"}:
        hold_reasons.append(f"NORMATIVE_APPLICABILITY_REVIEW_REQUIRED:{profile_status or 'MISSING'}")

    return {
        "schema_version": "1.0",
        "panel_id": panel_id,
        "panel_revision": panel_revision,
        "registry_id": registry.get("registry_id"),
        "normative_memory_id": memory.get("memory_id"),
        "resolved_groups": active_groups,
        "detected_conditions": list(profile.get("detected_conditions", [])),
        "references": references,
        "hold_reasons": list(dict.fromkeys(hold_reasons)),
        "status": "HOLD" if hold_reasons else "VALIDATED",
        "release_rule": "REVERIFY_APPLICABLE_REFERENCES_WITH_OFFICIAL_SOURCE_AND_TWO_VALIDATORS",
    }


def write_normative_manifest(
    project: Mapping[str, Any],
    registry: Mapping[str, Any],
    memory: Mapping[str, Any],
    output: Path,
) -> dict[str, Any]:
    meta = project.get("project") or {}
    panel_id = str(meta.get("id") or "")
    revision = str(meta.get("revision") or "")
    profile = project.get("normative_profile") or {}
    if not panel_id or not revision:
        raise ValueError("PROJECT_ID_OR_REVISION_MISSING")
    if not profile:
        raise ValueError("NORMATIVE_PROFILE_MISSING")

    result = resolve_applicable_norms(panel_id, revision, profile, registry, memory)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"INVALID_YAML_ROOT:{path}")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"INVALID_JSON_ROOT:{path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--registry", default="datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml")
    parser.add_argument("--memory", default="memory/AUT_PANEL_NORMATIVE_MEMORY.yaml")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        result = write_normative_manifest(
            _load_json(Path(args.project)),
            _load_yaml(Path(args.registry)),
            _load_yaml(Path(args.memory)),
            Path(args.output),
        )
        print(json.dumps({"status": result["status"], "output": args.output}, ensure_ascii=False))
        return 0 if result["status"] == "VALIDATED" else 3
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"HOLD: {exc}")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
