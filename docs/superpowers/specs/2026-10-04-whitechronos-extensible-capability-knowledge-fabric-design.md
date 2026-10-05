# WhiteChronos Extensible Capability + Knowledge Fabric Design

**Status:** Conversational architecture approved; written spec pending user review  
**Date:** 2026-10-04  
**Repository:** WhiteChronos/ChatGPT  
**Working branch:** feat/cloud-runtime-foundation  
**Draft PR:** #57  
**Parent hardening architecture:** docs/superpowers/specs/2026-10-04-github-control-plane-hardening-redundancy-design.md

## 1. Decision summary

WhiteChronos SHALL evolve into a hybrid, contract-driven capability fabric rather than a progressively larger monolithic application.

The selected architecture has four logical planes:

1. **Kernel / Control Plane integration** — stable contracts, discovery, policy, authorization, lifecycle rules, context routing, truth resolution, runtime evidence semantics, and governance boundaries.
2. **Capability Plane** — Skills, agents, MCP servers, plugins, models, workflows, adapters, knowledge providers, local modules, and external repositories exposed only through versioned capability contracts.
3. **Knowledge Plane** — a federated Knowledge Fabric backed by an append-only Knowledge Ledger, reconstructible materialized views, provenance, evidence, conflict-aware truth resolution, and context assembly on demand.
4. **Evolution Plane** — an append-only Evolution Ledger, permanent Capability Roadmap, gap detection, candidate research, Arena review, controlled capability creation, quarantine, canary, promotion, rollback, and continuous revalidation.

GitHub remains the single authoritative Control Plane for accepted source-controlled state, governance, promotion evidence, protected changes, and release history. This design SHALL NOT create a parallel authority.

The architectural objective is **extensible understanding without a fixed architectural ceiling**: future domains and capabilities should be addable without rewriting the Kernel, while physical compute, storage, latency, and context-window limits remain explicit operational constraints.

## 2. Intent and success criteria

The system is intended to become progressively more capable while becoming no less governable.

Success means that:

- adding a new capability normally requires a new manifest/provider/contract registration, not a Kernel code change;
- small capabilities may live inside WhiteChronos/ChatGPT while larger systems may live in independent repositories;
- local and external providers participate through the same contract, policy, test, lifecycle, and evidence interfaces;
- no capability directly depends on another capability's private implementation, database, memory, filesystem, or secret store;
- knowledge history can explain what was believed, why, from where, when, and under which version and policy;
- current knowledge, lifecycle, and operational state can be rebuilt from append-only authoritative records;
- conflicting knowledge remains visible instead of being silently overwritten;
- low-risk capabilities may promote automatically only after objective gates;
- high-risk capabilities and protected architectural surfaces require human approval;
- WhiteChronos may propose and prepare improvements to itself but may not ratify changes that expand its own authority or weaken its governing gates;
- the system can contain provider failures, recover from them, and preserve provenance;
- every promotion decision is reproducible from exact artifact identity plus evidence;
- the GitHub-first hardening architecture remains authoritative and is strengthened rather than bypassed.

## 3. Alternatives considered

### 3.1 Central extensible monolith

Most capabilities would live in the primary repository and be integrated through direct modules/plugins.

Advantages:

- lower short-term operational complexity;
- simple local debugging;
- fewer repositories.

Rejected as the primary architecture because long-term coupling grows with every integration. Direct imports, shared state, and ever-growing global instructions would eventually make the next capability harder to add than the previous one.

### 3.2 Fully distributed service federation

Every capability would live in an independent repository/service with network-only interaction.

Advantages:

- strong physical isolation;
- independent deployment lifecycles.

Rejected as the default because it creates premature operational burden, network complexity, deployment overhead, and provider management for small capabilities that do not need independent infrastructure.

### 3.3 Hybrid Capability Fabric

Small capabilities may remain local; larger systems may live independently. Both expose the same Capability Contracts and pass through the same Registry, Resolver, policy, lifecycle, evidence, and verification rules.

**Selected.**

This provides local simplicity where useful without allowing physical colocation to become logical coupling.

## 4. Constitutional invariants

The following rules are architecture-level invariants:

