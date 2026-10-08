# WhiteChronos Connection Controller + TinyFish Controller Design

**Status:** Conversational architecture approved; written specification awaiting user review  
**Date:** 2026-10-08  
**Repository:** `WhiteChronos/ChatGPT`  
**Base:** `main` at `8a3f175b92e6355dabd8ab11f19ba93a457de059`  
**Review method:** Superpowers architectural workflow + GitHub Arena structured 16-strategy review. The Arena pass in this ChatGPT runtime is sequential; no independent subagents are claimed.

## 1. Purpose

Extend the existing WhiteChronos Control Plane so every supported WhiteChronos conversation can establish a truthful connection state for the integrations it depends on, with GitHub, GitLab, TinyFish, Superpowers, GitHub Arena, Runtime Doctor and future plugins/apps following one fail-closed contract.

This design does **not** attempt to keep third-party OAuth sessions alive forever. Instead it makes connection state observable, repeatable, recoverable and explicit at conversation start and before sensitive actions.

The target user experience is:

```text
WhiteChronos task starts
-> official Superpowers bootstrap
-> connection preflight
-> required integrations classified from fresh evidence
-> missing/revoked/blocked connection reported precisely
-> task uses only integrations proven available
-> Runtime Doctor used when Codex host/runtime claims matter
-> GitHub/GitLab mutations remain evidence-driven
-> GitHub Arena reviews high-impact work before completion
```

## 2. Confirmed baseline

At the time this design was written, the active ChatGPT harness provided fresh evidence that:

- the GitHub connector is authenticated and can access `WhiteChronos/ChatGPT`;
- the authenticated GitHub installation covers all repositories for the linked WhiteChronos user installation;
- the GitLab connector is authenticated and can access `chronoswhite-group/ChronosWhite-project` with owner-level group access;
- the GitLab account exposes a GitHub identity link;
- existing GitHub/GitLab parity CI has produced `HEALTHY` evidence for exact provider identity/commit matching;
- the TinyFish ChatGPT app is installed and enabled;
- TinyFish service authentication is functional because a live wallet query succeeds;
- TinyFish search is callable;
- TinyFish Browser Profile listing currently returns an internal tool error;
- attempting to create a TinyFish Browser Profile from this harness is currently blocked by OpenAI safety settings;
- `.codex/config.toml` already enables Superpowers, Arena, ECC, Matt Pocock, Subagent Broker, Awesome LLM Apps controller and WhiteChronos Control Plane;
- the existing WhiteChronos Control Plane already owns runtime diagnosis, integration registry concepts and the distinction between repository configuration and live host capability.

These are runtime observations, not permanent guarantees. The design therefore requires timestamped evidence and never converts a past PASS into an eternal PASS.

## 3. Problem statement

The repository has two different classes of integration state:

1. **Repository/runtime configuration**
   - plugin manifests;
   - Codex marketplace registration;
   - `.codex/config.toml`;
   - registry descriptors;
   - MCP definitions;
   - CI and mirror policy.

2. **Current conversation/host state**
   - whether a ChatGPT plugin or connector is installed;
   - whether its tools are visible in this conversation;
   - whether OAuth/session authentication is still valid;
   - whether the required target repository/project is accessible;
   - whether an optional browser profile exists and is usable;
   - whether product policy blocks an operation even when the service is authenticated.

Today those facts can be conflated. A configured plugin may be unavailable in the host; an authenticated service may have one broken sub-capability; a browser-profile failure may be mistaken for a full TinyFish outage; and mirror parity may be confused with connector authentication.

The system needs one common state model that prevents those category errors.

## 4. Success criteria

The design is successful when the implementation can:

1. inspect current host/tool/plugin evidence without fabricating missing capabilities;
2. classify GitHub, GitLab and TinyFish independently;
3. distinguish plugin installation, host visibility, authentication, target access and live verification;
4. distinguish native connector health from TinyFish Browser Profile health;
5. keep GitHub/GitLab mirror parity independent from ChatGPT connector authentication;
6. prefer native GitHub/GitLab connectors for repository API work;
7. use TinyFish browser automation only for user-directed website workflows that require it;
8. avoid paid or mutating TinyFish operations during routine preflight;
9. give a deterministic recovery action for each failure class;
10. expose the same architecture to future plugins/apps through typed descriptors;
11. preserve Superpowers as the process owner and Arena as the final high-impact review layer;
12. remain truthful about the platform limit: repository code cannot force every unrelated ChatGPT conversation to load or authenticate every plugin forever.

For this project, “100% connected” means **all controllable required connection checks for the current task are PASS with fresh evidence**. It never means an external OAuth session is guaranteed never to expire.

