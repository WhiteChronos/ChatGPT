# WhiteChronos Process Gate v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a fail-closed WhiteChronos process gate that requires Superpowers routing and the appropriate Arena review level, binds process evidence to the exact PR head SHA, and enforces the result inside the existing `github-control-plane-policy` required check without fabricating runtime evidence.

**Architecture:** Add one machine-readable process policy, one JSON Schema for process evidence, and one Python gate that reuses `pipeline/github_path_policy.py` for change classification. The gate derives requirements from changed paths, validates structured evidence extracted from the pull-request body, distinguishes attestation/CI/runtime/human authority, and is invoked only for pull-request events inside the existing GitHub control-plane workflow.

**Tech Stack:** Python 3.11+, stdlib `argparse/json/pathlib/dataclasses`, `jsonschema==4.25.1`, pytest 8.4.1, GitHub Actions YAML, JSON Schema Draft 2020-12.

**Spec:** `docs/superpowers/specs/2026-10-06-whitechronos-process-gate-v1-design.md`

## Global Constraints

- Superpowers remains the development-process owner; this implementation MUST NOT fork or weaken official Superpowers workflows.
- GitHub Arena remains the adversarial quality layer; Arena strategy cards MUST NOT be treated as independent subagents.
- Micro Arena is the minimum for every controlled repository task.
- Review Arena is required for `CONTROL_PLANE_CRITICAL` and `RUNTIME_CONTROL` changes.
- Full Arena is required when the process evidence declares an explicit Full-Arena trigger or a future policy rule explicitly requires it; default recorded strategy count is 16 when Full Arena is required.
- `CONFIGURED`, `LOCAL_RUNTIME_HEALTHY`, `HOST_DISCOVERED`, and `LIVE_VERIFIED` remain distinct Runtime Doctor facts.
- Process attestation, CI verification, runtime verification, and human authorization MUST remain distinct evidence classes.
- Process evidence MUST bind to the exact evaluated PR head SHA; stale SHA evidence fails closed.
- TDD RED evidence is attested historical process evidence; a later green CI run MUST NOT be treated as proof that RED occurred.
- Independent-agent claims require real runtime evidence including lifecycle path and non-empty real agent IDs.
- PR body evidence may satisfy structured attestation, but MUST NOT by itself satisfy a runtime-verification claim.
- The existing `github-control-plane-policy` status check remains the single required GitHub control-plane check for this feature.
- Baseline workflow permissions remain read-only.
- PR #72 and PR #73 MUST NOT be mutated by this implementation project.
- No merge, deploy, canary, stable promotion, live smoke, R2/R3, or `PRODUCTION COMPLETE` is authorized by this plan.

## File Structure

- Create `governance/AGENT_PROCESS_POLICY.json` — repository process requirements, risk-to-Arena mapping, TDD applicability rules, and fail-closed defaults.
- Create `schemas/agent_process_evidence.schema.json` — shape validation for the PR-attested process evidence object.
- Create `pipeline/agent_process_gate.py` — policy/evidence loading, requirement derivation, semantic validation, PR-body extraction, CLI, and deterministic findings.
- Create `tests/test_agent_process_gate.py` — focused unit and semantic gate tests.
- Create `tests/fixtures/agent_process/` — minimal valid/invalid evidence and GitHub event fixtures used by gate tests.
- Create `.github/pull_request_template.md` — human-readable process checklist plus a machine-readable evidence block.
- Modify `.github/workflows/github-control-plane-policy.yml` — invoke the process gate for `pull_request` events while preserving read-only permissions.
- Modify `tests/test_github_control_plane_bootstrap.py` — assert the workflow invokes the gate and does not widen permissions.
- Modify `AGENTS.md` — document the Process Gate v1 evidence contract and the repository/product-surface boundary.

## Review Focus

