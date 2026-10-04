# GitHub Rulesets, Protected Targets, and Critical Path Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make GitHub enforce the first hardening slice: protected targets, PR-only integration, critical-path ownership/classification, and verifiable `Chronos` state, without touching Codex Cloud live execution.

**Architecture:** Add a source-controlled desired-state policy and validators, extend CODEOWNERS, and add one always-present GitHub Actions policy check. Roll `Chronos` out only after the check context exists and the live REST state matches the source policy.

**Tech Stack:** Python 3.11+, JSON, pytest 8.4.1, GitHub Actions, GitHub Rulesets REST API, CODEOWNERS.

**Spec:** `docs/superpowers/specs/2026-10-04-github-control-plane-hardening-redundancy-design.md`

## Global Constraints

- GitHub is the only Control Plane and source of truth.
- PR `#57` stays DRAFT.
- Current REST evidence still reports `Chronos` id `21770911` as `enforcement=disabled`; treat any UI activation as unverified until REST says otherwise.
- Phase 1 protects `~DEFAULT_BRANCH`, `refs/heads/spec/**`, and `refs/heads/release/**`.
- Work branches such as `feat/**`, `fix/**`, `docs/**`, `subagent/**`, and `chore/**` remain mutable.
- Solo mode: PR required; review-thread resolution required; approvals `0`; code-owner approval `false`; last-push approval `false`.
- Allowed merge methods: `squash`, `rebase`.
- Phase-1 rules: `deletion`, `non_fast_forward`, `required_linear_history`, `pull_request`, `required_status_checks`.
- Phase-1 forbidden/deferred rules: `creation`, `update`, `required_signatures`, `required_deployments`.
- Only new required check in this slice: `github-control-plane-policy`.
- Existing `runtime-foundation` and `cloud-runtime-foundation` are path-filtered and MUST NOT be universal required checks yet.
- No Codex live task, Runtime Doctor host discovery, Broker live smoke, GitHub Environment secret, or cold-mirror credential in this plan.
- Repository-admin changes happen only after policy/check tooling exists.
- If GitHub REST and UI disagree, stop and reconcile.

## Critical Path Classes

`CONTROL_PLANE_CRITICAL`: `.github/workflows/**`, `.github/CODEOWNERS`, `AGENTS.md`, `governance/**`, `pipeline/**`, `schemas/**`.
`RUNTIME_CONTROL`: `plugins/whitechronos-control-plane/**`, `plugins/subagent-broker/**`, `.codex/**`, `.agents/**`.
`DURABLE_STATE`: `memory/**`, `history/**`, `registry/**`, `datacenter/**`, `datasheet/**`.
`DOCUMENTATION`: `docs/**`, `mkdocs.yml`.
`OTHER`: everything else.

## Review Focus

1. UI says active but REST says disabled -> fail closed.
2. Empty/wrong protected-ref targeting -> fail.
3. Lockout-prone phase-1 rules remain -> fail.
4. Critical path omitted from CODEOWNERS/classifier -> fail.
5. Required check configured before its real check-run context exists -> stop.

---

### Task 1: Source-Controlled GitHub Control Plane Policy

**Files:**
- Create: `schemas/github_control_plane_policy_v1.schema.json`
- Create: `governance/GITHUB_CONTROL_PLANE_POLICY.json`
- Create: `pipeline/github_control_plane_policy_gate.py`
- Test: `tests/test_github_control_plane_policy_gate.py`

**Interfaces:**
- `load_policy(path: Path) -> dict[str, object]`
- `validate_policy(policy: dict[str, object]) -> list[str]`
- `verify_live_ruleset(policy: dict[str, object], ruleset: dict[str, object]) -> list[str]`
- CLI: `python pipeline/github_control_plane_policy_gate.py --policy <path> [--ruleset-json <path> --require-live]`

