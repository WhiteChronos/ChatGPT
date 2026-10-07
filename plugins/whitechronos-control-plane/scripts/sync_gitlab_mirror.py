from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlsplit

from pipeline.gitlab_contingency_policy import classify_ref, load_policy

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _run_git(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(["git", *args], cwd=cwd, check=False, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise RuntimeError("git operation failed without credential disclosure")
    return result


def _reject_inline_credentials(url: str) -> None:
    if url.startswith(("https://", "http://")):
        parsed = urlsplit(url)
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("inline HTTPS credentials are not allowed; use a credential helper")


def _identity(url: str) -> str:
    if url.startswith(("https://", "http://", "ssh://")):
        parsed = urlsplit(url)
        return f"{parsed.hostname or 'remote'}{parsed.path}"
    if "@" in url and ":" in url and not Path(url).exists():
        return url.split("@", 1)[-1]
    return Path(url).name or "local-repository"


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
    _reject_inline_credentials(source_url)
    _reject_inline_credentials(target_url)
    policy = load_policy(Path(repo_root) / "governance" / "GITLAB_CONTINGENCY_CI_POLICY.json")
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
            _run_git(["push", target_url, f"{source_local_ref}:{full_ref}"], cwd=bare)
            target_after = _remote_sha(target_url, full_ref)
            if target_after != source_sha:
                raise RuntimeError("target mirror SHA does not match authoritative source after sync")

    receipt = {
        "schema_version": 1,
        "transport": "neutral_worker",
        "source_identity": _identity(source_url),
        "target_identity": _identity(target_url),
        "ref": ref,
        "source_sha": source_sha,
        "target_sha": target_after,
        "target_sha_before": target_before,
        "timestamp": datetime.now(timezone.utc).isoformat(),
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
