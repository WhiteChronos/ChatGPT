# SponsoredTokens Local Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private, loopback-only browser chat that sends session messages to SponsoredTokens without exposing or persisting the API key.

**Architecture:** A Python standard-library `ThreadingHTTPServer` serves fixed local assets and two same-origin JSON routes. The server validates every request, injects the environment-held credential at the outbound boundary, normalizes upstream failures, and returns only safe response data; the browser keeps all conversation state in memory.

**Tech Stack:** Python 3 standard library (`http.server`, `urllib.request`, `unittest`), vanilla HTML/CSS/JavaScript, PowerShell operator workflow.

**Spec:** `docs/superpowers/specs/2026-10-12-sponsoredtokens-local-chat-design.md`

## Global Constraints

- Never write, print, snapshot, commit, or return `SPONSOREDTOKENS_API_KEY`.
- Bind only to `127.0.0.1`; reject wildcard, LAN, and non-loopback hosts.
- Do not add runtime packages, JavaScript packages, CDNs, telemetry, storage, cookies, CORS, agents, MCP, shell execution, or internet deployment.
- Keep paid/live traffic opt-in. All normal tests mock the outbound SponsoredTokens boundary.
- Preserve unrelated user changes and follow root `AGENTS.md` governance.

## Review Focus

- Reject unexpected `Host` values, alternate bind addresses, path traversal, oversized or incomplete bodies.
- Never leak credentials, upstream bodies, headers, account identifiers, or exception details.
- Treat malformed/missing upstream response text as a safe stable error.
- Prevent duplicate browser submissions and render all user/model text with text-only DOM APIs.
- Preserve Unicode and the complete sponsor footer exactly as returned.

## File Responsibilities

- `apps/sponsoredtokens-web/server.py`: configuration, validation, upstream
  transport, fixed-route HTTP handler, CLI, and opt-in smoke test.
- `apps/sponsoredtokens-web/static/index.html`: accessible semantic structure.
- `apps/sponsoredtokens-web/static/app.js`: in-memory session and API/UI state.
- `apps/sponsoredtokens-web/static/app.css`: local responsive presentation.
- `apps/sponsoredtokens-web/tests/test_server.py`: deterministic backend, HTTP,
  asset-policy, CLI, security, and redaction tests.
- `apps/sponsoredtokens-web/README.md`: private operator workflow and limits.
- `README.md`: one discoverability link; no duplicated operating instructions.

---

### Task 1: Establish the backend contract and message validation

**Files:**
- Create: `apps/sponsoredtokens-web/server.py`
- Create: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Python standard-library types only; no earlier task interfaces.
- Produces: `AppConfig`, `RequestValidationError`, `validate_bind_host`,
  `validate_messages`, `build_upstream_payload`, and `extract_response_text`.

- [ ] **Step 1: Write failing contract tests**

Add `unittest` coverage for these public interfaces in `server.py`:

```python
@dataclass(frozen=True)
class AppConfig:
    api_key: str | None
    model: str = DEFAULT_MODEL

def validate_bind_host(host: str) -> str: ...
def validate_messages(value: object) -> list[dict[str, str]]: ...
def build_upstream_payload(messages: list[dict[str, str]], model: str) -> dict: ...
def extract_response_text(payload: object) -> str: ...
```

Cover one valid Unicode conversation and failures for empty/non-list history,
more than 100 entries, unknown roles, unknown per-message fields, blank content,
non-string content, and content above `MAX_CONTENT_CHARS`. Assert only
`127.0.0.1` is accepted as a bind host. Cover `output_text` extraction and the
Responses-style nested `output[].content[].text` fallback, including exact
footer preservation.

- [ ] **Step 2: Run the tests and confirm they fail for missing implementation**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because `server.py` and its interfaces do not exist yet.

- [ ] **Step 3: Implement the smallest backend contract**