- [ ] **Step 1: Write failing tests** pinning ruleset id/name, desired `active`, exact protected refs, solo mode, forbidden rules, and required check.
- [ ] **Step 2: Verify RED** with `python -m pytest -q tests/test_github_control_plane_policy_gate.py`.
- [ ] **Step 3: Add schema + manifest** with `additionalProperties: false` and schema version `whitechronos-github-control-plane/v1`.
- [ ] **Step 4: Implement static validation** rejecting `~ALL`, duplicate/missing refs, solo-mode approval drift, merge method `merge`, missing policy check, or deferred rules.
- [ ] **Step 5: Implement live verification** for id/name/target, enforcement, ref conditions, bypass actors, rule set, PR parameters, and required check contexts; read-only only.
- [ ] **Step 6: Add edge-case tests** for disabled ruleset, empty includes, `creation`/`update`, premature signatures/deployments, missing policy check.
- [ ] **Step 7: Verify GREEN** with the test file plus the static CLI.
- [ ] **Step 8: Commit** `feat: define GitHub control-plane policy`.

---

### Task 2: Critical Path Classification and CODEOWNERS

**Files:**
- Create: `pipeline/github_path_policy.py`
- Create: `tests/test_github_path_policy.py`
- Modify: `.github/CODEOWNERS`

**Interfaces:**
- `classify_path(path: str) -> str`
- `classify_paths(paths: list[str]) -> dict[str, list[str]]`
- CLI reads newline-delimited paths and emits deterministic JSON.

- [ ] **Step 1: Write failing classifier tests** for representative paths in every class.
- [ ] **Step 2: Verify RED** with `python -m pytest -q tests/test_github_path_policy.py`.
- [ ] **Step 3: Implement classifier**; normalize separators, reject absolute/parent-traversal paths, use first-match priority, sort output.
- [ ] **Step 4: Extend CODEOWNERS** without removing existing lines:
`/memory/ @WhiteChronos`
`/history/ @WhiteChronos`
`/registry/ @WhiteChronos`
`/plugins/whitechronos-control-plane/ @WhiteChronos`
`/plugins/subagent-broker/ @WhiteChronos`
`/.codex/ @WhiteChronos`
`/.agents/ @WhiteChronos`
`/AGENTS.md @WhiteChronos`
`/.github/CODEOWNERS @WhiteChronos`
- [ ] **Step 5: Add CODEOWNERS contract tests** for every critical root.
- [ ] **Step 6: Verify GREEN**.
- [ ] **Step 7: Commit** `feat: classify and own critical GitHub paths`.

---

### Task 3: Always-Present `github-control-plane-policy` Check

**Files:**
- Create: `.github/workflows/github-control-plane-policy.yml`
- Modify: `tests/test_github_control_plane_policy_gate.py`
- Modify: `AGENTS.md`

**Interfaces:** produces check-run context `github-control-plane-policy` and consumes Tasks 1-2.

- [ ] **Step 1: Write failing workflow-contract tests** requiring `pull_request` branches `main`, `spec/**`, `release/**`, no `paths:` filter, `workflow_dispatch`, `permissions: contents: read`, Python 3.11, and no `pull_request_target`, write token, secrets, or direct push.
- [ ] **Step 2: Verify RED**.
- [ ] **Step 3: Implement workflow**: checkout, install dev requirements, run Task 1/2 tests, static policy gate, compute changed paths from merge-base, run classifier, print machine-readable result. Do not require live ruleset active yet.
- [ ] **Step 4: Update AGENTS.md** with the new required source-level validation commands.
- [ ] **Step 5: Observe the actual GitHub check-run name** before adding it to `Chronos`; if GitHub renders a different context, update the manifest.
- [ ] **Step 6: Verify GREEN** locally and in GitHub Actions.
- [ ] **Step 7: Commit** `ci: add GitHub control-plane policy check`.

---

### Task 4: Chronos Admin Runbook + Canary Verification

**Files:**
- Create: `docs/github-control-plane-admin.md`
- Modify: `tests/test_github_control_plane_policy_gate.py`