## 5. Non-goals

This subsystem SHALL NOT:

- store GitHub, GitLab or TinyFish passwords, tokens, cookies or browser storage in Git;
- request passwords in chat;
- copy TinyFish browser cookies into repository files;
- automatically create TinyFish Browser Profiles during preflight;
- automatically run paid TinyFish Agent or Browser steps just to prove availability;
- automatically top up the TinyFish wallet or enable auto-reload;
- route normal Git operations through browser automation when a native connector exists;
- bypass OpenAI, GitHub, GitLab or TinyFish security/policy restrictions;
- claim `HOST_DISCOVERED` from repository configuration alone;
- claim Browser Profile authentication when `list_profiles` cannot prove it;
- claim GitHub/GitLab mirror parity from account identity alone;
- merge, deploy, canary, stable, live-smoke, R2/R3 or declare `PRODUCTION COMPLETE` without their separate gates.

## 6. Selected architecture

### 6.1 Design decision

The approved conceptual architecture contains a **WhiteChronos Connection Controller** and a **TinyFish Controller**.

The implementation SHALL avoid creating a second top-level control plane that duplicates the existing `whitechronos-control-plane`. Therefore:

- **WhiteChronos Connection Controller** becomes a module + reusable Skill inside `plugins/whitechronos-control-plane`.
- **TinyFish Controller** becomes a separate thin local controller plugin because TinyFish has provider-specific routing, safety, cost and Browser Profile semantics.
- The actual TinyFish ChatGPT app remains the runtime provider. The local controller does not reimplement TinyFish and does not hold its credentials.

This preserves the user-approved architecture while minimizing duplicated lifecycle ownership.

### 6.2 High-level topology

```text
ChatGPT / Codex task
        |
        v
Official Superpowers
        |
        v
WhiteChronos Connection Controller
        |
        +-- host/plugin inventory
        +-- GitHub adapter
        +-- GitLab adapter
        +-- TinyFish adapter
        +-- generic integration state
        +-- target-access checks
        +-- recovery classification
        |
        +--> TinyFish Controller
        |      +-- search/fetch routing
        |      +-- browser automation policy
        |      +-- Browser Profile policy
        |      +-- monitor/cost policy
        |
        +--> Runtime Doctor
        |      +-- Codex/native/Broker/Arena runtime evidence
        |
        +--> GitHub / GitLab native connectors
        |
        v
Task execution
        |
        v
GitHub Arena review
```

## 7. Connection state model

### 7.1 Evidence dimensions

A connection is not represented by one boolean. Each integration observation SHALL expose at least:

```json
{
  "integration_id": "github",
  "configured": true,
  "host_visible": true,
  "authenticated": true,
  "target_accessible": true,
  "live_verified": true,
  "status": "PASS",
  "observed_at": "timestamp",
  "evidence": []
}
```

The dimensions mean:

- `configured`: repository/project configuration declares the integration;
- `host_visible`: the current harness actually exposes the relevant tool/plugin surface;
- `authenticated`: a safe provider identity probe succeeds;
- `target_accessible`: the required repository/project/resource is accessible;
- `live_verified`: the current task-specific capability has been demonstrated with non-destructive evidence.

### 7.2 Status vocabulary

Connection checks SHALL use:

```text
PASS
DEGRADED
FAIL
UNAVAILABLE
HOST_RELOAD_REQUIRED
USER_ACTION_REQUIRED
HOST_POLICY_BLOCKED
SECURITY_REVIEW_REQUIRED
NOT_APPLICABLE
```

`DEGRADED` is required for cases where the service is authenticated but one optional capability is broken. Example: TinyFish API PASS + Browser Profile API error.

### 7.3 Evidence freshness

Every observation records:

- provider;
- operation/probe used;
- target identifier when relevant;
- timestamp;
- repository commit when relevant;
- non-secret result summary.

No credential material is persisted.

A previous PASS may be reused only when the target and relevant commit are unchanged and the implementation's freshness policy allows it. Sensitive or mutating actions SHALL re-probe the required connection immediately before action.

## 8. Core provider contracts

### 8.1 GitHub adapter

Safe preflight sequence:

```text
tool visibility
-> authenticated profile/user probe
-> installation/account visibility
-> target repository metadata read
-> required permission check for planned action
```

For `WhiteChronos/ChatGPT`, a repository read is the minimum target-access proof.

A write operation must separately verify that the current connector exposes the required write action and that repository permission is sufficient. Historical permission evidence is not sufficient for an irreversible mutation.

### 8.2 GitLab adapter

