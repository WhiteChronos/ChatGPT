# Laya local routing for the SponsoredTokens chat

Date: 2026-10-13

## Status

Approved conversational design. This document specifies the implementation that
must be reviewed before an implementation plan is written. It does not authorize
installation by itself.

## Outcome

The private browser chat continues to use SponsoredTokens as its only response
generator. A local Laya process replaces the hosted TypeSafe Jev request used to
choose between the existing `fast`, `balanced`, and `deep` SponsoredTokens models.
If the local classifier is unavailable, slow, uncertain, or malformed, a bounded
deterministic classifier chooses a route without blocking the chat.

The completed system must:

- require no TypeSafe account, credits, or API key;
- keep SponsoredTokens as the only generative provider;
- expose only loopback HTTP listeners;
- start automatically for the current Windows user;
- remain usable when Laya is unavailable;
- report the router that actually selected each response model;
- never put credentials, message text, or upstream response bodies in logs or
  process arguments;
- remain removable without affecting the SponsoredTokens credential or ChatGPT
  web usage.

## Existing system

The application lives under `apps/sponsoredtokens-web`. The browser sends a
validated in-memory message history to a loopback Python server on
`127.0.0.1:8765`. The server currently sends the last user message to hosted Jev
when `TYPESAFE_API_KEY` exists and otherwise fixes the route to `deep`. It then
sends the complete validated history to SponsoredTokens.

The Windows installer copies a stable runtime to
`%LOCALAPPDATA%\WhiteChronos\SponsoredTokensLocalChat`, creates a current-user
Startup shortcut, and supervises the chat process. The current stable process is
healthy with `router=fixed`.

The target machine has Windows 11, Python 3.11, 64 GB RAM, an Intel i9-14900HX,
and an NVIDIA RTX 4060 Laptop GPU with 8 GB VRAM. Laya and PyTorch are not
currently installed in the Python environment used by the chat.

## Considered approaches

### A. Separate loopback Laya service with deterministic fallback — selected

Run Laya as an application-owned loopback service and keep the chat-to-router
seam as the TypeSafe-compatible `POST /v1/systemone` contract. This preserves a
small routing interface, isolates model dependencies from the chat server, allows
the router to restart independently, and makes later replacement possible without
changing the provider transport.

The additional process is justified because the same local System One endpoint
can later support another explicitly approved local application. The supervisor
and health reporting must hide that process complexity from chat callers.

### B. Embed the Laya Python library in the chat process — rejected

Embedding removes one listener and one process, but couples model import,
checkpoint loading, GPU memory, and failures to the chat server. A classifier
crash or dependency conflict could then stop the response provider. It also makes
the existing HTTP seam hypothetical rather than reusable.

### C. Use a free hosted demo or temporary free provider — rejected for runtime

Public demo endpoints are useful for manual comparison but have external rate
limits, privacy consequences, and no durability guarantee. They must not be an
automatic fallback. The application must not silently send user messages to a
different hosted classifier.

## Architecture

The system has four modules separated by explicit interfaces:

1. **Browser chat** — sends and displays messages; it never sees provider or
   classifier credentials.
2. **Chat server** — validates requests, selects a model through the routing
   module, calls SponsoredTokens, and returns safe metadata.
3. **Routing module** — presents one interface to the provider transport:
   `select_model(router_config, messages) -> RoutingDecision`. Its implementation
   tries the Laya adapter and then the deterministic adapter.
4. **Laya runtime** — serves the System One HTTP contract locally and owns model
   loading and inference.

The provider transport depends only on the routing interface. It must not know
whether the decision came from Laya or deterministic policy. The returned
`RoutingDecision` contains the selected SponsoredTokens model and the exact router
label, either `laya` or `deterministic`.

## Runtime topology

- Chat: `http://127.0.0.1:8765`
- Laya: `http://127.0.0.1:8770/v1/systemone`
- Laya package: application-owned virtual environment using Python 3.11 and a
  reviewed, exact `laya[serve]` version pin. The first implementation plan must
  start from the currently reviewed `0.4.6` release and update the pin only after
  re-running license, compatibility, and smoke checks.
- Laya model: multilingual checkpoint, because the primary chat language is
  Portuguese. Only one checkpoint remains resident unless measured behavior
  proves another is necessary.
- Binding: both processes bind only to IPv4 loopback. No firewall exposure or
  internet publication is introduced.

The installation may use CUDA only when an explicit capability probe in the
application-owned environment succeeds. Otherwise it uses CPU. Lack of GPU
acceleration is not an installation failure if the bounded latency test passes.

## Request flow

1. The browser submits the complete in-memory history to `/api/chat`.
2. The chat server validates the body, message count, roles, and content limits.
3. The routing module extracts only the final user message and truncates it to
   4,000 characters.
4. The Laya adapter sends one `choice` question with the closed options `fast`,
   `balanced`, and `deep` to the loopback System One endpoint.