1. GitHub is the authoritative Control Plane for accepted source-controlled state.
2. A capability is consumed through a contract, not through another provider's private implementation.
3. Direct system-to-system dependency is forbidden by default.
4. Every new capability begins isolated and untrusted.
5. Discovery does not imply installation, validation, activation, or trust.
6. Unknown risk fails closed.
7. Capability contracts are semantically versioned and immutable.
8. Incompatible behavior requires a new major contract version.
9. Multiple contract versions may coexist.
10. Adapters are explicit, versioned, testable, and observable.
11. Published knowledge is append-only; corrections create new records.
12. Materialized views are derived and reconstructible.
13. Conflicting claims are preserved and never silently collapsed.
14. Inference does not become verified fact without sufficient evidence.
15. Private operational state remains owned by its originating capability.
16. Shared knowledge crosses boundaries only through governed publication contracts.
17. ACTIVE means eligible under current policy, not globally trusted.
18. Permissions are minimal, explicit, temporary, verifiable, and revocable.
19. A capability cannot self-assert LIVE_VERIFIED.
20. A provider cannot independently certify itself for WhiteChronos promotion.
21. A fatal gate failure cannot be offset by high scores elsewhere.
22. WhiteChronos may propose its own changes but may not self-ratify changes to its authority, security boundaries, or core governance.
23. Failure is expected; uncontrolled propagation is not.
24. Telemetry observes; evidence proves; health is derived.
25. No degraded operating mode may become a governance bypass.

## 5. Macro architecture

~~~text
                    GitHub Control Plane
                 source of truth / history
                           |
                  protected changes
                           |
                WhiteChronos Kernel
       contracts | registry | resolver | policy
       context   | truth    | lifecycle | evidence
                           |
              contract-only invocation
                           |
        +------------------+------------------+
        |                  |                  |
   Local capability   External provider   Future type
   Skill / plugin     independent repo    unknown today
        |                  |                  |
        +------------------+------------------+
                           |
                    Knowledge Plane
        append-only ledger + derived indexes/views
                           |
                    Evolution Plane
        gaps + roadmap + quarantine + promotion
~~~

Logical centralization does not require one physical process. Kernel services may later be distributed, cached, sharded, or regional so long as contract, policy, provenance, and evidence semantics remain identical.

## 6. Kernel boundary

The Kernel SHALL remain small and stable.

It may contain only cross-cutting system responsibilities such as:

- Capability Contract registration and lookup;
- provider discovery and resolution;
- policy decision and authorization interfaces;
- lifecycle event semantics;
- context composition interfaces;
- truth resolution interfaces;
- evidence and provenance envelopes;
- runtime health/evidence semantics;
- promotion and revocation rules;
- compatibility and migration coordination.

The Kernel SHALL NOT accumulate provider-specific business logic.

Adding a new provider SHOULD NOT require modifying Kernel internals when the provider implements an existing contract.

Adding a new capability type SHOULD be possible through a namespaced extension contract unless it introduces a genuinely new cross-cutting primitive.

## 7. Capability Contract and Manifest v2

### 7.1 Contract / implementation separation

A Capability Contract describes behavior. A provider implements it.

A consumer declares a requirement such as:

~~~text
capability://knowledge/search >=2.1 <3
~~~

It SHALL NOT require a concrete implementation name when a capability contract is sufficient.

The Resolver chooses an eligible provider from compatible implementations.

### 7.2 Capability Manifest v2

Every executable or discoverable capability SHALL expose a manifest with a small stable envelope and extensible namespaces.

The envelope SHALL cover:

- stable capability/provider identity;
- contract and implementation versions;
- provenance, source repository, artifact/commit digest, publisher, and license;
- provided contracts;
- required contracts;
- input/output/error/side-effect semantics;
- risk profile and approval class;
- requested filesystem, network, credential, process, data, and mutation scopes;
- knowledge read/publication scopes;
- health/runtime probes;
- required conformance suites;
- compatibility ranges;
- rollback/deactivation metadata;
- ownership and provenance;
- namespaced extension metadata.

The extension model SHALL permit future types without forcing a Kernel rewrite.

Examples of logical extension namespaces include:

~~~text
whitechronos.skill/v1
whitechronos.agent/v1
whitechronos.mcp/v1
whitechronos.model/v1
whitechronos.workflow/v1
whitechronos.knowledge-source/v1
future.vendor.new-capability/v1
~~~

### 7.3 Risk becomes multidimensional

The current Registry v1 uses a single execution_class enum. Manifest v2 SHALL evolve this into a multidimensional risk profile because one capability may simultaneously be networked, credentialed, mutating, and autonomous.

The v1 schema remains valid during migration. It is not rewritten in place. Migration occurs through v2 plus explicit compatibility/adaptation rules.

## 8. Registry v2

The existing registry/integrations structure is retained as the migration foundation but SHALL evolve from a manually indexed integration catalog into a capability registry.

Logical responsibilities:

~~~text
registry/
  contracts/
  providers/
  adapters/
  lifecycle-events/
  certification/
  views/
~~~

Authoritative records SHALL be immutable manifests plus append-only lifecycle/certification events.

Generated indexes and views such as active, compatible, quarantined, deprecated, and searchable are materialized views and MAY be rebuilt.

A manually edited current-state field SHALL NOT be the final authority for lifecycle state.

## 9. Lifecycle model

Manifest identity is immutable; operational state changes through events.

A candidate lifecycle is:

~~~text
DISCOVERED
  -> QUARANTINED
  -> VALIDATING
  -> COMPATIBLE
  -> PROMOTABLE
  -> CANARY
  -> ACTIVE
  -> DEGRADED
  -> DEPRECATED
  -> REVOKED
~~~

Revalidation may move an ACTIVE capability into REVALIDATION_REQUIRED and then back to ACTIVE or into DEGRADED, QUARANTINED, or REVOKED.

The exact current state is a materialized interpretation of append-only lifecycle events.

## 10. Capability Resolver

The Resolver SHALL determine an eligible provider from:

- requested contract and compatible versions;
- provider lifecycle state;
- contract conformance;
- current policy and authorization;
- runtime/enforcement availability;
- health and circuit state;
- risk and approval state;
- environment restrictions;
- provider preference and cost/quality policy.

Every material resolution decision SHOULD be reproducible from recorded inputs.

A failover SHALL be visible in evidence. Provider substitution must not be silent.

## 11. Adapters

Adapters are first-class capabilities.

Each adapter SHALL declare:

- source contract/version;
- target contract/version;
- semantic transformation;
- information loss;
- unsupported cases;
- error mapping;
- conformance tests;
- provenance and lifecycle.

Adapter chains must be testable as complete chains, not only as isolated units.

An adapter may bridge compatible generations without allowing consumers to depend directly on provider internals.

## 12. Capability SDK

A minimal provider-neutral SDK SHOULD standardize stable operations such as:

~~~text
register
resolve
invoke
publish_knowledge
query_context
report_health
emit_evidence
request_approval
~~~

The SDK SHALL contain no domain-specific implementation logic.

A capability may depend on the SDK and declared contracts. It SHALL NOT depend directly on another capability's private implementation.

## 13. Isolation and dependency rules

Physical colocation does not create privilege.

A local module and an external repository are subject to the same logical boundary.

Forbidden by default:

- direct cross-capability imports into private implementation modules;
- private database access across capabilities;
- private memory reads;
- direct secret sharing;
- direct filesystem sharing;
- undeclared sockets or service calls;
- bypass of the Capability Bus/Resolver.

Permitted communication follows:

~~~text
consumer
  -> Capability SDK / Kernel boundary
  -> contract
  -> resolver
  -> provider
~~~

CI SHALL include structural checks that prove these boundaries instead of relying on documentation alone.

## 14. Knowledge Fabric

### 14.1 Private state vs shared knowledge

Each capability owns its private operational state.

Shared information enters the Knowledge Fabric only through a governed Knowledge Contract and ingestion gate.

No capability may directly read another capability's private database or memory merely because both participate in WhiteChronos.

### 14.2 Knowledge Record

A Knowledge Record SHALL carry enough metadata to preserve semantic meaning, provenance, authorization, and temporal interpretation.

At minimum it should represent:

- stable record identity and type;
- subject/predicate/object or equivalent semantic payload;
- domain/ontology namespace;
- producing capability and exact contract/provider versions;
- source and evidence references;
- observed time and validity interval;
- authority and confidence;
- verification state;
- access/security classification;
- relations such as supports, contradicts, supersedes, invalidates, and revokes;
- integrity digest;
- retention policy.

### 14.3 Append-only Knowledge Ledger

Published facts/claims SHALL NOT be silently overwritten or deleted.

Corrections create new records linked through relations such as supersedes, invalidates, or revokes.

Current knowledge is represented through reconstructible materialized views.

### 14.4 Derived indexes

Search indexes, graph projections, vector embeddings, caches, summaries, rankings, and other retrieval structures are derived.

They are not the historical authority and may be replaced or rebuilt from the Ledger.

This prevents the architecture from being permanently tied to a 2026 retrieval technology choice.

## 15. Epistemic typing and Truth Resolver

WhiteChronos SHALL distinguish evidence, claims, inference, and resolved conclusions.

A model-generated inference is not automatically a verified fact.

Truth resolution SHALL consider:

- source authority;
- evidence quality;
- provenance integrity;
- independence of sources;
- temporal validity;
- domain-specific policy;
- contract/provider version;
- confidence and uncertainty.

Resolution states SHOULD include at least:

- VERIFIED;
- SUPPORTED;
- DISPUTED;
- UNRESOLVED;
- NOT_VERIFIABLE;
- REVOKED.

Multiple apparently independent sources that derive from the same origin must not be counted as independent evidence.

Domain-specific truth policies SHALL be versioned outside Kernel domain logic.

## 16. Context Engine

WhiteChronos SHALL not attempt to load all available knowledge or all Skills into every model context.

Context is composed on demand.

Logical flow:

~~~text
task
 -> intent analysis
 -> domain detection
 -> capability discovery
 -> authorization filter
 -> relevant knowledge retrieval
 -> truth/conflict resolution
 -> ranking and deduplication
 -> context budget
 -> minimal sufficient Context Bundle
 -> selected agent/model/capability
