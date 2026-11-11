#!/usr/bin/env python3
"""Official MCP SDK adapter for the independent read-only static REA engine.

Runs only on localhost or via a separately managed private tunnel. It does
not create an OAuth provider, a public listener or a production deployment.
The legacy local bridge remains available and is not changed by this adapter.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from bridge import ReaBridge, SERVER_NAME

APP_ROOT = Path(__file__).resolve().parents[1]
SAFE_HOSTS = frozenset({'127.0.0.1', 'localhost', '::1'})


def assert_safe_bind(host: str) -> str:
    if host not in SAFE_HOSTS:
        raise ValueError('Public MCP listening address is forbidden; use a private secure tunnel')
    return host


def build_server(root: Path):
    """Register seven read-only tools through the official MCP Python SDK v2."""
    from mcp.server import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
    from mcp.types import ToolAnnotations

    bridge = ReaBridge(Path(root), APP_ROOT)
    mcp = MCPServer(SERVER_NAME, instructions=(
        'Read-only source inspection of an explicitly authorized directory. '
        'Static metadata only; no code execution, file modification or auto-approval.'))

    def invoke(name: str, **kwargs) -> dict:
        try:
            # The existing engine validates tool names, argument structure,
            # paths, symlinks, sensitive filenames and source-size limits.
            return bridge._call(name, kwargs)
        except Exception:
            # Never reveal filesystem roots, source names or secrets to MCP clients.
            raise ToolError('Read-only inspection blocked by source policy') from None

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_bridge_status() -> dict:
        """Report whether an independent upstream runtime is truly available."""
        return invoke('rea_bridge_status')

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_source_inspect(file: str) -> dict:
        """Read source metadata and its SHA-256, never source bodies."""
        return invoke('rea_source_inspect', file=file)

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_project_inventory(directory: str = '.', limit: int = 250) -> dict:
        """Bounded read-only inventory under the authorized root."""
        return invoke('rea_project_inventory', directory=directory, limit=limit)

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_internal_analyze(directory: str = '.', limit: int = 100) -> dict:
        """Static import graph and source metadata, no program execution."""
        return invoke('rea_internal_analyze', directory=directory, limit=limit)

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_arena_compare(objective: str = 'source_analysis', confidentiality: str = 'high') -> dict:
        """Four heuristic policy perspectives, not independent subagents."""
        return invoke('rea_arena_compare', objective=objective, confidentiality=confidentiality)

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_repositories_top10(catalog: str) -> dict:
        """Evaluate a user-supplied local catalog, never scrape or install."""
        return invoke('rea_repositories_top10', catalog=catalog)

    @mcp.tool(annotations=ToolAnnotations(read_only_hint=True,
            destructive_hint=False, open_world_hint=False, idempotent_hint=True))
    def rea_verify_evidence(file: str, expected_sha256: str) -> dict:
        """Verify an authorized local file digest without changing content."""
        return invoke('rea_verify_evidence', file=file, expected_sha256=expected_sha256)

    return mcp


def serve(mcp, *, transport: str, host: str = '127.0.0.1', port: int = 8768) -> None:
    if transport == 'stdio':
        mcp.run(transport='stdio')
        return
    if transport != 'streamable-http':
        raise ValueError('Unsupported MCP transport')
    assert_safe_bind(host)
    if not isinstance(port, int) or isinstance(port, bool) or not (1 <= port <= 65535):
        raise ValueError('Port must be between 1 and 65535')
    # The official SDK enables Host/Origin DNS-rebinding protection for
    # localhost. Never disable it to get a green remote test.
    mcp.run(transport='streamable-http', host=host, port=port,
            stateless_http=True, json_response=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True, type=Path, help='Authorized directory for read-only inspection')
    p.add_argument('--transport', default='stdio', choices=('stdio', 'streamable-http'))
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', default=8768, type=int)
    a = p.parse_args()
    assert_safe_bind(a.host)  # Deny public bind even when stdio is chosen.
    serve(build_server(a.root), transport=a.transport, host=a.host, port=a.port)


if __name__ == '__main__':
    main()
