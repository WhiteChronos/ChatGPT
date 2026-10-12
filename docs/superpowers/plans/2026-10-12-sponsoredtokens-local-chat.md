# SponsoredTokens Local Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private, loopback-only browser chat that uses SponsoredTokens first and safely falls back to a separately billed OpenAI API credential without exposing or persisting either key.

**Architecture:** A Python standard-library `ThreadingHTTPServer` serves fixed local assets and two same-origin JSON routes. Isolated Responses-compatible provider adapters feed a router that tries SponsoredTokens first and makes at most one OpenAI request only for approved availability failures; the browser keeps all conversation state in memory and displays the provider that actually answered.

**Tech Stack:** Python 3 standard library (`http.server`, `urllib.request`, `unittest`), vanilla HTML/CSS/JavaScript, PowerShell operator workflow.

**Spec:** `docs/superpowers/specs/2026-10-12-sponsoredtokens-local-chat-design.md`

## Global Constraints

- Never write, print, snapshot, commit, or return either API key.
- Bind only to `127.0.0.1`; reject wildcard, LAN, and non-loopback hosts.
- Do not add runtime packages, JavaScript packages, CDNs, telemetry, storage, cookies, CORS, agents, MCP, shell execution, or internet deployment.
- Keep paid/live traffic opt-in. All normal tests mock both outbound boundaries.
- Never use ChatGPT/Codex subscription credits as API credit, combine balances,
  or hide which provider answered.
- Preserve unrelated user changes and follow root `AGENTS.md` governance.

## Review Focus

- Reject unexpected `Host` values, alternate bind addresses, path traversal, oversized or incomplete bodies.
- Never leak either credential, upstream bodies, headers, account identifiers,
  or exception details.
- Fall back exactly once for the four approved primary failure codes and never
  for authentication, configuration, validation, or malformed responses.
- Treat malformed/missing upstream response text as a safe stable error.
- Prevent duplicate browser submissions and render all user/model text with text-only DOM APIs.
- Preserve Unicode and the complete sponsor footer exactly as returned.

## File Responsibilities

- `apps/sponsoredtokens-web/providers.py`: provider configuration, Responses
  transports, normalized failures, result metadata, and failover router.
- `apps/sponsoredtokens-web/server.py`: validation, fixed-route HTTP handler,
  CLI, environment loading, and opt-in smoke tests.
- `apps/sponsoredtokens-web/configure-openai-key.ps1`: secure interactive
  Windows user-environment setup with redacted verification.
- `apps/sponsoredtokens-web/static/index.html`: accessible semantic structure.
- `apps/sponsoredtokens-web/static/app.js`: in-memory session and API/UI state.
- `apps/sponsoredtokens-web/static/app.css`: local responsive presentation.
- `apps/sponsoredtokens-web/tests/test_server.py`: deterministic validation,
  provider, failover, HTTP, asset-policy, CLI, security, and redaction tests.
- `apps/sponsoredtokens-web/README.md`: private operator workflow and limits.
- `README.md`: one discoverability link; no duplicated operating instructions.

---

### Task 1: Establish the backend contract and message validation

**Files:**
- Create: `apps/sponsoredtokens-web/server.py`
- Create: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Python standard-library types only; no earlier task interfaces.
- Produces: `RequestValidationError`, `validate_bind_host`, and
  `validate_messages` for the HTTP boundary.

- [ ] **Step 1: Write failing contract tests**

Add `unittest` coverage for these public interfaces in `server.py`:

```python
def validate_bind_host(host: str) -> str: ...
def validate_messages(value: object) -> list[dict[str, str]]: ...
```

Cover one valid Unicode conversation and failures for empty/non-list history,
more than 100 entries, unknown roles, unknown per-message fields, blank content,
non-string content, and content above `MAX_CONTENT_CHARS`. Assert only
`127.0.0.1` is accepted as a bind host.

- [ ] **Step 2: Run the tests and confirm they fail for missing implementation**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because `server.py` and its interfaces do not exist yet.

