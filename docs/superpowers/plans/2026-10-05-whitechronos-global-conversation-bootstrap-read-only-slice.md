# WhiteChronos Global Conversation Bootstrap — Read-Only Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Implement the first approved WhiteChronos Global Conversation Bootstrap vertical slice so a compatible ChatGPT/Codex conversation can identify its host, load a trusted control snapshot, isolate session state, classify and authorize only R0/R1 work, resolve an eligible read-only capability, report evidence-qualified runtime state, and emit privacy-safe technical ledger metadata without granting mutation authority.

**Architecture:** Keep the approved \`Shared Core + Host-Native Bootstrap + Capability Fabric\` split. Reuse the existing Runtime Doctor and the Capability Registry/Resolver from the current Phase 2 branch, add a thin host-normalization/session/policy layer around them, and stop the first slice before generic provider execution. The slice is deliberately read-only: it proves trust, routing, isolation, evidence, and privacy boundaries before any R2/R3 Execution Lease or arbitrary provider dispatch exists.

**Tech Stack:** Python 3.11+ standard library, pytest 8.4.1, jsonschema 4.25.1, existing WhiteChronos Runtime Doctor, Capability Registry v2 / Resolver, Git, GitHub Actions, Skill Creator for the bootstrap Skill package.

**Spec:** \`docs/superpowers/specs/2026-10-05-whitechronos-global-conversation-bootstrap-design.md\`

## Execution Baseline and Dependencies

This plan is documentation-only and does not authorize merging predecessor pull requests.

Implementation MUST start from a repository state that contains all of the following:

1. the approved Design Freeze v1.0 spec from PR #60 / commit \`18ba35dee95bd58cb48444405f0498fb40abbeb8\`;
2. the Cloud Runtime Foundation currently carried by PR #57;
3. Capability Registry v2 plus the structural Capability Resolver / Adapter boundary currently carried by PR #59 at \`09f6f3d59931e69a4c101817a687356b8dc7fcb0\`, or a later reviewed descendant with equivalent interfaces.

If #57/#59 are still unmerged when implementation begins, create the implementation branch from the reviewed #59 head and include the approved spec/plan commits without changing predecessor PR state. If those PRs have already been reviewed and merged, branch from current \`main\` only after verifying that the interfaces named in this plan still exist.

Do not mark PR #57 or PR #59 ready, merge them, or broaden their scope as part of executing this plan unless separately authorized.

Before Task 1, run fresh baseline verification on the execution branch:

\`\`\`bash
python -m pytest -q plugins/whitechronos-control-plane/tests
python -m pytest -q
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
\`\`\`

Expected: all existing tests/gates pass before the first RED test for this slice. If the baseline is not green, stop this plan and use systematic debugging rather than hiding the failure inside bootstrap work.

## Global Constraints

- Preserve the frozen architecture and governance baseline; do not reopen Sections 1–9 or Section 26 while implementing this slice.
- Preserve the official governance chain: `Superpowers executes -> Arena challenges -> Verification validates -> Authorization Gate authorizes -> Executor acts -> Post-Verification confirms`.
- Preserve the state-separation invariants: `VERIFIED != AUTHORIZED`, `AUTHORIZED != EXECUTED`, and `EXECUTED != SUCCESSFUL`.
- Preserve independent authority domains: merge authority does not imply deploy authority; deploy authority does not imply canary authority; canary authority does not imply stable authority.
- GitHub/source-controlled repository state remains authoritative; a cache is last-known-trusted continuity only, never an independent control plane.
- First-slice runtime authority is limited to \`R0\` and \`R1\`; \`R2\`, \`R3\`, and \`UNKNOWN\` are blocked.
- Do not implement general-purpose mutating Execution Leases in this slice.
- Do not implement merge/send/delete/publish flows, unrestricted background autonomy, production promotion, live smoke, or broad credential creation.
- No permanent WhiteChronos superuser exists.
- Conversation/session operational state is isolated by default.
- Normal runtime/policy/registry snapshot versions are pinned per session; quarantine, revocation, emergency security state, and kill-switch state remain live.
- Adapters may not increase authority: \`authority(output) <= authority(input)\`.
- Delegated scope may only remain equal or shrink.
- Configuration does not prove host discovery; host discovery does not prove health; health does not grant authorization; authorization does not prove execution; execution does not prove success.
- Absence of current evidence yields \`UNKNOWN\`, not \`HEALTHY\`.
- No raw secrets, tokens, passwords, authorization headers, full conversation history, prompts, or message bodies may enter GitHub, cache payloads, telemetry, or the technical ledger.
- ChatGPT support means maximum product-permitted eligibility/routing, not guaranteed invocation on every turn.
- Codex \`enabled=true\` / \`multi_agent=true\` remains configuration evidence only until current-host evidence proves discovery.
- The bootstrap must stay thin and must not contain provider-specific business logic.
- Newly discovered providers remain ineligible until admitted by existing Registry/lifecycle policy.
- Do not create a generic provider executor in this slice. The deliverable stops at safe read-only route resolution plus evidence.
- Do not modify or execute vendored upstream mirrors.
- Existing Runtime Doctor live-smoke gate remains authoritative and must stay non-live in CI.

## Review Focus

The following failure modes are specifically pinned to owning-task tests below:

1. **Cross-session state bleed:** two Session Contexts must never share mutable task state or authority; Task 4 adds \`test_sessions_do_not_share_transient_state\`.
2. **Corrupt/stale cache continuity:** digest mismatch or expired trust cannot silently replace repository truth; Task 2 adds \`test_corrupt_cache_is_rejected\` and \`test_expired_cache_is_not_selected\`.
3. **Security state changes after snapshot creation:** live quarantine/revocation/kill-switch must override a still-valid pinned normal snapshot; Task 4/6 add \`test_live_security_overlay_overrides_pinned_snapshot\` and \`test_quarantine_after_snapshot_blocks_route\`.
4. **Host capability fabrication:** configured or manually activatable features must not become host-discovered/available automatically; Task 3 adds \`test_config_only_codex_feature_is_not_host_discovered\` and \`test_chatgpt_manual_activation_is_preserved\`.
5. **Content/secret leakage:** diagnostic/ledger output must reject prompt/message/secret/token fields rather than merely trusting callers; Task 8 adds \`test_ledger_rejects_content_and_secret_keys\`.

---

### Task 1: Global Bootstrap Semantic Models

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/bootstrap_model.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_bootstrap_model.py\`

**Interfaces:**
- Consumes: existing Python dataclass/Enum conventions from \`runtime/model.py\`.
- Produces:
  - \`EvidenceLevel\`
  - \`HealthState\`
  - \`HostFeatureState\`
  - \`ControlSource\`
  - \`HostFeature\`
  - \`HostCapabilityMatrix\`
  - \`ControlSnapshot\`
  - \`SecurityControlState\`
  - \`SessionSnapshot\`
  - \`SessionContext\`

- [ ] **Step 1: Write failing model tests**

Required tests:

\`\`\`python
def test_evidence_ladder_is_exact():
    assert [item.value for item in EvidenceLevel] == [
        "CONFIGURED",
        "LOCAL_RUNTIME_HEALTHY",
        "HOST_DISCOVERED",
        "LIVE_VERIFIED",
    ]

def test_host_feature_states_match_architecture():
    assert {item.value for item in HostFeatureState} == {
        "SUPPORTED",
        "AVAILABLE_ON_DEMAND",
        "MANUAL_ACTIVATION_REQUIRED",
        "AUTHORIZATION_REQUIRED",
        "UNAVAILABLE",
        "UNKNOWN",
    }

def test_session_snapshot_is_immutable_and_binds_control_versions():
    ...

def test_security_state_uses_immutable_sets():
    ...
\`\`\`

- [ ] **Step 2: Run model tests and verify RED**

Run:

\`\`\`bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_bootstrap_model.py
\`\`\`

Expected: FAIL because \`runtime/bootstrap_model.py\` does not exist.

- [ ] **Step 3: Implement exact model contracts**

Implement:

\`\`\`python
class EvidenceLevel(str, Enum): ...
class HealthState(str, Enum): ...
class HostFeatureState(str, Enum): ...
class ControlSource(str, Enum): ...

@dataclass(frozen=True)
class HostFeature:
    name: str
    state: HostFeatureState

@dataclass(frozen=True)
class HostCapabilityMatrix:
    host_id: str
    surface_id: str
    features: tuple[HostFeature, ...]
    evidence_level: EvidenceLevel
    observed_at: str

@dataclass(frozen=True)
class ControlSnapshot:
    release_id: str
    runtime_version: str
    policy_version: str
    registry_version: str
    release_channel: str
    source_commit: str
    digest: str
    source: ControlSource
    verified_at: str
    freshness_class: str

@dataclass(frozen=True)
class SecurityControlState:
    revision: str
    kill_switch_active: bool
    quarantined_provider_keys: frozenset[tuple[str, str]]
    revoked_release_ids: frozenset[str]

@dataclass(frozen=True)
class SessionSnapshot:
    session_id: str
    host_id: str
    surface_id: str
    control: ControlSnapshot
    host_capabilities: HostCapabilityMatrix
    bootstrap_evidence_refs: tuple[str, ...]

@dataclass(frozen=True)
class SessionContext:
    snapshot: SessionSnapshot
    security: SecurityControlState
\`\`\`

Validation rules: all identity/version/revision strings are nonblank; \`HostCapabilityMatrix.host_id/surface_id\` must match the Session Snapshot values; no dict/list field is retained in these frozen records.

- [ ] **Step 4: Run model tests and verify GREEN**

Run the Task 1 test file; expected PASS.

- [ ] **Step 5: Commit Task 1**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/bootstrap_model.py \
        plugins/whitechronos-control-plane/tests/test_bootstrap_model.py
git commit -m "feat: add global bootstrap semantic models"
\`\`\`

---

### Task 2: Trusted Repository Snapshot and Last-Known-Trusted Cache Selection

**Files:**
- Create: \`schemas/whitechronos_global_bootstrap_config_v1.schema.json\`
- Create: \`datacenter/WHITECHRONOS_GLOBAL_BOOTSTRAP_CONFIG.json\`
- Create: \`plugins/whitechronos-control-plane/runtime/trusted_snapshot.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_trusted_snapshot.py\`

**Interfaces:**
- Consumes: \`ControlSnapshot\`, existing schema validation helper from \`runtime/schema.py\`, Git repository HEAD.
- Produces:
  - \`SnapshotTrustError\`
  - \`load_repository_snapshot(repo_root: Path, *, now: datetime) -> ControlSnapshot\`
  - \`load_cached_snapshot(cache_root: Path, *, now: datetime, max_age_seconds: int) -> ControlSnapshot\`
  - \`select_control_snapshot(repo_root: Path, cache_root: Path | None, *, now: datetime, max_cache_age_seconds: int) -> ControlSnapshot\`

The first slice reads cache state only. It does not implement cache refresh/write/pointer promotion yet.

- [ ] **Step 1: Write failing trust/cache tests**

Required tests:

\`\`\`python
def test_repository_snapshot_is_preferred_over_cache(tmp_path):
    ...

def test_valid_cache_is_used_when_repository_snapshot_is_unavailable(tmp_path):
    ...

def test_corrupt_cache_is_rejected(tmp_path):
    ...

def test_expired_cache_is_not_selected(tmp_path):
    ...

def test_cache_never_contains_secret_fields(tmp_path):
    ...
\`\`\`

The cache fixture format must include the architecture-required identity fields: \`release_id\`, \`runtime_version\`, \`policy_version\`, \`registry_version\`, \`release_channel\`, \`source_commit\`, \`digest\`, \`verified_at\`, and \`freshness_class\`.

- [ ] **Step 2: Run trust/cache tests and verify RED**

Expected: missing module/config/schema.

- [ ] **Step 3: Add the source-controlled candidate bootstrap config**

Schema/config requirements:

- schema version is explicit;
- channel is \`candidate\` for this slice;
- no credential fields are permitted;
- no conversation/memory content fields are permitted;
- runtime/policy/registry versions are explicit;
- cache freshness threshold is configuration, not an architecture constant.

The repository snapshot digest is SHA-256 over the canonical config bytes and its \`source_commit\` is the actual Git HEAD observed at runtime.

- [ ] **Step 4: Implement read-only selection**

\`load_repository_snapshot()\` validates schema, computes digest, reads HEAD, and returns \`ControlSource.REPOSITORY\`.

\`load_cached_snapshot()\` validates the cache record, verifies its declared SHA-256 against its payload, checks age, and returns \`ControlSource.CACHE\`.

\`select_control_snapshot()\` prefers repository truth and falls back only to a still-valid cache. It never rewrites cache state.

- [ ] **Step 5: Run Task 2 tests and verify GREEN**

- [ ] **Step 6: Commit Task 2**

\`\`\`bash
git add schemas/whitechronos_global_bootstrap_config_v1.schema.json \
        datacenter/WHITECHRONOS_GLOBAL_BOOTSTRAP_CONFIG.json \
        plugins/whitechronos-control-plane/runtime/trusted_snapshot.py \
        plugins/whitechronos-control-plane/tests/test_trusted_snapshot.py
git commit -m "feat: add trusted bootstrap snapshot selection"
\`\`\`

---

### Task 3: Global Host Contract and Codex/ChatGPT Host Adapters

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/host_contract.py\`
- Create: \`plugins/whitechronos-control-plane/runtime/host_codex.py\`
- Create: \`plugins/whitechronos-control-plane/runtime/host_chatgpt.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_host_contract.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_host_codex.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_host_chatgpt.py\`

**Interfaces:**
- Consumes: Task 1 \`HostCapabilityMatrix\`, \`HostFeatureState\`, \`EvidenceLevel\`; existing Codex configuration semantics.
- Produces:
  - \`HostObservation\`
  - \`normalize_host_observation(observation: HostObservation) -> HostCapabilityMatrix\`
  - \`observe_codex_host(configured_features: dict[str, bool], host_tools: frozenset[str], *, inventory_observed: bool, surface_id: str) -> HostCapabilityMatrix\`
  - \`observe_chatgpt_host(surface_id: str, feature_states: dict[str, HostFeatureState], *, evidence_level: EvidenceLevel) -> HostCapabilityMatrix\`

- [ ] **Step 1: Write failing Host Contract tests**

Required tests include:

\`\`\`python
def test_config_only_codex_feature_is_not_host_discovered():
    ...

def test_codex_host_tools_raise_evidence_only_to_host_discovered():
    ...

def test_chatgpt_manual_activation_is_preserved():
    ...

def test_unknown_chatgpt_surface_does_not_invent_capabilities():
    ...

def test_adapter_never_promotes_evidence_without_observation():
    ...
\`\`\`

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement Host Contract normalization**

The Codex adapter may use repository config to report \`CONFIGURED\`, but only supplied current-host tool inventory may produce \`HOST_DISCOVERED\`. It may never infer \`LIVE_VERIFIED\`.

The ChatGPT adapter accepts only feature states supplied by the actual ChatGPT/product integration layer. It preserves \`MANUAL_ACTIVATION_REQUIRED\`, \`AUTHORIZATION_REQUIRED\`, \`UNAVAILABLE\`, and \`UNKNOWN\` rather than flattening them.

Neither adapter contains provider-specific business logic.

- [ ] **Step 4: Verify GREEN**

- [ ] **Step 5: Commit Task 3**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/host_contract.py \
        plugins/whitechronos-control-plane/runtime/host_codex.py \
        plugins/whitechronos-control-plane/runtime/host_chatgpt.py \
        plugins/whitechronos-control-plane/tests/test_host_contract.py \
        plugins/whitechronos-control-plane/tests/test_host_codex.py \
        plugins/whitechronos-control-plane/tests/test_host_chatgpt.py
git commit -m "feat: add global host contract adapters"
\`\`\`

---

### Task 4: Per-Conversation Session Isolation with Live Security Overlay

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/session_runtime.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_session_runtime.py\`

**Interfaces:**
- Consumes: \`ControlSnapshot\`, \`HostCapabilityMatrix\`, \`SecurityControlState\`.
- Produces:
  - \`create_session_context(control: ControlSnapshot, host: HostCapabilityMatrix, *, session_id: str, security: SecurityControlState, evidence_refs: tuple[str, ...] = ()) -> SessionContext\`
  - \`refresh_security_state(context: SessionContext, security: SecurityControlState) -> SessionContext\`

- [ ] **Step 1: Write failing isolation/security tests**

Required tests:

\`\`\`python
def test_sessions_do_not_share_transient_state():
    ...

def test_control_versions_stay_pinned_for_session():
    ...

def test_live_security_overlay_overrides_pinned_snapshot():
    ...

def test_refresh_security_state_does_not_change_host_or_control_snapshot():
    ...
\`\`\`

Use two sessions with the same normal control snapshot and prove their Session Snapshot objects and evidence refs are distinct immutable values.

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement session creation/refresh**

\`refresh_security_state()\` may only replace the live \`SecurityControlState\`; it must preserve the pinned normal Control Snapshot and Host Capability Matrix.

No cross-session lookup API is introduced.

- [ ] **Step 4: Verify GREEN**

- [ ] **Step 5: Commit Task 4**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/session_runtime.py \
        plugins/whitechronos-control-plane/tests/test_session_runtime.py
git commit -m "feat: isolate bootstrap session state"
\`\`\`

---

### Task 5: First-Slice Risk Classification and R0/R1 Policy Gate

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/bootstrap_policy.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_bootstrap_policy.py\`

**Interfaces:**
- Consumes: existing \`CapabilityContract\`, \`CapabilityManifest\`, \`SessionContext\`.
- Produces:
  - \`RiskClass\`: \`R0\`, \`R1\`, \`R2\`, \`R3\`, \`UNKNOWN\`
  - \`OperationContext\`
  - \`PolicyDecision\`
  - \`classify_risk(contract: CapabilityContract, manifest: CapabilityManifest, operation: OperationContext) -> RiskClass\`
  - \`evaluate_first_slice_policy(context: SessionContext, *, risk: RiskClass, provider_key: tuple[str, str]) -> PolicyDecision\`

\`OperationContext\` fields are exact booleans: \`network\`, \`external_read\`, \`local_mutation\`, \`external_mutation\`, \`control_plane_change\`, \`credentials\`, \`background_execution\`, \`materially_irreversible\`.

- [ ] **Step 1: Write failing policy tests**

Required tests:

\`\`\`python
def test_local_read_only_diagnostic_is_r0():
    ...

def test_external_read_without_mutation_is_r1():
    ...

def test_mutation_is_blocked_in_first_slice():
    ...

def test_irreversible_or_control_plane_operation_is_r3_and_blocked():
    ...

def test_contract_manifest_risk_contradiction_is_unknown_and_blocked():
    ...

def test_kill_switch_blocks_even_r0():
    ...

def test_revoked_release_blocks_even_r0():
    ...
\`\`\`

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement classification and policy**

Classification precedence:

1. contradictory/insufficient risk facts -> \`UNKNOWN\`;
2. \`control_plane_change\` or \`materially_irreversible\` -> \`R3\`;
3. any mutation -> \`R2\`;
4. external read/network without mutation -> \`R1\`;
5. otherwise non-mutating local diagnostic/analysis -> \`R0\`.

First-slice policy allows only R0/R1 after live security checks. R2/R3/UNKNOWN return \`allowed=False\` with a deterministic reason.

- [ ] **Step 4: Verify GREEN**

- [ ] **Step 5: Commit Task 5**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/bootstrap_policy.py \
        plugins/whitechronos-control-plane/tests/test_bootstrap_policy.py
git commit -m "feat: add read-only bootstrap policy gate"
\`\`\`

---

### Task 6: Canonical Read-Only Capability Seed and Security-Aware Route Wrapper

**Files:**
- Create: \`registry/capabilities/v2/contracts/whitechronos/runtime-doctor/1.0.0.json\`
- Create: \`registry/capabilities/v2/providers/whitechronos-runtime-doctor/0.1.0.json\`
- Create: \`registry/capabilities/v2/events/whitechronos-runtime-doctor-0.1.0-active.json\`
- Create: \`plugins/whitechronos-control-plane/runtime/bootstrap_router.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_bootstrap_router.py\`
- Modify: \`plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py\`

**Interfaces:**
- Consumes: existing \`load_capability_registry()\`, \`resolve_capability()\`, \`ResolutionRequest\`, Tasks 3–5.
- Produces:
  - \`RouteStatus\`: \`ELIGIBLE\`, \`ACTIVATION_REQUIRED\`, \`AUTHORIZATION_REQUIRED\`, \`UNAVAILABLE\`, \`BLOCKED\`
  - \`BootstrapRouteRequest\`
  - \`BootstrapRouteOutcome\`
  - \`resolve_first_slice_route(registry: CapabilityRegistry, context: SessionContext, request: BootstrapRouteRequest) -> BootstrapRouteOutcome\`

The canonical seed exists only to prove a real R0 read-only route. It does not create generic provider execution.

- [ ] **Step 1: Write failing Registry seed tests**

Assert the seeded contract:

- ID \`capability://whitechronos/runtime-doctor\`;
- version \`1.0.0\`;
- \`side_effect_class == "READ_ONLY"\`;
- provider risk has \`mutation_scope == "NONE"\`, \`external_side_effects == false\`, no credentials/background execution;
- provider lifecycle resolves to \`ACTIVE\`;
- digest/provenance fields satisfy existing Registry v2 policy.

- [ ] **Step 2: Write failing route tests**

Required tests:

\`\`\`python
def test_runtime_doctor_seed_resolves_as_r0():
    ...

def test_quarantine_after_snapshot_blocks_route():
    ...

def test_kill_switch_blocks_before_resolution():
    ...

def test_manual_activation_host_feature_is_not_auto_routed():
    ...

def test_unknown_host_feature_is_not_auto_routed():
    ...

def test_adapter_cannot_raise_side_effect_authority():
    ...

def test_unrelated_quarantine_does_not_disable_healthy_provider():
    ...
\`\`\`

- [ ] **Step 3: Verify RED**

Run Task 6 tests plus existing Registry/Resolver tests.

- [ ] **Step 4: Implement security-aware registry view and route wrapper**

Before calling \`resolve_capability()\`:

- fail immediately on global kill switch or revoked selected release;
- derive an eligible Registry view excluding currently quarantined provider/version keys;
- check required host feature states;
- preserve \`MANUAL_ACTIVATION_REQUIRED\` and \`AUTHORIZATION_REQUIRED\` as explicit outcomes;
- call the existing structural resolver;
- validate the selected direct/adapted route cannot increase side-effect authority;
- run Task 5 risk classification and first-slice policy.

Do not modify the structural resolver's existing deterministic ordering logic unless a failing test proves a bug in that component.

- [ ] **Step 5: Verify GREEN including existing resolver regression**

Run:

\`\`\`bash
python -m pytest -q \
  plugins/whitechronos-control-plane/tests/test_bootstrap_router.py \
  plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py \
  plugins/whitechronos-control-plane/tests/test_capability_resolver.py \
  plugins/whitechronos-control-plane/tests/test_capability_adapters.py
\`\`\`

- [ ] **Step 6: Commit Task 6**

\`\`\`bash
git add registry/capabilities/v2/contracts/whitechronos/runtime-doctor/1.0.0.json \
        registry/capabilities/v2/providers/whitechronos-runtime-doctor/0.1.0.json \
        registry/capabilities/v2/events/whitechronos-runtime-doctor-0.1.0-active.json \
        plugins/whitechronos-control-plane/runtime/bootstrap_router.py \
        plugins/whitechronos-control-plane/tests/test_bootstrap_router.py \
        plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
git commit -m "feat: add security-aware read-only capability route"
\`\`\`

---

### Task 7: Global Runtime Doctor Composition

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/global_doctor.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_global_doctor.py\`

**Interfaces:**
- Consumes: existing \`DoctorReport\`/Runtime Doctor evidence, Task 1 Session Context, Task 6 Route Outcome.
- Produces:
  - \`GlobalDoctorReport\`
  - \`run_global_doctor(context: SessionContext, route: BootstrapRouteOutcome, *, local_runtime_report: DoctorReport | None = None) -> GlobalDoctorReport\`
  - \`global_report_to_json(report: GlobalDoctorReport) -> dict[str, object]\`

- [ ] **Step 1: Write failing evidence/health tests**

Required tests:

\`\`\`python
def test_configured_evidence_never_becomes_host_discovered_without_observation():
    ...

def test_local_runtime_health_does_not_grant_route_authority():
    ...

def test_host_discovered_route_can_be_healthy_without_live_verified():
    ...

def test_missing_current_evidence_yields_unknown_not_healthy():
    ...

def test_quarantined_route_reports_quarantined_health():
    ...

def test_global_doctor_never_triggers_mutation_or_live_smoke(monkeypatch):
    ...
\`\`\`

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement composition**

The Global Doctor reports both evidence level and health state. It may consume existing Codex Runtime Doctor checks but does not reinterpret \`CONFIGURED\` as runtime proof.

First-slice code must not manufacture \`LIVE_VERIFIED\`; it can only preserve that level if explicitly supplied by an authoritative host observation outside this code path.

The doctor is read-only and has no repair/install/restart side effects.

- [ ] **Step 4: Verify GREEN**

- [ ] **Step 5: Commit Task 7**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/global_doctor.py \
        plugins/whitechronos-control-plane/tests/test_global_doctor.py
git commit -m "feat: compose global bootstrap runtime evidence"
\`\`\`

---

### Task 8: Privacy-Safe Technical Ledger Event Contract

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/technical_ledger.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_technical_ledger.py\`

**Interfaces:**
- Consumes: Session Snapshot, Policy Decision, Route Outcome, Global Doctor Report.
- Produces:
  - \`TechnicalLedgerEvent\`
  - \`build_technical_event(...) -> TechnicalLedgerEvent\`
  - \`technical_event_to_json(event: TechnicalLedgerEvent) -> dict[str, object]\`

No durable ledger writer is added in this slice.

- [ ] **Step 1: Write failing privacy tests**

Required tests:

\`\`\`python
def test_ledger_contains_control_metadata_only():
    ...

def test_ledger_rejects_content_and_secret_keys():
    ...

def test_ledger_has_route_risk_policy_and_evidence_references():
    ...

def test_ledger_serialization_is_deterministic():
    ...
\`\`\`

Forbidden metadata keys/patterns must include at minimum: \`content\`, \`conversation\`, \`prompt\`, \`message\`, \`secret\`, \`token\`, \`password\`, \`authorization\`, \`cookie\`, \`api_key\`.

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement allowlisted technical event construction**

The constructor accepts only technical identifiers/state plus an optional metadata mapping that is validated against forbidden key patterns. Reject unsafe metadata with \`ValueError\`; do not silently retain it.

Do not add file/database persistence yet.

- [ ] **Step 4: Verify GREEN**

- [ ] **Step 5: Commit Task 8**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/technical_ledger.py \
        plugins/whitechronos-control-plane/tests/test_technical_ledger.py
git commit -m "feat: add privacy-safe technical ledger events"
\`\`\`

---

### Task 9: End-to-End Read-Only Global Bootstrap Orchestrator and Probe CLI

**Files:**
- Create: \`plugins/whitechronos-control-plane/runtime/global_bootstrap.py\`
- Create: \`plugins/whitechronos-control-plane/scripts/global_bootstrap_probe.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_global_bootstrap.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_global_bootstrap_cli.py\`

**Interfaces:**
- Consumes: Tasks 2–8 plus \`load_capability_registry()\`.
- Produces:
  - \`GlobalBootstrapInput\`
  - \`GlobalBootstrapResult\`
  - \`run_global_bootstrap(inputs: GlobalBootstrapInput) -> GlobalBootstrapResult\`
  - CLI JSON/human report.

\`GlobalBootstrapInput\` must carry only explicit inputs: repo root, optional cache root, session ID, normalized host matrix, Security Control State, Bootstrap Route Request, current time, and max cache age.

- [ ] **Step 1: Write failing end-to-end tests**

Required tests:

\`\`\`python
def test_codex_read_only_vertical_slice_resolves_runtime_doctor(tmp_path):
    ...

def test_chatgpt_manual_activation_returns_activation_required(tmp_path):
    ...

def test_invalid_cache_plus_missing_repo_snapshot_fails_closed(tmp_path):
    ...

def test_live_quarantine_blocks_route_without_rewriting_session_snapshot(tmp_path):
    ...

def test_bootstrap_produces_privacy_safe_ledger_event(tmp_path):
    ...

def test_bootstrap_does_not_execute_provider_or_mutate_repo_or_cache(tmp_path):
    ...
\`\`\`

The last test snapshots directory contents/mtimes and monkeypatches network/subprocess provider execution entry points so any unexpected execution fails the test.

- [ ] **Step 2: Write failing CLI tests**

CLI options:

\`\`\`text
--repo <path>
--cache-root <path>
--session-id <id>
--host codex|chatgpt
--surface <id>
--host-tool <name>                 repeatable
--host-inventory-observed
--feature <name=STATE>             repeatable, for explicit ChatGPT observation
--contract <capability://...>
--version-range <range>
--required-host-feature <name>     repeatable
--max-cache-age-seconds <int>
--json
\`\`\`

Exit contract:

- \`0\`: route is \`ELIGIBLE\`;
- \`2\`: activation or authorization is required but no verified defect exists;
- \`1\`: blocked/unavailable/trust failure.

- [ ] **Step 3: Verify RED**

- [ ] **Step 4: Implement orchestration**

Exact order:

\`\`\`text
select trusted control snapshot
 -> create isolated Session Context
 -> load Capability Registry v2
 -> evaluate live Security Control State
 -> resolve first-slice route
 -> compose Global Runtime Doctor report
 -> build technical ledger event
 -> return result
\`\`\`

Do not add provider invocation after resolution.

- [ ] **Step 5: Verify GREEN**

Run both Task 9 files and all Tasks 1–8 tests.

- [ ] **Step 6: Commit Task 9**

\`\`\`bash
git add plugins/whitechronos-control-plane/runtime/global_bootstrap.py \
        plugins/whitechronos-control-plane/scripts/global_bootstrap_probe.py \
        plugins/whitechronos-control-plane/tests/test_global_bootstrap.py \
        plugins/whitechronos-control-plane/tests/test_global_bootstrap_cli.py
git commit -m "feat: add read-only global bootstrap probe"
\`\`\`

---

### Task 10: Host-Native Bootstrap Skill Package

**Files:**
- Create via Skill Creator: \`plugins/whitechronos-control-plane/skills/global-conversation-bootstrap/SKILL.md\`
- Create: \`plugins/whitechronos-control-plane/skills/global-conversation-bootstrap/agents/openai.yaml\`
- Create: \`plugins/whitechronos-control-plane/skills/global-conversation-bootstrap/references/architecture-contract.md\`
- Modify: \`plugins/whitechronos-control-plane/.codex-plugin/plugin.json\`
- Modify: \`plugins/whitechronos-control-plane/tests/test_repository_integration.py\`

**Interfaces:**
- Consumes: \`global_bootstrap_probe.py\` and the Design Freeze spec.
- Produces: a reusable bootstrap Skill eligible for Codex and ChatGPT installation where supported.

- [ ] **Step 1: Add failing repository integration tests**

Change the old assertion that the plugin exposes only Runtime Doctor. Required assertions:

- plugin version advances from \`0.1.0\` to \`0.2.0\`;
- Skill directories are exactly \`codex-runtime-doctor\` and \`global-conversation-bootstrap\`;
- bootstrap Skill states that ChatGPT invocation is product/surface dependent;
- Skill forbids full conversation/memory/repository bulk ingestion;
- Skill routes only through the probe/Shared Core and does not implement provider business logic;
- Skill states R2/R3 are out of scope for the first slice.

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Invoke Skill Creator before authoring the new Skill**

Use the installed \`skill-creator\` workflow and its initialization script for \`global-conversation-bootstrap\`. Remove generated example files not required by this approved design.

- [ ] **Step 4: Author the bootstrap Skill**

The Skill must:

- run a minimal bootstrap routing check when invoked;
- remain silent when healthy unless output is materially relevant;
- preserve higher-priority product/system/project rules;
- use host-native observation rather than inventing capabilities;
- retrieve memory/context only when materially relevant;
- never store secrets/content in ledger/cache;
- never claim guaranteed ChatGPT per-turn invocation;
- never grant mutation authority;
- preserve Runtime Doctor evidence semantics.

- [ ] **Step 5: Validate/package the Skill**

Use Skill Creator validation/package commands. The packaged artifact must contain only approved Skill files and must not be committed as a ZIP.

- [ ] **Step 6: Verify GREEN and commit**

\`\`\`bash
git add plugins/whitechronos-control-plane/skills/global-conversation-bootstrap \
        plugins/whitechronos-control-plane/.codex-plugin/plugin.json \
        plugins/whitechronos-control-plane/tests/test_repository_integration.py
git commit -m "feat: add host-native global bootstrap skill"
\`\`\`

---

### Task 11: Safe Codex User-Level Bootstrap Installer and Product-Surface Documentation

**Files:**
- Create: \`plugins/whitechronos-control-plane/scripts/install_global_bootstrap.py\`
- Create: \`plugins/whitechronos-control-plane/tests/test_install_global_bootstrap.py\`
- Create: \`docs/whitechronos-global-bootstrap.md\`

**Interfaces:**
- Produces:
  - \`InstallResult\`
  - \`install_global_bootstrap(codex_home: Path, skill_source: Path, *, dry_run: bool) -> InstallResult\`

- [ ] **Step 1: Write failing installer tests**

Required tests:

\`\`\`python
def test_installer_copies_skill_into_explicit_codex_home(tmp_path):
    ...

def test_installer_adds_bounded_idempotent_agents_block(tmp_path):
    ...

def test_installer_preserves_existing_agents_instructions(tmp_path):
    ...

def test_dry_run_changes_nothing(tmp_path):
    ...

def test_installer_never_uses_real_home_in_tests(tmp_path, monkeypatch):
    ...
\`\`\`

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Implement explicit-scope installer**

The installer:

- writes only beneath the explicitly resolved \`codex_home\`;
- installs the Skill under \`skills/global-conversation-bootstrap\`;
- manages one marker-bounded bootstrap block in \`AGENTS.md\`;
- preserves existing user instructions;
- is idempotent;
- supports \`--dry-run\`;
- does not install credentials, MCP servers, or providers;
- does not run a model task or live smoke.

- [ ] **Step 4: Document ChatGPT/Codex differences**

\`docs/whitechronos-global-bootstrap.md\` must state:

- Codex global user-level bootstrap can be installed through the reviewed installer where supported;
- ChatGPT bootstrap eligibility requires the Skill/plugin/app to be installed/available on the relevant ChatGPT surface;
- the repository cannot force invocation on 100% of ChatGPT turns;
- product/workspace permissions still govern tools/identity/authorization;
- first slice is read-only R0/R1 routing/evidence only.

- [ ] **Step 5: Verify GREEN and commit**

\`\`\`bash
git add plugins/whitechronos-control-plane/scripts/install_global_bootstrap.py \
        plugins/whitechronos-control-plane/tests/test_install_global_bootstrap.py \
        docs/whitechronos-global-bootstrap.md
git commit -m "feat: add safe Codex global bootstrap installer"
\`\`\`

---

### Task 12: CI Contract, Full Regression, and Pre-PR Verification

**Files:**
- Modify: \`.github/workflows/whitechronos-runtime-foundation.yml\`
- Modify: \`plugins/whitechronos-control-plane/tests/test_repository_integration.py\` only for CI contract assertions required by this task.

**Interfaces:**
- Consumes: all first-slice code/tests.
- Produces: deterministic CI evidence without impersonating live host/runtime verification.

- [ ] **Step 1: Write failing CI contract assertions**

Require the workflow to run:

\`\`\`bash
python -m pytest -q plugins/whitechronos-control-plane/tests
python -m pytest -q
\`\`\`

and a repository-local \`global_bootstrap_probe.py --json\` smoke using deterministic fixture/explicit host observations.

Assert CI does **not**:

- run \`SUBAGENT_BROKER_LIVE=1\`;
- run \`smoke_real_codex.mjs\`;
- write to real \`$HOME/.codex\`;
- claim \`LIVE_VERIFIED\`;
- execute a provider or external mutation.

- [ ] **Step 2: Verify RED**

- [ ] **Step 3: Extend Runtime Foundation workflow**

Add an explicit first-slice probe after tests using a clean checked-out/worktree copy and deterministic host inputs. The probe must demonstrate:

- trusted repository control snapshot selected;
- isolated Session Snapshot created;
- Runtime Doctor capability route resolves as R0/ELIGIBLE;
- evidence is no stronger than the supplied host observation;
- ledger event is emitted without content/secrets;
- no provider execution occurs;
- \`live_smoke_ready\` remains false in CI.

- [ ] **Step 4: Run focused first-slice suite**

\`\`\`bash
python -m pytest -q \
  plugins/whitechronos-control-plane/tests/test_bootstrap_model.py \
  plugins/whitechronos-control-plane/tests/test_trusted_snapshot.py \
  plugins/whitechronos-control-plane/tests/test_host_contract.py \
  plugins/whitechronos-control-plane/tests/test_host_codex.py \
  plugins/whitechronos-control-plane/tests/test_host_chatgpt.py \
  plugins/whitechronos-control-plane/tests/test_session_runtime.py \
  plugins/whitechronos-control-plane/tests/test_bootstrap_policy.py \
  plugins/whitechronos-control-plane/tests/test_bootstrap_router.py \
  plugins/whitechronos-control-plane/tests/test_global_doctor.py \
  plugins/whitechronos-control-plane/tests/test_technical_ledger.py \
  plugins/whitechronos-control-plane/tests/test_global_bootstrap.py \
  plugins/whitechronos-control-plane/tests/test_global_bootstrap_cli.py \
  plugins/whitechronos-control-plane/tests/test_install_global_bootstrap.py
\`\`\`

Expected: PASS, zero failures.

- [ ] **Step 5: Run full Control Plane and repository regression**

\`\`\`bash
python -m pytest -q plugins/whitechronos-control-plane/tests
python -m pytest -q
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
python -m pytest -q plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
python pipeline/capability_registry_policy.py --base <execution-base-sha> --head HEAD
python pipeline/capability_dependency_policy.py --repo .
\`\`\`

Expected: PASS.

- [ ] **Step 6: Run Runtime Doctor truthfulness regression**

Using fake Codex / no host inventory, verify:

- local Arena/Broker MCP checks remain truthful;
- host discovery is \`UNAVAILABLE\`, not PASS;
- \`LIVE_SMOKE_READY=false\`;
- no source mutation is recommended for host reload state.

- [ ] **Step 7: Apply final Review Arena**

Use at least four structured strategy perspectives and review:

1. session isolation and live security override;
2. cache trust / source-of-truth behavior;
3. risk classification and R2/R3 fail-closed behavior;
4. host evidence truthfulness and ChatGPT limitations;
5. adapter authority non-expansion;
6. secret/content leakage;
7. absence of arbitrary provider execution;
8. CI not impersonating live runtime.

Any material finding is fixed through a fresh RED/GREEN cycle before opening the implementation PR.

- [ ] **Step 8: Commit Task 12**

\`\`\`bash
git add .github/workflows/whitechronos-runtime-foundation.yml \
        plugins/whitechronos-control-plane/tests/test_repository_integration.py
git commit -m "ci: verify global conversation bootstrap read-only slice"
\`\`\`

---

## Self-Review Result

### Spec coverage

- Host-Native Bootstrap: Tasks 2, 3, 9, 10, 11.
- Session Snapshot / isolation: Tasks 1 and 4.
- Trusted source/cache behavior: Task 2.
- R0/R1 Policy Gate: Task 5.
- Capability Registry / Resolver integration: Task 6.
- Runtime Doctor/evidence truthfulness: Task 7.
- Codex Host Adapter: Task 3.
- ChatGPT Host Contract/Adapter boundary: Task 3 and Task 10.
- Privacy-safe technical ledger metadata: Task 8.
- First-slice end-to-end acceptance: Task 9.
- Global installation surface without overstating ChatGPT guarantees: Tasks 10–11.
- Regression/security/CI gates: Task 12.
- R2/R3, general Execution Leases, arbitrary provider execution, supply-chain promotion, circuit breakers, durable ledger storage, and production live smoke remain intentionally deferred per the spec.

No frozen architectural requirement required for the first slice is knowingly omitted.

### Type/interface consistency

The implementation chain is intentionally one-way:

\`\`\`text
bootstrap_model
 -> trusted_snapshot / host adapters
 -> session_runtime
 -> bootstrap_policy
 -> bootstrap_router
 -> global_doctor
 -> technical_ledger
 -> global_bootstrap
 -> probe CLI / Skill / installer
\`\`\`

The existing Capability Resolver remains structural and reusable; the new router wraps it rather than duplicating its ordering/version/adapter logic.

### Review-focus coverage

All five Review Focus risks have explicit named tests in Tasks 2, 3, 4, 6, and 8.

### Proportion

This plan fixes interfaces, test names, execution order, constraints, and verification gates. It deliberately does not embed full implementation bodies or reopen deferred technology choices.

## Execution Handoff

This plan should be implemented only after the spec/plan branch is reviewed and the dependency baseline is available.

**Recommended execution method: Subagent-driven development**, because the 12 tasks have clear interfaces and independent RED/GREEN/reviewer gates, while mistakes in trust, isolation, risk, or privacy boundaries would be costly to discover only at the end.

If real independent subagents are unavailable in the execution runtime, use \`superpowers:executing-plans\` rather than simulating subagents.