5. The adapter accepts a response only when the HTTP status, JSON structure,
   option name, numeric values, response size, and confidence policy are valid.
6. When accepted, the routing decision reports `router=laya`.
7. When rejected or unavailable, the deterministic adapter classifies the same
   bounded message and reports `router=deterministic`.
8. The provider transport sends the full validated history and selected model to
   SponsoredTokens.
9. The browser displays the response, provider, selected model, and actual router.

Laya never receives the complete conversation history, the SponsoredTokens key,
or the SponsoredTokens response.

## Laya decision contract

The request retains one narrow `choice` question. The options mean:

- `fast`: simple formatting, extraction, translation, or a short factual answer;
- `balanced`: ordinary analysis, drafting, or a bounded multi-step request;
- `deep`: code, debugging, security, high-risk content, complex reasoning,
  ambiguity, or many dependent steps.

The model identifier sent to a Laya-compatible service must be one explicitly
supported by that service. The implementation must not depend on the hosted-only
`jev-latest` identifier being accepted locally.

A Laya decision is advisory. Code owns route admission. Low confidence, missing
probabilities, non-finite values, an unknown choice, an oversized body, a redirect,
or a timeout all cause deterministic fallback.

The initial confidence threshold must be explicit and covered by tests. The
implementation plan must select it from local fixture evaluation rather than copy
a hosted Jev threshold. Until that evaluation establishes a lower safe value, the
default is conservative: a non-`deep` Laya route requires confidence of at least
`0.70`; `deep` may be accepted whenever it is the valid selected option because it
is the quality-preserving route.

## Deterministic fallback

The fallback is local code with no model, network request, or credential. Rules
are ordered from conservative to economical:

1. Select `deep` for code blocks, stack traces, debugging, security, credentials,
   legal/medical/financial risk, explicit high assurance, long structured input,
   or multiple dependent requested actions.
2. Select `fast` only for a short, single-operation request that explicitly asks
   for translation, formatting, extraction, a one-line summary, or a brief factual
   answer and contains no `deep` indicator.
3. Select `balanced` for all remaining requests.

Unknown and ambiguous cases therefore do not fall to `fast`. The rules and their
fixtures are part of the public routing interface and must be changed only with
tests demonstrating the intended route.

## Configuration and credentials

`TYPESAFE_API_KEY` is removed from this application's configuration, Windows
runner, documentation, and health logic. An unrelated user-level variable may
remain on the machine, but this application must neither read nor transmit it.

The application continues to read only `SPONSOREDTOKENS_API_KEY` as a provider
credential. The Laya URL is a non-secret application setting with a loopback-only
default. A command-line or environment override must be rejected unless it resolves
to the approved IPv4 loopback host and configured local port range.

Neither key material nor message content may appear in `repr`, status output,
exceptions, logs, shortcut arguments, process command lines, or health payloads.

## Windows installation and supervision

The stable installation remains under
`%LOCALAPPDATA%\WhiteChronos\SponsoredTokensLocalChat`. The installer owns a
virtual environment below that root and must use an exact dependency lock or
version pin. It must never install Laya globally.

`Manage-AutoStart.ps1 -Action Install` performs a replace-in-place application
update, creates or updates the isolated runtime, and preserves the existing
current-user Startup shortcut. Installation must fail safely before replacing the
working copy if dependency preparation or verification fails.

The hidden runner supervises Laya and the chat independently:

- start Laya on loopback;
- wait for bounded readiness and run one local warm-up decision;
- start the chat even if Laya readiness fails, because deterministic fallback is
  sufficient for availability;
- restart a failed process with bounded exponential backoff;
- avoid duplicate instances by checking the approved loopback ports and installed
  process paths;
- stop only processes whose executable command line belongs to the verified
  installation root.

The status command reports installation, chat liveness, provider readiness, Laya
liveness, active router state, URL, and task name. It reports safe error codes, not
raw exception text.

## Health and user interface

`GET /api/health` distinguishes provider readiness from router readiness. Its
stable fields include:

- `ready`: whether SponsoredTokens is configured;
- `provider`: `SponsoredTokens`;
- `model`: current conservative default model;
- `router`: `laya` after a successful recent probe, otherwise `deterministic`;
- `router_ready`: whether a recent bounded local probe confirmed Laya;
- `router_endpoint`: the fixed label `loopback`, never the full configurable URL.

The chat remains usable whenever `ready` is true, regardless of `router_ready`.
The response from `/api/chat` reports the router that selected that specific model.
The browser displays `Laya local` or `Fallback determinístico`; it must not describe
configuration presence as proof that Laya handled a request.

## Failure handling

- Laya connection failure, timeout, redirect, malformed JSON, invalid numbers,
  unknown option, low confidence, or oversized response: use deterministic routing.
