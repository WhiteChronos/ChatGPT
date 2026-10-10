# WhiteChronos Global Conversation Bootstrap Design

**Status:** APPROVED ARCHITECTURE & GOVERNANCE — BASELINE FREEZE v1.0  
**Date:** 2026-10-05  
**Repository:** WhiteChronos/ChatGPT  
**Working branch:** spec-whitechronos-global-conversation-bootstrap-v1  
**Base branch:** main  
**Base commit:** ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988  
**Related architecture:** docs/superpowers/specs/2026-10-03-whitechronos-control-plane-design.md  
**Repository integration note:** PR #57 remains DRAFT and unmerged unless separately authorized.  
**Approval record:** Sections 1–9 approved as one architectural design on 2026-10-05. On 2026-10-05 the user separately authorized the governance freeze recorded in Section 26, including the execution/authorization separation and closure of WhiteChronos v1.0 as the frozen architecture-and-governance baseline. Tasks 1–12 remain implementation-authorized but runtime-gated.

## 1. Decision summary

WhiteChronos SHALL provide a global governance and capability layer across compatible ChatGPT and Codex conversations using:

**Shared Core + Host-Native Bootstrap + Capability Fabric**

The selected architecture keeps governance semantics common while adapting to the real runtime surface of each host.

The global execution flow is:

~~~text
ChatGPT / Codex
      |
      v
Host-Native Bootstrap
      |
      +-- minimal bootstrap verification
      +-- host capability discovery
      +-- host-native identity context
      +-- trusted version/cache selection
      +-- degraded-state detection
      |
      v
WhiteChronos Shared Core
      |
      +-- Session Snapshot
      +-- Policy / Risk Gate
      +-- Capability Registry
      +-- Capability Resolver
      +-- Authorization Layer
      +-- Runtime Doctor
      +-- Quarantine / Revocation
      +-- Release / Channel Policy
      |
      v
Execution Lease when authority is required
      |
      v
Capability Fabric
      |
      +-- Provider
      +-- Adapter -> Provider
      |
      v
Result + Operational Evidence
      |
      v
Append-only Technical Ledger
~~~

GitHub remains the authoritative source of accepted source-controlled configuration, governance, release identity, and version history. A verified local cache provides bounded continuity when GitHub is temporarily unavailable. The cache never becomes an independent authority.

The governing architectural principle is:

> **Global in governance and available capability; isolated in conversation context; minimal in authority; proportional in evidence.**

The long-term system principle remains:

> **The system may become progressively more intelligent and capable without becoming progressively less controllable.**

## 2. Intent and success criteria

The user intends WhiteChronos to be available across ChatGPT and Codex conversations with the maximum automatic loading and routing each host legitimately permits.

Success means:

- Codex receives a strong user-level bootstrap where supported;
- ChatGPT receives the strongest eligible Skill/Plugin/App routing the product exposes, without falsely claiming guaranteed invocation on every turn;
- global governance state is consistent across sessions;
- conversation state and temporary authority remain isolated per session;
- context is shared only through explicitly authorized sources;
- memory is retrieved selectively and only when relevant;
- providers and adapters remain behind capability contracts;
- low-risk routing and analysis may happen automatically;
- external mutations require the policy-defined level of explicit authorization;
- no permanent WhiteChronos superuser exists;
- permissions are capability-scoped, resource-scoped, temporary, revocable, and auditable;
- availability, health, authorization, execution, and success remain distinct states;
- degraded operation preserves only the capabilities that can still operate safely;
- a compromised provider, adapter, capability, version, or channel can be quarantined without disabling unrelated capabilities;
- a global kill switch exists only as a last-resort containment mechanism;
- new capabilities cannot enter normal auto-routing merely by appearing in GitHub or the Registry;
- promotion uses immutable artifacts and controlled channels;
- production readiness is derived from objective evidence rather than a manual boolean;
- no conversation content is copied into global telemetry or the technical ledger by default.

## 3. Alternatives considered

### 3.1 Fat global bootstrap

Load most of WhiteChronos logic directly into every ChatGPT/Codex conversation.

Advantages:

- fewer runtime lookups;
- simple mental model.

Rejected because it increases context cost, coupling, upgrade blast radius, duplicated host assumptions, and the risk that provider-specific behavior leaks into global instructions.

### 3.2 Thin host bootstrap + Shared Core + Capability Fabric

Each host loads only a minimal bootstrap. The Shared Core owns contracts, policy, risk semantics, routing, authorization semantics, lifecycle, health/evidence semantics, and governance. Providers remain behind capability contracts.

**Selected.**

Advantages:

- host differences are explicit;
- global instructions stay small;
- capability growth does not require a larger bootstrap;
- provider logic remains decoupled;
- failures can be contained by capability/provider boundary;
- ChatGPT and Codex can share governance without pretending to share identical runtime mechanics.

### 3.3 Remote-first central Control Plane service

Make ChatGPT and Codex thin clients of a permanently hosted external WhiteChronos service.

Advantages:

- central synchronization;
- easy global telemetry aggregation.

Deferred as a possible future provider topology, not selected as the initial architecture. It introduces network dependency, service operations, remote authentication, availability engineering, and a new failure domain before the bootstrap contract itself has been proven.

## 4. Constitutional invariants

The following rules are architecture-level invariants.

