# WhiteChronos Runtime Independente — Design

**Status:** Approved architecture; implementation pending per-slice plan review  
**Date:** 2026-10-03  
**Repository:** WhiteChronos/ChatGPT  
**Base:** main at ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988

## 1. Purpose

Decouple executable runtime capabilities from the monolithic WhiteChronos/ChatGPT repository so Arena MCP, Subagent Broker MCP, native Codex multi-agent verification, and runtime distribution can evolve, fail, update, and be verified independently.

The architecture creates four independent repositories:

~~~text
WhiteChronos/
├── arena-mcp-runtime
├── subagent-broker-runtime
├── codex-native-runtime-verifier
└── runtime-marketplace
~~~

WhiteChronos/ChatGPT becomes a governed consumer of those runtimes rather than their permanent source implementation.

This design extends the already-merged WhiteChronos Control Plane. It does not replace the Runtime Doctor, Superpowers, GitHub Arena governance, or existing repository history.

## 2. Problem statement

The current repository state proves that code/configuration and host runtime exposure are separate facts.

Arena and Subagent Broker are already implemented, tested, registered, and locally probeable, but a current host session can still expose none of their tool names.

Expected Arena tools:

~~~text
arena_plan
arena_cards
arena_rubric
arena_review_checklist
~~~

Expected Broker tools:

~~~text
subagent_spawn
subagent_status
subagent_wait
subagent_result
subagent_followup
subagent_list
subagent_cancel
subagent_cleanup
~~~

Native multi-agent is a different class of capability. spawn_agent is not an MCP tool owned by WhiteChronos. When Codex Multi-agent is enabled, the OpenAI-hosted orchestration layer supplies hosted collaboration actions.

Therefore the architecture must never solve a missing native spawn_agent by creating a lookalike MCP tool with that name.

## 3. Authoritative platform facts

This design relies on current OpenAI platform behavior:

1. Plugins may contain Skills, MCP servers, or both.
2. Portable plugin packages use root plugin.json and mcp.json.
3. Codex compatibility packages continue to support .codex-plugin/plugin.json and .mcp.json.
4. Portable ingestion may derive compatibility manifests from portable source configuration.
5. Plugin MCP policy is controlled under plugin-scoped MCP configuration.
6. Marketplace sources may be Git-backed and pinned by ref or SHA.
7. codex plugin marketplace upgrade refreshes configured marketplace sources.
8. Existing sessions do not reload plugin tools after plugin/template changes; a new session is required.
9. Multi-agent hosted actions are provided by the Codex/Agents host and must not be reimplemented by the application.
10. Multi-agent activity can be evidenced from runtime/session events such as agent.session.subagent.created.

Primary references:

- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/api/docs/guides/agents-api/tools/plugins
- https://developers.openai.com/api/docs/guides/agents-api/multi-agent
- https://developers.openai.com/api/docs/guides/responses-multi-agent

These are external platform contracts, not WhiteChronos implementation details.

## 4. Goals

The Runtime Independente architecture SHALL:

1. isolate Arena runtime from Broker runtime;
2. isolate native multi-agent verification from both MCP implementations;
3. distribute WhiteChronos runtime plugins through one independent marketplace;
4. preserve existing tool names and behavior contracts during migration;
5. support portable plugin.json / mcp.json packages;
6. preserve compatibility .codex-plugin/plugin.json / .mcp.json manifests while needed;
7. make each repository independently testable and releasable;
8. support Git-backed marketplace updates;
9. provide deterministic health checks before a host session is started;
10. provide a deterministic fresh-session boundary after runtime/package updates;
11. distinguish local/remote MCP health from host discovery;
12. prove native multi-agent through actual hosted runtime evidence;
13. use Subagent Broker only as fallback when native multi-agent is unavailable;
14. keep WhiteChronos/ChatGPT working during migration;
15. avoid a big-bang deletion of current in-repo plugins;
16. preserve Superpowers as development process source of truth;
17. preserve GitHub Arena as review/quality control;
18. preserve historical commits, PRs, CI evidence, and Task 12 smoke criteria;
19. enable future runtime components without modifying all existing repositories;
20. make runtime provenance and compatibility machine-readable.