~~~

A Context Bundle SHOULD record enough information to reconstruct what evidence, claims, policies, capabilities, and unresolved conflicts were available to the executor at decision time.

This supports the question:

**What did the system know, and why, when it made this decision?**

## 17. Controlled Evolution Engine

### 17.1 Evolution Ledger

The Evolution Plane uses an append-only Evolution Ledger.

Representative events include:

~~~text
NEED_DETECTED
GAP_CONFIRMED
RESEARCH_STARTED
ALTERNATIVES_FOUND
ARENA_EVALUATED
DESIGN_PROPOSED
CANDIDATE_CREATED
QUARANTINED
TESTING
BLOCKED
PROMOTABLE
CANARY
ACTIVE
REGRESSED
ROLLED_BACK
DEPRECATED
REVOKED
~~~

The Capability Roadmap is a materialized view of this history.

### 17.2 Permanent Capability Roadmap

Each initiative SHALL have stable identity and explain:

- the problem and desired capability;
- why it matters;
- origin and evidence;
- priority and expected impact;
- dependency pressure;
- risk and confidence;
- blockers;
- candidate solutions;
- Arena evidence;
- current lifecycle stage;
- next gate and next action.

The roadmap must be able to represent current, implementing, blocked, candidate, missing, deprecated, and future capability needs simultaneously without loading all of them into model context.

### 17.3 Gap detection

The system may automatically detect potential gaps from evidence such as repeated manual work, provider failure, high cost, degraded quality, missing capabilities, dependency deprecation, unresolved knowledge conflicts, or new technology discovery.

Gap detection creates an Evolution Ledger entry. It does not itself authorize activation.

### 17.4 Arena as a process layer

Arena becomes a governed review discipline:

- Micro Arena for normal decisions;
- Review Arena for complex code, architecture, CI/CD, integration, and security changes;
- Full Arena for explicit requests and protected/fundamental architecture decisions.

Arena evidence may accompany the evolution initiative, but strategy cards SHALL NOT be represented as independent subagents unless real isolated agents ran.

### 17.5 Skill Forge and Capability Factory

The system may create candidate Skills and other capability types through a controlled factory.

The factory SHALL first search for an existing equivalent capability, preserve provenance/license constraints, generate a candidate only in isolation, and subject it to the same quarantine and conformance rules as third-party software.

A Skill declaration SHALL include what it does, when it applies, when it must not apply, inputs/outputs, allowed tools, side effects, dependencies, context needs, risk, provenance, version, and tests.

Self-generated does not mean trusted.

### 17.6 Non-self-ratification

The system may detect, research, design, generate, test, and propose changes to itself.

It SHALL NOT unilaterally approve changes to:

- Kernel authority;
- security boundaries;
- approval policy;
- risk semantics;
- fundamental Capability Contracts;
- fundamental Truth Resolver semantics;
- Evolution Engine governance;
- GitHub Control Plane protections.

A mechanism may not enlarge its own authority, reduce its own gates, or approve changes to the rules that govern it.

## 18. Zero-Trust Security Fabric

### 18.1 Effective authorization

Effective permission is the intersection of:

~~~text
manifest request
AND policy allowance
AND requester authority
AND environment allowance
AND runtime enforceability
AND current approval
~~~

Unknown authorization or enforcement state fails closed.

### 18.2 Policy Decision Point and Enforcement Points

The Kernel provides a Policy Decision Point.

Policy Enforcement Points SHALL exist at capability invocation, secrets, filesystem, network, subprocess execution, knowledge publication, context retrieval, GitHub mutation, background execution, and external side-effect boundaries.

Model text, Skill instructions, web content, and retrieved documents cannot directly grant tool authority.

### 18.3 Execution Lease

Privileged operations receive short-lived Execution Leases bound to:

- execution/task;
- capability/provider digest;
- requester;
- environment;
- allowed actions;
- resource scopes;
- expiration;
- policy version;
- approval reference.

Long-running/background execution must renew leases. Expired leases end privileged authority.

### 18.4 Runtime isolation

The runtime SHOULD progressively enforce process isolation, filesystem isolation, network isolation, credential isolation, resource quotas, timeouts, and environment boundaries.

If a required enforcement mechanism is unavailable, Runtime Doctor reports the gap and the capability cannot be treated as executable for that risk profile.

Policy SHALL NOT be weakened simply to make a capability run.

### 18.5 Filesystem and network

Filesystem and network access are deny-by-default.

Capabilities receive only declared paths/domains/ports/scopes.

The design must defend against path traversal, symlink escape, mount crossing, undeclared egress, private/internal network access, metadata endpoint access, and uncontrolled inbound exposure.

### 18.6 Secrets

Manifests declare credential requirements, not credential values.

A provider-neutral Secret/Credential Broker supplies runtime-scoped credentials.