1. Higher-priority product/system/safety rules always prevail.
2. WhiteChronos global safety and governance guarantees cannot be weakened by local project instructions.
3. Project/repository rules may specialize behavior without reducing minimum governance guarantees.
4. Conversation preferences may change style and flow but not safety or authorization requirements.
5. WhiteChronos defaults apply only where no more specific valid rule exists.
6. Capability availability does not imply execution authority.
7. Configuration does not prove host discovery.
8. Host discovery does not prove provider health.
9. Provider health does not grant authorization.
10. Authorization does not prove execution.
11. Execution does not prove success.
12. Success claims require evidence proportional to the claim.
13. Unknown risk fails closed.
14. Unknown compatibility is not presumed compatible.
15. A capability, provider, adapter, version, or channel under quarantine is ineligible regardless of technical health.
16. The global kill switch overrides stable status, health, and active leases.
17. Conversation operational state is isolated by default.
18. An Execution Lease from one session is invalid in another session.
19. Shared project context flows through an authorized source, not by direct session-to-session copying.
20. Memory availability does not imply automatic retrieval.
21. The global bootstrap does not bulk-ingest all conversations, files, memories, or repositories.
22. Secrets never enter GitHub, the Registry, the trusted cache, or the technical ledger.
23. Capabilities receive credential references, not raw credential values.
24. Adapters may not increase authority: `authority(output) <= authority(input)`.
25. Delegated capability scopes may only remain equal or shrink: `delegated_scope ⊆ original_scope`.
26. Normal runtime/policy/registry snapshots may be pinned for a conversation, but quarantine, revocation, emergency security policy, and kill switch remain live and immediate.
27. GitHub remains the source-controlled authority; the local cache is last-known-trusted continuity, not a parallel control plane.
28. Presence in GitHub does not imply admission into auto-routing.
29. Merge into GitHub does not imply promotion to global `stable`.
30. Promoting a release changes trust/channel state for the same immutable artifact; it does not rebuild a different artifact.
31. A revoked artifact is never an automatic fallback.
32. Telemetry observes; evidence proves; health is derived.
33. Absence of current evidence yields `UNKNOWN`, not `HEALTHY`.
34. Failure should degrade the smallest safe domain.
35. No degraded mode may become a security or governance bypass.
36. Content used transiently to answer a conversation does not become global retained state merely because it was processed.

## 5. Macro architecture and trust boundaries

### 5.1 Logical components

The global design contains:

- **Host-Native Bootstrap** — minimal startup, host discovery, local trusted version selection, and bootstrap health.
- **Host Adapter** — translates a concrete host/surface into the Global Host Contract.
- **Shared Core** — policy, risk semantics, registry access, resolver, authorization semantics, lifecycle, health/evidence semantics, and control-state interpretation.
- **Capability Fabric** — providers and adapters implementing declared capability contracts.
- **Runtime Doctor** — read-only truth source for runtime evidence and current health derivation.
- **Technical Ledger** — append-only operational/control decision history without conversation content by default.
- **Release/Admission Plane** — immutable releases, manifests, provenance, channels, quarantine, rollback, revocation, and kill switch.

### 5.2 Trust boundaries

#### Host -> WhiteChronos

The host supplies only the identity, tools, approvals, storage, context, and runtime capability signals it actually exposes.

WhiteChronos SHALL NOT invent unavailable host identity or tooling.

#### WhiteChronos -> Capability

A capability receives only the minimum action/resource/data scope required by the authorized task.

#### Capability -> external provider

Credentials remain in the host-native secret/app/connector mechanism. WhiteChronos receives references and policy-relevant metadata, not raw secrets.

#### Runtime -> GitHub

GitHub is the source of truth for accepted source-controlled state. The runtime may use a verified last-known-trusted cache during temporary unavailability.

## 6. Host-Native Bootstrap

The bootstrap SHALL remain deliberately small.

It may:

- identify host and surface;
- discover real host capabilities;
- resolve a trusted WhiteChronos release/cache snapshot;
- validate minimal bootstrap integrity;
- establish session identity and snapshot metadata;
- load global governance references;
- expose the Shared Core routing entrypoint;
- report degraded state.

It SHALL NOT:

- contain provider-specific business logic;
- contain duplicated R0-R3 policy logic;
- store secrets;
- bulk-load every Skill/provider;
- ingest all memories or files;
- mutate the Registry;
- silently activate unadmitted capabilities.

The bootstrap answers:

> **Is this session safe enough to make WhiteChronos routing decisions?**

It does not prove every provider is currently usable.

## 7. Conversation startup and auto-routing lifecycle

### 7.1 Initial bootstrap check

At conversation start, perform only minimal checks:

~~~text
bootstrap
 -> Shared Core availability
 -> policy snapshot
 -> Registry snapshot
 -> quarantine/revocation state
 -> trusted cache integrity
 -> host capability discovery
~~~

The bootstrap SHOULD remain silent to the user while healthy.

### 7.2 Session Snapshot

Each conversation receives an isolated logical snapshot containing at minimum:

~~~text
session_id
host_id
surface_id
runtime_version
policy_version
registry_version
release_channel
host_capability_matrix
bootstrap_evidence
~~~

Normal runtime/policy/registry versions stay pinned for session reproducibility.

Security controls remain live.

### 7.3 Request handling

For each task:

~~~text
request
 -> intent analysis
 -> needed capability
 -> risk classification
 -> policy decision
 -> capability resolution
 -> first-use runtime verification when needed
 -> authorization / Execution Lease when needed
 -> provider execution
 -> result + evidence
 -> technical ledger metadata
~~~

The system MAY analyze task content transiently to classify intent and risk. That content SHALL NOT be copied into global telemetry or the technical ledger by default.

### 7.4 Auto-routing