1. **Stale attestation after a push:** evidence whose `subject_sha` no longer equals the current PR head must fail with `PROCESS_EVIDENCE_STALE`.
2. **Routine documentation PR:** documentation-only change must require Micro Arena and Superpowers routing but must not require TDD.
3. **High-impact change with weak Arena:** `CONTROL_PLANE_CRITICAL` or `RUNTIME_CONTROL` change with only Micro Arena must fail with `ARENA_MODE_TOO_WEAK`.
4. **False independent-agent claim:** `independent_agents_claimed=true` with configuration-only or PR-body-only evidence must fail with `RUNTIME_EVIDENCE_MISSING` or `FALSE_INDEPENDENT_AGENT_CLAIM`.
5. **Malformed or ambiguous PR evidence block:** missing markers, duplicate blocks, invalid JSON, or schema-invalid content must fail closed with deterministic `PROCESS_EVIDENCE_INVALID`.

---

### Task 1: Add the process policy and evidence schema

**Files:**
- Create: `governance/AGENT_PROCESS_POLICY.json`
- Create: `schemas/agent_process_evidence.schema.json`
- Create: `tests/test_agent_process_gate.py`
- Create: `pipeline/agent_process_gate.py`

**Interfaces:**
- Consumes: no prior Process Gate interfaces.
- Produces:
  - `load_policy(path: Path) -> dict[str, object]`
  - `load_evidence(path: Path) -> dict[str, object]`
  - `validate_evidence_schema(evidence: dict[str, object], schema_path: Path) -> list[str]`
  - constants `POLICY_SCHEMA_VERSION = "whitechronos-agent-process-policy/v1"` and `EVIDENCE_SCHEMA_VERSION = "whitechronos-agent-process/v1"`.

- [ ] **Step 1: Write failing tests for policy and schema loading**

Add tests named:

```python
def test_process_policy_declares_required_baseline_controls():
    policy = gate.load_policy(POLICY)
    assert policy["schema_version"] == "whitechronos-agent-process-policy/v1"
    assert policy["baseline"]["superpowers_routing_required"] is True
    assert policy["baseline"]["minimum_arena_mode"] == "micro"
    assert policy["high_impact"]["arena_mode"] == "review"
    assert policy["full_arena"]["default_strategy_count"] == 16
    assert policy["fail_closed"] is True

def test_valid_process_evidence_matches_schema():
    evidence = gate.load_evidence(VALID_EVIDENCE)
    assert gate.validate_evidence_schema(evidence, SCHEMA) == []

def test_schema_rejects_missing_subject_sha():
    evidence = gate.load_evidence(VALID_EVIDENCE)
    del evidence["subject"]["subject_sha"]
    errors = gate.validate_evidence_schema(evidence, SCHEMA)
    assert errors
```

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "policy_declares or matches_schema or missing_subject_sha"
```

Expected: FAIL because `pipeline/agent_process_gate.py`, policy, and schema do not yet exist.

- [ ] **Step 3: Create the minimal policy**

Create `governance/AGENT_PROCESS_POLICY.json` with these required values:

```json
{
  "schema_version": "whitechronos-agent-process-policy/v1",
  "baseline": {
    "superpowers_routing_required": true,
    "minimum_arena_mode": "micro"
  },
  "high_impact": {
    "path_classes": ["CONTROL_PLANE_CRITICAL", "RUNTIME_CONTROL"],
    "arena_mode": "review"
  },
  "full_arena": {
    "require_when_attested_triggered": true,
    "default_strategy_count": 16
  },
  "tdd": {
    "roots": ["pipeline/", "plugins/", "scripts/"],
    "extensions": [".py", ".js", ".mjs", ".ts", ".tsx", ".sh"],
    "exclude_prefixes": ["tests/", "vendor/", "docs/"]
  },
  "fail_closed": true
}
```

Do not duplicate the path-classification implementation here; the gate must import `pipeline/github_path_policy.py`.

- [ ] **Step 4: Create the evidence schema**

The schema MUST require:

- `schema_version == "whitechronos-agent-process/v1"`;
- `subject.repository`, `subject.pull_request`, and 40-hex `subject.subject_sha`;
- `task.kind` in `non_development|development`;
- `superpowers.routing_checked`, `superpowers.bootstrap`, `superpowers.workflows`, `superpowers.status`;
- `arena.performed_mode` in `micro|review|full`, `arena.status`, `arena.full_arena_triggered`, `arena.independent_agents_claimed`;
- optional `tdd`, `review`, and `runtime` objects with typed statuses;
- `verification.status`;
- `human_authority.merge_authorized`;
- `blockers` as structured findings with severity/status/code.

Keep cross-field semantics out of JSON Schema; Task 3 owns semantic policy.

- [ ] **Step 5: Implement minimal schema loaders/validator**

Implement:

```python
def load_policy(path: Path) -> dict[str, object]: ...
def load_evidence(path: Path) -> dict[str, object]: ...
def validate_evidence_schema(
    evidence: dict[str, object],
    schema_path: Path,
) -> list[str]: ...
```

Use `jsonschema.Draft202012Validator` and return stable, sorted error strings.

- [ ] **Step 6: Run focused tests to verify GREEN**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "policy_declares or matches_schema or missing_subject_sha"
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add governance/AGENT_PROCESS_POLICY.json schemas/agent_process_evidence.schema.json pipeline/agent_process_gate.py tests/test_agent_process_gate.py
git commit -m "feat: define agent process policy and evidence schema"
```