## 5. Non-goals

The architecture SHALL NOT:

- create a fake MCP implementation named spawn_agent;
- imply that multi_agent=true proves native multi-agent availability;
- promise hot reload of tools into a session whose tool catalog is already fixed;
- copy all runtime code into every consumer repository;
- make Broker remote-first in the initial release;
- silently provision cloud infrastructure;
- silently create credentials;
- silently publish public plugins;
- automatically enable every MCP discovered in a marketplace;
- delete current plugins/github-arena or plugins/subagent-broker before equivalence is proven;
- rerun historical implementation/TDD/PR/CI cycles solely because code is being extracted;
- rewrite completed Broker smoke criteria;
- treat CI as proof of live host discovery;
- call Arena strategy cards independent subagents.

## 6. High-level architecture

~~~text
                         WhiteChronos/runtime-marketplace
                                      |
                +---------------------+----------------------+
                |                     |                      |
                v                     v                      v
      arena-mcp-runtime     subagent-broker-runtime   codex-native-runtime-verifier
                |                     |                      |
                +---------------------+----------------------+
                                      |
                                      v
                         Fresh Codex / ChatGPT runtime
                                      |
                                      v
                          Runtime Doctor / live proof
                                      |
                                      v
                           WhiteChronos/ChatGPT
                           governed consumer
~~~

## 7. Repository A — WhiteChronos/arena-mcp-runtime

### 7.1 Responsibility

Own the implementation and release lifecycle for:

~~~text
arena_plan
arena_cards
arena_rubric
arena_review_checklist
~~~

It SHALL NOT own GitHub mutation, Subagent Broker execution, native Codex spawning, or consumer-specific governance.

### 7.2 Package structure

~~~text
arena-mcp-runtime/
├── plugin.json
├── mcp.json
├── .codex-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   └── github-arena/
├── src/
│   ├── core/
│   ├── transports/
│   │   ├── stdio/
│   │   └── http/
│   └── server/
├── tests/
│   ├── contract/
│   ├── stdio/
│   └── http/
├── scripts/
│   ├── healthcheck
│   ├── verify-tools
│   └── package
├── runtime-contract.json
└── .github/workflows/
~~~

### 7.3 Transport policy

Arena is stateless enough to support two adapters over one core implementation:

~~~text
core Arena logic
├── stdio adapter       local Codex fallback/development
└── streamable HTTP     remote/shared runtime
~~~

Remote HTTP is the preferred long-term distribution surface because it can be shared by supported ChatGPT and Codex surfaces and updated independently from the consumer repository.

Stdio remains supported for local/offline development, regression, and environments where remote MCP is unavailable.

### 7.4 Tool contract

The four existing names remain stable through the first independent-runtime major version.

Any breaking tool-schema change requires a major version and compatibility review.

### 7.5 Health contract

The repository exposes a machine-readable verification result with runtime, version, transport, initialize status, tools/list status, expected tool count, actual tool count, and WhiteChronos runtime contract version.

A health result is not host-discovery evidence.

## 8. Repository B — WhiteChronos/subagent-broker-runtime

### 8.1 Responsibility

Own the fallback independent-agent MCP runtime:

~~~text
subagent_spawn
subagent_status
subagent_wait
subagent_result
subagent_followup
subagent_list
subagent_cancel
subagent_cleanup
~~~

It owns Broker process management, lifecycle evidence, cancellation, isolated Git worktree/snapshot behavior, and Codex CLI backend integration.

### 8.2 Package structure

~~~text
subagent-broker-runtime/
├── plugin.json
├── mcp.json
├── .codex-plugin/
│   └── plugin.json
├── .mcp.json
├── skills/
│   └── subagent-broker/
├── src/
│   ├── broker/
│   ├── codex-cli/
│   ├── git-isolation/
│   └── mcp/
├── tests/
│   ├── contract/
│   ├── lifecycle/
│   ├── cancellation/
│   └── isolation/
├── scripts/
│   ├── healthcheck
│   └── smoke-real-codex
├── runtime-contract.json
└── .github/workflows/
~~~