Only routes satisfying all required conditions are eligible:

~~~text
capability lifecycle eligible
AND release/channel allowed
AND integrity valid
AND not quarantined/revoked
AND contract compatible
AND host surface supports the route
AND policy permits the route
AND required health/evidence is sufficient
~~~

A route may be direct:

~~~text
capability -> provider
~~~

or adapted:

~~~text
capability -> adapter -> provider
~~~

An adapted route must never silently expand authority, resource scope, data scope, or side effects.

## 8. Global state, conversation isolation, memory, and cache

### 8.1 Global control state

Global state MAY contain:

- Registry and contract metadata;
- accepted policy versions;
- release/channel pointers;
- provider/capability lifecycle state;
- quarantine and revocation state;
- health/evidence summaries;
- cache trust metadata;
- admission decisions;
- technical audit metadata.

It SHALL NOT contain conversation histories by default.

### 8.2 Per-conversation state

Session state contains:

- snapshot identity;
- host/surface capabilities;
- transient policy decisions;
- leases;
- evidence references;
- task-local routing state.

Direct cross-session reads are forbidden.

### 8.3 Shared project context

Multiple sessions working on the same project share context only through an authorized source such as GitHub, files, a knowledge provider, or another explicitly permitted system.

The architecture is:

~~~text
Conversation A -> authorized project source <- Conversation B
~~~

not:

~~~text
Conversation A -> Conversation B
~~~

### 8.4 Selective memory

Memory is a context source, not an unrestricted global WhiteChronos database.

Retrieval SHOULD be demand-driven:

~~~text
current task
 -> is prior personal/project context materially relevant?
 -> yes: retrieve minimum necessary context
 -> no: do not query memory
~~~

Host-specific memory mechanics are translated by the Host Adapter.

### 8.5 Trusted local cache

The cache is for control/runtime artifacts such as:

- release manifests;
- policies;
- Registry snapshots;
- schemas/contracts;
- bootstrap/runtime metadata;
- verified artifact references.

It SHALL NOT store:

- raw secrets;
- tokens;
- passwords;
- full conversation history.

Each persistent cache object SHOULD include:

~~~text
artifact_id
version
source_commit
digest
channel
fetched_at
verified_at
trust_state
freshness_class
~~~

### 8.6 Freshness policy

Freshness is class-based and policy-controlled.

A stale non-critical schema/document may remain usable longer than a critical security policy.

If a critical policy is too stale to support a high-risk decision, only dependent high-risk operations are blocked; unrelated low-risk work may continue in safe degraded mode.

Concrete freshness thresholds are configuration/policy values and are intentionally not fixed by this architecture.

### 8.7 Atomic cache update

~~~text
fetch candidate
 -> validate manifest/provenance/integrity/contracts
 -> mark trusted
 -> atomic pointer swap
~~~

Failure leaves the previous trusted version active.

## 9. Identity, authorization, and risk

### 9.1 Identity model

WhiteChronos uses:

**host-native identity + capability-scoped delegated authorization + temporary execution permissions**

No permanent global WhiteChronos superuser exists.

The Host Adapter exposes only the identity level actually available, such as:

~~~text
authenticated_user
workspace_member
opaque_session
~~~

The system SHALL NOT fabricate stronger identity.

### 9.2 Risk classes

The baseline operational model is:

| Class | Meaning | Default behavior |
| --- | --- | --- |
| `R0` | local analysis, classification, routing, non-mutating diagnostics | automatic |
| `R1` | external read/search without material state mutation | automatic when policy permits |
| `R2` | reversible or limited-impact external mutation | explicit confirmation |
| `R3` | publish/send/delete/merge/configuration/credential or materially irreversible/high-impact mutation | explicit confirmation plus reinforced controls |

If risk cannot be classified confidently:

~~~text
UNKNOWN -> BLOCKED
~~~

Risk is contextual, not inferred solely from the capability name. Relevant inputs include capability, operation, provider, resource, destination, reversibility, blast radius, data class, credential requirements, and current system state.

For `R2` and `R3`, explicit confirmation SHALL identify the action, target/destination, and material effect clearly enough that the user knows what authority is being granted.

User confirmation and operational permission are separate. A user may approve an action that the host, workspace, credential, or provider still does not permit; execution requires both the policy/user authorization and the host/provider permission to be valid.

### 9.3 Policy precedence

The intended policy hierarchy is:

~~~text
Product/System/Safety rules
        ↓
WhiteChronos global safety/governance minimums
        ↓
Environment / Project / Repository rules
        ↓
Conversation preferences
        ↓
WhiteChronos defaults
~~~

More-specific rules may specialize behavior but cannot reduce minimum safety/governance guarantees.

## 10. Execution Leases

Privileged operations use an ephemeral `Execution Lease`.

A lease SHOULD bind at minimum:

~~~text
lease_id
session_id
principal_ref
capability_id
provider_id
operation
resource_scope
data_scope
risk_class
approval_ref
runtime_version
policy_version
registry_version
issued_at
expires_at
max_uses
integrity_binding
~~~

Rules:

- leases contain no raw secrets;
- mutating leases are single-use by default;
- batch authority is permitted only for an explicitly bounded set;
- leases expire automatically;
- leases do not self-renew;
- a lease from session A is invalid in session B;
- capability/provider/version quarantine or revocation invalidates affected leases immediately;
- a global kill switch invalidates execution regardless of lease state;
- delegated sub-capabilities receive an equal or narrower scope;
- pre-execution validation is mandatory immediately before the provider call.

The minimal lease lifecycle is:

