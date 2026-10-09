# GitHub Actions Neutral Mirror Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a trusted GitHub Actions neutral mirror worker that pushes the exact authoritative GitHub commit to GitLab, triggers a push-only GitLab evidence pipeline, and proves exact-SHA parity without exposing GitLab write credentials to feature-branch-controlled code.

**Architecture:** Extend the existing PR #76 mirror/evidence implementation rather than creating a second mirror engine. The trusted GitHub Actions workflow executes worker code from its own protected workflow revision, treats the subject ref/SHA only as data, invokes the existing `sync_gitlab_mirror.py` through a secret-safe credential adapter, and passes typed `ci.input` receipt fields to the existing GitLab push-only pipeline. TinyFish remains a read-only observer; GitHub AI remains advisory; Superpowers and Arena remain the mandatory process/review layers.

**Tech Stack:** Python 3.12, pytest, Git, GitHub Actions, GitLab CI/CD inputs/push options, GitLab Git-over-HTTPS `write_repository`, JSON Schema, existing WhiteChronos Runtime Foundation/governance suites.

**Spec:** `docs/superpowers/specs/2026-10-09-github-actions-neutral-mirror-design.md`

## Global Constraints

- GitHub remains the only authoritative source repository and merge authority.
- GitLab remains a non-authoritative mirror/evidence provider with no merge/deploy authority.
- Use the existing `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py`; do not create a second mirror engine.
- Eligible GitLab evidence requires a real Git push, `CI_PIPELINE_SOURCE=push`, `tag=false`, fresh receipt, exact SHA equality, and final `HEALTHY` parity.
- `mirror_pipeline_ref` is a branch/ref input, never a commit SHA.
- Preserve the existing `Path` import and persisted evidence timestamp normalization.
- The GitLab write credential is least-privilege Git-over-HTTPS repository write access; `write_repository` is sufficient when supported.
- Do not use `CI_JOB_TOKEN` as the final mirror credential because job-token pushes do not trigger the required GitLab pipeline.
- Never place a GitLab token in a remote URL, command argument, receipt, artifact, log, summary, Git config, or repository file.
- The subject feature branch must never control executable workflow code that receives the GitLab write secret.
- The GitHub Environment holding `GITLAB_MIRROR_TOKEN` must restrict deployment to the protected trusted worker ref; an in-YAML branch check alone is not a trust boundary.
- Third-party GitHub Actions used by the secret-bearing worker must be pinned to immutable full commit SHAs, not mutable tags.
- The trusted worker must record the trusted workflow/worker revision used for the mirror.
- Normal mirroring is non-force. Same-SHA freshness uses only `whitechronos-refresh/<digest>`.
- TinyFish may research/observe provider behavior but may not hold the mirror credential, push the authoritative mirror, or mint parity evidence.
- GitHub AI/Codex review is advisory; quota unavailability does not replace CI, Superpowers review, Arena, security checks, or exact-SHA evidence.
- No direct default-branch edits during implementation.
- Merge, deploy, canary, stable, live smoke, R2/R3, and `PRODUCTION COMPLETE` remain separate explicit gates.

## File Structure

- Modify `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py` — extend the existing receipt/push contract with trusted worker revision; remain the only Git mirror engine.
- Create `plugins/whitechronos-control-plane/runtime/github_neutral_mirror.py` — GitHub-hosted orchestration boundary: validate trusted context, create/clean the credential helper, and call `sync_ref`.
- Create `plugins/whitechronos-control-plane/scripts/github_neutral_mirror.py` — thin CLI wrapper around the runtime module; no mirror logic.
- Create `.github/workflows/gitlab-neutral-mirror.yml` — trusted manual/reusable worker surface; no PR/push auto-trigger.
- Modify `.gitlab-ci.yml` — add and verify trusted worker revision input without weakening push-only rules.
- Modify `pipeline/ci_provider_evidence.py` and `schemas/ci_provider_evidence.schema.json` — bind worker revision into persisted evidence/provenance.
- Modify `plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py` — receipt/push-option and credential-adapter tests.
- Create `plugins/whitechronos-control-plane/tests/test_github_neutral_mirror.py` — trusted-context, helper lifecycle, secret boundary and orchestration tests.
- Modify `tests/test_gitlab_pipeline_contract.py` and `tests/test_ci_provider_evidence.py` — GitLab worker-revision/evidence contract tests.
- Modify `plugins/whitechronos-control-plane/tests/test_repository_integration.py` — workflow registration/static security contract.
- Modify `docs/runbooks/gitlab-contingency-ci.md` — bootstrap, credential, dispatch, live-verification and recovery instructions.
- Create `docs/runbooks/github-neutral-mirror.md` — operator-focused GitHub Actions worker runbook.

