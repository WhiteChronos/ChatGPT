from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from typing import Callable

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.gitlab_contingency_policy import classify_ref, load_policy

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_SCP_REMOTE_RE = re.compile(r"^(?:[^/@:\s]+@)?[^/:\s]+:.+$")
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\\\/]")
_BLOCKED_GIT_ENV_EXACT = {
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM",
    "GIT_EXEC_PATH",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_PROXY_COMMAND",
}
_BLOCKED_GIT_ENV_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")


def _safe_git_environment() -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("GIT_", "SSH_"))
    }
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env



def _normalize_credential_helper(value: str | None) -> str | None:
    if value is None:
        return None
    raw = value.strip()
    if raw == "manager":
        return raw
    if not raw or raw != value:
        raise ValueError("credential helper must be the GCM 'manager' selector or an explicit absolute executable path")
    if any(ch.isspace() for ch in raw) or any(ch in raw for ch in (";", "&", "|", "!", "$", "`", "<", ">", "\n", "\r", "\x00")):
        raise ValueError("credential helper contains unsafe shell-control characters")
    path = Path(raw)
    if not path.is_absolute():
        raise ValueError("credential helper must be the GCM 'manager' selector or an explicit absolute executable path")
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ValueError("credential helper path does not exist") from exc
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError("credential helper must reference an executable file")
    return str(resolved)


def _git_argv(args: list[str], credential_helper: str | None = None) -> list[str]:
    if credential_helper is None:
        return ["git", *args]
    return [
        "git",
        "-c",
        "credential.helper=",
        "-c",
        f"credential.helper={credential_helper}",
        "-c",
        "credential.interactive=false",
        *args,
    ]


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    credential_helper: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        _git_argv(args, credential_helper),
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
        env=_safe_git_environment(),
    )
    if check and result.returncode != 0:
        raise RuntimeError("git operation failed without credential disclosure")
    return result


def _reject_inline_credentials(url: str) -> None:
    if url.startswith(("https://", "http://")):
        parsed = urlsplit(url)
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("inline HTTPS credentials are not allowed; use a credential helper")


def _validate_remote_argument(url: str) -> None:
    if not url or url != url.strip():
        raise ValueError("remote must be nonblank and free of surrounding whitespace")
    if url.startswith("-"):
        raise ValueError("remote must not be option-like")
    if any(ch in url for ch in ("\x00", "\n", "\r")):
        raise ValueError("remote contains invalid control characters")
    _reject_inline_credentials(url)


def _identity(url: str) -> str:
    if url.startswith(("https://", "http://", "ssh://")):
        parsed = urlsplit(url)
        return f"{parsed.hostname or 'remote'}{parsed.path}"
    if "@" in url and ":" in url and not Path(url).exists():
        return url.split("@", 1)[-1]
    return Path(url).name or "local-repository"


def _is_network_remote(url: str) -> bool:
    if url.startswith(("https://", "http://", "ssh://")):
        return True
    if _WINDOWS_DRIVE_RE.match(url):
        return False
    return bool(_SCP_REMOTE_RE.match(url) and not Path(url).exists())


def _validate_mirror_direction(source_url: str, target_url: str, policy) -> None:
    source_network = _is_network_remote(source_url)
    target_network = _is_network_remote(target_url)
    if not source_network and not target_network:
        return
    expected_source = f"https://github.com/{policy.source_repository}.git"
    if not policy.gitlab_project_path:
        raise ValueError("mirror direction requires a provisioned GitLab project")
    expected_target = f"https://gitlab.com/{policy.gitlab_project_path}.git"
    if source_url != expected_source or target_url != expected_target:
        raise ValueError("mirror direction must be canonical GitHub source -> GitLab target")


