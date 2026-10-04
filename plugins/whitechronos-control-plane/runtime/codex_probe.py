from __future__ import annotations

import os
import subprocess

from .model import CodexCapabilities

_SAFE_ENV_KEYS = (
    "PATH",
    "HOME",
    "USER",
    "TMPDIR",
    "TEMP",
    "TMP",
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
)


def _minimal_env() -> dict[str, str]:
    return {key: os.environ[key] for key in _SAFE_ENV_KEYS if key in os.environ}


def _capture(command: str, args: list[str], timeout_seconds: float) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            [command, *args],
            shell=False,
            env=_minimal_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=max(0.01, timeout_seconds),
            check=False,
        )
        return completed.returncode, completed.stdout, completed.stderr
    except (OSError, subprocess.TimeoutExpired):
        return 1, "", ""


def probe_codex_cli(
    codex_path: str,
    *,
    timeout_seconds: float = 5.0,
) -> CodexCapabilities:
    version_code, version_out, _ = _capture(codex_path, ["--version"], timeout_seconds)
    exec_code, exec_out, exec_err = _capture(codex_path, ["exec", "--help"], timeout_seconds)
    resume_code, resume_out, resume_err = _capture(codex_path, ["exec", "resume", "--help"], timeout_seconds)
    exec_help = f"{exec_out}\n{exec_err}"
    resume_help = f"{resume_out}\n{resume_err}"
    has_sandbox = "--sandbox" in exec_help
    return CodexCapabilities(
        version=version_out.strip() if version_code == 0 and version_out.strip() else "unavailable",
        exec=exec_code == 0,
        json=exec_code == 0 and "--json" in exec_help,
        resume=resume_code == 0 and "resume" in resume_help.lower(),
        sandbox_read_only=has_sandbox,
        sandbox_workspace_write=has_sandbox,
        approval_never="--ask-for-approval" in exec_help,
    )
