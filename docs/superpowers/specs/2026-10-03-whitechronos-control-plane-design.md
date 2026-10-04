# WhiteChronos Control Plane Design

**Status:** Approved architecture; implementation pending per-slice plan review  
**Date:** 2026-10-03  
**Repository:** `WhiteChronos/ChatGPT`  
**Base:** `main` at `9603fd2522a5a6e24a1cd4aaf87d508c632dc8ab`

## 1. Purpose

Build a reusable WhiteChronos control plane that makes Codex integrations easier to discover, install, diagnose, review, preserve, and resume across future conversations and future incorporated systems.

The control plane must preserve the already-established development process:

```text
repository / system / user constraints
-> official Superpowers process
-> specialized capability (ECC / Matt Pocock / Awesome LLM Apps / future systems)
-> GitHub evidence and mutation
-> GitHub Arena review
```

It must not replace Superpowers, GitHub Arena, the Subagent Broker, ECC, Matt Pocock skills, Awesome LLM Apps, or the existing engineering-governance layer. It must make those layers easier to load, verify, and extend.

## 2. Problem statement

The repository already contains substantial integration infrastructure:

- official Superpowers routing and mirrored provenance;
- GitHub Arena Skill and MCP server;
- ECC controller and upstream-native plugin integration;
- Matt Pocock controller and managed stable Skills;
- Awesome LLM Apps controller, catalog, mirror, and managed Skills;
- Subagent Broker code, plugin metadata, MCP server, runtime state model, and post-merge smoke harness;
- project-level Codex configuration in `.codex/config.toml`;
- local plugin marketplace metadata in `.agents/plugins/marketplace.json`;
- repository rules in `AGENTS.md`;
- persistent technical memory under `memory/`.

The current operational gap is that repository configuration and runtime exposure can diverge. For example, a plugin can be correctly committed and enabled while the current Codex host has not reloaded its MCP tools. Without a deterministic diagnostic layer, a stale session can be mistaken for broken code and cause unnecessary changes.

A second gap is repeatability. New integrations currently require several manually repeated steps: provenance capture, controller/Skill creation, marketplace registration, Codex enablement, tests, sync policy, history, memory, CI, and runtime verification.

A third gap is continuity. Git history preserves source changes, but future sessions need a compact, structured record of why integrations were added, what was validated, what remains pending, and exactly where to resume.

## 3. Design goals

The control plane SHALL:

1. distinguish repository configuration from current runtime capability;
2. provide a deterministic Codex runtime preflight;
3. make local MCP health independently testable through stdio without depending on host tool injection;
4. create a reusable factory for new WhiteChronos integrations and Skills;
5. automatically generate required project-scoped Skill and plugin metadata for approved integrations;
6. preserve provenance, licensing, risk, ownership, synchronization policy, and installation state;
7. maintain compact append-only technical history linked to Git commits, PRs, workflows, specs, and plans;
8. maintain a concise current-state memory snapshot separate from append-only history;
9. provide a global Codex bootstrap installer that is idempotent and non-destructive;
10. make Superpowers the default development process and Arena the mandatory final quality layer;
11. support native Codex multi-agent first, then Subagent Broker fallback, then truthful Superpowers inline fallback;
12. support future integrations through one standard lifecycle;
13. fail closed for unsafe, credentialled, self-modifying, autonomous, unknown-license, or unverified external integrations;
14. preserve existing repository governance and avoid changing already-validated implementation merely because a runtime session is stale;
15. make resume points explicit so future conversations can continue without rediscovering completed work.

## 4. Non-goals

The control plane SHALL NOT:

- claim that project repository instructions can force behavior in every unrelated ChatGPT conversation or every product surface;
- silently install or execute arbitrary third-party code;
- create API keys, credentials, wallets, cloud accounts, or paid infrastructure merely to activate an integration;
- auto-enable every MCP server found upstream;
- automatically run background/autonomous systems without explicit authority;
- copy full private conversation histories into this public repository;
- store credentials, private customer data, personally identifying data, proprietary drawings, or confidential source documents;
- replace Git as the source of truth for source history;
- replace existing Superpowers, Arena, ECC, Matt, Awesome, or Broker implementations;
- rerun completed TDD/Arena/PR/CI/merge cycles only because a new runtime has not loaded their tools;
- treat Arena strategy cards, prompt personas, or same-context role play as independent subagents;
- call the Subagent Broker verified until the approved real post-merge smoke criteria pass.

