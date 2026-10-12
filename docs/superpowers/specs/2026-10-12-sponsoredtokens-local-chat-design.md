# SponsoredTokens Local Chat — Design

## Context and intent

WhiteChronos needs a private local web chat that uses the already validated
SponsoredTokens account without exposing credentials to browser code or Git.
When SponsoredTokens has no balance, is rate-limited, times out, or is
temporarily unavailable, a separately billed OpenAI Platform API credential can
answer as an explicit fallback. The first version remains intentionally small:
prove a secure browser-to-local-server chat loop and provider failover before
integrating WhiteChronos agents, MCP servers, deployment, or persistent storage.

The application lives at `apps/sponsoredtokens-web` in this repository. It is
for one user on one Windows computer and binds only to the loopback interface.

## Goals

- Serve a usable chat interface at a local `http://127.0.0.1:<port>` address.
- Send prompts through the SponsoredTokens Responses-compatible endpoint first.
- Fall back to the OpenAI Responses API only for approved availability errors.
- Read `SPONSOREDTOKENS_API_KEY` and `OPENAI_API_KEY` only from the server
  process environment.
- Keep conversation history only in browser memory for the current tab.
- Display connection state and the provider/model that actually answered.
- Preserve the complete sponsor footer whenever SponsoredTokens answers.
- Provide deterministic unit tests without making paid or sponsored network calls.
- Provide an explicit, opt-in live smoke test for operators who have a valid key.

## Non-goals

- Publishing the application to the internet.
- Replacing `chatgpt.com`, Codex Cloud, or ChatGPT account limits.
- Using ChatGPT-plan credits as an API fallback.
- Combining balances, splitting one request across providers, or hiding which
  provider incurred API usage.
- Running WhiteChronos agents, MCP servers, shell commands, or repository tools.
- Persisting conversations, credentials, telemetry, analytics, or user accounts.
- Streaming responses in the first version.

## Architecture

The first version uses Python's standard library and static browser assets. It
adds no Node.js toolchain and no production web framework to this Python-first
repository.

```text
Browser tab on 127.0.0.1
        |
        | same-origin JSON
        v
Python ThreadingHTTPServer on 127.0.0.1
        |
        v
Provider router
   | primary                                      | fallback
   | Authorization: Bearer <sponsored env key>   | Authorization: Bearer <openai env key>
   v                                              v
SponsoredTokens Responses API                    OpenAI Responses API
```

### Components

1. `providers.py`
   - Defines isolated SponsoredTokens and OpenAI Responses-compatible adapters.
   - Applies one shared bounded request/response parser and secret-redaction rule.
   - Routes every request to SponsoredTokens first.
   - Retries once with OpenAI only for `quota_exhausted`, `rate_limited`,
     `upstream_timeout`, or `upstream_unavailable`.
   - Does not fall back for missing credentials, authentication failures,
     malformed input, or malformed upstream responses.

2. `server.py`
   - Parses command-line options for port and optional browser opening.
   - Refuses non-loopback bind addresses.
   - Serves static files from a fixed directory without arbitrary path access.
   - Implements health and chat API routes.
   - Calls the provider router with `urllib.request` and bounded timeouts.
   - Redacts upstream error details before returning them to the browser.

3. `static/index.html`
   - Defines the accessible chat layout and status panel.
   - Loads only repository-owned local assets.

4. `static/app.js`
   - Holds message history in an in-memory JavaScript array.
   - Sends the full current history to the local API for each turn.
   - Renders text with DOM text nodes, never `innerHTML`.
   - Preserves the sponsor footer exactly as returned in the model text.
   - Supports send, retry after error, and clear-session actions.

5. `static/app.css`
   - Provides a responsive, keyboard-usable interface without external fonts,
     scripts, images, or CDNs.

## Local API

### `GET /api/health`

Returns non-secret configuration state:

```json
{
  "status": "ready",
  "primary": {
    "provider": "SponsoredTokens",
    "model": "sponsored/openai/gpt-5.1-codex-mini",
    "key_configured": true
  },
  "fallback": {
    "provider": "OpenAI",
    "model": "gpt-5-mini",
    "key_configured": true
  }
}
```

This endpoint never validates or returns either key. The status is `ready` when
the primary key exists, `primary_configuration_required` when only the fallback
key exists, and `configuration_required` when neither exists. The static
interface remains usable in every configuration state, but it never silently
promotes OpenAI when the SponsoredTokens key is missing or invalid.

### `POST /api/chat`

Request:

```json
{
  "messages": [
    {"role": "user", "content": "Ola"}
  ]
}
```

Rules:

- The request body is limited to 1 MiB.
- `messages` must contain between 1 and 100 entries.
- Roles are restricted to `user` and `assistant`.
- Every content value must be nonblank text with a bounded length.
- Unknown fields are ignored only at the top level; malformed messages fail.
- The server converts messages into Responses API input and routes the request
  according to the approved failover policy.

