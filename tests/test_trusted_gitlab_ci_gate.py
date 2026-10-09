"""Security gates for independently hosted GitLab CI (no provider writes)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from pipeline.trusted_gitlab_ci_gate import (
    check_configuration, verify_authenticated_receipt, GateState,
)

ROOT = Path(__file__).resolve().parents[1]
MIRROR = "chronoswhite-group/ChronosWhite-project"
TRUSTED = "chronoswhite-group/trusted-ci-verifier"
CONFIG = "ci/trusted-mirror.yml@" + TRUSTED + ":main"
SHA = "a" * 40
WORKER = "b" * 40
KEY = "test-only-high-entropy-placeholder-not-a-real-secret-000000001"


def snapshot(**changes):
    base = dict(
        id=86465539,
        path_with_namespace=MIRROR,
        ci_config_path=CONFIG,
        default_branch="bootstrap/mirror-controller",
    )
    base.update(changes)
    return base


def trusted_ref(**changes):
    base = dict(
        name="main",
        protected=True,
        commit={"id": SHA},
        project_path=TRUSTED,
        project_id=93001100,
    )
    base.update(changes)
    return base


def receipt(**changes):
    data = dict(
        schema_version=1,
        transport="neutral_worker",
        source_repository="WhiteChronos/ChatGPT",
        target_project_path=MIRROR,
        ref="main",
        pipeline_ref="main",
        source_sha=SHA,
        target_sha=SHA,
        timestamp=datetime.now(timezone.utc).isoformat(),
        worker_revision=WORKER,
    )
    data.update(changes)
    return data


def auth_data(rec):
    raw = json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()
    digest = hashlib.sha256(raw).hexdigest()
    signature = hmac.new(KEY.encode(), bytes.fromhex(digest), hashlib.sha256).hexdigest()
    return digest, signature


def api_job(**changes):
    job = dict(
        ref="main", tag=False,
        pipeline={"project_id":86465539,"sha":SHA,"source":"push","id":9781},
        commit={"id":SHA},
    )
    job.update(changes)
    return job


def test_external_config_with_protected_separate_project_is_ready_for_secretless_preflight():
    state = check_configuration(snapshot(), trusted_ref(),
        expected_project=TRUSTED, expected_revision=SHA)
    assert state is GateState.PREPARED


@pytest.mark.parametrize("bad", ["", ".gitlab-ci.yml", "ci/trusted.yml", "ci/t.yml@"+MIRROR+":main",
                                "ci/t.yml@"+TRUSTED+":latest", "https://attacker.test/a.yml"])
def test_no_mirrored_or_ambiguous_pipeline_config_is_accepted(bad):
    assert check_configuration(snapshot(ci_config_path=bad), trusted_ref(),
        expected_project=TRUSTED, expected_revision=SHA) is GateState.BLOCKED


def test_unknown_project_or_unprotected_ref_cannot_be_trusted():
    assert check_configuration(snapshot(), trusted_ref(protected=False),
        expected_project=TRUSTED, expected_revision=SHA) is GateState.BLOCKED
    assert check_configuration(snapshot(), trusted_ref(project_path=MIRROR),
        expected_project=TRUSTED, expected_revision=SHA) is GateState.BLOCKED
    assert check_configuration(snapshot(), trusted_ref(commit={"id":"f"*40}),
        expected_project=TRUSTED, expected_revision=SHA) is GateState.BLOCKED


def test_actual_connected_empty_config_is_fail_closed():
    assert check_configuration(snapshot(ci_config_path=""), trusted_ref(),
        expected_project=TRUSTED, expected_revision=SHA) is GateState.BLOCKED


def test_signed_exact_sha_authenticated_push_passes_but_never_grants_merge():
    rec = receipt()
    digest, signature = auth_data(rec)
    verdict = verify_authenticated_receipt(rec, digest, signature,
        signing_key=KEY, job=api_job(), observed_head_sha=SHA)
    assert verdict is GateState.ATTESTED


@pytest.mark.parametrize("alter", [
    {"worker_revision":"0"*40}, {"source_sha":"0"*40},
    {"target_sha":"0"*40}, {"timestamp":"2000-01-01T00:00:00+00:00"},
])
def test_signed_claim_cannot_be_changed_without_resigning(alter):
    original = receipt()
    digest, sig = auth_data(original)
    assert verify_authenticated_receipt(receipt(**alter),digest,sig,
        signing_key=KEY,job=api_job(),observed_head_sha=SHA) is GateState.BLOCKED


def test_wrong_secret_missing_secret_and_api_trigger_all_fail_closed():
    rec = receipt()
    digest,sig = auth_data(rec)
    assert verify_authenticated_receipt(rec,digest,sig,signing_key="wrong",job=api_job(),
        observed_head_sha=SHA) is GateState.BLOCKED
    assert verify_authenticated_receipt(rec,digest,sig,signing_key="",job=api_job(),
        observed_head_sha=SHA) is GateState.BLOCKED
    job = api_job()
    job["pipeline"]["source"] = "api"
    assert verify_authenticated_receipt(rec,digest,sig,signing_key=KEY,job=job,
        observed_head_sha=SHA) is GateState.BLOCKED


def test_commit_identity_requires_job_token_identity_and_matching_ref():
    rec=receipt()
    digest,sig=auth_data(rec)
    assert verify_authenticated_receipt(rec,digest,sig,signing_key=KEY,
        job=api_job(commit={"id":"f"*40}), observed_head_sha=SHA) is GateState.BLOCKED
    assert verify_authenticated_receipt(rec,digest,sig,signing_key=KEY,
        job=api_job(ref="whitechronos-refresh/bad"), observed_head_sha=SHA) is GateState.BLOCKED
    assert verify_authenticated_receipt(rec,digest,sig,signing_key=KEY,
        job=api_job(tag=True),observed_head_sha=SHA) is GateState.BLOCKED


def test_untrusted_receipt_fields_and_future_timestamp_blocked():
    rec=receipt(untrusted="payload")
    digest,sig=auth_data(rec)
    assert verify_authenticated_receipt(rec,digest,sig,signing_key=KEY,
        job=api_job(),observed_head_sha=SHA) is GateState.BLOCKED
    future=receipt(timestamp=(datetime.now(timezone.utc)+timedelta(hours=3)).isoformat())
    digest,sig=auth_data(future)
    assert verify_authenticated_receipt(future,digest,sig,signing_key=KEY,
        job=api_job(),observed_head_sha=SHA) is GateState.BLOCKED


def test_trusted_gitlab_template_does_not_execute_subject_code():
    cfg=(ROOT/"docs"/"gitlab-trusted-ci"/"trusted-mirror.yml").read_text()
    assert 'GIT_STRATEGY: "none"' in cfg
    assert "CI_PIPELINE_SOURCE" in cfg
    assert "CI_JOB_TOKEN" in cfg
    assert "VERIFIER_SHA256" in cfg
    assert "pipeline/trusted_gitlab_ci_gate.py" not in cfg
    assert "pip install" not in cfg


def test_no_secrets_required_or_configured_by_gate():
    gate_source=(ROOT/"pipeline"/"trusted_gitlab_ci_gate.py").read_text()
    assert "GITLAB_MIRROR_TOKEN" not in gate_source
    assert "git push" not in gate_source
    assert "create_pipeline" not in gate_source