Preferred mechanisms are OIDC/workload identity and short-lived scoped tokens.

Static secrets, when unavoidable, stay in approved secret managers or GitHub Environment boundaries and never enter Git, durable memory, Data Center, Evidence Bundles, or backup manifests.

Secrets are bound to capability, execution, environment, scope, and TTL.

### 18.7 Prompt injection boundary

External content is data, not authority.

Prompt injection cannot:

- escalate permission;
- release secrets;
- change policy;
- grant filesystem/network access;
- bypass protected Control Plane operations.

Authorization is enforced outside the prompt content boundary.

### 18.8 Supply-chain integrity

Where appropriate, promotion evidence SHALL include immutable source pins, dependency locks, artifact digests, SBOM/provenance, and signatures or attestations.

A materially changed dependency may reopen required gates.

### 18.9 Background autonomy

Background capabilities SHALL declare purpose, trigger/schedule, maximum runtime, resource budget, network/mutation scopes, stop conditions, and lease renewal policy.

They SHALL have watchdog and kill-switch behavior.

### 18.10 Revocation

REVOKED must stop new resolution, revoke leases and short-lived credentials where possible, stop background work, invalidate affected caches, isolate the runtime, select a safe compatible fallback when allowed, and emit evidence.

## 19. Operational Evidence Fabric

### 19.1 Telemetry, evidence, and health

These are distinct.

- **Telemetry** may be high-volume, sampled, aggregated, time-limited, and stored in replaceable backends.
- **Evidence** proves promotions, denials, security events, policy decisions, canaries, rollbacks, runtime verification, and other critical outcomes.
- **Health** is a derived current view.

Telemetry systems such as future metrics/log/trace vendors are not authoritative merely because they are operationally useful.

### 19.2 Runtime event envelope

Material runtime events SHOULD correlate:

- task and execution identity;
- trace/parent identity;
- capability/provider/contract identity;
- exact artifact digest;
- repository/commit/PR;
- policy/environment identity;
- authorization lease and approval;
- runtime/Doctor evidence;
- result/error/side-effect summary;
- evidence integrity digest.

### 19.3 Health

Health is multidimensional and may include:

- availability;
- latency;
- contract conformance;
- quality;
- security;
- runtime integrity;
- dependency health.

Representative states include HEALTHY, DEGRADED, UNAVAILABLE, REVALIDATION_REQUIRED, QUARANTINED, REVOKED, and UNKNOWN.

UNKNOWN is not equivalent to HEALTHY.

### 19.4 SLI/SLO/error budget

Each Capability Contract may define relevant SLIs and SLOs.

No universal score SHALL pretend that every capability has the same operational requirements.

The Evolution Engine may use SLO/error-budget evidence to identify improvement or replacement needs.

## 20. Failure containment

Each capability is a failure domain.

Containment mechanisms MAY include:

- deadlines;
- timeouts;
- bounded retries;
- circuit breakers;
- bulkheads;
- resource quotas;
- provider failover;
- graceful degradation;
- quarantine.

Retries for side-effecting operations require explicit safety such as idempotency keys or deduplication. UNKNOWN execution results SHALL NOT be blindly retried.

Error classes SHOULD distinguish transient, permanent, policy-denied, authorization-expired, incompatible, contract-violation, resource-exhausted, security, dependency-failure, and unknown failures.

A circuit-open provider is temporarily ineligible for resolution but remains historically registered.

Capabilities may declare REQUIRED, OPTIONAL, or ENHANCEMENT dependency roles so degradation behavior is explicit.

## 21. Runtime Doctor evolution

The existing Runtime Doctor already separates repository/configuration checks, local probes, host discovery, runtime kind, Broker readiness, routing selection, and LIVE_SMOKE_READY.

This architecture extends that foundation rather than replacing it.

Future probes may cover:

- configuration;
- local initialization;
- contract surface;
- host discovery;
- runtime identity;
- filesystem enforcement;
- network enforcement;
- secret broker availability;
- lease enforcement;
- sandbox capability;
- provider health;
- canary;
- live smoke.

A passing individual check does not automatically confer a global evidence level.

## 22. Evidence levels and Runtime Evidence Bundles

Evidence levels are monotonic proof states such as:

~~~text
DECLARED
 -> CONFIG_VALIDATED
 -> LOCAL_PROBED
 -> HOST_DISCOVERED
 -> RUNTIME_VERIFIED
 -> CANARY_VERIFIED
 -> LIVE_VERIFIED
~~~

Each level is contextual to exact implementation digest, contract version, environment/runtime, policy, source commit, verification profile, and time.

A changed artifact, runtime, policy, or dependency may require revalidation.

Runtime Evidence Bundles SHALL be redacted and may include exact source/runtime identity, contracts, authorization, policy decision, Runtime Doctor evidence, checks, input/output digests, degradation/failover, and final status.

Secrets are excluded.

