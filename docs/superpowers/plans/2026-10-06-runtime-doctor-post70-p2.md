# Runtime Doctor post-PR #70 P2 remediation implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the four P2 Runtime Doctor findings raised by Codex review after PR #70 merged, without broadening scope beyond configuration eligibility and native-host discovery.

**Architecture:** Keep `runtime/doctor.py` as the single behavior surface. Tighten native lifecycle recognition so a complete lifecycle must exist in one representation (plain or one namespace), make explicit V2 precedence deterministic, and fail closed when configuration parsing or V1 feature shape is invalid. Add regression tests before implementation and preserve all existing runtime/broker/live-smoke boundaries.

**Tech Stack:** Python 3.12, `tomllib`, pytest, GitHub Actions.

**Spec:** PR #70 post-merge Codex review threads on commit `e5d039525c14cc63280720888f2e725c9efee1bd`, merged to `main` as `8a3f175b92e6355dabd8ab11f19ba93a457de059`.

## Global Constraints

- Base exactly on `main@8a3f175b92e6355dabd8ab11f19ba93a457de059`.
- Scope is limited to the four P2 findings from PR #70 review.
- TDD is mandatory: regression test first, observed RED, then minimal GREEN.
- A native lifecycle is discovered only when one complete representation is visible; partial plain/namespaced or cross-namespace unions fail closed.
- Explicit `multi_agent_v2` selection suppresses V1 effectiveness.
- A failed `.codex/config.toml` parse cannot yield `NATIVE_MULTI_AGENT_CONFIG=PASS`.
- `features.multi_agent` must be a boolean; V1 table syntax is invalid even if V2 is otherwise enabled.
- Existing V1/V2 plain and `namespace__tool` support remains intact.
- Existing Broker routing, repository binding, live-smoke criteria, and host/config evidence separation remain intact.
- No merge, deploy, canary, stable, live smoke, R2/R3, or `PRODUCTION COMPLETE`.
- Final state is a new PR only, with Full Arena review and a stop at the merge gate.

## Review Focus

1. Mixed plain + namespaced V2 tools must not synthesize a complete lifecycle.
2. Mixed `collaboration__*` + configured custom namespace tools must not synthesize a complete lifecycle.
3. Explicit V2 with V1 still enabled in TOML must report only V2 as effective.
4. TOML syntax failure must block derived native-config readiness.
5. V1 table syntax must be rejected as invalid configuration shape, including when V2 is enabled.

---

### Task 1: Add regression coverage for the four P2 findings

**Files:**
- Modify: `plugins/whitechronos-control-plane/tests/test_doctor.py`

**Interfaces:**
- Consumes: `doctor.run_doctor(DoctorInput(...))`
- Produces: failing regressions that precisely reproduce each P2.

- [ ] **Step 1: Add a test that combines partial plain/namespaced V2 inventories and requires HOST_RELOAD_REQUIRED.**
- [ ] **Step 2: Add a test that combines partial default/custom V2 namespaces and requires HOST_RELOAD_REQUIRED.**
- [ ] **Step 3: Add a test proving explicit V2 suppresses V1 effectiveness and reports eligibility via V2 only.**
- [ ] **Step 4: Add a test proving TOML parse failure cannot produce NATIVE_MULTI_AGENT_CONFIG=PASS.**
- [ ] **Step 5: Add a test proving `[features.multi_agent]` table syntax is rejected, including with V2 enabled.**
- [ ] **Step 6: Run Runtime Doctor tests and record the expected RED failures before changing production code.**

### Task 2: Enforce representation-atomic native lifecycle discovery

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/doctor.py`

**Interfaces:**
- Consumes: observed `host_tools`, V1/V2 expected lifecycle sets, known/configured namespaces.
- Produces: `HOST_NATIVE_SUBAGENT_DISCOVERY` PASS only when one plain or one namespaced representation contains the complete lifecycle.

- [ ] **Step 1: Replace per-tool cross-representation visibility with representation-level completeness evaluation.**
- [ ] **Step 2: Preserve V1 and V2 separation and existing supported `namespace__tool` forms.**
- [ ] **Step 3: Run the targeted mixed-inventory regressions and confirm GREEN.**

### Task 3: Harden native configuration eligibility

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/doctor.py`

**Interfaces:**
- Consumes: parsed TOML plus parse-success state.
- Produces: fail-closed `NATIVE_MULTI_AGENT_CONFIG` evidence.

- [ ] **Step 1: Track whether `.codex/config.toml` parsed successfully.**
- [ ] **Step 2: If parsing failed, emit non-PASS native-config status without applying defaults.**
- [ ] **Step 3: Reject non-boolean `features.multi_agent` shape.**
- [ ] **Step 4: Compute V2 effectiveness first; compute V1 effectiveness only when V2 is not selected.**
- [ ] **Step 5: Run targeted configuration regressions and confirm GREEN.**

### Task 4: Full regression and review gate

**Files:**
- No additional production surface unless a verified regression requires it.

**Interfaces:**
- Consumes: branch head after Tasks 1–3.
- Produces: verification evidence and review package for the PR.

- [ ] **Step 1: Run Runtime Foundation tests.**
- [ ] **Step 2: Run the full repository regression suite.**
- [ ] **Step 3: Run repository governance gates required by AGENTS.md.**
- [ ] **Step 4: Verify no deploy/live-smoke workflow or action was executed.**
- [ ] **Step 5: Run Full Arena with 16 strategy cards. If independent subagents are unavailable, use the documented same-model sequential adaptation and say so explicitly.**
- [ ] **Step 6: Perform final diff/constraint review and open/update the PR.**
- [ ] **Step 7: Stop at READY FOR MERGE REVIEW. Do not merge.**