def _mirror_receipt_claim(
    *,
    policy,
    ref: str,
    source_sha: str,
    timestamp: str,
    worker_revision: str,
    pipeline_ref: str | None = None,
) -> dict[str, object]:
    if not policy.gitlab_project_path:
        raise ValueError("mirror receipt requires a provisioned GitLab project")
    if not _SHA_RE.fullmatch(worker_revision):
        raise ValueError("worker revision must be an exact 40-character Git commit SHA")
    return {
        "schema_version": 1,
        "transport": "neutral_worker",
        "source_repository": policy.source_repository,
        "target_project_path": policy.gitlab_project_path,
        "ref": ref,
        "pipeline_ref": pipeline_ref or ref,
        "source_sha": source_sha.lower(),
        "target_sha": source_sha.lower(),
        "timestamp": timestamp,
        "worker_revision": worker_revision.lower(),
    }


def _mirror_receipt_digest(receipt: dict[str, object]) -> str:
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _refresh_ref(receipt: dict[str, object]) -> str:
    raw = "\0".join(
        str(receipt[key])
        for key in ("ref", "source_sha", "timestamp")
    ).encode("utf-8")
    return f"refs/heads/whitechronos-refresh/{hashlib.sha256(raw).hexdigest()}"


def _mirror_push_options(receipt: dict[str, object], *, signature: str | None = None) -> list[str]:
    digest = _mirror_receipt_digest(receipt)
    inputs = {
        "mirror_transport": receipt["transport"],
        "mirror_source_repository": receipt["source_repository"],
        "mirror_target_project": receipt["target_project_path"],
        "mirror_ref": receipt["ref"],
        "mirror_pipeline_ref": receipt["pipeline_ref"],
        "mirror_source_sha": receipt["source_sha"],
        "mirror_target_sha": receipt["target_sha"],
        "mirror_timestamp": receipt["timestamp"],
        "mirror_worker_revision": receipt["worker_revision"],
        "mirror_receipt_sha256": digest,
    }
    if signature is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", signature):
            raise ValueError("invalid detached receipt signature")
        inputs["mirror_receipt_signature"] = signature
    options: list[str] = []
    for key, value in inputs.items():
        options.extend(["-o", f"ci.input={key}={value}"])
    return options


def _remote_sha(
    url: str,
    full_ref: str,
    *,
    credential_helper: str | None = None,
) -> str | None:
    result = _run_git(
        ["ls-remote", "--exit-code", url, full_ref],
        check=False,
        credential_helper=credential_helper,
    )
    if result.returncode == 2:
        return None
    if result.returncode != 0:
        raise RuntimeError("remote ref observation failed without credential disclosure")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError("remote ref observation returned malformed output")
    parts = lines[0].split()
    if len(parts) != 2 or parts[1] != full_ref or not _SHA_RE.fullmatch(parts[0]):
        raise RuntimeError("remote ref observation returned malformed output")
    return parts[0].lower()