GitHub may anchor accepted evidence through manifests/digests without storing all raw telemetry.

## 23. Bounded degraded mode

Temporary GitHub/Control Plane unavailability SHALL NOT create a second authority.

A bounded degraded mode may permit already-authorized low-risk operations under a last-known-good policy and still-valid leases for a limited TTL.

During degraded mode:

- no new promotion;
- no new privileged authority;
- no Kernel change;
- no governance change;
- no new high-risk activation.

When the TTL expires, privileged degraded operation stops.

If required critical evidence cannot be persisted, high-risk operations fail closed.

## 24. Incident and recovery model

Critical operational failures produce structured Incident evidence with identity, trigger, affected capabilities/executions, timeline, containment, impact, root cause, recovery, and closure criteria.

Confirmed incident knowledge may feed the Knowledge Ledger and Evolution Ledger.

Recovery SHALL rebuild from authoritative manifests/events where possible:

~~~text
restore authoritative records
 -> verify integrity
 -> rebuild materialized views
 -> re-resolve providers
 -> Runtime Doctor
 -> canary
 -> return to service
~~~

Caches and derived indexes are disposable.

RPO/RTO requirements differ by state class: Kernel/governance, Knowledge Ledger, Evolution Ledger, and accepted Runtime Evidence require stronger protection than raw telemetry or caches.

The external cold mirror remains one-way disaster recovery only and never writes back automatically.

## 25. Continuous Verification Fabric

### 25.1 Three verification layers

WhiteChronos SHALL keep distinct:

1. **Implementation Tests** — provider-owned internal correctness.
2. **Contract Tests** — contract-owned proof that any provider satisfies the external behavior.
3. **System Certification** — WhiteChronos-owned proof that the exact provider can operate under current runtime, policy, security, and compatibility requirements.

Provider-owned PASS is not equivalent to WhiteChronos certification.

### 25.2 Conformance Harness

A universal Conformance Harness SHALL evaluate the exact provider artifact against the relevant contract, security, isolation, compatibility, failure, runtime, and promotion requirements.

Candidate verification levels may include:

~~~text
MANIFEST_VALID
STATIC_CONFORMANT
CONTRACT_CONFORMANT
COMPATIBILITY_VERIFIED
SECURITY_VERIFIED
ISOLATION_VERIFIED
FAILURE_BEHAVIOR_VERIFIED
RUNTIME_VERIFIED
CANARY_VERIFIED
LIVE_VERIFIED
~~~

These are verification dimensions supporting evidence levels; they do not replace lifecycle or health.

### 25.3 Positive, negative, and boundary tests

Security and capability conformance must verify both allowed behavior and forbidden behavior.

Examples include denied private paths, traversal/symlink escape, cross-capability state access, undeclared network, Ledger overwrite, inference promoted as verified fact, expired lease use, direct protected-state write, and self-declared LIVE_VERIFIED.

### 25.4 Constitutional invariant tests

The repository SHALL eventually have executable tests for key architectural invariants such as:

- no direct private system-to-system dependency;
- no private-memory cross-access;
- no silent Ledger overwrite;
- no unknown risk to low-risk default;
- no provider self-certification;
- no secret persisted in evidence;
- no protected branch bypass;
- no Kernel self-ratification;
- no GitHub outage governance bypass.

These are release blockers.

### 25.5 Hard blockers before scoring

Promotion is:

~~~text
all required hard gates PASS
AND
quality policy PASS
~~~

A fatal flaw makes a candidate ineligible regardless of performance or aggregate score.

Hard blockers include contract violations, critical security failures, undeclared privilege, unacceptable provenance/license, integrity mismatch, protected-state bypass, private cross-capability access, missing required evidence, and missing rollback/failover strategy when policy requires one.

### 25.6 Quality scorecards

Eligible providers may then be compared on domain-appropriate metrics such as correctness, reliability, security, performance, efficiency, observability, maintainability, interoperability, and recovery.

No universal score SHALL erase domain-specific requirements.

### 25.7 Compatibility matrix

Compatibility between consumers, contracts, providers, and adapters must be proven.

Unknown compatibility is NOT_VERIFIED, never presumed compatible.

Adapter chains are tested as complete semantic paths.

### 25.8 Property, fuzz, replay, shadow, and chaos testing

Where appropriate:

- property-based testing verifies invariants across generated cases;
- fuzzing attacks parsers and untrusted boundaries;
- deterministic state rebuilds are replay-tested;
- probabilistic AI systems are tested against invariant schemas/policy/provenance rather than exact text;
- Shadow Mode compares candidate behavior without external side effects;
- controlled chaos testing proves failure containment and degraded behavior only in authorized environments.

### 25.9 Rollback evidence

A rollback declaration alone is insufficient. Critical promotion may require proof that rollback or equivalent restore/failover actually works.

### 25.10 Impact-based revalidation

