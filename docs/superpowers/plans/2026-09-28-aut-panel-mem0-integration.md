# AUT Panel Mem0 Auxiliary Memory Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional Mem0-based contextual retrieval without allowing memory to become an engineering authority or break operation when disabled/unavailable.

**Architecture:** Keep Git/SQLite as canonical memory and add a backend-only Mem0 adapter behind `MEM0_ENABLED`. Eligible canonical events are mirrored to Mem0 with provenance metadata; retrieved memories are reconciled against current repository authority before entering agent context.

**Tech Stack:** Python 3.12, existing SQLite memory events, `mem0ai` pinned after compatibility verification, pytest.

**Spec:** `docs/superpowers/specs/2026-09-28-aut-panel-auto-engineering-design.md`

## Global Constraints

- Mem0 is additive and optional.
- Feature disabled => existing behavior unchanged.
- No API keys or memory writes in client-side artifacts.
- Every mirrored memory references canonical event ID and source hashes.
- Retrieved memory cannot mutate engineering directly.
- Superseded/historical records are contextual only.
- Failure or unavailability of Mem0 must not corrupt canonical state.

## Review Focus

- Cross-panel memory leakage between PN-AUT-01 and PN-AUT-02.
- Old revision returned above current revision.
- Mem0 unavailable during candidate generation.
- Duplicate mirroring of the same canonical event.
- Retrieved content containing instructions that conflict with Golden Rules.

---

### Task 1: Mem0 Configuration and Adapter Contract

**Files:**
- Create: `configs/mem0_v1.yaml`
- Create: `pipeline/aut_panel_mem0.py`
- Modify: `requirements-ml.txt`
- Test: `tests/test_aut_panel_mem0.py`

**Interfaces:**
- Produces:
```python
class MemoryBackend(Protocol):
    def add_event(self, event: dict[str, Any]) -> str: ...
    def search(self, *, query: str, panel_id: str, panel_revision: str | None, limit: int) -> list[dict[str, Any]]: ...
```
- Concrete `NullMemoryBackend` and `Mem0MemoryBackend`.

- [ ] **Step 1: Write failing adapter tests**

Test null backend, feature-off behavior, metadata fields and no import-time dependency failure when Mem0 is disabled.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_mem0.py`  
Expected: FAIL.

- [ ] **Step 3: Implement minimal adapter and pin**

Pin a compatible `mem0ai` version only after dependency resolution against the project environment. Do not vendor `WhiteChronos/mem0` into the repository.

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_mem0.py`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add configs/mem0_v1.yaml pipeline/aut_panel_mem0.py requirements-ml.txt tests/test_aut_panel_mem0.py
git commit -m "feat: add optional Mem0 backend"
```

### Task 2: Canonical Event Mirroring

**Files:**
- Modify: `pipeline/aut_panel_db.py`
- Modify: `pipeline/aut_panel_mem0.py`
- Test: `tests/test_aut_panel_mem0.py`

**Interfaces:**
- Consumes existing `record_memory_event(...)`.
- Produces `mirror_memory_event(event_id, *, db_path, backend) -> dict`.

- [ ] **Step 1: Write failing mirroring tests**

Assert idempotency by canonical event ID, panel/revision metadata, evidence hash propagation and canonical DB success even when Mem0 fails.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_mem0.py -k mirror`  
Expected: FAIL.

- [ ] **Step 3: Implement mirroring**

Mirror only after the SQLite event commits. Store mirror status separately; never roll back canonical event because Mem0 failed.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_mem0.py`  
Expected: PASS.

```bash
git add pipeline/aut_panel_db.py pipeline/aut_panel_mem0.py tests/test_aut_panel_mem0.py
git commit -m "feat: mirror canonical memory events to Mem0"
```

### Task 3: Retrieval Reconciliation

**Files:**
- Create: `pipeline/aut_panel_memory_context.py`
- Modify: `pipeline/context_manifest.py`
- Test: `tests/test_aut_panel_memory_context.py`

**Interfaces:**
- Produces:
```python
def retrieve_context(*, query: str, panel_id: str, panel_revision: str,
                     backend: MemoryBackend, canonical_state: dict[str, Any]) -> dict[str, Any]: ...
```

- [ ] **Step 1: Write failing reconciliation tests**

Cover wrong panel, superseded revision, missing provenance, conflicting dimension, malicious/conflicting instruction and valid regression-memory retrieval.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_memory_context.py`  
Expected: FAIL.

- [ ] **Step 3: Implement reconciliation**

Return `accepted`, `historical`, `rejected` lists with reasons. Only accepted context may enter agent manifests.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_memory_context.py tests/test_aut_panel_fast_context.py`  
Expected: PASS.

```bash
git add pipeline/aut_panel_memory_context.py pipeline/context_manifest.py tests/test_aut_panel_memory_context.py
git commit -m "feat: reconcile Mem0 context against canonical engineering state"
```

### Task 4: Agent Integration and Failure Isolation

**Files:**
- Modify: `agents/AUT_PANEL_AGENT_SYSTEM.yaml`
- Modify: `AGENTS.md`
- Modify: `skills/aut-panel-engineering/SKILL.md`
- Test: `tests/test_aut_panel_agent_system.py`

**Interfaces:**
- Consumes reconciled context manifest only.
- Produces no direct engineering writes from Mem0.

- [ ] **Step 1: Write failing agent-contract tests**

Assert MEMORY_CURATOR owns mirroring, ORCHESTRATOR may read reconciled context, engineering agents cannot write to Mem0 directly, and Mem0 outage is non-authoritative.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_agent_system.py -k memory`  
Expected: FAIL.

- [ ] **Step 3: Update contracts and documentation**

Document feature flag, source hierarchy and failure behavior.

- [ ] **Step 4: Run regression and commit**

Run: `python -m pytest -q tests/test_aut_panel_mem0.py tests/test_aut_panel_memory_context.py tests/test_aut_panel_agent_system.py`  
Expected: PASS.

```bash
git add agents/AUT_PANEL_AGENT_SYSTEM.yaml AGENTS.md skills/aut-panel-engineering/SKILL.md tests/test_aut_panel_agent_system.py
git commit -m "feat: integrate reconciled Mem0 context with AUT panel agents"
```
