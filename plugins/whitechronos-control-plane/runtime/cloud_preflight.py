from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from .cloud_model import CloudPreflightInput, CloudPreflightReport
from .codex_probe import probe_codex_cli
from .model import CheckResult, CheckStatus


def _check(name: str, status: CheckStatus, detail: str, **evidence: object) -> CheckResult:
    return CheckResult(name, status, detail, evidence)


def _capture(
    args: list[str],
    cwd: Path | None = None,
    timeout_seconds: float = 5.0,
) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=max(0.01, timeout_seconds),
            check=False,
        )
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


def _capture_repo(
    args: list[str],
    cwd: Path,
    timeout_seconds: float = 5.0,
) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=max(0.01, timeout_seconds),
            check=False,
        )
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


def _python_version() -> tuple[int, int]:
    return sys.version_info.major, sys.version_info.minor


def _normalize_github_remote(remote: str) -> str | None:
    value = remote.strip()
    if value.startswith("git@github.com:"):
        value = value[len("git@github.com:") :]
    elif value.startswith(("https://", "http://", "ssh://")):
        parsed = urlsplit(value)
        if parsed.hostname != "github.com":
            return None
        value = parsed.path.lstrip("/")
    else:
        return None

    if value.endswith(".git"):
        value = value[:-4]
    value = value.strip("/")
    if not re.fullmatch(r"[^/\s]+/[^/\s]+", value):
        return None
    return value


def _repository_check(
    full_name: str,
    role: str,
    path: Path | None,
) -> tuple[CheckResult, str | None]:
    name = f"CLOUD_REPOSITORY_{role.upper()}"
    if path is None:
        return (
            _check(
                name,
                CheckStatus.FAIL,
                f"required repository path missing: {full_name}",
                repository=full_name,
            ),
            f"REPOSITORY:{full_name}",
        )
    resolved = Path(path).resolve()
    if not resolved.is_dir():
        return (
            _check(
                name,
                CheckStatus.FAIL,
                f"repository path does not exist: {resolved}",
                repository=full_name,
                path=str(resolved),
            ),
            f"REPOSITORY:{full_name}",
        )
    code, inside, err = _capture_repo(
        ["git", "rev-parse", "--is-inside-work-tree"],
        resolved,
    )
    if code != 0 or inside.lower() != "true":
        return (
            _check(
                name,
                CheckStatus.FAIL,
                f"path is not a Git worktree: {resolved}: {err or inside}",
                repository=full_name,
                path=str(resolved),
            ),
            f"REPOSITORY:{full_name}",
        )
    code, remote, _ = _capture_repo(["git", "remote", "get-url", "origin"], resolved)
    normalized = _normalize_github_remote(remote) if code == 0 else None
    if code != 0 or normalized != full_name:
        observed = normalized or "unrecognized-remote"
        return (
            _check(
                name,
                CheckStatus.FAIL,
                f"origin mismatch for {full_name}: observed {observed}",
                repository=full_name,
                path=str(resolved),
                observed_origin=observed,
            ),
            f"REPOSITORY:{full_name}",
        )
    return (
        _check(
            name,
            CheckStatus.PASS,
            f"repository identity verified: {full_name}",
            repository=full_name,
            path=str(resolved),
        ),
        None,
    )


def _tool_check(name: str, args: list[str], detail_ok: str) -> CheckResult:
    code, out, err = _capture(args)
    if code == 0:
        return _check(name, CheckStatus.PASS, detail_ok, version=out)
    return _check(
        name,
        CheckStatus.UNAVAILABLE,
        f"{args[0]} unavailable: {err or out or 'command failed'}",
    )


