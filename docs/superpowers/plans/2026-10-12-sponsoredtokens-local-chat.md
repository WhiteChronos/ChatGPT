# SponsoredTokens-Only Local Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private loopback browser chat and local Codex workflow that use SponsoredTokens only, without exposing or persisting the key and without any local OpenAI API path.

**Architecture:** A Python standard-library `ThreadingHTTPServer` serves fixed same-origin assets and two JSON routes. A single SponsoredTokens adapter owns the bounded Responses-compatible request; the browser keeps session history only in memory. ChatGPT web remains account/plan based and is outside this local application.

**Tech Stack:** Python 3 standard library (`http.server`, `urllib.request`, `unittest`), vanilla HTML/CSS/JavaScript, PowerShell operator workflow.

**Spec:** `docs/superpowers/specs/2026-10-12-sponsoredtokens-local-chat-design.md`

## Global Constraints

- Only `SPONSOREDTOKENS_API_KEY` may be read by the local application.
- No production application file (`providers.py`, `server.py`, static assets,
  or app README) may reference `OPENAI_API_KEY`, `api.openai.com`,
  `gpt-5-mini`, OpenAI fallback, or provider selection. Tests may name these
  markers only to enforce their absence from production files.
- Never write the SponsoredTokens key to files, logs, command lines, snapshots,
  browser responses, or Git.
- Bind only to `127.0.0.1`; reject wildcard, LAN, and alternate hosts.
- Add no runtime packages, JavaScript packages, CDNs, telemetry, storage,
  cookies, CORS, agents, MCP, shell execution, or internet deployment.
- All normal tests are offline; the single live smoke test is explicit opt-in.
- Preserve unrelated changes and follow root `AGENTS.md` governance.

## Review Focus

- Reject unexpected `Host`, absolute-form targets, traversal, oversized bodies,
  incomplete bodies, malformed UTF-8, and malformed JSON.
- Never leak the key through success text, errors, headers, logs, repr, or HTML.
- Normalize upstream protocol, timeout, oversized, malformed, and HTTP failures.
- Prevent duplicate browser submissions and use text-only DOM rendering.
- Preserve Unicode and the complete SponsoredTokens sponsor footer exactly.

## File Responsibilities

- `apps/sponsoredtokens-web/providers.py`: SponsoredTokens-only configuration,
  payload, transport, response extraction, redaction, and normalized errors.
- `apps/sponsoredtokens-web/server.py`: input validation, fixed-route HTTP
  boundary, environment loading, CLI, and opt-in live smoke test.
- `apps/sponsoredtokens-web/static/index.html`: accessible semantic structure.
- `apps/sponsoredtokens-web/static/app.js`: in-memory session and API/UI state.
- `apps/sponsoredtokens-web/static/app.css`: local responsive presentation.
- `apps/sponsoredtokens-web/tests/test_server.py`: deterministic provider,
  validation, HTTP, UI-policy, CLI, and security tests.
- `apps/sponsoredtokens-web/README.md`: private operator workflow and limits.
- `README.md`: one discoverability link.

---

### Task 1: Preserve the completed validation contract

**Files:**
- Existing: `apps/sponsoredtokens-web/server.py`
- Existing: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Produces: `RequestValidationError`, `validate_bind_host`, and
  `validate_messages`.

- [x] **Step 1: Validation contract implemented and independently reviewed**

Commit `75f1a3ad` implements strict loopback, role, field, count, content, and
Unicode validation. Fourteen focused tests passed; the task review approved it.

### Task 2: Remove OpenAI fallback and keep one SponsoredTokens adapter

**Files:**
- Modify: `apps/sponsoredtokens-web/providers.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: validated `list[dict[str, str]]` from Task 1.
- Produces: `SponsoredTokensConfig`, `ProviderResult`, `ProviderError`,
  `build_upstream_payload`, `extract_response_text`, and
  `call_sponsoredtokens`.

- [ ] **Step 1: Replace obsolete fallback tests with failing sponsored-only tests**

Specify:

```python
@dataclass(frozen=True)
class SponsoredTokensConfig:
    api_key: str | None

@dataclass(frozen=True)
class ProviderResult:
    text: str
    provider: str
    model: str

class ProviderError(Exception):
    code: str
    http_status: int