## Review Focus

1. **Untrusted subject code:** a feature branch must be mirrorable as data without any step executing code or workflow YAML from that branch while the GitLab secret is available; GitHub Environment deployment-branch policy must independently enforce the trusted ref; Tasks 3 and 8 pin this.
2. **Secret leakage through Git plumbing:** the token must not enter argv, URLs, receipts, artifacts, summaries or persisted config, including failure paths; Task 2 pins this.
3. **Trusted worker replay/substitution:** GitLab evidence must bind the exact trusted workflow/worker revision used for the push, not merely the subject SHA; Tasks 1 and 4 pin this.
4. **Same-SHA refresh confusion:** the reserved refresh ref may trigger the pipeline but must never become the parity subject or change the authoritative target branch; Tasks 1 and 4 pin this.
5. **Bootstrap/supply-chain circularity:** the live secret must not be provisioned to a worker that exists only on the feature branch, nor to a worker that loads mutable third-party action tags; Tasks 3 and 8 make trusted-ref installation, environment branch policy and immutable action pinning explicit gates.

---

### Task 1: Extend the existing mirror receipt with trusted worker revision

**Files:**
- Modify: `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py`
- Modify: `plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py`

**Interfaces:**
- Modifies `_mirror_receipt_claim(..., worker_revision: str, pipeline_ref: str | None = None) -> dict[str, object]`.
- Modifies `sync_ref(..., worker_revision: str, target_credential_helper: str | None = None, source_credential_helper: str | None = None) -> dict[str, object]`.
- CLI adds required `--worker-revision <40-hex-sha>`.
- Receipt claim adds `worker_revision`.
- Git push options add `ci.input=mirror_worker_revision=<40-hex-sha>`.
- Later tasks consume the same field in GitLab CI and provider evidence.

- [ ] **Step 1: Write failing receipt-contract tests**

Add tests:

```python
def test_receipt_claim_requires_40_hex_worker_revision(): ...
def test_push_options_bind_worker_revision(): ...
def test_worker_revision_changes_receipt_claim_digest(): ...
def test_same_sha_refresh_keeps_original_parity_ref_and_worker_revision(): ...
```

Assertions:
- invalid/missing worker revision raises `ValueError`;
- `mirror_ref` remains the original ref;
- `mirror_pipeline_ref` may be the reserved refresh ref;
- `worker_revision` is present in the claim and push options;
- changing only `worker_revision` changes the receipt claim digest.

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
```

Expected: new worker-revision tests FAIL while existing mirror tests remain green.

- [ ] **Step 3: Implement the minimal receipt/push extension**

In `sync_gitlab_mirror.py`:

- validate worker revision with the existing 40-hex SHA rule;
- include it in the receipt claim before digesting;
- include it in `_mirror_push_options`;
- require it at the public `sync_ref` and CLI boundary;
- do not alter canonical provider direction, no-force behavior, same-SHA refresh derivation, or credential-helper semantics.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the Step 2 command.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py
git add plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
git commit -m "feat: bind trusted worker revision to mirror receipt"
```