### 8.3 Transport policy

Initial release:

~~~text
stdio local = REQUIRED
remote HTTP = NOT_INITIAL_SCOPE
~~~

Reason: Broker intentionally manages local Codex processes, repository worktrees, PIDs, local cancellation, and filesystem isolation.

A future remote Broker requires a separate security design for remote workspace ownership, authentication, tenant isolation, credentials, repository cloning, and remote cancellation.

### 8.4 Native-first policy

Broker never shadows native multi-agent.

~~~text
native Codex multi-agent verified
        ↓ yes
use native
        ↓ no
Broker host-discovered and healthy
        ↓ yes
use Broker
        ↓ no
Superpowers inline fallback
~~~

### 8.5 Existing smoke criteria

The independent repository inherits the already-approved real smoke criteria unchanged:

- simultaneous independent children;
- distinct PIDs;
- distinct agent_id values;
- distinct trace paths;
- isolated writer worktree/branch;
- independent reviewer snapshot;
- cancellation reaches CANCELLED;
- no secrets in evidence;
- follow-up same session/worktree when supported;
- truthful CAPABILITY_UNAVAILABLE when follow-up is unsupported.

Extraction does not reset this historical gate.

## 9. Repository C — WhiteChronos/codex-native-runtime-verifier

### 9.1 Responsibility

Verify native Codex multi-agent as a hosted capability.

It does not implement MCP tools that pretend to be native multi-agent.

### 9.2 What it proves

~~~text
CONFIG_REQUESTED
SESSION_CREATED
MULTI_AGENT_ENABLED
HOSTED_ACTIONS_AVAILABLE
SUBAGENT_CREATED
SUBAGENT_EVENT_OBSERVED
SUBAGENT_COMPLETED
LIVE_VERIFIED
~~~

### 9.3 Verification targets

Where the surface/API exposes events, proof includes agent.session.subagent.created plus a real subagent ID and subsequent lifecycle evidence.

Where a host does not expose raw events, the verifier records the strongest observable evidence and classifies unavailable evidence as CAPABILITY_UNAVAILABLE rather than fabricating proof.

### 9.4 Package structure

~~~text
codex-native-runtime-verifier/
├── verifier/
│   ├── capabilities/
│   ├── sessions/
│   ├── events/
│   ├── evidence/
│   └── report/
├── adapters/
│   ├── agents-api/
│   ├── codex-cli/
│   └── host-inventory/
├── tests/
├── scripts/
│   ├── verify-native
│   └── export-evidence
├── schemas/
│   └── runtime-evidence.schema.json
├── runtime-contract.json
└── .github/workflows/
~~~

### 9.5 Credential policy

The verifier does not create credentials.

Agents API verification that requires an API key runs only when the user/environment already authorized it.

No credential value is stored in evidence.

### 9.6 Native tool-name policy

The verifier may recognize hosted action names such as spawn_agent, send_message, followup_task, wait_agent, interrupt_agent, and list_agents.

It never publishes those names as WhiteChronos MCP tools.

## 10. Repository D — WhiteChronos/runtime-marketplace

### 10.1 Responsibility

Be the distribution and compatibility catalog for WhiteChronos runtime components.

It contains no Arena logic, Broker process engine, or native multi-agent implementation.

### 10.2 Target structure

~~~text
runtime-marketplace/
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── channels/
│   ├── stable.json
│   └── preview.json
├── compatibility/
│   └── matrix.json
├── schemas/
├── scripts/
│   ├── bootstrap
│   ├── upgrade
│   ├── doctor
│   ├── verify-lock
│   └── print-new-session-command
├── locks/
│   └── runtime.lock.json
└── .github/workflows/
~~~

### 10.3 Git-backed plugin sources

Marketplace entries may reference independent repositories through supported Git-backed plugin sources.

Stable channel policy:

- releases/tags preferred;
- immutable SHA recorded in runtime.lock.json;
- refresh may discover a newer allowed version;
- activation requires compatibility checks.

