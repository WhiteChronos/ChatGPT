# REA private official MCP SDK adapter — design

Goal: standardize the seven existing read-only REA tools on a supported MCP SDK transport, preserving the independently implemented static engine and its path policy without changing the MCE system.

## Arena alternatives

1. Expose old `http.server` bridge directly to the Internet: **rejected** (partial MCP semantics, static token and data exposure).
2. Build custom OAuth and HTTP protocol from scratch: **rejected** (unreviewed security and protocol implementation).
3. Use official Python MCP SDK v2 for stdio/loopback HTTP and **Secure MCP Tunnel** for remote private ChatGPT use: **selected**, pending host credentials, deployment and acceptance.
4. Copy `morluto/rea` upstream in-tree: **rejected** (distinct product, licenses and unverified runtime).

## Contract

`src/sdk_server.py` builds `MCPServer` from official `mcp>=2.2,<3`, registers the seven exact tool names and declares `ToolAnnotations` read-only. Invocations delegate exclusively to `ReaBridge._call` with the original path sanitization and size limits. Tool exceptions are sanitized. CLI supports stdio and Streamable HTTP only on loopback; no public listener or credential in code. Existing `src/server.py` remains backwards compatible and intentionally local. The official SDK client must negotiate, list, and call tools over in-process, stdio and loopback HTTP; DNS rebinding Host/Origin attacks must fail.

## Boundaries

ChatGPT Web connection and Secure MCP Tunnel are separate real-host gates: operator-provided tunnel ID, OpenAI Platform/workspace permissions, managed API key, long-running host, client discovery, monitoring and rollback. CI is not that acceptance; no numeric '100%' can be asserted without them.