In `server.py`, define constants for endpoint, provider, model, body/message/
content limits, and timeout. Implement the interfaces above with a local
`RequestValidationError` whose public code/message contain no submitted text.
Convert validated history to the Responses API `input` shape without modifying
content. Reject rather than truncate over-limit input.

- [ ] **Step 4: Re-run the focused tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS for validation, payload construction, extraction, footer, and
loopback checks.

- [ ] **Step 5: Commit the backend contract**

```powershell
git add apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: define sponsoredtokens chat contract"
```

### Task 2: Add the secure SponsoredTokens transport boundary

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: `AppConfig`, `build_upstream_payload`, and
  `extract_response_text` from Task 1.
- Produces: `SponsoredTokensError` and `call_sponsoredtokens` for the HTTP and
  live-smoke boundaries.

- [ ] **Step 1: Write failing transport tests**

Define the intended interface:

```python
class SponsoredTokensError(Exception):
    code: str
    http_status: int

def call_sponsoredtokens(
    config: AppConfig,
    messages: list[dict[str, str]],
    *,
    opener: Callable = urllib.request.urlopen,
) -> str: ...
```

Use fake openers/responses to assert the exact endpoint, JSON content type,
Bearer authentication, timeout, model, and message payload. Cover missing key,
HTTP 401, 402, 429, 5xx, `URLError`, timeout, invalid JSON, missing output text,
and an upstream error body containing a sentinel secret. Assert returned/local
exception data never contains that body, the API key, headers, or raw exception.

- [ ] **Step 2: Run the focused suite and confirm the new tests fail**

Run:

```powershell
python -m unittest apps/sponsoredtokens-web/tests/test_server.py -v
```

Expected: FAIL because the transport interface is not implemented.

- [ ] **Step 3: Implement the outbound request and stable error mapping**

Read the key only from `AppConfig`; set `Authorization` only on the outbound
request. Parse successful JSON with a bounded response read. Normalize failures
to these local codes: `configuration_required`, `authentication_failed`,
`quota_exhausted`, `rate_limited`, `upstream_timeout`, `upstream_unavailable`,
and `invalid_upstream_response`. Do not chain raw upstream exceptions into
browser-visible text or logs.

- [ ] **Step 4: Re-run transport and contract tests**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: PASS, including exact sponsor-footer preservation and redaction.

- [ ] **Step 5: Commit the transport boundary**

```powershell
git add apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: add sponsoredtokens responses transport"
```

### Task 3: Implement the loopback HTTP API and static-file boundary

**Files:**
- Modify: `apps/sponsoredtokens-web/server.py`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Create: `apps/sponsoredtokens-web/static/index.html`
- Create: `apps/sponsoredtokens-web/static/app.css`
- Create: `apps/sponsoredtokens-web/static/app.js`

**Interfaces:**
- Consumes: Task 1 validation/configuration and Task 2
  `call_sponsoredtokens(config, messages, *, opener=...) -> str`.
- Produces: `make_handler`, `create_server`, `GET /api/health`,
  `POST /api/chat`, and the fixed static routes used by the browser.

- [ ] **Step 1: Write failing HTTP integration tests**

Specify these factory interfaces:

```python
def make_handler(config: AppConfig, transport: Callable = call_sponsoredtokens): ...
def create_server(
    config: AppConfig,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    transport: Callable = call_sponsoredtokens,
) -> ThreadingHTTPServer: ...
```

Start an ephemeral loopback server in test setup and shut it down in cleanup.
Assert:

- `GET /api/health` reports ready/configuration-required without key material;
- `POST /api/chat` returns text/provider/model through an injected fake transport;
- invalid JSON, missing/invalid `Content-Length`, partial body, body over 1 MiB,
  invalid messages, and unsupported methods receive stable JSON errors;
- 401/402/429/timeout/generic local transport errors map to safe HTTP statuses;
- unexpected `Host`, absolute-form targets, encoded traversal, and unknown paths
  are rejected;
