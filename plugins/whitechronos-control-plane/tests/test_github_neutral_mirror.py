from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = ROOT / "plugins" / "whitechronos-control-plane"
RUNTIME_PATH = PLUGIN_ROOT / "runtime" / "github_neutral_mirror.py"
CLI_PATH = PLUGIN_ROOT / "scripts" / "github_neutral_mirror.py"
SUBJECT_SHA = "a" * 40
WORKER_SHA = "b" * 40
TOKEN = "glpat-synthetic-secret-value-for-tests"
TARGET_URL = "https://gitlab.com/chronoswhite-group/ChronosWhite-project.git"


def load_module():
    assert RUNTIME_PATH.is_file(), "github_neutral_mirror runtime module missing"
    spec = importlib.util.spec_from_file_location("github_neutral_mirror", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def request(module, tmp_path: Path, *, subject_sha: str = SUBJECT_SHA, worker_revision: str = WORKER_SHA):
    return module.NeutralMirrorRequest(
        subject_ref="feat/example",
        subject_sha=subject_sha,
        worker_revision=worker_revision,
        target_url=TARGET_URL,
        receipt_path=tmp_path / "receipt.json",
    )


def test_untrusted_workflow_ref_fails_before_secret_access(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.delenv("GITLAB_MIRROR_TOKEN", raising=False)
    with pytest.raises(ValueError, match="trusted worker ref"):
        module.run_neutral_mirror(
            ROOT,
            request(module, tmp_path),
            workflow_ref="refs/heads/feat/example",
            workflow_sha=WORKER_SHA,
            trusted_ref="refs/heads/main",
        )


def test_worker_sha_must_equal_workflow_sha(tmp_path):
    module = load_module()
    with pytest.raises(ValueError, match="worker revision"):
        module.validate_trusted_worker_context(
            request(module, tmp_path),
            workflow_ref="refs/heads/main",
            workflow_sha="c" * 40,
            trusted_ref="refs/heads/main",
        )


def test_subject_sha_is_data_not_executable_worker_revision(tmp_path, monkeypatch):
    module = load_module()
    captured = {}

    def fake_sync(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {
            "source_sha": SUBJECT_SHA,
            "target_sha": SUBJECT_SHA,
            "worker_revision": WORKER_SHA,
        }

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: SUBJECT_SHA)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)
    result = module.run_neutral_mirror(
        ROOT,
        request(module, tmp_path),
        workflow_ref="refs/heads/main",
        workflow_sha=WORKER_SHA,
        trusted_ref="refs/heads/main",
    )
    assert captured["kwargs"]["worker_revision"] == WORKER_SHA
    assert captured["kwargs"]["worker_revision"] != SUBJECT_SHA
    assert result["source_sha"] == SUBJECT_SHA


def test_missing_gitlab_token_fails_before_git(tmp_path, monkeypatch):
    module = load_module()
    monkeypatch.delenv("GITLAB_MIRROR_TOKEN", raising=False)
    monkeypatch.setattr(
        module,
        "_sync_ref",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("git must not run")),
    )
    with pytest.raises(RuntimeError, match="GITLAB_MIRROR_TOKEN"):
        module.run_neutral_mirror(
            ROOT,
            request(module, tmp_path),
            workflow_ref="refs/heads/main",
            workflow_sha=WORKER_SHA,
            trusted_ref="refs/heads/main",
        )


def test_credential_helper_contains_no_token_literal():
    module = load_module()
    with module.temporary_gitlab_credential_helper(TOKEN) as helper:
        body = helper.read_text(encoding="utf-8")
        assert TOKEN not in body
        assert "credential.material" in body


def test_credential_material_mode_is_0600():
    module = load_module()
    with module.temporary_gitlab_credential_helper(TOKEN) as helper:
        material = helper.parent / "credential.material"
        assert stat.S_IMODE(material.stat().st_mode) == 0o600


def test_credential_helper_mode_is_0700():
    module = load_module()
    with module.temporary_gitlab_credential_helper(TOKEN) as helper:
        assert stat.S_IMODE(helper.stat().st_mode) == 0o700


