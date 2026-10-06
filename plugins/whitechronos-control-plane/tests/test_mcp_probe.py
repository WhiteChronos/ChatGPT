from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO / "plugins" / "whitechronos-control-plane"
sys.path.insert(0, str(PLUGIN_ROOT))

from runtime.mcp_probe import McpLaunchSpec, McpProbeSecurityError, probe_stdio_mcp, resolve_mcp_launch
from runtime.model import CheckStatus, IntegrationDescriptor, RuntimeProbeSpec
from runtime.registry import load_registry


def test_arena_local_probe_lists_exact_expected_tools():
    descriptor = load_registry(REPO)["github-arena"]
    launch = resolve_mcp_launch(REPO, descriptor)
    result = probe_stdio_mcp(launch, expected_tools=descriptor.runtime_probe.expected_tools)
    assert result.status is CheckStatus.PASS
    assert result.tools == descriptor.runtime_probe.expected_tools
    assert result.server_info["name"] == "github-arena"


def test_broker_local_probe_lists_exact_expected_tools_with_fake_codex():
    descriptor = load_registry(REPO)["subagent-broker"]
    fake_codex = REPO / "plugins" / "subagent-broker" / "tests" / "fake-codex.mjs"
    launch = resolve_mcp_launch(REPO, descriptor, codex_path=str(fake_codex))
    result = probe_stdio_mcp(launch, expected_tools=descriptor.runtime_probe.expected_tools)
    assert result.status is CheckStatus.PASS
    assert result.tools == descriptor.runtime_probe.expected_tools
    assert launch.env["SUBAGENT_BROKER_CODEX_PATH"] == str(fake_codex)
    assert launch.env["SUBAGENT_BROKER_REPO_ROOT"] == str(REPO.resolve())


def test_probe_rejects_shell_or_unknown_command_without_execution(tmp_path):
    plugin = tmp_path / "repo" / "plugins" / "unsafe"
    plugin.mkdir(parents=True)
    marker = tmp_path / "executed"
    (plugin / ".mcp.json").write_text(json.dumps({"mcpServers":{"unsafe":{"type":"stdio","command":"sh","args":["-c",f"touch {marker}"],"cwd":"."}}}), encoding="utf-8")
    descriptor = IntegrationDescriptor(
        id="unsafe", display_name="Unsafe", source_type="local", source="plugins/unsafe",
        license_status="MIT", execution_class="LOCAL_MUTATING", status="REGISTERED_PROJECT",
        controller_plugin="unsafe", skill_paths=(), mcp_servers=("unsafe",),
        runtime_probe=RuntimeProbeSpec("plugins/unsafe", ".mcp.json", "unsafe", ("x",), False),
    )
    with pytest.raises(McpProbeSecurityError):
        resolve_mcp_launch(tmp_path / "repo", descriptor)
    assert not marker.exists()


def test_probe_reports_missing_tool_as_failure(tmp_path):
    script = tmp_path / "server.mjs"
    script.write_text("""import readline from 'node:readline';const r=readline.createInterface({input:process.stdin});r.on('line',l=>{const q=JSON.parse(l);if(q.method==='notifications/initialized')return;const result=q.method==='initialize'?{serverInfo:{name:'tiny',version:'1'},capabilities:{tools:{}},protocolVersion:'2025-11-25'}:{tools:[{name:'one'}]};process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:q.id,result})+'\\n')});""", encoding="utf-8")
    launch = McpLaunchSpec(command="node", args=(str(script),), cwd=tmp_path, env={"PATH": os.environ["PATH"]})
    result = probe_stdio_mcp(launch, expected_tools=("one", "two"))
    assert result.status is CheckStatus.FAIL
    assert result.missing_tools == ("two",)


def test_probe_times_out_and_terminates_child(tmp_path):
    marker = tmp_path / "terminated"
    script = tmp_path / "hang.mjs"
    script.write_text("""import fs from 'node:fs';process.on('SIGTERM',()=>{fs.writeFileSync(process.env.MARKER,'yes');process.exit(0)});setInterval(()=>{},1000);""", encoding="utf-8")
    launch = McpLaunchSpec(command="node", args=(str(script),), cwd=tmp_path, env={"PATH": os.environ["PATH"], "MARKER": str(marker)})
    started = time.monotonic()
    result = probe_stdio_mcp(launch, expected_tools=("never",), timeout_seconds=0.25)
    assert result.status is CheckStatus.FAIL
    assert time.monotonic() - started < 2.0
    assert marker.exists()

def test_broker_launch_rejects_manifest_without_repo_root_env_passthrough(tmp_path):
    repo = tmp_path / "repo"
    plugin = repo / "plugins" / "subagent-broker"
    server = plugin / "mcp-server" / "mcp_server.mjs"
    server.parent.mkdir(parents=True)
    server.write_text("process.exit(0);\n", encoding="utf-8")
    (plugin / ".mcp.json").write_text(
        json.dumps({
            "mcpServers": {
                "subagent_broker": {
                    "type": "stdio",
                    "command": "node",
                    "args": ["./mcp-server/mcp_server.mjs"],
                    "cwd": "."
                }
            }
        }),
        encoding="utf-8",
    )
    descriptor = IntegrationDescriptor(
        id="subagent-broker",
        display_name="Subagent Broker",
        source_type="local",
        source="plugins/subagent-broker",
        license_status="MIT",
        execution_class="LOCAL_MUTATING",
        status="REGISTERED_PROJECT",
        controller_plugin="subagent-broker",
        skill_paths=(),
        mcp_servers=("subagent_broker",),
        runtime_probe=RuntimeProbeSpec(
            "plugins/subagent-broker",
            ".mcp.json",
            "subagent_broker",
            ("subagent_spawn",),
            True,
        ),
    )
    with pytest.raises(McpProbeSecurityError, match="SUBAGENT_BROKER_REPO_ROOT"):
        resolve_mcp_launch(repo, descriptor)

