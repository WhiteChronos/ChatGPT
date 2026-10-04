# WhiteChronos Cloud Control Plane Design

**Status:** Conversational architecture approved; written spec pending user review  
**Date:** 2026-10-04  
**Repository:** `WhiteChronos/ChatGPT`  
**Branch:** `spec/whitechronos-cloud-control-plane`  
**Parent architecture:** `docs/superpowers/specs/2026-10-03-whitechronos-control-plane-design.md` and `docs/superpowers/specs/2026-10-03-runtime-independent-architecture-design.md`

## 1. Decision summary

WhiteChronos adopts a **cloud-first control-plane architecture** with:

1. **Codex Cloud as the primary execution environment** for development tasks, tests, runtime diagnostics, and approved live verification.
2. **GitHub as the persistent source of truth** for source code, architecture, registry, durable project memory, Data Center records, resumable history, CI, and recovery.
3. **WhiteChronos Control Plane as the policy/orchestration layer**, preserving Superpowers, GitHub Arena, Runtime Doctor, ECC, Matt Pocock integrations, Awesome LLM Apps governance, and runtime routing.
4. **Subagent Broker as the independent-agent fallback** when native Codex multi-agent capability is not actually exposed and verified by the current host.
5. **No Desktop Commander dependency and no DigitalOcean dependency** in the target architecture.

The earlier Desktop Bridge proposal is superseded. Desktop access may be reconsidered only as a separately approved future integration; it is not part of this design.

## 2. Purpose

The Cloud Control Plane exists to make WhiteChronos work resumable, auditable, recoverable, and usable without depending on one local machine.

The required outcome is:

```text
Codex Cloud
    |
    +-- executes approved engineering/software work
    +-- runs tests, Runtime Doctor, and live verification
    +-- consumes approved Skills/plugins/MCP configuration
    |
    v
GitHub Persistent Core
    |
    +-- source code
    +-- architecture/specs/plans
    +-- memory/
    +-- datacenter/
    +-- datasheet/
    +-- registry/
    +-- history/
    +-- CI / release evidence
    |
    v
WhiteChronos Control Plane
    |
    +-- Superpowers workflow
    +-- Runtime Doctor
    +-- GitHub Arena
    +-- Subagent Broker routing
    +-- capability / integration registry
    +-- continuity / recovery
```

A fresh Codex Cloud task must be able to reconstruct the current project state from GitHub plus the published cloud-environment configuration without requiring the user's desktop.

## 3. Governing constraints

This design preserves all existing repository governance.

Mandatory routing remains:

```text
repository / system / user constraints
-> official Superpowers process
-> specialized capability when relevant
-> GitHub evidence and mutation
-> GitHub Arena final review
```

Runtime routing remains:

```text
native Codex multi-agent, when actually host-exposed and verified
-> otherwise Subagent Broker, when host-exposed and healthy
-> otherwise official Superpowers inline fallback
```

The following statements are invariants:

- repository configuration is not runtime proof;
- `multi_agent = true` is not native-agent proof;
- plugin or MCP manifests are not host-discovery proof;
- Arena strategy cards are review perspectives, not independent agents;
- CI cannot claim `HOST_DISCOVERED` or `LIVE_VERIFIED` without real runtime evidence;
- secrets, tokens, device codes, credentials, and sensitive runtime traces are never committed;
- already-completed GitHub/TDD/CI work is not repeated merely because a new cloud session has not loaded a capability yet.

## 4. Goals

The architecture SHALL:

1. make Codex Cloud the preferred execution surface;
2. make GitHub the recoverable and durable source of truth;
3. preserve and extend the existing `memory/`, `datacenter/`, `datasheet/`, `registry/`, `plugins/`, `pipeline/`, and `docs/` structures;
4. add an append-oriented `history/` layer for resumable checkpoints and runtime evidence;
5. allow future conversations/tasks to recover exact status without relying on ephemeral chat context;
6. preserve Runtime Doctor's four evidence levels:
   - `CONFIGURED`
   - `LOCAL_RUNTIME_HEALTHY`
   - `HOST_DISCOVERED`
   - `LIVE_VERIFIED`