---

### Task 2: Derive process requirements from changed paths

**Files:**
- Modify: `pipeline/agent_process_gate.py`
- Modify: `tests/test_agent_process_gate.py`

**Interfaces:**
- Consumes:
  - `github_path_policy.classify_paths(paths: list[str]) -> dict[str, list[str]]`
  - policy fields from Task 1.
- Produces:
  - immutable `ProcessRequirements` dataclass with:
    - `minimum_arena_mode: str`
    - `superpowers_routing_required: bool`
    - `tdd_required: bool`
    - `independent_review_required: bool`
    - `high_impact: bool`
  - `derive_requirements(paths: list[str], policy: dict[str, object]) -> ProcessRequirements`
  - `arena_mode_rank(mode: str) -> int`.

- [ ] **Step 1: Write failing classification tests**

Add tests:

```python
def test_documentation_only_requires_micro_without_tdd():
    req = gate.derive_requirements(["docs/guide.md"], policy)
    assert req.minimum_arena_mode == "micro"
    assert req.tdd_required is False
    assert req.high_impact is False

def test_control_plane_change_requires_review_arena():
    req = gate.derive_requirements(["pipeline/agent_process_gate.py"], policy)
    assert req.minimum_arena_mode == "review"
    assert req.high_impact is True
    assert req.tdd_required is True

def test_runtime_control_change_requires_review_arena():
    req = gate.derive_requirements(
        ["plugins/subagent-broker/server.mjs"],
        policy,
    )
    assert req.minimum_arena_mode == "review"
    assert req.tdd_required is True
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "documentation_only or control_plane_change or runtime_control_change"
```

Expected: FAIL because `ProcessRequirements` and `derive_requirements` do not exist.

- [ ] **Step 3: Implement requirement derivation**

Import `github_path_policy` rather than copying its path logic.

Rules:

- baseline Arena = `micro`;
- any non-empty `CONTROL_PLANE_CRITICAL` or `RUNTIME_CONTROL` class upgrades minimum Arena to `review`;
- `tdd_required=True` when a changed path is under one of the configured TDD roots, has one of the configured code extensions, and is not under an excluded prefix;
- `independent_review_required=True` for high-impact changes;
- no path class may lower a stronger requirement already derived.

- [ ] **Step 4: Add edge-case tests**

Add:

```python
def test_test_file_alone_does_not_trigger_tdd():
    req = gate.derive_requirements(["tests/test_x.py"], policy)
    assert req.tdd_required is False

def test_mixed_docs_and_pipeline_uses_strongest_requirement():
    req = gate.derive_requirements(["docs/x.md", "pipeline/x.py"], policy)
    assert req.minimum_arena_mode == "review"
    assert req.tdd_required is True
```

