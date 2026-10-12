# SponsoredTokens Local Chat — Design

## Context and intent

WhiteChronos needs a private local web chat that uses the already validated
SponsoredTokens account without exposing its API key to browser code or Git.
The first version is intentionally small: prove a secure browser-to-local-server
chat loop before integrating WhiteChronos agents, MCP servers, deployment, or
persistent storage.

The application lives at `apps/sponsoredtokens-web` in this repository. It is
for one user on one Windows computer and binds only to the loopback interface.

## Goals

- Serve a usable chat interface at a local `http://127.0.0.1:<port>` address.
- Send prompts through the SponsoredTokens Responses-compatible endpoint.
- Read `SPONSOREDTOKENS_API_KEY` only from the server process environment.
- Keep conversation history only in browser memory for the current tab.
- Display connection state, provider, model, and the complete sponsor footer.
- Provide deterministic unit tests without making paid or sponsored network calls.
- Provide an explicit, opt-in live smoke test for operators who have a valid key.

## Non-goals

- Publishing the application to the internet.
- Replacing `chatgpt.com`, Codex Cloud, or ChatGPT account limits.
- Using ChatGPT-plan credits as an API fallback.
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
        | Authorization: Bearer <environment key>
        v
https://sponsoredtokens.com/api/v1/responses
```

### Components

1. `server.py`
   - Parses command-line options for port and optional browser opening.
   - Refuses non-loopback bind addresses.
   - Serves static files from a fixed directory without arbitrary path access.
   - Implements health and chat API routes.
   - Calls SponsoredTokens with `urllib.request` and bounded timeouts.
   - Redacts upstream error details before returning them to the browser.

2. `static/index.html`
   - Defines the accessible chat layout and status panel.
   - Loads only repository-owned local assets.

3. `static/app.js`
   - Holds message history in an in-memory JavaScript array.
   - Sends the full current history to the local API for each turn.
   - Renders text with DOM text nodes, never `innerHTML`.
   - Preserves the sponsor footer exactly as returned in the model text.
   - Supports send, retry after error, and clear-session actions.

4. `static/app.css`
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
- The server converts messages into Responses API input and uses the configured
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
upstream failures. It does not relay headers, response bodies, account IDs, or
credentials from upstream errors.

## Security and privacy

- Bind to `127.0.0.1`, never `0.0.0.0`.
- Require same-origin requests and reject unexpected `Host` headers.
- Send restrictive security headers, including Content Security Policy,
  `X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`.
- Do not enable CORS.
- Never place the API key in HTML, JavaScript, logs, URLs, exceptions, fixtures,
  screenshots, or repository files.
- Do not persist messages in local storage, cookies, files, or databases.
- Escape all rendered model and user content by using text-only DOM operations.
- Use explicit request-size, message-count, content-length, and timeout limits.

## Operator workflow

The operator starts the service from a PowerShell window that can read the
existing user-level `SPONSOREDTOKENS_API_KEY` variable:

```powershell
python apps/sponsoredtokens-web/server.py --open
```

The server prints only the loopback URL, provider, model, and readiness state.
It never prints the key. `Ctrl+C` stops the service, and closing or refreshing
the browser tab clears the in-memory conversation.

## Testing strategy

Unit and integration-style tests use the standard library and mock the outbound
HTTP boundary. Required coverage includes:

- health response with and without a configured key;
- valid chat request and model text extraction;
- complete sponsor footer preservation;
- invalid JSON, oversized bodies, invalid roles, empty content, and too many
  messages;
- upstream 401, 402, 429, timeout, and generic failure mapping;
- absence of key material in browser responses and logs;
- path traversal rejection and expected security headers;
- loopback-only bind validation.

The optional live smoke test runs only when explicitly requested and when
`SPONSOREDTOKENS_API_KEY` is available. It sends a minimal prompt, asserts a
nonempty response, and reports only pass/fail metadata.

## Files to add

```text
apps/sponsoredtokens-web/
  README.md
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
4. Refreshing the page clears history and no conversation is written to disk.
5. Tests cover validation, security boundaries, upstream failures, and secret
   redaction.
6. The live smoke test passes with the existing saved key.
7. Repository governance gates and relevant test suites pass.

## Deferred follow-up

After this version is validated, a separate design can add selected
WhiteChronos agent capabilities behind explicit server-side allowlists. That
follow-up must not expose arbitrary shell or MCP access to browser input and
must retain the repository's Runtime Doctor and provenance requirements.