### Task 2: Add secret-safe GitHub neutral mirror orchestration

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/github_neutral_mirror.py`
- Create: `plugins/whitechronos-control-plane/scripts/github_neutral_mirror.py`
- Create: `plugins/whitechronos-control-plane/tests/test_github_neutral_mirror.py`

**Interfaces:**
- Produces `NeutralMirrorRequest(subject_ref: str, subject_sha: str, worker_revision: str, target_url: str, receipt_path: Path)`.
- Produces `validate_trusted_worker_context(request: NeutralMirrorRequest, *, workflow_ref: str, workflow_sha: str, trusted_ref: str) -> None`.
- Produces `temporary_gitlab_credential_helper(token: str, username: str = "oauth2") -> ContextManager[Path]` that creates a mode-0600 credential material file plus a mode-0700 helper executable and yields only the helper path.
- Produces `run_neutral_mirror(repo_root: Path, request: NeutralMirrorRequest, *, workflow_ref: str, workflow_sha: str, trusted_ref: str) -> dict[str, object]`.
- CLI consumes `--subject-ref`, `--subject-sha`, `--worker-revision`, `--target-url`, `--receipt`, `--trusted-ref`; token comes only from `GITLAB_MIRROR_TOKEN`.

- [ ] **Step 1: Write failing trust/secret-boundary tests**

Add tests:

```python
def test_untrusted_workflow_ref_fails_before_secret_access(): ...
def test_worker_sha_must_equal_workflow_sha(): ...
def test_subject_sha_is_data_not_executable_worker_revision(): ...
def test_missing_gitlab_token_fails_before_git(): ...
def test_credential_helper_contains_no_token_literal(): ...
def test_credential_material_mode_is_0600(): ...
def test_credential_helper_mode_is_0700(): ...
def test_token_is_removed_from_child_environment_before_git(): ...
def test_credential_helper_and_material_are_removed_on_success(): ...
def test_credential_helper_and_material_are_removed_on_sync_failure(): ...
def test_token_never_appears_in_sync_ref_arguments_or_receipt(): ...
```

Use monkeypatch/fakes for `sync_ref`; do not make network calls.

- [ ] **Step 2: Run focused tests and verify RED**

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_github_neutral_mirror.py
```

Expected: FAIL because the orchestration module does not exist.

- [ ] **Step 3: Implement the runtime orchestration**

Rules:

- check trusted workflow/ref/worker revision before reading `GITLAB_MIRROR_TOKEN`;
- accept only a 40-hex subject SHA and worker SHA;
- read `GITLAB_MIRROR_TOKEN` once, create a mode-0600 temporary credential material file, then remove the token variable from the process environment before invoking Git;
- create a temporary executable helper with mode `0700`; helper code contains only the path to the temporary credential material, never the token literal;
- helper emits Git credential protocol fields only to Git's credential-helper stdout;
- call the existing `sync_ref` directly from trusted code after the token is absent from the child environment;
- cleanup helper, credential material and temp directory in `finally` on success or failure;
- never catch-and-print the token, credential material contents, or raw environment.

- [ ] **Step 4: Implement the thin CLI wrapper**

The CLI imports `run_neutral_mirror`, converts paths, and emits only secret-free JSON receipt output. Validation/runtime errors return non-zero with fixed/sanitized diagnostics.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run Step 2.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/whitechronos-control-plane/runtime/github_neutral_mirror.py
git add plugins/whitechronos-control-plane/scripts/github_neutral_mirror.py
git add plugins/whitechronos-control-plane/tests/test_github_neutral_mirror.py
git commit -m "feat: add trusted GitHub neutral mirror runtime"
```

### Task 3: Add the trusted GitHub Actions worker workflow

**Files:**
- Create: `.github/workflows/gitlab-neutral-mirror.yml`
- Modify: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`

**Interfaces:**
- Workflow name: `GitLab Neutral Mirror`.
- Trigger: `workflow_dispatch` only for the initial trusted worker; no `pull_request`, `push`, or `workflow_run` automatic secret-bearing trigger.
- Inputs: `subject_ref` and `subject_sha`, both required strings.
- Environment: `gitlab-neutral-mirror`, configured in GitHub to allow deployments only from the protected trusted worker ref (initially `main`).
- Secret: environment/repository secret `GITLAB_MIRROR_TOKEN`.
- GitHub permissions: `contents: read`; no write permission is required.
- Trusted branch/ref: `refs/heads/main` unless a later separately approved protected worker ref replaces it.
- Worker revision: `${{ github.workflow_sha }}` (or the equivalent trusted job workflow SHA available to the runtime).
- Subject SHA is passed to the Python worker as data; the workflow must not checkout/execute the subject commit while the GitLab secret is available.

- [ ] **Step 1: Write failing static workflow-security tests**

Add assertions that:

- workflow has only `workflow_dispatch`;
- inputs are required;
- permissions are read-only;
- job is bound to the `gitlab-neutral-mirror` environment;
- job fails unless running the trusted worker ref;
- trusted code checkout/ref is the workflow revision, not `subject_sha`;
- the environment name is `gitlab-neutral-mirror` and the runbook requires environment deployment-branch policy restricted to the protected trusted ref;
- every external `uses:` action in the secret-bearing job is pinned to the exact reviewed SHAs listed above;
- `subject_sha` never appears as an `actions/checkout ref`;
- token is referenced only in the mirror step environment;
- token text/name is not passed as a CLI argument;
- workflow invokes `scripts/github_neutral_mirror.py`;
- workflow uploads only secret-free receipt/evidence artifacts;
- no direct merge/deploy command exists.

