# WhiteChronos Extension Plane Security Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved Sealed Core + Open Extension Plane so new WhiteChronos capabilities can be admitted safely without changing the frozen Core or collapsing verification, admission, promotion, and execution authority.

**Architecture:** Keep Registry v2 as the structural capability registry, add immutable Core-lock, namespace, admission, provenance, and authority controls around it, and preserve the existing resolver as structural-only. A new safe routing layer consumes structural resolution only after admission, live security, host/runtime, risk, and authorization gates pass. Admission is two-phase so a subject cannot self-promote in the same PR.

**Tech Stack:** Python 3.11+, JSON / the repository's bounded JSON-Schema subset, pytest 8.4.1, Git, GitHub Actions, existing WhiteChronos Control Plane runtime modules.

**Spec:** `docs/superpowers/specs/2026-10-05-whitechronos-sealed-core-open-extension-plane-design.md`

**Security review:** `docs/superpowers/reviews/2026-10-05-whitechronos-sealed-core-security-arena-review.md`

## Global Constraints

- Frozen Core baseline is exactly `2f6fd7a785999ef7827e74f35167a452c98d7920`.
- Approved written spec identity is `c5321b17a69148e4f48c1fe3eefd84dfde112a1c`.
- PR #59 Registry v2 interfaces are dependency input only at `09f6f3d59931e69a4c101817a687356b8dc7fcb0` or a later separately reviewed equivalent.
- The frozen Core spec is never edited in place for an extension.
- GitHub remains source-controlled authority.
- Presence in GitHub or Registry never implies admission.
- Structural resolution never implies authorization or execution.
- `VERIFIED != AUTHORIZED`.
- `AUTHORIZED != EXECUTED`.
- `EXECUTED != SUCCESSFUL`.
- `extension_admission_authority != core_change_authority`.
- `merge_authority != deploy_authority != canary_authority != stable_authority != production_closure_authority`.
- Unknown risk, provenance, compatibility, health, or authorization fails closed.
- Adapters may not increase authority.
- Revoked artifacts are never automatic fallback.
- This plan does not authorize merge, deploy, canary, stable, live smoke, R2/R3, broad credentials, or PRODUCTION COMPLETE.
- Tasks 1–12 remain on their separate authorized/runtime-gated track.
- Provider execution remains out of scope until the approved safe bootstrap/router path exists.
- The current Chronos required-check mismatch is an external integration blocker; do not weaken the ruleset from this plan.

## File Structure

### New Core/admission policy files

- `governance/WHITECHRONOS_CORE_V1_LOCK.json` — immutable Core identity and protected-authority file digests.
- `schemas/whitechronos_core_lock_v1.schema.json` — Core lock schema.
- `registry/capabilities/v2/namespace.schema.json` — namespace ownership record schema.
- `registry/capabilities/v2/admission.schema.json` — immutable extension admission receipt schema.
- `plugins/whitechronos-control-plane/runtime/extension_admission.py` — admission, namespace, receipt, and eligibility models.
- `plugins/whitechronos-control-plane/runtime/capability_authority.py` — authority/risk lattice and non-escalation checks.
- `plugins/whitechronos-control-plane/runtime/extension_router.py` — safe wrapper around structural resolver.
- `plugins/whitechronos-control-plane/runtime/provenance.py` — source-type-specific identity/digest verification.
- `pipeline/whitechronos_core_lock_gate.py` — verifies frozen Core files against the lock.
- `pipeline/capability_admission_policy.py` — two-phase admission, anti-self-approval, namespace, and base-policy checks.

### Existing files modified

