# WhiteChronos GitLab Mirror + Contingency CI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a non-authoritative GitLab mirror and contingency CI path that validates the exact same WhiteChronos commit SHA while preserving GitHub as the sole source-controlled authority.

**Architecture:** GitHub remains authoritative for repository history, PR review, rulesets, merge, and all downstream operational gates. GitLab receives one-way replicated Git objects, runs provider-scoped contingency CI against the mirrored SHA, and emits evidence that is accepted only after mirror-parity validation. Native GitLab pull mirroring is preferred when the connected tier exposes it; otherwise an independent neutral mirror worker performs one-way Git synchronization without using GitHub Actions.

**Tech Stack:** Git, Python 3.12, Node.js 22, pytest, GitHub Actions, GitLab CI/CD, GitLab project/repository APIs, JSON policy/evidence artifacts.

**Spec:** `docs/superpowers/specs/2026-10-05-whitechronos-gitlab-contingency-ci-design.md`

## Global Constraints

- WhiteChronos v1.0 Sealed Core baseline remains immutable at `2f6fd7a785999ef7827e74f35167a452c98d7920`.
- This implementation is an `ADDITIVE_EXTENSION`; no task may reinterpret a frozen Core invariant.
- GitHub remains the sole source-controlled authority.
- Mirror direction is one-way: `GitHub -> GitLab`.
- Exact immutable Git commit SHA is the cross-provider artifact identity.
- Branch names, tags, messages, or provider badges alone are never sufficient identity.
- GitLab CI evidence is provider-scoped technical evidence only.
- `CI SUCCESS != MERGE AUTHORIZED`.
- GitLab SHALL NOT receive authority to merge, deploy, canary, stable-promote, live-smoke, execute R2/R3, or declare `PRODUCTION COMPLETE`.
- `active_failover = DISABLED` throughout this plan.
- Mirror divergence fails closed: GitLab evidence becomes ineligible; GitHub authority does not change.
- Provider disagreement fails closed and requires investigation; never choose the more convenient result.
- Raw credentials SHALL NOT be committed to GitHub, GitLab, CI artifacts, logs, policy files, or evidence records.
- GitLab project provisioning, token creation, mirror activation, and pipeline activation are execution-time control-plane mutations and require separate execution authority before they occur.
- GitLab-native pull mirroring / external-repository CI is feature-gated by GitLab tier/instance configuration. Execution SHALL probe availability; if unavailable, use the neutral-worker transport defined in this plan rather than weakening the architecture.
- The neutral-worker transport SHALL NOT run inside GitHub Actions as its sole execution environment.
- Existing GitHub required checks remain required. GitLab evidence does not satisfy or replace them in this version.
- Mirror evidence freshness window is exactly **3600 seconds**.
- Accepted evidence clock skew is at most **300 seconds** into the future.
- Existing PRs #64, #65, and #66 are separate authority domains. If any are integrated before this plan executes, preserve their resulting security controls and re-run the preflight diff before Task 1.
- No merge of this plan or its future implementation is implied by plan approval.

## External References

- GitLab CI/CD for external repositories: `https://docs.gitlab.com/ci/ci_cd_for_external_repos/`
- GitLab GitHub external-CI integration: `https://docs.gitlab.com/ci/ci_cd_for_external_repos/github_integration/`
- GitLab pull mirroring: `https://docs.gitlab.com/user/project/repository/mirror/pull/`
- GitLab repository mirroring: `https://docs.gitlab.com/user/project/repository/mirror/`

## Planned File Structure

### Policy and schemas

- Create `governance/GITLAB_CONTINGENCY_CI_POLICY.json` — immutable authority/mirror/evidence policy; no secrets.
- Create `schemas/gitlab_contingency_ci.schema.json` — validates policy shape and forbidden authority escalation.
- Create `schemas/ci_provider_evidence.schema.json` — provider-scoped CI evidence contract.

### Runtime / pipeline logic

- Create `pipeline/gitlab_contingency_policy.py` — load/validate policy and classify refs.
- Create `pipeline/git_mirror_observation.py` — read-only remote-ref observation via `git ls-remote`; no provider mutation and no inline credentials.
- Create `pipeline/git_mirror_parity.py` — pure parity classifier for source SHA, mirror SHA, CI subject SHA, receipt freshness, and provider identity.
- Create `pipeline/ci_provider_evidence.py` — normalize and validate GitHub/GitLab/local evidence without inferring authority.
- Create `pipeline/contingency_ci_gate.py` — provider-neutral aggregate gate that invokes canonical repository validators and emits deterministic result metadata.
- Create `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py` — neutral-worker one-way Git synchronization with non-fast-forward divergence detection and JSON receipt output.

