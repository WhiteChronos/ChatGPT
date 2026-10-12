# SponsoredTokens Local Chat — Design

## Context and intent

WhiteChronos needs a private local web chat that uses the already validated
SponsoredTokens account without exposing its API key to browser code or Git.
The local Codex and this local chat use SponsoredTokens only. No OpenAI Platform
API credential participates in either local flow.

ChatGPT on the web remains a separate product authenticated by the user's
OpenAI account and governed by the ChatGPT/Codex plan. It does not consume a
local `OPENAI_API_KEY`. Any future hosted application using the OpenAI Platform
would require a separate design and billing arrangement.

The application lives at `apps/sponsoredtokens-web` in this repository. It is
for one user on one Windows computer and binds only to the loopback interface.

## Goals

- Serve a usable chat interface at a local `http://127.0.0.1:<port>` address.
- Send prompts only through the SponsoredTokens Responses-compatible endpoint.
- Read `SPONSOREDTOKENS_API_KEY` only from the server process environment.
- Keep conversation history only in browser memory for the current tab.
- Display connection state, provider, model, and the complete sponsor footer.
- Provide deterministic unit tests without making sponsored network calls.
- Provide an explicit, opt-in live smoke test for operators who have a valid key.

## Non-goals

- Publishing the application to the internet.
- Calling the OpenAI Platform API from local Codex or this application.
- Reading, creating, storing, validating, or using `OPENAI_API_KEY` locally.
- Replacing `chatgpt.com`, Codex Cloud, or ChatGPT account limits.
- Combining balances or treating ChatGPT-plan credits as API credits.
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
        | Authorization: Bearer <SponsoredTokens environment key>
        v
https://sponsoredtokens.com/api/v1/responses
```

### Components

1. `providers.py`
   - Defines the isolated SponsoredTokens Responses-compatible adapter.
   - Applies bounded request/response parsing and secret-redaction rules.
   - Uses the fixed SponsoredTokens endpoint and model.
   - Has no OpenAI endpoint, model, credential, fallback, or provider router.

2. `server.py`
   - Parses command-line options for port and optional browser opening.
   - Refuses non-loopback bind addresses.
   - Serves static files from a fixed directory without arbitrary path access.
   - Implements health and chat API routes.
   - Calls SponsoredTokens with `urllib.request` and bounded timeouts.
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
  "provider": "SponsoredTokens",
  "model": "sponsored/openai/gpt-5.1-codex-mini",
  "key_configured": true
}
```

This endpoint never validates or returns the key. A missing key produces
`status: "configuration_required"` while the static interface remains usable.

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
- The server converts messages into Responses API input and uses the fixed
  SponsoredTokens model.

Success response:

```json
{
  "text": "Resposta completa, incluindo o rodape do patrocinador.",
  "provider": "SponsoredTokens",
  "model": "sponsored/openai/gpt-5.1-codex-mini"
}
```

The server returns stable local error codes for invalid input, missing
configuration, upstream authentication, quota/rate limits, timeouts, and other
upstream failures. It does not relay headers, response bodies, account IDs,
credentials, or response text containing the configured key.

## Security and privacy

- Bind to `127.0.0.1`, never `0.0.0.0`.
- Require same-origin requests and reject unexpected `Host` headers.
- Send restrictive security headers, including Content Security Policy,
  `X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`.
- Do not enable CORS.
- Never place the SponsoredTokens key in HTML, JavaScript, logs, URLs,
  exceptions, fixtures, screenshots, responses, or repository files.
- Reject an upstream success response if its text contains the configured key.
- Do not read or reference `OPENAI_API_KEY` anywhere in the local application.
- Do not expose a browser provider selector or fallback control.
- Do not persist messages in local storage, cookies, files, or databases.
- Escape all rendered model and user content by using text-only DOM operations.
- Use explicit request-size, message-count, content-length, response-size, and
  timeout limits.

## Operator workflow

The operator starts the service from a PowerShell window that can read the
existing user-level `SPONSOREDTOKENS_API_KEY` variable:

```powershell
python apps/sponsoredtokens-web/server.py --open
```

The server prints only the loopback URL, provider, model, and readiness state.
It never prints the key. `Ctrl+C` stops the service, and closing or refreshing
the browser tab clears the in-memory conversation.

The local Codex launcher remains configured for SponsoredTokens only. ChatGPT
web continues through the user's OpenAI login and plan; it does not inherit or
read this local application's environment.

## Testing strategy

Unit and integration-style tests use the standard library and mock the outbound
HTTP boundary. Required coverage includes:

- health response with and without the configured SponsoredTokens key;
- valid chat request and model text extraction;
- complete sponsor footer preservation;
- invalid JSON, oversized bodies, invalid roles, empty content, and too many
  messages;
- upstream 401, 402, 429, timeout, and generic failure mapping;
- rejection of success text containing the configured key;
- absence of key material in browser responses and logs;
- absence of OpenAI endpoint/model/key/fallback references from application code;
- path traversal rejection and expected security headers;
- loopback-only bind validation.

The optional live smoke test runs only when explicitly requested and when
`SPONSOREDTOKENS_API_KEY` is available. It sends a minimal prompt, asserts a
nonempty response, and reports only pass/fail/provider/model metadata.

## Files to add

```text
apps/sponsoredtokens-web/
  README.md
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
3. Provider, model, connection state, and sponsor footer remain visible.
4. No local application path reads or uses `OPENAI_API_KEY`.
5. Refreshing the page clears history and no conversation is written to disk.
6. Tests cover validation, security boundaries, upstream failures, and secret
   redaction.
7. The SponsoredTokens live smoke test passes with the existing saved key.
8. Repository governance gates and relevant test suites pass.

## Deferred follow-up

After this version is validated, a separate design can add selected
WhiteChronos agent capabilities behind explicit server-side allowlists. That
follow-up must not expose arbitrary shell or MCP access to browser input and
must retain the repository's Runtime Doctor and provenance requirements.

Any future OpenAI Platform integration, local or hosted, requires a separate
specification and must not silently reuse ChatGPT subscription assumptions.