- [ ] **Step 5: Run Task 2 tests to verify GREEN**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "documentation_only or control_plane_change or runtime_control_change or test_file_alone or mixed_docs"
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/agent_process_gate.py tests/test_agent_process_gate.py
git commit -m "feat: derive process requirements from repository changes"
```

---

### Task 3: Enforce semantic process evidence and fail-closed findings

**Files:**
- Modify: `pipeline/agent_process_gate.py`
- Modify: `tests/test_agent_process_gate.py`

**Interfaces:**
- Consumes:
  - `ProcessRequirements` from Task 2;
  - schema-valid evidence from Task 1.
- Produces:
  - `evaluate_process_evidence(evidence: dict[str, object], requirements: ProcessRequirements, expected_repository: str, expected_pr: int, expected_sha: str) -> list[str]`
  - deterministic finding-code prefixes from the spec.

- [ ] **Step 1: Write failing tests for exact-subject and baseline requirements**

Add:

```python
def test_stale_subject_sha_fails_closed():
    errors = gate.evaluate_process_evidence(
        evidence_with_sha("0" * 40),
        requirements=docs_requirements,
        expected_repository="WhiteChronos/ChatGPT",
        expected_pr=74,
        expected_sha="1" * 40,
    )
    assert "PROCESS_EVIDENCE_STALE" in error_codes(errors)

def test_missing_superpowers_routing_fails():
    evidence = valid_evidence()
    evidence["superpowers"]["routing_checked"] = False
    errors = evaluate(evidence, docs_requirements)
    assert "SUPERPOWERS_ROUTING_MISSING" in error_codes(errors)

def test_review_required_but_micro_performed_fails():
    evidence = valid_evidence(arena_mode="micro")
    errors = evaluate(evidence, control_plane_requirements)
    assert "ARENA_MODE_TOO_WEAK" in error_codes(errors)
```

- [ ] **Step 2: Run tests to verify RED**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "stale_subject or missing_superpowers or review_required"
```

Expected: FAIL because semantic evaluation does not exist.

- [ ] **Step 3: Implement baseline semantic checks**

Implement checks in deterministic order:

1. repository / PR identity;
2. exact SHA;
3. Superpowers routing + bootstrap `using-superpowers`;
4. Arena performed mode at or above required mode;
5. Full Arena trigger: if `arena.full_arena_triggered=true`, require `performed_mode=full`;
6. required verification status;
7. open blocker scan.

Use finding strings in the form:

```text
<CODE>: <human-readable detail>
```

- [ ] **Step 4: Write failing TDD and independent-review tests**

Add:

```python
def test_code_change_without_tdd_evidence_fails():
    errors = evaluate(valid_evidence_without_tdd(), code_requirements)
    assert "TDD_EVIDENCE_MISSING" in error_codes(errors)

def test_tdd_requires_red_green_and_regression_fields():
    evidence = valid_evidence_with_tdd()
    del evidence["tdd"]["red"]
    errors = evaluate(evidence, code_requirements)
    assert "TDD_EVIDENCE_MISSING" in error_codes(errors)

def test_high_impact_change_without_review_evidence_fails():
    errors = evaluate(valid_evidence_without_review(), control_plane_requirements)
    assert "REVIEW_EVIDENCE_MISSING" in error_codes(errors)
```

- [ ] **Step 5: Implement TDD/review semantic checks**

When `requirements.tdd_required` is true, require:

- `tdd.status == "PASS"`;
- nonblank `tdd.red.command`;
- nonblank `tdd.red.expected_failure`;
- nonblank `tdd.green.command`;
- `tdd.green.status == "PASS"`;
- nonblank regression command;
- regression status `PASS`.

When `requirements.independent_review_required` is true, require review status `PASS` and a nonblank reviewer source.

Do not claim that CI proves historical RED.

- [ ] **Step 6: Write failing runtime-truthfulness tests**

Add:

```python
def test_independent_agent_claim_without_runtime_evidence_fails():
    evidence = valid_evidence()
    evidence["arena"]["independent_agents_claimed"] = True
    evidence["runtime"] = {"required": True, "status": "FAIL", "evidence": []}
    errors = evaluate(evidence, docs_requirements)
    assert "RUNTIME_EVIDENCE_MISSING" in error_codes(errors)

def test_config_only_runtime_evidence_cannot_prove_independent_agents():
    evidence = independent_agent_evidence(
        runtime_path="configured_only",
        agent_ids=[],
    )
    errors = evaluate(evidence, docs_requirements)
    assert "FALSE_INDEPENDENT_AGENT_CLAIM" in error_codes(errors)

def test_real_runtime_path_with_agent_ids_can_satisfy_claim():
    evidence = independent_agent_evidence(
        runtime_path="native_codex_multi_agent",
        agent_ids=["agent-1", "agent-2"],
    )
    assert runtime_claim_errors(evidence) == []
```

- [ ] **Step 7: Implement runtime-claim semantics**

If `independent_agents_claimed=true`, require:

- `runtime.status == "PASS"`;
- `runtime.path` in `native_codex_multi_agent|subagent_broker`;
- non-empty unique `runtime.agent_ids`;
- at least one evidence item classified as runtime evidence;
- no evidence item whose only class is `CONFIGURED` or `CI_VERIFIED` may satisfy the host-lifecycle requirement.

- [ ] **Step 8: Add blocker and human-authority tests**

Add tests proving:

- OPEN `CRITICAL` or `IMPORTANT` blocker fails with `UNRESOLVED_PROCESS_BLOCKER`;
- RESOLVED blockers do not fail;
- `human_authority.merge_authorized=false` is valid during ordinary PR validation and does not fail merely because the PR exists.

- [ ] **Step 9: Run Task 3 tests to verify GREEN**

Run:

```bash
pytest -q tests/test_agent_process_gate.py
```

Expected: PASS.

- [ ] **Step 10: Commit**

```bash
git add pipeline/agent_process_gate.py tests/test_agent_process_gate.py
git commit -m "feat: enforce fail-closed agent process evidence"
```

---

### Task 4: Parse PR evidence and expose a deterministic CLI

**Files:**
- Modify: `pipeline/agent_process_gate.py`
- Create: `tests/fixtures/agent_process/valid_pull_request_event.json`
- Create: `tests/fixtures/agent_process/malformed_pull_request_event.json`
- Modify: `tests/test_agent_process_gate.py`

**Interfaces:**
- Consumes:
  - GitHub event JSON at `GITHUB_EVENT_PATH` or explicit `--github-event-json`;
  - exact changed-path list;
  - policy/schema paths.
- Produces:
  - `extract_process_evidence(pr_body: str) -> dict[str, object]`;
  - `load_pull_request_context(event_path: Path) -> PullRequestContext`;
  - CLI output `AGENT_PROCESS_GATE=PASS|FAIL`.

- [ ] **Step 1: Write failing PR-body extraction tests**

The PR template will use exactly one marker pair:

```text
<!-- WHITECHRONOS_PROCESS_EVIDENCE_START -->
```

and

```text
<!-- WHITECHRONOS_PROCESS_EVIDENCE_END -->
```

Between them is one fenced JSON object.

Add tests proving:

- one valid block parses;
- no block fails;
- duplicate blocks fail;
- invalid JSON fails;
- text outside the block is ignored.

Expected error code for all malformed cases: `PROCESS_EVIDENCE_INVALID`.

- [ ] **Step 2: Run extraction tests to verify RED**

Run:

```bash
pytest -q tests/test_agent_process_gate.py -k "process_evidence_block or duplicate_blocks or invalid_json"
```

Expected: FAIL because extraction is not implemented.

- [ ] **Step 3: Implement strict extraction**

Implement `extract_process_evidence(pr_body: str)` with these rules:

- exactly one start marker;
- exactly one end marker;
- end marker follows start marker;
- exactly one JSON object in the selected block;
- optional ```json fences are stripped;
- duplicate marker pairs fail closed;
- return a dictionary only.

Do not execute YAML or arbitrary code.

- [ ] **Step 4: Write failing GitHub event-context tests**

Add fixture assertions for:

```python
context.repository == "WhiteChronos/ChatGPT"
context.pull_request == 74
context.head_sha == "<fixture SHA>"
context.body == "<fixture PR body>"
```

Reject non-`pull_request` event payloads when the CLI is invoked in PR-validation mode.

- [ ] **Step 5: Implement CLI**

Required arguments:

```text
--policy governance/AGENT_PROCESS_POLICY.json
--schema schemas/agent_process_evidence.schema.json
--github-event-json <path>
--changed-paths-file <path>
```

CLI flow:

1. load event context;
2. read changed paths;
3. derive requirements;
4. extract evidence from PR body;
5. schema-validate;
6. semantic-validate against exact event repository/PR/head SHA;
7. print `AGENT_PROCESS_GATE=PASS` and requirement summary on success;
8. print `AGENT_PROCESS_GATE=FAIL` plus deterministic findings and exit 1 on failure.

- [ ] **Step 6: Run CLI fixture tests to verify GREEN**

Run:

```bash
pytest -q tests/test_agent_process_gate.py
```

Expected: PASS.

Also run one explicit fixture command:

```bash
python pipeline/agent_process_gate.py \
  --policy governance/AGENT_PROCESS_POLICY.json \
  --schema schemas/agent_process_evidence.schema.json \
  --github-event-json tests/fixtures/agent_process/valid_pull_request_event.json \
  --changed-paths-file tests/fixtures/agent_process/valid_changed_paths.txt
```

Expected output includes `AGENT_PROCESS_GATE=PASS`.

- [ ] **Step 7: Commit**

```bash
git add pipeline/agent_process_gate.py tests/test_agent_process_gate.py tests/fixtures/agent_process
git commit -m "feat: validate pull request process evidence"
```

---

### Task 5: Integrate the gate into the existing required GitHub check

**Files:**
- Modify: `.github/workflows/github-control-plane-policy.yml`
- Modify: `tests/test_github_control_plane_bootstrap.py`
- Create: `.github/pull_request_template.md`

**Interfaces:**
- Consumes:
  - existing `/tmp/changed-paths.txt` produced by the workflow;
  - `GITHUB_EVENT_PATH` supplied by GitHub Actions;
  - CLI from Task 4.
- Produces:
  - the existing required `github-control-plane-policy` job additionally blocks PRs whose Process Gate fails.

- [ ] **Step 1: Write failing workflow integration tests**

Extend `tests/test_github_control_plane_bootstrap.py` with assertions that:

```python
assert "pipeline/agent_process_gate.py" in text
assert "governance/AGENT_PROCESS_POLICY.json" in text
assert "schemas/agent_process_evidence.schema.json" in text
assert "GITHUB_EVENT_PATH" in text
assert "pull-requests: write" not in text
assert "contents: write" not in text
assert "issues: write" not in text
```

Also assert that the process-gate step is conditional on `github.event_name == 'pull_request'`.

- [ ] **Step 2: Run bootstrap test to verify RED**

Run:

```bash
pytest -q tests/test_github_control_plane_bootstrap.py
```

Expected: FAIL because workflow integration does not yet exist.

- [ ] **Step 3: Add the PR template**

Create `.github/pull_request_template.md` with:

- a short human checklist;
- one machine block using the exact markers from Task 4;
- placeholder `subject_sha` that must be replaced by the exact PR head;
- baseline `superpowers.bootstrap = "using-superpowers"`;
- explicit `arena.performed_mode`;
- `full_arena_triggered`;
- typed TDD/review/runtime sections;
- `human_authority.merge_authorized = false` by default;
- no credentials or runtime traces.

The template must state that changing the PR head makes existing evidence stale until `subject_sha` is refreshed.

- [ ] **Step 4: Integrate the CLI into the workflow**

After `Classify changed paths`, add a step equivalent to:

```yaml
- name: Validate agent process evidence
  if: github.event_name == 'pull_request'
  env:
    GITHUB_EVENT_PATH: ${{ github.event_path }}
  run: |
    python pipeline/agent_process_gate.py \
      --policy governance/AGENT_PROCESS_POLICY.json \
      --schema schemas/agent_process_evidence.schema.json \
      --github-event-json "$GITHUB_EVENT_PATH" \
      --changed-paths-file /tmp/changed-paths.txt