## 5. Architectural principles

### 5.1 Repository facts and runtime facts are separate

The control plane must report both:

```text
CONFIGURED
LOCAL_RUNTIME_HEALTHY
HOST_DISCOVERED
LIVE_VERIFIED
```

A repository manifest proving a tool should exist is never evidence that the current host actually exposes it.

### 5.2 One control plane, multiple small modules

Do not create a monolithic super-plugin whose failure breaks all integrations. Split responsibilities into independently testable modules with narrow interfaces.

### 5.3 Skills are control surfaces, not data dumps

Every new control-plane Skill must remain compact and use references/scripts for details. Large catalogs and histories remain outside Skill context and are queried on demand.

### 5.4 Git remains authoritative source history

The new history layer stores decision-grade indexes and resumable context, not duplicate copies of full diffs.

### 5.5 Automatic registration is not automatic execution

Safe reviewed local integrations may be registered automatically. Execution requiring credentials, network mutation, background operation, self-modification, sensitive filesystem access, or paid infrastructure remains gated.

### 5.6 Global behavior is bounded by product surface

The repository can enforce behavior for Codex tasks that load this repository and can install reusable Skills into Codex global configuration where supported. ChatGPT Skills/plugins must be installed in the relevant ChatGPT environment; repository code cannot force every generic ChatGPT conversation to load them.

## 6. High-level architecture

```text
WhiteChronos Control Plane
|
+-- codex-runtime-doctor
|   +-- repository/config checks
|   +-- local MCP stdio probes
|   +-- Codex CLI capability probe
|   +-- host-discovery comparison
|   +-- smoke readiness gate
|
+-- whitechronos-bootstrap
|   +-- using-superpowers first
|   +-- repository instruction loading
|   +-- runtime doctor routing
|   +-- Skill selection/routing
|   +-- final Arena requirement
|
+-- system-integration-factory
|   +-- integration manifest
|   +-- controller/plugin skeleton
|   +-- Skill skeleton
|   +-- provenance + risk metadata
|   +-- marketplace/config registration
|   +-- CI/sync templates
|
+-- system-history
|   +-- integration event history
|   +-- session resume capsules
|   +-- release/runtime evidence index
|   +-- current-state memory generation
|
+-- continuous-improvement
    +-- drift audit
    +-- stale integration detection
    +-- missing Skill/config/runtime checks
    +-- improvement candidates
    +-- Arena review routing
```

## 7. Module A: Codex Runtime Doctor

### 7.1 Purpose

Provide a deterministic diagnosis of the exact gap between repository state and runtime state.

### 7.2 Inputs

- repository root;
- `.codex/config.toml`;
- `.agents/plugins/marketplace.json`;
- plugin `.codex-plugin/plugin.json` manifests;
- plugin `.mcp.json` files;
- installed `node`, `git`, and `codex` executables;
- local MCP server processes;
- observed current-host tool inventory when the harness exposes it;
- optional expected commit SHA.

### 7.3 Required checks

The doctor must check at minimum:

```text
REPOSITORY_ROOT
GIT_HEAD
WORKTREE_STATE
CODEX_CONFIG_PARSE
MARKETPLACE_PARSE
SUPERPOWERS_CONFIG
ARENA_PLUGIN_MANIFEST
ARENA_MCP_CONFIG
ARENA_MCP_LOCAL_INITIALIZE
ARENA_MCP_LOCAL_TOOLS
BROKER_PLUGIN_MANIFEST
BROKER_MCP_CONFIG
BROKER_MCP_LOCAL_INITIALIZE
BROKER_MCP_LOCAL_TOOLS
NODE_VERSION
GIT_VERSION
CODEX_VERSION
CODEX_EXEC
CODEX_EXEC_JSON
CODEX_RESUME
NATIVE_MULTI_AGENT_CONFIG
HOST_ARENA_DISCOVERY
HOST_BROKER_DISCOVERY
HOST_NATIVE_SUBAGENT_DISCOVERY
LIVE_SMOKE_READY
```

### 7.4 Local MCP probe

The doctor must be able to start the configured stdio MCP server locally and perform:

```text
initialize
tools/list
```

for:

- `github_arena`;
- `subagent_broker`.

The local probe must not require the host to have injected those tools already.

Expected Arena tools:

```text
arena_plan
arena_cards
arena_rubric
arena_review_checklist
```

Expected Broker tools:

```text
subagent_spawn
subagent_status
subagent_wait
subagent_result
subagent_followup
subagent_list
subagent_cancel
subagent_cleanup
```

### 7.5 Status model

Each check returns exactly one of:

```text
PASS
FAIL
UNAVAILABLE
NOT_APPLICABLE
HOST_RELOAD_REQUIRED
USER_ACTION_REQUIRED
SECURITY_REVIEW_REQUIRED
```

### 7.6 Readiness rule

`LIVE_SMOKE_READY=YES` requires:

- expected repository commit available;
- broker plugin/config valid;
- broker local MCP probe PASS;
- real Codex CLI probe supports required initial execution;
- a fresh trusted remote/network Codex session;
- current host has actually discovered either native multi-agent tools or Broker MCP tools needed for the selected path;
- no known credential/runtime blocker.

`multi_agent = true` alone is never sufficient.

### 7.7 Recovery matrix

Examples:

```text
CONFIG_MISSING
-> repository bugfix path

MCP_LOCAL_FAILED
-> systematic debugging + TDD bugfix

MCP_LOCAL_PASS + HOST_TOOLS_MISSING
-> no code change
-> HOST_RELOAD_REQUIRED
-> start fresh Codex task/environment

CODEX_CLI_MISSING
-> environment setup action

CODEX_EXEC_JSON_UNAVAILABLE
-> CAPABILITY_UNAVAILABLE / runtime upgrade path

BROKER_READY + HOST_VISIBLE
-> live smoke permitted

SMOKE_FAILED
-> isolate verified defect
-> bugfix branch
-> TDD RED/GREEN
-> review/PR/CI/merge

SMOKE_PASS
-> record runtime evidence
-> mark Task 12 verified
```

## 8. Module B: WhiteChronos Bootstrap

### 8.1 Purpose

Establish the standard entry sequence for Codex tasks in this repository and optionally for a user's global Codex environment.

### 8.2 Repository bootstrap order

For software-development tasks:

```text
repository/system/user constraints
-> official Superpowers using-superpowers
-> WhiteChronos bootstrap
-> relevant process Skill
-> runtime doctor when runtime capability matters
-> specialized Skills/controllers
-> GitHub evidence/mutation
-> Arena final review
```

### 8.3 Global Codex installer

Provide an idempotent installer, conceptually:

```text
scripts/install_whitechronos_codex.py
```

It may install approved WhiteChronos Skills into `$CODEX_HOME/skills/` and maintain a clearly delimited WhiteChronos block in the global `AGENTS.md`.

Requirements:

- dry-run mode;
- never erase unrelated global instructions;
- detect previously installed version;
- atomic writes;
- backup before first mutation;
- idempotent repeated execution;
- uninstall/rollback support for the WhiteChronos-owned block/files;
- maintain explicit WhiteChronos ownership/version metadata for globally installed files;
- coexist with existing global installers such as GitHub Arena without duplicating or stealing ownership of their files;
- prefer the official Superpowers plugin at runtime rather than copying or forking its official Skills;
- no credential copying;
- no automatic MCP credential setup.

### 8.4 ChatGPT surface

For ChatGPT, the project may produce validated `skill.zip` packages for user installation and local plugin manifests where supported.

The system must state truthfully that repository bootstrap cannot force unrelated ChatGPT chats to load project Skills automatically.

## 9. Module C: System Integration Factory

### 9.1 Purpose

Convert the repeated integration pattern into a deterministic factory.

### 9.2 Integration descriptor

Every integrated system gets a manifest under:

```text
registry/integrations/<integration-id>.json
```

Minimum fields:

```json
{
  "id": "integration-id",
  "display_name": "Integration Name",
  "source_type": "local|upstream_git|external_reference|official_plugin",
  "source": "...",
  "upstream_ref": "...",
  "upstream_commit": "...",
  "license_status": "...",
  "execution_class": "...",
  "network_required": false,
  "credentials_required": false,
  "background_capable": false,
  "self_modifying": false,
  "broad_filesystem_access": false,
  "paid_infrastructure_possible": false,
  "controller_plugin": "...",
  "skill_paths": [],
  "mcp_servers": [],
  "sync_workflow": null,
  "ownership_manifest": null,
  "history_root": "...",
  "status": "..."
}
```