- [ ] **Step 1: Write failing runbook contract tests** requiring ruleset id `21770911`, current REST state `disabled`, exact protected refs, deferred-rule removal, solo parameters, observed policy-check context, rollback, REST verification, and PR `#57` draft instruction.
- [ ] **Step 2: Verify RED**.
- [ ] **Step 3: Write runbook**: configure refs; remove `creation`, `update`, `required_signatures`, `required_deployments`; add PR rule; add required check only after Task 3 proves it; keep bypass actors empty; activate; save; verify REST.
- [ ] **Step 4: Add rollback**: return enforcement to disabled if legitimate integration is locked out; do not add a broad bypass; capture before/after JSON.
- [ ] **Step 5: Add live verifier commands** using `GET /repos/WhiteChronos/ChatGPT/rulesets/21770911` and the Task 1 CLI.
- [ ] **Step 6: Verify active rules** for `main` and `spec/whitechronos-cloud-control-plane`, and verify `feat/cloud-runtime-foundation` is not protected by this ruleset.
- [ ] **Step 7: Verify GREEN and commit** `docs: add safe Chronos activation runbook`.

---

### Task 5: Activate and Prove Chronos — Administrative Gate

**Files:** no source mutation unless verification finds a mismatch.

- [ ] **Step 1: Re-read ruleset**. If REST already says `active`, compare to desired state first; if still `disabled`, use the runbook.
- [ ] **Step 2: Apply only runbook-approved admin changes** through GitHub Settings/UI or a future explicitly authorized admin integration.
- [ ] **Step 3: Run live verifier**; require `CHRONOS_ENFORCEMENT=ACTIVE`, protected default/spec/release coverage, and unprotected work-branch scope.
- [ ] **Step 4: Negative canary** by reading applied rules; do not attempt destructive force-push/deletion.
- [ ] **Step 5: Record non-secret evidence on PR #57**: id, timestamp, enforcement, patterns, required context, verifier result. Keep PR DRAFT.

---

### Task 6: Final Regression + Review Arena

- [ ] **Step 1: Run new gates**: `python -m pytest -q tests/test_github_control_plane_policy_gate.py tests/test_github_path_policy.py` and static policy CLI.
- [ ] **Step 2: Run engineering governance regressions**: engineering compatibility gate, Protocol Zero gate, and their tests.
- [ ] **Step 3: Run Runtime Foundation regressions**: control-plane tests, full pytest, Broker compatibility tests.
- [ ] **Step 4: Verify final GitHub checks**: `github-control-plane-policy` success; no required context that the PR cannot produce.
- [ ] **Step 5: Review Arena**: check lockout risk, critical-path bypass, status-check deadlock, work-branch scope leakage, premature signature/deployment enforcement, and unproven source claims.
- [ ] **Step 6: Commit only verified fixes** with focused messages.

## Administrative Handoff After This Plan

This plan intentionally stops before GitHub Environments, secret-scanning/push-protection, global third-party Action pinning, external cold mirror, Codex Cloud live authorization, Runtime Doctor GitHub evidence handoff, Broker live smoke, and PR #57 ready-for-review/merge.

## Self-Review Results

- **Spec coverage:** first two approved slices only: Rulesets + Protected Targets and Critical Path Ownership + Path Policy.
- **Step scan:** every source task has RED/GREEN and a commit boundary; admin activation has before/after evidence and rollback.
- **Type consistency:** Task 1 defines the policy/verifier interfaces used later.
- **Review Focus:** all five risk classes have an owning test or gate.
- **Proportion:** decisions are pinned without pre-writing implementation bodies.

## Review Arena Conclusions

1. **Systems thinking / build-then-break / completeness:** active is not enough; targeting, lockout rules, and check availability must be proven together.
2. **Constraint-first / requirements checklist / explicit trade-offs:** solo mode keeps PR traceability without fake independent approval; signatures/deployments stay deferred.
3. **Working backwards / iterative deepening:** prove the check exists before requiring it; prove protected/unprotected branch behavior before later runtime gates depend on it.
4. **Evidence-first / test-first / edge-cases-first:** GitHub REST is the automation proof source; UI statements and source manifests cannot upgrade enforcement state.