- `plugins/whitechronos-control-plane/runtime/capability_model.py`
- `plugins/whitechronos-control-plane/runtime/capability_lifecycle.py`
- `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- `plugins/whitechronos-control-plane/runtime/capability_resolver.py`
- `plugins/whitechronos-control-plane/runtime/schema.py`
- `pipeline/capability_dependency_policy.py`
- `pipeline/capability_registry_policy.py`
- `.github/workflows/whitechronos-runtime-foundation.yml`
- `AGENTS.md`
- Registry v2 README/documentation.

### New/expanded tests

- `plugins/whitechronos-control-plane/tests/test_extension_admission.py`
- `plugins/whitechronos-control-plane/tests/test_capability_authority.py`
- `plugins/whitechronos-control-plane/tests/test_extension_router.py`
- `plugins/whitechronos-control-plane/tests/test_provenance.py`
- `tests/test_whitechronos_core_lock_gate.py`
- `tests/test_capability_admission_policy.py`
- existing Registry/lifecycle/resolver/dependency tests.

## Review Focus

1. **Source record says ACTIVE without an accepted admission receipt** -> structural resolver may see it, safe router must return BLOCKED.
2. **Lifecycle root ACTIVE or REVOKED -> ACTIVE** -> registry load/policy must fail closed.
3. **Adapter maps READ_ONLY consumer contract to CONTROL_PLANE target** -> admission and safe routing must reject authority escalation.
4. **Dense/cyclic adapter graph exceeds trusted budget** -> deterministic `ResolutionBudgetExceeded`, no partial winner.
5. **New record uses unowned namespace, mutable revision, or mismatched digest** -> admission policy must reject it before routing.

---

### Task 1: Freeze Core Identity With a Machine-Checked Lock

**Files:**
- Create: `schemas/whitechronos_core_lock_v1.schema.json`
- Create: `governance/WHITECHRONOS_CORE_V1_LOCK.json`
- Create: `pipeline/whitechronos_core_lock_gate.py`
- Test: `tests/test_whitechronos_core_lock_gate.py`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: `load_core_lock(path: Path) -> CoreLock`
- Produces: `verify_core_lock(repo_root: Path, lock: CoreLock) -> tuple[str, ...]`
- CLI: `python pipeline/whitechronos_core_lock_gate.py --repo . --lock governance/WHITECHRONOS_CORE_V1_LOCK.json`

- [ ] **Step 1: Write failing tests** for exact frozen commit, SHA-256 digest of the authoritative v1 Core spec, unknown lock fields, wrong digest, changed protected Core file, and a normal extension file change that does not touch protected Core content.
- [ ] **Step 2: Run RED** with `python -m pytest -q tests/test_whitechronos_core_lock_gate.py`.
- [ ] **Step 3: Add the bounded schema** with `additionalProperties: false`, exact schema/version values, exact 40-hex Git commit field, `sha256:<64 hex>` content digests, and a nonempty protected-artifact list.
- [ ] **Step 4: Add the v1 lock record** pinning `2f6fd7a785999ef7827e74f35167a452c98d7920` and the SHA-256 of the frozen Global Conversation Bootstrap design.
- [ ] **Step 5: Implement `verify_core_lock()`** so it reads protected content from the working tree, computes SHA-256, and fails when the frozen artifact changes. Do not lock ordinary extension/runtime implementation files.
- [ ] **Step 6: Add AGENTS requirement** that extension work must pass the Core lock gate and may not update the lock in the same ordinary extension PR.
- [ ] **Step 7: Run GREEN** and commit `feat: add immutable WhiteChronos core lock`.

---

### Task 2: Add Namespace Ownership and Canonical Capability Identities

**Files:**
- Create: `registry/capabilities/v2/namespace.schema.json`
- Create: `plugins/whitechronos-control-plane/runtime/extension_admission.py`
- Test: `plugins/whitechronos-control-plane/tests/test_extension_admission.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_model.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`

**Interfaces:**
- Produces: `CapabilityNamespace(namespace_id: str, owner_id: str, contract_prefixes: tuple[str, ...])`
- Produces: `validate_capability_id(value: str) -> str` with canonical lowercase ASCII grammar.
- Produces: `validate_namespace_ownership(contract_id: str, namespaces: Mapping[str, CapabilityNamespace]) -> str`.

- [ ] **Step 1: Write failing tests** for uppercase IDs, Unicode confusables, empty segments, overlong segments, unowned namespace, reserved `whitechronos` namespace impersonation, and valid owned namespace.
- [ ] **Step 2: Run RED** on the focused test.
- [ ] **Step 3: Tighten capability-id grammar** to bounded lowercase ASCII namespace/path segments without changing accepted canonical IDs already used by reviewed fixtures.
- [ ] **Step 4: Implement namespace records** as immutable source records under `registry/capabilities/v2/namespaces/`.
- [ ] **Step 5: Load namespaces before contracts/providers/adapters** and reject unowned contract namespaces.
- [ ] **Step 6: Add duplicate/prefix-overlap ownership tests** so two owners cannot claim the same protected namespace.
- [ ] **Step 7: Run GREEN** plus Registry v2 regression and commit `feat: govern capability namespaces`.

---

### Task 3: Add Immutable Extension Admission Receipts

**Files:**
- Create: `registry/capabilities/v2/admission.schema.json`
- Modify: `plugins/whitechronos-control-plane/runtime/extension_admission.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Test: `plugins/whitechronos-control-plane/tests/test_extension_admission.py`

