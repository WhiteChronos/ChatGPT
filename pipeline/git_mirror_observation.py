from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
import re
import subprocess
from urllib.parse import urlsplit
from pathlib import Path

_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_CANONICAL_GITHUB_REMOTE = "https://github.com/WhiteChronos/ChatGPT.git"


@dataclass(frozen=True)
class RemoteRefObservation:
    remote_url: str
    ref_name: str
    sha: str | None
    observed_at: str
    available: bool
    reason: str


def _reject_inline_credentials(remote_url: str) -> None:
    if remote_url.startswith(("http://", "https://")):
        parsed = urlsplit(remote_url)
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("inline HTTPS credentials are not allowed")


def _validate_remote(remote_url: str) -> None:
    value = remote_url.strip()
    if not value or value.startswith("-"):
        raise ValueError("remote must be a repository URL or local repository path")
    _reject_inline_credentials(value)
    if value.startswith(("http://", "https://", "ssh://")) or (
        "@" in value and ":" in value and not Path(value).exists()
    ):
        if value != _CANONICAL_GITHUB_REMOTE:
            raise ValueError("network remote is not the configured authoritative GitHub repository")


def _safe_git_env() -> dict[str, str]:
    allowed: dict[str, str] = {}
    for key in ("PATH", "HOME", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR", "TMP", "TEMP", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            allowed[key] = value
    allowed["GIT_CONFIG_NOSYSTEM"] = "1"
    allowed["GIT_CONFIG_GLOBAL"] = os.devnull
    allowed["GIT_TERMINAL_PROMPT"] = "0"
    return allowed


def _normalize_ref(ref_name: str) -> tuple[str, str]:
    value = ref_name.strip()
    if value.startswith("refs/heads/"):
        value = value[len("refs/heads/"):]
    if not value or ".." in value.split("/") or value.startswith("refs/"):
        raise ValueError("invalid branch ref")
    return value, f"refs/heads/{value}"


def observe_remote_ref(remote_url: str, ref_name: str) -> RemoteRefObservation:
    _validate_remote(remote_url)
    normalized, full_ref = _normalize_ref(ref_name)
    observed_at = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", remote_url, full_ref],
        check=False,
        text=True,
        capture_output=True,
        env=_safe_git_env(),
    )
    if result.returncode == 2:
        return RemoteRefObservation(remote_url, normalized, None, observed_at, False, "ref not found")
    if result.returncode != 0:
        return RemoteRefObservation(remote_url, normalized, None, observed_at, False, "remote unavailable")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise ValueError("malformed git ls-remote output")
    parts = lines[0].split()
    if len(parts) != 2 or parts[1] != full_ref or not _SHA_RE.fullmatch(parts[0]):
        raise ValueError("malformed git ls-remote output")
    return RemoteRefObservation(remote_url, normalized, parts[0].lower(), observed_at, True, "observed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--remote-url", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        obs = observe_remote_ref(args.remote_url, args.ref)
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, sort_keys=True))
        else:
            print(f"ERROR: {exc}")
        return 1
    payload = asdict(obs)
    print(json.dumps(payload, sort_keys=True) if args.json else payload)
    return 0 if obs.available else 4


if __name__ == "__main__":
    raise SystemExit(main())
