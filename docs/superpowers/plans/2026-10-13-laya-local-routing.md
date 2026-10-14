# Laya Local Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hosted TypeSafe routing in the private SponsoredTokens chat with a supervised local Laya classifier and a deterministic fallback that keeps the chat available without TypeSafe credits or credentials.

**Architecture:** Preserve the existing `select_model` seam. A loopback-only Laya adapter implements the System One decision path; a deterministic adapter owns degraded operation. The Windows installer owns a pinned Python 3.11 Laya runtime and supervises the classifier independently from the chat server.

**Tech Stack:** Python 3.11 standard library, `laya[serve]==0.4.6`, PowerShell, Windows Startup shortcut, browser JavaScript, `unittest`/pytest.

**Spec:** `docs/superpowers/specs/2026-10-13-laya-local-routing-design.md`

## Global Constraints

- SponsoredTokens remains the only response generator and continues to use `SPONSOREDTOKENS_API_KEY` only.
- The application must not read, require, or transmit `TYPESAFE_API_KEY`.
- Chat binds to `127.0.0.1:8765`; Laya binds to `127.0.0.1:8770`.
- Only the final user message, truncated to 4,000 characters, reaches Laya.
- The accepted routes remain `fast`, `balanced`, and `deep`, mapped to the existing SponsoredTokens model identifiers.
- A non-`deep` Laya route requires confidence `>= 0.70`; valid `deep` remains admissible regardless of concentration.
- The initial local package pin is `laya[serve]==0.4.6` in an application-owned Python 3.11 environment.
- The multilingual checkpoint is the only preloaded/resident Laya checkpoint unless later measurements justify another.
- No public demo or alternate hosted classifier may be an automatic fallback.
- No credentials, messages, upstream bodies, or raw exception details may appear in output, logs, process arguments, or health responses.
- Preserve the unrelated untracked `docs/glossario-interativo.md`.

## Review Focus

- A non-Laya process or stale server occupies port 8770: the protocol probe must fail closed to deterministic routing rather than report Laya ready.
- Laya selects `fast` or `balanced` below confidence 0.70: the deterministic policy must make the effective decision.
- Windows paths contain spaces or non-ASCII characters: process launches and file operations must use argument arrays and literal paths.
- Package preparation or checkpoint warm-up fails: the last verified installed chat must remain usable and the Startup shortcut must not point at an incomplete runtime.
- Exceptions contain message text, URLs, headers, or key material: externally visible errors and status must reduce them to stable safe codes.

---

## File Map

- `apps/sponsoredtokens-web/routing.py` — routing types, local Laya HTTP adapter, deterministic policy, response validation, and readiness probe.
- `apps/sponsoredtokens-web/providers.py` — SponsoredTokens configuration and consumption of the routing interface.
- `apps/sponsoredtokens-web/server.py` — environment loading, health contract, injection of router probe, and safe smoke metadata.
- `apps/sponsoredtokens-web/static/app.js` — exact router labels shown to the user.
- `apps/sponsoredtokens-web/tests/test_routing.py` — isolated deterministic and Laya protocol behavior.
- `apps/sponsoredtokens-web/tests/test_server.py` — provider, HTTP, UI, CLI, and Windows integration behavior.
- `apps/sponsoredtokens-web/requirements-laya.txt` — reviewed exact top-level Laya runtime pin.
- `apps/sponsoredtokens-web/windows/Run-LocalChat.ps1` — independent Laya/chat process supervision and bounded restart policy.
- `apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1` — runtime preparation, stable-copy update, status, start, stop, and uninstall lifecycle.
- `apps/sponsoredtokens-web/README.md` — install, operation, status, failure, rollback, and removal instructions.
- `apps/sponsoredtokens-web/THIRD_PARTY_NOTICES.md` — Laya upstream, version, checkpoint family, and Apache-2.0 notice.

### Task 1: Local routing module

**Files:**
- Create: `apps/sponsoredtokens-web/tests/test_routing.py`
- Modify: `apps/sponsoredtokens-web/routing.py`

