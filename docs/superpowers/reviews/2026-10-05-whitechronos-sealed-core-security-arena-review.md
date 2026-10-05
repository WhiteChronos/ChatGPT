# WhiteChronos Sealed Core Security Review — Superpowers + Full Arena

**Status:** REVIEW COMPLETE — REMEDIATION PLANNED — NO PRODUCTION CLAIM  
**Date:** 2026-10-05  
**Repository:** WhiteChronos/ChatGPT  
**Approved spec:** PR #62 / commit `c5321b17a69148e4f48c1fe3eefd84dfde112a1c`  
**Frozen Core baseline:** `2f6fd7a785999ef7827e74f35167a452c98d7920`  
**Registry v2 implementation reviewed:** PR #59 / `09f6f3d59931e69a4c101817a687356b8dc7fcb0` or its reviewed branch content  
**Governance hardening evidence reviewed:** PR #57 / `f976ac5f02d51233a1015d59fe627b8918c3945a`

## 1. Review method

This review applies:

- the official Superpowers workflow as the process layer;
- the WhiteChronos frozen governance invariants;
- a Full Arena review with 16 strategy cards;
- the Frontier Infra agent-governance threat lenses for authority, verifier freshness, mutation-path coverage, reversibility, human gates, audit receipts, runtime health, and negative tests;
- direct GitHub evidence from the current repository and PR heads.

The current ChatGPT host exposes no native or Broker subagent lifecycle tools. Therefore the 16 Arena strategies were executed as sequential review perspectives in one model context, not represented as independent agents.

This is a high-coverage review of the WhiteChronos surfaces inspected here. It does not claim that unknown vulnerabilities cannot exist in files, dependencies, external services, or runtime states that were not available to this session.

## 2. Current live evidence

### 2.1 Chronos ruleset

GitHub currently reports ruleset `Chronos` id `21770911` as:

~~~text
enforcement = active
protected refs =
  ~DEFAULT_BRANCH
  refs/heads/spec/**
  refs/heads/release/**
required check = github-control-plane-policy
bypass actors = none
~~~

This closes the earlier condition where the ruleset was disabled.

### 2.2 Required-check availability mismatch

The PR #62 head `c5321b17...` currently has zero check runs.

The PR #61 head `70be04b3...` currently has zero check runs.

The PR #57 head `f976ac5f...`, which contains the `.github/workflows/github-control-plane-policy.yml` workflow, has successful `github-control-plane-policy` check runs.

Therefore the ruleset is active before the required check producer is present on the baseline used by PRs #60/#61/#62. This is a confirmed integration deadlock risk and must be remediated before controlled merge can be considered.

## 3. Severity model

- **CRITICAL** — can collapse a frozen authority/security invariant or create a direct governance bypass.
- **HIGH** — can admit/reroute untrusted capability, leak authority/credentials, or materially weaken supply-chain/runtime isolation.
- **MEDIUM** — can corrupt audit truth, allow denial-of-service, create unsafe future interpretation, or undermine deterministic validation.
- **LOW** — hardening or deterministic-operability issue with limited direct impact.

A finding can be confirmed in code while still not be production-reachable because PR #59 is draft/unmerged or because the current host has no compatible runtime.

## 4. Findings and solutions

### WC-SEC-001 — Unconstrained capability lifecycle transitions
**Severity:** CRITICAL  
**State:** Confirmed in reviewed Registry v2 code; not merged to production.

`derive_lifecycle_view()` verifies chain shape but does not enforce an allowed transition matrix. A lifecycle may start at `ACTIVE`, and `REVOKED -> ACTIVE` is structurally possible. The resolver treats the last `ACTIVE` event as eligible.

**Solution**

- require the only root state to be `DISCOVERED`;
- define an explicit allowed-transition map;
- make `REVOKED` terminal;
- require fresh admission/authorization evidence for transitions to `CANARY` or `ACTIVE`;
- add negative tests for root ACTIVE, REVOKED->ACTIVE, branching, replay, missing predecessor, and unauthorized promotion.

### WC-SEC-002 — Source-controlled ACTIVE can collapse merge vs promotion
**Severity:** CRITICAL  
**State:** Confirmed design/implementation gap in draft Registry v2.

The structural resolver uses source-controlled lifecycle `ACTIVE` directly. Without a second admission/trust-channel gate, adding a provider plus an ACTIVE event can make source merge equivalent to runtime admission.

This violates:

~~~text
merge_authority != deploy_authority
deploy_authority != canary_authority
canary_authority != stable_authority
~~~

**Solution**

Introduce a two-phase model:

1. subject PR adds immutable contract/provider/adapter records;
2. independent admission/promotion record is created only after verification and Authorization Gate;
3. the safe runtime router requires both structural eligibility and an accepted admission/trust receipt;
4. raw `resolve_capability()` remains structural only and cannot directly authorize provider execution.

### WC-SEC-003 — Active Chronos ruleset currently requires a missing check on PR #62
**Severity:** CRITICAL for controlled integration availability; HIGH for security operations  
**State:** Confirmed current GitHub state.

Ruleset `Chronos` is active and requires `github-control-plane-policy`, but PR #62 currently produces no check runs. The workflow that emits the required context exists on PR #57's branch and succeeds there, but is not present in the baseline used by #62.

**Solution**

Do not weaken the ruleset silently.

Preferred recovery:

1. prepare a minimal bootstrap Control Plane PR whose head contains the approved `github-control-plane-policy` workflow and dependencies;
2. verify that its head produces the exact required check context;
3. obtain separate merge authorization;
4. integrate the check producer before dependent protected PRs;
5. verify Chronos again via GitHub REST.

If a bootstrap PR cannot produce the check, any temporary ruleset change requires explicit repository-admin authorization, a rollback receipt, and immediate restoration. It must never be inferred from this plan.

### WC-SEC-004 — Manifest digest/revision are declarative, not proven
**Severity:** HIGH  
**State:** Confirmed.

`CapabilityManifest` validates digest syntax but does not bind the digest to the actual source bytes. `revision` is only required to be nonblank.

**Solution**

Use source-type-specific immutable provenance:

- `local`: deterministic SHA-256 tree digest recomputed in CI;
- `upstream_git` / `component_repository`: exact immutable commit SHA plus verified content digest;
- `official_plugin`: exact version/revision plus package/plugin provenance digest;
- `external_reference`: non-executable by default until independently verified.

Admission fails closed on digest mismatch or mutable source identity.

### WC-SEC-005 — No namespace ownership / contract-squatting control
**Severity:** HIGH  
**State:** Confirmed design gap.

`validate_capability_id()` verifies only broad syntax. There is no authoritative owner for `capability://<namespace>/...`, and provider IDs have no ownership binding.

**Solution**

Add append-only namespace ownership records with reserved WhiteChronos namespaces, canonical lowercase grammar, owner identity, and allowed prefixes. A contract/provider/adapter admission must prove namespace authority.

### WC-SEC-006 — Adapter authority escalation is not machine-enforced
**Severity:** HIGH  
**State:** Confirmed.

Adapters validate semantic source/target identities and lossiness but do not compare side-effect authority or provider risk. A future route could bridge a read-only consumer contract to a stronger mutating provider contract unless a higher gate catches it.

**Solution**

Define an authority lattice:

~~~text
PURE < READ_ONLY < LOCAL_MUTATING < EXTERNAL_MUTATING < CONTROL_PLANE
~~~

Require:

~~~text
authority(target_contract) <= authority(source_contract)
effective_provider_risk <= authorized_risk_ceiling
authority(adapter_output) <= authority(adapter_input)
~~~

Reject escalation during registry validation and again in the safe router.

### WC-SEC-007 — Adapter graph search has no explicit complexity budget
**Severity:** HIGH for availability  
**State:** Confirmed.

The resolver avoids cycles per path but can enumerate many simple adapter paths. A dense graph can cause combinatorial CPU/memory growth.

**Solution**

Add deterministic hard limits:

- maximum adapter hops;
- maximum graph expansions;
- maximum candidates;
- maximum start nodes;
- fail-closed `ResolutionBudgetExceeded`.

The limits belong to trusted policy, not caller-controlled request fields.

### WC-SEC-008 — Dependency scanner is not a security sandbox
**Severity:** HIGH  
**State:** Confirmed.

`capability_dependency_policy.py` scans Python AST imports and literal filesystem references. It cannot reliably catch computed paths, reflection, native code, JavaScript/shell providers, generated code, or runtime syscalls.

**Solution**

Treat the scanner as defense-in-depth only. Add:

- strict local source-root allowlisting;
- deny provider roots that overlap control-plane/governance areas;
- language-aware checks where supported;
- runtime process/workspace isolation before provider execution is ever enabled;
- scoped filesystem/network authority enforced outside provider code.

No CI scanner alone may be described as the provider security boundary.

### WC-SEC-009 — Subagent Broker repository binding violates current security contract
**Severity:** HIGH  
**State:** Confirmed on current repository source; current ChatGPT host does not expose Broker tools.

Installed Broker security policy requires explicit absolute `SUBAGENT_BROKER_REPO_ROOT` and fail-closed behavior. Current `mcp_server.mjs` derives the repository from the plugin installation directory using `discoverRepoRoot(pluginDir)`.

**Solution**

- require `SUBAGENT_BROKER_REPO_ROOT`;
- require absolute canonical path;
- require it to resolve to a Git worktree/repository;
- reject missing, relative, non-Git, or plugin-installation-derived binding;
- add MCP startup negative tests;
- never infer the consumer repo.

This should be fixed as a separate bounded Broker security change, not hidden inside the Extension Plane implementation.

### WC-SEC-010 — Raw Codex access token is allowlisted into Broker child environment
**Severity:** HIGH risk / exploitability runtime-dependent  
**State:** Confirmed code behavior.

`buildChildEnv()` forwards `CODEX_ACCESS_TOKEN` to every Codex child. The child process therefore receives a raw credential even for read-only work.

**Solution**

Prefer host-native authenticated execution that does not expose a reusable raw token to child tool processes. If the CLI absolutely requires a token:

- use the narrowest token scope and lifetime;
- prevent propagation to child shell/tool subprocesses;
- separate authentication environment from model-executed tool environment;
- redact token from every persisted stream;
- classify the Broker as credential-bearing and test credential non-disclosure.

### WC-SEC-011 — Broker cleanup trusts persisted branch metadata too far
**Severity:** MEDIUM-HIGH  
**State:** Confirmed hardening gap.

Cleanup deletes `workspace.branch` with `git branch -D` when `purgeBranch` is true. The branch normally comes from controlled creation, but persisted state is local mutable data. A corrupted state record should not be able to redirect deletion.

**Solution**

Before deletion, require:

- exact branch pattern `subagent/<agent_id>`;
- exact worktree ownership match;
- branch tip belongs to expected worktree/base lineage;
- refuse deletion on any mismatch.

### WC-SEC-012 — Risk profile is provider-declared without independent reconciliation
**Severity:** HIGH  
**State:** Confirmed design gap.

Risk fields are schema-validated but are not independently compared to source behavior.

**Solution**

For local providers, derive conservative observed-risk signals from source/package metadata and require declared risk to be equal or higher. External/opaque providers require independent security evidence. Unknown risk remains `UNKNOWN` and fails closed.

### WC-SEC-013 — Policy-and-payload can be changed together
**Severity:** HIGH  
**State:** Confirmed governance threat.

A PR that changes admission validators/workflows and adds the extension payload can attempt to weaken the validator that judges itself.

**Solution**

Implement anti-self-approval:

- security policy/schema changes and extension payload changes cannot be admitted in the same normal PR;
- run the protected/base version of admission policy against the candidate diff;
- then run the candidate policy for forward compatibility;
- governance-policy changes use a separate Control Plane change class and authorization gate.

### WC-SEC-014 — GitHub Actions use mutable major-version tags
**Severity:** HIGH supply-chain risk  
**State:** Confirmed on multiple current workflows.

Examples include `actions/checkout@v4`, `actions/setup-python@v5`, and `actions/setup-node@v4`.

**Solution**

Pin security-critical Actions to reviewed full commit SHAs, annotate the human-readable release version in comments, and use a controlled update workflow/Dependabot process. Apply this repository-wide through the existing GitHub hardening track.

### WC-SEC-015 — Lifecycle audit timestamps are not canonicalized
**Severity:** MEDIUM  
**State:** Confirmed.

Timestamp validation accepts ISO-like values without requiring timezone-aware UTC. Chain order currently uses predecessor links, but ambiguous timestamps reduce audit integrity.

**Solution**

Require canonical RFC3339 UTC timestamps and monotonic nondecreasing timestamps along each lifecycle chain. Reject future skew beyond a bounded policy window where runtime time is authoritative.

### WC-SEC-016 — Actor and evidence references are syntactically weak
**Severity:** MEDIUM  
**State:** Confirmed.

`actor_id` and `evidence_refs` are arbitrary nonblank strings. They do not prove that an authorization or verification actually exists.

**Solution**

Define typed evidence/authorization receipts bound to:

- exact subject identity/version/digest;
- Core baseline;
- action;
- actor/principal;
- verifier identity;
- commit/workflow/run evidence;
- issued/expiry timestamps where applicable;
- revocation state.

Lifecycle events reference receipt IDs, not free-form proof claims.

### WC-SEC-017 — Registry record size/graph size are not bounded
**Severity:** MEDIUM  
**State:** Confirmed hardening gap.

Schemas use `minLength` but no maximum string/array/file limits. Repository-controlled input can still create CI/runtime denial-of-service or oversized audit state.

**Solution**

Add bounded `maxLength`, `maxItems`, maximum record bytes, total-record limits, and resolver graph budgets. Extend the local schema validator to support only the additional bounded keywords actually required.

### WC-SEC-018 — Free-form adapter paths/metadata can become unsafe if later interpreted
**Severity:** MEDIUM  
**State:** Confirmed future-risk surface.

`transformation`, `conformance_tests`, `extensions`, names, reasons, and other fields are free-form data. They are currently inert, but later code could accidentally execute a path/DSL or inject content into prompts.

**Solution**

- declare these fields inert by contract;
- resolve test paths under an allowlisted repository root;
- never `eval` transformation text;
- namespace extension metadata;
- escape metadata before UI/prompt rendering;
- add size limits and secret/content rejection where global retention is involved.

### WC-SEC-019 — Caller provider preference/pin must not become authorization
**Severity:** MEDIUM  
**State:** Confirmed structural behavior, policy gap.

`preferred_provider_ids` and `provider_pin` can influence structural selection. This is valid for a resolver, but unsafe if an execution path treats caller preference as trust authority.

**Solution**

The safe router may honor preference only inside an already eligible trust/risk set. Provider pinning that lowers trust or changes authority requires its own authorization.

### WC-SEC-020 — External-reference providers can be structurally ACTIVE
**Severity:** MEDIUM  
**State:** Confirmed structural possibility.

The manifest model allows `external_reference`; structural resolver eligibility depends on lifecycle ACTIVE, not executability or host discovery.

**Solution**

Keep structural resolver pure, but safe runtime routing must require executable provider class, host availability, health, admission, and authorization. External references default to documentation/discovery-only.

### WC-SEC-021 — License status is an unverified string
**Severity:** MEDIUM  
**State:** Confirmed.

`license_status` only needs to be nonblank.

**Solution**

Use a controlled status enum plus evidence reference, SPDX expression when available, and explicit `UNKNOWN/REVIEW_REQUIRED` fail-closed states for executable admission.

### WC-SEC-022 — Capability identifiers lack strict canonical grammar
**Severity:** MEDIUM  
**State:** Confirmed.

Capability IDs reject traversal/whitespace but allow broad Unicode/punctuation/case variation that can create ambiguous identities across tools.

**Solution**

Define canonical lowercase ASCII namespace/segment grammar, bounded segment lengths, and round-trip canonicalization tests.

### WC-SEC-023 — Safe router / live security overlay is not yet implemented
**Severity:** HIGH if raw resolver were used for execution; currently implementation-gated  
**State:** Known missing first-slice capability.

The frozen design explicitly requires policy/risk gate, live quarantine/revocation overlay, host truth, and authorization separation. Tasks 1–12 are authorized but waiting for compatible runtime.

**Solution**

Do not expose provider execution before the approved bootstrap/router slice exists. Structural resolution may be developed/tested, but execution remains disabled until live security overlay and host/runtime evidence are in place.

### WC-SEC-024 — Production closure lacks a current machine-enforced four-layer health proof
**Severity:** HIGH for future production claim  
**State:** Design/implementation gap, not a false current claim.

A production system should not equate process heartbeat with system health.

**Solution**

Before `PRODUCTION COMPLETE`, require fresh passing health for:

~~~text
process
scheduler/orchestration
execution/provider path
governance/authorization gate
~~~

Missing/stale layer -> unhealthy/unknown. Keep an out-of-band operator halt/dial-down path with an independent receipt sink and measured effect SLO.

### WC-SEC-025 — Core identity should be reinforced with SHA-256 content lock
**Severity:** LOW-MEDIUM hardening  
**State:** Design improvement.

The Core is pinned to an immutable Git commit SHA, while WhiteChronos elsewhere requires SHA-256 provenance.

**Solution**

Add a Core lock manifest containing the frozen commit plus SHA-256 digests of the authoritative Core spec/governance artifacts. Extension CI verifies the locked content is unchanged.

## 5. Findings already mitigated or correctly designed

The review also confirmed several controls that are already good:

- Registry records are append-only at the source policy level.
- Registry record paths are constrained under the v2 root.
- duplicate provider/adapter identities are rejected;
- lifecycle history rejects cross-provider predecessors, branches, cycles, and unreachable events;
- missing lifecycle state is ineligible;
- quarantined adapter implementation is structurally ineligible;
- lossy adapters require explicit opt-in;
- provider source roots escaping the repository are rejected by the dependency scanner;
- Broker worktrees use safe agent IDs and scoped worktree namespaces;
- Broker process cancellation verifies Linux process identity;
- Broker state files use private directory/file modes;
- child environment is allowlisted rather than inherited wholesale;
- Chronos currently has no bypass actors and is enforced on protected refs.

These controls should be preserved while the gaps above are fixed.

## 6. Remediation tracks

### Track A — Extension Plane security hardening
Implements approved spec #62.

Priority findings:
`001, 002, 004, 005, 006, 007, 012, 013, 015-023, 025`.

Implementation plan:
`docs/superpowers/plans/2026-10-05-whitechronos-extension-plane-security-hardening.md`.

### Track B — GitHub Control Plane bootstrap
Current blocker:
`WC-SEC-003`.

Use the already-designed GitHub hardening architecture/plan. First objective is to make the required `github-control-plane-policy` context available on protected PRs without weakening Chronos.

No ruleset mutation or merge is authorized by this review.

### Track C — Broker security reconciliation
Priority findings:
`WC-SEC-009, 010, 011`.

This should be a separate bounded Superpowers/TDD change because it modifies independent runtime infrastructure.

No Broker live smoke is authorized by this review.

### Track D — Repository supply-chain hardening
Priority:
`WC-SEC-014`.

Pin Actions and verify update provenance through the existing GitHub hardening track.

### Track E — Production closure
Priority:
`WC-SEC-023, 024`.

Depends on the approved Tasks 1–12 and a compatible runtime. It does not reopen the Core.

## 7. Full Arena conclusions

Across the 16 sequential strategies, the strongest common conclusions were:

1. The Core should remain immutable; fixes belong around it, not inside it.
2. Structural resolution must never be confused with admission or execution authority.
3. Promotion evidence must be independent of the record being promoted.
4. A policy must not be allowed to rewrite itself while validating the same payload.
5. The current required-check mismatch is the first integration blocker to resolve.
6. Static source scanning is useful but cannot be the runtime security boundary.
7. Adapters are security-relevant because semantic compatibility can otherwise hide authority escalation.
8. Supply-chain identity must be content-verifiable, not a string claim.
9. Production closure must be machine-derived from fresh runtime/governance evidence.
10. Unknown or stale evidence must remain fail-closed.

## 8. Current disposition

~~~text
Core v1.0                    = SEALED / unchanged
Spec #62                     = APPROVED
Security review              = COMPLETE for inspected surfaces
Extension remediation plan   = AUTHORED on stacked plan branch
Implementation               = NOT STARTED
Merge                        = NOT AUTHORIZED
Deploy                       = NOT AUTHORIZED
Canary                       = NOT AUTHORIZED
Stable                       = NOT AUTHORIZED
Live smoke                   = NOT AUTHORIZED
PRODUCTION COMPLETE          = NOT CLAIMED
~~~
