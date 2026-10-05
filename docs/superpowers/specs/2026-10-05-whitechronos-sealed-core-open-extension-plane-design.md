# WhiteChronos Sealed Core + Open Extension Plane Design

**Status:** DESIGN APPROVED — WRITTEN SPEC PENDING USER REVIEW  
**Date:** 2026-10-05  
**Repository:** WhiteChronos/ChatGPT  
**Working branch:** spec-whitechronos-sealed-core-open-extension-plane-v1  
**Base branch:** spec-whitechronos-global-conversation-bootstrap-v1  
**Frozen Core baseline commit:** 2f6fd7a785999ef7827e74f35167a452c98d7920  
**Related baseline:** docs/superpowers/specs/2026-10-05-whitechronos-global-conversation-bootstrap-design.md  
**Related capability architecture:** Registry v2 / Capability Resolver / Adapter boundary work represented by PR #59 or a later reviewed equivalent.

## 1. Authorization record

The user explicitly authorized the following architectural design on 2026-10-05:

> AUTORIZO o design Sealed Core + Open Extension Plane para o WhiteChronos v1.0, com o Core fechado e imutável, Extension Plane aberto para novas capacidades versionadas, e mudanças incompatíveis exigindo nova versão major. Autorizo a criação do documento formal de arquitetura/governança e, em seguida, do plano de implementação correspondente.

The same authorization explicitly does not grant merge, deploy, canary, stable, live smoke, or PRODUCTION COMPLETE authority. Those remain subject to their independent gates.

This document is a companion specification to the frozen WhiteChronos v1.0 baseline. It does not rewrite, amend in place, or replace the frozen Core baseline commit.

## 2. Decision summary

WhiteChronos SHALL adopt the architecture:

**Sealed Core + Open Extension Plane**

The WhiteChronos v1.0 Core remains closed and immutable as an architectural and governance reference. Future capability growth happens through an additive, versioned Extension Plane with explicit contracts, provenance, risk classification, compatibility evidence, authorization, and lifecycle state.

The governing principle is:

> **Close the Core; keep evolution open.**

The ecosystem principle remains:

> **WhiteChronos defines the foundation; other systems build on it independently.**

The closure principle is:

> **A closed version is a stable reference, not a prohibition on future capability.**

## 3. Goals

This design SHALL:

1. preserve WhiteChronos v1.0 as a stable and immutable Core baseline;
2. allow new capabilities, systems, providers, adapters, skills, plugins, and compatible contract versions to be added without reopening the Core;
3. prevent an extension from silently changing Core semantics or governance;
4. classify incompatible changes as a new major-version architecture event;
5. preserve independent authorization domains for integration, deployment, canary, stable promotion, and production closure;
6. keep the existing Tasks 1–12 runtime track independent from future extension work;
7. make extension admission deterministic, auditable, reversible, and fail-closed;
8. contain extension failure to the smallest safe domain;
9. retain GitHub as source-controlled authority;
10. preserve the existing WhiteChronos governance chain.

## 4. Non-goals

This design does not:

- execute Tasks 1–12;
- authorize inline fallback for the real Subagent-driven runtime requirement;
- merge PR #57, #59, #60, #61, or this specification;
- deploy any WhiteChronos component;
- promote candidate, canary, or stable;
- run a live smoke;
- authorize R2/R3 operations;
- grant credentials;
- declare PRODUCTION COMPLETE;
- turn GitHub presence into runtime admission;
- permit extensions to modify the frozen Core baseline in place.

## 5. System topology

The logical topology is:

~~~text
WhiteChronos
|
+-- Sealed Core v1.0
|   +-- architecture baseline
|   +-- governance invariants
|   +-- trust boundaries
|   +-- authority separation
|   +-- host/runtime truth semantics
|   +-- security minimums
|
+-- Runtime Track
|   +-- Tasks 1-12
|   +-- runtime implementation
|   +-- tests and evidence
|   +-- release/deploy/promotion gates
|
+-- Open Extension Plane
    +-- capability contracts
    +-- providers
    +-- adapters
    +-- skills/plugins
    +-- system integrations
    +-- compatible contract evolution
    +-- lifecycle/admission records
~~~

These three domains are related but not interchangeable.

## 6. Sealed Core definition

The Sealed Core is the immutable architectural and governance reference defined by the WhiteChronos v1.0 baseline commit:

~~~text
2f6fd7a785999ef7827e74f35167a452c98d7920
~~~

The Sealed Core SHALL NOT be changed in place to admit a new capability.

Core closure covers at minimum:

- constitutional invariants;
- trust boundaries;
- governance chain;
- evidence-state separation;
- authority-domain separation;
- risk fail-closed semantics;
- session-isolation principles;
- source-of-truth rules;
- secret-handling minimums;
- quarantine, revocation, and kill-switch semantics;
- production-readiness truthfulness rules.

