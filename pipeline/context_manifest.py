#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from pipeline.aut_panel_router import route_intent
from pipeline.aut_panel_normative_control import (
    merge_normative_registries,
    resolve_applicable_norms,
)

CORE_INPUTS = (
    "governance/golden_rules.yaml",
    "pipeline/pipeline.yaml",
    "datacenter/datacenter.yaml",
    "datasheet/datasheet.yaml",
    "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml",
    "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml",
    "memory/AUT_PANEL_NORMATIVE_MEMORY.yaml",
    "datacenter/LI_MATERIAL_CONTROL.json",
    "memory/LI_MATERIAL_CONTROL_MEMORY.yaml",
    "configs/layout_optimizer_v1.yaml",
    "prompts/PROMPT_MASTER_AUT_PANEL_GITHUB_CODEX_V1.md",
    "context/AUT_PANEL_CONTEXT_MANIFEST_V1.yaml",
)

AGENT_INPUTS = {
    "AUTOMATION_IO": ("pipeline/aut_panel_learning.py",),
    "LI_BOM": ("datacenter/LI_MATERIAL_CONTROL.json",),
    "LAYOUT_OPTIMIZER": ("configs/layout_optimizer_v1.yaml",),
    "NORMATIVE": (
        "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml",
        "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml",
        "pipeline/aut_panel_normative_control.py",
    ),
    "EVOLUTION_PROPOSER": ("pipeline/evolution_engine.py",),
}

PANEL_BOM_CANDIDATES = (
    "bom/{panel}_BOM.json",
    "bom/{panel}.json",
    "output/{panel}_BOM.json",
)