7. use a published Codex Cloud environment definition that can be reused by new tasks;
8. make setup idempotent and fail closed;
9. keep credentials outside Git and outside durable project memory;
10. preserve independent runtime boundaries for Arena, Broker, native verifier, and future runtime components;
11. record runtime/version/provenance evidence after significant milestones;
12. support disaster recovery by recreating a fresh cloud task from GitHub plus environment configuration;
13. keep GitHub Actions focused on CI, deterministic checks, synchronization, release validation, and scheduled maintenance jobs rather than treating Actions as a permanent interactive runtime;
14. keep every external integration explicitly registered with provenance, permissions, execution class, and activation state.

## 5. Non-goals

The architecture SHALL NOT:

- provide unrestricted access to every user account, device, or private service;
- bypass OAuth, repository permissions, workspace controls, or provider authorization;
- store raw credentials in GitHub;
- make the user's Windows desktop a required runtime;
- use Desktop Commander;
- use DigitalOcean as a required execution layer;
- run GitHub Actions as a fake always-on agent server;
- duplicate or fork official Superpowers behavior;
- publish fake native multi-agent tools;
- treat ChatGPT account memory as the project's authoritative engineering memory;
- commit full private conversation histories;
- commit sensitive `.superpowers/subagents/` traces;
- auto-enable every third-party MCP or plugin;
- auto-run credentialled, paid, destructive, self-modifying, autonomous, or broad-filesystem integrations without explicit authority.

## 6. Architecture

### 6.1 Layer A — Codex Cloud Runtime

Codex Cloud is the primary compute/runtime layer.

The environment SHALL contain or prepare:

- the required WhiteChronos repositories;
- Python and Node dependencies;
- Git tooling;
- Codex-compatible Skills/plugins required by the approved runtime;
- runtime validation commands;
- deterministic setup/bootstrap logic;
- explicitly authorized network access;
- secret references supplied through supported secret/credential mechanisms rather than committed files.

The environment is reusable configuration, not the authoritative project history.

Each task may have its own isolated workspace. Therefore durable state that must survive task replacement belongs in GitHub.

### 6.2 Layer B — GitHub Persistent Core

`WhiteChronos/ChatGPT` remains the governed consumer/control repository.

Durable responsibilities:

```text
memory/      current durable project knowledge
datacenter/  configuration, catalogs, technical source indexes
datasheet/   machine-readable current state and evidence summaries
registry/    integrations, capabilities, versions, provenance, ownership
history/     append-oriented events, runtime proof, resumable checkpoints
docs/        specs, plans, operating documentation
plugins/     project-scoped control/routing integrations
pipeline/    deterministic validators and gates
.github/     CI, synchronization, release and audit workflows
```

Git commits, tags, PRs, and workflow runs remain the authoritative history for source mutations.

### 6.3 Layer C — WhiteChronos Control Plane

The existing Control Plane remains the policy and orchestration layer.

It coordinates:

- official Superpowers workflow;
- Runtime Doctor;
- GitHub Arena;
- integration registry;
- history and resume capsules;
- memory snapshots;
- continuous-improvement/drift audits;
- runtime routing;
- capability activation policy;
- fresh-session/reload semantics.

It does not become a monolithic runtime.

### 6.4 Layer D — Runtime capabilities

Runtime capabilities remain independently verifiable.

Primary capabilities include:

- Arena runtime;
- Subagent Broker runtime;
- native multi-agent verifier;
- runtime marketplace/distribution when implemented;
- future MCP/runtime components registered through the integration lifecycle.

Failure of one capability must not make the others untestable.

### 6.5 Layer E — GitHub CI and recovery

GitHub Actions SHALL provide:

- unit/integration tests;
- schema validation;
- manifest equivalence checks;
- provenance checks;
- drift detection;
- registry/history consistency checks;
- package/build validation;
- synchronization workflows;
- release checks;
- scheduled non-interactive maintenance where appropriate.

Actions SHALL NOT be treated as the interactive long-running Codex host.

## 7. Codex Cloud environment contract

### 7.1 Repository access

The published cloud environment must explicitly include the repositories required by the current implementation slice.

Minimum initial set:

```text
WhiteChronos/ChatGPT
WhiteChronos/subagent-broker-runtime
```

Additional independent runtime repositories are added only when their implementation/migration plans authorize them.

GitHub authentication remains user/workspace-scoped. Access to a Codex environment does not override GitHub repository permissions.

### 7.2 Setup behavior

Environment preparation must be:

- idempotent;
- deterministic;
- bounded in time;
- safe to rerun;
- explicit about failure;
- free of long-lived secret values in logs.

Conceptual setup stages:

```text
verify repo checkout
-> verify supported Python
-> verify supported Node
-> install pinned dependencies
-> validate Skills/plugins/manifests
-> validate runtime contracts
-> run non-live preflight
-> emit environment readiness report
```

No live Broker smoke occurs during generic setup.

### 7.3 Secrets

Secrets SHALL use the strongest supported secret mechanism for the selected Codex Cloud surface.

Rules:

- never commit secret values;
- never store secret values in `memory/`, `datacenter/`, `datasheet/`, `history/`, or runtime evidence;
- use least-privilege credentials;
- restrict network destinations where supported;
- redact credential-bearing environment output;
- record only secret names, scope metadata, and activation status.

### 7.4 Network access

Network access is deny-by-default at the architecture level.

Each integration descriptor must declare:

```text
network_required
allowed_hosts
mutation_capable
credentials_required
paid_infrastructure_possible
```

The runtime may activate only what the current approved task needs.

## 8. Persistent memory and Data Center

### 8.1 Memory model

Project memory is repository-backed and deliberately separated from transient model/chat memory.

`memory/` SHALL contain concise current-state knowledge that future tasks need to resume correctly.

Examples:

- current architecture state;
- approved decisions;
- active integration versions;
- accepted constraints;
- pending verification gates;
- exact next resume point.

Memory files must avoid raw secrets, personal account tokens, private chat transcripts, and unnecessary sensitive data.

### 8.2 History model

Add:

```text
history/
  integrations/
  sessions/
  runtime/
  releases/
  incidents/
  index.json
```

A session resume capsule records:

- objective;
- approved decisions;
- repositories/branches/commits;
- completed work;
- verification evidence;
- blockers;
- exact next step;
- links/paths to relevant specs and plans.

This is a decision-grade summary, not a verbatim conversation archive.

### 8.3 Data Center model

`datacenter/` remains the durable technical/configuration catalog.

It may hold:

- integration catalogs;
- capability definitions;
- compatibility metadata;
- approved environment configuration descriptors;
- source indexes;
- non-secret network policy metadata;
- current deployment/runtime topology descriptors.

Raw source evidence must not be overwritten silently.

### 8.4 Datasheet model

`datasheet/` contains machine-readable current state and validated summaries.

For runtime/control-plane use, records may include:

- component versions;
- runtime contract versions;
- latest verified status;
- environment identity metadata;
- compatibility state;
- last successful CI evidence;
- latest live verification timestamp;
- recovery pointer.

Datasheets must be generated/validated from authoritative sources rather than manually asserting success.

## 9. Integration registry

Every external system, plugin, Skill family, MCP server, runtime, or automation is represented in `registry/`.

Required semantic fields include:

```json
{
  "id": "integration-id",
  "source": "official_plugin|local|upstream_git|external_reference",
  "provenance": {},
  "version": "...",
  "execution_class": "...",
  "network_required": false,
  "credentials_required": false,
  "broad_filesystem_access": false,
  "background_capable": false,
  "self_modifying": false,
  "paid_infrastructure_possible": false,
  "activation_state": "...",
  "runtime_evidence": {}
}
```

