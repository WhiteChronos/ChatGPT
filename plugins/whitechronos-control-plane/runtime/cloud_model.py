from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .model import CheckResult


@dataclass(frozen=True)
class CloudRepositorySpec:
    full_name: str
    role: str
    required: bool


@dataclass(frozen=True)
class CloudToolchainSpec:
    python_min: tuple[int, int]
    node_major: int
    require_git: bool
    require_npm: bool
    require_codex_exec: bool
    require_codex_json: bool
    require_codex_resume: bool


@dataclass(frozen=True)
class CloudNetworkPolicy:
    mode: str
    allowed_hosts: tuple[str, ...]


@dataclass(frozen=True)
class CloudEnvironmentProfile:
    schema_version: str
    environment_name: str
    runtime_kind: str
    repositories: tuple[CloudRepositorySpec, ...]
    toolchain: CloudToolchainSpec
    network: CloudNetworkPolicy
    required_secret_names: tuple[str, ...]


@dataclass(frozen=True)
class CloudPreflightInput:
    profile: CloudEnvironmentProfile
    repo_paths: dict[str, Path]
    codex_path: str


@dataclass(frozen=True)
class CloudPreflightReport:
    checks: tuple[CheckResult, ...]
    ready: bool
    blockers: tuple[str, ...]
