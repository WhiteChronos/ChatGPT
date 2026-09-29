# AUT Panel GitHub and Codex Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automate candidate engineering generation, independent validation and Codex review in GitHub while preventing auto-merge, production deployment and release bypass.

**Architecture:** Add a dedicated candidate-engineering workflow with read-mostly permissions and artifact publication. Codex consumes versioned prompts/AGENTS contracts to propose or review candidate changes; GitHub Actions independently executes deterministic tests and emits a candidate-review bundle.

**Tech Stack:** GitHub Actions, Python 3.12, pytest, repository prompts/AGENTS contracts, existing PR #23 workflow conventions.

**Spec:** `docs/superpowers/specs/2026-09-28-aut-panel-auto-engineering-design.md`

## Global Constraints

- Actions use minimum required permissions.
- No workflow may auto-merge PR #23.
- No workflow may issue fabrication release or production PLC deployment.
- Candidate generator and independent QA must be distinct steps.
- External tools/repositories require pinned versions and approval before activation.
- Secrets must not be exposed to untrusted pull-request code.

## Review Focus

- Fork/untrusted PR cannot gain secret-bearing write execution.
- Candidate artifact from one commit cannot be validated/published as if produced by another commit.
- Rerunning CI must not mutate historical LI.
- Codex review comment/status must not be treated as human engineering approval.
- Workflow failure must leave an auditable partial candidate bundle, not silently mark PASS.

---

### Task 1: Versioned Codex Candidate-Engineering Prompt

**Files:**
- Create: `prompts/PROMPT_CODEX_AUT_PANEL_AUTO_ENGINEERING_V1.md`
- Modify: `AGENTS.md`
- Test: `tests/test_aut_panel_codex_contract.py`

**Interfaces:**
- Prompt consumes candidate trigger, panel/revision, canonical hashes and test requirements.
- Output contract requires changed files, evidence, candidate delta, tests, HOLDs, rollback and no-release statement.

- [ ] **Step 1: Write failing contract tests**

Assert prompt explicitly forbids historical mutation, gate weakening, auto-merge and production PLC download; requires candidate-revision API and deterministic QA.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_codex_contract.py`  
Expected: FAIL.

- [ ] **Step 3: Add prompt and AGENTS handoff**

Reference the approved spec and implementation plan paths.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_codex_contract.py`  
Expected: PASS.

```bash
git add prompts/PROMPT_CODEX_AUT_PANEL_AUTO_ENGINEERING_V1.md AGENTS.md tests/test_aut_panel_codex_contract.py
git commit -m "docs: add Codex auto-engineering candidate contract"
```

### Task 2: Candidate Engineering GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/aut-panel-candidate-engineering.yml`
- Modify: `tests/test_ci_workflow_contract.py`

**Interfaces:**
- Trigger: `workflow_dispatch` and controlled repository events.
- Produces immutable artifact bundle keyed by commit SHA + candidate ID.

- [ ] **Step 1: Write failing workflow-contract tests**

Assert:
- `permissions: contents: read` by default;
- no `pull_request_target` for executing candidate code;
- no merge/deploy commands;
- Python 3.12;
- candidate runner, candidate gate and regression tests execute;
- artifact name contains commit SHA/candidate ID;
- workflow does not write R02 paths.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_ci_workflow_contract.py -k candidate`  
Expected: FAIL.

- [ ] **Step 3: Create workflow**

The workflow generates candidate artifacts, runs deterministic QA, uploads evidence and exits before human release.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_ci_workflow_contract.py`  
Expected: PASS.

```bash
git add .github/workflows/aut-panel-candidate-engineering.yml tests/test_ci_workflow_contract.py
git commit -m "ci: add AUT panel candidate engineering workflow"
```

### Task 3: Independent Candidate Artifact Verifier

**Files:**
- Create: `pipeline/aut_panel_artifact_verifier.py`
- Test: `tests/test_aut_panel_artifact_verifier.py`
- Modify: `.github/workflows/aut-panel-candidate-engineering.yml`

**Interfaces:**
- Produces:
```python
def verify_bundle(bundle_dir: Path, *, expected_commit_sha: str,
                  expected_candidate_id: str) -> dict[str, Any]: ...
```

- [ ] **Step 1: Write failing verifier tests**

Cover wrong commit SHA, wrong candidate ID, altered PNG/SVG, BOM/render mismatch, missing source hashes and stale QA manifest.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_artifact_verifier.py`  
Expected: FAIL.

- [ ] **Step 3: Implement verifier and wire it after generation**

Verification must operate on serialized artifacts, not in-memory generator state.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_artifact_verifier.py tests/test_ci_workflow_contract.py`  
Expected: PASS.

```bash
git add pipeline/aut_panel_artifact_verifier.py tests/test_aut_panel_artifact_verifier.py .github/workflows/aut-panel-candidate-engineering.yml
git commit -m "feat: independently verify candidate engineering artifact bundles"
```

### Task 4: Codex Review Automation Boundary

**Files:**
- Create: `prompts/PROMPT_CODEX_AUT_PANEL_CANDIDATE_REVIEW_V1.md`
- Modify: `AGENTS.md`
- Test: `tests/test_aut_panel_codex_contract.py`

**Interfaces:**
- Review output: findings, evidence, test gaps, candidate status recommendation; no merge/release action.

- [ ] **Step 1: Write failing review-boundary tests**

Assert review prompt cannot mark `Aprovado para emissão`, cannot merge, cannot waive deterministic findings and must cite artifact hashes.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_codex_contract.py -k review`  
Expected: FAIL.

- [ ] **Step 3: Implement review prompt and AGENTS rules**

Keep Codex as reviewer/proposer, not release authority.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_codex_contract.py`  
Expected: PASS.

```bash
git add prompts/PROMPT_CODEX_AUT_PANEL_CANDIDATE_REVIEW_V1.md AGENTS.md tests/test_aut_panel_codex_contract.py
git commit -m "docs: constrain Codex candidate review authority"
```

### Task 5: End-to-End CI Regression

**Files:**
- Modify: `.github/workflows/aut-panel-learning.yml`
- Modify: `.github/workflows/aut-panel-candidate-engineering.yml`
- Test: `tests/test_ci_workflow_contract.py`
- Test: all new AUT Panel tests

**Interfaces:**
- Consumes all prior subsystem public interfaces.
- Produces CI evidence that candidate automation cannot bypass release control.

- [ ] **Step 1: Add workflow path coverage for all new modules/configs/tests**

Include candidate core, Mem0 adapter, memory benchmark, prompts and workflows.

- [ ] **Step 2: Add smoke fixture**

Exercise: capacity failure → candidate revision → automatic alternative → regeneration → QA → candidate-ready state; explicitly assert source R02 hash unchanged.

- [ ] **Step 3: Run complete targeted suite**

Run:
```bash
python -m compileall -q pipeline tests
python -m pytest -q   tests/test_aut_panel_candidate_*.py   tests/test_aut_panel_mem0.py   tests/test_aut_panel_memory_context.py   tests/test_aut_panel_memory_benchmark.py   tests/test_aut_panel_codex_contract.py   tests/test_aut_panel_artifact_verifier.py   tests/test_aut_panel_agent_system.py   tests/test_layout_optimizer_*.py   tests/test_ci_workflow_contract.py
```
Expected: PASS.

- [ ] **Step 4: Verify forbidden capabilities by static assertions**

Confirm no workflow contains auto-merge, production PLC download, fabrication release mutation or historical LI write paths.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/aut-panel-learning.yml .github/workflows/aut-panel-candidate-engineering.yml tests
git commit -m "test: close AUT panel automatic engineering automation loop"
```