**Interfaces:**
- Produces: `ExtensionSubject(kind: str, subject_id: str, version: str)`
- Produces: `ExtensionAdmission(admission_id: str, subject: ExtensionSubject, core_baseline: str, source_digest: str, risk_ceiling: str, authorization_ref: str, evidence_refs: tuple[str, ...])`
- Produces: `AdmissionView.by_subject: dict[ExtensionSubject, ExtensionAdmission]`
- Produces: `is_admitted(subject: ExtensionSubject, exact_digest: str, core_baseline: str) -> bool`.

- [ ] **Step 1: Write failing tests** for wrong Core baseline, wrong subject digest, missing authorization ref, duplicate admission identity, admission for missing subject, and exact accepted admission.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Add admission schema** with bounded strings/arrays and no free-form executable fields.
- [ ] **Step 4: Load admission records after structural subjects** and require exact subject/version reference.
- [ ] **Step 5: Materialize immutable admission view** without changing provider lifecycle state.
- [ ] **Step 6: Verify GREEN** and commit `feat: add extension admission receipts`.

---

### Task 4: Verify Source Provenance Instead of Trusting Manifest Strings

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/provenance.py`
- Test: `plugins/whitechronos-control-plane/tests/test_provenance.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Modify: `registry/capabilities/v2/manifest.schema.json`

**Interfaces:**
- Produces: `compute_tree_sha256(root: Path) -> str`
- Produces: `validate_source_identity(manifest: CapabilityManifest, repo_root: Path) -> ProvenanceResult`
- Produces: `ProvenanceResult(ok: bool, immutable_revision: str, digest: str, reasons: tuple[str, ...])`.

- [ ] **Step 1: Write failing tests** for mutable git revision names, local digest mismatch, local source escaping allowed provider roots, local root overlapping control-plane paths, external reference without verification evidence, and matching local digest.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement deterministic local tree hashing** with normalized relative paths, file bytes, and explicit exclusions for ephemeral VCS/runtime artifacts.
- [ ] **Step 4: Enforce source-type identity rules**: exact immutable git revision for git/component sources; exact digest for local; external references remain non-executable until separately verified.
- [ ] **Step 5: Extend manifest schema only with backward-compatible bounded validation needed for immutable identity.**
- [ ] **Step 6: Run GREEN** and commit `feat: verify extension provenance`.

---

### Task 5: Enforce Lifecycle Transition Semantics

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/capability_lifecycle.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_model.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py`

**Interfaces:**
- Produces: `can_transition(from_state: LifecycleState, to_state: LifecycleState) -> bool`
- Produces: `validate_lifecycle_chain(events: Sequence[LifecycleEvent]) -> None`.

- [ ] **Step 1: Add failing tests**: root ACTIVE rejected; root must DISCOVERED; REVOKED->ACTIVE rejected; REVOKED terminal; valid DISCOVERED->VALIDATING->COMPATIBLE; timestamp without timezone rejected; non-monotonic timestamp rejected.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement explicit transition map** with least-permissive transitions; do not create an automatic route out of REVOKED.
- [ ] **Step 4: Require canonical timezone-aware RFC3339/UTC timestamps** and nondecreasing chain time.
- [ ] **Step 5: Preserve existing branch/cycle/cross-provider checks** and run GREEN.
- [ ] **Step 6: Commit `feat: enforce capability lifecycle transitions`.

---

### Task 6: Enforce Authority and Risk Non-Escalation

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/capability_authority.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_authority.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_adapter.py`

**Interfaces:**
- Produces: `SideEffectRank` ordered as `PURE < READ_ONLY < LOCAL_MUTATING < EXTERNAL_MUTATING < CONTROL_PLANE`.
- Produces: `validate_provider_contract_risk(contract: CapabilityContract, manifest: CapabilityManifest) -> tuple[str, ...]`
- Produces: `validate_adapter_authority(source: CapabilityContract, target: CapabilityContract, adapter_provider: CapabilityManifest) -> tuple[str, ...]`.

