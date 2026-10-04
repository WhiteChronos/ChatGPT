from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from .cloud_model import CloudEnvironmentProfile

_OUTPUT_LIMIT = 4096
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
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "NODE_EXTRA_CA_CERTS",
)


@dataclass(frozen=True)
class BootstrapStep:
    repository: str
    cwd: Path
    argv: tuple[str, ...]


@dataclass(frozen=True)
class BootstrapResult:
    step: BootstrapStep
    returncode: int
    stdout_tail: str
    stderr_tail: str


def _minimal_env() -> dict[str, str]:
    env = {key: os.environ[key] for key in _SAFE_ENV_KEYS if key in os.environ}
    env["PIP_CONFIG_FILE"] = os.devnull
    env["NPM_CONFIG_USERCONFIG"] = os.devnull
    return env


def _require_file(path: Path, name: str) -> None:
    required = path / name
    if not required.is_file():
        raise ValueError(f"required bootstrap file missing: {required}")


def build_bootstrap_plan(
    profile: CloudEnvironmentProfile,
    repo_paths: dict[str, Path],
) -> tuple[BootstrapStep, ...]:
    steps: list[BootstrapStep] = []
    for repository in profile.repositories:
        if not repository.required:
            continue
        raw_path = repo_paths.get(repository.full_name)
        if raw_path is None:
            raise ValueError(f"repository path missing: {repository.full_name}")
        path = Path(raw_path).resolve()
        if not path.is_dir():
            raise ValueError(f"repository path does not exist: {path}")
        if repository.role == "consumer":
            _require_file(path, "requirements-dev.txt")
            argv = (
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                "requirements-dev.txt",
            )
        elif repository.role == "broker":
            _require_file(path, "package.json")
            _require_file(path, "package-lock.json")
            argv = ("npm", "ci")
        else:
            raise ValueError(f"unknown repository role: {repository.role}")
        steps.append(BootstrapStep(repository.full_name, path, argv))
    return tuple(steps)


def _tail(value: str) -> str:
    if len(value) <= _OUTPUT_LIMIT:
        return value
    return value[-_OUTPUT_LIMIT:]


def execute_bootstrap_plan(
    steps: tuple[BootstrapStep, ...],
    *,
    apply: bool,
    timeout_seconds: float = 300.0,
) -> tuple[BootstrapResult, ...]:
    if not apply:
        return tuple(BootstrapResult(step, 0, "DRY_RUN", "") for step in steps)

    results: list[BootstrapResult] = []
    for step in steps:
        try:
            completed = subprocess.run(
                list(step.argv),
                cwd=step.cwd,
                shell=False,
                env=_minimal_env(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=max(0.01, timeout_seconds),
                check=False,
            )
            result = BootstrapResult(
                step,
                completed.returncode,
                _tail(completed.stdout or ""),
                _tail(completed.stderr or ""),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = BootstrapResult(step, 1, "", _tail(str(exc)))
        results.append(result)
        if result.returncode != 0:
            break
    return tuple(results)