```

Preserve:

```yaml
permissions:
  contents: read
```

Do not add write permissions or API calls for PR comments.

- [ ] **Step 5: Run focused workflow tests to verify GREEN**

Run:

```bash
pytest -q tests/test_github_control_plane_bootstrap.py tests/test_agent_process_gate.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/github-control-plane-policy.yml .github/pull_request_template.md tests/test_github_control_plane_bootstrap.py
git commit -m "ci: enforce WhiteChronos agent process gate"
```

---

### Task 6: Document the enforced process and run full regression

**Files:**
- Modify: `AGENTS.md`
- Modify: `tests/test_agent_process_gate.py` only if a missing acceptance-case test is discovered during spec coverage review.

**Interfaces:**
- Consumes: completed Process Gate behavior from Tasks 1-5.
- Produces: repository instructions that accurately describe what is policy-required, CI-verifiable, runtime-verifiable, and outside repository control.

- [ ] **Step 1: Add the Process Gate v1 section to `AGENTS.md`**

Document exactly:

```text
POLICY_REQUIRED
PROCESS_ATTESTED
CI_VERIFIED
RUNTIME_VERIFIED
HUMAN_AUTHORIZED
```

State:

- Superpowers routing is required for every controlled repository task;
- Micro Arena is the baseline;
- Review Arena applies to high-impact changes;
- Full Arena is required when explicitly triggered;
- PR evidence must bind to the exact head SHA;
- stale evidence fails closed;
- independent-agent claims require real lifecycle evidence;
- CI never manufactures `HOST_DISCOVERED`;
- unrelated external ChatGPT/IDE sessions are outside repository enforcement unless they load these instructions.

Do not weaken the existing Runtime Doctor or subagent routing sections.

- [ ] **Step 2: Run Process Gate focused regression**

Run:

```bash
pytest -q tests/test_agent_process_gate.py tests/test_github_control_plane_bootstrap.py
```

Expected: PASS.

- [ ] **Step 3: Run repository-mandated governance tests**

Run:

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

Expected: all PASS.

- [ ] **Step 4: Run full repository regression**

Run:

```bash
pytest -q
```

Expected: PASS with zero failures.

If the repository's Node runtime-control tests are in scope for the changed branch, also run:

```bash
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
```

Expected: PASS.

- [ ] **Step 5: Run final static safety assertions**

Verify:

```bash
git diff --check
git status --short
```

Expected:

- `git diff --check` produces no output;
- tracked worktree is clean after the final commit.

Verify no changed workflow adds:

```text
contents: write
pull-requests: write
issues: write
git push
pull_request_target
```

- [ ] **Step 6: Run Review Arena on the final branch**

Use the GitHub Arena Review mode with at least four materially distinct strategies and review specifically for:

1. false-runtime-proof paths;
2. stale-SHA bypasses;
3. weak-Arena bypasses;
4. PR-body parser ambiguity;
5. permission escalation;
6. regression against existing GitHub control-plane policy.

Any Critical/Important finding must be fixed and re-reviewed before the branch can be presented for merge authorization.

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md
git commit -m "docs: require WhiteChronos process gate evidence"
```

- [ ] **Step 8: Produce the implementation handoff**

Record:

- final implementation branch HEAD SHA;
- focused RED/GREEN evidence per task;
- full regression result;
- governance-gate results;
- Review Arena findings and fix rounds;
- confirmation that PR #72 and #73 were untouched;
- confirmation that no merge/deploy/canary/stable/live-smoke/R2/R3/`PRODUCTION COMPLETE` action occurred.

Stop at the separate merge-authorization gate.