~~~text
REQUESTED
 -> ISSUED
 -> ACTIVE
    +-> CONSUMED
    +-> EXPIRED
    +-> REVOKED
    +-> OUTCOME_UNKNOWN
~~~

The pre-execution gate checks:

~~~text
lease unexpired
capability still eligible
provider still healthy enough
no new quarantine/revocation
policy still permits
resource/data scope still matches
credential reference still usable
host still supports the action
~~~

### 10.1 TOCTOU and uncertain mutation outcomes

If a side-effecting request may have reached the provider but the result is lost, the state becomes:

~~~text
OUTCOME_UNKNOWN
~~~

The system SHALL NOT blindly retry a non-idempotent mutation.

It must first query the authoritative external state when possible.

Idempotency keys or equivalent provider mechanisms SHOULD be used where supported.

## 11. Credential handling

WhiteChronos sees credential requirements and references, never credential values.

Example:

~~~text
credential_ref = github.user.authorized
~~~

rather than a token value.

Host-native secret stores, app connections, credential brokers, or provider-native mechanisms retain the secret.

The Shared Core, GitHub repository, Registry, trusted cache, telemetry, and ledger SHALL not persist raw credentials.

## 12. Capability admission and lifecycle safety

New capabilities/providers/adapters/releases enter through:

**signed manifest + provenance + review + allowlist + validation before `ACTIVE`**

Discovery alone never authorizes auto-routing.

A candidate admission flow is:

~~~text
DISCOVERED
 -> provenance/license/integrity review
 -> contract/dependency/risk validation
 -> CANDIDATE
 -> validation
 -> eligible promotion path
 -> ACTIVE
~~~

A critical admission failure results in quarantine rather than best-effort activation.

Admission SHALL verify, when applicable:

- source identity and immutable source reference;
- artifact digest;
- signed manifest or equivalent authenticated release declaration;
- license;
- dependency identity;
- required contracts;
- requested permissions;
- risk profile;
- test/conformance evidence;
- reviewer/allowlist policy.

The concrete signature technology is intentionally deferred. The architecture requires cryptographic authenticity and integrity, not a specific signing vendor.

## 13. Selective quarantine and global kill switch

Containment is granular by default.

The system can quarantine:

~~~text
provider
adapter
capability
release/version
dependency
channel
~~~

Quarantine is separate from temporary operational unavailability.

A technically responsive but quarantined component remains ineligible.

The global kill switch is a last-resort control used only when selective containment is insufficient.

It overrides:

- `ACTIVE` lifecycle;
- `stable` channel;
- provider health;
- valid leases;
- normal fallback.

Quarantine activation, release, revocation, and global kill-switch events SHALL be recorded in the technical ledger.

## 14. Runtime Doctor, evidence, and health

### 14.1 Runtime Doctor role

Runtime Doctor is the read-only source of operational truth.

A diagnosis does not itself grant authority to change configuration, restart systems, install components, modify providers, or mutate external state.

### 14.2 Evidence levels

The baseline evidence ladder is:

~~~text
CONFIGURED
 -> LOCAL_RUNTIME_HEALTHY
 -> HOST_DISCOVERED
 -> LIVE_VERIFIED
~~~

Interpretation:

- `CONFIGURED`: declared configuration exists.
- `LOCAL_RUNTIME_HEALTHY`: required local structural/runtime checks pass.
- `HOST_DISCOVERED`: the current host/surface proves the capability is actually exposed.
- `LIVE_VERIFIED`: recent real execution evidence proves the capability worked in the target runtime.

A lower level cannot support a stronger claim.

### 14.3 Health states

Health is separate from evidence and includes:

~~~text
UNKNOWN
HEALTHY
DEGRADED
UNAVAILABLE
QUARANTINED
~~~

`UNKNOWN` is not a synonym for `HEALTHY`.

Health is dimensional. The system may report:

~~~text
Shared Core = HEALTHY
GitHub sync = DEGRADED
Provider X = UNAVAILABLE
Provider Y = HEALTHY
Capability Z = HEALTHY via Provider Y
~~~

### 14.4 Hybrid verification

At conversation start, verify only the bootstrap/control-plane minimum.

On the first actual use of a capability, verify the capability-specific route:

~~~text
provider discovered?
credential reference available?
contract compatible?
dependencies healthy?
route usable now?
~~~

This avoids testing all providers in every conversation.

### 14.5 Evidence freshness

Operational evidence records when it was observed and its validity window.

Expired evidence remains historical audit evidence but cannot sustain a present-tense `HEALTHY` or `LIVE_VERIFIED` claim without current validation.

### 14.6 Circuit breaker and safe fallback

Repeated operational failure may open a local circuit breaker.

Circuit state is not quarantine.

A fallback provider is allowed only when it provides the same required capability contract with equal-or-lower risk and authority, is admitted, and is sufficiently healthy.

Fallback SHALL never silently change side-effect semantics.

## 15. Safe degraded mode

Failure does not imply global shutdown when unrelated capabilities remain safe.

The conversation itself SHOULD continue whenever the host remains usable. Material degradation SHALL be disclosed when it affects the requested task, and only capabilities that depend on the unavailable or untrusted component are blocked.

Examples:

~~~text
GitHub unavailable
+ trusted cache valid
-> GitHub sync DEGRADED
-> eligible low-risk work may continue
~~~

~~~text
Provider X unavailable
-> capabilities depending only on X UNAVAILABLE
-> unrelated providers continue
~~~

If a critical security policy is too stale or unverifiable:

- independent `R0/R1` work may continue when policy permits;
- dependent `R2/R3` actions fail closed.

Failure of Runtime Doctor itself yields `UNKNOWN` or `UNAVAILABLE`, never an assumed success.

No degradation state may create new authority.

## 16. Observability and technical ledger

### 16.1 Minimal operational telemetry

Default telemetry is technical and minimal, such as:

~~~text
runtime_version
policy_version
registry_version
capability_id
provider_id
adapter_id
health_state
evidence_level
latency/error class
risk_class
release_channel
rollback/quarantine events
~~~

Conversation content is not collected automatically.

### 16.2 Append-only ledger

The audit model is:

**append-only ledger of technical events and control decisions, no conversation content by default**

Representative records include:

~~~text
version identity
capability/provider route
risk classification
policy decision
authorization/approval reference
lease lifecycle
execution result state
evidence reference
rollback/revocation/quarantine
~~~

### 16.3 Retention and integrity

Retention is class-based.

Critical security, authorization, rollback, revocation, and governance events may be retained longer than routine operational telemetry.

Ledger integrity SHALL be cryptographically detectable, for example through hash chaining or equivalent mechanisms.

Expiration follows explicit retention policy; it is not silent historical editing.

The exact durable storage technology is intentionally deferred.

### 16.4 Content diagnostics exception

Conversation content may be included in a diagnostic artifact only with explicit authorization and a defined retention/scope boundary.

It is never the default.

## 17. Release lifecycle and supply-chain integrity

### 17.1 Separate lifecycle concepts

Capability lifecycle and release channel are distinct.

Capability state may include:

~~~text
CANDIDATE
ACTIVE
QUARANTINED
RETIRED
~~~

Release channel is:

~~~text
candidate
canary
stable
~~~

An `ACTIVE` capability may have a new version still in `candidate`.

### 17.2 Immutable release identity

Each release SHALL bind:

~~~text
release_id
version
source_commit
artifact_digest
manifest_digest
provenance_ref
signature_ref
builder_identity
built_at
~~~

Content changes create a new release identity.

### 17.3 Promotion invariant

The same artifact digest moves across channels.

~~~text
candidate digest = ABC123
canary digest    = ABC123
stable digest    = ABC123
~~~

Promotion SHALL NOT rebuild a different artifact.

### 17.4 Release manifest and provenance

A release manifest SHOULD include:

- version;
- source repository/commit;
- artifact digest;
- Registry/policy compatibility;
- required contracts;
- dependencies;
- build identity;
- provenance;
- licenses;
- timestamp.

Hash/integrity and authenticated publisher identity are separate guarantees and both are required.

### 17.5 Candidate -> canary -> stable

`candidate` passes static, contract, security, dependency, Registry, Runtime Doctor, and regression gates.

`canary` exposes the exact same artifact to a deliberately limited rollout group.

Promotion to `stable` requires objective gates such as:

~~~text
all mandatory checks PASS
no critical regression
no policy violation
health within approved limits
provenance/integrity valid
no blocking quarantine
~~~

Conversation content is not automatically used as promotion material.

Canary cohort selection SHALL be deterministic or explicitly assigned. A conversation/session SHALL NOT randomly switch between `stable` and `canary` mid-work; ordinary channel selection remains pinned for the session, subject to immediate security revocation/quarantine.

The normal rule is that every stable release passes through `candidate` and `canary`. Any emergency break-glass bypass must be separately governed, explicitly authorized, fully audited, and may never bypass artifact integrity, trusted-publisher requirements, or revocation.

### 17.6 Atomic promotion and rollback

Channels SHOULD be represented by trusted pointers to immutable releases.

Pointer changes are atomic.

Rollback restores a previously trusted immutable artifact; it does not create a new build.

Policy-defined critical canary or stable regressions SHOULD be able to trigger automatic rollback to the last trusted stable artifact. Automatic rollback SHALL emit evidence and SHALL be verified after restoration rather than assuming that a pointer change alone succeeded.

At least the current stable and previous trusted stable SHOULD be retained for recovery.

### 17.7 Rollback vs revocation

Rollback means a version is operationally unsuitable and the system returns to a previous trusted version.

Revocation means a version must not execute.

A revoked artifact remains blocked even when its digest and signature are valid.

### 17.8 GitHub relationship

GitHub integration is necessary but not sufficient for global execution.

~~~text
merged in GitHub
 !=
stable global runtime
~~~

The required path is:

~~~text
accepted source change
 -> immutable release
 -> candidate gates
 -> canary
 -> stable
~~~

## 18. Host contracts: Codex and ChatGPT

### 18.1 Shared semantic contract

WhiteChronos normalizes host capabilities through a Global Host Contract including concepts such as:

~~~text
host_id
surface_id
host_version
bootstrap_version
instruction_capabilities
skill_capabilities
plugin_capabilities
tool_capabilities
identity_capabilities
approval_capabilities
context_capabilities
storage_capabilities
background_capabilities
host_health
reload_state
~~~

Feature states may include:

~~~text
SUPPORTED
AVAILABLE_ON_DEMAND
MANUAL_ACTIVATION_REQUIRED
AUTHORIZATION_REQUIRED
UNAVAILABLE
UNKNOWN
~~~

### 18.2 Semantic parity, not technical parity

ChatGPT and Codex share WhiteChronos semantics for:

- risk;
- lifecycle;
- leases;
- quarantine;
- health;
- evidence;
- release channels.

They do not need identical host mechanisms.

### 18.3 Codex bootstrap

