from __future__ import annotations

import json
import re
from pathlib import Path

from .cloud_model import (
    CloudEnvironmentProfile,
    CloudNetworkPolicy,
    CloudRepositorySpec,
    CloudToolchainSpec,
)
from .schema import validate_schema_subset


_SCHEMA_NAME = "whitechronos_codex_cloud_environment_v1.schema.json"
_REQUIRED_REPOSITORIES = (
    ("WhiteChronos/ChatGPT", "consumer", True),
    ("WhiteChronos/subagent-broker-runtime", "broker", True),
)
_SECRET_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_HOST_LABEL_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def _within(root: Path, candidate: Path) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"profile path must stay under repository root: {candidate}") from exc
    return candidate


def _load_object(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load JSON object from {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def validate_allowed_host(host: str) -> None:
    if not isinstance(host, str) or not host:
        raise ValueError("allowed host must be a non-empty bare DNS hostname")
    if "*" in host or "://" in host or "/" in host or ":" in host or "?" in host or "#" in host:
        raise ValueError(f"invalid allowed host: {host!r}")
    if host.startswith(".") or host.endswith(".") or ".." in host:
        raise ValueError(f"invalid allowed host: {host!r}")
    labels = host.split(".")
    if len(labels) < 2 or not all(_HOST_LABEL_RE.fullmatch(label) for label in labels):
        raise ValueError(f"invalid allowed host: {host!r}")


def validate_secret_name(name: str) -> None:
    if not isinstance(name, str) or _SECRET_NAME_RE.fullmatch(name) is None:
        raise ValueError(f"invalid secret name: {name!r}")


def load_cloud_profile(
    repo_root: Path,
    profile_path: Path,
) -> CloudEnvironmentProfile:
    repo_root = Path(repo_root).resolve()
    profile_path = _within(repo_root, Path(profile_path))
    schema_path = _within(repo_root, repo_root / "schemas" / _SCHEMA_NAME)

    data = _load_object(profile_path)
    schema = _load_object(schema_path)
    validate_schema_subset(data, schema)

    repositories_raw = data["repositories"]
    assert isinstance(repositories_raw, list)
    seen_repositories: set[str] = set()
    repositories: list[CloudRepositorySpec] = []
    for item in repositories_raw:
        assert isinstance(item, dict)
        full_name = item["full_name"]
        role = item["role"]
        required = item["required"]
        assert isinstance(full_name, str)
        assert isinstance(role, str)
        assert isinstance(required, bool)
        if full_name in seen_repositories:
            raise ValueError(f"duplicate repository: {full_name}")
        seen_repositories.add(full_name)
        repositories.append(CloudRepositorySpec(full_name, role, required))

    actual_required = tuple((item.full_name, item.role, item.required) for item in repositories)
    if actual_required != _REQUIRED_REPOSITORIES:
        raise ValueError(
            "repositories must exactly match the WhiteChronos Codex Cloud v1 initial repository set"
        )

    toolchain_raw = data["toolchain"]
    assert isinstance(toolchain_raw, dict)
    python_min_raw = toolchain_raw["python_min"]
    assert isinstance(python_min_raw, list)
    if python_min_raw != [3, 11]:
        raise ValueError("toolchain.python_min must be exactly [3, 11]")

    network_raw = data["network"]
    assert isinstance(network_raw, dict)
    allowed_hosts_raw = network_raw["allowed_hosts"]
    assert isinstance(allowed_hosts_raw, list)
    seen_hosts: set[str] = set()
    allowed_hosts: list[str] = []
    for host in allowed_hosts_raw:
        assert isinstance(host, str)
        validate_allowed_host(host)
        if host in seen_hosts:
            raise ValueError(f"duplicate allowed host: {host}")
        seen_hosts.add(host)
        allowed_hosts.append(host)

    secret_names_raw = data["required_secret_names"]
    assert isinstance(secret_names_raw, list)
    secret_names: list[str] = []
    for name in secret_names_raw:
        assert isinstance(name, str)
        validate_secret_name(name)
        secret_names.append(name)

    return CloudEnvironmentProfile(
        schema_version=str(data["schema_version"]),
        environment_name=str(data["environment_name"]),
        runtime_kind=str(data["runtime_kind"]),
        repositories=tuple(repositories),
        toolchain=CloudToolchainSpec(
            python_min=(3, 11),
            node_major=int(toolchain_raw["node_major"]),
            require_git=bool(toolchain_raw["require_git"]),
            require_npm=bool(toolchain_raw["require_npm"]),
            require_codex_exec=bool(toolchain_raw["require_codex_exec"]),
            require_codex_json=bool(toolchain_raw["require_codex_json"]),
            require_codex_resume=bool(toolchain_raw["require_codex_resume"]),
        ),
        network=CloudNetworkPolicy(
            mode=str(network_raw["mode"]),
            allowed_hosts=tuple(allowed_hosts),
        ),
        required_secret_names=tuple(secret_names),
    )
