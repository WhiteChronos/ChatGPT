# AUT Panel Candidate Revision Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable deterministic agents to create and modify new engineering candidate revisions automatically while preserving historical revisions and human release authority.

**Architecture:** Add a candidate-revision service around the existing pipeline, database and layout optimizer. It clones only mutable candidate state, records an immutable delta ledger, applies authorized engineering changes, invalidates downstream artifacts and leaves release blocked until human approval.

**Tech Stack:** Python 3.12, SQLite, JSON/YAML, pytest, existing OR-Tools layout optimizer and AUT Panel pipeline.

**Spec:** `docs/superpowers/specs/2026-09-28-aut-panel-auto-engineering-design.md`

## Global Constraints

- Historical R02 files/rows are immutable.
- Candidate changes must carry trigger, evidence, previous value, proposed value, invalidations, tests and rollback target.
- Automatic enclosure/component/quantity changes apply only to candidate revisions.
- Golden Rules and deterministic gate thresholds are not auto-modifiable.
- Production PLC download, fabrication release and PR auto-merge remain prohibited.

## Review Focus

- Re-running candidate creation with the same source must not duplicate or mutate historical rows.
- Failed mutation midway must leave no half-written candidate state.
- Candidate enclosure change must invalidate load/BOM/layout/render/QA as applicable.
- A candidate may contain HOLDs, but cannot be promoted to release-ready while any blocking HOLD remains.
- Rollback must change only candidate state and pointers, never history.

---

### Task 1: Candidate Revision Data Contract

**Files:**
- Create: `schemas/aut_panel_candidate_revision_v1.schema.json`
- Modify: `database/aut_panel_schema.sql`
- Test: `tests/test_aut_panel_candidate_revision.py`

**Interfaces:**
- Consumes: panel ID, source revision, trigger finding, canonical input hashes.
- Produces: SQLite `candidate_revisions` and `candidate_revision_changes` records plus JSON schema.

- [ ] **Step 1: Write failing schema/database tests**

Add tests asserting:
- `candidate_revisions` stores `candidate_id`, `panel_id`, `source_revision`, `candidate_revision`, `status`, `trigger_type`, `created_at`, `rollback_target`.
- `candidate_revision_changes` stores `change_id`, `candidate_id`, `change_type`, `path`, `before_json`, `after_json`, `evidence_json`, `invalidates_json`.
- no trigger may update an existing `panels(panel_id, revision)` historical row.

- [ ] **Step 2: Run the test and verify failure**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py`  
Expected: FAIL because the tables/schema do not exist.

- [ ] **Step 3: Implement the schema additions**

Add the two tables, foreign keys/indexes, and JSON schema required fields. Use append-only rows for change records.

- [ ] **Step 4: Run the test and verify PASS**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add database/aut_panel_schema.sql schemas/aut_panel_candidate_revision_v1.schema.json tests/test_aut_panel_candidate_revision.py
git commit -m "feat: add AUT panel candidate revision contract"
```

### Task 2: Candidate Revision Service

**Files:**
- Create: `pipeline/aut_panel_candidate_revision.py`
- Modify: `pipeline/aut_panel_db.py`
- Test: `tests/test_aut_panel_candidate_revision.py`

**Interfaces:**
- Consumes: `create_candidate(db_path, panel_id, source_revision, trigger, canonical_inputs) -> dict`.
- Produces: `apply_change(db_path, candidate_id, change) -> dict`, `rollback_candidate(db_path, candidate_id) -> dict`.

- [ ] **Step 1: Write failing service tests**

Add tests for:
- `create_candidate(...)` returns a new revision ID and preserves the source row byte-for-byte.
- repeated creation returns distinct candidate IDs without changing R02.
- `apply_change(...)` writes one delta row and downstream invalidations.
- transaction rollback removes partial writes on exception.
- `rollback_candidate(...)` marks candidate abandoned without deleting history.

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py`  
Expected: FAIL because the service is missing.

- [ ] **Step 3: Implement the service**

Exact public API:
```python
def create_candidate(db_path: Path, *, panel_id: str, source_revision: str,
                     trigger: dict[str, Any], canonical_inputs: dict[str, str]) -> dict[str, Any]: ...
def apply_change(db_path: Path, *, candidate_id: str, change: dict[str, Any]) -> dict[str, Any]: ...
def rollback_candidate(db_path: Path, *, candidate_id: str, reason: str) -> dict[str, Any]: ...
```

Use SQLite transactions and fail closed on missing source revision or unsupported change type.

- [ ] **Step 4: Run tests to verify PASS**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/aut_panel_candidate_revision.py pipeline/aut_panel_db.py tests/test_aut_panel_candidate_revision.py
git commit -m "feat: add candidate revision service"
```

### Task 3: Authorized Automatic Engineering Change Policy

**Files:**
- Create: `configs/auto_engineering_v1.yaml`
- Modify: `pipeline/evolution_engine.py`
- Modify: `agents/AUT_PANEL_AGENT_SYSTEM.yaml`
- Test: `tests/test_aut_panel_candidate_revision.py`

**Interfaces:**
- Consumes: candidate change proposal and policy config.
- Produces: `classify_candidate_change(change: dict, policy: dict) -> dict` with `allowed`, `requires_candidate_revision`, `release_requires_human`, `reason`.

- [ ] **Step 1: Write failing policy tests**

Test:
- enclosure change, component substitution, quantity change and layout change are allowed only in candidate revision;
- Golden Rule modification remains denied;
- release approval, auto-merge and production PLC download remain denied;
- unsupported change types fail closed.