Exact schema is implementation-plan work, but the architecture requires typed machine validation.

### 9.3 Factory command

Conceptual interface:

```text
whitechronos new-integration <name>
```

or equivalent script.

The factory generates only approved structures and does not execute arbitrary upstream installers.

Candidate generated structure:

```text
plugins/<name>/
  .codex-plugin/plugin.json
  .mcp.json                  # only when MCP is part of approved design
  README.md
  upstream.lock.json         # when there is upstream provenance
  skills/<name>/
    SKILL.md
    agents/openai.yaml
    references/
  scripts/
  tests/
```

It also prepares, when applicable:

- registry integration manifest;
- `.agents/plugins/marketplace.json` entry;
- `.codex/config.toml` entry;
- managed Skill ownership manifest;
- synchronization workflow template;
- CI workflow;
- history bootstrap record;
- documentation references.

### 9.4 Skill creation policy

Every new integration must be evaluated for whether a reusable Skill is appropriate.

A Skill is REQUIRED when the integration introduces one or more of:

- reusable routing rules;
- non-obvious operational workflow;
- repeatable activation/safety requirements;
- tool/MCP usage conventions;
- persistent domain/process behavior.

A Skill is NOT required for a pure data artifact that has no reusable agent behavior.

Generated Skills must follow the current Skill format:

```text
SKILL.md
agents/openai.yaml
scripts/          optional
references/       optional
assets/           optional
```

Before release, every user-installable Skill must be validated and packaged as `skill.zip`.

### 9.5 Automatic registration and installation policy

The factory may automatically prepare registration/install changes on an isolated branch, but it must never write them directly to `main` or bypass review. Activation follows risk.

Low-risk, reviewed local integrations may be set to `INSTALLED_BY_DEFAULT` so a fresh Codex session can load them after merge.

Installation state is explicit:

```text
SCAFFOLDED
REGISTERED_PROJECT
PACKAGED
GLOBAL_INSTALL_ELIGIBLE
ACTIVATION_GATED
ACTIVE_RUNTIME_VERIFIED
```

A generated Skill is not considered installed merely because its files exist in the repository. Project registration, user-installable packaging, optional global Codex installation, and observed runtime activation are separate facts.

The following require explicit review/authority before execution:

- credentialled;
- background/autonomous;
- self-modifying;
- broad filesystem scanning;
- network mutation;
- paid infrastructure;
- unverified license;
- arbitrary shell/installer execution;
- external-reference-only sources.

## 10. Module D: System History

### 10.1 Purpose

Make future conversations resumable without relying on ephemeral chat context.

### 10.2 Separation of responsibilities

`memory/` remains the current durable technical memory.

New `history/` becomes append-oriented integration/session/release history.

Git remains the authoritative source-code history.

### 10.3 Proposed layout

```text
history/
  integrations/
    <integration-id>/
      events/
      latest.json
  sessions/
    YYYY/
      YYYY-MM-DD-<topic>.md
  runtime/
    YYYY/
      <runtime-evidence>.json
  releases/
    YYYY/
      <release-record>.json
  incidents/
  index.json
```

### 10.4 Integration event model

An event may record:

- integration ID;
- event type;
- timestamp;
- branch;
- commit SHA;
- PR number;
- spec path;
- plan path;
- CI/workflow run IDs;
- Skills added/removed;
- MCP changes;
- runtime state;
- upstream commit;
- superseded event ID;
- next resume point.

No source diff is duplicated; the record points to Git.

### 10.5 Session resume capsule

At meaningful milestones, generate a concise session capsule containing:

- objective;
- approved decisions;
- architecture;
- completed work;
- current commit/PR;
- verification evidence;
- open blockers;
- exact next step;
- paths to spec/plan/history/evidence.

Session capsules are project records, not verbatim chat archives.

### 10.6 Conversation-history import

If the user explicitly provides or exports prior conversation data, the system may transform it into redacted project history.

It must not:

- scrape private ChatGPT account history without an authorized connector/tool;
- commit raw conversations by default;
- preserve credentials or personal/confidential material in the public repository.

The default output from historical chat is a decision-grade summary/capsule.

### 10.7 Memory snapshot

A generated/current integration status file may summarize the latest state of all integrations for quick session startup.

It must be derivable from the append-only history plus current registry and Git state.

## 11. Module E: Continuous Improvement

### 11.1 Purpose

Find integration drift and improvement candidates without silently changing production behavior.

