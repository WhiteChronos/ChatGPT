"""GitHub-only mode regression: no live GitLab mirror and no trust bypass."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "governance/GITLAB_CONTINGENCY_CI_POLICY.json"
SCHEMA = ROOT / "schemas/gitlab_contingency_ci.schema.json"
WORKER = ROOT / "plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py"


def test_github_only_disables_gitlab_without_claiming_it_was_deleted():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(policy, schema)
    assert policy["authority_provider"] == "github"
    assert policy["provisioning_state"] == "DISABLED"
    assert policy["gitlab_project_id"] is None
    assert policy["gitlab_project_path"] is None
    assert policy["mirror_transport"] is None
    assert policy["active_failover"] is False
    assert policy["gitlab_merge_authority"] is False
    assert policy["gitlab_deploy_authority"] is False
    assert policy["allowed_evidence_providers"] == ["github", "local"]


def test_real_gitlab_network_mirror_is_refused_before_any_git_execution(monkeypatch, tmp_path):
    spec = importlib.util.spec_from_file_location("legacy_mirror_denial", WORKER)
    assert spec and spec.loader
    worker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(worker)

    def never_run_git(*args, **kwargs):
        raise AssertionError("GitLab is retired; no git command may execute")

    monkeypatch.setattr(worker, "_run_git", never_run_git)
    with pytest.raises(ValueError, match="[Dd]isabled"):
        worker.sync_ref(
            ROOT,
            "https://github.com/WhiteChronos/ChatGPT.git",
            "https://gitlab.com/chronoswhite-group/ChronosWhite-project.git",
            "main",
            tmp_path / "receipt.json",
            target_credential_helper="manager",
        )


def test_github_policy_remains_active_and_independent():
    github = json.loads((ROOT / "governance/GITHUB_CONTROL_PLANE_POLICY.json").read_text(encoding="utf-8"))
    assert github["ruleset"]["enforcement"] == "active"
    assert "github-control-plane-policy" in github["required_status_checks"]
    assert (ROOT / ".github/workflows/github-control-plane-policy.yml").exists()


def test_no_gitlab_mirror_workflow_is_enabled_on_main():
    assert not (ROOT / ".github/workflows/gitlab-neutral-mirror.yml").exists()


def test_disabled_policy_rejects_any_gitlab_ref_as_mirror_eligible():
    from pipeline.gitlab_contingency_policy import load_policy, classify_ref
    assert classify_ref("main", load_policy(POLICY)).eligible is False


def test_disabled_policy_rejects_retired_gitlab_provider_evidence():
    from dataclasses import replace
    from datetime import datetime, timezone
    from pipeline.ci_provider_evidence import (
        CIProviderEvidence, EvidenceDisposition, compare_provider_evidence,
        compute_provenance_sha256, validate_evidence,
    )

    now = datetime.now(timezone.utc)
    raw = CIProviderEvidence(
        provider="gitlab",
        repository_identity="chronoswhite-group/ChronosWhite-project",
        subject_sha="a" * 40,
        pipeline_or_run_id="historical-test-only",
        gate_name="historical-gate",
        result="PASS",
        timestamp=now,
        ci_config_revision="a" * 40,
        mirror_parity_status="HEALTHY",
        attempt=1,
        input_artifacts_sha256={
            "mirror-input.json": "1" * 64,
            "mirror-parity.json": "2" * 64,
            "gitlab-runtime-identity.json": "3" * 64,
            "contingency-python.json": "4" * 64,
            "contingency-broker.json": "5" * 64,
            "mirror-parity-final.json": "6" * 64,
        },
        provenance_sha256="0" * 64,
    )
    historical = replace(raw, provenance_sha256=compute_provenance_sha256(raw))

    with pytest.raises(ValueError, match="disabled"):
        validate_evidence(historical, now=now)
    for github in (None,):
        outcome = compare_provider_evidence(
            github, historical, gitlab_live_verified=True, now=now
        )
        assert outcome.disposition is EvidenceDisposition.GITLAB_EVIDENCE_INELIGIBLE