class ContextBuildError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def sha256_object(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ContextBuildError(f"invalid mapping: {path}")
    return data


def _require_file(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        raise ContextBuildError(f"required canonical input missing: {relative}")
    return path


def _canonical_entry(root: Path, relative: str, role: str, authority: str) -> dict[str, str]:
    path = _require_file(root, relative)
    return {
        "path": relative,
        "sha256": sha256_file(path),
        "role": role,
        "authority": authority,
    }


def _panel_record(root: Path, panel_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    dc = load_yaml(_require_file(root, "datacenter/datacenter.yaml"))
    ds = load_yaml(_require_file(root, "datasheet/datasheet.yaml"))
    dc_panel = (dc.get("panels") or {}).get(panel_id)
    ds_panel = (ds.get("panels") or {}).get(panel_id)
    if not isinstance(dc_panel, dict) or not isinstance(ds_panel, dict):
        raise ContextBuildError(f"panel not registered in canonical registries: {panel_id}")
    return dc_panel, ds_panel


def _golden_rule_ids(root: Path) -> list[str]:
    golden = load_yaml(_require_file(root, "governance/golden_rules.yaml"))
    return [str(x.get("id")) for x in golden.get("required_rules", []) if x.get("id")]


def _normative_manifest(
    root: Path,
    panel_id: str,
    panel_revision: str,
    ds_panel: dict[str, Any],
) -> dict[str, Any]:
    primary = load_yaml(_require_file(root, "datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml"))
    supplement = load_yaml(_require_file(root, "datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml"))
    memory = load_yaml(_require_file(root, "memory/AUT_PANEL_NORMATIVE_MEMORY.yaml"))
    profile = ds_panel.get("normative_profile") or {}
    merged = merge_normative_registries(primary, supplement)
    return resolve_applicable_norms(
        panel_id=panel_id,
        panel_revision=panel_revision,
        profile=profile,
        registry=merged,
        memory=memory,
    )


def _find_bom_hash(root: Path, panel_id: str) -> tuple[str, str | None]:
    for pattern in PANEL_BOM_CANDIDATES:
        rel = pattern.format(panel=panel_id)
        path = root / rel
        if path.is_file():
            return sha256_file(path), rel
    return "MISSING", None


def build_context_manifest(
    root: Path,
    *,
    task_id: str,
    intent: str,
    panel_id: str,
    agent_version: str,
    hints: list[str] | None = None,
) -> dict[str, Any]:
    route = route_intent(intent, hints or ())
    dc_panel, ds_panel = _panel_record(root, panel_id)
    panel_revision = str(dc_panel.get("li_revision") or ds_panel.get("li_id") or "UNKNOWN")

    input_paths = list(CORE_INPUTS)
    li_file = str(dc_panel.get("li_file") or ds_panel.get("li_file"))
    if li_file and li_file != "None":
        input_paths.append(li_file)
    for item in AGENT_INPUTS.get(route.agent, ()):
        input_paths.append(item)

    deduped = list(dict.fromkeys(input_paths))
    canonical_inputs = [
        _canonical_entry(
            root,
            rel,
            role="panel_specific" if rel == li_file else "canonical_contract",
            authority="CANONICAL_REPOSITORY",
        )
        for rel in deduped
    ]

    norm = _normative_manifest(root, panel_id, panel_revision, ds_panel)
    norm_hash = sha256_object(norm)
    bom_hash, bom_path = _find_bom_hash(root, panel_id)
    li_hash = next((x["sha256"] for x in canonical_inputs if x["path"] == li_file), "MISSING")
    dc_hash = next(x["sha256"] for x in canonical_inputs if x["path"] == "datacenter/datacenter.yaml")

    cache_material = {
        "panel_revision": panel_revision,
        "li_hash": li_hash,
        "bom_hash": bom_hash,
        "datacenter_hash": dc_hash,
        "normative_manifest_hash": norm_hash,
        "agent_version": agent_version,
    }
    cache_key = sha256_object(cache_material)

    holds: list[dict[str, Any]] = []
    if bom_hash == "MISSING":
        holds.append({
            "hold_id": "HOLD-CACHE-BOM-MISSING",
            "reason": "BOM artifact not found; cache key uses explicit MISSING sentinel.",
            "blocking": False,
            "owner": "LI_BOM",
            "next_action": "Generate/locate canonical BOM before downstream layout/release.",
        })
    for reason in norm.get("hold_reasons", []):
        holds.append({
            "hold_id": f"HOLD-NORM-{sha256_object(reason)[:10].upper()}",
            "reason": str(reason),
            "blocking": True,
            "owner": "NORMATIVE",
            "next_action": "Review applicability/reverify official source before release.",
        })
    if route.mode != "DETERMINISTIC":
        holds.append({
            "hold_id": "HOLD-ROUTER-AMBIGUOUS",
            "reason": "No unique deterministic route.",
            "blocking": True,
            "owner": "ORCHESTRATOR",
            "next_action": "Resolve intent before write-capable execution.",
        })

    return {
        "schema_version": "1.0",
        "manifest_id": "AUT-PANEL-CONTEXT-MANIFEST-V1",
        "task_id": task_id,
        "intent": route.intent,
        "panel_id": panel_id,
        "panel_revision": panel_revision,
        "agent": route.agent,
        "route": {
            "mode": route.mode,
            "confidence": route.confidence,
            "reasons": list(route.reasons),
        },
        "canonical_inputs": canonical_inputs,
        "golden_rules": _golden_rule_ids(root),
        "normative_manifest": norm,
        "memory_scope": {
            "panel_scoped": True,
            "paths": [
                "memory/AUT_PANEL_NORMATIVE_MEMORY.yaml",
                "memory/LI_MATERIAL_CONTROL_MEMORY.yaml",
            ],
        },
        "upstream_dependencies": ["BOOTSTRAP_CONTEXT", "DATACENTER", "DATASHEET"],
        "downstream_dependencies": {
            "AUTOMATION_IO": ["LI_QUANTITY", "LOAD_BALANCE", "BOM", "LAYOUT", "QA", "RELEASE"],
            "LI_BOM": ["LOAD_BALANCE", "BOM", "LAYOUT", "QA", "RELEASE"],
            "LAYOUT_OPTIMIZER": ["RENDER_IMAGE", "QA", "MEMORY_SYNC", "RELEASE"],
        }.get(route.agent, ["QA", "MEMORY_SYNC", "RELEASE"]),
        "cache": {
            "key": cache_key,
            "status": "MISS",
            "invalidation_reason": None,
            "material": cache_material,
            "bom_path": bom_path,
        },
        "holds": holds,
        "policy": {
            "canonical_repo_wins_over_chat": True,
            "ml_advisory_only": True,
            "no_auto_merge": True,
            "human_gate_for_locked_changes": True,
        },
    }


def write_manifest(root: Path, manifest: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", default=".")
    p.add_argument("--task-id", required=True)
    p.add_argument("--intent", required=True)
    p.add_argument("--panel", required=True, choices=["PN-AUT-01", "PN-AUT-02"])
    p.add_argument("--agent-version", default="AUT-PANEL-FAST-CONTEXT-V1")
    p.add_argument("--hint", action="append", default=[])
    p.add_argument("--output", required=True)
    args = p.parse_args()

    root = Path(args.root).resolve()
    manifest = build_context_manifest(
        root,
        task_id=args.task_id,
        intent=args.intent,
        panel_id=args.panel,
        agent_version=args.agent_version,
        hints=args.hint,
    )
    out = Path(args.output)
    if not out.is_absolute():
        out = root / out
    write_manifest(root, manifest, out)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
