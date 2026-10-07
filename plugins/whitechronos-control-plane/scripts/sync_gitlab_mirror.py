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

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline.gitlab_contingency_policy import classify_ref, load_policy

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
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
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env



def _run_git(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
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
    return url.startswith(("https://", "http://", "ssh://")) or (
        "@" in url and ":" in url and not Path(url).exists()
    )


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


def _mirror_receipt_claim(*, policy, ref: str, source_sha: str, timestamp: str) -> dict[str, object]:
    if not policy.gitlab_project_path:
        raise ValueError("mirror receipt requires a provisioned GitLab project")
    return {
        "schema_version": 1,
        "transport": "neutral_worker",
        "source_repository": policy.source_repository,
        "target_project_path": policy.gitlab_project_path,
        "ref": ref,
        "source_sha": source_sha.lower(),
        "target_sha": source_sha.lower(),
        "timestamp": timestamp,
    }


def _mirror_receipt_digest(receipt: dict[str, object]) -> str:
    encoded = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _mirror_push_options(receipt: dict[str, object]) -> list[str]:
    digest = _mirror_receipt_digest(receipt)
    inputs = {
        "mirror_transport": receipt["transport"],
        "mirror_source_repository": receipt["source_repository"],
        "mirror_target_project": receipt["target_project_path"],
        "mirror_ref": receipt["ref"],
        "mirror_source_sha": receipt["source_sha"],
        "mirror_target_sha": receipt["target_sha"],
        "mirror_timestamp": receipt["timestamp"],
        "mirror_receipt_sha256": digest,
    }
    options: list[str] = []
    for key, value in inputs.items():
        options.extend(["-o", f"ci.input={key}={value}"])
    return options


def _remote_sha(url: str, full_ref: str) -> str | None:
    result = _run_git(["ls-remote", "--exit-code", url, full_ref], check=False)
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
    dry_run: bool = False,
) -> dict[str, object]:
    _validate_remote_argument(source_url)
    _validate_remote_argument(target_url)
    policy = load_policy(Path(repo_root) / "governance" / "GITLAB_CONTINGENCY_CI_POLICY.json")
    _validate_mirror_direction(source_url, target_url, policy)
    decision = classify_ref(ref_name, policy)
    if not decision.eligible:
        raise ValueError("ref is not mirror eligible")
    ref = decision.ref_name
    full_ref = f"refs/heads/{ref}"

    with tempfile.TemporaryDirectory(prefix="whitechronos-gitlab-mirror-") as td:
        bare = Path(td) / "mirror.git"
        _run_git(["init", "--bare", str(bare)])
        source_local_ref = f"refs/whitechronos/source/{ref}"
        _run_git(["fetch", "--no-tags", source_url, f"{full_ref}:{source_local_ref}"], cwd=bare)
        source_sha = _run_git(["rev-parse", source_local_ref], cwd=bare).stdout.strip().lower()
        if not _SHA_RE.fullmatch(source_sha):
            raise RuntimeError("source ref did not resolve to a valid commit SHA")
        receipt_timestamp = datetime.now(timezone.utc).isoformat()
        receipt_claim = _mirror_receipt_claim(
            policy=policy,
            ref=ref,
            source_sha=source_sha,
            timestamp=receipt_timestamp,
        )

        target_before = _remote_sha(target_url, full_ref)
        if target_before:
            target_local_ref = f"refs/whitechronos/target/{ref}"
            _run_git(["fetch", "--no-tags", target_url, f"{full_ref}:{target_local_ref}"], cwd=bare)
            ancestry = _run_git(["merge-base", "--is-ancestor", target_before, source_sha], cwd=bare, check=False)
            if ancestry.returncode != 0:
                raise RuntimeError("target mirror has diverged from the authoritative source")

        if dry_run:
            target_after = target_before
        else:
            push_args = ["push"]
            if _is_network_remote(target_url):
                push_args.extend(_mirror_push_options(receipt_claim))
            push_args.extend([target_url, f"{source_local_ref}:{full_ref}"])
            _run_git(push_args, cwd=bare)
            target_after = _remote_sha(target_url, full_ref)
            if target_after != source_sha:
                raise RuntimeError("target mirror SHA does not match authoritative source after sync")

        source_after = _remote_sha(source_url, full_ref)
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
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        receipt = sync_ref(
            Path(args.repo_root),
            args.source_url,
            args.target_url,
            args.ref,
            Path(args.receipt),
            args.dry_run,
        )
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