def call_sponsoredtokens(
    config: SponsoredTokensConfig,
    messages: list[dict[str, str]],
    *,
    opener: Callable = urllib.request.urlopen,
) -> ProviderResult: ...
```

Tests must assert the fixed endpoint
`https://sponsoredtokens.com/api/v1/responses`, model
`sponsored/openai/gpt-5.1-codex-mini`, 30-second timeout, 1 MiB response bound,
isolated Bearer header, redirect refusal, exact Unicode/footer preservation,
and safe mapping for missing key, 401, 402, 429, 5xx, timeout, network,
protocol, oversized, malformed, and missing-text failures. Reject a success
text containing the configured key.

Add a source-policy assertion that application files contain none of:
`OPENAI_API_KEY`, `api.openai.com`, `gpt-5-mini`, `RuntimeConfig`,
`fallback_used`, or `route_chat`.

- [ ] **Step 2: Run tests and confirm failure against obsolete fallback code**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because fallback contracts and OpenAI constants still exist.

- [ ] **Step 3: Implement the single adapter**

Delete OpenAI constants, `RuntimeConfig`, fallback allowlists, routing, and all
fallback metadata. Keep bounded transport, stable local errors, credential-safe
`repr`, redirect refusal, and credential-echo rejection. Do not append or edit
response text.

- [ ] **Step 4: Re-run focused tests**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: all tests PASS with no network traffic and no forbidden OpenAI marker
in application files.

- [ ] **Step 5: Commit**

```powershell
git add apps/sponsoredtokens-web/providers.py apps/sponsoredtokens-web/tests/test_server.py
git commit -m "refactor: keep local chat sponsoredtokens only"
```

### Task 3: Implement the secure loopback HTTP boundary

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Create: `apps/sponsoredtokens-web/static/index.html`
- Create: `apps/sponsoredtokens-web/static/app.css`
- Create: `apps/sponsoredtokens-web/static/app.js`

**Interfaces:**
- Consumes: Task 1 validation and Task 2 `SponsoredTokensConfig`,
  `ProviderResult`, `ProviderError`, `call_sponsoredtokens`.
- Produces: `make_handler`, `create_server`, `GET /api/health`,
  `POST /api/chat`, and fixed static routes.

- [ ] **Step 1: Write failing HTTP integration tests**

Specify:

```python
def make_handler(config: SponsoredTokensConfig, transport: Callable = call_sponsoredtokens): ...
def create_server(
    config: SponsoredTokensConfig,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    transport: Callable = call_sponsoredtokens,
) -> ThreadingHTTPServer: ...
```

Using an ephemeral loopback server and fake transport, cover health with and
without key; chat success text/provider/model; every stable provider error;
invalid/missing/partial/oversized bodies; unsupported methods; unexpected Host;
absolute targets; encoded traversal; unknown routes; fixed MIME types; no CORS;
and these headers on every response: restrictive CSP,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
`Cache-Control: no-store`. Assert sentinel key absence in body, headers, and
captured logs.

- [ ] **Step 2: Run tests and confirm HTTP interfaces are absent**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL for missing handler/server factories.

- [ ] **Step 3: Implement the HTTP boundary**

Serve only `/`, `/index.html`, `/app.css`, and `/app.js` from an allowlist.
Require loopback Host with active port, reject authority/scheme targets, read
exactly the declared bounded body, parse UTF-8 JSON, validate messages, invoke
the injected transport, and emit `ensure_ascii=False` JSON. Suppress default
request logging or use fixed route/status metadata only.

- [ ] **Step 4: Re-run all app tests**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/static apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: serve secure sponsoredtokens chat api"
```

### Task 4: Build the in-memory browser chat

**Files:**
- Modify: `apps/sponsoredtokens-web/static/index.html`
- Modify: `apps/sponsoredtokens-web/static/app.css`
- Modify: `apps/sponsoredtokens-web/static/app.js`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Task 3 health/chat contracts.
- Produces: send, retry, clear, status, provider, model, and in-memory history UI.

- [ ] **Step 1: Add failing asset-policy tests**

Assert named accessible elements for status/provider/model/messages/composer/
send/retry/clear; local-only assets; labels/live regions; `textContent` or text
nodes; one in-memory messages collection; and absence of `innerHTML`, storage,
cookies, remote URLs, credentials, OpenAI markers, provider selectors, and
fallback controls.

- [ ] **Step 2: Run tests and confirm UI contract failure**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

- [ ] **Step 3: Implement the UI**

Fetch health on load. On submit, append text safely, disable duplicate submit,
post full in-memory history, append the exact assistant response, and show
SponsoredTokens/model. Preserve failed turn for retry; clear empties only array
and DOM; refresh naturally resets. Support keyboard/multiline input, focus, and
screen-reader status.

- [ ] **Step 4: Re-run tests and commit**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
git add apps/sponsoredtokens-web/static apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: add private sponsoredtokens chat ui"
```