- [ ] **Step 1: Write failing tests** for READ_ONLY->CONTROL_PLANE adapter, PURE contract backed by mutating provider, credential-bearing provider behind credential-free ceiling, and valid non-escalating adapter.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement side-effect lattice and conservative risk comparison**; UNKNOWN/inconsistent combinations fail.
- [ ] **Step 4: Validate every provider's declared risk against every provided contract** during registry load.
- [ ] **Step 5: Validate adapter source/target/provider authority** during registry load and later safe routing.
- [ ] **Step 6: Run GREEN** and commit `feat: enforce capability authority ceilings`.

---

### Task 7: Bound Adapter Resolution and Keep the Raw Resolver Structural

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/capability_resolver.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_resolver.py`

**Interfaces:**
- Produces: `ResolutionBudgetExceeded(ResolutionError)`.
- Trusted constants: `MAX_ADAPTER_HOPS`, `MAX_GRAPH_EXPANSIONS`, `MAX_CANDIDATES`.
- Preserves: `resolve_capability(registry: CapabilityRegistry, request: ResolutionRequest) -> ResolutionDecision`.

- [ ] **Step 1: Write failing tests** for graph exceeding hops, graph exceeding expansion budget, candidate explosion, deterministic result below budget, and cycle handling.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Add trusted internal budgets** that cannot be raised by untrusted caller input.
- [ ] **Step 4: Count expansions/candidates before enqueue/append** and raise deterministic fail-closed error without returning a partial winner.
- [ ] **Step 5: Document `resolve_capability` as structural-only** and ensure no execution/authorization side effect is added.
- [ ] **Step 6: Run GREEN** and commit `fix: bound capability resolver graph search`.

---

### Task 8: Add the Safe Extension Router

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/extension_router.py`
- Test: `plugins/whitechronos-control-plane/tests/test_extension_router.py`

**Interfaces:**
- Consumes: structural `ResolutionDecision`, `AdmissionView`, Core baseline, live security overlay, host capability observation, risk/authorization decision.
- Produces: `ExtensionRouteStatus = ELIGIBLE | ACTIVATION_REQUIRED | AUTHORIZATION_REQUIRED | UNAVAILABLE | BLOCKED`.
- Produces: `resolve_admitted_capability(...) -> ExtensionRouteDecision`.

- [ ] **Step 1: Write failing tests** for ACTIVE-but-unadmitted provider, admitted-but-quarantined provider, admitted provider with stale/missing host evidence, caller pin outside eligible trust set, revoked admission, authority escalation, and fully eligible read-only route.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement order**: live quarantine/revocation -> Core/admission identity -> host availability -> structural resolver -> authority/risk -> authorization requirement -> decision.
- [ ] **Step 4: Ensure provider preference/pin only ranks already eligible candidates** and never upgrades trust.
- [ ] **Step 5: Keep provider invocation absent**; this task returns a decision only.
- [ ] **Step 6: Run GREEN** and commit `feat: add security-aware extension router`.

---

### Task 9: Enforce Two-Phase Admission and Anti-Self-Approval in CI

**Files:**
- Create: `pipeline/capability_admission_policy.py`
- Test: `tests/test_capability_admission_policy.py`
- Modify: `pipeline/capability_registry_policy.py`
- Modify: `.github/workflows/whitechronos-runtime-foundation.yml`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: `classify_capability_changes(changes: Sequence[RegistryChange]) -> CapabilityChangeSet`.
- Produces: `validate_two_phase_admission(base_registry: ..., head_registry: ..., changes: CapabilityChangeSet) -> tuple[str, ...]`.
- CLI: `python pipeline/capability_admission_policy.py --repo . --base <sha> --head <sha>`.

- [ ] **Step 1: Write failing tests** for provider+admission same PR, adapter+admission same PR, ACTIVE event without admission already present in base, admission for a digest that differs from subject, gate/schema modification plus extension payload in one normal PR, and valid second-phase admission PR.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Implement two-phase diff policy** using base and head repository states; only the base can satisfy pre-existing admission prerequisites for a normal promotion.
- [ ] **Step 4: Add anti-self-approval rule**: ordinary extension payload changes cannot be combined with changes to admission policy, schemas, or protected gate workflow.
- [ ] **Step 5: Run the protected/base policy logic first** where possible, then candidate policy; a candidate may strengthen but not erase the base decision.
- [ ] **Step 6: Wire the new gate into Runtime Foundation workflow** without claiming it satisfies the repository-level `github-control-plane-policy` bootstrap issue.
- [ ] **Step 7: Run GREEN** and commit `ci: enforce two-phase extension admission`.

