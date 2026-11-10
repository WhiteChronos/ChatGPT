"""Read-only, fail-closed preflight for the GitHub-only private MCE document vault.

Never uploads documents or grants access. Must run on authorized Windows
GitHub Actions after the private destination exists and is approved.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

_REPO_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\Z")
DEFAULT_REPOSITORY = "WhiteChronos/mce-document-vault"


def _outcome(status: str, reason: str) -> dict[str, str]:
    return {"status": status, "reason": reason}


def evaluate_repository(data: object, expected_repository: str) -> dict[str, str]:
    """Validate authenticated GitHub repo metadata, never inference from a URL."""
    if not isinstance(data, dict) or data.get("full_name") != expected_repository:
        return _outcome("BLOCKED", "WRONG_REPOSITORY")
    if data.get("private") is not True:
        return _outcome("BLOCKED", "REPO_NOT_PRIVATE")
    permissions = data.get("permissions")
    if not isinstance(permissions, dict) or permissions.get("push") is not True:
        return _outcome("BLOCKED", "NO_WRITE_PERMISSION")
    branch = data.get("default_branch")
    if not isinstance(branch, str) or not branch.strip():
        return _outcome("BLOCKED", "NO_DEFAULT_BRANCH")
    return _outcome("PASS", "PRIVATE_REPO_ACCESSIBLE")


def _fetch_repository(repository: str, token: str) -> object:
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MCE-GitHub-vault-preflight",
        },
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        # GitHub repository metadata is small. A malformed or huge payload
        # must not be printed and must not accidentally authorize access.
        return json.loads(response.read(524288).decode("utf-8"))


def check_vault(
    repository: str, token: str | None, fetcher=None
) -> dict[str, str]:
    """Check existence, privacy and write access without reading any files."""
    if not isinstance(repository, str) or _REPO_PATTERN.fullmatch(repository) is None:
        return _outcome("BLOCKED", "INVALID_REPOSITORY")
    if not isinstance(token, str) or not token.strip():
        return _outcome("BLOCKED", "MISSING_TOKEN")
    try:
        data = (fetcher or _fetch_repository)(repository, token)
    except FileNotFoundError:
        return _outcome("BLOCKED", "VAULT_NOT_ACCESSIBLE")
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            return _outcome("BLOCKED", "VAULT_NOT_ACCESSIBLE")
        return _outcome("BLOCKED", "VAULT_CHECK_FAILED")
    except (OSError, ValueError, TypeError, RuntimeError):
        # Do not emit exception messages: some can contain auth headers.
        return _outcome("BLOCKED", "VAULT_CHECK_FAILED")
    return evaluate_repository(data, repository)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MCE GitHub-only private vault read-only preflight")
    parser.add_argument("--repo", default=DEFAULT_REPOSITORY)
    args = parser.parse_args(argv)
    token = os.environ.get("MCE_VAULT_GITHUB_TOKEN")
    result = check_vault(args.repo, token)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
