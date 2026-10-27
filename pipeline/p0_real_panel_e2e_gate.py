#!/usr/bin/env python3
"""Fail-closed release gate for a real AUT panel P0 end-to-end package.

The gate does not create engineering facts. It verifies that upstream controlled
engineering has already closed Step 2, Step 4, input gaps, frozen geometry and
all P0_REAL_PANEL_E2E stages, with SHA-256 linkage between artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
REQUIRED_STAGES = ("LI", "GEOMETRY", "CAD", "VIEWS", "QA")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path, missing_hold: str, invalid_hold: str, holds: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        holds.append(missing_hold)
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        holds.append(invalid_hold)
        return None
    if not isinstance(data, dict):
        holds.append(invalid_hold)
        return None
    return data


def add_identity_holds(data: dict[str, Any], project: str, panel: str, prefix: str, holds: list[str]) -> None:
    if str(data.get("project_number", "")) != project:
        holds.append(f"{prefix}_PROJECT_MISMATCH")
    if str(data.get("panel_id", "")) != panel:
        holds.append(f"{prefix}_PANEL_MISMATCH")


def evaluate(project: str, panel: str, project_control: Path, artifact_root: Path) -> dict[str, Any]:
    holds: list[str] = []
    evidence: dict[str, Any] = {
        "project_number": project,
        "panel_id": panel,
        "project_control": str(project_control),
        "artifact_root": str(artifact_root),
    }

    control = load_json(
        project_control,
        "MISSING_PROJECT_CONTROL",
        "INVALID_PROJECT_CONTROL_JSON",
        holds,
    )
    if control is not None:
        if str(control.get("project_number", "")) != project:
            holds.append("PROJECT_CONTROL_PROJECT_MISMATCH")
        canonical_panel = str(control.get("panel_id", ""))
        previous_alias = str(control.get("previous_project_alias", ""))
        if panel not in {canonical_panel, previous_alias}:
            holds.append("PROJECT_CONTROL_PANEL_MISMATCH")
        if control.get("status") != "STEP2_PANEL_DEFINITION_FROZEN":
            holds.append("STEP2_NOT_FROZEN")
        if "INVALIDATED" in str(control.get("downstream_status", "")).upper():
            holds.append("DOWNSTREAM_INVALIDATED")
        evidence["project_control_status"] = control.get("status")
        evidence["project_control_panel_id"] = canonical_panel

    gap_path = artifact_root / "INPUT_GAP_REGISTER_CURRENT.json"
    manifest_path = artifact_root / "PANEL_GEOMETRY_MANIFEST.json"
    result_path = artifact_root / "P0_REAL_PANEL_E2E_RESULT.json"

    gap = load_json(gap_path, "MISSING_INPUT_GAP_REGISTER", "INVALID_INPUT_GAP_REGISTER_JSON", holds)
    if gap is not None:
        add_identity_holds(gap, project, panel, "INPUT_GAP_REGISTER", holds)
        open_gaps = gap.get("open_gaps")
        if gap.get("status") != "CLOSED" or not isinstance(open_gaps, list) or open_gaps:
            holds.append("INPUT_GAPS_OPEN")
        evidence["input_gap_register_sha256"] = sha256_file(gap_path)
        evidence["input_gap_count"] = len(open_gaps) if isinstance(open_gaps, list) else None

    manifest = load_json(
        manifest_path,
        "MISSING_PANEL_GEOMETRY_MANIFEST",
        "INVALID_PANEL_GEOMETRY_MANIFEST_JSON",
        holds,
    )
    if manifest is not None:
        add_identity_holds(manifest, project, panel, "PANEL_GEOMETRY_MANIFEST", holds)
        if manifest.get("status") != "PANEL_GEOMETRY_MANIFEST_FROZEN":
            holds.append("PANEL_GEOMETRY_MANIFEST_NOT_FROZEN")
        if manifest.get("step4_status") != "STEP4_LI_LOAD_FROZEN":
            holds.append("STEP4_NOT_FROZEN")
        manifest_gaps = manifest.get("input_gaps")
        if not isinstance(manifest_gaps, list) or manifest_gaps:
            holds.append("MANIFEST_INPUT_GAPS_OPEN")
        assembly_hash = str(manifest.get("assembly_hash", ""))
        if not HEX64.fullmatch(assembly_hash):
            holds.append("INVALID_ASSEMBLY_HASH")

        source_refs = manifest.get("source_refs")
        if not isinstance(source_refs, list) or not source_refs:
            holds.append("MISSING_CONTROLLED_SOURCE_REFS")
        else:
            for index, ref in enumerate(source_refs, start=1):
                if not isinstance(ref, dict) or not str(ref.get("ref_id", "")).strip():
                    holds.append(f"SOURCE_REF_{index}_INVALID_ID")
                    continue
                if not HEX64.fullmatch(str(ref.get("sha256", ""))):
                    holds.append(f"SOURCE_REF_{index}_INVALID_SHA256")

        if gap is not None:
            declared_gap_sha = str(manifest.get("input_gap_register_sha256", ""))
            actual_gap_sha = sha256_file(gap_path)
            if not HEX64.fullmatch(declared_gap_sha) or declared_gap_sha.lower() != actual_gap_sha.lower():
                holds.append("MANIFEST_STALE_INPUT_GAP_REGISTER")

        evidence["manifest_sha256"] = sha256_file(manifest_path)
        evidence["assembly_hash"] = assembly_hash

    result = load_json(result_path, "MISSING_P0_REAL_PANEL_E2E_RESULT", "INVALID_P0_REAL_PANEL_E2E_RESULT_JSON", holds)
    if result is not None:
        add_identity_holds(result, project, panel, "P0_RESULT", holds)
        if result.get("status") != "PASS":
            holds.append("P0_STATUS_NOT_PASS")
        declared_holds = result.get("blocking_holds")
        if not isinstance(declared_holds, list) or declared_holds:
            holds.append("P0_DECLARED_BLOCKING_HOLDS")
        stages = result.get("stages")
        if not isinstance(stages, dict):
            holds.append("P0_STAGES_MISSING")
        else:
            for stage in REQUIRED_STAGES:
                if stages.get(stage) != "PASS":
                    holds.append(f"P0_STAGE_{stage}_NOT_PASS")
        if manifest is not None:
            declared_manifest_sha = str(result.get("manifest_sha256", ""))
            actual_manifest_sha = sha256_file(manifest_path)
            if not HEX64.fullmatch(declared_manifest_sha) or declared_manifest_sha.lower() != actual_manifest_sha.lower():
                holds.append("P0_RESULT_STALE_MANIFEST")
        evidence["p0_result_status"] = result.get("status")

    unique_holds = list(dict.fromkeys(holds))
    return {
        "gate": "P0_REAL_PANEL_E2E",
        "status": "PASS" if not unique_holds else "HOLD",
        "blocking_holds": unique_holds,
        "required_stages": list(REQUIRED_STAGES),
        "evidence": evidence,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-number", required=True)
    parser.add_argument("--panel-id", required=True)
    parser.add_argument("--project-control", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = evaluate(args.project_number, args.panel_id, args.project_control, args.artifact_root)
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(serialized, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(serialized, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