---

### Task 10: Harden Registry Metadata Bounds and Inert Fields

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/schema.py`
- Modify: Registry v2 schemas
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py`

**Interfaces:**
- Extend schema subset only with bounded keywords required by current records: `maxLength`, `maxItems`.
- Produces: safe repository-path validator for schema/test references.

- [ ] **Step 1: Write failing tests** for oversized IDs/reasons/evidence lists, path traversal in conformance-test refs, unknown extension namespace interpreted as executable, and bounded valid metadata.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Add `maxLength` / `maxItems` support** to the local schema validator.
- [ ] **Step 4: Bound all executable-adjacent metadata** and declare transformation/extension text inert.
- [ ] **Step 5: Validate conformance-test/schema references under allowed repository roots** without shell evaluation.
- [ ] **Step 6: Add privacy rule** that evidence refs are identifiers/locations, not conversation content or secrets.
- [ ] **Step 7: Run GREEN** and commit `fix: bound capability registry metadata`.

---

### Task 11: Strengthen Dependency Policy Without Calling It a Sandbox

**Files:**
- Modify: `pipeline/capability_dependency_policy.py`
- Modify: `tests/test_capability_dependency_policy.py`
- Modify: `registry/capabilities/README.md`

**Interfaces:**
- Produces: `validate_local_provider_root(...) -> Path`.
- Preserves: `scan_provider_boundaries(...) -> tuple[DependencyViolation, ...]`.

- [ ] **Step 1: Write failing tests** for source root equal to repository root, source root under governance/pipeline/registry/control-plane roots, symlink/alias overlap, computed-path cases that the scanner cannot prove safe, and valid isolated provider root.
- [ ] **Step 2: Run RED**.
- [ ] **Step 3: Restrict local provider roots** to explicitly allowed isolated roots and reject control-plane overlap.
- [ ] **Step 4: Add additional static checks only where deterministic**; do not attempt to prove runtime isolation from AST.
- [ ] **Step 5: Update docs**: static dependency scan is defense-in-depth, runtime sandbox/process authority is the security boundary for future execution.
- [ ] **Step 6: Run GREEN** and commit `fix: harden provider dependency boundaries`.

---

### Task 12: Define the New-System Dependency Declaration Contract

