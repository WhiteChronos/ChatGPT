from __future__ import annotations

import json
import os
import selectors
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from .model import CheckStatus, IntegrationDescriptor, McpProbeResult


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


class McpProbeSecurityError(ValueError):
    status = CheckStatus.SECURITY_REVIEW_REQUIRED


@dataclass(frozen=True)
class McpLaunchSpec:
    command: str
    args: tuple[str, ...]
    cwd: Path
    env: dict[str, str]


def _contained(base: Path, candidate: Path, label: str) -> Path:
    base = base.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise McpProbeSecurityError(f"{label} must stay within plugin_root") from exc
    return candidate


def _minimal_env(*, codex_path: str | None = None) -> dict[str, str]:
    env = {key: os.environ[key] for key in _SAFE_ENV_KEYS if key in os.environ}
    if codex_path is not None:
        env["SUBAGENT_BROKER_CODEX_PATH"] = codex_path
    return env


def resolve_mcp_launch(
    repo_root: Path,
    descriptor: IntegrationDescriptor,
    *,
    codex_path: str = "codex",
) -> McpLaunchSpec:
    probe = descriptor.runtime_probe
    if probe is None:
        raise ValueError(f"integration {descriptor.id} has no runtime_probe")
    repo_root = Path(repo_root).resolve()
    plugin_root = _contained(repo_root, repo_root / probe.plugin_root, "runtime_probe.plugin_root")
    config_path = _contained(plugin_root, plugin_root / probe.mcp_config, "runtime_probe.mcp_config")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read MCP config {config_path}: {exc}") from exc
    servers = config.get("mcpServers") if isinstance(config, dict) else None
    server = servers.get(probe.mcp_server) if isinstance(servers, dict) else None
    if not isinstance(server, dict):
        raise ValueError(f"MCP server {probe.mcp_server!r} not found in {config_path}")
    if server.get("type") != "stdio":
        raise McpProbeSecurityError("only stdio MCP servers are allowed by Runtime Foundation")
    command = server.get("command")
    if command != "node":
        raise McpProbeSecurityError(f"unsupported MCP probe command: {command!r}")
    raw_args = server.get("args")
    if not isinstance(raw_args, list) or len(raw_args) != 1 or not isinstance(raw_args[0], str):
        raise McpProbeSecurityError("Runtime Foundation allows exactly one Node script argument")
    raw_cwd = server.get("cwd", ".")
    if not isinstance(raw_cwd, str):
        raise McpProbeSecurityError("MCP cwd must be a string")
    cwd = _contained(plugin_root, plugin_root / raw_cwd, "MCP cwd")
    script = _contained(plugin_root, cwd / raw_args[0], "MCP script")
    if script.suffix != ".mjs":
        raise McpProbeSecurityError("MCP Node entrypoint must be an .mjs file")
    env = _minimal_env(codex_path=codex_path if descriptor.id == "subagent-broker" else None)
    if descriptor.id == "subagent-broker":
        env["SUBAGENT_BROKER_REPO_ROOT"] = str(repo_root)
    return McpLaunchSpec(command="node", args=(str(script),), cwd=cwd, env=env)


def _terminate(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait(timeout=0.5)


def probe_stdio_mcp(
    launch: McpLaunchSpec,
    *,
    expected_tools: tuple[str, ...],
    timeout_seconds: float = 5.0,
) -> McpProbeResult:
    child = subprocess.Popen(
        [launch.command, *launch.args],
        cwd=launch.cwd,
        env=launch.env,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert child.stdin is not None and child.stdout is not None and child.stderr is not None
    selector = selectors.DefaultSelector()
    selector.register(child.stdout, selectors.EVENT_READ, "stdout")
    selector.register(child.stderr, selectors.EVENT_READ, "stderr")
    os.set_blocking(child.stdout.fileno(), False)
    os.set_blocking(child.stderr.fileno(), False)
    stdout_buffer = bytearray()
    stderr_buffer = bytearray()
    responses: dict[int, dict[str, object]] = {}
    sent_list = False
    deadline = time.monotonic() + max(0.01, timeout_seconds)

    def send(payload: dict[str, object]) -> None:
        child.stdin.write((json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8"))
        child.stdin.flush()

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "whitechronos-runtime-doctor", "version": "0.1.0"}}})
    try:
        while time.monotonic() < deadline and 2 not in responses:
            remaining = max(0.0, deadline - time.monotonic())
            for key, _ in selector.select(remaining):
                try:
                    chunk = os.read(key.fileobj.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    try:
                        selector.unregister(key.fileobj)
                    except Exception:
                        pass
                    continue
                if key.data == "stderr":
                    stderr_buffer.extend(chunk)
                    if len(stderr_buffer) > 65536:
                        del stderr_buffer[:-65536]
                    continue
                stdout_buffer.extend(chunk)
                while b"\n" in stdout_buffer:
                    raw, _, rest = stdout_buffer.partition(b"\n")
                    stdout_buffer = bytearray(rest)
                    if not raw.strip():
                        continue
                    try:
                        message = json.loads(raw.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                    if isinstance(message, dict) and isinstance(message.get("id"), int):
                        responses[int(message["id"])] = message
            if 1 in responses and not sent_list:
                send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
                send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
                sent_list = True
    finally:
        _terminate(child)
        selector.close()

    stderr_tail = stderr_buffer.decode("utf-8", errors="replace")[-8192:]
    init = responses.get(1)
    listed = responses.get(2)
    if init is None or listed is None:
        return McpProbeResult(
            server_name="unknown",
            status=CheckStatus.FAIL,
            server_info={"error": "MCP probe timed out or returned incomplete JSON-RPC responses"},
            tools=(),
            missing_tools=tuple(expected_tools),
            unexpected_tools=(),
            stderr_tail=stderr_tail,
        )
    init_result = init.get("result") if isinstance(init, dict) else None
    list_result = listed.get("result") if isinstance(listed, dict) else None
    server_info = init_result.get("serverInfo", {}) if isinstance(init_result, dict) else {}
    raw_tools = list_result.get("tools", []) if isinstance(list_result, dict) else []
    tools = tuple(item.get("name") for item in raw_tools if isinstance(item, dict) and isinstance(item.get("name"), str))
    missing = tuple(name for name in expected_tools if name not in tools)
    unexpected = tuple(name for name in tools if name not in expected_tools)
    exact = tools == tuple(expected_tools)
    return McpProbeResult(
        server_name=str(server_info.get("name", "unknown")) if isinstance(server_info, dict) else "unknown",
        status=CheckStatus.PASS if exact else CheckStatus.FAIL,
        server_info=dict(server_info) if isinstance(server_info, dict) else {},
        tools=tools,
        missing_tools=missing,
        unexpected_tools=unexpected,
        stderr_tail=stderr_tail,
    )