- static responses have the expected MIME type and all responses include CSP,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`,
  `Cache-Control: no-store`, and no CORS header;
- a sentinel key passed to `AppConfig` never appears in body, headers, or captured
  logs.

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
  provider, and model UI behavior.

- [ ] **Step 1: Add failing asset-policy tests**

Read the three assets from disk and assert that they provide named elements for
status, provider, model, messages, composer, send, retry, and clear. Assert the
JavaScript uses `textContent`/text nodes, contains no `innerHTML`, `localStorage`,
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
connection/provider/model. On submit, append the user message with text-only DOM
operations, disable duplicate submission, post the full in-memory history,
append the assistant response verbatim, and keep it in history. On failure,
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
- Create: `apps/sponsoredtokens-web/README.md`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 2 `call_sponsoredtokens` and Task 3 `create_server`.
- Produces: `load_config_from_environment`, `parse_args`, `run_live_smoke`,
  `main`, and the documented PowerShell operator commands.

- [ ] **Step 1: Write failing CLI and live-smoke guard tests**

Specify:

```python
def load_config_from_environment(environ: Mapping[str, str]) -> AppConfig: ...
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace: ...
def run_live_smoke(config: AppConfig) -> bool: ...
def main(argv: Sequence[str] | None = None) -> int: ...
```

Assert default host/port, `--port`, `--open`, and explicit `--live-smoke` parsing;
reject attempts to select another host. Assert ordinary startup never calls the
live endpoint, and `--live-smoke` refuses to run without a configured key. Mock
server creation/browser opening/transport so no test performs network access.

- [ ] **Step 2: Run the tests and confirm CLI cases fail**

Run:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Expected: FAIL because the operator entry points are incomplete.

- [ ] **Step 3: Implement startup and documentation**

Load `SPONSOREDTOKENS_API_KEY` once at process start without logging it. Print
only loopback URL, provider, model, and readiness. Support `Ctrl+C` clean
shutdown and open the URL only after successful bind when `--open` is present.
Make `--live-smoke` send one minimal prompt, print only pass/fail/provider/model,
and exit without starting the server.

Document in the app README:

```powershell
python apps/sponsoredtokens-web/server.py --open
python apps/sponsoredtokens-web/server.py --live-smoke
```

Explain privacy, session-only history, loopback scope, environment-variable
requirement, stop behavior, safe troubleshooting by local error code, and the
fact that this does not combine or extend ChatGPT plan limits. Add one short
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

- [ ] **Step 3: Run the explicit live SponsoredTokens smoke test**

From a fresh PowerShell process that can read the existing user environment:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Expected: PASS with nonempty response metadata; no prompt, response body, sponsor
account data, or credential is printed. If SponsoredTokens is unavailable,
record the exact safe local error code and do not misreport completion.

- [ ] **Step 4: Manually verify the browser loop**

```powershell
python apps/sponsoredtokens-web/server.py --open
```

Send one harmless Portuguese prompt. Confirm provider/model/status are visible,
the complete sponsor footer appears in the answer, clear removes the session,
refresh resets it, and DevTools shows no key, cookies, storage entries, external
assets, or cross-origin requests. Stop with `Ctrl+C`.

- [ ] **Step 5: Apply defect-only fixes with regression tests**

For every defect found, first add a failing regression test, then make the
smallest fix, rerun the focused test, and repeat Steps 1–4 as affected.

- [ ] **Step 6: Run final secret and scope audit**

```powershell
rg -n "sk-st-|SPONSOREDTOKENS_API_KEY\s*=|innerHTML|localStorage|sessionStorage|0\.0\.0\.0" apps/sponsoredtokens-web README.md
git status --short
git log --oneline origin/main..HEAD
```

Expected: no credential value or forbidden runtime behavior. The environment
variable name may appear only in server-side loading/tests/docs; `0.0.0.0` may
appear only in rejection tests/docs. Worktree contains only intended changes.

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