Activation states remain separate from file existence.

Recommended state model:

```text
DISCOVERED
PROVENANCE_VERIFIED
REVIEWED
REGISTERED
CONFIGURED
LOCAL_RUNTIME_HEALTHY
HOST_DISCOVERED
LIVE_VERIFIED
BLOCKED
DEPRECATED
```

## 10. Runtime Doctor in Codex Cloud

Runtime Doctor remains the gatekeeper for runtime claims.

The canonical command remains:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
```

The Doctor must distinguish:

```text
CONFIGURED
LOCAL_RUNTIME_HEALTHY
HOST_DISCOVERED
LIVE_VERIFIED
```

If local capability passes but the current host lacks tools:

```text
HOST_RELOAD_REQUIRED
```

The response is a fresh task/session/environment, not a source-code rewrite.

Only if:

```text
LIVE_SMOKE_READY=YES
```

may the approved Broker real smoke run.

## 11. Subagent Broker cloud routing

The exact Broker lifecycle surface remains:

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

Routing order:

```text
if native multi-agent is actually host-exposed and LIVE_VERIFIED:
    use native
elif Broker is host-exposed, healthy, and properly bound:
    use Broker
else:
    use official Superpowers inline fallback
```

The independent Broker requires an explicit valid `SUBAGENT_BROKER_REPO_ROOT`.

No fallback may silently infer the consumer repository from the plugin installation location.

### 11.1 Existing live-smoke acceptance criteria

The live test must preserve the previously approved criteria:

- at least two simultaneous real children;
- distinct PIDs;
- distinct agent IDs;
- distinct event/trace paths;
- isolated writer branch/worktree;
- independent reviewer snapshot;
- follow-up retains session/worktree when supported;
- cancellation reaches `CANCELLED`;
- sensitive data is redacted;
- evidence is recorded without committing secrets/raw sensitive traces.

No criterion is weakened to make the smoke pass.

## 12. Access model

"Access to everything" means **access to all explicitly connected and authorized WhiteChronos resources required by the task**, not unrestricted access to the user's entire digital life.

The Control Plane must always know:

- what resource is connected;
- which identity/authorization is being used;
- what permissions are granted;
- whether the action is read-only or mutating;
- whether the action can incur cost;
- whether the data is safe to persist.

No integration may convert a broad desire for continuity into silent privilege escalation.

## 13. Continuity and resume protocol

At every meaningful milestone:

```text
work completed
-> tests / review evidence
-> Git commit / PR / workflow evidence
-> history event
-> memory snapshot refresh
-> exact next-step capsule
```

A future Codex Cloud task starts with:

```text
load repository instructions
-> load current memory snapshot
-> read latest history resume capsule
-> confirm current Git HEAD / PR state
-> run Runtime Doctor if runtime capability matters
-> continue from exact pending gate
```

This is the primary continuity mechanism.

Chat history may supplement it, but it is not required for project recovery.

## 14. Disaster recovery

If a Codex Cloud task disappears or becomes stale:

1. create a fresh Codex Cloud task from the published environment;
2. check out the current approved branch/commit;
3. read the latest memory/history capsule;
4. validate registry/compatibility state;
5. run non-live tests;
6. run Runtime Doctor;
7. continue from the recorded gate.

No desktop restoration is required.

If the published environment itself is unavailable, GitHub remains sufficient to reconstruct a new environment because source, manifests, setup instructions, registry, memory, Data Center metadata, and recovery pointers are repository-backed.

## 15. GitHub Actions role

GitHub Actions is the persistent automation layer, not the conversational runtime.

Approved uses include:

- CI;
- schema/manifest validation;
- release packaging;
- scheduled drift audits;
- mirror/provenance synchronization;
- compatibility checks;
- history/index consistency;
- pull-request gates.

Unapproved uses include:

- pretending to be a permanently connected interactive Codex session;
- storing durable agent credentials in repository files;
- claiming native/Broker host discovery from CI alone.

## 16. Security boundaries

### 16.1 Secrets

- no secret in Git;
- no device code in history;
- no raw OAuth token in logs;
- no secret in runtime evidence;
- redact command output before persistence.

### 16.2 Supply chain

- verify provenance;
- record immutable upstream SHA when practical;
- validate licenses;
- fail closed on unknown/unsafe executable sources;
- do not execute arbitrary upstream installers automatically.

### 16.3 Filesystem

Cloud tasks operate only within the environment's authorized repository/workspace scope unless an explicitly approved integration provides more.

### 16.4 Network

Network permissions must be explicit, minimal, and integration-scoped.

### 16.5 Runtime evidence

Sensitive local traces remain local/ephemeral unless redacted into a safe evidence record.

## 17. Observability

The Control Plane SHALL expose a concise machine-readable status summary.

Minimum fields:

```json
{
  "cloud_environment": "...",
  "git_repository": "WhiteChronos/ChatGPT",
  "git_ref": "...",
  "git_sha": "...",
  "runtime_doctor": {
    "configured": "...",
    "local_runtime": "...",
    "host_discovered": "...",
    "live_verified": "..."
  },
  "routing": "NATIVE|BROKER|INLINE",
  "memory_snapshot": "...",
  "history_resume_capsule": "...",
  "last_ci": "...",
  "blockers": []
}
```

The summary must never upgrade evidence levels automatically.

## 18. Implementation decomposition

This architecture is too broad for one implementation plan.

Required slices:

1. **Cloud Runtime Foundation**
   - Codex Cloud environment contract;
   - repository set;
   - deterministic setup;
   - non-secret environment configuration;
   - preflight.

2. **GitHub Persistent Memory + Data Center**
   - `history/` model;
   - resume capsules;
   - current memory snapshot rules;
   - runtime evidence record;
   - consistency validators.

3. **Cloud Bootstrap + Registry**
   - startup sequence;
   - registry activation states;
   - capability discovery;
   - fail-closed integration loading.

4. **Runtime Doctor Cloud Handoff**
   - cloud environment metadata;
   - host inventory handoff;
   - fresh-session semantics;
   - report persistence.

5. **Subagent Broker Live Proof**
   - only after Runtime Doctor reports readiness;
   - run the existing smoke unchanged;
   - persist redacted proof;
   - update memory/history status.

6. **CI / Drift / Recovery**
   - registry/history validation;
   - scheduled drift checks;
   - recovery verification;
   - rollback documentation.

Each slice receives its own Superpowers plan, TDD/review/PR/CI/merge cycle.

## 19. Migration from current state

The migration is additive.

Current validated work is preserved.

```text
existing Control Plane
existing Runtime Doctor
existing Subagent Broker independent repo
existing Arena/ECC/Matt/Awesome governance
existing specs/plans/history
        |
        v
