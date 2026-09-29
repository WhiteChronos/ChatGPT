# AUT Panel Memory Benchmark Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evaluate AUT Panel memory retrieval for revision isolation, stale-memory suppression and regression-context precision without conflating benchmark scores with engineering approval.

**Architecture:** Keep the benchmark in a separate evaluation surface. Build a PN-AUT dataset and provider adapter compatible with Agent Memory Benchmark concepts; run it against null/BM25/Mem0 backends with pinned inputs and emit machine-readable reports consumed only by memory-quality gates.

**Tech Stack:** Python 3.12, pytest, JSONL/JSON, optional external Agent Memory Benchmark checkout pinned by commit.

**Spec:** `docs/superpowers/specs/2026-09-28-aut-panel-auto-engineering-design.md`

## Global Constraints

- Benchmark outputs are advisory quality evidence, never engineering-release evidence.
- Dataset fixtures must not contain confidential source documents.
- External benchmark code is not vendored until license review is resolved.
- External repository commit must be pinned.
- Evaluation cases must distinguish current, historical, rejected and cross-panel memories.

## Review Focus

- A system returning many memories must fail precision tests when noise includes wrong panel/revision.
- Benchmark must not pass solely because fixed local context answers the case.
- Provider result IDs must map deterministically to canonical event IDs.
- Missing external benchmark dependency must skip external comparison cleanly, not break engineering CI.
- Score changes must be reproducible from pinned dataset and configuration.

---

### Task 1: PN-AUT Memory Evaluation Dataset

**Files:**
- Create: `memory/benchmark/pn_aut_memory_cases.json`
- Create: `schemas/pn_aut_memory_benchmark_v1.schema.json`
- Test: `tests/test_aut_panel_memory_benchmark.py`

**Interfaces:**
- Each case declares `query`, `panel_id`, `panel_revision`, `must_include_event_ids`, `must_exclude_event_ids`, and `category`.

- [ ] **Step 1: Write failing fixture tests**

Include cases for stale dimensions, cross-panel contamination, duplicate-door regression, cable-entry provenance, removed visual blocks, old PASS reuse and conflicting memory instruction.

- [ ] **Step 2: Run test**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py`  
Expected: FAIL until schema/data exist.

- [ ] **Step 3: Add schema and fixtures**

Keep fixtures synthetic or derived from non-confidential repository metadata.

- [ ] **Step 4: Run test and commit**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py`  
Expected: PASS.

```bash
git add memory/benchmark/pn_aut_memory_cases.json schemas/pn_aut_memory_benchmark_v1.schema.json tests/test_aut_panel_memory_benchmark.py
git commit -m "test: add PN-AUT memory precision benchmark dataset"
```

### Task 2: Local Retrieval Benchmark Runner

**Files:**
- Create: `pipeline/aut_panel_memory_benchmark.py`
- Test: `tests/test_aut_panel_memory_benchmark.py`

**Interfaces:**
- Produces:
```python
def run_retrieval_benchmark(cases: list[dict], provider: MemoryBackend) -> dict[str, Any]: ...
```
with per-case precision assertions and aggregate `active_pass_rate`.

- [ ] **Step 1: Write failing runner tests**

Assert exact must-include/must-exclude behavior and no LLM judge.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py -k runner`  
Expected: FAIL.

- [ ] **Step 3: Implement runner**

Score only provider-returned event IDs; preserve raw retrieval evidence.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py`  
Expected: PASS.

```bash
git add pipeline/aut_panel_memory_benchmark.py tests/test_aut_panel_memory_benchmark.py
git commit -m "feat: add deterministic PN-AUT memory benchmark runner"
```

### Task 3: Optional Agent Memory Benchmark Adapter

**Files:**
- Create: `plugins/agent_memory_benchmark_registry.json`
- Create: `scripts/run_external_memory_benchmark.py`
- Test: `tests/test_aut_panel_memory_benchmark.py`

**Interfaces:**
- Consumes pinned external repo commit and local PN-AUT fixtures.
- Produces comparison report without modifying canonical engineering files.

- [ ] **Step 1: Write failing pin/license tests**

Assert registry pins `vectorize-io/agent-memory-benchmark` by commit, records license status, and refuses activation while license status is unresolved.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py -k external`  
Expected: FAIL.

- [ ] **Step 3: Implement registry and wrapper**

Wrapper must exit with a clear HOLD when external benchmark is not approved/installed; no implicit pip/git install in CI.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py`  
Expected: PASS.

```bash
git add plugins/agent_memory_benchmark_registry.json scripts/run_external_memory_benchmark.py tests/test_aut_panel_memory_benchmark.py
git commit -m "feat: add controlled external memory benchmark adapter"
```

### Task 4: Memory Quality Gate

**Files:**
- Create: `pipeline/aut_panel_memory_quality_gate.py`
- Modify: `pipeline/learning_pipeline.yaml`
- Test: `tests/test_aut_panel_memory_benchmark.py`

**Interfaces:**
- Consumes benchmark report.
- Produces `PASS`, `HOLD_MEMORY_QUALITY`, or `REPROVADO_MEMORY_ISOLATION`.

- [ ] **Step 1: Write failing gate tests**

Cross-panel leakage must be REPROVADO; stale-memory miss/noise below configured threshold must HOLD; benchmark PASS cannot set engineering release state.

- [ ] **Step 2: Run tests**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py -k quality_gate`  
Expected: FAIL.

- [ ] **Step 3: Implement gate and learning-stage hook**

Keep gate scoped to memory subsystem health.

- [ ] **Step 4: Run tests and commit**

Run: `python -m pytest -q tests/test_aut_panel_memory_benchmark.py tests/test_aut_panel_mem0.py`  
Expected: PASS.

```bash
git add pipeline/aut_panel_memory_quality_gate.py pipeline/learning_pipeline.yaml tests/test_aut_panel_memory_benchmark.py
git commit -m "feat: gate AUT panel memory quality independently of engineering release"
```