Not every change reruns every test.

The system computes an affected verification set.

Examples:

- documentation-only change: no runtime recertification;
- provider artifact change: implementation, contract, and runtime revalidation;
- security policy change: authorization/security revalidation;
- contract major change: compatibility recertification;
- dependency change: supply-chain plus affected behavior tests.

### 25.11 Promotion Evidence Bundle

Every promotion SHALL produce structured evidence bound to the exact candidate artifact, source commit, contract, dependency/provenance identity, conformance results, security results, compatibility, Doctor/runtime proof, required chaos/failure/rollback/canary results, policy version, approvals, and timestamp.

PROMOTED is a derived lifecycle event from this evidence, not a manually asserted current-state field.

## 26. Process as data

The development/evolution process SHALL become machine-verifiable rather than living only in prose.

A project should be able to report stages such as:

~~~text
Design: APPROVED
Written Spec: PENDING_REVIEW
Implementation Plan: BLOCKED_BY_SPEC_APPROVAL
Implementation: NOT_AUTHORIZED
~~~

Applicable process stages include brainstorming, alternatives, Arena, design, written spec, implementation plan, implementation, tests, review, promotion, and verification.

This prevents future work from silently forgetting required gates as the repository grows.

## 27. AGENTS.md evolution

AGENTS.md currently contains many integration-specific layers and routing rules.

The long-term architecture SHOULD evolve AGENTS.md toward a stable constitution containing:

- non-negotiable governance;
- process routing;
- safety and evidence invariants;
- references to structured registries/policies.

Integration-specific catalogs, versions, providers, and activation metadata SHOULD migrate toward manifests/registries rather than being appended indefinitely to the global instruction file.

This migration must be incremental and must not remove currently enforced repository rules before equivalent structured enforcement exists and is verified.

## 28. GitHub Control Plane integration

This architecture is subordinate to and compatible with the existing GitHub hardening design.

Protected changes continue to follow:

~~~text
candidate
 -> isolated branch
 -> tests / conformance
 -> Arena
 -> pull request
 -> required GitHub checks
 -> approvals where required
 -> protected integration
~~~

Capabilities, Evolution Engine workflows, self-modification proposals, Runtime Doctor, and the Conformance Harness SHALL NOT obtain a side channel that can update protected state directly.

External component repositories may be canonical for their own code only after the root Control Plane registers and pins their immutable identity. They do not become parallel control planes.

PR #57 SHALL remain DRAFT throughout this written-spec review.

## 29. Migration from current repository state

The current repository already provides useful foundations:

- registry/integrations/schema.json v1;
- registry/integrations/index.json;
- registered GitHub Arena and Subagent Broker integrations;
- Runtime Doctor and runtime probes;
- GitHub-first hardening rules and policy gates;
- append-oriented engineering evidence principles;
- Superpowers and Arena process requirements.

Migration SHALL be additive and staged:

1. preserve Registry v1 compatibility;
2. introduce Capability Contract/Manifest v2 schemas without silently mutating v1 semantics;
3. separate immutable manifests from lifecycle events;
4. generate registry materialized views instead of treating manual indexes/current-state fields as ultimate authority;
5. introduce contract-based resolution alongside current integration routing;
6. add Knowledge/Evolution Ledgers and their materialized views;
7. introduce Zero-Trust policy and execution-lease enforcement incrementally;
8. extend Runtime Doctor with capability-oriented probes;
9. introduce Conformance Harness and Promotion Evidence;
10. migrate integration-specific AGENTS.md knowledge only after equivalent structured rules are proven.

No migration step may weaken the current GitHub hardening gates.

## 30. Failure semantics

The architecture SHALL fail conservatively:

- unknown capability risk -> quarantine/human review;
- unknown compatibility -> NOT_VERIFIED;
- missing evidence -> not promoted;
- unresolved truth conflict -> DISPUTED/UNRESOLVED/NOT_VERIFIABLE;
- unavailable required runtime enforcement -> execution denied;
- expired authorization -> privileged execution stops;
- security/contract violation -> isolate and emit evidence;
- provider degradation -> circuit/open/failover when safe;
- evidence sink unavailable for high-risk action -> fail closed;
- stale host/runtime -> reload/revalidate, not source-code workaround;
- unavailable optional enhancement -> explicit graceful degradation;
- unavailable required capability -> block the task;
- GitHub temporarily unavailable -> bounded degraded mode only, with no governance changes.

## 31. Objective acceptance criteria

This umbrella architecture is considered implemented only when the following are objectively demonstrable:

1. A new low-risk provider for an existing contract can be added without Kernel modification.
2. A large provider can move from monorepo to an external canonical component repository without consumer code depending on its private internals.
3. Direct cross-capability private imports/access are blocked by CI/runtime policy.
4. Contract versions and adapters coexist without silent migration.
5. Registry current-state views can be rebuilt from immutable manifests/events.
6. Knowledge current-state views can be rebuilt from the append-only Knowledge Ledger.
7. Conflicting valid claims remain visible and the Truth Resolver never hides unresolved conflict.
8. Context Engine can construct a minimal task-specific Context Bundle with provenance.
9. Evolution Ledger can explain what exists, what is missing, what is blocked, why, and the next gate/action.
10. Self-generated capabilities enter quarantine exactly like external candidates.
11. High-risk promotion cannot occur without the required human approval.
12. A protected Kernel/governance change cannot be self-ratified.
13. Unknown risk and unknown compatibility fail closed.
14. Execution Leases constrain privileged runtime operations and can expire/revoke.
15. Secrets do not appear in manifests, durable knowledge, Evidence Bundles, or Git history.
16. A capability failure can be contained without cascading through unrelated providers.
17. Circuit/failover behavior is visible in evidence.
18. Runtime Doctor can prove the enforcement prerequisites required by a sensitive capability.
19. A provider cannot self-declare LIVE_VERIFIED.
20. Promotion Evidence binds the exact artifact, contract, runtime, policy, approvals, and required test results.
21. Fatal blockers prevent promotion regardless of quality score.
22. Rollback/failover can be demonstrated where required.
23. GitHub remains the accepted source-controlled authority and no operational subsystem becomes a parallel authority.
24. Materialized operational and knowledge views can be reconstructed after loss.
25. Process state can prove that design/spec/plan/implementation gates were not skipped.

## 32. Implementation decomposition

This design is an umbrella architecture and is intentionally larger than a single low-risk implementation slice.

Implementation SHOULD be decomposed into staged work while preserving one architecture:

1. Capability Contract + Manifest v2 + Registry event model.
2. Resolver + Adapter semantics + dependency-boundary enforcement.
3. Knowledge Record + append-only Ledger + materialized view foundation.
4. Truth Resolver + Context Engine.
5. Evolution Ledger + permanent Capability Roadmap + gap detection.
6. Skill/Capability Factory + quarantine/promotion lifecycle.
7. Zero-Trust policy model + Execution Leases + Secret Broker interfaces.
8. Runtime isolation/enforcement integration.
9. Operational Evidence Fabric + health/circuit/failover model.
10. Runtime Doctor capability-probe extension.
11. Continuous Verification + Conformance Harness + Promotion Evidence.
12. AGENTS.md constitutional consolidation and migration.
13. System-level recovery, replay, chaos, canary, and acceptance validation.

Each staged implementation receives its own tests, review evidence, rollback strategy, and GitHub-controlled merge path.

No stage is authorized merely by this design document.

## 33. Full Arena conclusions

The architecture was reviewed using a Full Arena plan of 16 strategy cards in four logical elimination rounds: 16 -> 8 -> 4 -> 2 -> 1.

The current ChatGPT runtime did not expose 16 independent isolated agents. The Arena run is therefore a structured sequential adaptation and SHALL NOT be represented as independent-agent execution.

Material conclusions from the review:

- keep Kernel responsibilities small and cross-cutting;
- prefer contracts over provider identities;
- preserve append-only authority and make current views reconstructible;
- keep conflicts visible instead of maximizing apparent certainty;
- treat process state as machine-verifiable data;
- separate ACTIVE from TRUSTED;
- make authorization contextual and temporary;
- separate telemetry from evidence;
- make failure containment and rollback first-class;
- require exact-artifact conformance rather than trusting provider-owned tests;
- let hard blockers dominate aggregate quality scores;
- preserve GitHub as the only accepted source-controlled authority;
- ensure every future extensibility mechanism fails closed when it encounters a capability, risk, or compatibility class it does not understand.

## 34. Intentionally deferred implementation choices

This spec fixes architecture and invariants but intentionally does not lock WhiteChronos to a specific future implementation technology for:

- ledger database/storage engine;
- vector index/search backend;
- graph store;
- telemetry backend;
- secret-manager vendor;
- policy engine implementation;
- container/sandbox technology;
- message/event transport;
- service-mesh technology;
- distributed cache;
- workload scheduler.

Those are provider/implementation decisions and must satisfy the contracts and acceptance criteria above. Deferring them is intentional extensibility, not an unresolved architectural requirement.

## 35. Implementation boundary and next process gate

This document records the approved conversational design as a written architecture for user review.

It does **not** authorize:

- product/runtime implementation;
- Registry v2 migration;
- Kernel modification;
- new capability activation;
- GitHub ruleset/environment/security mutation;
- live smoke;
- protected-branch merge;
- PR #57 ready-for-review transition;
- PR #57 merge.

After this written spec is reviewed and explicitly approved, the next mandatory Superpowers step is to invoke writing-plans and produce the implementation plan. Implementation may begin only after the user reviews that plan and selects the execution method.
