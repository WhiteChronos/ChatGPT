# REA Internal Remote MCP Smoke — Design (28 Oct 2026)

**Goal:** Progress the independent REA static-analysis MCP toward a secure operator-approved HTTPS endpoint without claiming it already exists.

**Constraints:** The REA internal engine is NOT official `morluto/rea`; no MCE dependency; read-only tools, authorized root, secret handling and loopback bind remain intact. Never deploy direct HTTP to public Internet.

## Alternatives

- Expose current loopback listener on `0.0.0.0`: **rejected**, unsafe token and source boundary.
- Static Pages deployment: **rejected**, cannot host MCP server or local filesystem.
- Secure managed container/VM with TLS and identity-aware reverse proxy: **recommended**, requires separate operator authorization, infrastructure and security review.
- Local read-only HTTPS smoke harness plus negative tests: **selected immediate implementation**, executable independently now; never bypasses live host acceptance.

## Acceptance boundaries

1. The smoke refuses HTTP, URL credentials, query-token exposure, invalid endpoint paths, and missing environment secret before network calls.
2. It uses TLS-verified client defaults, rejects redirects, validates unauthenticated denial and calls safe MCP methods only.
3. It validates seven independent REA tool names but never treats test doubles as real live evidence.
4. It cannot return `production_complete=true` without a separate observed ChatGPT host discovery, operational acceptance, rollback and security review.

**Non-goals:** Provisioning tokens/hosting, activating official upstream `rea-agents`, public source exposure, auto-merging REA PR.