def sync_ref(
    repo_root: Path,
    source_url: str,
    target_url: str,
    ref_name: str,
    receipt_path: Path,
    worker_revision: str,
    dry_run: bool = False,
    target_credential_helper: str | None = None,
    source_credential_helper: str | None = None,
    expected_source_sha: str | None = None,
    receipt_signer: Callable[[str], str] | None = None,
) -> dict[str, object]:
    _validate_remote_argument(source_url)
    _validate_remote_argument(target_url)
    policy = load_policy(Path(repo_root) / "governance" / "GITLAB_CONTINGENCY_CI_POLICY.json")
    _validate_mirror_direction(source_url, target_url, policy)
    normalized_target_helper = _normalize_credential_helper(target_credential_helper)
    normalized_source_helper = _normalize_credential_helper(source_credential_helper)
    if _is_network_remote(target_url) and normalized_target_helper is None:
        raise ValueError("target credential helper is required for a network GitLab target")
    decision = classify_ref(ref_name, policy)
    if not decision.eligible:
        raise ValueError("ref is not mirror eligible")
    ref = decision.ref_name
    full_ref = f"refs/heads/{ref}"

    with tempfile.TemporaryDirectory(prefix="whitechronos-gitlab-mirror-") as td:
        bare = Path(td) / "mirror.git"
        _run_git(["init", "--bare", str(bare)])
        source_local_ref = f"refs/whitechronos/source/{ref}"
        _run_git(
            ["fetch", "--no-tags", source_url, f"{full_ref}:{source_local_ref}"],
            cwd=bare,
            credential_helper=normalized_source_helper,
        )
        source_sha = _run_git(["rev-parse", source_local_ref], cwd=bare).stdout.strip().lower()
        if not _SHA_RE.fullmatch(source_sha):
            raise RuntimeError("source ref did not resolve to a valid commit SHA")
        if expected_source_sha is not None:
            if not _SHA_RE.fullmatch(expected_source_sha):
                raise ValueError("expected source SHA must be an exact 40-character Git commit SHA")
            if source_sha != expected_source_sha.lower():
                raise RuntimeError("authoritative source SHA does not match requested subject before push")
        receipt_timestamp = datetime.now(timezone.utc).isoformat()
        receipt_base = _mirror_receipt_claim(
            policy=policy,
            ref=ref,
            source_sha=source_sha,
            timestamp=receipt_timestamp,
            worker_revision=worker_revision,
        )

        target_before = _remote_sha(
            target_url,
            full_ref,
            credential_helper=normalized_target_helper,
        )
        if target_before:
            target_local_ref = f"refs/whitechronos/target/{ref}"
            _run_git(
                ["fetch", "--no-tags", target_url, f"{full_ref}:{target_local_ref}"],
                cwd=bare,
                credential_helper=normalized_target_helper,
            )
            ancestry = _run_git(["merge-base", "--is-ancestor", target_before, source_sha], cwd=bare, check=False)
            if ancestry.returncode != 0:
                raise RuntimeError("target mirror has diverged from the authoritative source")

        pipeline_full_ref = full_ref
        if (
            not dry_run
            and _is_network_remote(target_url)
            and target_before == source_sha
        ):
            pipeline_full_ref = _refresh_ref(receipt_base)
        pipeline_ref = pipeline_full_ref[len("refs/heads/"):]
        receipt_claim = _mirror_receipt_claim(
            policy=policy,
            ref=ref,
            source_sha=source_sha,
            timestamp=receipt_timestamp,
            worker_revision=worker_revision,
            pipeline_ref=pipeline_ref,
        )

        receipt_signature = None
        push_args = ["push"]
        if dry_run:
            push_args.append("--dry-run")
        if _is_network_remote(target_url):
            receipt_signature = (
                receipt_signer(_mirror_receipt_digest(receipt_claim))
                if receipt_signer is not None else None
            )
            push_args.extend(_mirror_push_options(receipt_claim, signature=receipt_signature))
        push_args.extend([target_url, f"{source_local_ref}:{pipeline_full_ref}"])
        _run_git(
            push_args,
            cwd=bare,
            credential_helper=normalized_target_helper,
        )

        if dry_run:
            target_after = target_before
        else:
            target_after = _remote_sha(
                target_url,
                full_ref,
                credential_helper=normalized_target_helper,
            )
            if target_after != source_sha:
                raise RuntimeError("target mirror SHA does not match authoritative source after sync")

        source_after = _remote_sha(
            source_url,
            full_ref,
            credential_helper=normalized_source_helper,
        )
        if source_after != source_sha:
            raise RuntimeError("authoritative source ref changed during sync; success receipt refused")

    receipt = {
        **receipt_claim,
        "receipt_sha256": _mirror_receipt_digest(receipt_claim),
        "source_identity": _identity(source_url),
        "target_identity": _identity(target_url),
        "target_sha": target_after,
        "target_sha_before": target_before,
        "dry_run": bool(dry_run),
    }
    if receipt_signature is not None:
        receipt["receipt_signature"] = receipt_signature
    receipt["record_sha256"] = _mirror_receipt_digest(receipt)
    receipt_path = Path(receipt_path)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--target-url", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--worker-revision", required=True)
    parser.add_argument("--target-credential-helper")
    parser.add_argument("--source-credential-helper")
    parser.add_argument("--expected-source-sha")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        receipt = sync_ref(
            Path(args.repo_root),
            args.source_url,
            args.target_url,
            args.ref,
            Path(args.receipt),
            args.worker_revision,
            args.dry_run,
            args.target_credential_helper,
            args.source_credential_helper,
            args.expected_source_sha,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