**Interfaces:**
- Produces: `RoutingConfig(endpoint: str = "http://127.0.0.1:8770/v1/systemone", model: str = "multilingual", timeout_seconds: float = 2.0, min_confidence: float = 0.70)`.
- Produces: `RoutingDecision(model: str, router: str)` where `router` is exactly `laya` or `deterministic`.
- Produces: `deterministic_route(messages: list[dict[str, str]]) -> RoutingDecision`.
- Produces: `select_model(config: RoutingConfig, messages: list[dict[str, str]], *, opener: Callable | None = None) -> RoutingDecision`.
- Produces: `probe_router(config: RoutingConfig, *, opener: Callable | None = None) -> bool`.

- [ ] **Step 1: Add failing deterministic-route fixtures**

Create tests named `test_deterministic_routes_high_risk_and_code_to_deep`, `test_deterministic_routes_explicit_short_transform_to_fast`, `test_deterministic_routes_ordinary_request_to_balanced`, and `test_deterministic_prefers_deep_over_fast_indicator`. Assert the exact existing SponsoredTokens model IDs and `router="deterministic"`.

- [ ] **Step 2: Run the deterministic tests and verify RED**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_routing.py" -v`

Expected: FAIL because `RoutingConfig` and `deterministic_route` do not exist.

- [ ] **Step 3: Implement the deterministic adapter**

In `routing.py`, add `RoutingConfig` and `deterministic_route`. Apply ordered rules from the spec: deep indicators first, then narrowly enumerated short transformation intents, then balanced. Keep `_last_user_message` as the single bounded extractor.

- [ ] **Step 4: Run the deterministic tests and verify GREEN**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_routing.py" -v`

Expected: all deterministic tests PASS.

- [ ] **Step 5: Add failing Laya protocol and failure-path tests**

Add tests asserting:

- the request URL is exactly the configured loopback endpoint;
- no `Authorization` header exists;
- the payload uses model `multilingual` and only the final 4,000 user characters;
- valid `fast`, `balanced`, and `deep` choices map correctly;
- non-`deep` confidence below `0.70` delegates to the deterministic adapter;
- timeout, refusal, redirect, oversized body, malformed JSON, non-finite numbers, unknown choice, and missing probability/confidence fields delegate deterministically;
- exception messages containing a sentinel prompt, URL, header, or credential never appear in `str`/`repr` output, health metadata, or captured diagnostics;
- `probe_router` returns true only for a structurally valid response and false for a merely listening incompatible server.

- [ ] **Step 6: Run the Laya tests and verify RED**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_routing.py" -v`

Expected: FAIL because the current adapter requires a TypeSafe key, uses the hosted endpoint, and has no probe.

- [ ] **Step 7: Implement the Laya adapter and readiness probe**

Change `select_model` to accept `RoutingConfig`, send no credential, reject redirects, bound the request/response, validate finite probabilities and confidence, and invoke `deterministic_route` for every invalid or unavailable result. Implement `probe_router` through the same validator with a fixed safe local state.

- [ ] **Step 8: Run the routing suite and verify GREEN**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_routing.py" -v`

Expected: all tests PASS with no network access.

- [ ] **Step 9: Commit the routing module**

```powershell
git add -- apps/sponsoredtokens-web/routing.py apps/sponsoredtokens-web/tests/test_routing.py
git commit -m "feat: add local Laya routing fallback"
```

### Task 2: Provider, server health, and browser integration

**Files:**
- Modify: `apps/sponsoredtokens-web/providers.py`
- Modify: `apps/sponsoredtokens-web/server.py`
- Modify: `apps/sponsoredtokens-web/static/app.js`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Task 1 `RoutingConfig`, `RoutingDecision`, `select_model`, and `probe_router`.
- Produces: `SponsoredTokensConfig(api_key: str | None, routing: RoutingConfig)` with secret-safe `repr`.
- Produces: `make_handler(config, transport=call_sponsoredtokens, router_probe=probe_router)`.
- Produces: health JSON fields `ready`, `provider`, `model`, `router`, `router_ready`, and `router_endpoint`.