A later specification may supersede the Core only through a separately authorized major-version process. Supersession never mutates the historical v1.0 identity.

## 7. Open Extension Plane definition

The Extension Plane is the authorized growth surface for WhiteChronos-compatible capability.

It MAY admit:

- new capability contracts;
- new provider implementations;
- new adapters;
- new skills or plugins;
- new host integrations;
- new read-only or mutating capabilities subject to risk and authority gates;
- new systems that depend on WhiteChronos contracts;
- compatible new versions of extension contracts;
- lifecycle events, evidence, admission metadata, and revocation state.

Admission to the Extension Plane SHALL be additive and versioned.

Presence in a repository, marketplace, plugin catalog, or Registry directory SHALL NOT by itself make an extension active or authorized.

## 8. Core immutability rules

The following invariants are mandatory:

1. Core baseline identity is pinned to an immutable commit SHA.
2. New inclusion SHALL NOT rewrite the baseline commit.
3. New inclusion SHALL NOT weaken a Core invariant.
4. New inclusion SHALL NOT reinterpret UNKNOWN as healthy, compatible, authorized, executed, or successful.
5. New inclusion SHALL NOT merge authority domains.
6. New inclusion SHALL NOT broaden delegated authority.
7. New inclusion SHALL NOT introduce permanent superuser authority.
8. New inclusion SHALL NOT move secrets into GitHub, cache, Registry, or ledger.
9. New inclusion SHALL NOT make runtime availability claims from configuration alone.
10. New inclusion SHALL NOT make production claims without fresh evidence.

The central authority invariant remains:

~~~text
authority(output) <= authority(input)
~~~

Delegation remains:

~~~text
delegated_scope subset_of original_scope
~~~

## 9. Extension classification

Every proposed inclusion SHALL be classified before implementation or admission.

### 9.1 ADDITIVE_EXTENSION

A new capability that does not alter an existing Core semantic contract.

Examples:

- a new capability contract;
- a new provider for an existing contract;
- a new adapter between accepted contracts;
- a new Skill that consumes existing governance contracts;
- a new system that depends on WhiteChronos without changing WhiteChronos Core behavior.

Result: may proceed through the Extension Plane.

### 9.2 COMPATIBLE_EVOLUTION

An additive new version that preserves the compatibility guarantees declared by its predecessor and does not alter frozen Core invariants.

Compatible evolution SHALL be represented as a new immutable version/record. It SHALL NOT overwrite a previously accepted record.

Result: may proceed through the Extension Plane after compatibility evidence.

### 9.3 BREAKING_CHANGE

Any proposal that changes the meaning of a frozen Core invariant, breaks an accepted compatibility promise, broadens authority semantics, changes the security model, or requires consumers to reinterpret the v1.0 Core.

Result:

~~~text
BREAKING_CHANGE
 -> reject from v1 Extension Plane
 -> require separately authorized WhiteChronos v2 design
 -> new spec
 -> new implementation plan
 -> independent authorization gates
~~~

A breaking change SHALL NOT be smuggled into a minor, patch, provider, adapter, or policy record.

## 10. Extension identity and provenance

Every admitted extension SHALL have an immutable identity sufficient to answer:

- what is it;
- which version is it;
- what Core baseline does it target;
- what contracts does it provide or require;
- where did it come from;
- what immutable revision/digest identifies its implementation;
- what license/provenance applies;
- what risk profile applies;
- what evidence admitted it;
- what lifecycle state is current.

Where Registry v2 is applicable, its append-only contract/provider/adapter/lifecycle model SHALL be reused rather than duplicated.

Existing accepted records SHALL NOT be edited to simulate lifecycle transition. Lifecycle changes are append-only events.

## 11. Dependency model

Every extension SHALL explicitly declare its dependencies.

At minimum:

~~~text
extension_id
extension_version
minimum_core_baseline
provided_contracts
required_contracts
provider_or_source_identity
immutable_revision_or_digest
risk_profile
admission_evidence
~~~

Dependencies SHALL be explicit rather than inferred from filesystem proximity, naming convention, or transitive imports.

An extension SHALL NOT directly depend on another provider's private implementation when a declared capability contract is the required boundary.

## 12. Admission pipeline

The normal admission pipeline is:

~~~text
Proposal
 -> Classification
 -> Provenance / identity check
 -> Contract validation
 -> Compatibility validation
 -> Risk classification
 -> Security review
 -> Runtime requirements check
 -> Arena challenge
 -> Verification
 -> Authorization Gate
 -> Admission action
 -> Post-Verification
 -> Lifecycle state update
