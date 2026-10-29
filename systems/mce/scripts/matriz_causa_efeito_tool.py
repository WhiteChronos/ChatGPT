#!/usr/bin/env python3
"""Run MCE's three pinned GitHub-format adapters and persist an unapproved DataSheet.

This is a *pre-analysis* tool. It never edits an XLSX or grants engineering approval.
External GitHub repos are only input-format references; their code is never run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ROOT / "scripts" / "mce_system.py"
BRIDGE = ROOT / ".agents" / "skills" / "engenharia-mce-projeto" / "scripts" / "pid_bridge.py"
ALLOWED = {
    "azure": "Azure-Samples/digitization-of-piping-and-instrument-diagrams",
    "houston": "S-Houston/digitised-pid-mlops",
    "industrial": "ZzzJjt/Industrial-Control",
}
FORMAT = "mce.matriz-tool.manifest.v1"
SHEET_FORMAT = "mce.matriz-tool.datasheet.v1"
BASENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,35}\Z")
MAX_MANIFEST = 65536


def _sha(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _unique_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def _json(path: Path, limit: int = MAX_MANIFEST) -> dict:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > limit:
        raise ValueError("Missing, unsafe or oversized JSON input")
    content = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_keys,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonstandard JSON")))
    if type(content) is not dict:
        raise ValueError("Expected JSON object")
    return content


def _file_name(name: str) -> str:
    if not isinstance(name, str) or not BASENAME.fullmatch(name) or name in (".", ".."):
        raise ValueError("Unsafe source file name")
    return name


def _label(value: object) -> str:
    if not isinstance(value, str) or not (1 <= len(value.strip()) <= 160):
        raise ValueError("Document, revision and location are required")
    if any(ord(c) < 32 for c in value):
        raise ValueError("Control character in document label")
    return value.strip()


def _command(command: list[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=120, check=False)
    if completed.returncode:
        raise ValueError("Existing MCE adapter refused input (exit " + str(completed.returncode) + ")")
    return json.loads(completed.stdout)


def _state(workspace: Path) -> dict:
    # Trust the existing MCE inventory and hashes, not input-provided claims.
    from mce_system import wf
    return wf.load_state(workspace)


def _inventory_source(workspace: Path, state: dict, name: str) -> Path:
    name = _file_name(name)
    source = next((x for x in state["sources"] if x["name"] == name), None)
    if source is None:
        raise ValueError("Source is not in the canonical MCE inventory")
    path = workspace / "sources" / name
    if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError("Unsafe source file")
    if _sha(path) != source["sha256"]:
        raise ValueError("Source digest differs from canonical MCE inventory")
    return path


def _parse_manifest(manifest: dict) -> tuple[str, list[dict], str | None]:
    if set(manifest) != {"schema", "run_id", "sources", "io_source_name"}:
        raise ValueError("Unexpected manifest structure")
    if manifest["schema"] != FORMAT:
        raise ValueError("Unsupported manifest schema")
    run_id = manifest["run_id"]
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        raise ValueError("Unsafe run_id")
    sources = manifest["sources"]
    if type(sources) is not list or not 1 <= len(sources) <= 3:
        raise ValueError("Provide 1-3 GitHub-format sources")
    seen: set[str] = set()
    for item in sources:
        if type(item) is not dict or set(item) != {"adapter", "source_name", "document", "revision", "location"}:
            raise ValueError("Unexpected source declaration")
        adapter = item["adapter"]
        if not isinstance(adapter, str) or adapter not in ALLOWED or adapter in seen:
            raise ValueError("Unknown or duplicate adapter")
        seen.add(adapter)
        _file_name(item["source_name"])
        for label in ("document", "revision", "location"):
            _label(item[label])
    io_name = manifest["io_source_name"]
    if io_name is not None:
        _file_name(io_name)
        if "azure" not in seen:
            raise ValueError("I/O comparison requires the Azure topology adapter")
    return run_id, sources, io_name


def _safe_workspace(workspace: Path) -> Path:
    w = workspace.expanduser().absolute()
    if any(part.is_symlink() for part in (w, *w.parents)) or not w.is_dir():
        raise ValueError("Workspace must exist with no symlinks")
    # The existing MCE memory security boundary also bans data in its Git checkout.
    import mce_memory
    mce_memory._path(w / "state.json")
    for dirname in ("sources", "base", "output"):
        folder = w / dirname
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError("Malformed MCE workspace")
    derived = w / "derived"
    if derived.exists() and (not derived.is_dir() or derived.is_symlink()):
        raise ValueError("Unsafe derived folder")
    return w


def prepare(workspace: Path, manifest_path: Path, db: Path | None = None) -> dict:
    w = _safe_workspace(workspace)
    raw = _json(manifest_path)
    run_id, sources, io_name = _parse_manifest(raw)
    state = _state(w)
    if state.get("status") != "INVENTARIADO" or state.get("approval") is not None:
        raise ValueError("STOP: MCE already past unapproved inventory stage")
    if db is not None:
        import mce_memory
        mce_memory.verify(db)  # No auto-create and no false persistence claim.
    for item in sources:
        _inventory_source(w, state, item["source_name"])
    if io_name is not None:
        _inventory_source(w, state, io_name)
    derived = w / "derived"
    targets = {a: derived / f"MCE_{run_id}_{a}.json" for a in (x["adapter"] for x in sources)}
    if io_name is not None:
        targets["io"] = derived / f"MCE_{run_id}_io.json"
    targets["datasheet"] = derived / f"MCE_{run_id}_DATASHEET.json"
    for path in targets.values():
        if path.exists() or path.is_symlink():
            raise ValueError("Output exists: use a new run_id; no overwrite permitted")
    return {"workspace": w, "state": state, "sources": sources, "io": io_name,
            "run_id": run_id, "manifest_sha256": _sha(manifest_path), "targets": targets,
            "missing_adapters": sorted(set(ALLOWED) - {x["adapter"] for x in sources})}


def _read_bridge_result(path: Path, adapter: str, item: dict, original_sha: str) -> dict:
    result = _json(path, 15000000)
    if result.get("schema") != "mce.pid.v1" or result.get("adapter") != adapter:
        raise ValueError("Unrecognized P&ID bridge artifact")
    if result.get("eligible_for_mce_automatic") is not False or result.get("approved_safety_effects") != []:
        raise ValueError("Bridge attempted automatic engineering approval")
    if result.get("approval_status") != "AGUARDANDO_ENGENHEIRO":
        raise ValueError("Bridge produced an invalid approval state")
    src = result.get("source", {})
    if src.get("repo") != ALLOWED[adapter] or src.get("input_sha256") != original_sha:
        raise ValueError("Bridge provenance mismatch")
    doc = result.get("document", {})
    if (doc.get("document_number"), doc.get("revision"), doc.get("evidence_location")) != (
        item["document"].strip(), item["revision"].strip(), item["location"].strip()
    ):
        raise ValueError("Bridge documentation trace mismatch")
    return result


def _save_exclusive(path: Path, payload: dict) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(text)


def run(workspace: Path, manifest_path: Path, db: Path) -> dict:
    context = prepare(workspace, manifest_path, db)
    w, targets = context["workspace"], context["targets"]
    derived = w / "derived"
    derived.mkdir(exist_ok=True)
    stages = {}
    # Prevalidate ALL three formats with the existing parser before persistent writes.
    with tempfile.TemporaryDirectory(prefix="mce-stage-") as temp:
        temp_path = Path(temp)
        for item in context["sources"]:
            adapter = item["adapter"]
            source = _inventory_source(w, context["state"], item["source_name"])
            stage = temp_path / f"{adapter}.json"
            _command([sys.executable, str(BRIDGE), "import", "--adapter", adapter,
                      "--input", str(source), "--output", str(stage),
                      "--document", item["document"], "--revision", item["revision"],
                      "--location", item["location"]])
            normalized = _read_bridge_result(stage, adapter, item, _sha(source))
            stages[adapter] = {"normalized": normalized, "stage": stage}
        # Prevalidate optional I/O comparison with the Azure staged topology.
        if context["io"] is not None:
            source_io = _inventory_source(w, context["state"], context["io"])
            _command([sys.executable, str(BRIDGE), "compare-io", "--graph", str(stages["azure"]["stage"]),
                      "--io", str(source_io), "--output", str(temp_path / "io.json")])
        # Commit to the already established MCE pipeline. It records source hashes
        # and requires explicit human review in the next understand stage.
        for item in context["sources"]:
            adapter = item["adapter"]
            _command([sys.executable, str(SYSTEM), "pid-import", "--workspace", str(w),
                      "--adapter", adapter, "--source-name", item["source_name"],
                      "--document", item["document"], "--revision", item["revision"],
                      "--location", item["location"], "--output-name", targets[adapter].name])
        if context["io"] is not None:
            _command([sys.executable, str(SYSTEM), "compare-io", "--workspace", str(w),
                      "--graph-name", targets["azure"].name, "--io-name", context["io"],
                      "--output-name", targets["io"].name])
    # A report includes only provenance/counts, no raw OCR text, TAG list, or safety logic.
    current = _state(w)
    if current["status"] != "INVENTARIADO" or current.get("approval") is not None:
        raise ValueError("Canonical MCE state changed unexpectedly")
    artifacts = []
    for item in context["sources"]:
        adapter = item["adapter"]
        source = _inventory_source(w, current, item["source_name"])
        output = targets[adapter]
        normalized = _read_bridge_result(output, adapter, item, _sha(source))
        integration = next((x for x in current.get("pid_integrations", [])
                            if x["output_file"] == str(output.relative_to(w))), None)
        if integration is None or integration.get("output_sha256") != _sha(output):
            raise ValueError("Canonical MCE state does not contain hashed integration")
        if integration.get("eligible_to_edit_matrix") is not False:
            raise ValueError("Unexpected edit permission in MCE integration")
        artifacts.append({"adapter": adapter, "repository": ALLOWED[adapter],
                          "source_sha256": _sha(source), "output_sha256": _sha(output),
                          "document": item["document"], "revision": item["revision"],
                          "evidence_location": item["location"],
                          "source_name": item["source_name"], "output_name": output.name,
                          "component_candidates": len(normalized["components"]),
                          "connection_candidates": len(normalized["connections"]),
                          "ocr_observations": len(normalized["ocr_observations"]),
                          "example_only": adapter == "industrial",
                          "review_status": "PENDENTE_REVISAO_ENGENHARIA"})
    if context["io"] is not None:
        artifacts.append({"adapter": "io_compare", "repository": ALLOWED["azure"],
                          "output_name": targets["io"].name, "output_sha256": _sha(targets["io"]),
                          "review_status": "PENDENTE_REVISAO_ENGENHARIA"})
    data = {"schema": SHEET_FORMAT, "product": "MCE_INDEPENDENTE",
            "tool": "matriz-causa-efeito", "run_id": context["run_id"],
            "status": "PRE_ANALISE_PENDENTE_REVISAO", "mce_workflow_phase": current["status"],
            "template_sha256": current["template_sha256"],
            "source_manifest_sha256": current["source_manifest_sha256"],
            "input_manifest_sha256": context["manifest_sha256"],
            "sources": artifacts, "missing_adapters": context["missing_adapters"],
            "cause_effect_relations_documented": 0,
            "cause_effect_relations_approved": 0,
            "matrix_edit_authorized": False, "human_review_required": True,
            "master_workbook_modified": False, "production_complete": False,
            "next_gate": "REVISAR_FONTES_E_EXECUTAR_UNDERSTAND_COM_PID_INTEGRATION_REVIEW"}
    _save_exclusive(targets["datasheet"], data)
    # Shared MCE database: tool namespace in event metadata, no new database.
    import mce_memory
    event = mce_memory.append(db, "STATUS", "MCE_TOOL_MATRIZ_CAUSA_EFEITO",
                              {"tool": "matriz-causa-efeito", "run_id": context["run_id"],
                               "datasheet_sha256": _sha(targets["datasheet"]),
                               "integrations_count": len(context["sources"]),
                               "gate": "PRE_ANALISE_PENDENTE_REVISAO",
                               "production_complete": False},
                              reference="mce-tool/matriz-causa-efeito",
                              source_sha256=_sha(targets["datasheet"]))
    return {"product": "MCE_INDEPENDENTE", "tool": "matriz-causa-efeito",
            "status": data["status"], "datasheet": str(targets["datasheet"]),
            "datasheet_sha256": _sha(targets["datasheet"]),
            "event_seq": event["seq"], "mce_workflow_phase": current["status"],
            "human_review_required": True, "production_complete": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "run"):
        sub = commands.add_parser(command)
        sub.add_argument("--workspace", required=True, type=Path)
        sub.add_argument("--manifest", required=True, type=Path)
        sub.add_argument("--db", type=Path, required=command == "run")
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            p = prepare(args.workspace, args.manifest, args.db)
            result = {"product": "MCE_INDEPENDENTE", "tool": "matriz-causa-efeito",
                      "status": "PRECHECK_PASS", "run_id": p["run_id"],
                      "adapters": [a["adapter"] for a in p["sources"]],
                      "missing_adapters": p["missing_adapters"],
                      "memory_verified": args.db is not None, "production_complete": False}
        else:
            result = run(args.workspace, args.manifest, args.db)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError, sqlite3.Error, TypeError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"product": "MCE_INDEPENDENTE", "tool": "matriz-causa-efeito",
                          "status": "BLOCKED", "reason_type": type(exc).__name__,
                          "production_complete": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())