Preview may track a branch/ref but never silently promotes to stable.

### 10.4 Marketplace lifecycle

~~~text
codex plugin marketplace add WhiteChronos/runtime-marketplace
        ↓
codex plugin marketplace upgrade
        ↓
resolve plugin sources
        ↓
verify lock/provenance
        ↓
run local health checks
        ↓
write/update project config if authorized
        ↓
SESSION_RESTART_REQUIRED
        ↓
start a NEW session
        ↓
Runtime Doctor
        ↓
runtime proof
~~~

### 10.5 No fake hot reload

Dynamic behavior is:

~~~text
refresh sources + verify + start new session
~~~

It is not:

~~~text
mutate the current host tool catalog in place
~~~

### 10.6 Launcher behavior

For local Codex surfaces, the marketplace may provide a launcher conceptually named whitechronos-runtime start.

Responsibilities:

1. refresh marketplace;
2. validate source locks;
3. validate Arena/Broker package health;
4. inspect project configuration;
5. emit or execute a new Codex session launch;
6. pass expected runtime contract/version information;
7. invoke Runtime Doctor after session creation when supported.

For ChatGPT/desktop surfaces where process launch is unavailable, it prints exact restart/new-chat instructions instead.

## 11. Portable plugin contract

### 11.1 Source-of-truth manifests

Each independent plugin repository uses portable root manifests as the primary source:

~~~text
plugin.json
mcp.json
~~~

Compatibility files are generated/validated artifacts:

~~~text
.codex-plugin/plugin.json
.mcp.json
~~~

Do not maintain two divergent hand-edited definitions.

### 11.2 Packaging pipeline

~~~text
portable source
    ↓
schema validation
    ↓
compatibility generation
    ↓
diff/equivalence check
    ↓
package test
    ↓
release artifact
~~~

A mismatch between portable and compatibility definitions fails CI.

## 12. Cross-repository runtime contract

Every runtime repository publishes runtime-contract.json.

Minimum semantics:

~~~json
{
  "contract_version": "whitechronos-runtime/v1",
  "component": "arena|broker|native-verifier|marketplace",
  "component_version": "0.0.0",
  "plugin_name": null,
  "tool_contract": [],
  "supported_transports": [],
  "required_host_capabilities": [],
  "minimum_codex_version": null,
  "consumer_compatibility": {
    "whitechronos-chatgpt": ">=0"
  }
}
~~~

The exact schema is implementation-plan work, but these semantic fields are mandatory.

## 13. Compatibility matrix

runtime-marketplace/compatibility/matrix.json records tested combinations:

~~~text
Arena version
Broker version
Native verifier version
Runtime Doctor contract version
Codex compatibility range
WhiteChronos/ChatGPT consumer range
status
~~~

Statuses:

~~~text
SUPPORTED
PREVIEW
INCOMPATIBLE
UNVERIFIED
DEPRECATED
~~~

Marketplace bootstrap fails closed on known INCOMPATIBLE combinations.

## 14. WhiteChronos/ChatGPT consumer migration

### 14.1 Target role

After migration, WhiteChronos/ChatGPT owns:

- repository governance;
- Runtime Doctor consumer integration;
- Control Plane policies;
- integration registry/history;
- Superpowers routing;
- ECC/Matt/Awesome routing;
- version pins/locks;
- consumer-level acceptance tests.

It no longer owns canonical Arena or Broker runtime implementation.

### 14.2 Transitional state

During migration:

~~~text
plugins/github-arena
plugins/subagent-broker
~~~

remain as compatibility wrappers/mirrors until equivalence is proven.

No immediate deletion.

### 14.3 Consumer marketplace entry

After the migration gate, the repository-scoped marketplace consumes independent Git-backed runtime sources instead of the local implementations.

Exact source syntax follows the supported marketplace format at implementation time.

## 15. Migration phases

### Phase 0 — Freeze canonical behavior

Record current tool names, schemas, Skill behavior, manifests, smoke criteria, and successful CI evidence.