- [ ] **Step 1: Replace hosted-Jev integration expectations with failing local-router expectations**

Update existing tests so configuration reads only `SPONSOREDTOKENS_API_KEY`; provider calls receive `config.routing`; health reports `laya` only when the injected probe returns true and otherwise reports `deterministic`; health always reports `router_endpoint="loopback"`. Assert that a sentinel `TYPESAFE_API_KEY` is never accessed or displayed.

- [ ] **Step 2: Add failing per-response and UI metadata tests**

Assert that `/api/chat` preserves `router=laya` or `router=deterministic` from the actual `ProviderResult`, and that `app.js` renders `Laya local` and `Fallback determinístico` without inferring use from configuration presence.

- [ ] **Step 3: Run affected tests and verify RED**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_server.py" -v`

Expected: FAIL on the old `jev_api_key`, old health shape, and old UI labels.

- [ ] **Step 4: Implement configuration and provider integration**

Replace `jev_api_key` with a `RoutingConfig` field, remove `TYPESAFE_API_KEY` from `load_config_from_environment`, and call Task 1 `select_model(config.routing, messages)` from `call_sponsoredtokens`.

- [ ] **Step 5: Implement health and browser integration**

Inject `router_probe` at the server seam. Compute `router_ready` from the probe, derive `router` from that boolean, keep `ready` tied only to SponsoredTokens, and update `app.js` labels using response metadata.

- [ ] **Step 6: Run app tests and verify GREEN**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -v`

Expected: all app tests PASS and no test contacts an external service.

- [ ] **Step 7: Commit provider and UI integration**

```powershell
git add -- apps/sponsoredtokens-web/providers.py apps/sponsoredtokens-web/server.py apps/sponsoredtokens-web/static/app.js apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: expose local router health"
```

### Task 3: Isolated Laya runtime and Windows supervision

**Files:**
- Create: `apps/sponsoredtokens-web/requirements-laya.txt`
- Modify: `apps/sponsoredtokens-web/windows/Run-LocalChat.ps1`
- Modify: `apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1`
- Modify: `apps/sponsoredtokens-web/tests/test_server.py`

**Interfaces:**
- Consumes: Task 2 health endpoint and stable installed application layout.
- Produces: application-owned runtime root `%LOCALAPPDATA%\WhiteChronos\SponsoredTokensRuntimes\laya-0.4.6-py311`.
- Produces: status JSON fields `installed`, `running`, `ready`, `routerRunning`, `routerReady`, `router`, `url`, and `task`.

- [ ] **Step 1: Add failing installer and status tests**

Extend `WindowsAutomationTests` to assert that `Install -WhatIf -Json` names the exact Laya pin and runtime root without modifying them, status returns the new stable fields without secrets, the source scripts never read `TYPESAFE_API_KEY`, and paths are passed as literal arguments rather than shell-built command strings.

- [ ] **Step 2: Add failing lifecycle safety tests**

Add tests or bounded PowerShell test helpers that prove:

- dependency preparation occurs before installed processes are stopped;
- an injected preparation failure leaves the current installed-copy hashes and shortcut unchanged;
- process matching is restricted to resolved paths below approved application/runtime roots;
- restart backoff is capped at 60 seconds and maintained independently for chat and Laya;
- uninstall refuses roots outside `%LOCALAPPDATA%\WhiteChronos`.

- [ ] **Step 3: Run Windows tests and verify RED**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_server.py" -v`

Expected: FAIL because the current installer has no isolated Laya runtime or router lifecycle fields.

- [ ] **Step 4: Add the reviewed dependency pin**

Create `requirements-laya.txt` containing the exact top-level requirement `laya[serve]==0.4.6` and a comment naming the Apache-2.0 upstream. Do not add Laya to the user's global Python.

- [ ] **Step 5: Implement safe runtime preparation**