### CI orchestration

- Create `.gitlab-ci.yml` — GitLab contingency pipeline, thin over repository validators.
- Do not modify GitHub required-check semantics in this plan.
- Modify GitHub workflows only if necessary to consume the same provider-neutral gate; preserve any immutable Action pins present at execution time.

### Tests

- Create `tests/test_gitlab_contingency_policy.py`.
- Create `tests/test_git_mirror_observation.py`.
- Create `tests/test_git_mirror_parity.py`.
- Create `tests/test_ci_provider_evidence.py`.
- Create `tests/test_contingency_ci_gate.py`.
- Create `tests/test_gitlab_pipeline_contract.py`.
- Create `plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py`.

### Operations / evidence

- Create `docs/runbooks/gitlab-contingency-ci.md` — provisioning, tier preflight, credentials, mirror modes, outage operation, recovery, and rotation.
- Create `docs/runbooks/gitlab-contingency-drill.md` — non-production resilience drill procedure and expected evidence.

## Review Focus

1. **GitLab project exists but points at the wrong GitHub repository:** reject evidence even when the SHA string happens to match; Task 3 tests provider identity plus SHA.
2. **GitLab mirror branch diverges while pipeline remains green:** classify `MIRROR_DIVERGED` and make evidence ineligible; Tasks 3 and 7 test this.
3. **GitHub Actions is unavailable and native GitLab pull mirroring is also unavailable:** neutral worker must still preserve exact SHA without depending on Actions; Tasks 5 and 8 test the portable path.
4. **Untrusted mirrored branch attempts to expose mirror credentials:** protected credential scope and pipeline rules must keep secrets unavailable; Tasks 7 and 8 test protected/non-protected contexts.
5. **GitHub and GitLab produce opposite results for the same SHA:** normalize both results but return discrepancy/blocking state rather than override; Task 4 tests all disagreement permutations.

---

### Task 1: Add the immutable GitLab contingency policy and schema

**Files:**
- Create: `governance/GITLAB_CONTINGENCY_CI_POLICY.json`
- Create: `schemas/gitlab_contingency_ci.schema.json`
- Create: `tests/test_gitlab_contingency_policy.py`

**Interfaces:**
- Consumes: WhiteChronos Sealed Core authority invariants from the approved spec.
- Produces: `load_policy(path: Path) -> GitLabContingencyPolicy` inputs for Task 2; exact policy constants used by all later tasks.

- [ ] **Step 1: Write failing schema/policy tests**

Create tests asserting all of the following exact invariants:

```python
assert policy["schema_version"] == 1
assert policy["authority_provider"] == "github"
assert policy["mirror_direction"] == "github_to_gitlab"
assert policy["active_failover"] is False
assert policy["gitlab_merge_authority"] is False
assert policy["gitlab_deploy_authority"] is False
assert policy["source_repository"] == "WhiteChronos/ChatGPT"
assert policy["evidence_requires_exact_sha"] is True
assert policy["mirror_freshness_seconds"] == 3600
assert policy["max_clock_skew_seconds"] == 300
assert policy["provisioning_state"] == "UNPROVISIONED"
assert policy["gitlab_project_id"] is None
assert policy["gitlab_project_path"] is None
assert policy["mirror_transport"] is None
assert policy["mirror_divergence_behavior"] == "FAIL_CLOSED"
assert policy["provider_disagreement_behavior"] == "BLOCK_FOR_INVESTIGATION"
```

Also assert allowed evidence providers are exactly `github`, `gitlab`, and `local`, and allowed mirror-ref classes include `main`, `spec/*`, `plan/*`, `feat/*`, `fix/*`, and `release/*`.

- [ ] **Step 2: Run the policy tests and verify RED**

Run:

```bash
python -m pytest -q tests/test_gitlab_contingency_policy.py
```

Expected: FAIL because policy/schema files and loader do not exist.

- [ ] **Step 3: Create the schema and policy JSON**

Schema requirements:

- `additionalProperties: false`;
- explicit booleans for every authority field;
- `active_failover`, `gitlab_merge_authority`, and `gitlab_deploy_authority` constrained to `false`;
- mirror direction constrained to `github_to_gitlab`;
- source repository constrained to `WhiteChronos/ChatGPT`;
- `provisioning_state` constrained to `UNPROVISIONED | PROVISIONED`;
- nullable non-secret `gitlab_project_id`, `gitlab_project_path`, and `mirror_transport` fields;
- schema conditional: `UNPROVISIONED` requires those fields to be `null`; `PROVISIONED` requires non-empty project identity and `mirror_transport` in `gitlab_native_pull | neutral_worker`;
- `mirror_freshness_seconds` constrained to `3600`;
- `max_clock_skew_seconds` constrained to `300`;
- no fields named `token`, `password`, `secret`, or `credential`.

Policy shall define a bounded infrastructure retry limit of **2** attempts for only:

```text
PROVIDER_INFRA_FAILURE
RUNNER_ASSIGNMENT_FAILURE
```

No code/policy failure is retry-eligible by default.

- [ ] **Step 4: Add the minimal policy loader to support tests**

Create `pipeline/gitlab_contingency_policy.py` with:

```python
@dataclass(frozen=True)
class GitLabContingencyPolicy: ...

def load_policy(path: Path) -> GitLabContingencyPolicy: ...
def ref_is_mirror_eligible(ref_name: str, policy: GitLabContingencyPolicy) -> bool: ...
```

Reject missing files, invalid JSON, unknown keys, wrong authority constants, and path traversal.

- [ ] **Step 5: Run tests and verify GREEN**

Run:

```bash
python -m pytest -q tests/test_gitlab_contingency_policy.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add governance/GITLAB_CONTINGENCY_CI_POLICY.json schemas/gitlab_contingency_ci.schema.json pipeline/gitlab_contingency_policy.py tests/test_gitlab_contingency_policy.py
git commit -m "feat: define GitLab contingency policy"
```

---

### Task 2: Enforce mirror-ref eligibility and authority immutability

**Files:**
- Modify: `pipeline/gitlab_contingency_policy.py`
- Modify: `tests/test_gitlab_contingency_policy.py`

**Interfaces:**
- Consumes: `GitLabContingencyPolicy` from Task 1.
- Produces: `RefDecision(ref_name: str, eligible: bool, reason: str)` used by mirror sync in Task 5 and GitLab CI in Task 7.

- [ ] **Step 1: Add failing tests for eligible and ineligible refs**

Cover:

```text
main                         -> eligible
spec/example                 -> eligible
plan/example                 -> eligible
feat/example                 -> eligible
fix/example                  -> eligible
release/v1                   -> eligible
subagent/temp                -> ineligible
refs/pull/1/merge            -> ineligible
../main                      -> ineligible
empty ref                    -> ineligible
unknown/example              -> ineligible
```

Also test that attempting to load a policy with any authority field set to `true` raises `ValueError`.

- [ ] **Step 2: Run the tests and verify RED**

```bash
python -m pytest -q tests/test_gitlab_contingency_policy.py
```

Expected: new cases FAIL.

- [ ] **Step 3: Implement exact ref classification**

Add:

```python
@dataclass(frozen=True)
class RefDecision:
    ref_name: str
    eligible: bool
    reason: str

def classify_ref(ref_name: str, policy: GitLabContingencyPolicy) -> RefDecision: ...
```

Normalize only a leading `refs/heads/`; do not normalize path traversal or unknown namespaces into acceptable refs.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest -q tests/test_gitlab_contingency_policy.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/gitlab_contingency_policy.py tests/test_gitlab_contingency_policy.py
git commit -m "feat: enforce GitLab mirror ref policy"
```

---

### Task 3: Build remote-ref observation and the mirror-parity gate

**Files:**
- Create: `pipeline/git_mirror_observation.py`
- Create: `pipeline/git_mirror_parity.py`
- Create: `tests/test_git_mirror_observation.py`
- Create: `tests/test_git_mirror_parity.py`

**Interfaces:**
- Consumes: a public/noncredentialed remote URL, eligible ref, provider identities, exact SHAs, sync receipt timestamp, and policy.
- Produces: `RemoteRefObservation(remote_url, ref_name, sha, observed_at, available)` and `MirrorParityResult(status, evidence_eligible, reason)` where status is one of `HEALTHY`, `STALE`, `DIVERGED`, `UNAVAILABLE`.

- [ ] **Step 1: Write failing remote-observation and parity tests**

For remote observation, use temporary local bare repositories to assert exact SHA lookup, missing ref -> unavailable, malformed output -> failure, and rejection of HTTPS URLs containing inline credentials.

For parity, define tests for:

```python
HEALTHY: github_sha == gitlab_sha == ci_subject_sha and identities match
DIVERGED: same ref name but github_sha != gitlab_sha
DIVERGED: gitlab_sha != ci_subject_sha
DIVERGED: wrong GitHub repository identity
DIVERGED: wrong GitLab project identity
STALE: receipt age exceeds policy freshness window
UNAVAILABLE: a required provider observation is absent
```

For every state except `HEALTHY`:

```python
assert result.evidence_eligible is False
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q tests/test_git_mirror_observation.py tests/test_git_mirror_parity.py
```

Expected: FAIL because module does not exist.

- [ ] **Step 3: Implement read-only remote observation and the pure parity classifier**

Create in `pipeline/git_mirror_observation.py`:

```python
@dataclass(frozen=True)
class RemoteRefObservation: ...