- [ ] **Step 3: Implement the smallest backend contract**

In `server.py`, define constants for body/message/content limits. Implement the
interfaces above with a local
`RequestValidationError` whose public code/message contain no submitted text.
Reject rather than truncate over-limit input.

- [ ] **Step 4: Re-run the focused tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS for validation and loopback checks.

- [ ] **Step 5: Commit the backend contract**

```powershell
git add apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: define local chat validation contract"
```

### Task 2: Add provider adapters and the controlled failover router

**Files:**
- Create: `apps/sponsoredtokens-web/providers.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: validated `list[dict[str, str]]` messages from Task 1.
- Produces: `ProviderConfig`, `RuntimeConfig`, `ProviderResult`, `ProviderError`,
  `build_upstream_payload`, `extract_response_text`, `call_provider`, and
  `route_chat` for the HTTP and live-smoke boundaries.

- [ ] **Step 1: Write failing adapter and router tests**

Define the intended interface:

```python
@dataclass(frozen=True)
class ProviderConfig:
    name: str
    endpoint: str
    model: str
    api_key: str | None

@dataclass(frozen=True)
class RuntimeConfig:
    primary: ProviderConfig
    fallback: ProviderConfig

@dataclass(frozen=True)
class ProviderResult:
    text: str
    provider: str
    model: str
    fallback_used: bool

class ProviderError(Exception):
    code: str
    http_status: int