Make `Manage-AutoStart.ps1` locate Python 3.11 explicitly, prepare the versioned runtime before stopping the working installation, install from `requirements-laya.txt`, verify the package import/version, and only then update the stable application copy and Startup shortcut. A failed new runtime may be removed only after resolving and confirming it is below `SponsoredTokensRuntimes`.

- [ ] **Step 6: Implement independent supervision**

Update `Run-LocalChat.ps1` to launch Laya with `LAYA_HOST=127.0.0.1`, `LAYA_PORT=8770`, `LAYA_MODELS=multilingual`, `LAYA_DEFAULT_MODEL=multilingual`, and one loaded checkpoint. Supervise Laya and chat as separate child processes, use per-process exponential backoff capped at 60 seconds, and never put message or credential values in arguments.

- [ ] **Step 7: Implement truthful status, stop, and uninstall behavior**

Probe both services with two-second bounds, report safe state fields, stop only verified installed processes, and remove application/runtime directories only after containment checks. Leave the user-level SponsoredTokens credential unchanged.

- [ ] **Step 8: Run Windows and complete app tests and verify GREEN**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -v`

Expected: all tests PASS; `Install -WhatIf` changes no files or processes.

- [ ] **Step 9: Commit Windows runtime automation**

```powershell
git add -- apps/sponsoredtokens-web/requirements-laya.txt apps/sponsoredtokens-web/windows/Run-LocalChat.ps1 apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 apps/sponsoredtokens-web/tests/test_server.py
git commit -m "feat: supervise local Laya runtime"
```

### Task 4: Documentation, provenance, and rollback contract

**Files:**
- Create: `apps/sponsoredtokens-web/THIRD_PARTY_NOTICES.md`
- Modify: `apps/sponsoredtokens-web/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Tasks 1–3 commands, status fields, and version pin.
- Produces: operator instructions that never require a TypeSafe key and a provenance record for the installed classifier.

- [ ] **Step 1: Add failing documentation assertions**

Add a focused test in `test_server.py` asserting that the application README contains the exact install/status/stop/uninstall commands, explains `laya` versus `deterministic`, states that SponsoredTokens remains the generator, and contains no instruction to create or save `TYPESAFE_API_KEY`.

- [ ] **Step 2: Run the documentation assertion and verify RED**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -p "test_server.py" -v`

Expected: FAIL because the current README documents hosted Jev and a TypeSafe key.

- [ ] **Step 3: Update operator documentation**

Document installation, first checkpoint download, expected cold start, GPU/CPU selection, status interpretation, degraded deterministic operation, safe live smoke, rollback, and uninstallation. State explicitly that neither Laya nor local routing creates generative tokens.

- [ ] **Step 4: Record third-party provenance**

Create `THIRD_PARTY_NOTICES.md` naming `NandhaKishorM/laya`, Apache-2.0, package `0.4.6`, the multilingual checkpoint family, and that no substantive upstream source is copied into WhiteChronos.

- [ ] **Step 5: Run app tests and verify GREEN**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -v`

Expected: all app tests PASS.

- [ ] **Step 6: Commit documentation**

```powershell
git add -- apps/sponsoredtokens-web/README.md apps/sponsoredtokens-web/THIRD_PARTY_NOTICES.md README.md apps/sponsoredtokens-web/tests/test_server.py
git commit -m "docs: document local Laya operations"
```

### Task 5: Install and validate the real local runtime

**Files:**
- Runtime only: `%LOCALAPPDATA%\WhiteChronos\SponsoredTokensLocalChat`
- Runtime only: `%LOCALAPPDATA%\WhiteChronos\SponsoredTokensRuntimes\laya-0.4.6-py311`

**Interfaces:**
- Consumes: Task 3 installer and Task 2 health contract.
- Produces: live loopback Laya and chat processes with deterministic degraded operation.

- [ ] **Step 1: Capture the pre-install rollback evidence**

Run the status command with `-Json`, record current installed-file SHA-256 hashes, current shortcut target, and current health payload. Store only safe metadata in the implementation report; do not record environment-variable values.