def observe_remote_ref(remote_url: str, ref_name: str) -> RemoteRefObservation: ...
```

Use `subprocess.run(["git", "ls-remote", "--exit-code", remote_url, full_ref], ...)`; never use `shell=True`, never mutate a provider, and reject inline HTTPS credentials before invoking Git.

Create in `pipeline/git_mirror_parity.py`:

```python
class MirrorParityStatus(StrEnum):
    HEALTHY = "HEALTHY"
    STALE = "STALE"
    DIVERGED = "DIVERGED"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass(frozen=True)
class MirrorParityInput: ...

@dataclass(frozen=True)
class MirrorParityResult: ...

def evaluate_mirror_parity(value: MirrorParityInput, policy: GitLabContingencyPolicy) -> MirrorParityResult: ...
```

No network access and no provider mutation in this module.

- [ ] **Step 4: Add deterministic JSON CLI**

Observation CLI:

```bash
python pipeline/git_mirror_observation.py --remote-url https://github.com/WhiteChronos/ChatGPT.git --ref main --json
```

Parity CLI:

```bash
python pipeline/git_mirror_parity.py --input evidence.json --json
```

Exit semantics:

```text
0 = HEALTHY
2 = STALE
3 = DIVERGED
4 = UNAVAILABLE
1 = invalid input/internal error
```

- [ ] **Step 5: Verify GREEN**

```bash
python -m pytest -q tests/test_git_mirror_observation.py tests/test_git_mirror_parity.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/git_mirror_observation.py pipeline/git_mirror_parity.py tests/test_git_mirror_observation.py tests/test_git_mirror_parity.py
git commit -m "feat: add Git mirror parity gate"
```

---

### Task 4: Add provider-scoped CI evidence and discrepancy classification

**Files:**
- Create: `schemas/ci_provider_evidence.schema.json`
- Create: `pipeline/ci_provider_evidence.py`
- Create: `tests/test_ci_provider_evidence.py`

**Interfaces:**
- Consumes: provider result, exact subject SHA, config revision, parity result, timestamps.
- Produces: deterministic `CIProviderEvidence` and `EvidenceComparison` values; never produces authorization.

- [ ] **Step 1: Write failing evidence tests**

Required evidence fields:

```text
provider
repository_identity
subject_sha
pipeline_or_run_id
gate_name
result
timestamp
ci_config_revision
mirror_parity_status
attempt
```

Test:

```python
gitlab_pass.merge_authorized is False
gitlab_pass.deploy_authorized is False
```

If those fields do not exist in the runtime type, assert serialization contains no authority grant fields.

Test comparison matrix:

```text
GitHub PASS + GitLab PASS         -> CORROBORATED
GitHub PASS + GitLab FAIL         -> DISCREPANCY_BLOCKED
GitHub FAIL + GitLab PASS         -> DISCREPANCY_BLOCKED
GitHub unavailable + GitLab PASS  -> CONTINGENCY_EVIDENCE_ONLY
mirror != HEALTHY                 -> GITLAB_EVIDENCE_INELIGIBLE
different subject SHA             -> SUBJECT_MISMATCH_BLOCKED
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q tests/test_ci_provider_evidence.py
```

Expected: FAIL.

- [ ] **Step 3: Implement evidence normalization**

Create:

```python
@dataclass(frozen=True)
class CIProviderEvidence: ...

class EvidenceDisposition(StrEnum): ...