### 11.2 Audit domains

The auditor checks:

- plugin manifests;
- Skill presence/format;
- managed ownership manifests;
- upstream locks;
- registry descriptors;
- `.codex/config.toml`;
- marketplace registration;
- `AGENTS.md` routing;
- MCP local health;
- sync workflows;
- CI coverage;
- history/memory consistency;
- runtime smoke evidence freshness;
- unresolved license/security metadata.

### 11.3 Audit statuses

```text
PASS
DRIFT
STALE
MISSING
INCONSISTENT
UNVERIFIED
CAPABILITY_UNAVAILABLE
SECURITY_REVIEW_REQUIRED
USER_ACTION_REQUIRED
```

### 11.4 Change policy

The auditor may create recommendations or a review branch, but must not merge automatically.

High-impact improvement work still follows Superpowers + Arena + PR/CI gates.

## 12. Standard lifecycle for every future integration

Every future system should follow this lifecycle:

```text
DISCOVER
-> PROVENANCE
-> LICENSE
-> SECURITY / EXECUTION-RISK CLASSIFICATION
-> ARENA DESIGN REVIEW
-> SPEC
-> PLAN
-> SKILL / CONTROLLER DESIGN
-> PLUGIN / MCP DESIGN IF NEEDED
-> TDD RED
-> IMPLEMENT
-> GREEN
-> VERIFICATION
-> ARENA CODE REVIEW
-> PR
-> CI
-> MERGE
-> HISTORY EVENT
-> MEMORY SNAPSHOT
-> INSTALL / REGISTER
-> FRESH RUNTIME
-> RUNTIME DOCTOR
-> LIVE SMOKE IF APPLICABLE
```

A later runtime reload problem must not restart the lifecycle from TDD.

## 13. Superpowers integration

The official Superpowers plugin remains the process source of truth.

The control plane must route as follows:

- new feature/architecture -> `brainstorming`;
- approved architecture -> `writing-plans`;
- implementation -> `subagent-driven-development` only when real independent agents are actually available, otherwise `executing-plans`;
- code changes -> `test-driven-development`;
- failures -> `systematic-debugging`;
- review -> `requesting-code-review` / `receiving-code-review`;
- completion -> `verification-before-completion` then `finishing-a-development-branch`.

No WhiteChronos Skill may silently fork or weaken these official workflows.

## 14. GitHub Arena integration

Arena remains a quality/review system, not a runtime executor.

### 14.1 Default behavior

Micro Arena applies to every task:

- evidence-first;
- constraint-first;
- edge-cases-first;
- built-to-last.

### 14.2 High-impact work

Review Arena applies to:

- architecture;
- repository governance;
- integration factory changes;
- runtime bootstrap;
- plugin/MCP changes;
- security-sensitive configuration;
- CI/CD.

When true isolated subagents are unavailable, Arena perspectives are run sequentially and never reported as independent agents.

## 15. Multi-agent and Subagent Broker policy

Default routing:

```text
native Codex multi-agent
-> Subagent Broker
-> Superpowers inline fallback
```

Availability must be proven from the current runtime tool inventory.

The existing Subagent Broker post-merge Task 12 acceptance criteria remain unchanged. The control plane does not rewrite or weaken them.

The Runtime Doctor's purpose is to determine when the existing smoke may truthfully run.

## 16. Existing integrations remain intact

The architecture must preserve and model, rather than replace:

- `github-arena`;
- official `superpowers@openai-curated`;
- `superpowers-controller`;
- upstream-native ECC plus `ecc-controller`;
- `matt-pocock-controller` and Matt-managed Skills;
- `awesome-llm-apps-controller` and its managed Skills/catalog/mirror;
- `subagent-broker`.

Existing completed TDD, PR, CI, merge, and schema-hardening evidence is historical input and must not be redone as part of this project.

## 17. Proposed repository layout

```text
WhiteChronos/ChatGPT/
  .agents/
    plugins/
      marketplace.json
    skills/
      codex-runtime-doctor/
      whitechronos-bootstrap/
      system-integration-factory/
      system-history/
      continuous-improvement/

  .codex/
    config.toml

  history/
    integrations/
    sessions/
    runtime/
    releases/
    incidents/
    index.json

  memory/
    ...

  registry/
    integrations/
      schema.json
      index.json
      <integration-id>.json

  plugins/
    whitechronos-control-plane/
      .codex-plugin/
        plugin.json
      README.md
      skills/
      scripts/
      tests/

  scripts/
    install_whitechronos_codex.py

  docs/
    superpowers/
      specs/
      plans/
      reports/
```