No extraction yet.

### Phase 1 — Arena extraction

Create arena-mcp-runtime.

Prove:

- tool schema parity;
- stdio parity;
- package parity;
- independent CI;
- no consumer behavior regression.

### Phase 2 — Broker extraction

Create subagent-broker-runtime.

Prove:

- eight-tool parity;
- lifecycle parity;
- Git isolation parity;
- cancellation parity;
- smoke harness parity.

Do not rerun the live smoke merely because files were extracted until the new runtime reaches the post-merge host-verification gate.

### Phase 3 — Native verifier

Create codex-native-runtime-verifier.

Prove native capability without introducing a WhiteChronos spawn_agent tool.

### Phase 4 — Marketplace

Create runtime-marketplace with stable/preview channels and pinned source locks.

### Phase 5 — Shadow consumption

WhiteChronos/ChatGPT validates both existing local runtime and new independent runtime against the same contract fixtures.

Only one is active in a runtime session; shadow means CI/equivalence verification, not duplicate MCP registration in the same host.

### Phase 6 — Switch consumer

Change WhiteChronos/ChatGPT marketplace source to independent runtime repos.

Start a fresh Codex session.

Run Runtime Doctor.

### Phase 7 — Live proof

~~~text
fresh session
→ marketplace/version evidence
→ Arena host discovery
→ Broker host discovery
→ native multi-agent verification
→ routing selection
→ Broker live smoke only if Broker path is selected/required
~~~

### Phase 8 — Compatibility wrappers

Convert old in-repo runtime directories to thin compatibility/readme wrappers or archived mirrors.

Delete old canonical implementation only after one stable release cycle with independent runtimes verified.

## 16. Fresh-session bootstrap contract

A runtime update has these states:

~~~text
SOURCE_UPDATED
PACKAGE_VALIDATED
MARKETPLACE_REFRESHED
CONFIG_READY
SESSION_RESTART_REQUIRED
NEW_SESSION_STARTED
HOST_DISCOVERED
LIVE_VERIFIED
~~~

No transition from MARKETPLACE_REFRESHED directly to HOST_DISCOVERED is allowed for an already-open session.

## 17. Dynamic update strategy

### 17.1 Stable channel

- pinned release/tag;
- immutable SHA lock;
- compatibility matrix PASS;
- CI PASS;
- no silent major upgrades.

### 17.2 Preview channel

- may track branch/ref;
- explicitly selected;
- cannot overwrite stable lock without review.

### 17.3 Remote Arena update

When Arena is deployed as streamable HTTP:

- server implementation can update independently;
- tool changes remain subject to schema compatibility/review;
- package metadata/Skill changes follow normal plugin package update requirements.

### 17.4 Broker update

Local Broker code refreshes from its Git-backed plugin source.

A new Codex session is required before expecting changed tools/package behavior.

## 18. Runtime Doctor evolution

The existing Runtime Doctor becomes a consumer of independent runtime contracts.

New checks:

~~~text
MARKETPLACE_SOURCE
MARKETPLACE_LOCK
ARENA_SOURCE_VERSION
ARENA_TRANSPORT
ARENA_PACKAGE_HEALTH
BROKER_SOURCE_VERSION
BROKER_PACKAGE_HEALTH
NATIVE_VERIFIER_VERSION
SESSION_FRESHNESS
HOST_ARENA_DISCOVERY
HOST_BROKER_DISCOVERY
NATIVE_MULTI_AGENT_EVIDENCE
ROUTING_DECISION
LIVE_SMOKE_READY
~~~

New classifications:

~~~text
SOURCE_DRIFT
PACKAGE_DRIFT
MARKETPLACE_STALE
SESSION_RESTART_REQUIRED
HOST_RELOAD_REQUIRED
NATIVE_CAPABILITY_UNAVAILABLE
CONTRACT_INCOMPATIBLE
LIVE_VERIFIED
~~~

## 19. Runtime routing decision

Routing is deterministic:

~~~text
if native verifier == LIVE_VERIFIED:
    route = NATIVE