def build_upstream_payload(messages: list[dict[str, str]], model: str) -> dict: ...
def extract_response_text(payload: object) -> str: ...
def call_provider(
    config: ProviderConfig,
    messages: list[dict[str, str]],
    *,
    opener: Callable = urllib.request.urlopen,
) -> str: ...
def route_chat(
    config: RuntimeConfig,
    messages: list[dict[str, str]],
    *,
    caller: Callable = call_provider,
) -> ProviderResult: ...
```

Use fake openers/responses to assert the exact endpoint, JSON content type,
provider-specific Bearer credential, timeout, model, and message payload. Cover
both adapters for missing key, HTTP 401, 402, 429, 5xx, `URLError`, timeout,
invalid JSON, missing output text, and an upstream error body containing two
sentinel secrets. Assert local exceptions never contain bodies, keys, headers,
or raw exceptions. Cover `output_text` and nested Responses output extraction,
Unicode, and exact sponsor-footer preservation.

Use a fake caller to prove that `route_chat`:

- returns primary metadata without calling fallback after success;
- calls fallback exactly once after each of `quota_exhausted`, `rate_limited`,
  `upstream_timeout`, and `upstream_unavailable`;
- does not call fallback for `configuration_required`, `authentication_failed`,
  `invalid_request`, or `invalid_upstream_response`;
- returns `fallback_used=True` only when OpenAI actually answers;
- returns a safe error if fallback also fails, without retry loops.

- [ ] **Step 2: Run the focused suite and confirm the new tests fail**

Run:

```powershell
python -m unittest apps/sponsoredtokens-web/tests/test_server.py -v
```

Expected: FAIL because provider adapters and routing are not implemented.

- [ ] **Step 3: Implement the adapters and stable error mapping**

Define the fixed SponsoredTokens endpoint/model and the fixed OpenAI Responses
endpoint with model `gpt-5-mini`. Read keys only from `ProviderConfig`; set
`Authorization` only on the matching outbound request. Parse successful JSON
with a bounded response read. Normalize failures to `configuration_required`,
`authentication_failed`, `quota_exhausted`, `rate_limited`,
`upstream_timeout`, `upstream_unavailable`, and
`invalid_upstream_response`. Do not chain raw upstream exceptions into visible
text or logs.

Implement `route_chat` as a two-attempt maximum: primary first, then fallback
only for the four approved codes. Never mutate the messages or append a sponsor
footer.

- [ ] **Step 4: Re-run transport and contract tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS, including exact footer preservation, dual-secret redaction, and
the failover allowlist/denylist.

- [ ] **Step 5: Commit the transport boundary**

```powershell
git add apps/sponsoredtokens-web/providers.py apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: add controlled provider failover"
```

### Task 3: Implement the loopback HTTP API and static-file boundary

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Create: `apps/sponsoredtokens-web/static/index.html`
- Create: `apps/sponsoredtokens-web/static/app.css`
- Create: `apps/sponsoredtokens-web/static/app.js`

**Interfaces:**
- Consumes: Task 1 validation and Task 2
  `route_chat(config, messages, *, caller=...) -> ProviderResult`.
- Produces: `make_handler`, `create_server`, `GET /api/health`,
  `POST /api/chat`, and the fixed static routes used by the browser.

- [ ] **Step 1: Write failing HTTP integration tests**

Specify these factory interfaces:

```python
def make_handler(config: RuntimeConfig, router: Callable = route_chat): ...
def create_server(
    config: RuntimeConfig,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    router: Callable = route_chat,
) -> ThreadingHTTPServer: ...
```

Start an ephemeral loopback server in test setup and shut it down in cleanup.
Assert:

- `GET /api/health` reports `ready`, `primary_configuration_required`, or
  `configuration_required` for zero/one/two configured keys without key material;
- `POST /api/chat` returns text/provider/model/fallback metadata through an
  injected fake router;
- invalid JSON, missing/invalid `Content-Length`, partial body, body over 1 MiB,
  invalid messages, and unsupported methods receive stable JSON errors;
- provider authentication/quota/rate/timeout/generic errors map to safe HTTP
  statuses without revealing which key failed;
- unexpected `Host`, absolute-form targets, encoded traversal, and unknown paths
  are rejected;
- static responses have the expected MIME type and all responses include CSP,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `Cache-Control: no-store`, and no CORS header;
- sentinel keys passed to `RuntimeConfig` never appear in body, headers, or
  captured logs.

- [ ] **Step 2: Run the HTTP tests and confirm failure**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because the handler/server factories are absent.

- [ ] **Step 3: Implement the HTTP boundary**

Serve only `/`, `/index.html`, `/app.css`, and `/app.js` from the fixed static
directory; do not concatenate request paths to filesystem paths. Require a
loopback `Host` with the active port, reject request targets containing a scheme
or authority, and omit CORS entirely. Read exactly the declared bounded body,
parse UTF-8 JSON, validate it, call the injected transport, and return JSON with
`ensure_ascii=False`. Suppress default request logging or replace it with fixed,
non-sensitive route/status metadata.

- [ ] **Step 4: Re-run the HTTP and backend tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS for both API and security boundary cases.

- [ ] **Step 5: Commit the HTTP boundary and placeholder assets**

```powershell
git add apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/tests/test_server.py apps/sponsoredtokens-web/static
git commit -m "feat: serve secure loopback chat api"
```

### Task 4: Build the private browser chat experience

**Files:**
- Modify: `apps/sponsoredtokens-web/static/index.html`
- Modify: `apps/sponsoredtokens-web/static/app.css`
- Modify: `apps/sponsoredtokens-web/static/app.js`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Task 3 static routes and JSON contracts for `/api/health` and
  `/api/chat`.
- Produces: an in-memory browser session with send, retry, clear, status,
  provider, model, and visible fallback-state UI behavior.

- [ ] **Step 1: Add failing asset-policy tests**

Read the three assets from disk and assert that they provide named elements for
status, primary, fallback, active provider, model, fallback notice, messages,
composer, send, retry, and clear. Assert the JavaScript uses
`textContent`/text nodes, contains no `innerHTML`, `localStorage`,
`sessionStorage`, cookies, remote URL, or credential name, and has a single
in-memory `messages` collection. Assert HTML has no external scripts/styles and
includes accessible labels/live regions.

- [ ] **Step 2: Run the suite and confirm the UI contract fails**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL until the complete UI contract is present.

- [ ] **Step 3: Implement the UI**

Build a responsive, dependency-free chat. On load, fetch `/api/health` and show
both configured routes without exposing a provider selector. On submit, append
the user message with text-only DOM
operations, disable duplicate submission, post the full in-memory history,
append the assistant response verbatim, show the provider/model that answered,
and display a persistent per-response fallback badge when `fallback_used` is
true. Keep the answer in history. On failure,
retain the unsent turn and expose retry; clear empties only the in-memory array
and DOM. Refresh naturally resets history. Preserve keyboard submission while
allowing multiline input, visible focus, and screen-reader status updates.

- [ ] **Step 4: Re-run all app tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS, including injection-prevention and no-persistence assertions.

- [ ] **Step 5: Commit the browser experience**

```powershell
git add apps/sponsoredtokens-web/static apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: add private sponsoredtokens chat ui"
```

### Task 5: Add the operator entry point, documentation, and opt-in live smoke test

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Create: `apps/sponsoredtokens-web/configure-openai-key.ps1`
- Create: `apps/sponsoredtokens-web/README.md`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 2 provider configurations/router and Task 3 `create_server`.
- Produces: `load_config_from_environment`, `parse_args`, `run_live_smoke`,
  `main`, the secure PowerShell key setup, and documented operator commands.

- [ ] **Step 1: Write failing CLI and live-smoke guard tests**

Specify:

```python
def load_config_from_environment(environ: Mapping[str, str]) -> RuntimeConfig: ...
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace: ...
def run_live_smoke(config: RuntimeConfig, provider: str) -> bool: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