~~~

The frozen governance chain remains authoritative:

~~~text
Superpowers executes
 -> Arena challenges
 -> Verification validates
 -> Authorization Gate authorizes
 -> Executor acts
 -> Post-Verification confirms
~~~

The mandatory state separation remains:

~~~text
VERIFIED != AUTHORIZED
AUTHORIZED != EXECUTED
EXECUTED != SUCCESSFUL
~~~

## 13. Authority domains

Extension admission does not collapse release authority.

The following remain independent:

~~~text
extension_admission_authority != core_change_authority
merge_authority               != deploy_authority
deploy_authority              != canary_authority
canary_authority              != stable_authority
stable_authority              != production_closure_authority
~~~

An approval for a new extension SHALL NOT authorize a change to the Sealed Core.

An approval to merge an extension SHALL NOT authorize deploy.

An approval to deploy SHALL NOT authorize canary or stable promotion.

Stable promotion SHALL NOT by itself justify PRODUCTION COMPLETE.

## 14. Risk and execution boundaries

Each extension SHALL be classified under WhiteChronos risk semantics.

Unknown risk fails closed.

Extensions requiring mutation, credentials, background execution, irreversible action, external side effects, or control-plane change SHALL require the corresponding higher authority and SHALL NOT inherit authorization merely because the extension itself was admitted.

Adapters SHALL preserve:

~~~text
authority(output) <= authority(input)
~~~

A semantically compatible adapter does not confer operational permission.

## 15. Isolation and blast-radius containment

Extension failure SHALL degrade the smallest safe domain.

A failed, regressed, quarantined, or revoked extension SHALL NOT require reopening or disabling the Sealed Core unless the Core itself is independently proven unsafe.

The preferred failure sequence is:

~~~text
affected version
 -> affected provider
 -> affected adapter
 -> affected capability
 -> affected channel
 -> broader containment only when evidence requires it
~~~

The global kill switch remains a last-resort Core control.

## 16. Compatibility with Registry v2

The existing Registry v2 direction is aligned with this design because it already models accepted records additively and uses immutable identity plus append-only lifecycle events.

Where applicable, the Extension Plane SHALL reuse:

- capability contracts;
- provider manifests;
- adapters;
- lifecycle events;
- immutable versions;
- provenance;
- risk profiles;
- deterministic resolution.

The Extension Plane SHALL NOT create a competing second capability registry unless separately designed and authorized.

Registry structure is not execution authority. Resolution is not authorization. Admission is not activation.

## 17. Runtime Track remains independent

The previously authorized Tasks 1–12 remain on their own implementation track.

Their current semantic status remains:

~~~text
tasks_1_12     = AUTHORIZED
execution      = WAITING_FOR_COMPATIBLE_RUNTIME
start_point    = TASK_1
~~~

The Sealed Core + Open Extension Plane design does not require those tasks to finish before other compatible systems can evolve.

Likewise, extension development does not convert Tasks 1–12 into complete work.

## 18. Production closure semantics

WhiteChronos SHALL keep Core closure separate from runtime production closure.

~~~text
CORE_CLOSED != PRODUCTION_COMPLETE
~~~

Core closure means:

- architecture frozen;
- governance frozen;
- immutable baseline identity established;
- incompatible changes require a new major version.

PRODUCTION COMPLETE requires actual implementation and evidence for the production claim, including all applicable execution, verification, release, deployment, promotion, and post-verification gates.

No document status may manufacture PRODUCTION COMPLETE.

## 19. Versioning rules

The versioning model is:

### Patch-level extension change

Use for compatible implementation corrections or metadata/evidence changes that do not alter contract semantics. Immutable accepted records are replaced by new versions/events rather than edited historically where the registry contract requires immutability.

### Minor-compatible extension evolution

Use for additive, compatible capabilities or contract versions. Existing consumers pinned to older accepted versions remain valid.

### Major change

Required when the proposal changes frozen Core semantics or breaks compatibility.

~~~text
v1 Core remains historical and immutable
new major design becomes a separate baseline
~~~

A future v2 may supersede v1 for new consumers, but it SHALL NOT rewrite v1 history.

## 20. New-system dependency rule

A new system MAY use WhiteChronos v1.0 as a foundation without waiting for Tasks 1–12 unless that system has a concrete technical dependency on a capability implemented by those tasks.

Each new system SHALL declare:

- which WhiteChronos baseline it references;
- which contracts it consumes;
- which runtime capabilities it actually requires;
- its own implementation/test plan;
- its own Authorization Gates;
- whether it can degrade safely when a WhiteChronos runtime capability is unavailable.

This preserves:

> **Foundation, not queue.**

## 21. Extension admission states