- [ ] **Step 2: Run repository integration tests and verify RED**

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
```

Expected: FAIL because the workflow does not exist.

- [ ] **Step 3: Create the workflow**

Use:

- pin `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1), `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97` (v7.0.0), and `actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9` (v7.0.2) if artifact upload is used; do not replace these with mutable tags during this implementation;
- checkout of trusted repository code at the trusted workflow revision;
- Python 3.12;
- minimal dependency install required by the existing mirror/runtime code;
- mirror step with `GITLAB_MIRROR_TOKEN` only in step-level `env`;
- `worker_revision` from trusted workflow SHA;
- receipt artifact upload after secret cleanup;
- `concurrency` keyed by subject ref to avoid overlapping writes to the same mirror ref.

Do not add an automatic trigger from untrusted PR code.

- [ ] **Step 4: Run repository integration tests and verify GREEN**

Run Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/gitlab-neutral-mirror.yml
git add plugins/whitechronos-control-plane/tests/test_repository_integration.py
git commit -m "feat: add trusted GitLab neutral mirror workflow"
```

### Task 4: Bind trusted worker revision into GitLab evidence

**Files:**
- Modify: `.gitlab-ci.yml`
- Modify: `pipeline/ci_provider_evidence.py`
- Modify: `schemas/ci_provider_evidence.schema.json`
- Modify: `tests/test_gitlab_pipeline_contract.py`
- Modify: `tests/test_ci_provider_evidence.py`

**Interfaces:**
- GitLab CI adds required input `mirror_worker_revision` matching exactly 40 hexadecimal characters using the existing RE2 full-text anchoring style.
- Variable `WHITECHRONOS_MIRROR_WORKER_REVISION` carries the input.
- Mirror receipt reconstruction includes `worker_revision`.
- Runtime identity records `worker_revision`.
- `CIProviderEvidence` adds `worker_revision: str`.
- `worker_revision` is included in `_PROVENANCE_FIELDS` and JSON Schema required fields.

- [ ] **Step 1: Write failing pipeline/evidence tests**

Add:

```python
def test_pipeline_requires_worker_revision_input(): ...
def test_receipt_digest_reconstruction_includes_worker_revision(): ...
def test_runtime_identity_records_worker_revision(): ...
def test_provider_evidence_requires_worker_revision(): ...
def test_provider_provenance_changes_when_worker_revision_changes(): ...
```

Also pin the existing review-focus condition:

```python
def test_refresh_pipeline_keeps_original_mirror_ref_with_same_worker_revision(): ...
```

- [ ] **Step 2: Run focused tests and verify RED**

```bash
python -m pytest -q tests/test_gitlab_pipeline_contract.py tests/test_ci_provider_evidence.py
```

Expected: FAIL only on new worker-revision contract tests.

- [ ] **Step 3: Extend GitLab input/runtime contract**

Add `mirror_worker_revision` without changing:

- `workflow.rules` push-only;
- tag rejection;
- normal/ref vs refresh/ref distinction;
- final dual-provider re-observation;
- final parity freshness logic.

- [ ] **Step 4: Extend provider evidence/schema**

Normalize worker SHA to lowercase for provenance, validate 40-hex, and include it in persisted evidence.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run Step 2.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .gitlab-ci.yml
git add pipeline/ci_provider_evidence.py schemas/ci_provider_evidence.schema.json
git add tests/test_gitlab_pipeline_contract.py tests/test_ci_provider_evidence.py
git commit -m "feat: bind trusted worker revision to GitLab evidence"
```

### Task 5: Document bootstrap, credential provisioning, dispatch and recovery