Where supported, Codex may use user-level instructions under `$CODEX_HOME` plus globally installed Skills.

The global instruction block SHALL remain small and SHALL:

- route into WhiteChronos;
- preserve higher-priority rules;
- preserve project-local instructions;
- load capabilities on demand;
- avoid declaring host/provider availability without evidence.

A project-local rule may specialize the global bootstrap but may not reduce WhiteChronos minimum security/governance guarantees.

Configuration such as `enabled = true` or `multi_agent = true` is only `CONFIGURED` evidence until host discovery proves the current runtime loaded the feature.

A host reload requirement is operational state, not a reason to mutate source code.

### 18.4 ChatGPT bootstrap

WhiteChronos on ChatGPT means:

> **maximum automatic eligibility/routing allowed by the product and current surface**

It does not mean:

- guaranteed invocation in every turn;
- replacement of the ChatGPT system prompt;
- bypass of product/workspace permissions;
- guaranteed parity across web, desktop, mobile, and Work surfaces.

A Skill/Plugin/App may be installed and eligible yet still require explicit activation, authentication, workspace approval, or a compatible surface.

`MANUAL_ACTIVATION_REQUIRED` is not automatically a health failure; a component may be healthy while still requiring user activation on that surface.

A Skill is also not proof that an executable provider capability exists. Workflow guidance and actual host-exposed execution authority SHALL remain distinct.

The ChatGPT Host Adapter SHALL report those distinctions rather than collapsing them into `AVAILABLE` or `UNAVAILABLE`.

### 18.5 Host Adapter boundary

Host Adapters may:

- discover actual features;
- normalize identity;
- expose approval mechanics;
- translate calls;
- report availability/health limitations.

They SHALL NOT:

- duplicate provider business logic;
- duplicate global risk policy;
- store secrets;
- mutate the Registry independently;
- bypass the Policy Gate;
- invent host capabilities.

## 19. Testing and production readiness

### 19.1 Test layers

The required verification hierarchy is:

~~~text
schema / contract tests
 -> unit tests
 -> invariant/property tests
 -> integration tests
 -> Host Contract tests
 -> security/adversarial tests
 -> failure injection
 -> Runtime Doctor tests
 -> canary
 -> safe live smoke when authorized
~~~

Passing unit tests alone does not imply live readiness.

A live smoke test may run only when Runtime Doctor or an equivalent authoritative probe proves `LIVE_SMOKE_READY = true` (or an equivalent ready state). WhiteChronos SHALL NOT broaden credentials, permissions, or network access merely to force a live-smoke PASS.

### 19.2 Required invariant tests

Tests SHALL cover, where technically applicable:

- adapter authority cannot increase;
- delegated scope cannot expand;
- quarantined/revoked components never resolve;
- unknown risk blocks;
- session A leases cannot execute in session B;
- expired/consumed leases cannot execute;
- target/resource substitution after approval is blocked;
- TOCTOU revocation blocks at pre-execution;
- uncertain non-idempotent mutation produces `OUTCOME_UNKNOWN`;
- cache corruption is rejected;
- partial cache updates do not replace the trusted version;
- stale critical policy blocks dependent high-risk work;
- same digest survives candidate/canary/stable promotion;
- revoked release is never chosen as fallback;
- selective quarantine does not disable unrelated providers;
- global kill switch has absolute precedence;
- Runtime Doctor never promotes `CONFIGURED` to `HOST_DISCOVERED` without evidence;
- expired evidence cannot support current health;
- telemetry/ledger do not contain full conversation content or canary secrets by default.

### 19.3 Host compatibility profiles

Production acceptance uses separate profiles:

~~~text
CORE
CODEX
CHATGPT
~~~

`CORE` contains host-independent guarantees.

`CODEX` adds Codex-specific bootstrap/discovery requirements.

`CHATGPT` adds only requirements that the ChatGPT product surface can legitimately guarantee.

Absence of an unsupported optional capability may be an expected `PASS` when correctly reported as unavailable.

### 19.4 Production-ready is derived

No manually set `production_ready = true` flag is authoritative.

A release is production-ready only when the applicable expression is true:

~~~text
CONTRACTS_PASS
AND TESTS_PASS
AND SECURITY_GATES_PASS
AND SUPPLY_CHAIN_VERIFIED
AND POLICY_VALID
AND REQUIRED_HOST_COMPATIBILITY_PASS
AND ROLLBACK_VERIFIED
AND CANARY_GATES_PASS
AND NO_BLOCKING_QUARANTINE
AND NO_CRITICAL_UNRESOLVED_FINDINGS
~~~

If the claim includes real external operation, required current live evidence must also be present.

A system may be production-ready while an optional provider is unavailable, provided no mandatory capability depends on it.

### 19.5 Flaky tests

A flaky mandatory gate is not silently converted to success by repeated retries.

Instability must be treated as a defect in the test or system and resolved or explicitly blocked.

### 19.6 Regression discipline

A material bug fix SHOULD add a regression test that fails under the old behavior and passes under the fix, unless technical impossibility is explicitly documented.

## 20. First implementation slice

This architecture SHALL be implemented incrementally.

The first implementation is intentionally a **read-only vertical slice**.

Goal:

> Prove that a compatible conversation can detect its host, load a trusted WhiteChronos snapshot, isolate session state, discover real capabilities, apply governance, resolve an R0/R1 route, and report truthful evidence without granting mutation authority.

Initial flow:

~~~text
Conversation
 -> Host Bootstrap
 -> Host Capability Matrix
 -> trusted cache / manifest
 -> Session Snapshot
 -> Policy Gate R0/R1
 -> Capability Resolver
 -> read-only capability
 -> Runtime Doctor evidence
 -> technical ledger metadata
~~~

### 20.1 First-slice scope

The initial implementation SHOULD include:

- Global Host Contract;
- Host Capability Matrix;
- Session Snapshot model;
- baseline health/evidence models;
- minimal release/cache trust model;
- technical ledger event contract;
- lightweight bootstrap;
- trusted-cache validation;
- per-session isolation;
- integration with the existing Capability Resolver;
- R0/R1 classification and policy gate;
- Runtime Doctor extensions required for this slice;
- Codex Host Adapter;
- ChatGPT Host Contract/Adapter boundary;
- privacy tests proving no default conversation-content retention.

### 20.2 Explicitly excluded from the first slice

The first implementation SHALL NOT yet include:

- real R2/R3 external mutations;
- general-purpose mutating Execution Lease enforcement;
- merge/send/delete/publish flows;
- unrestricted background autonomy;
- permanent remote Control Plane service;
- global conversation ingestion;
- automatic scanning of all files;
- a WhiteChronos-owned secret store;
- arbitrary execution of newly discovered providers;
- unrestricted auto-promotion.

This reduces blast radius while validating the global bootstrap foundation.

## 21. Later implementation increments

### Increment 2 — delegated authority

Add:

- full R0-R3 policy enforcement;
- Execution Lease lifecycle;
- pre-execution validation;
- first narrowly scoped, reversible mutating provider operation;
- TOCTOU, idempotency, and outcome-unknown handling.

### Increment 3 — release and supply-chain plane

Add:

- authenticated release manifests;
- provenance;
- immutable release artifacts;
- candidate/canary/stable channel control;
- atomic promotion;
- automatic rollback;
- revocation.

### Increment 4 — operational resilience

Add:

- circuit breakers;
- multi-provider fallback;
- selective quarantine controls;
- global kill switch;
- retention-class implementation;
- cryptographic ledger integrity;
- production readiness profiles and derived reporting.

Each increment receives its own implementation plan, tests, review evidence, and GitHub-controlled integration path.

## 22. Permanent platform limitations

The architecture SHALL NOT promise, unless a host later exposes an explicit supported mechanism:

- forcing WhiteChronos to run on 100% of ChatGPT turns;
- replacing ChatGPT/Codex system-level product instructions;
- bypassing platform safety policy;
- bypassing workspace/app/provider permissions;
- fabricating identity stronger than the host supplies;
- accessing ungranted secrets;
- treating an installed Skill as proof of an executable provider tool;
- treating configured multi-agent state as proof that independent agents are actually available.

These are permanent truthfulness constraints, not missing implementation features.

## 23. Objective acceptance criteria for the first slice

The first slice is complete only when evidence demonstrates:

1. The current host and surface can be identified or truthfully reported as unknown.
2. A trusted WhiteChronos release/cache snapshot can be selected and integrity-checked.
3. A per-conversation Session Snapshot is created without sharing leases or transient state across sessions.
4. Policy and Registry versions are bound to the session snapshot.
5. Live quarantine/revocation/kill-switch state can override a pinned normal snapshot.
6. The Host Capability Matrix reports unavailable/manual/auth-required states without inventing capabilities.
7. An R0/R1 request can be classified and resolved through the existing Capability Resolver.
8. The resolver refuses ineligible/quarantined/incompatible routes.
9. Adapter authority cannot exceed caller authority.
10. Runtime Doctor separates configuration, local health, host discovery, and live evidence.
11. A stale/invalid cache produces the correct degraded/blocked behavior.
12. GitHub temporary unavailability can use a still-valid last-known-trusted cache without creating a second authority.
13. The technical ledger records control metadata without storing conversation content by default.
14. Telemetry contains no raw secret values.
15. A capability unavailable on a host/surface is reported as unavailable or activation-required rather than fabricated as healthy.
16. Codex project rules can specialize but not weaken global minimum governance.
17. ChatGPT behavior is documented and tested against host-exposed semantics rather than a guarantee of per-turn invocation.
18. The system can answer "is WhiteChronos running?" with an evidence-qualified state instead of a generic yes/no.

## 24. Review and process evidence

This architecture was developed through an architectural Superpowers brainstorming flow:

- intent and success criteria;
- explicit requirement decisions;
- three macro approaches and selection;
- section-by-section design approval;
- Sections 1 through 9 explicitly approved by the user.

A GitHub Arena Review pass was also performed with four structured sequential strategy perspectives generated by the Arena adapter:

1. Systems thinking + build-then-break + completeness.
2. Constraint-first + requirements checklist + explicit trade-offs.
3. Working backwards + iterative deepening + explicit trade-offs.
4. Evidence-first + test-first + edge-cases-first.

The current runtime did not expose independent Arena subagents. These were structured sequential review perspectives, not independent-agent execution.

Material review conclusions incorporated into this spec include:

- bootstrap must remain thin;
- host parity is semantic, not technical;
- session snapshots must be reproducible while security controls remain live;
- authority must be temporary and narrower than capability availability;
- provider health and authorization must remain separate;
- last-known-trusted cache continuity must not become a parallel authority;
- quarantine must be selective and distinct from operational failure;
- kill switch must have absolute last-resort precedence;
- promotion must preserve the exact immutable artifact;
- ChatGPT auto-routing must be described as maximum host-permitted eligibility, not guaranteed invocation;
- production readiness must be derived from evidence.

