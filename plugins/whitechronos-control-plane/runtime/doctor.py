from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path

from .codex_probe import probe_codex_cli
from .mcp_probe import McpProbeSecurityError, probe_stdio_mcp, resolve_mcp_launch
from .model import CheckResult, CheckStatus, DoctorInput, DoctorReport, McpProbeResult
from .registry import load_registry

_ARENA_ID = "github-arena"
_BROKER_ID = "subagent-broker"
_TRUSTED_RUNTIME_KINDS = {"trusted_remote", "codex_cloud"}
_TRANSIENT_UNTRACKED_PREFIXES = (".pytest_cache/", ".mypy_cache/", ".ruff_cache/", ".superpowers/", ".worktrees/")
_TRANSIENT_UNTRACKED_FILES = {".coverage"}
_NATIVE_V1_TOOLS = ("spawn_agent", "send_input", "wait_agent", "resume_agent", "close_agent")
_NATIVE_V2_TOOLS = ("spawn_agent", "send_message", "followup_task", "wait_agent", "interrupt_agent", "list_agents")
_NATIVE_V1_NAMESPACES = ("multi_agent_v1",)
_NATIVE_V2_NAMESPACES = ("collaboration", "multi_agent_v2")


def _is_transient_untracked(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return (
        normalized in _TRANSIENT_UNTRACKED_FILES
        or normalized.endswith(".pyc")
        or "/__pycache__/" in f"/{normalized}"
        or any(normalized.startswith(prefix) for prefix in _TRANSIENT_UNTRACKED_PREFIXES)
    )


def _worktree_changes(repo: Path) -> tuple[int, tuple[str, ...], str]:
    code, stdout, stderr = _capture(["git", "status", "--porcelain=v1", "--untracked-files=all"], repo)
    relevant: list[str] = []
    for line in stdout.splitlines():
        if line.startswith("?? ") and _is_transient_untracked(line[3:]):
            continue
        if line:
            relevant.append(line)
    return code, tuple(relevant), stderr


def _check(name: str, status: CheckStatus, detail: str, **evidence: object) -> CheckResult:
    return CheckResult(name, status, detail, evidence)


def _capture(args: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)


def _read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _read_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a TOML table")
    return data


def _plugin_manifest_check(repo: Path, integration_id: str) -> CheckResult:
    path = repo / "plugins" / integration_id / ".codex-plugin" / "plugin.json"
    name = "ARENA_PLUGIN_MANIFEST" if integration_id == _ARENA_ID else "BROKER_PLUGIN_MANIFEST"
    try:
        data = _read_json(path)
        ok = data.get("name") == integration_id
        return _check(name, CheckStatus.PASS if ok else CheckStatus.FAIL, f"{path} {'matches' if ok else 'does not match'} plugin {integration_id}", path=str(path), plugin_name=data.get("name"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _check(name, CheckStatus.FAIL, f"plugin manifest unavailable or invalid: {exc}", path=str(path))


def _config_mcp_check(config: dict[str, object], integration_id: str, mcp_server: str, expected_tools: tuple[str, ...]) -> CheckResult:
    name = "ARENA_MCP_CONFIG" if integration_id == _ARENA_ID else "BROKER_MCP_CONFIG"
    plugin_key = f"{integration_id}@whitechronos-repo"
    plugins = config.get("plugins")
    plugin = plugins.get(plugin_key) if isinstance(plugins, dict) else None
    server = None
    if isinstance(plugin, dict):
        servers = plugin.get("mcp_servers")
        server = servers.get(mcp_server) if isinstance(servers, dict) else None
    enabled_tools = server.get("enabled_tools") if isinstance(server, dict) else None
    ok = (
        isinstance(plugin, dict)
        and plugin.get("enabled") is True
        and isinstance(server, dict)
        and server.get("enabled") is True
        and isinstance(enabled_tools, list)
        and tuple(enabled_tools) == expected_tools
    )
    return _check(name, CheckStatus.PASS if ok else CheckStatus.FAIL, f"{plugin_key}/{mcp_server} {'enabled with expected tools' if ok else 'is missing, disabled, or drifted'}", plugin=plugin_key, mcp_server=mcp_server)


def _broker_repo_binding_check(repo: Path) -> CheckResult:
    raw = os.environ.get("SUBAGENT_BROKER_REPO_ROOT")
    if not raw:
        return _check(
            "BROKER_REPO_BINDING",
            CheckStatus.USER_ACTION_REQUIRED,
            "SUBAGENT_BROKER_REPO_ROOT is not set in the current host environment",
            expected=str(repo),
            actual=None,
        )
    candidate = Path(raw)
    if not candidate.is_absolute():
        return _check(
            "BROKER_REPO_BINDING",
            CheckStatus.USER_ACTION_REQUIRED,
            "SUBAGENT_BROKER_REPO_ROOT must be an absolute path to the consumer repository",
            expected=str(repo),
            actual=raw,
        )
    try:
        resolved = candidate.resolve()
    except OSError as exc:
        return _check(
            "BROKER_REPO_BINDING",
            CheckStatus.USER_ACTION_REQUIRED,
            f"cannot resolve SUBAGENT_BROKER_REPO_ROOT: {exc}",
            expected=str(repo),
            actual=raw,
        )
    if resolved != repo:
        return _check(
            "BROKER_REPO_BINDING",
            CheckStatus.USER_ACTION_REQUIRED,
            "SUBAGENT_BROKER_REPO_ROOT does not match the diagnosed consumer repository",
            expected=str(repo),
            actual=str(resolved),
        )
    return _check(
        "BROKER_REPO_BINDING",
        CheckStatus.PASS,
        "SUBAGENT_BROKER_REPO_ROOT matches the diagnosed consumer repository",
        expected=str(repo),
        actual=str(resolved),
    )


def _local_probe_checks(inputs: DoctorInput, descriptor, codex_path: str) -> tuple[CheckResult, CheckResult, McpProbeResult | None]:
    prefix = "ARENA" if descriptor.id == _ARENA_ID else "BROKER"
    init_name = f"{prefix}_MCP_LOCAL_INITIALIZE"
    tools_name = f"{prefix}_MCP_LOCAL_TOOLS"
    try:
        launch = resolve_mcp_launch(inputs.repo_root, descriptor, codex_path=codex_path)
        result = probe_stdio_mcp(launch, expected_tools=descriptor.runtime_probe.expected_tools)
    except McpProbeSecurityError as exc:
        return (
            _check(init_name, CheckStatus.SECURITY_REVIEW_REQUIRED, str(exc)),
            _check(tools_name, CheckStatus.SECURITY_REVIEW_REQUIRED, str(exc)),
            None,
        )
    except Exception as exc:
        return (
            _check(init_name, CheckStatus.FAIL, f"local MCP probe failed: {exc}"),
            _check(tools_name, CheckStatus.FAIL, f"local MCP probe failed: {exc}"),
            None,
        )
    init_ok = bool(result.server_info) and "error" not in result.server_info
    return (
        _check(init_name, CheckStatus.PASS if init_ok else CheckStatus.FAIL, f"local MCP initialize {'succeeded' if init_ok else 'failed'}", server_info=result.server_info),
        _check(tools_name, result.status, f"local MCP tools: {', '.join(result.tools) if result.tools else 'none'}", tools=list(result.tools), missing=list(result.missing_tools), unexpected=list(result.unexpected_tools)),
        result,
    )


def _host_check(name: str, expected: tuple[str, ...], host_tools: frozenset[str], local_status: CheckStatus, *, inventory_observed: bool) -> CheckResult:
    if not inventory_observed:
        return _check(name, CheckStatus.UNAVAILABLE, "current host tool inventory was not supplied")
    if local_status is not CheckStatus.PASS:
        return _check(name, CheckStatus.FAIL, "local MCP health is not PASS; host discovery cannot be trusted")
    missing = tuple(tool for tool in expected if tool not in host_tools)
    if not missing:
        return _check(name, CheckStatus.PASS, "all expected tools are visible in the current host", tools=list(expected))
    return _check(name, CheckStatus.HOST_RELOAD_REQUIRED, f"local MCP is healthy but host is missing: {', '.join(missing)}", missing=list(missing))


def _feature_enabled(features: object, key: str, *, default: bool) -> bool:
    if not isinstance(features, dict) or key not in features:
        return default
    raw = features[key]
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, dict):
        enabled = raw.get("enabled")
        return default if enabled is None else enabled is True
    return False


def _native_tool_visible(
    host_tools: frozenset[str],
    tool: str,
    namespaces: tuple[str, ...],
) -> bool:
    if tool in host_tools:
        return True
    for namespace in namespaces:
        for separator in (".", "__", "/"):
            if f"{namespace}{separator}{tool}" in host_tools:
                return True
    return False


def _native_missing(
    host_tools: frozenset[str],
    expected: tuple[str, ...],
    namespaces: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        tool
        for tool in expected
        if not _native_tool_visible(host_tools, tool, namespaces)
    )


def _native_host_check(host_tools: frozenset[str], *, inventory_observed: bool) -> CheckResult:
    if not inventory_observed:
        return _check(
            "HOST_NATIVE_SUBAGENT_DISCOVERY",
            CheckStatus.UNAVAILABLE,
            "current host tool inventory was not supplied",
        )

    v2_missing = _native_missing(host_tools, _NATIVE_V2_TOOLS, _NATIVE_V2_NAMESPACES)
    if not v2_missing:
        return _check(
            "HOST_NATIVE_SUBAGENT_DISCOVERY",
            CheckStatus.PASS,
            "complete native Codex V2 subagent lifecycle is visible",
            version="v2",
            tools=list(_NATIVE_V2_TOOLS),
        )

    v1_missing = _native_missing(host_tools, _NATIVE_V1_TOOLS, _NATIVE_V1_NAMESPACES)
    if not v1_missing:
        return _check(
            "HOST_NATIVE_SUBAGENT_DISCOVERY",
            CheckStatus.PASS,
            "complete native Codex V1 subagent lifecycle is visible",
            version="v1",
            tools=list(_NATIVE_V1_TOOLS),
        )

    return _check(
        "HOST_NATIVE_SUBAGENT_DISCOVERY",
        CheckStatus.HOST_RELOAD_REQUIRED,
        "no complete native Codex V1 or V2 lifecycle is visible in the current host",
        v1_missing=list(v1_missing),
        v2_missing=list(v2_missing),
    )


def run_doctor(inputs: DoctorInput) -> DoctorReport:
    repo = Path(inputs.repo_root).resolve()
    checks: list[CheckResult] = []

    repo_ok = repo.is_dir() and (repo / ".git").exists()
    checks.append(_check("REPOSITORY_ROOT", CheckStatus.PASS if repo_ok else CheckStatus.FAIL, f"repository root: {repo}", path=str(repo)))

    head_code, head, head_err = _capture(["git", "rev-parse", "HEAD"], repo)
    head_ok = head_code == 0 and bool(head) and (inputs.expected_commit is None or head == inputs.expected_commit)
    head_detail = f"HEAD {head}" if head else f"git HEAD unavailable: {head_err}"
    if inputs.expected_commit is not None and head and head != inputs.expected_commit:
        head_detail = f"HEAD {head} does not match expected {inputs.expected_commit}"
    checks.append(_check("GIT_HEAD", CheckStatus.PASS if head_ok else CheckStatus.FAIL, head_detail, head=head, expected=inputs.expected_commit))

    status_code, status_lines, status_err = _worktree_changes(repo)
    clean = status_code == 0 and not status_lines
    status_text = "\n".join(status_lines)
    checks.append(_check("WORKTREE_STATE", CheckStatus.PASS if clean else CheckStatus.FAIL, "source-relevant worktree is clean" if clean else f"source-relevant worktree is dirty or unavailable: {status_text or status_err}", porcelain=status_text))

    config: dict[str, object] = {}
    try:
        config = _read_toml(repo / ".codex" / "config.toml")
        checks.append(_check("CODEX_CONFIG_PARSE", CheckStatus.PASS, ".codex/config.toml parsed successfully"))
    except Exception as exc:
        checks.append(_check("CODEX_CONFIG_PARSE", CheckStatus.FAIL, f"cannot parse .codex/config.toml: {exc}"))

    try:
        _read_json(repo / ".agents" / "plugins" / "marketplace.json")
        checks.append(_check("MARKETPLACE_PARSE", CheckStatus.PASS, ".agents/plugins/marketplace.json parsed successfully"))
    except Exception as exc:
        checks.append(_check("MARKETPLACE_PARSE", CheckStatus.FAIL, f"cannot parse marketplace.json: {exc}"))

    plugins = config.get("plugins") if isinstance(config, dict) else None
    superpowers = plugins.get("superpowers@openai-curated") if isinstance(plugins, dict) else None
    super_ok = isinstance(superpowers, dict) and superpowers.get("enabled") is True
    checks.append(_check("SUPERPOWERS_CONFIG", CheckStatus.PASS if super_ok else CheckStatus.FAIL, "official Superpowers plugin is enabled" if super_ok else "official Superpowers plugin is not enabled"))

    registry = load_registry(repo)
    arena = registry[_ARENA_ID]
    broker = registry[_BROKER_ID]
    checks.append(_plugin_manifest_check(repo, _ARENA_ID))
    checks.append(_config_mcp_check(config, _ARENA_ID, arena.runtime_probe.mcp_server, arena.runtime_probe.expected_tools))
    arena_init, arena_tools, _ = _local_probe_checks(inputs, arena, inputs.codex_path)
    checks.extend((arena_init, arena_tools))
    checks.append(_plugin_manifest_check(repo, _BROKER_ID))
    checks.append(_config_mcp_check(config, _BROKER_ID, broker.runtime_probe.mcp_server, broker.runtime_probe.expected_tools))
    broker_init, broker_tools, _ = _local_probe_checks(inputs, broker, inputs.codex_path)
    checks.extend((broker_init, broker_tools))
    broker_binding = _broker_repo_binding_check(repo)
    checks.append(broker_binding)

    node_code, node_out, _ = _capture(["node", "--version"], repo)
    checks.append(_check("NODE_VERSION", CheckStatus.PASS if node_code == 0 else CheckStatus.UNAVAILABLE, node_out or "node unavailable", version=node_out))
    git_code, git_out, _ = _capture(["git", "--version"], repo)
    checks.append(_check("GIT_VERSION", CheckStatus.PASS if git_code == 0 else CheckStatus.UNAVAILABLE, git_out or "git unavailable", version=git_out))

    caps = probe_codex_cli(inputs.codex_path)
    checks.append(_check("CODEX_VERSION", CheckStatus.PASS if caps.version != "unavailable" else CheckStatus.UNAVAILABLE, caps.version, version=caps.version))
    checks.append(_check("CODEX_EXEC", CheckStatus.PASS if caps.exec else (CheckStatus.UNAVAILABLE if caps.version == "unavailable" else CheckStatus.FAIL), "codex exec available" if caps.exec else "codex exec unavailable"))
    checks.append(_check("CODEX_EXEC_JSON", CheckStatus.PASS if caps.json else (CheckStatus.UNAVAILABLE if not caps.exec else CheckStatus.FAIL), "codex exec --json available" if caps.json else "codex exec --json unavailable"))
    checks.append(_check("CODEX_RESUME", CheckStatus.PASS if caps.resume else CheckStatus.UNAVAILABLE, "codex exec resume available" if caps.resume else "codex exec resume unavailable"))

    agents = config.get("agents") if isinstance(config, dict) else None
    native_enabled = True if not isinstance(agents, dict) else agents.get("enabled", True) is True
    features = config.get("features") if isinstance(config, dict) else None
    multi_agent_v1_enabled = _feature_enabled(features, "multi_agent", default=True)
    multi_agent_v2_enabled = _feature_enabled(features, "multi_agent_v2", default=False)
    multi_agent_v1_effective = native_enabled and multi_agent_v1_enabled
    multi_agent_v2_effective = multi_agent_v2_enabled
    native_config_ok = multi_agent_v2_effective or multi_agent_v1_effective
    if native_config_ok:
        enabled_versions = [
            version
            for version, enabled in (
                ("v1", multi_agent_v1_effective),
                ("v2", multi_agent_v2_effective),
            )
            if enabled
        ]
        native_config = _check(
            "NATIVE_MULTI_AGENT_CONFIG",
            CheckStatus.PASS,
            f"native Codex multi-agent configuration is eligible via {', '.join(enabled_versions)}",
            agents_enabled=native_enabled,
            multi_agent_v1_enabled=multi_agent_v1_enabled,
            multi_agent_v2_enabled=multi_agent_v2_enabled,
            multi_agent_v1_effective=multi_agent_v1_effective,
            multi_agent_v2_effective=multi_agent_v2_effective,
        )
    else:
        native_config = _check(
            "NATIVE_MULTI_AGENT_CONFIG",
            CheckStatus.FAIL,
            "repository configuration does not guarantee an enabled native Codex multi-agent route",
            agents_enabled=native_enabled,
            multi_agent_v1_enabled=multi_agent_v1_enabled,
            multi_agent_v2_enabled=multi_agent_v2_enabled,
            multi_agent_v1_effective=multi_agent_v1_effective,
            multi_agent_v2_effective=multi_agent_v2_effective,
        )
    checks.append(native_config)

    inventory_observed = inputs.host_inventory_observed or bool(inputs.host_tools)
    arena_host = _host_check("HOST_ARENA_DISCOVERY", arena.runtime_probe.expected_tools, inputs.host_tools, arena_tools.status, inventory_observed=inventory_observed)
    broker_host = _host_check("HOST_BROKER_DISCOVERY", broker.runtime_probe.expected_tools, inputs.host_tools, broker_tools.status, inventory_observed=inventory_observed)
    if broker_host.status is CheckStatus.PASS and broker_binding.status is not CheckStatus.PASS:
        broker_host = _check(
            "HOST_BROKER_DISCOVERY",
            broker_binding.status,
            "Broker lifecycle is host-visible but the consumer repository binding is not valid",
            binding_status=broker_binding.status.value,
        )
    elif broker_host.status is CheckStatus.PASS and not caps.resume:
        broker_host = _check(
            "HOST_BROKER_DISCOVERY",
            CheckStatus.FAIL,
            "Broker lifecycle is host-visible but codex exec resume is unavailable",
            codex_resume=False,
        )
    checks.extend((arena_host, broker_host))
    native_host = _native_host_check(inputs.host_tools, inventory_observed=inventory_observed)
    checks.append(native_host)

    if native_host.status is CheckStatus.PASS:
        selected = "native_codex_multi_agent"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.PASS, "native Codex multi-agent route is available", route=selected)
    elif broker_host.status is CheckStatus.PASS:
        selected = "subagent_broker"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.PASS, "Subagent Broker route is available", route=selected)
    elif not inventory_observed:
        selected = "superpowers_inline"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.UNAVAILABLE, "current host tool inventory was not supplied", route=selected)
    elif native_host.status is CheckStatus.HOST_RELOAD_REQUIRED or broker_host.status is CheckStatus.HOST_RELOAD_REQUIRED:
        selected = "superpowers_inline"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.HOST_RELOAD_REQUIRED, "no complete independent-subagent lifecycle is visible in the current host", route=selected)
    elif native_host.status is CheckStatus.USER_ACTION_REQUIRED or broker_host.status is CheckStatus.USER_ACTION_REQUIRED:
        selected = "superpowers_inline"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.USER_ACTION_REQUIRED, "independent-subagent lifecycle needs host environment action before it is usable", route=selected)
    else:
        selected = "superpowers_inline"
        subagent_host = _check("HOST_SUBAGENT_DISCOVERY", CheckStatus.FAIL, "no healthy independent-subagent route is available", route=selected)
    checks.append(subagent_host)

    required_ok = (
        repo_ok
        and head_ok
        and clean
        and broker_tools.status is CheckStatus.PASS
        and next(item for item in checks if item.name == "BROKER_MCP_CONFIG").status is CheckStatus.PASS
        and caps.exec
        and caps.json
        and caps.resume
        and broker_binding.status is CheckStatus.PASS
        and inputs.runtime_kind in _TRUSTED_RUNTIME_KINDS
        and broker_host.status is CheckStatus.PASS
    )

    blockers: list[str] = []
    if arena_host.status is CheckStatus.HOST_RELOAD_REQUIRED:
        blockers.append("ARENA_HOST_RELOAD_REQUIRED")
    if broker_host.status is CheckStatus.HOST_RELOAD_REQUIRED:
        blockers.append("BROKER_HOST_RELOAD_REQUIRED")
    if subagent_host.status is CheckStatus.HOST_RELOAD_REQUIRED:
        blockers.append("HOST_RELOAD_REQUIRED")
    if broker_host.status is CheckStatus.USER_ACTION_REQUIRED or subagent_host.status is CheckStatus.USER_ACTION_REQUIRED:
        blockers.append("USER_ACTION_REQUIRED")
    if inputs.runtime_kind not in _TRUSTED_RUNTIME_KINDS:
        blockers.append("USER_ACTION_REQUIRED")
    for item in checks:
        if item.name in {"GIT_HEAD", "WORKTREE_STATE", "BROKER_MCP_CONFIG", "BROKER_MCP_LOCAL_TOOLS", "BROKER_REPO_BINDING", "CODEX_EXEC", "CODEX_EXEC_JSON", "CODEX_RESUME"} and item.status not in {CheckStatus.PASS, CheckStatus.NOT_APPLICABLE}:
            blockers.append(item.name)
    blockers = list(dict.fromkeys(blockers))

    if required_ok:
        live_status = CheckStatus.PASS
        live_detail = "Broker live smoke prerequisites are satisfied"
    elif broker_host.status is CheckStatus.HOST_RELOAD_REQUIRED:
        live_status = CheckStatus.HOST_RELOAD_REQUIRED
        live_detail = "local Broker MCP is healthy but the current host must reload it in a fresh Codex environment/session"
    elif broker_host.status is CheckStatus.USER_ACTION_REQUIRED or broker_binding.status is CheckStatus.USER_ACTION_REQUIRED:
        live_status = CheckStatus.USER_ACTION_REQUIRED
        live_detail = "the Broker consumer repository binding must be set to the diagnosed repository"
    elif inputs.runtime_kind not in _TRUSTED_RUNTIME_KINDS:
        live_status = CheckStatus.USER_ACTION_REQUIRED
        live_detail = "a fresh trusted remote/network Codex runtime is required"
    else:
        live_status = CheckStatus.FAIL
        live_detail = "one or more Broker live-smoke prerequisites are not satisfied"
    checks.append(_check("LIVE_SMOKE_READY", live_status, live_detail, runtime_kind=inputs.runtime_kind))

    return DoctorReport(tuple(checks), selected, required_ok, tuple(blockers))