def test_token_is_removed_from_child_environment_before_git(tmp_path, monkeypatch):
    module = load_module()

    def fake_sync(*args, **kwargs):
        assert "GITLAB_MIRROR_TOKEN" not in os.environ
        return {
            "source_sha": SUBJECT_SHA,
            "target_sha": SUBJECT_SHA,
            "worker_revision": WORKER_SHA,
        }

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: SUBJECT_SHA)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)
    module.run_neutral_mirror(
        ROOT,
        request(module, tmp_path),
        workflow_ref="refs/heads/main",
        workflow_sha=WORKER_SHA,
        trusted_ref="refs/heads/main",
    )


def test_credential_helper_and_material_are_removed_on_success(tmp_path, monkeypatch):
    module = load_module()
    captured = {}

    def fake_sync(*args, **kwargs):
        helper = Path(kwargs["target_credential_helper"])
        captured["helper"] = helper
        captured["material"] = helper.parent / "credential.material"
        assert captured["helper"].exists()
        assert captured["material"].exists()
        return {
            "source_sha": SUBJECT_SHA,
            "target_sha": SUBJECT_SHA,
            "worker_revision": WORKER_SHA,
        }

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: SUBJECT_SHA)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)
    module.run_neutral_mirror(
        ROOT,
        request(module, tmp_path),
        workflow_ref="refs/heads/main",
        workflow_sha=WORKER_SHA,
        trusted_ref="refs/heads/main",
    )
    assert not captured["helper"].exists()
    assert not captured["material"].exists()


def test_credential_helper_and_material_are_removed_on_sync_failure(tmp_path, monkeypatch):
    module = load_module()
    captured = {}

    def fake_sync(*args, **kwargs):
        helper = Path(kwargs["target_credential_helper"])
        captured["helper"] = helper
        captured["material"] = helper.parent / "credential.material"
        raise RuntimeError("synthetic sync failure")

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: SUBJECT_SHA)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)
    with pytest.raises(RuntimeError, match="synthetic sync failure"):
        module.run_neutral_mirror(
            ROOT,
            request(module, tmp_path),
            workflow_ref="refs/heads/main",
            workflow_sha=WORKER_SHA,
            trusted_ref="refs/heads/main",
        )
    assert not captured["helper"].exists()
    assert not captured["material"].exists()


def test_token_never_appears_in_sync_ref_arguments_or_receipt(tmp_path, monkeypatch):
    module = load_module()

    def fake_sync(*args, **kwargs):
        rendered = repr((args, kwargs))
        assert TOKEN not in rendered
        return {
            "source_sha": SUBJECT_SHA,
            "target_sha": SUBJECT_SHA,
            "worker_revision": WORKER_SHA,
        }

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: SUBJECT_SHA)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)
    result = module.run_neutral_mirror(
        ROOT,
        request(module, tmp_path),
        workflow_ref="refs/heads/main",
        workflow_sha=WORKER_SHA,
        trusted_ref="refs/heads/main",
    )
    assert TOKEN not in json.dumps(result, sort_keys=True)


def test_cli_entrypoint_is_present_and_sanitizes_validation_errors(tmp_path):
    assert CLI_PATH.is_file(), "github_neutral_mirror CLI missing"
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), "--repo-root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "invalid input" in result.stderr.lower()


def test_subject_sha_mismatch_fails_before_sync(tmp_path, monkeypatch):
    module = load_module()
    called = {"sync": False}

    def fake_sync(*args, **kwargs):
        called["sync"] = True
        raise AssertionError("sync must not run when subject SHA moved")

    monkeypatch.setattr(module, "_sync_ref", fake_sync)
    monkeypatch.setattr(module, "_observe_source_sha", lambda *args, **kwargs: "c" * 40)
    monkeypatch.setenv("GITLAB_MIRROR_TOKEN", TOKEN)

    with pytest.raises(RuntimeError, match="subject SHA"):
        module.run_neutral_mirror(
            ROOT,
            request(module, tmp_path),
            workflow_ref="refs/heads/main",
            workflow_sha=WORKER_SHA,
            trusted_ref="refs/heads/main",
        )
    assert called["sync"] is False