elif broker local health == PASS and broker host discovery == PASS:
    route = BROKER
else:
    route = SUPERPOWERS_INLINE
~~~

Arena is orthogonal review capability and does not substitute for either independent-agent route.

## 20. Failure isolation

### Arena unavailable

Broker and native verifier continue operating.

Final review falls back to repository Skill/Micro Arena rules with explicit runtime limitation.

### Broker unavailable

Native multi-agent remains usable when verified.

If native is unavailable too, use Superpowers inline fallback.

### Native unavailable

This is not a Broker defect.

Route to Broker when Broker is healthy and host-discovered.

### Marketplace unavailable

An existing pinned local snapshot may be used when integrity/lock is valid.

No automatic unverified source fallback.

### Remote Arena unavailable

Local stdio Arena may be selected when supported and explicitly configured.

## 21. Security boundaries

### Supply chain

- stable releases pinned by immutable SHA;
- provenance recorded;
- release checksums recorded where practical;
- no arbitrary upstream installers;
- release promotion requires CI/review.

### Credentials

- secrets never committed;
- Broker child processes receive an allowlisted environment;
- native verifier consumes user-authorized credentials only.

### Filesystem

Arena has no broad filesystem mutation authority.

Broker receives only the repository/worktree scope needed for an approved child.

Marketplace never scans arbitrary user directories.

### Tool identity

No independent repository may publish a WhiteChronos MCP tool named spawn_agent, send_message, wait_agent, or another hosted multi-agent action in a way that can be confused with native Codex capability.

## 22. CI contract by repository

### Arena

- portable manifest validation;
- compatibility manifest equivalence;
- exact four-tool contract;
- stdio tests;
- HTTP tests;
- schema regression;
- security tests.

### Broker

- portable manifest validation;
- exact eight-tool contract;
- lifecycle tests;
- cancellation tests;
- process-isolation tests;
- Git worktree/snapshot tests;
- secret-redaction tests;
- fake-Codex tests;
- no live model smoke in ordinary CI.

### Native verifier

- fixture/event parser tests;
- capability classification tests;
- no fake native-success claims;
- credential-redaction tests;
- mocked session state tests.

### Marketplace

- source resolution;
- lock validation;
- compatibility matrix;
- stable/preview separation;
- update/rollback tests;
- restart-required state tests;
- consumer contract tests.

## 23. Live runtime verification

Live verification is post-install/post-merge.

### Arena live proof

Evidence:

- fresh session identity/timestamp;
- expected source/version;
- four Arena tools host-visible;
- successful benign Arena tool invocation where host permits.

### Broker live proof

Evidence:

- fresh session;
- eight Broker tools host-visible;
- Runtime Doctor readiness;
- approved real smoke command;
- existing lifecycle acceptance criteria.

### Native live proof

Evidence:

- Multi-agent enabled;
- actual hosted subagent creation;
- real subagent ID;
- lifecycle/event evidence;
- no WhiteChronos MCP masquerading as native.

## 24. Repository creation policy

Creating the four repositories is implementation work and is not authorized by this design document alone.

Each repository is created only after:

1. this spec is approved;
2. implementation plans are written and approved;
3. repository visibility/licensing/default-branch policy is fixed in the plan;
4. execution method is selected.

## 25. Plan decomposition

This architecture MUST NOT be implemented from one giant plan.

Required plan set:

1. Arena Independent Runtime
2. Broker Independent Runtime
3. Native Runtime Verifier
4. Runtime Marketplace
5. WhiteChronos/ChatGPT Consumer Migration
6. Fresh-session Bootstrap + Dynamic Update
7. Cross-repo Compatibility + Release Governance
8. Post-migration Live Runtime Proof

Each plan gets its own TDD/review/PR/CI/merge lifecycle.

## 26. Recommended implementation order

~~~text
Arena extraction
    ↓
Broker extraction
    ↓
Native verifier
    ↓
Runtime marketplace
    ↓
cross-repo contract tests
    ↓
ChatGPT consumer shadow mode
    ↓
consumer switch
    ↓