- [ ] **Step 2: Run the tests**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py -k policy`  
Expected: FAIL.

- [ ] **Step 3: Implement policy classification**

Add `classify_candidate_change(change: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]` to `evolution_engine.py`. Replace blanket `PROPOSAL_ONLY` behavior only for explicitly authorized candidate-revision changes; locked release/governance actions remain human-only.

- [ ] **Step 4: Update the agent registry**

Change LAYOUT_OPTIMIZER decision policy from unconditional user decision on enclosure/split to governed candidate-generation mode. Add `AUTO_ENGINEERING_COORDINATOR` with write scope limited to candidate-revision artifacts.

- [ ] **Step 5: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_candidate_revision.py tests/test_aut_panel_agent_system.py`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add configs/auto_engineering_v1.yaml pipeline/evolution_engine.py agents/AUT_PANEL_AGENT_SYSTEM.yaml tests/test_aut_panel_candidate_revision.py
git commit -m "feat: authorize governed candidate engineering changes"
```

### Task 4: Layout Capacity → Automatic Enclosure Candidate

**Files:**
- Modify: `pipeline/layout_optimizer/cli.py`
- Modify: `configs/layout_optimizer_v1.yaml`
- Test: `tests/test_layout_optimizer_capacity.py`
- Test: `tests/test_aut_panel_candidate_revision.py`

**Interfaces:**
- Consumes: `LayoutResult` with `HOLD_LAYOUT_CAPACITY`.
- Produces: selected candidate enclosure proposal linked to a candidate revision; never mutates source panel.

- [ ] **Step 1: Write failing capacity tests**

Assert that:
- capacity failure with validated larger enclosure creates one candidate-revision change;
- source enclosure remains unchanged;
- smallest compliant enclosure is selected deterministically;
- no validated alternative returns `HOLD_LAYOUT_CAPACITY`;
- panel split is proposed only when configured and does not auto-release.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_layout_optimizer_capacity.py tests/test_aut_panel_candidate_revision.py -k enclosure`  
Expected: FAIL.

- [ ] **Step 3: Implement candidate emission**

Expose:
```python
def choose_enclosure_candidate(panel, instances, catalog, config) -> dict | None: ...
```
Use existing `find_larger_enclosure_candidates`; emit a candidate change instead of `USER_DECISION_REQUIRED` when policy allows.

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q tests/test_layout_optimizer_*.py tests/test_aut_panel_candidate_revision.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/layout_optimizer/cli.py configs/layout_optimizer_v1.yaml tests/test_layout_optimizer_capacity.py tests/test_aut_panel_candidate_revision.py
git commit -m "feat: create enclosure candidates on layout capacity failure"
```

### Task 5: Downstream Invalidation and Candidate Regeneration

**Files:**
- Create: `pipeline/aut_panel_candidate_runner.py`
- Modify: `pipeline/pipeline.yaml`
- Test: `tests/test_aut_panel_candidate_runner.py`

**Interfaces:**
- Consumes: candidate ID and candidate-change ledger.
- Produces: ordered stage execution list and candidate artifact manifest.

- [ ] **Step 1: Write failing invalidation tests**

Cover enclosure, component model, quantity, I/O and communication changes. Assert exact invalidated stages and that RELEASE is never auto-executed.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_candidate_runner.py`  
Expected: FAIL.

- [ ] **Step 3: Implement runner**

Public API:
```python
def build_candidate_execution_plan(candidate: dict[str, Any],
                                   pipeline_contract: dict[str, Any]) -> list[str]: ...
def run_candidate(candidate_id: str, *, root: Path, db_path: Path) -> dict[str, Any]: ...
```

Stop at `CANDIDATE_READY_FOR_HUMAN_REVIEW`; do not call RELEASE.

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_candidate_runner.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/aut_panel_candidate_runner.py pipeline/pipeline.yaml tests/test_aut_panel_candidate_runner.py
git commit -m "feat: regenerate invalidated candidate engineering stages"
```

### Task 6: Candidate Release Boundary and Audit Trail

**Files:**
- Create: `pipeline/aut_panel_candidate_gate.py`
- Modify: `AGENTS.md`
- Modify: `context/AUT_PANEL_CONVERSATION_MEMORY.yaml`
- Test: `tests/test_aut_panel_candidate_gate.py`

**Interfaces:**
- Consumes: candidate artifact manifest, QA status, human approval record.
- Produces: `CANDIDATE_READY_FOR_HUMAN_REVIEW`, `HOLD`, or `REPROVADO`; never autonomous RELEASE.

- [ ] **Step 1: Write failing release-boundary tests**

Assert CI PASS without human approval remains candidate-only; auto-merge/deploy flags are rejected; source hashes and rollback target are mandatory.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_candidate_gate.py`  
Expected: FAIL.

- [ ] **Step 3: Implement gate**

Public API:
```python
def evaluate_candidate(candidate_manifest: dict[str, Any],
                       approval_record: dict[str, Any] | None = None) -> dict[str, Any]: ...
```

Even with a valid human approval record, return a release authorization artifact; do not perform merge, fabrication or PLC deployment.

- [ ] **Step 4: Run focused and full regression**

Run:
```bash
python -m pytest -q tests/test_aut_panel_candidate_*.py
python -m pytest -q tests/test_aut_panel_agent_system.py tests/test_layout_optimizer_*.py
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pipeline/aut_panel_candidate_gate.py AGENTS.md context/AUT_PANEL_CONVERSATION_MEMORY.yaml tests/test_aut_panel_candidate_gate.py
git commit -m "feat: enforce human release boundary for candidate engineering"
```