### Task 5: Add startup, documentation, and explicit live smoke test

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Create: `apps/sponsoredtokens-web/README.md`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 2 adapter and Task 3 server factory.
- Produces: `load_config_from_environment`, `parse_args`, `run_live_smoke`,
  `main`, and documented PowerShell commands.

- [ ] **Step 1: Write failing CLI/smoke guard tests**

Specify:

```python
def load_config_from_environment(environ: Mapping[str, str]) -> SponsoredTokensConfig: ...
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace: ...
def run_live_smoke(config: SponsoredTokensConfig) -> bool: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

Cover default port, `--port`, `--open`, `--live-smoke`, refusal of alternate
host, no network in normal tests, missing-key smoke refusal, safe output, and
absence of any `OPENAI_API_KEY` read.

- [ ] **Step 2: Run tests and confirm CLI interfaces are absent**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

- [ ] **Step 3: Implement startup and documentation**

Load `SPONSOREDTOKENS_API_KEY` once without logging it. Print only loopback URL,
provider, model, readiness. Support clean `Ctrl+C`; open browser only after bind.
`--live-smoke` sends one minimal prompt, prints only pass/fail/provider/model,
and exits. Document:

```powershell
python apps/sponsoredtokens-web/server.py --open
python apps/sponsoredtokens-web/server.py --live-smoke
```

Explain privacy, session-only history, loopback, stop behavior, safe local error
codes, current provider outage behavior, and separation from ChatGPT web plan.

- [ ] **Step 4: Verify and commit**

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
python apps/sponsoredtokens-web/server.py --help
git add apps/sponsoredtokens-web README.md
git commit -m "docs: add sponsoredtokens local chat workflow"
```

### Task 6: Run live and repository verification

**Files:**
- Modify only for defect fixes: Tasks 2–5 files

**Interfaces:**
- Consumes: complete app/CLI/tests and repository gates.
- Produces: deterministic, governance, live, browser, secret, and scope evidence.

- [ ] **Step 1: Run deterministic and governance checks**

```powershell
git diff --check origin/main...HEAD
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Use the repository's approved pytest runtime; do not install globally.

- [ ] **Step 2: Run explicit live smoke**

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Expected: PASS with nonempty safe metadata. If SponsoredTokens returns 503 or
another safe code, record it exactly and do not claim live completion.

- [ ] **Step 3: Verify browser loop when provider is available**

```powershell
python apps/sponsoredtokens-web/server.py --open
```

Confirm one harmless Portuguese turn, exact footer, status/provider/model,
clear/refresh behavior, and no key, cookies, storage, external assets, OpenAI
request, or cross-origin browser traffic. Stop with `Ctrl+C`.

- [ ] **Step 4: Run final secret/scope audit**

```powershell
rg -n "sk-st-|OPENAI_API_KEY|api\.openai\.com|gpt-5-mini|fallback|innerHTML|localStorage|sessionStorage|0\.0\.0\.0" apps/sponsoredtokens-web README.md
git status --short
git log --oneline origin/main..HEAD
```

Only negative source-policy assertions in `tests/test_server.py` may name the
OpenAI/fallback markers; only intentional rejection-test/docs mentions of
`0.0.0.0` are allowed. Credential values remain forbidden everywhere.

- [ ] **Step 5: Add regression tests for defects, fix, rerun affected checks, commit**

Do not create an empty commit.

### Task 7: Final review and delivery

**Files:**
- Review: all files changed by `origin/main...HEAD`

**Interfaces:**
- Consumes: approved spec, implementation diff, and Task 6 evidence.
- Produces: evidence-backed delivery summary and branch decision.

- [ ] **Step 1: Review full diff against every spec criterion and non-goal**

Apply GitHub Arena Review mode and inspect credential handling, Windows behavior,
HTTP parsing, UI injection, tests, and claims.

- [ ] **Step 2: Run complete final commands once after fixes**

Capture exit codes, test counts, live safe status, and tested SHA.

- [ ] **Step 3: Report accurately**

Report files, tests/gates, live/browser evidence, branch/SHA, and limitations.
Do not say “100%”, `LIVE_VERIFIED`, or complete while SponsoredTokens live smoke
or browser evidence is unavailable.