def run_cloud_preflight(inputs: CloudPreflightInput) -> CloudPreflightReport:
    checks: list[CheckResult] = []
    blockers: list[str] = []

    for repository in inputs.profile.repositories:
        if not repository.required:
            continue
        check, blocker = _repository_check(
            repository.full_name,
            repository.role,
            inputs.repo_paths.get(repository.full_name),
        )
        checks.append(check)
        if blocker is not None:
            blockers.append(blocker)

    current_python = _python_version()
    python_ok = current_python >= inputs.profile.toolchain.python_min
    checks.append(
        _check(
            "CLOUD_PYTHON_VERSION",
            CheckStatus.PASS if python_ok else CheckStatus.FAIL,
            f"Python {current_python[0]}.{current_python[1]} "
            f"{'meets' if python_ok else 'does not meet'} minimum "
            f"{inputs.profile.toolchain.python_min[0]}.{inputs.profile.toolchain.python_min[1]}",
            version=f"{current_python[0]}.{current_python[1]}",
        )
    )
    if not python_ok:
        blockers.append("CLOUD_PYTHON_VERSION")

    node_code, node_out, node_err = _capture(["node", "--version"])
    match = (
        re.fullmatch(r"v?(\d+)(?:\.\d+){0,2}", node_out.strip())
        if node_code == 0
        else None
    )
    node_ok = bool(match) and int(match.group(1)) == inputs.profile.toolchain.node_major
    checks.append(
        _check(
            "CLOUD_NODE_VERSION",
            CheckStatus.PASS
            if node_ok
            else (CheckStatus.FAIL if node_code == 0 else CheckStatus.UNAVAILABLE),
            f"Node {node_out or node_err or 'unavailable'} "
            f"{'matches' if node_ok else 'does not match'} required major "
            f"{inputs.profile.toolchain.node_major}",
            version=node_out,
        )
    )
    if not node_ok:
        blockers.append("CLOUD_NODE_VERSION")

    if inputs.profile.toolchain.require_git:
        git_check = _tool_check("CLOUD_GIT", ["git", "--version"], "Git available")
        checks.append(git_check)
        if git_check.status is not CheckStatus.PASS:
            blockers.append("CLOUD_GIT")

    if inputs.profile.toolchain.require_npm:
        npm_check = _tool_check("CLOUD_NPM", ["npm", "--version"], "npm available")
        checks.append(npm_check)
        if npm_check.status is not CheckStatus.PASS:
            blockers.append("CLOUD_NPM")

    caps = probe_codex_cli(inputs.codex_path)
    version_ok = caps.version != "unavailable"
    checks.append(
        _check(
            "CLOUD_CODEX_VERSION",
            CheckStatus.PASS if version_ok else CheckStatus.UNAVAILABLE,
            caps.version,
            version=caps.version,
        )
    )
    if not version_ok:
        blockers.append("CLOUD_CODEX_VERSION")

    capability_checks = (
        ("CLOUD_CODEX_EXEC", inputs.profile.toolchain.require_codex_exec, caps.exec),
        (
            "CLOUD_CODEX_EXEC_JSON",
            inputs.profile.toolchain.require_codex_json,
            caps.json,
        ),
        (
            "CLOUD_CODEX_RESUME",
            inputs.profile.toolchain.require_codex_resume,
            caps.resume,
        ),
    )
    for name, required, available in capability_checks:
        status = (
            CheckStatus.PASS
            if available
            else (CheckStatus.FAIL if required else CheckStatus.NOT_APPLICABLE)
        )
        checks.append(
            _check(name, status, f"{name} {'available' if available else 'unavailable'}")
        )
        if required and not available:
            blockers.append(name)

    blockers = list(dict.fromkeys(blockers))
    return CloudPreflightReport(tuple(checks), not blockers, tuple(blockers))


def cloud_report_to_json(report: CloudPreflightReport) -> dict[str, object]:
    return {
        "checks": [
            {
                "name": item.name,
                "status": item.status.value,
                "detail": item.detail,
                "evidence": item.evidence,
            }
            for item in report.checks
        ],
        "ready": report.ready,
        "blockers": list(report.blockers),
    }


def render_cloud_report(report: CloudPreflightReport) -> str:
    lines = ["CHECK\tSTATUS\tDETAIL"]
    lines.extend(
        f"{item.name}\t{item.status.value}\t{item.detail}" for item in report.checks
    )
    lines.append(f"CLOUD_READY\t{'YES' if report.ready else 'NO'}")
    if report.blockers:
        lines.append(f"BLOCKERS\t{','.join(report.blockers)}")
    return "\n".join(lines) + "\n"
