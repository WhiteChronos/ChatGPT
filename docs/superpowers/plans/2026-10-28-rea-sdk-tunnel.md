# REA private MCP adapter — implementation plan

> For agentic workers: REQUIRED SUB-SKILL `superpowers:executing-plans` or `superpowers:subagent-driven-development`. Preserve TDD and review gates.

**Goal:** Enable the independent REA internal engine through the official MCP SDK and a documented private connection path.

**Architecture:** Adapter in a new file registers existing backend functions; protocol handling is delegated to the official SDK. Connection uses stdio inside Secure MCP Tunnel, avoiding public ingress.

**Tech Stack:** Python 3.12+, `mcp>=2.2,<3`, `pytest`, `uvicorn`, official `tunnel-client` (operator-installed).

**Spec:** `docs/superpowers/specs/2026-10-28-rea-sdk-tunnel-design.md`.

## Global constraints

- No MCE dependency, no private source upload, no public 0.0.0.0 bind.
- Keep existing bridge and local tests; fail closed for forbidden files.
- Do not create keys, OAuth identity or production host automatically.

## Review focus

1. The tool inventory must contain exactly seven names, none related to other products.
2. Path traversal errors must not leak absolute paths.
3. `0.0.0.0` and `::` listeners must be rejected.
4. Invalid Host/Origin HTTP requests must be rejected by SDK.
5. Mock-only JSON-RPC tests cannot substitute actual official SDK client tests.

### Task 1 — TDD SDK adapter

**Files:** `systems/rea/tests/test_sdk_bridge.py`, `systems/rea/src/sdk_server.py`.

- [x] RED: make a fake SDK verify seven handlers, filesystem confinement and public binding denial; observe missing-module failures.
- [x] GREEN: create seven official SDK declarations delegated to existing read-only engine.
- [x] RED: require read-only, non-destructive tool annotations; observe failure.
- [x] GREEN: declare appropriate `ToolAnnotations` for all seven handlers.
- [x] Run local test suite; SDK-only client tests are expected to skip offline if SDK cannot be installed.
- [ ] Run official SDK integration tests on GitHub Actions on exact current SHA: inproc, stdio, Streamable HTTP, DNS rebinding security.

### Task 2 — CI + operator runbook

**Files:** `systems/rea/requirements-mcp.txt`, `.github/workflows/rea-independent-qa.yml`, `systems/rea/docs/PRIVATE_MCP_TUNNEL.md`, `systems/rea/README.md`.

- [x] Install official SDK in PR CI and require full suite.
- [x] Document private outbound-only tunnel, allowed data directory, Tunnels RBAC and ChatGPT plugin setup.
- [ ] Run real `tunnel-client doctor` and observed tool call in ChatGPT workspace.

### Task 3 — Release and operational acceptance

- [ ] Review, approve and merge exact PR SHA under Chronos protection.
- [ ] Configure a long-running service and tunnel in approved host/organization, with recovery and approved access.
- [ ] Store evidence of DNS/host protections, access revocation, remote tool discovery and operational signoff.