## 25. Intentionally deferred technology choices

This spec fixes architecture and invariants but intentionally does not lock WhiteChronos to a specific implementation technology for:

- release-signature format/provider;
- policy engine;
- durable ledger database;
- cache backend;
- telemetry backend;
- secret manager;
- distributed coordination;
- remote Control Plane transport;
- circuit-breaker library;
- host-side persistence format.

Any future selection must satisfy the contracts and invariants in this document.

## 26. Baseline freeze, governance, and execution boundary

This document is the formal **WhiteChronos Global Conversation Bootstrap Architecture & Governance v1.0** baseline.

The architectural decisions represented by the approved conversational Sections 1–9 remain frozen. The governance rules in this section were separately and explicitly authorized on 2026-10-05. Clarifications may improve terminology, traceability, and evidence, but future architectural redesign or governance changes require a new revision with explicit review and authorization.

### 26.1 Official governance chain

WhiteChronos v1.0 SHALL use the following operational chain:

~~~text
Superpowers executes
 -> Arena challenges
 -> Verification validates
 -> Authorization Gate authorizes
 -> Executor acts
 -> Post-Verification confirms
~~~

The layers have distinct responsibilities:

- **Superpowers** owns the disciplined development/execution workflow, including planning, isolation, TDD, debugging, review, and completion gates.
- **Arena** is an adversarial quality layer. It challenges correctness, completeness, robustness, specificity, edge cases, and constraint adherence. Arena review does not itself create execution authority.
- **Verification** proves whether the relevant technical acceptance conditions are satisfied. A verification PASS is evidence, not operational permission.
- **Authorization Gate** evaluates whether a valid human authorization exists for the exact action, scope, target, artifact/version, environment, and applicable conditions.
- **Executor** performs only the action authorized by that gate and may not broaden scope.
- **Post-Verification** independently checks the resulting state and prevents an attempted action from being equated with successful completion.

### 26.2 Mandatory state-separation invariants

The following distinctions are permanent governance invariants:

~~~text
VERIFIED != AUTHORIZED
AUTHORIZED != EXECUTED
EXECUTED != SUCCESSFUL
~~~

Equivalent human-readable form:

- technical readiness does not grant operational authority;
- operational authority does not prove that an action occurred;
- an attempted or completed action does not prove the intended result.

WhiteChronos SHALL preserve those states separately in policy decisions, runtime evidence, ledger events, release decisions, and user-facing status.

### 26.3 Authority domains remain independent

Authority SHALL be capability- and action-scoped. In particular:

~~~text
merge_authority      != deploy_authority
deploy_authority     != canary_authority
canary_authority     != stable_authority
~~~

Authorization for one domain SHALL NOT be interpreted as authorization for another.

Where conditional authorization is used, the Authorization Gate SHALL re-check the named conditions immediately before execution, including the exact target and immutable identity where applicable. Any scope mismatch, stale evidence, changed target, changed artifact digest/SHA, expired authority, revocation, quarantine, or UNKNOWN state fails closed.

### 26.4 WhiteChronos v1.0 closure state

WhiteChronos v1.0 is **closed as an architecture-and-governance baseline**.

Closure means:

- architecture is frozen at v1.0;
- governance is frozen at v1.0;
- the official execution/quality/authorization chain is fixed by Sections 26.1–26.3;
- deferred implementation work does not reopen the architecture or governance baseline;
- future systems may depend on this baseline without waiting for every WhiteChronos implementation increment to be complete.

Closure does **not** mean that the first implementation slice has already been implemented, merged, deployed, promoted, or live-verified.

The implementation state is explicitly:

~~~text
architecture       = FROZEN
governance         = FROZEN
tasks_1_12         = AUTHORIZED
implementation     = WAITING_FOR_COMPATIBLE_RUNTIME
merge_main         = NOT_AUTHORIZED
deploy             = NOT_AUTHORIZED
promotion          = NOT_AUTHORIZED
live_smoke         = NOT_AUTHORIZED
r2_r3              = NOT_AUTHORIZED
redesign           = NOT_AUTHORIZED
~~~

### 26.5 Tasks 1–12 execution authorization

The user separately authorized implementation of Tasks 1–12 from PR #61 under the Design Freeze v1.0 and the reviewed PR #59 interfaces.

That authorization remains valid and does not require the architecture or plan to be re-approved.

Execution remains gated by the selected **real Subagent-driven** method:

1. prefer native Codex multi-agent tools when the current host actually exposes them;
2. otherwise use the Subagent Broker only when its approved lifecycle tools are actually host-discovered and healthy, with explicit repository binding and isolation evidence;
3. if neither independent-agent runtime is available, stop at the runtime gate rather than representing Arena cards, personas, or inline turns as independent subagents.

Configuration such as `multi_agent=true` or an enabled plugin remains only `CONFIGURED` evidence. Task 1 begins only after compatible independent-agent capability is genuinely `HOST_DISCOVERED`.

The implementation authorization does **not** authorize:

- merge or integration into `main`;
- deploy;
- candidate/canary/stable promotion;
- live smoke;
- R2/R3 execution;
- broad credential creation;
- governance changes beyond this authorized v1.0 freeze;
- architectural redesign.

### 26.6 Subsequent evolution

With this baseline frozen, future WhiteChronos implementation increments and other systems may proceed independently under their own plans and authorization gates.

A later implementation, release, merge, deploy, promotion, or redesign SHALL reference this baseline and obtain only the additional authority required for that specific action. The existence of a future implementation or release plan SHALL NOT silently amend this frozen baseline.