Implementation may refine filenames while preserving these responsibility boundaries.

## 18. Ownership and collision rules

Generated/managed files must have explicit ownership metadata.

The factory must fail closed when a new integration would overwrite:

- an unmanaged project Skill;
- another integration's managed Skill;
- an unrelated plugin;
- a human-maintained history/memory artifact not declared generated.

No integration may silently steal a Skill name.

## 19. Provenance and licensing

Every external/upstream integration must record:

- source URL;
- upstream ref;
- observed commit/release;
- license status;
- local mirror policy if mirrored;
- synchronization method;
- excluded artifacts;
- execution-risk classification.

Unknown or inconsistent licensing remains visible as an inconsistency and blocks automatic executable promotion when required.

## 20. Security model

The control plane must fail closed.

It must never automatically:

- expose arbitrary shell command parameters through MCP;
- forward all parent environment variables to child processes;
- print secrets;
- write credentials to history;
- execute upstream installers during discovery/sync;
- enable all discovered MCPs;
- deploy cloud infrastructure;
- change plugin permissions globally;
- scan broad filesystem areas without explicit authorization;
- commit runtime traces containing sensitive data.

History, logs, and diagnostics must redact secret-like values and avoid storing raw environment dumps.

## 21. CI and verification model

The project will need a dedicated control-plane workflow, but CI must not impersonate live Codex host verification.

CI may validate:

- schemas;
- manifests;
- Skills;
- registry consistency;
- factory deterministic output;
- ownership collision behavior;
- local MCP `initialize` + `tools/list`;
- Runtime Doctor fixture behavior;
- installer dry-run/idempotency;
- history schema;
- memory snapshot determinism;
- existing repository governance gates.

CI must not mark `HOST_DISCOVERED` or `LIVE_SMOKE_READY` based solely on local tests.

Live host/runtime evidence remains a post-merge runtime step where required.

## 22. Improvement discovery

The continuous-improvement module may discover candidates from:

- current repository drift;
- upstream version drift;
- missing test coverage;
- stale runtime verification;
- missing Skill packaging;
- integration metadata inconsistencies;
- repeated manual steps visible in history.

It should rank improvements using:

1. correctness/risk;
2. user impact;
3. repeated maintenance cost;
4. security/provenance;
5. simplicity.

Arena remains the review layer for selecting high-impact improvements.

## 23. Documentation and historical continuity

Every integrated system should have discoverable links among:

```text
registry descriptor
<-> controller/plugin
<-> Skill(s)
<-> spec
<-> plan
<-> PR/commit
<-> CI evidence
<-> history events
<-> runtime evidence
<-> current memory/status
```

A future conversation should be able to start from `history/index.json` plus the integration registry and identify the latest validated resume point without replaying the original chat.

## 24. Migration strategy

Initial implementation must model existing integrations without rewriting them.

Migration order:

1. create control-plane schemas and read-only inventory;
2. import existing integrations into registry descriptors;
3. create history records that point to existing Git/PR evidence;
4. add Runtime Doctor;
5. add bootstrap;
6. add factory;
7. add continuous-improvement audit;
8. add optional global Codex installer;
9. only then use the factory for future systems.

Existing files remain authoritative during migration until equivalence tests prove the new registry/control-plane view matches them.

## 25. Failure handling

Examples:

### Stale host session

Local MCP PASS + host tools absent:

```text
HOST_RELOAD_REQUIRED
```

No source change.

### Broken MCP

Local MCP probe FAIL:

```text
VERIFIED_DEFECT
```

Use systematic debugging and isolated bugfix lifecycle.

### Registry drift

Plugin exists but registry entry missing:

```text
INCONSISTENT
```

Control-plane integration fix required.

### Unsafe new upstream

Unknown license + executable installer + credential requirement:

```text
SECURITY_REVIEW_REQUIRED
```

No automatic activation.

### Missing runtime capability

Required Codex CLI option unavailable:

```text
CAPABILITY_UNAVAILABLE
```

Do not fabricate equivalent capability.

## 26. Acceptance criteria

Architecture is successfully implemented when:

1. a deterministic Runtime Doctor can distinguish repository config, local MCP health, host discovery, and live verification;
2. Arena and Broker local MCP tools can be probed without relying on host injection;
3. stale-host diagnosis never causes source-code mutation by default;
4. new integration creation produces a validated registry entry and appropriate Skill/plugin/controller scaffolding;
5. Skill name collisions fail closed;
6. approved low-risk local integrations can be registered consistently without manual multi-file drift;
7. higher-risk integrations remain gated;
8. all control-plane Skills validate under the current Skill format;
9. user-installable control-plane Skills can be packaged as `skill.zip`;
10. global Codex installation is idempotent, reversible, and preserves unrelated instructions;
11. history records link to real Git/PR/CI evidence instead of duplicating source history;
12. session resume capsules identify exact completed state and next step;
13. no raw private chat transcript is committed by default;
14. current memory/status can be regenerated from structured sources;
15. existing Superpowers/Arena/ECC/Matt/Awesome/Broker behavior remains intact;
16. CI verifies deterministic local behavior while keeping live-host claims separate;
17. future integration workflows follow the standard lifecycle;
18. Runtime Doctor can gate the existing real Subagent Broker smoke without changing that smoke's acceptance criteria;
19. repository governance checks remain green;
20. final documentation clearly distinguishes what is globally enforceable in Codex from what requires installation/availability in ChatGPT.

## 27. Initial implementation decomposition

This architecture is intentionally broad and contains multiple independently valuable subsystems. It MUST NOT be implemented from one giant plan.

After this umbrella architecture is approved, `writing-plans` must be used to create a **plan set**, with one independently reviewable plan per delivery slice. Each plan links back to this spec, receives its own review, and may be implemented/merged independently.

Recommended delivery order:

1. **Runtime Foundation** — minimal integration registry/schema needed by the Runtime Doctor + Runtime Doctor itself;
2. **Post-merge Runtime Validation** — use the Runtime Doctor to resume the already-approved Subagent Broker Task 12 smoke without rebuilding Broker code;
3. **System History** — structured events, resume capsules, history index, and current-state derivation;
4. **WhiteChronos Bootstrap** — repository startup routing and runtime/history-aware resume behavior;
5. **Integration Factory** — integration descriptor generation, Skill/controller/plugin scaffolding, ownership manifests, and registration branch generation;
6. **Continuous Improvement** — drift/staleness/risk audit and Arena-routed recommendations;
7. **Global Codex Installer** — idempotent, reversible installation of WhiteChronos-owned global Skills/instructions;
8. **Existing Integration Migration** — model Arena, Superpowers controller, ECC, Matt, Awesome, and Broker in the registry/history without rewriting their implementations;
9. **Factory Adoption** — use the factory as the mandatory template for future incorporated systems.

The Runtime Foundation is intentionally first so the current Broker smoke can be unblocked as early as possible.

Each slice must be independently testable and reviewable. A later slice may depend on stable interfaces from an earlier slice, but approval of this umbrella spec does not implicitly approve implementation of every slice in one branch.

## 28. Review Arena conclusions incorporated

The architectural review used sequential Arena perspectives because this session does not expose independent subagents.

Material conclusions incorporated:

- prefer decomposition over a monolithic control-plane plugin;
- make runtime diagnosis local/protocol-based so host discovery failures are distinguishable from broken MCP code;
- keep automatic registration separate from automatic execution;
- preserve Git as the authoritative source history and store only decision-grade history indexes/capsules;
- make privacy/redaction a first-class constraint for conversation-derived history;
- model existing systems before migrating or rewriting them;
- keep global Codex installation reversible and bounded;
- preserve official Superpowers process ownership;
- preserve Arena as review rather than runtime;
- fail closed on ownership collisions, unknown provenance, unsafe execution classes, or missing runtime capabilities.

## 29. Implementation boundary

This document approves **architecture only**.

It does not authorize implementation, dependency installation, global Codex mutation, MCP activation, external service setup, cloud provisioning, live smoke execution, PR merge, or migration by itself.

After the user reviews and approves this committed umbrella spec, the next required Superpowers step is `writing-plans` for the first delivery slice: **Runtime Foundation**.

Subsequent modules receive their own linked implementation plans rather than being collapsed into one oversized plan.

Implementation of a slice begins only after:

1. this committed umbrella spec is approved;
2. that slice's implementation plan is written and reviewed;
3. the execution method for that slice is selected.

