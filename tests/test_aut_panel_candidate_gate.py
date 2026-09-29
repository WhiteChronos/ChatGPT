from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "candidate_gate", ROOT / "pipeline/aut_panel_candidate_gate.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def base_manifest():
    return {
        "candidate_id": "CAND-1",
        "qa_status": "PASS",
        "deterministic_status": "PASS",
        "blocking_holds": [],
        "source_hashes": {"li": "a" * 64},
        "rollback_target": "R02",
        "release_executed": False,
        "auto_merge": False,
        "production_plc_download": False,
        "artifact_hashes": {"manifest": "b" * 64},
    }


def test_ci_pass_without_human_approval_remains_candidate_only():
    gate = load_module()
    out = gate.evaluate_candidate(base_manifest())
    assert out["status"] == "CANDIDATE_READY_FOR_HUMAN_REVIEW"
    assert out["release_executed"] is False
    assert out["human_release_required"] is True


def test_forbidden_release_side_effects_are_rejected():
    gate = load_module()
    for key in ("release_executed", "auto_merge", "production_plc_download"):
        manifest = base_manifest()
        manifest[key] = True
        assert gate.evaluate_candidate(manifest)["status"] == "REPROVADO"


def test_missing_provenance_or_rollback_holds_candidate():
    gate = load_module()
    manifest = base_manifest()
    manifest["source_hashes"] = {}
    assert gate.evaluate_candidate(manifest)["status"] == "HOLD"
    manifest = base_manifest()
    manifest["rollback_target"] = ""
    assert gate.evaluate_candidate(manifest)["status"] == "HOLD"


def test_valid_human_approval_returns_authorization_artifact_only():
    gate = load_module()
    approval = {
        "approval_id": "APR-1",
        "human_approved": True,
        "approver": "engineer",
        "approved_at": "2026-09-28T22:00:00-03:00",
        "reference": "review",
    }
    out = gate.evaluate_candidate(base_manifest(), approval)
    assert out["status"] == "RELEASE_AUTHORIZED_BY_HUMAN"
    assert out["release_executed"] is False
    assert out["approval_record_id"] == "APR-1"
