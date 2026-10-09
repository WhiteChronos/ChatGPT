from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import importlib.util
import os
from pathlib import Path
import re
import sys
import tempfile
from types import ModuleType
from typing import Iterator

SOURCE_URL = "https://github.com/WhiteChronos/ChatGPT.git"
CANONICAL_TARGET_URL = "https://gitlab.com/chronoswhite-group/ChronosWhite-project.git"
TOKEN_ENV = "GITLAB_MIRROR_TOKEN"
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_REF_RE = re.compile(r"^(?:main|(?:spec|plan|feat|fix|release)/[^\s\x00\r\n]+)$")


@dataclass(frozen=True)
class NeutralMirrorRequest:
    subject_ref: str
    subject_sha: str
    worker_revision: str
    target_url: str
    receipt_path: Path


def _require_sha(value: str, label: str) -> str:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        raise ValueError(f"{label} must be an exact 40-character Git commit SHA")
    return value.lower()


def _require_subject_ref(value: str) -> str:
    if not isinstance(value, str) or not _REF_RE.fullmatch(value):
        raise ValueError("subject ref is not mirror eligible")
    return value


def validate_trusted_worker_context(
    request: NeutralMirrorRequest,
    *,
    workflow_ref: str,
    workflow_sha: str,
    trusted_ref: str,
) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true" and os.environ.get("GITHUB_RUN_ATTEMPT") != "1":
        raise ValueError("rerun attempt rejected for secret-bearing worker")
    if workflow_ref != trusted_ref:
        raise ValueError("trusted worker ref mismatch")
    worker_sha = _require_sha(request.worker_revision, "worker revision")
    observed_worker_sha = _require_sha(workflow_sha, "workflow SHA")
    if worker_sha != observed_worker_sha:
        raise ValueError("worker revision must equal trusted workflow SHA")
    _require_sha(request.subject_sha, "subject SHA")
    _require_subject_ref(request.subject_ref)
    if request.target_url != CANONICAL_TARGET_URL:
        raise ValueError("target URL must be the canonical GitLab mirror project")
    if not isinstance(request.receipt_path, Path):
        raise ValueError("receipt path must be a pathlib.Path")


def _load_sync_module(repo_root: Path) -> ModuleType:
    script = (
        Path(repo_root)
        / "plugins"
        / "whitechronos-control-plane"
        / "scripts"
        / "sync_gitlab_mirror.py"
    )
    if not script.is_file():
        raise RuntimeError("mirror implementation is unavailable")
    module_name = "whitechronos_sync_gitlab_mirror"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise RuntimeError("mirror implementation could not be loaded")
    module = importlib.util.module_from_spec(spec)
    repo_text = str(Path(repo_root).resolve())
    added = repo_text not in sys.path
    if added:
        sys.path.insert(0, repo_text)
    try:
        spec.loader.exec_module(module)
    finally:
        if added:
            sys.path.remove(repo_text)
    return module


def _observe_source_sha(repo_root: Path, subject_ref: str) -> str:
    subject = _require_subject_ref(subject_ref)
    module = _load_sync_module(repo_root)
    observed = module._remote_sha(SOURCE_URL, f"refs/heads/{subject}")
    if observed is None:
        raise RuntimeError("authoritative subject ref is unavailable")
    return _require_sha(observed, "observed subject SHA")


def _sync_ref(*args, **kwargs):
    repo_root = Path(args[0]) if args else Path(kwargs["repo_root"])
    module = _load_sync_module(repo_root)
    return module.sync_ref(*args, **kwargs)


@contextmanager
def temporary_gitlab_credential_helper(
    token: str,
    username: str = "oauth2",
) -> Iterator[Path]:
    if not isinstance(token, str) or not token or any(ch in token for ch in "\x00\r\n"):
        raise ValueError("GitLab mirror token is invalid")
    if not isinstance(username, str) or not username or any(ch in username for ch in "\x00\r\n"):
        raise ValueError("GitLab credential username is invalid")

    with tempfile.TemporaryDirectory(prefix="whitechronos-gitlab-credential-") as td:
        root = Path(td)
        material = root / "credential.material"
        helper = root / "git-credential-whitechronos"

        material.write_text(
            f"username={username}\npassword={token}\n",
            encoding="utf-8",
        )
        material.chmod(0o600)

        helper.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  get) cat \"$(dirname \"$0\")/credential.material\" ;;\n"
            "  store|erase) exit 0 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        helper.chmod(0o700)
        yield helper


def run_neutral_mirror(
    repo_root: Path,
    request: NeutralMirrorRequest,
    *,
    workflow_ref: str,
    workflow_sha: str,
    trusted_ref: str,
) -> dict[str, object]:
    validate_trusted_worker_context(
        request,
        workflow_ref=workflow_ref,
        workflow_sha=workflow_sha,
        trusted_ref=trusted_ref,
    )

    # Guard against stale worker revisions before reading the token.
    # Per-SHA GitHub Environment revocation is the actual secret-release gate.
    if os.environ.get("GITHUB_ACTIONS") == "true":
        observed_main_sha = _observe_source_sha(Path(repo_root), "main")
        if observed_main_sha != _require_sha(request.worker_revision, "worker revision"):
            raise ValueError("retired trusted worker revision is not current main")

    signing_key = os.environ.pop("GITLAB_MIRROR_SIGNING_KEY", None)
    if os.environ.get("GITHUB_ACTIONS") == "true" and not signing_key:
        raise RuntimeError("authenticated mirror receipt signer is unavailable")
    if signing_key is not None:
        from pipeline.mirror_receipt_auth import sign_receipt_digest
        receipt_signer = lambda digest: sign_receipt_digest(digest, signing_key)
    else:
        receipt_signer = None

    token = os.environ.pop(TOKEN_ENV, None)
    if not token:
        raise RuntimeError("GITLAB_MIRROR_TOKEN is required")

    observed_source_sha = _observe_source_sha(Path(repo_root), request.subject_ref)
    expected_subject_sha = _require_sha(request.subject_sha, "subject SHA")
    if observed_source_sha != expected_subject_sha:
        raise RuntimeError("authoritative subject SHA no longer matches requested subject SHA")

    with temporary_gitlab_credential_helper(token) as helper:
        receipt = _sync_ref(
            Path(repo_root),
            SOURCE_URL,
            request.target_url,
            request.subject_ref,
            request.receipt_path,
            worker_revision=request.worker_revision,
            target_credential_helper=str(helper),
            source_credential_helper=None,
            expected_source_sha=expected_subject_sha,
            receipt_signer=receipt_signer,
        )

    source_sha = _require_sha(str(receipt.get("source_sha", "")), "receipt source SHA")
    target_sha = _require_sha(str(receipt.get("target_sha", "")), "receipt target SHA")
    receipt_worker = _require_sha(
        str(receipt.get("worker_revision", "")),
        "receipt worker revision",
    )
    if source_sha != expected_subject_sha or target_sha != expected_subject_sha:
        raise RuntimeError("mirror receipt does not match requested subject SHA")
    if receipt_worker != request.worker_revision.lower():
        raise RuntimeError("mirror receipt worker revision mismatch")
    return receipt