Assert exact environment mapping for both keys, default host/port, `--port`,
`--open`, and `--live-smoke {sponsoredtokens,openai,all}` parsing; reject attempts
to select another bind host. Assert ordinary startup never calls a live endpoint
and each smoke mode refuses to run without its matching key. Mock server
creation, browser opening, and provider calls so no test performs network access.

Add static PowerShell policy tests asserting the helper uses `Read-Host
-AsSecureString`, writes only the user-scoped `OPENAI_API_KEY`, does not accept a
key argument, never echoes or interpolates the plaintext value, verifies only
redacted presence/length, and clears temporary references in `finally`.

- [ ] **Step 2: Run the tests and confirm CLI cases fail**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because the operator entry points are incomplete.

- [ ] **Step 3: Implement startup and documentation**

Load `SPONSOREDTOKENS_API_KEY` and `OPENAI_API_KEY` once at process start without
logging them. Print only loopback URL, provider names/models, and readiness.
Support `Ctrl+C` clean shutdown and open the URL only after successful bind when
`--open` is present. Make each `--live-smoke` mode send one minimal direct prompt
per selected provider, print only pass/fail/provider/model, and exit without
starting the server. Do not deliberately exhaust SponsoredTokens to test live
failover; the router tests own that proof.

Implement `configure-openai-key.ps1` as an interactive secure-input helper. It
must not create an OpenAI key; the operator creates a project key in the OpenAI
Platform, pastes it only into the secure PowerShell prompt, and then opens a new
process so the saved user variable becomes visible.

Document in the app README:

```powershell
pwsh -File apps/sponsoredtokens-web/configure-openai-key.ps1
python apps/sponsoredtokens-web/server.py --open
python apps/sponsoredtokens-web/server.py --live-smoke sponsoredtokens
python apps/sponsoredtokens-web/server.py --live-smoke openai
python apps/sponsoredtokens-web/server.py --live-smoke all
```

Explain privacy, session-only history, loopback scope, environment-variable
requirements for both keys, approved fallback codes, stop behavior, safe
troubleshooting by local error code, and the fact that OpenAI Platform billing
does not combine with or extend ChatGPT plan limits. Add one short
discoverability link to the root README.