def report_to_json(report: DoctorReport) -> dict[str, object]:
    return {
        "checks": [
            {"name": item.name, "status": item.status.value, "detail": item.detail, "evidence": item.evidence}
            for item in report.checks
        ],
        "selected_subagent_path": report.selected_subagent_path,
        "live_smoke_ready": report.live_smoke_ready,
        "blockers": list(report.blockers),
    }


def render_report(report: DoctorReport) -> str:
    lines = ["CHECK\tSTATUS\tDETAIL"]
    lines.extend(f"{item.name}\t{item.status.value}\t{item.detail}" for item in report.checks)
    lines.append(f"SELECTED_SUBAGENT_PATH\t{report.selected_subagent_path}")
    lines.append(f"LIVE_SMOKE_READY\t{'YES' if report.live_smoke_ready else 'NO'}")
    if "HOST_RELOAD_REQUIRED" in report.blockers:
        lines.append("NEXT_ACTION\tStart a fresh Codex environment/session and reload project plugins; do not change source for a stale-host diagnosis.")
    elif "BROKER_REPO_BINDING" in report.blockers:
        lines.append("NEXT_ACTION\tSet SUBAGENT_BROKER_REPO_ROOT to the canonical consumer repository root before using the Broker route.")
    return "\n".join(lines) + "\n"