Safe preflight sequence:

```text
tool visibility
-> current-user probe
-> target project metadata read
-> project/group permission snapshot
-> task-specific CI/MR/project read as required
```

The GitLab adapter records GitHub identity-link metadata only as identity evidence. It SHALL NOT treat that identity link as proof of mirror parity.

### 8.3 GitHub/GitLab mirror parity

Mirror parity is a separate integration property:

```text
GITHUB_AUTH
GITLAB_AUTH
GITHUB_TARGET_ACCESS
GITLAB_TARGET_ACCESS
MIRROR_PARITY
```

`MIRROR_PARITY=HEALTHY` requires the existing control-plane parity logic/evidence showing provider identities and exact commit SHAs match.

The connection controller may surface the newest eligible parity receipt, but it SHALL NOT replace the canonical parity implementation.

### 8.4 TinyFish adapter

TinyFish SHALL be observed at separate layers:

```text
TINYFISH_PLUGIN_INSTALLED
TINYFISH_HOST_VISIBLE
TINYFISH_SERVICE_AUTH
TINYFISH_SEARCH_HEALTH
TINYFISH_FETCH_HEALTH
TINYFISH_PROFILE_API_HEALTH
TINYFISH_PROFILE_GITHUB_AUTH
TINYFISH_PROFILE_GITLAB_AUTH
TINYFISH_BROWSER_READY
TINYFISH_MONITOR_READY
```

Routine preflight MAY use a read-only account/service probe such as wallet state to establish service authentication.

Routine preflight SHALL NOT start browser automation, create a profile, run a monitor or consume paid Agent/Browser steps merely to establish health.

If `list_profiles` errors while service authentication succeeds:

```text
TINYFISH_SERVICE_AUTH=PASS
TINYFISH_PROFILE_API_HEALTH=DEGRADED
TINYFISH_BROWSER_READY=UNVERIFIED
```

The whole TinyFish service must not be marked FAIL.

If profile creation is blocked by the host's safety policy:

```text
TINYFISH_PROFILE_CREATE=HOST_POLICY_BLOCKED
```

That state is not a repository bug and SHALL NOT trigger source-code changes intended to bypass the platform.

## 9. TinyFish Controller

### 9.1 Purpose

The TinyFish Controller provides reusable routing and safety behavior around the official TinyFish app.

It SHALL:

- detect whether TinyFish tools are visible in the current host;
- prefer `search` and `fetch_content` for public information retrieval when TinyFish is the selected provider;
- use `run_web_automation` only for a concrete user-directed browser interaction;
- preserve TinyFish's required polling semantics for browser runs;
- use Browser Profiles only when authenticated browser state is required;
- never request passwords in chat;
- distinguish profile API failure from provider authentication failure;
- expose monitor operations only when the user explicitly asks for monitoring;
- surface wallet/cost state when a paid action is about to be used or the user asks;
- avoid automatic paid health checks;
- never make TinyFish the credential broker for GitHub or GitLab native connectors.

### 9.2 GitHub/GitLab relationship

The preferred routing is:

```text
repository API/read/write
-> native GitHub or GitLab connector

website-only workflow requiring interactive UI
-> TinyFish browser automation, only when explicitly requested

authenticated website workflow
-> TinyFish Browser Profile, only if the profile API is healthy and the user completes provider login
```

TinyFish Browser Profile authentication for GitHub/GitLab is therefore **optional secondary capability**, not a prerequisite for native connector use.

## 10. Conversation bootstrap

### 10.1 WhiteChronos task bootstrap

For WhiteChronos software/repository work:

```text
repository/system/user constraints
-> official using-superpowers
-> WhiteChronos Connection Controller preflight
-> applicable Superpowers process skill
-> Runtime Doctor when host/runtime claims matter
-> specialized controller/provider
-> GitHub/GitLab evidence/mutation
-> GitHub Arena final review
```

### 10.2 Core preflight set

The core set for this repository is:

- Superpowers availability/configuration;
- GitHub connector visibility/auth/target access;
- GitLab connector visibility/auth/target access when GitLab evidence is required;
- GitHub/GitLab parity evidence when mirror state matters;
- TinyFish plugin/service state when web/browser capability is required;
- Arena availability/configuration;
- Runtime Doctor only when current Codex/Arena/Broker/native multi-agent runtime capability is being claimed.

Not every tool must be called on every simple question. The controller chooses the minimum fresh evidence required by the task.

### 10.3 Product-surface boundary

Repository instructions can govern Codex tasks that load this repository and can package/install supported WhiteChronos Skills.