def validate_evidence(record: CIProviderEvidence) -> None: ...
def compare_provider_evidence(github: CIProviderEvidence | None, gitlab: CIProviderEvidence | None) -> EvidenceComparison: ...
```

Reject unknown provider names, malformed SHAs, timestamps more than **300 seconds** into the future, parity-ineligible GitLab records, and mismatched subjects.

- [ ] **Step 4: Add JSON schema validation tests**

Schema shall reject unknown fields and any attempted authority field such as `merge_authorized: true`.

- [ ] **Step 5: Verify GREEN**

```bash
python -m pytest -q tests/test_ci_provider_evidence.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add schemas/ci_provider_evidence.schema.json pipeline/ci_provider_evidence.py tests/test_ci_provider_evidence.py
git commit -m "feat: add provider scoped CI evidence"
```

---

### Task 5: Implement the independent one-way mirror worker

**Files:**
- Create: `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py`
- Create: `plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py`

**Interfaces:**
- Consumes: source Git remote, GitLab target Git remote, one eligible ref, Task 2 ref policy.
- Produces: exact GitLab ref with the same commit SHA plus a JSON sync receipt; never changes GitHub.

- [ ] **Step 1: Write failing integration tests using local bare repositories**

Build local temporary Git repositories and assert:

1. fast-forward source update is copied to target with the same SHA;
2. target non-fast-forward divergence is rejected before overwrite;
3. ineligible ref is rejected;
4. source SHA and target SHA in receipt are equal after success;
5. target remote URL containing HTTPS inline credentials is rejected from receipt/log output;
6. no `git push --force` is issued in normal mode;
7. source repository is never mutated.

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
```

Expected: FAIL because script does not exist.

- [ ] **Step 3: Implement the mirror worker**

CLI:

```text
sync_gitlab_mirror.py
  --repo-root PATH
  --source-url URL
  --target-url URL
  --ref NAME
  --receipt PATH
  [--dry-run]
```

Implementation requirements:

- create a temporary bare repository;
- fetch only the requested eligible ref from GitHub;
- resolve exact source SHA;
- query target ref first;
- reject non-fast-forward divergence;
- push without force;
- query target ref again;
- require exact SHA equality;
- write deterministic JSON receipt with identities, ref, source SHA, target SHA, timestamp, and transport `neutral_worker`;
- redact credential material from all errors/output;
- never accept tokens via command-line flags.

Authentication SHALL be supplied through an external Git credential helper / approved environment mechanism, not persisted by this script.

- [ ] **Step 4: Verify GREEN**

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
```

Expected: PASS.

- [ ] **Step 5: Run focused security assertions**

```bash
grep -R --line-number --fixed-strings "git push --force" plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py && exit 1 || true
python -m pytest -q plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
```

Expected: no force-push string; tests PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
git commit -m "feat: add independent GitLab mirror worker"
```

---

### Task 6: Create a provider-neutral contingency validation gate

**Files:**
- Create: `pipeline/contingency_ci_gate.py`
- Create: `tests/test_contingency_ci_gate.py`

**Interfaces:**
- Consumes: repository root and named validation profile.
- Produces: deterministic gate result JSON for `python-governance`, `broker`, or `full-contingency`.

- [ ] **Step 1: Write failing tests for the command catalog**

The catalog must call existing canonical repository validators rather than reimplement their rules.

Required `python-governance` commands:

```text
python -m pytest -q
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
```

Required `broker` command:

```text
node --test plugins/subagent-broker/tests/*.test.mjs
```

`full-contingency` is the union of both profiles.

Tests shall assert no command contains `git push`, deployment tooling, canary/stable promotion, or live-smoke flags.

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q tests/test_contingency_ci_gate.py
```

Expected: FAIL.

- [ ] **Step 3: Implement gate orchestration**

Create:

```python
@dataclass(frozen=True)
class GateCommand: ...
@dataclass(frozen=True)
class GateResult: ...

def commands_for_profile(profile: str) -> tuple[GateCommand, ...]: ...
def run_profile(repo_root: Path, profile: str) -> GateResult: ...
```

Use `subprocess.run(..., check=False)` with argv arrays, not `shell=True`.

Stop the profile at the first command failure and record the failed command index/result.

- [ ] **Step 4: Add dry-run JSON mode**

```bash
python pipeline/contingency_ci_gate.py --profile full-contingency --dry-run --json
```

Expected: exit 0 and deterministic command catalog JSON without executing tests.

- [ ] **Step 5: Verify GREEN**

```bash
python -m pytest -q tests/test_contingency_ci_gate.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/contingency_ci_gate.py tests/test_contingency_ci_gate.py
git commit -m "feat: add provider neutral contingency gate"
```

---

### Task 7: Add GitLab contingency pipeline orchestration

**Files:**
- Create: `.gitlab-ci.yml`
- Create: `tests/test_gitlab_pipeline_contract.py`

**Interfaces:**
- Consumes: exact mirrored commit, Task 3 parity gate, Task 6 validation profiles.
- Produces: GitLab pipeline jobs and provider-scoped evidence artifacts; no authority mutation.

- [ ] **Step 1: Write failing static contract tests**

Assert `.gitlab-ci.yml`:

- exists;
- defines `mirror-parity`, `python-governance`, `broker`, and `contingency-evidence` jobs;
- contains no deployment stage;
- contains no `environment:` deployment target;
- contains no merge command;
- contains no force push;
- calls `pipeline/git_mirror_observation.py` to observe the authoritative GitHub ref;
- calls `pipeline/git_mirror_parity.py`;
- calls `pipeline/contingency_ci_gate.py`;
- emits `ci-provider-evidence.json`;
- references only approved CI variable names and never literal secret values; protected/masked configuration is verified operationally in Task 8;
- pins every container image by digest using `@sha256:`.

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q tests/test_gitlab_pipeline_contract.py
```