- Laya cold start: use deterministic routing for requests received before readiness;
  do not queue the browser indefinitely.
- Laya process crash: keep the chat available and let the supervisor restart Laya.
- SponsoredTokens authentication, quota, rate limit, timeout, or upstream failure:
  preserve the existing stable provider error mapping. Laya does not replace the
  generative provider.
- Installer failure: retain the last verified stable copy and do not change the
  Startup shortcut to an incomplete runtime.
- Repeated restart failure: back off and report degraded deterministic operation;
  do not create an unbounded rapid restart loop.

## Security and privacy

- All local listeners bind only to `127.0.0.1`.
- HTTP redirects are rejected for both routing and provider credentials.
- Request and response sizes remain bounded.
- Laya receives only a bounded final user message.
- No public demo endpoint is an automatic fallback.
- Downloaded Python packages and checkpoints are pinned or verified before use.
- Third-party licenses and notices are retained in repository documentation and
  the installed runtime where their terms require it.
- Uninstallation verifies the resolved installation path before recursive removal.

## Tests and release evidence

Implementation follows red-green-refactor through the existing public seams.
Required automated coverage includes:

1. valid Laya `fast`, `balanced`, and `deep` decisions;
2. confidence threshold behavior;
3. deterministic `fast`, `balanced`, and `deep` fixtures;
4. timeout, refused connection, redirect, oversized response, malformed JSON,
   non-finite values, unknown choice, and missing fields;
5. proof that no TypeSafe key is read or transmitted;
6. proof that only the final bounded user message reaches the router;
7. health semantics independent of provider readiness;
8. per-response router metadata shown correctly by the browser;
9. Windows install `-WhatIf`, status JSON, safe process matching, independent
   restart, and uninstall path containment;
10. preservation of existing HTTP authority, body-size, static-file, provider
    transport, and secret-redaction tests.

Release verification requires:

- the complete SponsoredTokens application test suite;
- the complete repository test suite;
- Engineering Compatibility Gate;
- Protocol Zero Gate;
- a local Laya protocol smoke test;
- a deterministic fallback smoke test with Laya stopped;
- one explicitly authorized live SponsoredTokens smoke request using each router
  path that can be exercised without exposing credentials;
- a final GitHub Arena review covering correctness, completeness, robustness,
  specificity, clarity, licensing, provenance, and Windows lifecycle behavior.

Tool discovery, a listening port, or a configured environment variable is not
sufficient evidence of live routing. Evidence must contain an actual decision and
the resulting SponsoredTokens request model, with secrets and message content
redacted.

## Rollout and rollback

Rollout is staged:

1. implement and test routing without changing the stable installation;
2. install the isolated Laya runtime and validate its protocol locally;
3. update the stable copy and supervisor;
4. confirm health and deterministic degraded operation;
5. run the authorized end-to-end smoke test;
6. leave the previous stable source and installer backup recoverable until final
   validation completes.

Rollback stops installed processes, restores the last verified application copy,
and restarts the chat with deterministic routing. Rollback never deletes or changes
`SPONSOREDTOKENS_API_KEY`.

## Deferred integrations

Installing `suenot/codex-jev-router` as a deterministic evidence-selection MCP is
a separate project. Its installer changes the global Codex configuration and can
make the server visible in other workspaces even when file access is restricted to
one configured root. It therefore requires a separate preview, shared-workspace
impact warning, approval, installation, Codex restart, and runtime smoke test.

Simple Jev public demo, OpenCode's temporarily free Jev model, and heavier local
Open-Jev implementations remain comparison or contingency references. They are not
automatic runtime fallbacks and are not installed by this design.

## Third-party provenance

The selected classifier upstream is `https://github.com/NandhaKishorM/laya`,
published under Apache-2.0. The implementation plan must record the exact package
version, checkpoint identifiers, resolved artifacts, and applicable notices used by
the installed runtime. No substantive upstream source is copied into this
repository; the application integrates through the published package and local
System One interface.

## Non-goals

- Generating responses with Laya.
- Combining TypeSafe credits with SponsoredTokens.
- Adding OpenAI API fallback to the local chat.
- Publishing the chat or router to the network.
- Persisting conversation history.
- Installing every discovered Jev-related repository.
- Modifying ChatGPT web billing, plan limits, or authentication.
- Claiming that local classification creates additional generative tokens.

## Acceptance criteria

The design is complete when implementation evidence proves all of the following:

- the chat answers through SponsoredTokens with no TypeSafe credential;
- a valid local Laya decision selects the expected SponsoredTokens model;
- stopping Laya changes the reported router to `deterministic` without making the
  chat unavailable;
- restarting Laya restores `router=laya` after a successful local probe;
- automatic startup survives a Windows sign-in restart;
- status and health output reveal no secrets or message content;
- every required automated and live gate passes with fresh evidence;
- rollback restores a usable deterministic chat.
