"""Second PR #78 review: no live/secret external actions."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys

import pytest

from pipeline.ci_provider_evidence import (
    CIProviderEvidence, EvidenceDisposition, compute_provenance_sha256,
    compare_provider_evidence, validate_evidence,
)
from pipeline.neutral_mirror_policy import load_policy, classify_ref
from pipeline.mirror_receipt_auth import verify_receipt_digest_signature

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "whitechronos-control-plane"
WORKER_SHA = "b" * 40
SUBJECT_SHA = "a" * 40
SIGNING_KEY = "synthetic-exclusively-for-tests-review-key-32-byte-material"
TARGET_URL = "https://gitlab.com/chronoswhite-group/ChronosWhite-project.git"


def module_from_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_stdlib_worker_policy_is_strict_and_ref_bounded():
    source = (ROOT / "pipeline/neutral_mirror_policy.py").read_text()
    assert "import jsonschema" not in source
    sync = (PLUGIN / "scripts/sync_gitlab_mirror.py").read_text()
    assert "from pipeline.neutral_mirror_policy import classify_ref, load_policy" in sync
    policy = load_policy(ROOT / "governance/GITLAB_CONTINGENCY_CI_POLICY.json")
    assert classify_ref("feat/review", policy).eligible
    for unsafe in ("feat/x..y", "feat/x^y", "feat/x lock", "refs/tags/main"):
        assert not classify_ref(unsafe, policy).eligible


def test_stdlib_worker_policy_rejects_privilege_escalation(tmp_path):
    raw = json.loads((ROOT / "governance/GITLAB_CONTINGENCY_CI_POLICY.json").read_text())
    raw["gitlab_merge_authority"] = True
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="authority"):
        load_policy(path)


def test_secrets_are_removed_before_first_git_probe(monkeypatch, tmp_path):
    m = module_from_file("neutral_review_runtime", PLUGIN / "runtime/github_neutral_mirror.py")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", "synthetic-gitlab-write-token-for-tests")
    monkeypatch.setenv("GITLAB_MIRROR_SIGNING_KEY", SIGNING_KEY)
    probes = []

    def observed(repo, ref):
        probes.append(ref)
        assert "GITLAB_MIRROR_TOKEN" not in os.environ
        assert "GITLAB_MIRROR_SIGNING_KEY" not in os.environ
        return WORKER_SHA if ref == "main" else SUBJECT_SHA

    def synced(*args, **kwargs):
        signer = kwargs["receipt_signer"]
        digest = "0" * 64
        assert verify_receipt_digest_signature(digest, signer(digest), SIGNING_KEY)
        return {"source_sha": SUBJECT_SHA, "target_sha": SUBJECT_SHA, "worker_revision": WORKER_SHA}

    monkeypatch.setattr(m, "_observe_source_sha", observed)
    monkeypatch.setattr(m, "_sync_ref", synced)
    request = m.NeutralMirrorRequest(
        subject_ref="feat/review", subject_sha=SUBJECT_SHA, worker_revision=WORKER_SHA,
        target_url=TARGET_URL, receipt_path=tmp_path / "receipt.json",
    )
    m.run_neutral_mirror(
        ROOT, request, workflow_ref="refs/heads/main",
        workflow_sha=WORKER_SHA, trusted_ref="refs/heads/main",
    )
    assert probes == ["main", "feat/review"]


def test_external_recovery_cli_signs_without_key_on_argv(monkeypatch, tmp_path, capsys):
    m = module_from_file("neutral_review_sync", PLUGIN / "scripts/sync_gitlab_mirror.py")
    monkeypatch.setenv("GITLAB_MIRROR_SIGNING_KEY", SIGNING_KEY)
    captured = {}
    def fake_sync(*args, **kwargs):
        captured.update(kwargs)
        return {"dry_run": False, "receipt_sha256": "0" * 64}
    monkeypatch.setattr(m, "sync_ref", fake_sync)
    monkeypatch.setattr(sys, "argv", [
        "sync_gitlab_mirror.py", "--repo-root", str(ROOT),
        "--source-url", "https://github.com/WhiteChronos/ChatGPT.git",
        "--target-url", TARGET_URL, "--ref", "main",
        "--receipt", str(tmp_path / "receipt.json"), "--worker-revision", WORKER_SHA,
        "--target-credential-helper", "manager",
    ])
    assert m.main() == 0
    digest = "1" * 64
    signature = captured["receipt_signer"](digest)
    assert verify_receipt_digest_signature(digest, signature, SIGNING_KEY)
    assert "GITLAB_MIRROR_SIGNING_KEY" not in os.environ
    assert SIGNING_KEY not in capsys.readouterr().out


def test_unsigned_network_push_fails_before_git(tmp_path):
    m = module_from_file("neutral_review_unsigned", PLUGIN / "scripts/sync_gitlab_mirror.py")
    with pytest.raises(ValueError, match="authenticated signing key"):
        m.sync_ref(
            ROOT, "https://github.com/WhiteChronos/ChatGPT.git",
            TARGET_URL, "main", tmp_path / "receipt.json", WORKER_SHA,
            target_credential_helper="manager",
        )


def test_retained_v1_gitlab_record_is_only_archival():
    now = datetime.now(timezone.utc)
    rec = CIProviderEvidence(
        provider="gitlab", repository_identity="chronoswhite-group/ChronosWhite-project",
        subject_sha=SUBJECT_SHA, pipeline_or_run_id="old", gate_name="full-contingency",
        result="PASS", timestamp=now, ci_config_revision=SUBJECT_SHA,
        mirror_parity_status="HEALTHY", attempt=1,
        input_artifacts_sha256={
            key: "1" * 64 for key in (
                "mirror-input.json", "mirror-parity.json", "gitlab-runtime-identity.json",
                "contingency-python.json", "contingency-broker.json", "mirror-parity-final.json",
            )
        },
        provenance_sha256="0" * 64, worker_revision=None, schema_version=1,
    )
    rec = replace(rec, provenance_sha256=compute_provenance_sha256(rec))
    validate_evidence(rec, now=now)
    result = compare_provider_evidence(None, rec, gitlab_live_verified=True, now=now)
    assert result.disposition is EvidenceDisposition.GITLAB_EVIDENCE_INELIGIBLE


def test_receipt_artifact_survives_wrapper_validation_failure():
    workflow = (ROOT / ".github/workflows/gitlab-neutral-mirror.yml").read_text()
    assert "always() && hashFiles('artifacts/gitlab-neutral-mirror/receipt.json')" in workflow
    assert "if-no-files-found: error" in workflow


def test_revision_environment_and_signing_key_bootstrap_documented():
    workflow = (ROOT / ".github/workflows/gitlab-neutral-mirror.yml").read_text()
    runbook = (ROOT / "docs/runbooks/github-neutral-mirror.md").read_text()
    assert "environment: gitlab-neutral-mirror-" in workflow
    assert "GITLAB_MIRROR_SIGNING_KEY" in runbook
    assert "openssl rand -hex 32" in runbook
    assert "ci_config_path" in runbook
    assert "revoke" in runbook.lower()