They cannot force arbitrary unrelated ChatGPT conversations to expose every plugin or keep every OAuth token permanently valid.

Therefore the durable guarantee is:

> On a WhiteChronos task where the Connection Controller is loaded, required integrations are checked and their real state is reported before they are relied upon.

## 11. Registry and repository structure

### 11.1 Integration registry evolution

The existing `registry/integrations/schema.json` SHOULD evolve compatibly to describe non-MCP provider connection contracts.

A new optional connection block is preferred over a parallel duplicate registry.

Conceptually:

```json
{
  "connection": {
    "surfaces": ["chatgpt_plugin", "connector", "codex_plugin"],
    "auth_required": true,
    "safe_probe": "provider-specific",
    "target_probe": "provider-specific",
    "paid_probe_forbidden": true,
    "credential_storage": "provider_managed"
  }
}
```

The implementation plan must choose a schema-version migration that preserves validation of existing v1 descriptors.

### 11.2 Proposed files

The implementation is expected to create or modify the following surfaces:

```text
plugins/whitechronos-control-plane/
  runtime/
    connections.py
    connection_models.py
  scripts/
    connection_preflight.py
  skills/
    whitechronos-connection-controller/
      SKILL.md
      agents/openai.yaml
      references/
  tests/
    test_connections.py
    test_connection_preflight.py

plugins/tinyfish-controller/
  .codex-plugin/plugin.json
  README.md
  skills/
    tinyfish-controller/
      SKILL.md
      agents/openai.yaml
      references/
  tests/
    test_repository_integration.py
    test_policy.py

registry/integrations/
  tinyfish.json
  schema.json
  index.json

.codex/config.toml
.agents/plugins/marketplace.json
AGENTS.md

docs/runbooks/
  whitechronos-connections.md

.github/workflows/
  whitechronos-runtime-foundation.yml
  tinyfish-controller.yml
```

The exact file split may be simplified during planning if tests show fewer modules are sufficient.

## 12. Generic plugin/app support

The Connection Controller SHALL be extensible beyond the three initial providers.

For every integration, it should answer:

1. Is the integration declared/configured?
2. Is its tool/plugin surface visible now?
3. Is provider authentication valid?
4. Can it access the target required by this task?
5. Is the specific capability needed by this task live?
6. Is the failure a code defect, user-auth action, host reload issue, provider outage, policy block or optional degraded capability?

Provider-specific adapters own the actual safe probe. The generic controller owns state normalization and recovery classification.

This design intentionally avoids a universal “ping everything” operation because some plugins are paid, mutating, privacy-sensitive or unavailable outside specific product surfaces.

## 13. Security and privacy

The implementation SHALL:

- redact secrets from logs and evidence;
- never serialize OAuth tokens/cookies/passwords;
- never commit Browser Profile state;
- use provider-managed authentication;
- avoid broad filesystem/network permissions merely to make a check pass;
- fail closed when the required permission or target cannot be proven;
- separate read verification from write authority;
- treat TinyFish browser automation as network mutation when it clicks/submits forms;
- require user-directed intent for browser login flows;
- preserve existing GitHub/GitLab merge/deploy/live-smoke authorization gates;
- avoid persisting personally identifying profile details unless essential to a non-secret identity match.

## 14. Cost controls

TinyFish introduces metered capabilities.

Routine connection preflight SHALL:

- use no-cost/read-only provider checks where available;
- not start TinyFish Agent runs;
- not start TinyFish Browser runs;
- not create/run monitors;
- not top up wallet balance;
- not change auto-reload.

A task that needs a metered operation must use the normal TinyFish tool contract and report an insufficient-credit response without silently substituting an unauthorized weaker workflow.

## 15. Error and recovery matrix

### GitHub connector unavailable

```text
host tool absent
-> UNAVAILABLE or HOST_RELOAD_REQUIRED depending on platform evidence
-> do not claim repository access
```

### GitHub auth expired/revoked

```text
tool visible + identity probe fails
-> USER_ACTION_REQUIRED
-> reconnect GitHub through ChatGPT plugin/connector UI
```

### GitLab connector unavailable/auth failure

Use the same classification. Mirror CI evidence does not substitute for current connector authentication.

### Mirror mismatch

```text
both providers accessible + parity mismatch
-> FAIL
-> stop mirror-sensitive actions
-> use existing mirror diagnosis workflow
```

### TinyFish service works, profiles fail

```text
service auth PASS
profile API error
-> DEGRADED
-> search/fetch may continue
-> browser-profile-dependent workflow stops
```

### TinyFish profile creation blocked by host policy