Expected: FAIL because `.gitlab-ci.yml` does not exist.

- [ ] **Step 3: Resolve and pin the CI images**

Use official base images only.

Resolve immutable digests for:

- Python 3.12 job image;
- Node.js 22 job image.

Record the exact digest in `.gitlab-ci.yml` and a comment with the human-readable upstream tag. Do not use mutable tag-only images.

- [ ] **Step 4: Implement pipeline workflow rules**

Run only for mirrored branch pushes, schedules, or explicit web/API starts. Do not treat GitLab merge requests as authoritative triggers.

Required stages:

```text
parity
validate
evidence
```

`mirror-parity` first observes `https://github.com/WhiteChronos/ChatGPT.git` for the current mirrored ref, then compares that observed SHA with `$CI_COMMIT_SHA` and the configured project identity. If GitHub itself is unavailable, observation returns `UNAVAILABLE`; validation jobs may still run for diagnostic value but resulting GitLab evidence is ineligible for normal cross-provider corroboration.

`python-governance` and `broker` SHALL run after the `mirror-parity` job completes, including when parity is `UNAVAILABLE`, so the mirrored SHA can still receive diagnostic validation during a complete GitHub outage. Configure downstream jobs with `needs` plus `when: always` (or the GitLab equivalent that preserves this behavior); they SHALL NOT infer evidence eligibility from job scheduling.

`contingency-evidence` is the eligibility decision point. It serializes provider-scoped evidence and marks it eligible only when `mirror_parity_status == HEALTHY` and the validation result is PASS. `STALE`, `DIVERGED`, and `UNAVAILABLE` may retain diagnostic test results but MUST serialize ineligible / `CONTINGENCY_EVIDENCE_ONLY` state rather than `CORROBORATED`.

- [ ] **Step 5: Add artifact retention without secrets**

Artifacts may include:

- `mirror-parity.json`;
- `contingency-gate.json`;
- `ci-provider-evidence.json`.

Artifacts SHALL NOT include environment dumps or token-bearing configuration.

- [ ] **Step 6: Verify static contract**

```bash
python -m pytest -q tests/test_gitlab_pipeline_contract.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add .gitlab-ci.yml tests/test_gitlab_pipeline_contract.py
git commit -m "ci: add GitLab contingency pipeline"
```

---

### Task 8: Add GitLab project provisioning and mirror-mode runbook

**Files:**
- Create: `docs/runbooks/gitlab-contingency-ci.md`
- Modify: `governance/GITLAB_CONTINGENCY_CI_POLICY.json` only after execution-time project identity is known.
- Modify: `tests/test_gitlab_contingency_policy.py` to require the recorded non-secret project identity after provisioning.

**Interfaces:**
- Consumes: authenticated GitLab environment and separate execution authorization.
- Produces: one non-authoritative GitLab project identity plus selected mirror transport mode.

- [ ] **Step 1: Document execution-time preflight**

The runbook must verify:

```text
GitLab authenticated
project creation permitted
shared or approved runner available
native pull-mirror feature available? yes/no
external-repository CI feature available? yes/no
GitHub source repository reachable
no existing WhiteChronos mirror with conflicting identity
current connector/runtime has a project-creation action? yes/no
```

If no project-creation action exists in the connected GitLab tooling, provisioning is an explicit human/operator GitLab UI/CLI/API step under the same separate execution authorization; do not fabricate a connector mutation.

- [ ] **Step 2: Define exact project security posture**

Provision as a **private non-authoritative mirror project** unless the user separately authorizes different visibility.

Required posture:

- GitLab merge requests disabled for authoritative development;
- issues/wiki/snippets disabled unless needed later;
- default branch protected;
- direct human development on mirror refs prohibited by policy;
- no GitHub branch-write credential stored in GitLab;
- GitLab mirror service credential is scoped to only the mirror project and expires/rotates;
- protected/masked CI variables for any GitLab write credential;
- no deployment credentials.

- [ ] **Step 3: Define deterministic transport selection**

Selection logic:

```text
IF GitLab native pull mirroring is available:
    mirror_transport = gitlab_native_pull
ELSE:
    mirror_transport = neutral_worker
```

No third behavior and no automatic bidirectional mirror.

For `gitlab_native_pull`, enable pipeline triggering for mirror updates and disable any GitLab-to-GitHub push mirror.

For `neutral_worker`, use Task 5 script from an independent host; GitHub Actions is not an acceptable sole host.

- [ ] **Step 4: Record provider identity after provisioning**

After separate execution authority creates the project, set `provisioning_state = PROVISIONED` and update only non-secret policy identity fields with the exact returned GitLab project path/ID and selected transport. The schema conditional must reject `PROVISIONED` with missing identity/transport and reject `UNPROVISIONED` with populated identity/transport.

Run:

```bash
python -m pytest -q tests/test_gitlab_contingency_policy.py
```

Expected: PASS.

- [ ] **Step 5: Commit the runbook and recorded non-secret identity**

```bash
git add docs/runbooks/gitlab-contingency-ci.md governance/GITLAB_CONTINGENCY_CI_POLICY.json tests/test_gitlab_contingency_policy.py
git commit -m "docs: define GitLab contingency operations"
```

**Gate:** This task's provisioning steps MUST NOT execute until the user separately authorizes implementation/control-plane mutation. During plan review, only the runbook text is authored.

---

### Task 9: Add infrastructure retry and disagreement handling

**Files:**
- Modify: `pipeline/ci_provider_evidence.py`
- Modify: `tests/test_ci_provider_evidence.py`
- Create: `docs/runbooks/gitlab-contingency-drill.md`

**Interfaces:**
- Consumes: Task 4 evidence plus failure classification.
- Produces: bounded retry decision and a resilience-drill procedure; does not execute retries automatically across authority boundaries.

- [ ] **Step 1: Write failing retry-policy tests**

Exact matrix:

```text
PROVIDER_INFRA_FAILURE     attempt 1 -> RETRY_ELIGIBLE
RUNNER_ASSIGNMENT_FAILURE attempt 1 -> RETRY_ELIGIBLE
PROVIDER_INFRA_FAILURE     attempt 2 -> RETRY_LIMIT_REACHED
CODE_FAILURE               attempt 1 -> NOT_RETRY_ELIGIBLE
POLICY_FAILURE             attempt 1 -> NOT_RETRY_ELIGIBLE
MIRROR_FAILURE             attempt 1 -> NOT_RETRY_ELIGIBLE
UNKNOWN                    attempt 1 -> NOT_RETRY_ELIGIBLE
```

- [ ] **Step 2: Run and verify RED**

```bash
python -m pytest -q tests/test_ci_provider_evidence.py
```

Expected: new cases FAIL.

- [ ] **Step 3: Implement bounded retry classification**

Add:

```python
class FailureClass(StrEnum): ...
class RetryDisposition(StrEnum): ...

def classify_retry(failure: FailureClass, attempt: int, policy: GitLabContingencyPolicy) -> RetryDisposition: ...
```

This function only returns a decision; it does not call provider APIs or mutate runs.

- [ ] **Step 4: Write the non-production resilience drill**

The drill shall simulate:

1. GitHub Actions runner assignment unavailable;
2. GitHub repository still reachable;
3. exact SHA mirrored to GitLab;
4. GitLab parity `HEALTHY`;
5. GitLab CI `PASS`;
6. resulting state `CONTINGENCY_EVIDENCE_ONLY`;
7. merge authority remains not granted.

A second scenario shall inject GitLab mirror divergence and require evidence rejection.

No production deploy or live smoke appears in the drill.

- [ ] **Step 5: Verify GREEN**

```bash
python -m pytest -q tests/test_ci_provider_evidence.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/ci_provider_evidence.py tests/test_ci_provider_evidence.py docs/runbooks/gitlab-contingency-drill.md
git commit -m "feat: classify contingency retries and drills"
```

---

### Task 10: Cross-provider regression, security review, and implementation handoff