An extension lifecycle SHOULD distinguish at minimum:

~~~text
PROPOSED
DISCOVERED
VALIDATING
COMPATIBLE
PROMOTABLE
CANARY
ACTIVE
DEGRADED
REVALIDATION_REQUIRED
REGRESSED
ROLLED_BACK
DEPRECATED
REVOKED
~~~

State names may reuse the existing Registry v2 lifecycle when applicable.

No state name shall erase the distinction between technical state and authorization state.

## 22. Revocation and rollback

Rollback and revocation remain different.

- **Rollback** selects a previously acceptable implementation/version.
- **Revocation** marks an artifact/version ineligible for trust or routing.

A revoked extension SHALL NOT be selected as an automatic fallback.

Revoking an extension does not mutate the Sealed Core.

## 23. Evidence and audit

Extension admission and production claims SHALL be evidence-based.

Evidence SHOULD be sufficient to reconstruct:

- selected baseline;
- exact extension identity/version;
- exact source revision/digest;
- tests and validation performed;
- Arena findings and dispositions;
- risk classification;
- Authorization Gate decision;
- executor action;
- post-verification result;
- lifecycle transition.

Evidence metadata SHALL remain privacy-safe and SHALL NOT retain conversation content or secrets by default.

## 24. Security requirements

The Extension Plane SHALL preserve least privilege.

Extensions SHALL NOT:

- receive undeclared credentials;
- persist raw secrets;
- expand filesystem/network authority implicitly;
- bypass host-native authorization;
- bypass quarantine/revocation;
- weaken UNKNOWN fail-closed behavior;
- bypass the Runtime Doctor evidence ladder;
- claim HOST_DISCOVERED from configuration;
- claim LIVE_VERIFIED without approved real-runtime evidence.

## 25. Required implementation controls

The implementation plan produced after written-spec approval SHALL include controls for:

1. immutable Core baseline pinning;
2. extension classification;
3. extension manifest/schema validation;
4. explicit Core baseline compatibility declaration;
5. additive identity/version rules;
6. detection of attempted Core mutation;
7. detection of undeclared/broadened authority;
8. extension-specific quarantine/revocation;
9. deterministic admission evidence;
10. independent authorization gates;
11. regression coverage proving existing v1 consumers remain unaffected;
12. documentation of new-system dependency declarations.

Implementation SHALL prefer existing Registry v2 primitives where they satisfy these requirements.

## 26. Acceptance criteria

This design is correctly implemented when all of the following are demonstrated:

- the frozen Core baseline commit remains unchanged;
- a compatible new capability can be added without editing the Core;
- a provider can be added as a new immutable version;
- an adapter cannot broaden authority;
- a quarantined/revoked extension becomes ineligible without disabling unrelated extensions;
- an extension cannot become active merely by existing in GitHub;
- a breaking Core change is rejected from the v1 Extension Plane;
- a breaking proposal is routed to a new-major design path;
- merge/deploy/canary/stable/production authorities remain separate;
- Core closure cannot be confused with PRODUCTION COMPLETE;
- Tasks 1–12 remain independently runtime-gated;
- a new system can reference the frozen Core baseline without waiting for unrelated runtime work.

## 27. Migration and adoption

No migration of the frozen Core is required.

Adoption happens by adding the Extension Plane governance and implementation around the frozen baseline.

Existing work SHOULD progressively declare its referenced Core baseline and explicit capability dependencies when touched for related reasons. No broad unrelated refactor is required.

PR #59 or a later reviewed equivalent remains the preferred source for Registry v2 resolver/adapter primitives when the implementation plan reaches those dependencies.

## 28. Governance closure

After this written specification is reviewed and accepted, the intended governance state is:

~~~text
WhiteChronos Core v1.0
architecture       = SEALED
governance         = SEALED
baseline identity  = IMMUTABLE
direct core edits  = CLOSED

WhiteChronos Extension Plane
new inclusions     = OPEN THROUGH ADMISSION
compatibility      = REQUIRED
versioning         = REQUIRED
authorization      = REQUIRED
breaking changes   = REQUIRE NEW MAJOR

WhiteChronos Runtime Track
tasks_1_12         = AUTHORIZED
execution          = WAITING_FOR_COMPATIBLE_RUNTIME
production         = NOT YET COMPLETE
~~~

This is the durable interpretation of:

> **A system can be closed and stable while remaining prepared to accept new capability without reopening its Core.**

## 29. Next gate

Per the Superpowers architectural workflow, this written specification requires user review before the implementation plan is authored.

Approval of this written specification authorizes the next step: creation of the detailed implementation plan.

It still does not authorize merge, deploy, canary, stable, live smoke, R2/R3 execution, or PRODUCTION COMPLETE.