fresh session
    ↓
Runtime Doctor
    ↓
live proof
~~~

Reason: Arena is lower-risk/stateless and validates the independent plugin/repository distribution model before the stateful Broker is moved.

## 27. Acceptance criteria

The Runtime Independente architecture is complete only when:

1. all four independent repositories exist;
2. each has independent CI;
3. portable plugin manifests validate where applicable;
4. compatibility manifests match portable source;
5. Arena exact four-tool contract passes independently;
6. Broker exact eight-tool contract passes independently;
7. native verifier never publishes fake native tools;
8. marketplace resolves/pins independent runtime versions;
9. marketplace upgrade is tested;
10. stable/preview channels are distinct;
11. WhiteChronos/ChatGPT consumes independent runtime sources;
12. old local runtime implementations are no longer canonical;
13. Runtime Doctor reads independent runtime versions/contracts;
14. a new session is required and recorded after runtime updates;
15. Arena host discovery is proven in a fresh session;
16. Broker host discovery is proven in a fresh session;
17. native multi-agent is either LIVE_VERIFIED or truthfully CAPABILITY_UNAVAILABLE;
18. routing selects Native → Broker → Inline correctly;
19. Broker live smoke passes on the independent runtime when Broker is the target;
20. no historical TDD/PR/CI work is unnecessarily redone;
21. no secret or sensitive raw trace is committed;
22. each independent runtime can fail without making the others untestable;
23. rollback to the previous pinned runtime set is documented and tested;
24. the consumer repository remains recoverable throughout migration.

## 28. Review Arena conclusions

The architectural review used four sequential Arena perspectives because this session does not expose real independent subagents.

1. Systems thinking / build-then-break / completeness
   - separate blast radius and release lifecycle;
   - avoid replacing one monolith with another.

2. Constraint first / requirements checklist / explicit trade-offs
   - preserve existing tool names;
   - do not fabricate spawn_agent;
   - preserve Superpowers and current smoke criteria.

3. Working backwards / iterative deepening / explicit trade-offs
   - start from desired proof: fresh-session host discovery and real subagent evidence;
   - design distribution and bootstrap backwards from that proof.

4. Evidence first / test first / edge cases first
   - repository config is not runtime proof;
   - marketplace refresh is not session reload;
   - local MCP health is not host discovery;
   - native config is not native runtime proof.

## 29. Migration rollback

At every phase, rollback is version/source selection, not destructive restoration.

Rollback inputs:

- last known-good marketplace lock;
- last known-good runtime tags/SHAs;
- existing in-repo compatibility runtime;
- current consumer config backup.

A failed migration must return WhiteChronos/ChatGPT to its previous pinned runtime set without rewriting Git history.

## 30. OpenAI surface limitations

Different supported surfaces expose different installation/restart controls.

The architecture may automate local Codex CLI/desktop bootstrap where a process/session can be started.

It must not claim that a plugin can forcibly reload an already-running ChatGPT conversation.

Where restart/session creation is user-controlled, bootstrap emits the exact action and resumes verification after the new session starts.

## 31. Relationship to existing Control Plane

The existing WhiteChronos Control Plane remains the policy/control layer.

~~~text
Control Plane
= policy, registry, diagnosis, history, routing

Runtime Marketplace
= distribution, version locks, compatibility

Arena Runtime
= Arena executable capability

Broker Runtime
= fallback subagent executable capability

Native Runtime Verifier
= proof of hosted native capability

WhiteChronos/ChatGPT
= governed consumer
~~~

## 32. Implementation boundary

This document approves architecture only.

It does not authorize:

- creating the four repositories;
- moving runtime code;
- changing consumer marketplace entries;
- deploying remote MCP infrastructure;
- installing marketplace sources globally;
- provisioning hosting;
- starting live native-agent API sessions;
- running the Broker real smoke;
- deleting current plugins;
- merging implementation PRs.

After the user approves this written spec, the next required Superpowers step is writing-plans for the first slice: Arena Independent Runtime.

No implementation begins until that first plan is written, reviewed, and its execution method is selected.