**Files:**
- Modify: `docs/runbooks/gitlab-contingency-ci.md`
- Create: `docs/runbooks/github-neutral-mirror.md`
- Modify: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`

**Interfaces:**
- Trusted environment name: `gitlab-neutral-mirror`.
- Secret name: `GITLAB_MIRROR_TOKEN`.
- Username used by Git credential helper: `oauth2` (non-secret).
- Required GitLab token capability: Git-over-HTTPS push limited to the mirror project; prefer `write_repository` when available.
- Bootstrap gate: secret provisioning/live execution occurs only after the worker workflow exists on a protected trusted ref.

- [ ] **Step 1: Write failing runbook contract tests**

Assert documentation states:

- project access token `write_repository` is preferred when the GitLab tier supports it;
- if project access tokens are unavailable, use another project-scoped/fine-grained credential that grants only repository push for the target project; never broaden to `api` merely for convenience;
- deploy tokens are not a repository-push solution;
- `CI_JOB_TOKEN` push cannot satisfy the final design because it does not trigger the required pipeline;
- token is stored only in GitHub Actions secret/environment storage;
- workflow must already be trusted before secret provisioning;
- GitHub Environment `gitlab-neutral-mirror` must restrict deployments to the protected trusted worker ref; runtime YAML checks are defense-in-depth only;
- the runbook records the exact reviewed action SHAs (`checkout` v7.0.1, `setup-python` v7.0.0, `upload-artifact` v7.0.2) and requires a separate review before updating them;
- subject ref/SHA are data;
- exact manual dispatch procedure;
- same-SHA refresh behavior;
- revocation/rotation procedure;
- failure recovery never uses force-push or API commits to fabricate parity.

- [ ] **Step 2: Run repository integration tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
```

Expected: FAIL until runbooks exist/contain the required contract.

- [ ] **Step 3: Write/update the runbooks**

Include operator commands without embedding any real credential. The dispatch instructions must require the authoritative subject ref and exact 40-hex SHA.

- [ ] **Step 4: Run tests and verify GREEN**

Run Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/runbooks/gitlab-contingency-ci.md docs/runbooks/github-neutral-mirror.md
git add plugins/whitechronos-control-plane/tests/test_repository_integration.py
git commit -m "docs: add neutral mirror bootstrap runbook"
```

### Task 6: Run complete regression, security and governance verification

**Files:** no product-code changes expected; repair only regressions caused by Tasks 1-5.

**Interfaces:**
- Consumes the implementation branch HEAD.
- Produces fresh same-SHA verification evidence.
- Does not expose or require the live GitLab secret.

- [ ] **Step 1: Run Control Plane tests**

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
```

Expected: PASS.

- [ ] **Step 2: Run full Python regression**

```bash
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 3: Run Broker compatibility**

```bash
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
```

Expected: PASS.

- [ ] **Step 4: Run repository governance gates**

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Expected: all PASS.

- [ ] **Step 5: Run Runtime Doctor locally**

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
```

Expected: configuration/local checks are truthful; repository config does not manufacture host/subagent discovery.

- [ ] **Step 6: Run static secret and workflow safety checks**

```bash
git diff --check
git grep -nEi "(github_pat_|gh[pousr]_[A-Za-z0-9]{20,}|glpat-|authorization:[[:space:]]*(bearer|basic)|client_secret=|access[_-]?token=|refresh[_-]?token=|password=|cookie=)" -- .
```

Inspect matches manually. Synthetic rejection fixtures are allowed; real credentials are not.

Also verify:

- no token in Git remote URL;
- no subject-SHA checkout/execution in the secret-bearing worker job;
- secret-bearing environment is protected by GitHub deployment-branch rules, not only in-workflow conditionals;
- all external actions in that job are commit-SHA pinned;
- no force push;
- no automatic merge/deploy command.

- [ ] **Step 7: Run TinyFish read-only observer checks**

Use TinyFish only to corroborate current provider documentation/behavior when useful. Do not create Browser Profiles, paid browser runs, monitors, or credentials for routine verification.

Expected: TinyFish availability or profile degradation does not change source/mirror authority.

- [ ] **Step 8: Commit only legitimate regression fixes**

No empty verification commit.

### Task 7: Whole-branch review, Arena and GitHub CI

**Files:** no direct main mutation.

**Interfaces:**
- Produces reviewed implementation PR evidence.
- Does not provision the live GitLab secret.
- Does not authorize merge.

- [ ] **Step 1: Run Superpowers whole-branch code review**

If genuine isolated subagents are available, use the approved real route. Otherwise use the official inline fallback and say so accurately.

Review especially:

- feature-branch code cannot receive the secret;
- trusted worker SHA binding;
- credential-helper cleanup;
- source/target canonical binding;
- same-SHA refresh semantics;
- GitLab push-only evidence;
- provenance and final parity.

- [ ] **Step 2: Run GitHub Arena Review**

Use at least four materially different strategies. Treat a verified secret exposure, subject-code execution with secret access, forged parity path, or authority escalation as fatal.

Expected: no unresolved fatal flaw.

- [ ] **Step 3: Open/update the implementation PR**

PR body must link:

- approved spec;
- this plan;
- RED/GREEN commits;
- test commands/results;
- bootstrap trust gate;
- explicit statement that merge/deploy/live smoke are not authorized.

- [ ] **Step 4: Require GitHub CI on the exact PR head**

Applicable Runtime Foundation, governance/policy and new neutral-worker workflow contract tests must PASS on the current head SHA. If fixes change the head, discard stale CI evidence.

- [ ] **Step 5: Request advisory GitHub AI/Codex review**

If available, request code and security review. If quota-blocked, record that state and continue only with the mandatory Superpowers/Arena/CI/security gates; do not claim Codex review PASS.

- [ ] **Step 6: STOP at bootstrap gate**

Required state before any secret provisioning:

```text
SPEC_APPROVED=YES
PLAN_APPROVED=YES
TDD=PASS
REGRESSION=PASS
SECURITY_REVIEW=PASS
ARENA=PASS
GITHUB_CI=PASS
TRUSTED_WORKER_INSTALLED=NO
LIVE_MIRROR_AUTHORIZED=NO
```

Do not expose `GITLAB_MIRROR_TOKEN` yet.

### Task 8: Trusted-worker bootstrap and live exact-SHA mirror verification

**Files:** no feature-branch code changes expected.

**Interfaces:**
- Requires separately authorized installation/merge of the reviewed worker infrastructure onto the protected trusted GitHub ref.
- Requires user/administrator provisioning of `GITLAB_MIRROR_TOKEN` only after the trusted worker exists.
- Produces live receipt, GitLab push pipeline, final parity artifacts and exact-SHA gate state.
- Ends before the application merge/deploy gate.

- [ ] **Step 1: Verify trusted worker installation precondition**

Read the protected trusted ref and prove:

- `.github/workflows/gitlab-neutral-mirror.yml` exists there;
- its trusted commit SHA is the worker revision to execute;
- branch protection/trusted-ref policy is intact;
- GitHub Environment `gitlab-neutral-mirror` exists and its deployment branch/tag policy admits only the protected trusted worker ref; verify through the GitHub environment/deployment-branch-policy API or equivalent authoritative UI evidence, not from workflow YAML alone;
- external actions referenced by the trusted workflow are pinned to immutable full commit SHAs.

If false:

```text
TRUSTED_WORKER_INSTALLED=NO
```

STOP. Do not provision/expose the secret.

- [ ] **Step 2: Obtain separate bootstrap authorization if installation is still required**

This is a human authorization gate, not an implementation step. The approved implementation plan does not itself authorize merging worker infrastructure into `main`.

- [ ] **Step 3: Provision the least-privilege GitLab credential**

After the trusted worker and environment branch policy exist, the user/authorized administrator creates or supplies a credential restricted to Git repository push for `chronoswhite-group/ChronosWhite-project` and stores only its token in the `gitlab-neutral-mirror` GitHub Actions environment as `GITLAB_MIRROR_TOKEN`. The workflow uses the non-secret username `oauth2` for Git-over-HTTPS access-token authentication.

Do not request the token in chat and do not store it in repository files.

- [ ] **Step 4: Dispatch the trusted worker for the exact subject**

Inputs:

```text
subject_ref=<eligible original branch>
subject_sha=<exact current GitHub PR head SHA>
```

The workflow itself supplies `worker_revision` from its trusted workflow revision.

- [ ] **Step 5: Verify the GitHub worker run**

Require:

- trusted workflow revision matches the receipt;
- no secret appears in logs/artifacts;
- push is non-force;
- receipt exists and its claim/full-record digests validate;
- GitLab target branch after push equals the exact subject SHA.

- [ ] **Step 6: Verify the GitLab pipeline**

Using the GitLab connector, require:

```text
pipeline.source = push
pipeline.sha = subject_sha
pipeline.tag = false
```