**Files:**
- Create: `schemas/whitechronos_consumer_dependency_v1.schema.json`
- Create: `pipeline/whitechronos_consumer_dependency_gate.py`
- Create: `tests/test_whitechronos_consumer_dependency_gate.py`
- Create: `docs/whitechronos-extension-consumer-contract.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Produces: `load_consumer_dependency(path: Path) -> dict[str, object]`
- Produces: `validate_consumer_dependency(document: dict[str, object]) -> tuple[str, ...]`
- CLI: `python pipeline/whitechronos_consumer_dependency_gate.py <consumer-dependency.json>`

Required declaration fields:

~~~text
consumer_id
consumer_version
whitechronos_core_baseline
consumed_contracts
required_runtime_capabilities
implementation_test_plan_ref
authorization_gate_refs
safe_degraded_behavior
~~~

- [ ] **Step 1: Write failing tests** for missing Core baseline, unknown contract, undeclared runtime dependency, missing own test-plan reference, missing Authorization Gate references, empty degraded behavior, and a valid consumer declaration.
- [ ] **Step 2: Run RED** with `python -m pytest -q tests/test_whitechronos_consumer_dependency_gate.py`.
- [ ] **Step 3: Add the bounded schema and validator**; require the frozen v1 baseline or a separately accepted later major baseline, exact capability IDs/version ranges, and nonblank safe-degraded behavior.
- [ ] **Step 4: Write the consumer contract guide** explaining that a system may evolve without waiting for unrelated Tasks 1-12, but must declare any concrete runtime dependency that does require them.
- [ ] **Step 5: Add AGENTS routing rule** requiring the declaration for new WhiteChronos-dependent systems when they are integrated with the shared capability fabric.
- [ ] **Step 6: Run GREEN** and commit `docs: define WhiteChronos consumer dependency contract`.

---

### Task 13: Full Security Regression, Arena, and Handoff

**Files:**
- Modify: `.github/workflows/whitechronos-runtime-foundation.yml` only for verified focused gates.
- Modify: security review disposition if findings close during implementation.

- [ ] **Step 1: Run focused security tests**:
  `python -m pytest -q plugins/whitechronos-control-plane/tests/test_extension_admission.py plugins/whitechronos-control-plane/tests/test_capability_authority.py plugins/whitechronos-control-plane/tests/test_extension_router.py plugins/whitechronos-control-plane/tests/test_provenance.py tests/test_whitechronos_core_lock_gate.py tests/test_capability_admission_policy.py tests/test_whitechronos_consumer_dependency_gate.py`.
- [ ] **Step 2: Run Registry/Resolver regressions**:
  `python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py plugins/whitechronos-control-plane/tests/test_capability_resolver.py tests/test_capability_registry_policy.py tests/test_capability_dependency_policy.py`.
- [ ] **Step 3: Run complete Control Plane and repository regressions**:
  `python -m pytest -q plugins/whitechronos-control-plane/tests` then `python -m pytest -q`.
- [ ] **Step 4: Run Broker compatibility regressions** without Broker live smoke:
  `node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs`.
- [ ] **Step 5: Run engineering governance**:
  `python pipeline/engineering_compatibility_gate.py`;
  `python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json`;
  their focused pytest tests.
- [ ] **Step 6: Run deterministic Core/admission/consumer CLIs** against the candidate diff; require fail-closed success with exact frozen baseline.
- [ ] **Step 7: Run Full Arena security review** over BASE..HEAD with at least the same classes as this review: lifecycle bypass, self-approval, namespace squatting, provenance substitution, adapter escalation, graph DoS, trust/pin bias, privacy leakage, and undeclared consumer dependency.
- [ ] **Step 8: Verify repository GitHub state separately**: do not mark integration-ready while protected PRs lack the required `github-control-plane-policy` check.
- [ ] **Step 9: Record remaining external blockers**: Broker repo-binding drift, Action SHA pinning, Runtime Tasks 1-12, production four-layer health.
- [ ] **Step 10: Commit only verified documentation/status updates**; do not merge, deploy, promote, run live smoke, or claim PRODUCTION COMPLETE.

## Parallel Blocking Remediation Tracks

These are real findings but intentionally not implemented by this plan because they belong to independent subsystems.

### A. GitHub Control Plane bootstrap — WC-SEC-003

Use the existing GitHub hardening design/plan. Prepare a minimal bootstrap change whose head actually emits `github-control-plane-policy` before requesting any merge into a protected target. No silent ruleset weakening.

### B. Subagent Broker security — WC-SEC-009/010/011

Separate bounded Superpowers/TDD change:

- explicit absolute `SUBAGENT_BROKER_REPO_ROOT`;
- credential-minimized child environment;
- cleanup branch identity verification.

No live smoke until separately authorized.

### C. Repository Action pinning — WC-SEC-014

Existing GitHub hardening track should pin third-party Actions to reviewed commit SHAs repository-wide.

### D. Production closure — WC-SEC-023/024

Requires Tasks 1–12 and compatible runtime. Before PRODUCTION COMPLETE, require fresh process/scheduler/execution/governance health plus Post-Verification. This does not reopen the Core.

## Self-Review Results

- **Spec coverage:** all twelve implementation controls from spec #62 Section 25 map to Tasks 1–13 above, including a dedicated consumer-dependency declaration task.
- **Security-review coverage:** every Extension Plane finding WC-SEC-001/002/004-008/012-013/015-023/025 has an owning task or an explicit parallel track.
- **Step scan:** each task has RED/GREEN verification and a commit boundary; no implementation body is pre-written.
- **Type consistency:** admission, authority, provenance, and safe-router interfaces are defined once and consumed downstream by name.
- **Review Focus:** all five high-risk classes have explicit negative tests in their owning tasks.
- **Proportion:** the plan pins interfaces, invariants, tests, and commands without transcribing the implementation.

## Execution Handoff

Recommended execution method: **Subagent-driven**, because this change touches trust, admission, lifecycle, provenance, resolver behavior, CI policy, and security invariants where an independent implementer/reviewer loop materially reduces false confidence across thirteen independently reviewable tasks.

The current ChatGPT runtime exposes no native or Broker subagent lifecycle tools. Therefore this plan must not be described as started in Subagent-driven mode from this session.

If Subagent-driven is selected, execution begins only when a real independent-agent runtime is HOST_DISCOVERED. Native execution would require a separate explicit choice for this plan.

No execution method selection grants merge, deploy, canary, stable, live smoke, R2/R3, or PRODUCTION COMPLETE authority.