**Files:**
- Modify only if findings require fixes: files from Tasks 1–9.
- Add review evidence under: `docs/superpowers/reviews/2026-10-05-whitechronos-gitlab-contingency-ci-review.md`

**Interfaces:**
- Consumes: all Task 1–9 deliverables.
- Produces: review evidence and a verified implementation branch ready for a separate merge-authorization gate.

- [ ] **Step 1: Run focused GitLab contingency tests**

```bash
python -m pytest -q   tests/test_gitlab_contingency_policy.py   tests/test_git_mirror_parity.py   tests/test_ci_provider_evidence.py   tests/test_contingency_ci_gate.py   tests/test_gitlab_pipeline_contract.py   plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
```

Expected: PASS.

- [ ] **Step 2: Run repository regression**

```bash
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 3: Run canonical governance gates**

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Expected: all PASS.

- [ ] **Step 4: Run Broker regression**

```bash
node --test plugins/subagent-broker/tests/*.test.mjs
```

Expected: PASS.

- [ ] **Step 5: Perform security-specific static checks**

Verify:

- no committed token/secret literals;
- no bidirectional/push-back mirror;
- no normal force push;
- no GitLab deploy environment;
- no `active_failover: true`;
- no GitLab merge/deploy authority grant;
- no pipeline path can emit eligible GitLab evidence when parity is not `HEALTHY`;
- no retry of code/policy/mirror/unknown failures;
- every image in `.gitlab-ci.yml` is digest-pinned.

- [ ] **Step 6: Perform Review Arena**

Use four materially different review lenses:

1. systems/blast-radius;
2. authority and trust-boundary constraints;
3. recovery/operational continuity;
4. evidence/test/edge-case correctness.

Record findings, severity, disposition, and exact verification evidence in the review document.

- [ ] **Step 7: Verify Core and authority separation**

Explicitly record:

```text
sealed_core_sha        = 2f6fd7a785999ef7827e74f35167a452c98d7920
core_modified          = NO
github_authority       = AUTHORITATIVE
gitlab_authority       = NONE
active_failover        = DISABLED
merge_authority        = NOT_GRANTED_BY_IMPLEMENTATION
deploy_authority       = NOT_GRANTED_BY_IMPLEMENTATION
production_complete    = NO
```

- [ ] **Step 8: Commit final review evidence**

```bash
git add docs/superpowers/reviews/2026-10-05-whitechronos-gitlab-contingency-ci-review.md
git commit -m "docs: review GitLab contingency CI implementation"
```

- [ ] **Step 9: Stop at the merge authorization gate**

Do not merge.

Report:

```text
IMPLEMENTATION VERIFIED != MERGE AUTHORIZED
```

The next step requires a separate explicit user authorization for merge. Deploy, canary, stable, live smoke, R2/R3, and production closure remain separate even after any future merge.

## Plan Self-Review

### Spec coverage

- GitHub sole authority: Tasks 1, 4, 8, 10.
- One-way mirror: Tasks 2, 5, 8.
- Exact SHA parity: Tasks 3, 5, 7.
- Divergence fail-closed: Tasks 3, 5, 9.
- Shared canonical validation logic: Tasks 6 and 7.
- Provider-scoped evidence: Task 4.
- GitLab outage / GitHub Actions degradation behavior: Tasks 7, 8, 9.
- No authority grant from GitLab CI: Tasks 1, 4, 10.
- Secret isolation: Tasks 5, 7, 8, 10.
- Public/untrusted-code safety: Tasks 7 and 8.
- Future active failover disabled: Tasks 1, 10.
- Resilience drill: Task 9.
- Sealed Core preservation: Task 10.

No spec requirement is intentionally omitted.

### Type consistency

- `GitLabContingencyPolicy` originates in Task 1, including `provisioning_state` and `mirror_transport`, and is consumed by Tasks 2, 3, 8, 9.
- `RemoteRefObservation` originates in Task 3 and is consumed by the GitLab parity job in Task 7.
- `RefDecision` originates in Task 2 and is consumed by Task 5.
- `MirrorParityResult` originates in Task 3 and is consumed by Tasks 4 and 7.
- `CIProviderEvidence` / `EvidenceComparison` originate in Task 4 and are extended in Task 9.
- `GateResult` originates in Task 6 and is consumed by Task 7.

### Execution boundary

This plan is now an implementation description only. Plan approval does **not** authorize any Task 1–10 execution, GitLab provisioning, credentials, mirror activation, CI activation, merge, deploy, canary, stable, live smoke, R2/R3, or `PRODUCTION COMPLETE`.