For a same-SHA refresh, pipeline ref may be `whitechronos-refresh/<digest>`; parity subject remains the original branch.

- [ ] **Step 7: Verify final evidence artifacts**

Require:

- `mirror-parity-final.json.status == HEALTHY`;
- `contingency-gate.json.evidence_eligible == true`;
- `ci-provider-evidence.json.subject_sha == subject_sha`;
- provider evidence worker revision equals the trusted GitHub worker revision;
- input artifact digests/provenance validate;
- freshness window is current.

- [ ] **Step 8: Re-observe all three SHAs**

Prove:

```text
GITHUB_SHA == GITLAB_MIRROR_SHA == GITLAB_PIPELINE_SHA == subject_sha
```

Historical parity from another SHA is invalid.

- [ ] **Step 9: Run final Arena/Superpowers gate summary**

Expected final pre-merge state:

```text
SPEC_APPROVED=YES
PLAN_APPROVED=YES
TDD=PASS
REGRESSION=PASS
SECURITY_REVIEW=PASS
ARENA=PASS
GITHUB_CI=PASS

TRUSTED_WORKER_INSTALLED=YES
NEUTRAL_WORKER=PASS
GITLAB_PUSH_SOURCE=PASS
GITLAB_TAG=false
RECEIPT_VALID=YES
FINAL_PARITY=HEALTHY
EVIDENCE_ELIGIBLE=true
MIRROR_PARITY=HEALTHY

MERGE_AUTHORIZED=NO
DEPLOY_AUTHORIZED=NO
PRODUCTION_COMPLETE=NO
```

- [ ] **Step 10: STOP**

Do not merge the application PR, deploy, canary, stable-promote, live-smoke, run R2/R3, or declare `PRODUCTION COMPLETE` without separate explicit authorization.

## Execution Bootstrap

After this plan is approved:

1. invoke `superpowers:using-git-worktrees`;
2. inspect the then-current authoritative `main` and open PR #76/#77 state;
3. choose the implementation baseline that contains the approved PR #76 mirror/evidence hardening without silently merging unrelated work;
4. create an isolated feature branch/worktree for the neutral-worker implementation;
5. carry the approved spec and plan as provenance if they are not yet in the selected baseline;
6. use the execution method selected by the user;
7. execute Tasks 1-7 through TDD/review;
8. STOP at the trusted-worker bootstrap gate;
9. execute Task 8 only after the separate trusted-worker installation and credential-provisioning gates are satisfied.


## PR #78 post-review security addendum — 2026-10-09

The seven Codex review findings (five P1 and two P2) amend the pre-bootstrap
release contract without authorizing deployment or provisioning:

- **Trusted GitLab CI:** the subject commit's own `.gitlab-ci.yml` MUST NOT
  control evidence jobs. GitLab project `86465539` must independently read
  from a protected external CI configuration (configured in the provider's
  CI/CD configuration file setting). The connected project currently returns
  an empty `ci_config_path`, so the gate is **BLOCKED**.
- **No mutable secret-runner installs:** no live `pip install` on the
  secret-bearing worker. If the reviewed dependency is absent, fail closed;
  a separately reviewed hermetic runner bootstrap is needed for activation.
- **Authenticated receipt:** canonical receipt SHA-256 alone is unauthenticated.
  Use detached HMAC-SHA256 with an independent 256-bit signing key, passed as
  `mirror_receipt_signature` (never the key itself) and verified in the
  protected external GitLab evidence job before accepting worker-revision claims.
  Neither the key nor the mirror token is provisioned by PR #78.
- **Reruns and retirement:** the trusted GitHub Environment name must include
  the exact trusted worker SHA; no repository-level fallback secret is allowed.
  Retire prior SHA-specific secrets on worker replacement. The code also
  rejects rerun attempts and obsolete main revisions; it cannot revoke a
  credential already provisioned to an old workflow, so external revocation
  is mandatory.
- **Evidence history:** keep unmodified v1 provenance hashes verifiable while
  new worker-bound records use a versioned v2 format. Canonicalize SHA fields
  case-insensitively before hashing.
- **Recovery:** every externally invoked sync CLI supplies the exact
  reviewed `--worker-revision` from its checkout.

GitHub remains authoritative. GitLab remains evidence-only. TinyFish is
read-only research. STOP before merge, secret installation, live mirror, or
deploy until separate gates and authorizations.