- [ ] **Step 4: Run app tests and CLI help**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
python apps/sponsoredtokens-web/server.py --help
```

Expected: tests PASS; help lists only safe local options and reveals no key.

- [ ] **Step 5: Commit operator workflow**

```powershell
git add apps/sponsoredtokens-web README.md
git commit -m "docs: add sponsoredtokens local chat workflow"
```

### Task 6: Perform live and repository-level verification

**Files:**
- Modify only if verification exposes a defect: files from Tasks 1–5

**Interfaces:**
- Consumes: the complete app, CLI, tests, and repository gates from Tasks 1–5.
- Produces: reproducible unit, governance, live-smoke, browser, secret-audit,
  and scope-audit evidence for final review.

- [ ] **Step 1: Run static repository checks**

```powershell
git diff --check origin/main...HEAD
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: no whitespace errors; all app tests PASS with no network traffic.

- [ ] **Step 2: Run the repository governance gates**

```powershell
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Expected: all commands exit 0. If the bundled runtime lacks `pytest`, use the
repository's documented test environment rather than installing globally.

- [ ] **Step 3: Run both explicit live provider smoke tests**

From a fresh PowerShell process that can read the existing user environment:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke sponsoredtokens
python apps/sponsoredtokens-web/server.py --live-smoke openai
```

Expected: each configured provider reports PASS with nonempty response metadata;
no prompt, response body, account data, or credential is printed. If either is
unavailable, record its exact safe local error code and do not misreport
completion.

- [ ] **Step 4: Manually verify the browser loop**

```powershell
python apps/sponsoredtokens-web/server.py --open
```

Send one harmless Portuguese prompt. Confirm provider/model/status are visible,
the complete sponsor footer appears when SponsoredTokens answers, clear removes
the session, refresh resets it, and DevTools shows no key, cookies, storage
entries, external assets, provider selector, or cross-origin browser requests.
Confirm the deterministic router test (not intentional balance exhaustion)
proves the fallback badge/metadata path. Stop with `Ctrl+C`.

- [ ] **Step 5: Apply defect-only fixes with regression tests**

For every defect found, first add a failing regression test, then make the
smallest fix, rerun the focused test, and repeat Steps 1–4 as affected.

- [ ] **Step 6: Run final secret and scope audit**

```powershell
rg -n "sk-st-|sk-proj-|SPONSOREDTOKENS_API_KEY\s*=|OPENAI_API_KEY\s*=|innerHTML|localStorage|sessionStorage|0\.0\.0\.0" apps/sponsoredtokens-web README.md
git status --short
git log --oneline origin/main..HEAD
```

Expected: no credential value or forbidden runtime behavior. Environment
variable names may appear only in server-side loading, the secure helper,
tests, and docs; `0.0.0.0` may appear only in rejection tests/docs. Worktree
contains only intended changes.

- [ ] **Step 7: Commit any verification fixes**

If Step 5 changed files:

```powershell
git add apps/sponsoredtokens-web README.md
git commit -m "fix: harden sponsoredtokens local chat"
```

If no files changed, do not create an empty commit.

### Task 7: Final review and handoff

**Files:**
- Review: all files changed by `origin/main...HEAD`

**Interfaces:**
- Consumes: Task 6 verification evidence and the approved design spec.
- Produces: an evidence-backed delivery summary with branch and commit identity.

- [ ] **Step 1: Review the final diff against the approved spec**

Verify every success criterion and non-goal. Pay particular attention to the
five items in **Review Focus**, test determinism, Windows compatibility, and
whether documentation claims only what was actually verified.

- [ ] **Step 2: Run the complete final command set once more**

Repeat Task 6 Steps 1–3 after the final review. Capture only exit codes, test
counts, safe local status codes, and the tested commit SHA.

- [ ] **Step 3: Prepare the delivery summary**

Report implemented files, test/gate results, live-smoke result, browser result,
current branch/SHA, and any remaining limitation. Do not say “100%”,
`LIVE_VERIFIED`, or complete unless the corresponding live evidence exists.
