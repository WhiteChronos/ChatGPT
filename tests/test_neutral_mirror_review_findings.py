"""Regression contracts for PR #78 review findings (RED before fixes)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import jsonschema
import pytest

from pipeline.ci_provider_evidence import compute_provenance_sha256, load_evidence_json, validate_evidence

ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 40


def _legacy_payload():
    from datetime import datetime, timezone
    payload = {
        "provider": "github",
        "repository_identity": "WhiteChronos/ChatGPT",
        "subject_sha": SHA,
        "pipeline_or_run_id": "legacy-123",
        "gate_name": "full-contingency",
        "result": "PASS",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ci_config_revision": SHA,
        "mirror_parity_status": "NOT_APPLICABLE",
        "attempt": 1,
        "input_artifacts_sha256": {},
    }
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["provenance_sha256"] = hashlib.sha256(body).hexdigest()
    return payload


def test_p1_historical_v1_evidence_preserves_original_hash_and_schema(tmp_path):
    payload = _legacy_payload()
    schema = json.loads((ROOT / "schemas/ci_provider_evidence.schema.json").read_text())
    jsonschema.validate(payload, schema)
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    evidence = load_evidence_json(path)
    assert compute_provenance_sha256(evidence) == payload["provenance_sha256"]
    validate_evidence(evidence)


def test_p2_worker_revision_hex_case_does_not_change_provenance():
    payload = {**_legacy_payload(), "worker_revision": "b" * 40}
    uppercase = {**payload, "worker_revision": "B" * 40}
    assert compute_provenance_sha256(payload) == compute_provenance_sha256(uppercase)


def test_p2_recovery_runbook_passes_revision_to_cli():
    body = (ROOT / "docs/runbooks/gitlab-contingency-ci.md").read_text()
    command = body.split("python plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py", 1)[1].split("```", 1)[0]
    assert "--worker-revision" in command


def test_p1_secret_bearing_runner_does_not_install_mutable_packages():
    workflow = (ROOT / ".github/workflows/gitlab-neutral-mirror.yml").read_text()
    assert "pip install" not in workflow
    assert "Install mirror dependencies" not in workflow


def test_p1_rerun_of_old_worker_is_rejected_even_when_ref_matches(monkeypatch, tmp_path):
    source = ROOT / "plugins/whitechronos-control-plane/runtime/github_neutral_mirror.py"
    spec = importlib.util.spec_from_file_location("neutral_review_regression", source)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    request = module.NeutralMirrorRequest(
        subject_ref="main",
        subject_sha=SHA,
        worker_revision=SHA,
        target_url=module.CANONICAL_TARGET_URL,
        receipt_path=tmp_path / "receipt.json",
    )
    with pytest.raises(ValueError, match="rerun|retired|attempt"):
        module.validate_trusted_worker_context(request, workflow_ref="refs/heads/main", workflow_sha=SHA, trusted_ref="refs/heads/main")


def test_p1_trusted_gitlab_config_is_independent_of_mirrored_subject():
    runbook = (ROOT / "docs/runbooks/github-neutral-mirror.md").read_text().lower()
    assert "ci/cd configuration file" in runbook
    assert "external" in runbook and "protected" in runbook
    assert "fail closed" in runbook


def test_p1_receipt_provenance_must_have_authenticity_not_only_public_digest():
    sync = (ROOT / "plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py").read_text()
    pipeline = (ROOT / ".gitlab-ci.yml").read_text()
    assert "mirror_receipt_signature" in sync
    assert "mirror_receipt_signature" in pipeline