```text
HOST_POLICY_BLOCKED
-> no bypass attempt
-> no source mutation presented as a fix
-> retry only in a supported surface or after platform policy changes
```

### Runtime Doctor reports HOST_RELOAD_REQUIRED

```text
no code change
-> new supported Codex environment/session
-> re-run with observed host inventory
```

## 16. TDD and verification requirements

Implementation SHALL follow Superpowers TDD.

Minimum RED/GREEN coverage:

1. generic connection-state normalization;
2. configured != host-visible;
3. host-visible != authenticated;
4. authenticated != target-accessible;
5. GitHub safe-probe mapping;
6. GitLab safe-probe mapping;
7. mirror parity remains independent;
8. TinyFish service PASS + profile error -> DEGRADED, not FAIL;
9. host policy block classification;
10. no paid TinyFish operation in preflight;
11. no secrets persisted in evidence;
12. repository marketplace/config preserve all existing plugins;
13. TinyFish controller registration;
14. connection controller Skill registration;
15. Runtime Doctor behavior remains unchanged unless explicitly extended by tests;
16. existing control-plane, Broker, Arena, Awesome, ECC and engineering-governance tests remain green.

Verification SHALL include the repository's existing mandatory governance checks applicable to touched files and the relevant control-plane/controller test suites.

## 17. Rollout and authorization gates

The implementation lifecycle is:

```text
written spec approval
-> implementation plan approval
-> isolated feature branch/worktree
-> RED tests
-> GREEN implementation
-> focused refactor
-> code review
-> Full/Review Arena as required
-> GitHub PR
-> CI
-> GitLab mirror/parity verification where applicable
-> merge gate
```

The following remain independent and are not implied by this design approval:

- merge;
- deploy;
- canary;
- stable;
- live smoke;
- R2/R3;
- production-complete declaration.

## 18. Alternatives considered

### Alternative A — separate Connection Controller plugin + separate TinyFish Controller

**Advantages:** very explicit component ownership.  
**Disadvantages:** duplicates the existing WhiteChronos Control Plane's registry/runtime responsibilities, increases marketplace/config surface and creates two competing runtime authorities.

**Decision:** rejected as a separate top-level plugin. Preserve Connection Controller as a module/Skill inside the existing control plane.

### Alternative B — extend WhiteChronos Control Plane + separate thin TinyFish Controller

**Advantages:** reuses the existing registry, Runtime Doctor concepts and bootstrap model; keeps provider-specific policy isolated; fewest moving parts; easiest to test and extend.

**Decision:** selected.

### Alternative C — use TinyFish as the central browser orchestrator for GitHub and GitLab

**Advantages:** one browser automation surface.

**Disadvantages:** weaker than native API connectors for repository work, unnecessary credential/session duplication, paid browser cost, fragile UI automation, larger security surface and poor separation of mirror/auth state.

**Decision:** rejected.

## 19. Arena outcome

The structured 16-strategy Arena review converged on five material decisions:

1. extend the existing control plane rather than introduce a duplicate orchestration plugin;
2. treat TinyFish Browser Profile state as a sub-capability, not as TinyFish's entire health state;
3. prefer native GitHub/GitLab connectors and keep TinyFish browser use secondary;
4. make “100%” evidence-based and task-scoped rather than promise permanent OAuth connectivity;
5. preserve fail-closed boundaries and classify host/policy failures without source-code workarounds.

No independent agents were executed by the Arena adapter in this ChatGPT session.

## 20. Acceptance criteria

This design is ready for implementation planning when the user approves this written specification.

The eventual implementation is complete for this scope only when fresh evidence can produce a connection report equivalent to:

```text
SUPERPOWERS                    PASS
GITHUB_HOST_VISIBLE            PASS
GITHUB_AUTH                    PASS
GITHUB_TARGET_ACCESS           PASS
GITLAB_HOST_VISIBLE            PASS
GITLAB_AUTH                    PASS
GITLAB_TARGET_ACCESS           PASS
MIRROR_PARITY                  HEALTHY
TINYFISH_PLUGIN                PASS
TINYFISH_SERVICE_AUTH          PASS
TINYFISH_PROFILE_API           PASS | DEGRADED with explicit reason
TINYFISH_BROWSER_READY         PASS | NOT_APPLICABLE | USER_ACTION_REQUIRED
ARENA                          PASS
RUNTIME_DOCTOR                 PASS | NOT_APPLICABLE
REQUIRED_TASK_CONNECTIONS      PASS
```

A degraded optional TinyFish Browser Profile must not block unrelated GitHub/GitLab native connector work.

A required capability that cannot be proven must stop only the action that depends on it and provide the exact recovery classification.