- [ ] **Step 2: Preview installation**

Run:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -WhatIf -Json
```

Expected: exact application root, runtime root, Laya pin, task, and loopback URLs; `changed=false`.

- [ ] **Step 3: Install the isolated runtime and stable copy**

Run:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -Json
```

Expected: exit 0 and `changed=true`; no global package installation.

- [ ] **Step 4: Start and warm the runtime**

Run:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Start -Json
```

Poll status with bounded waits of at most 60 seconds per call until the checkpoint warm-up either succeeds or reports deterministic degraded operation. Do not use an unbounded wait.

- [ ] **Step 5: Prove local Laya protocol use**

Send a bounded local System One request directly to `127.0.0.1:8770`, then call the chat routing seam with an injected/non-generative probe. Redact the request and response bodies. Evidence must show a real valid decision, `router=laya`, and the selected SponsoredTokens model without printing the message or any credential.

- [ ] **Step 6: Prove deterministic degraded operation**

Stop only the verified Laya child process, invoke a routing smoke case, and verify `router=deterministic` while chat health remains `ready=true`. Allow the supervisor to restore Laya and verify a later successful probe returns `router=laya`.

- [ ] **Step 7: Run one authorized end-to-end SponsoredTokens smoke**

Run:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Expected: `LIVE_SMOKE=PASS provider=SponsoredTokens model=<selected-model> router=laya|deterministic`, with no response body or credential displayed.

- [ ] **Step 8: Record operational evidence**

Create `docs/superpowers/reports/2026-10-13-laya-local-routing-evidence.md` containing versions, safe process/status metadata, commands, exit codes, test counts, router transitions, and rollback result. Exclude prompts, responses, keys, headers, and raw exception text.

- [ ] **Step 9: Commit runtime evidence**

```powershell
git add -- docs/superpowers/reports/2026-10-13-laya-local-routing-evidence.md
git commit -m "test: record local Laya runtime evidence"
```

### Task 6: Repository gates and final review

**Files:**
- Modify only if a gate exposes a defect covered by this plan.

**Interfaces:**
- Consumes: all previous task deliverables.
- Produces: fresh verification evidence suitable for branch completion.

- [ ] **Step 1: Run format and diff checks**

Run: `git diff --check 019a6af7..HEAD`

Expected: exit 0 and no output.

- [ ] **Step 2: Run the complete application suite**

Run: `python -m unittest discover -s apps/sponsoredtokens-web/tests -v`

Expected: all tests PASS with zero failures/errors.

- [ ] **Step 3: Run the complete repository suite**

Run: `python -m pytest -q`

Expected: exit 0 with zero failures.

- [ ] **Step 4: Run mandatory engineering gates**

```powershell
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Expected: both gates PASS and both focused suites report zero failures.

- [ ] **Step 5: Apply final GitHub Arena review**

Review correctness, completeness, robustness, specificity, clarity, licensing, provenance, loopback restrictions, secret handling, Windows process containment, failure backoff, and truthful runtime claims. Fix only verified defects through new red-green cycles.

- [ ] **Step 6: Re-run every affected and full gate after review fixes**

Expected: fresh exit-zero evidence for the application suite, repository suite, engineering gates, protocol gates, local Laya smoke, deterministic degraded smoke, and live SponsoredTokens smoke.

- [ ] **Step 7: Confirm branch state**

Run: `git status --short --branch` and `git log --oneline --decorate -8`.

Expected: only the preserved unrelated `docs/glossario-interativo.md` remains untracked; all planned work is committed on `feat/sponsoredtokens-local-chat`.

## Execution Notes

- Implement each task in order because Tasks 2–5 consume interfaces defined by earlier tasks.
- Follow red-green-refactor for every behavior change; never edit production code before observing the corresponding test fail for the expected reason.
- Do not install `suenot/codex-jev-router` in this plan. Its global Codex configuration impact requires a separate preview and approval after this runtime is validated.
- Do not push, open a pull request, merge, or change `main` without separate user authorization.
