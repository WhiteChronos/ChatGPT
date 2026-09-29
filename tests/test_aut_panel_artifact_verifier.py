from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("artifact_verifier", ROOT / "pipeline/aut_panel_artifact_verifier.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_bundle(tmp_path: Path):
    (tmp_path / "panel.svg").write_text("<svg/>", encoding="utf-8")
    (tmp_path / "panel.png").write_bytes(b"PNGDATA")
    manifest = {
        "candidate_id": "CAND-1",
        "source_commit_sha": "1" * 40,
        "source_hashes": {"li": "a" * 64},
        "bom_counts": {"HMI": 1, "PLC": 1},
        "render_counts": {"HMI": 1, "PLC": 1},
        "qa": {"status": "PASS", "candidate_id": "CAND-1", "source_commit_sha": "1" * 40},
        "artifacts": [
            {"path": "panel.svg", "sha256": sha(tmp_path / "panel.svg")},
            {"path": "panel.png", "sha256": sha(tmp_path / "panel.png")},
        ],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def test_verify_bundle_accepts_matching_serialized_artifacts(tmp_path):
    mod = load_module(); make_bundle(tmp_path)
    out = mod.verify_bundle(tmp_path, expected_commit_sha="1" * 40, expected_candidate_id="CAND-1")
    assert out["status"] == "PASS"
    assert out["verified_artifacts"] == 2


@pytest.mark.parametrize("field,value,error", [
    ("commit", "2" * 40, "SOURCE_COMMIT_MISMATCH"),
    ("candidate", "CAND-X", "CANDIDATE_ID_MISMATCH"),
])
def test_verify_bundle_rejects_wrong_identity(tmp_path, field, value, error):
    mod = load_module(); make_bundle(tmp_path)
    kwargs = {"expected_commit_sha": "1" * 40, "expected_candidate_id": "CAND-1"}
    kwargs["expected_commit_sha" if field == "commit" else "expected_candidate_id"] = value
    out = mod.verify_bundle(tmp_path, **kwargs)
    assert out["status"] == "REPROVADO"
    assert error in out["errors"]


def test_verify_bundle_rejects_altered_artifact(tmp_path):
    mod = load_module(); make_bundle(tmp_path)
    (tmp_path / "panel.png").write_bytes(b"ALTERED")
    out = mod.verify_bundle(tmp_path, expected_commit_sha="1" * 40, expected_candidate_id="CAND-1")
    assert out["status"] == "REPROVADO"
    assert any(x.startswith("ARTIFACT_HASH_MISMATCH:panel.png") for x in out["errors"])


def test_verify_bundle_rejects_bom_render_mismatch_and_stale_qa(tmp_path):
    mod = load_module(); manifest = make_bundle(tmp_path)
    manifest["render_counts"]["HMI"] = 2
    manifest["qa"]["source_commit_sha"] = "9" * 40
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    out = mod.verify_bundle(tmp_path, expected_commit_sha="1" * 40, expected_candidate_id="CAND-1")
    assert out["status"] == "REPROVADO"
    assert "BOM_RENDER_COUNT_MISMATCH" in out["errors"]
    assert "QA_SOURCE_COMMIT_MISMATCH" in out["errors"]


def test_verify_bundle_holds_missing_source_hashes(tmp_path):
    mod = load_module(); manifest = make_bundle(tmp_path)
    manifest["source_hashes"] = {}
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    out = mod.verify_bundle(tmp_path, expected_commit_sha="1" * 40, expected_candidate_id="CAND-1")
    assert out["status"] == "HOLD"
    assert "SOURCE_HASHES_MISSING" in out["errors"]