add Codex Cloud runtime contract
        |
        v
add persistent history/resume layer
        |
        v
publish/reuse cloud environment
        |
        v
fresh Codex Cloud task
        |
        v
Runtime Doctor
        |
        v
Broker live smoke when ready
```

No completed GitHub implementation is reconstructed merely to support the cloud transition.

## 20. Acceptance criteria

The WhiteChronos Cloud Control Plane architecture is operationally complete when:

1. a reusable Codex Cloud environment can be created for the governed project;
2. the environment can access the authorized WhiteChronos repositories;
3. setup is deterministic and idempotent;
4. no long-lived secret is committed;
5. GitHub contains the authoritative memory/Data Center/history state required for recovery;
6. a fresh task can reconstruct the exact resume point from GitHub;
7. registry state distinguishes registration/configuration/host discovery/live verification;
8. Runtime Doctor runs successfully in the cloud environment;
9. stale-host conditions produce reload/new-session guidance instead of code churn;
10. the Broker is bound to the explicit consumer repository root;
11. the host exposes Broker tools before Broker execution is claimed;
12. the real Broker smoke runs only when `LIVE_SMOKE_READY=YES`;
13. smoke evidence satisfies the existing PID/agent/worktree/reviewer/follow-up/cancellation requirements;
14. native multi-agent is either genuinely verified or truthfully unavailable;
15. routing selects Native -> Broker -> Inline correctly;
16. GitHub Actions validates state without claiming interactive runtime proof;
17. future sessions can continue without depending on Desktop Commander, DigitalOcean, or the user's PC;
18. rollback/recovery to the last known-good Git state is documented and tested.

## 21. Review Arena conclusions

Four sequential Arena perspectives were used because the current ChatGPT host does not expose real independent subagent lifecycle tools.

### Perspective 1 — systems thinking / build-then-break / completeness

Conclusion:

- separate ephemeral execution from durable project state;
- keep Cloud runtime replaceable;
- keep GitHub recoverable;
- avoid creating one giant stateful control-plane service.

### Perspective 2 — constraint-first / requirements checklist / explicit trade-offs

Conclusion:

- remove Desktop Commander and DigitalOcean from required architecture;
- preserve all existing Superpowers/Runtime Doctor/Broker gates;
- define "access to everything" as authorized-resource access, not unrestricted privilege.

### Perspective 3 — working backwards / iterative deepening / explicit trade-offs

Conclusion:

Start from the desired recovery proof:

```text
fresh cloud task
-> exact repository state
-> exact memory/resume state
-> Runtime Doctor
-> verified routing
-> live smoke only when ready
```

Then design persistence and environment setup backward from that proof.

### Perspective 4 — evidence-first / test-first / edge-cases-first

Conclusion:

- environment publication is not runtime proof;
- GitHub config is not host discovery;
- task state is not durable project memory;
- CI is not live-agent proof;
- secret-bearing evidence must be redacted before persistence.

## 22. External platform assumptions

This design relies only on documented platform capabilities that are treated as environment assumptions, not repository facts:

- Codex Cloud executes coding tasks on OpenAI-managed computers using reusable cloud environments;
- cloud environments group repositories, tools, dependencies, and access configuration;
- GitHub repository access remains subject to the connected user's GitHub permissions and environment inclusion;
- cloud tasks use isolated workspaces and published-environment changes apply to new tasks;
- long-lived secrets should use supported secret/vault mechanisms rather than source control.

Reference documentation:

- OpenAI Help Center: `https://help.openai.com/pt-br/articles/20001545-using-codex-cloud`
- OpenAI Help Center: `https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan`
- OpenAI Developers: `https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted`
- OpenAI Developers: `https://developers.openai.com/api/docs/guides/agents-api/tools/vaults`

If the product surface changes, Runtime Doctor and environment setup must adapt without weakening the repository/runtime evidence distinction.

## 23. Superseded desktop decision

The prior proposal included a Desktop Bridge based on Remote Desktop Commander.

That proposal is superseded by this spec.

Target state:

```text
Codex Cloud + GitHub Persistent Core
```

not:

```text
Codex Cloud + GitHub + mandatory desktop bridge
```

A desktop integration may be designed later only as an optional, separately reviewed capability.

## 24. Implementation boundary

This document approves architecture only.

It does not itself authorize:

- changing cloud workspace/admin settings;
- creating or exposing credentials;
- enabling broad network access;
- modifying production runtime routing;
- running a paid/live native-agent API session;
- running the Broker real smoke before Runtime Doctor readiness;
- merging implementation PRs;
- deleting any validated existing runtime component.

After the user approves this written spec, the next mandatory Superpowers step is **writing-plans**, beginning with the first slice:

```text
Cloud Runtime Foundation
```

No product implementation begins before that plan is written, reviewed, and the execution method is selected.
