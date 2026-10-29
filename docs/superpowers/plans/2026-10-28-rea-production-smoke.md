# REA Internal Production Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a secure remote HTTPS smoke diagnostic to the existing independent REA engine.

**Architecture:** Leave the read-only MCP server on localhost; the new probe communicates with a separately authorized HTTPS proxy endpoint. Operator-managed token stays in environment, output excludes source and token.

**Tech Stack:** Python >=3.12, urllib/ssl standard library, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-28-rea-production-smoke-design.md`

## Global Constraints

- Keep 7 tool names independent and readonly; no MCE imports.
- Do not deploy, create secrets, or claim host plugin discovery automatically.
- Fail closed on insecure URL, redirects, authentication bypass and missing tools.

## Review Focus

1. HTTP and query-token links cannot be probed.
2. No token means zero outbound requests.
3. Wrong server/tool inventory blocks.
4. Redirects must not forward `Authorization`.
5. No successful mock can elevate `host_discovered` or `production_complete`.

### Task 1: Authenticated read-only HTTPS probe (implemented locally, pending PR CI)

**Files:** Create `systems/rea/scripts/production_smoke.py`, `systems/rea/tests/test_production_smoke.py`.

- [x] Test insecure URL, token absence, tool inventory, auth negative path and redirect rejection; observe TDD red.
- [x] Implement `assess(url, token, opener=None) -> dict` with HTTPS validation, redirect refusal and bounded JSON-RPC.
- [x] Verify focused regression, no token leakage, safe real CLI no-endpoint BLOCKED.
- [ ] Verify new tests on exact PR HEAD via GitHub Actions.

### Task 2: Real canary and hosted acceptance (requires operator approval)

**Files:** `systems/rea/docs/PRODUCTION_ACCEPTANCE.md`, deployment host records and customer-owned credentials.

- [ ] Identify authorized existing host or obtain separate infrastructure/cost/credential approval.
- [ ] Deploy private canary with TLS, SSO/OAuth or equivalent operator security, least privilege and rollback.
- [ ] Execute real HTTPS smoke and negative access tests; save endpoint and SHA-linked evidence.
- [ ] Register approved MCP in ChatGPT Web and verify `tools/list` observed by the connected host.
- [ ] Confirm operations/security owner, monitoring, rollback and user acceptance before `PRODUCTION_COMPLETE`.