Success response:

```json
{
  "text": "Resposta completa, incluindo o rodape do patrocinador.",
  "provider": "SponsoredTokens",
  "model": "sponsored/openai/gpt-5.1-codex-mini",
  "fallback_used": false
}
```

When OpenAI answers, the response sets `provider` to `OpenAI`, `model` to
`gpt-5-mini`, and `fallback_used` to `true`. The UI displays a visible fallback
notice. It does not fabricate or append a sponsor footer to OpenAI responses.

The server returns stable local error codes for invalid input, missing
configuration, upstream authentication, quota/rate limits, timeouts, and other
upstream failures. It does not relay headers, response bodies, account IDs, or
credentials from upstream errors.

### Failover policy

Each chat request starts with SponsoredTokens; there is no sticky circuit
breaker in the first version. At most one OpenAI fallback request is made.
Failover is allowed only after the primary returns a normalized
`quota_exhausted`, `rate_limited`, `upstream_timeout`, or
`upstream_unavailable` error. Authentication, configuration, validation, and
response-format failures stop immediately with a safe local error. This keeps
fallback usage visible and prevents an invalid primary configuration from
creating unexpected OpenAI charges.

## Security and privacy

- Bind to `127.0.0.1`, never `0.0.0.0`.
- Require same-origin requests and reject unexpected `Host` headers.
- Send restrictive security headers, including Content Security Policy,
  `X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`.
- Do not enable CORS.
- Never place either API key in HTML, JavaScript, logs, URLs, exceptions,
  fixtures, screenshots, or repository files.
- Never expose a browser control that can select a paid provider or override the
  server-side routing policy.
- Do not persist messages in local storage, cookies, files, or databases.
- Escape all rendered model and user content by using text-only DOM operations.
- Use explicit request-size, message-count, content-length, and timeout limits.

## Operator workflow

The operator stores a separately created OpenAI Platform project key through a
PowerShell secure-input helper. The helper writes `OPENAI_API_KEY` to the Windows
user environment, validates only redacted presence, and clears its temporary
references. The key is never pasted into chat or passed on a command line.

The operator then starts the service from a fresh PowerShell window that can
read both user-level variables:

```powershell
python apps/sponsoredtokens-web/server.py --open
```

The server prints only the loopback URL, providers, models, and readiness state.
It never prints a key. `Ctrl+C` stops the service, and closing or refreshing the
browser tab clears the in-memory conversation. OpenAI Platform usage and billing
remain separate from ChatGPT/Codex subscription limits.

## Testing strategy

Unit and integration-style tests use the standard library and mock the outbound
HTTP boundary. Required coverage includes:

- health response with zero, one, and both configured keys;
- valid chat request and model text extraction;
- complete sponsor footer preservation;
- invalid JSON, oversized bodies, invalid roles, empty content, and too many
  messages;
- provider-specific 401, 402, 429, timeout, and generic failure mapping;
- fallback on exactly the four approved primary failure codes;
- no fallback for authentication, configuration, validation, or malformed
  upstream responses;
- a maximum of one fallback call and accurate `fallback_used` metadata;
- absence of either key's material in browser responses and logs;
- path traversal rejection and expected security headers;
- loopback-only bind validation.

Optional live smoke tests run only when explicitly requested. They can validate
SponsoredTokens and OpenAI independently when the corresponding key is
available. They send a minimal prompt, assert a nonempty response, and report
only pass/fail/provider/model metadata. Deterministic unit tests simulate
primary exhaustion to verify the failover path without intentionally consuming
or exhausting account balances.

## Files to add

```text
apps/sponsoredtokens-web/
  README.md
  configure-openai-key.ps1
  providers.py
  server.py
  static/
    index.html
    app.css
    app.js
  tests/
    test_server.py
```

The root documentation will receive only a short discoverability link if the
implementation is accepted. No generated assets, `.env` files, credentials, or
runtime history will be committed.

## Success criteria

The first version is complete when:

1. The server starts on loopback without external dependencies.
2. The browser can send a message and receive a real SponsoredTokens response.
3. A separate live probe can receive a real OpenAI API response.
4. Deterministic tests prove automatic OpenAI failover for all and only the
   approved SponsoredTokens failure classes.
5. Provider, model, connection state, fallback state, and any sponsor footer
   remain visible and accurate.
6. Refreshing the page clears history and no conversation is written to disk.
7. Tests cover validation, security boundaries, upstream failures, and secret
   redaction.
8. Live smoke tests pass with both saved keys without printing response bodies.
9. Repository governance gates and relevant test suites pass.

## Deferred follow-up

After this version is validated, a separate design can add selected
WhiteChronos agent capabilities behind explicit server-side allowlists. That
follow-up must not expose arbitrary shell or MCP access to browser input and
must retain the repository's Runtime Doctor and provenance requirements.
