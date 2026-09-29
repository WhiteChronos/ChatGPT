#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from pipeline.aut_panel_cache import ContentAddressedCache
from pipeline.aut_panel_handoff import build_handoff
from pipeline.context_manifest import build_context_manifest


def _load_mapping(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"mapping expected: {path}")
    return data


def _write_mapping(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".yaml", ".yml"}:
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = root / cache_dir
    manifest = build_context_manifest(
        root,
        task_id=args.task_id,
        intent=args.intent,
        panel_id=args.panel,
        agent_version=args.agent_version,
        hints=args.hint,
        cache_dir=cache_dir,
    )
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    _write_mapping(output, manifest)
    print(json.dumps({
        "status": "PASS",
        "manifest": str(output),
        "agent": manifest["agent"],
        "route_mode": manifest["route"]["mode"],
        "cache_status": manifest["cache"]["status"],
        "blocking_holds": [h["hold_id"] for h in manifest["holds"] if h.get("blocking")],
    }, ensure_ascii=False))
    return 0


def cmd_cache_store(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    manifest = _load_mapping(Path(args.manifest))
    result = _load_mapping(Path(args.result))
    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = root / cache_dir
    cache = ContentAddressedCache(cache_dir)
    path = cache.store(
        key=str(manifest["cache"]["key"]),
        material=dict(manifest["cache"]["material"]),
        result=result,
        metadata={
            "task_id": manifest.get("task_id"),
            "panel_id": manifest.get("panel_id"),
            "panel_revision": manifest.get("panel_revision"),
            "agent": manifest.get("agent"),
        },
    )
    print(json.dumps({"status": "PASS", "cache_path": str(path)}, ensure_ascii=False))
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    data = _load_mapping(Path(args.input))
    payload = build_handoff(
        task_id=str(data["task_id"]),
        from_agent=str(data["from"]),
        to_agent=str(data["to"]),
        panel=str(data["panel"]),
        revision=str(data["revision"]),
        status=str(data["status"]),
        outputs=list(data.get("outputs") or []),
        validated_facts=list(data.get("validated_facts") or []),
        source_refs=list(data.get("source_refs") or []),
        holds=list(data.get("holds") or []),
        next_action=str(data["next_action"]),
    )
    output = Path(args.output)
    _write_mapping(output, payload)
    print(json.dumps({"status": "PASS", "handoff": str(output), "handoff_id": payload["handoff_id"]}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AUT Panel Fast Context CLI")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("bootstrap", help="Route task and build a panel-scoped context manifest")
    b.add_argument("--root", default=".")
    b.add_argument("--task-id", required=True)
    b.add_argument("--intent", required=True)
    b.add_argument("--panel", required=True, choices=["PN-AUT-01", "PN-AUT-02"])
    b.add_argument("--agent-version", default="AUT-PANEL-FAST-CONTEXT-V1")
    b.add_argument("--hint", action="append", default=[])
    b.add_argument("--cache-dir", default=".cache/aut_panel")
    b.add_argument("--output", required=True)
    b.set_defaults(func=cmd_bootstrap)

    c = sub.add_parser("cache-store", help="Store an agent result under the manifest SHA256 cache key")
    c.add_argument("--root", default=".")
    c.add_argument("--manifest", required=True)
    c.add_argument("--result", required=True)
    c.add_argument("--cache-dir", default=".cache/aut_panel")
    c.set_defaults(func=cmd_cache_store)

    h = sub.add_parser("handoff", help="Build and validate a structured agent handoff")
    h.add_argument("--input", required=True)
    h.add_argument("--output", required=True)
    h.set_defaults(func=cmd_handoff)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
