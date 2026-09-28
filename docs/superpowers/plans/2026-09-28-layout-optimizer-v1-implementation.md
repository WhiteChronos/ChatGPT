# Layout Optimizer V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deterministic OR-Tools-based panel layout optimizer that derives valid component, DIN-rail, wireway, terminal, and cable-gland positions from frozen LI/BOM and validated Data Center dimensions, diagnoses capacity failures, generates larger-enclosure and multi-panel split alternatives without auto-selecting them, and feeds the existing deterministic SVG renderer.

**Architecture:** Add a focused `pipeline/layout_optimizer/` package behind a single façade and CLI. The optimizer consumes existing LI/BOM/Data Center/Data Sheet contracts, converts them into a normalized geometry model, solves hard constraints with CP-SAT, ranks valid layouts with versioned soft objectives, emits a normalized layout result, then reuses the existing render/QA path. Capacity alternatives are advisory and end in `USER_DECISION_REQUIRED`; they never mutate canonical Data Center/Data Sheet/LI files.

**Tech Stack:** Python 3.12, Google OR-Tools CP-SAT, NetworkX, JSON/YAML, existing AUT Panel control/QA code, pytest. OpenCV/CairoSVG remain render-QA integrations and are not required for the first solver task.

**Spec:** `docs/superpowers/specs/2026-09-28-layout-optimizer-memory-ml-design.md`

## Global Constraints

- The canonical engineering sequence remains `BOOTSTRAP -> DATACENTER -> DATASHEET -> SELECT -> LI_QUANTITY -> LOAD_BALANCE -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> MEMORY_SYNC -> RELEASE`.
- LI remains the single quantity source; BOM/layout/render quantities must equal the frozen LI.
- The optimizer must never delete, substitute, scale, distort, or silently rotate a BOM component.
- Missing critical dimensions, mounting constraints, or source evidence produce `HOLD_LAYOUT_INPUT`.
- The locked enclosure may not be enlarged automatically.
- An infeasible locked enclosure produces `HOLD_LAYOUT_CAPACITY`.
- Larger-enclosure and split-panel analyses are candidate generation only and end in `USER_DECISION_REQUIRED`.
- HMI remains on the approved door surface.
- Lower cable-entry, lower wireway, bend-clearance, terminal, and gland zones remain distinct.
- Deterministic hard-constraint failure always overrides soft objectives and ML.
- Solver settings, objective weights, seed, time limit, and generated artifact hashes must be recorded for reproducibility.
- Existing approved workbook/image templates and Golden Rules are not changed by this plan.
- Persistent memory and ML training infrastructure are separate implementation plans; this plan only emits structured optimizer diagnostics/events that those subsystems can later ingest.

## Review Focus

1. **Grouped LI tags with quantity > 1** — the optimizer must expand them into deterministic physical instances without changing the frozen LI quantity.
2. **Catalog component missing width/height/depth** — the run must stop with `HOLD_LAYOUT_INPUT`, never guess dimensions.
3. **Solver timeout without proof of infeasibility** — report `HOLD_LAYOUT_SOLVER_TIMEOUT`, not `HOLD_LAYOUT_CAPACITY` and never PASS.
4. **Split candidate that severs mandatory controller/I/O or power dependencies** — reject the partition before presenting it.
5. **Candidate layout valid geometrically but below required reserve or lower-zone constraints** — return HOLD/invalid candidate rather than rendering it.

---

## File Structure

### Create

- `pipeline/layout_optimizer/__init__.py` — stable public API exports.
- `pipeline/layout_optimizer/models.py` — typed domain records and status constants.
- `pipeline/layout_optimizer/normalize.py` — convert LI/BOM/Data Center/Data Sheet into physical instances and constraints.
- `pipeline/layout_optimizer/geometry.py` — deterministic rectangle, clearance, zone, and validation helpers.
- `pipeline/layout_optimizer/solver.py` — OR-Tools CP-SAT single-enclosure solver.
- `pipeline/layout_optimizer/infrastructure.py` — DIN-rail, wireway, terminal-strip, and cable-gland generation.
- `pipeline/layout_optimizer/capacity.py` — infeasibility diagnostics and larger-enclosure candidate search.
- `pipeline/layout_optimizer/partition.py` — NetworkX dependency graph and technically valid split candidates.
- `pipeline/layout_optimizer/export.py` — normalized layout JSON/Data Sheet placement export and solver manifest.
- `pipeline/layout_optimizer/cli.py` — command-line entry point.
- `configs/layout_optimizer_v1.yaml` — versioned hard/soft solver defaults and objective weights.
- `schemas/layout_optimizer_result_v1.schema.json` — result/artifact contract.
- `tests/test_layout_optimizer_models.py`
- `tests/test_layout_optimizer_normalize.py`
- `tests/test_layout_optimizer_solver.py`
- `tests/test_layout_optimizer_infrastructure.py`
- `tests/test_layout_optimizer_capacity.py`
- `tests/test_layout_optimizer_partition.py`
- `tests/test_layout_optimizer_export.py`
- `tests/fixtures/layout_optimizer/*.json` — deterministic synthetic fixtures.

### Modify

- `requirements-dev.txt` — add pinned OR-Tools and NetworkX versions used by CI.
- `pipeline/aut_panel_standard.py` — add optional optimizer invocation before render; preserve existing validation path.
- `pipeline/render_panel_scaled.py` — accept optimizer-produced placements only after contract validation.
- `pipeline/AUT_PANEL_PIPELINE.json` — register optimizer artifact/contract without reordering stages.
- `pipeline/pipeline.yaml` — register optimizer implementation under the existing LAYOUT stage without changing stage order.
- `agents/AUT_PANEL_AGENT_SYSTEM.yaml` — point `LAYOUT_OPTIMIZER` at the new façade/result contract.
- `.github/workflows/aut-panel-learning.yml` or `.github/workflows/aut-panel-quality.yml` — install layout dependencies and run optimizer regression tests.
- `tests/test_aut_panel_control.py` — regression proving legacy renderer consumes optimizer placements without changing geometry rules.

---

### Task 1: Define normalized layout domain model and status contract

**Files:**
- Create: `pipeline/layout_optimizer/models.py`
- Create: `pipeline/layout_optimizer/__init__.py`
- Create: `schemas/layout_optimizer_result_v1.schema.json`
- Test: `tests/test_layout_optimizer_models.py`

**Interfaces:**
- Consumes: plain normalized engineering values in millimetres.
- Produces:
  - `LayoutStatus`
  - `RectMM`
  - `ClearanceMM`
  - `PhysicalInstance`
  - `PanelGeometry`
  - `LayoutConfig`
  - `Placement`
  - `LayoutMetrics`
  - `LayoutResult`
  - `CapacityAlternative`

- [ ] **Step 1: Write failing tests for status values, rectangle geometry, immutable dataclasses, and JSON-schema-required result fields.**

Tests must assert exact statuses:
`LAYOUT_FEASIBLE`, `LAYOUT_VALIDATED`, `HOLD_LAYOUT_INPUT`, `HOLD_LAYOUT_CAPACITY`, `HOLD_LAYOUT_SOLVER_TIMEOUT`, `HOLD_LAYOUT_THERMAL`, `HOLD_LAYOUT_EMC`, `HOLD_LAYOUT_CABLE_ENTRY`, `USER_DECISION_REQUIRED`.

- [ ] **Step 2: Run `pytest -q tests/test_layout_optimizer_models.py` and verify failure because the module/contracts do not exist.**

- [ ] **Step 3: Implement the typed records and stable serialization methods in `models.py`; export public symbols from `__init__.py`.**

Required signatures:
`RectMM.right -> float`, `RectMM.top -> float`, `RectMM.area_mm2 -> float`, `LayoutResult.to_dict() -> dict[str, Any]`.

- [ ] **Step 4: Implement `schemas/layout_optimizer_result_v1.schema.json` with required panel/revision/status/placements/metrics/solver_manifest/diagnostics/alternatives fields.**

- [ ] **Step 5: Re-run the model tests; expected PASS.**

- [ ] **Step 6: Commit `feat(layout): add optimizer domain model and result schema`.**

---

### Task 2: Normalize LI/BOM/Data Center/Data Sheet into physical instances

**Files:**
- Create: `pipeline/layout_optimizer/normalize.py`
- Create: `tests/test_layout_optimizer_normalize.py`
- Create fixtures: `tests/fixtures/layout_optimizer/normalization_*.json`

**Interfaces:**
- Consumes:
  - `normalize_inputs(panel_id: str, li: Mapping[str, Any], bom: Mapping[str, Any], catalog: Mapping[str, Any], project: Mapping[str, Any], config: LayoutConfig) -> tuple[PanelGeometry, list[PhysicalInstance], list[str]]`
- Produces normalized instances and diagnostics for Task 3+.

- [ ] **Step 1: Write failing tests proving LI/BOM quantity parity, grouped-tag deterministic expansion, HMI door assignment, enclosure/plate geometry extraction, and missing-dimension HOLD diagnostics.**

Grouped quantity example must deterministically expand `BAT-01A/B` quantity 2 into stable instance IDs `BAT-01A/B#01` and `BAT-01A/B#02` while retaining source tag `BAT-01A/B`.

- [ ] **Step 2: Add a failing test for a catalog item with `dimensions_mm: null`; expected diagnostic `MISSING_DIMENSIONS:<catalog_id>` and no solver-ready instance for that item.**

- [ ] **Step 3: Run normalization tests; expected FAIL.**

- [ ] **Step 4: Implement normalization with strict source parity and no inferred dimensions.**

Special physical infrastructure tags (`DIN-*`, `WD-*`, `CG-*`) must be classified as infrastructure requests rather than ordinary component rectangles; their quantities remain traceable to LI.

- [ ] **Step 5: Re-run tests; expected PASS.**

- [ ] **Step 6: Commit `feat(layout): normalize frozen LI and BOM for solver`.**

---

### Task 3: Add deterministic geometry and hard-constraint helpers

**Files:**
- Create: `pipeline/layout_optimizer/geometry.py`
- Create: `tests/test_layout_optimizer_geometry.py`

**Interfaces:**
- Consumes: `RectMM`, `ClearanceMM`, `PanelGeometry`, placement candidates.
- Produces:
  - `expanded_rect(rect: RectMM, clearance: ClearanceMM) -> RectMM`
  - `overlaps(a: RectMM, b: RectMM) -> bool`
  - `inside(rect: RectMM, boundary: RectMM) -> bool`
  - `validate_hard_geometry(...) -> list[str]`

- [ ] **Step 1: Write failing boundary, exact-touch, overlap, clearance-expansion, door-vs-plate, and lower-zone tests.**

- [ ] **Step 2: Run geometry tests; expected FAIL.**

- [ ] **Step 3: Implement helpers using millimetres only; touching expanded keep-out envelopes is allowed only when `right <= left`/equivalent proves no intersection.**

- [ ] **Step 4: Re-run tests; expected PASS.**

- [ ] **Step 5: Commit `feat(layout): add deterministic hard-geometry checks`.**

---

### Task 4: Implement OR-Tools single-enclosure component solver

**Files:**
- Create: `pipeline/layout_optimizer/solver.py`
- Create: `configs/layout_optimizer_v1.yaml`
- Create: `tests/test_layout_optimizer_solver.py`
- Modify: `requirements-dev.txt`

**Interfaces:**
- Consumes:
  - `solve_single_panel(panel: PanelGeometry, instances: Sequence[PhysicalInstance], reserved_zones: Sequence[RectMM], config: LayoutConfig) -> LayoutResult`
- Produces valid component placements or a non-final solver status with diagnostics.

- [ ] **Step 1: Add pinned `ortools` dependency and versioned config fields for `solver_seed`, `max_time_seconds`, `coordinate_resolution_mm`, and objective weights.**

- [ ] **Step 2: Write a failing easy-fit fixture test asserting every physical instance is placed exactly once, all coordinates are within bounds, and no expanded rectangles overlap.**

- [ ] **Step 3: Write a failing tight-fit deterministic regression asserting two identical runs with the same seed/config produce the same placement ordering and coordinates.**

- [ ] **Step 4: Write the Review Focus timeout test: force an effectively zero time limit and assert `HOLD_LAYOUT_SOLVER_TIMEOUT`, not `HOLD_LAYOUT_CAPACITY`.**

- [ ] **Step 5: Run solver tests; expected FAIL.**

- [ ] **Step 6: Implement CP-SAT integer-coordinate placement, using configured millimetre resolution, AddNoOverlap2D, allowed surfaces/orientations, panel bounds, reserved zones, and deterministic search settings.**

Do not infer infeasibility from `UNKNOWN`; only map CP-SAT `INFEASIBLE` to `HOLD_LAYOUT_CAPACITY`.

- [ ] **Step 7: Add soft objectives in this order: minimize occupied envelope, minimize Manhattan distance between connected/grouped devices when connection metadata exists, maximize bottom-zone separation margin. Record weights in the solver manifest.**

- [ ] **Step 8: Re-run solver tests; expected PASS.**

- [ ] **Step 9: Commit `feat(layout): add deterministic OR-Tools panel solver`.**

---

### Task 5: Generate DIN rails, wireways, terminal strips, and cable glands

**Files:**
- Create: `pipeline/layout_optimizer/infrastructure.py`
- Create: `tests/test_layout_optimizer_infrastructure.py`

**Interfaces:**
- Consumes solved ordinary component placements, infrastructure requests from LI, panel geometry, lower-zone contract, component mounting metadata.
- Produces:
  - `build_din_rails(...) -> list[Placement]`
  - `build_wireways(...) -> list[Placement]`
  - `build_terminal_strips(...) -> list[Placement]`
  - `build_cable_glands(...) -> list[Placement]`
  - updated infrastructure diagnostics.

- [ ] **Step 1: Write failing tests for rail-mounted component grouping and exact rail length calculation from real occupied widths plus configured edge allowance.**

- [ ] **Step 2: Write failing lower-zone test asserting cable glands, cable-exit region, bend-clearance region, lower wireway, and terminal strip occupy distinct non-overlapping bands.**

- [ ] **Step 3: Write failing cable-gland overcrowding fixture asserting `HOLD_LAYOUT_CABLE_ENTRY`.**

- [ ] **Step 4: Write Review Focus test: a geometrically valid layout that violates reserve/lower-zone requirements is not renderable.**

- [ ] **Step 5: Run infrastructure tests; expected FAIL.**

- [ ] **Step 6: Implement infrastructure generation without changing LI quantities. Infrastructure placement may choose geometry, but its source LI tag/quantity remains in result provenance.**

- [ ] **Step 7: Re-run tests; expected PASS.**

- [ ] **Step 8: Commit `feat(layout): solve rails wireways terminals and glands`.**

---

### Task 6: Calculate layout metrics and final single-panel validation

**Files:**
- Modify: `pipeline/layout_optimizer/solver.py`
- Create: `pipeline/layout_optimizer/metrics.py`
- Create: `tests/test_layout_optimizer_metrics.py`

**Interfaces:**
- Consumes all solved placements and panel geometry.
- Produces:
  - `calculate_metrics(...) -> LayoutMetrics`
  - `validate_layout_result(...) -> LayoutResult`

- [ ] **Step 1: Write failing tests for occupied area, free reserve percentage, minimum clearance, overlap count, rail count, wireway count, terminal count, and gland count.**

- [ ] **Step 2: Run metric tests; expected FAIL.**

- [ ] **Step 3: Implement metrics with no use of generated raster images.**

- [ ] **Step 4: Validate minimum reserve from `enclosure.minimum_free_reserve_percent`; below target produces HOLD diagnostics and is not promoted to `LAYOUT_VALIDATED`.**

- [ ] **Step 5: Re-run tests; expected PASS.**

- [ ] **Step 6: Commit `feat(layout): add deterministic layout metrics and validation`.**

---

### Task 7: Diagnose capacity failure and generate larger-enclosure candidates

**Files:**
- Create: `pipeline/layout_optimizer/capacity.py`
- Create: `tests/test_layout_optimizer_capacity.py`
- Create fixtures: `tests/fixtures/layout_optimizer/capacity_*.json`

**Interfaces:**
- Consumes failed single-enclosure result, component catalog, approved enclosure catalog entries, and solver façade.
- Produces:
  - `diagnose_capacity(...) -> list[str]`
  - `find_larger_enclosure_candidates(...) -> list[CapacityAlternative]`

- [ ] **Step 1: Write a failing impossible-enclosure fixture asserting `HOLD_LAYOUT_CAPACITY` only when CP-SAT proves infeasibility.**

- [ ] **Step 2: Write a failing diagnostic test requiring binding reasons such as available plate envelope, lower-zone consumption, minimum required component envelope, and missing reserve.**

- [ ] **Step 3: Write a failing larger-enclosure test where catalog candidates are evaluated smallest-first and only candidates that produce `LAYOUT_VALIDATED` appear in alternatives.**

- [ ] **Step 4: Assert every alternative has `requires_user_decision == true` and never mutates input project/enclosure data.**

- [ ] **Step 5: Implement diagnostics and candidate search.**

- [ ] **Step 6: Re-run tests; expected PASS.**

- [ ] **Step 7: Commit `feat(layout): add capacity diagnostics and enclosure alternatives`.**

---

### Task 8: Build dependency graph and technically valid multi-panel split alternatives

**Files:**
- Create: `pipeline/layout_optimizer/partition.py`
- Create: `tests/test_layout_optimizer_partition.py`
- Modify: `requirements-dev.txt` to add pinned NetworkX.

**Interfaces:**
- Consumes physical instances, architecture/I/O metadata, optional connection records, power/controller dependencies, and solver façade.
- Produces:
  - `build_dependency_graph(...) -> networkx.Graph`
  - `generate_split_candidates(...) -> list[CapacityAlternative]`
  - `validate_partition(...) -> list[str]`

- [ ] **Step 1: Write failing graph tests for controller-to-I/O, power-supply-to-load, network, field-area/floor, and interlock relationships.**

- [ ] **Step 2: Write candidate-strategy tests for power/control, VFD/control, floor/area, main/remote-I/O, thermal, EMC, and cable-concentration partitions when the fixture contains the necessary metadata.**

- [ ] **Step 3: Write Review Focus test: severing a mandatory controller/I/O or required shared power dependency without an explicit inter-panel replacement link rejects the candidate.**

- [ ] **Step 4: Write test asserting each accepted split solves every child panel and reports new inter-panel links, communication, power, and I/O impacts.**

- [ ] **Step 5: Write test asserting split alternatives end in `USER_DECISION_REQUIRED` and no candidate is marked selected/recommended as a final decision.**

- [ ] **Step 6: Implement graph building, strategy generation, validation, child-panel solve, and Pareto non-dominance filtering over size/occupancy/inter-panel-complexity/reserve metrics.**

Pareto output may order deterministically for display, but must not declare a winner.

- [ ] **Step 7: Re-run tests; expected PASS.**

- [ ] **Step 8: Commit `feat(layout): add graph-based panel split alternatives`.**

---

### Task 9: Export canonical optimizer result and bridge to existing renderer

**Files:**
- Create: `pipeline/layout_optimizer/export.py`
- Create: `tests/test_layout_optimizer_export.py`
- Modify: `pipeline/aut_panel_standard.py`
- Modify: `pipeline/render_panel_scaled.py`
- Modify: `tests/test_aut_panel_control.py`

**Interfaces:**
- Consumes `LayoutResult`.
- Produces:
  - `export_layout_result(result: LayoutResult, output: Path) -> Path`
  - `apply_layout_to_project(project: Mapping[str, Any], result: LayoutResult) -> dict[str, Any]`

- [ ] **Step 1: Write failing export-schema test and placement parity test.**

- [ ] **Step 2: Write failing regression asserting `apply_layout_to_project` changes only placement coordinates/infrastructure result fields allowed by the optimizer contract and does not change LI tags, catalog IDs, quantities, enclosure dimensions, or visual-template IDs.**

- [ ] **Step 3: Write failing renderer regression proving `gerar_svg` consumes optimizer placements and preserves GR-021/022/023/024/025/026/037/040/044.**

- [ ] **Step 4: Implement export and render bridge.**

- [ ] **Step 5: Re-run export plus existing panel-control regression tests; expected PASS.**

- [ ] **Step 6: Commit `feat(layout): bridge optimized placements to canonical renderer`.**

---

### Task 10: Add CLI façade and fail-closed end-to-end pipeline

**Files:**
- Create: `pipeline/layout_optimizer/cli.py`
- Modify: `pipeline/layout_optimizer/__init__.py`
- Create: `tests/test_layout_optimizer_cli.py`

**Interfaces:**
- Produces:
  - `optimize_panel(...) -> LayoutResult`
  - CLI: `python -m pipeline.layout_optimizer.cli optimize ...`

- [ ] **Step 1: Write failing CLI tests for feasible panel, missing dimension, proven infeasible panel, timeout, larger-enclosure alternatives, and split alternatives.**

- [ ] **Step 2: Implement `optimize_panel` orchestration: normalize -> solve -> infrastructure -> metrics -> validate -> if capacity fail generate alternatives -> export.**

- [ ] **Step 3: Enforce exit codes: `0` for `LAYOUT_VALIDATED`; `2` for REPROVADO-type contract violation; `3` for HOLD; `4` for `USER_DECISION_REQUIRED`.**

- [ ] **Step 4: Re-run CLI tests; expected PASS.**

- [ ] **Step 5: Commit `feat(layout): add fail-closed optimizer CLI`.**

---

### Task 11: Register optimizer in canonical contracts without changing stage order

**Files:**
- Modify: `pipeline/pipeline.yaml`
- Modify: `pipeline/AUT_PANEL_PIPELINE.json`
- Modify: `agents/AUT_PANEL_AGENT_SYSTEM.yaml`
- Modify: `docs/AUT_PANEL_AGENT_SYSTEM.md`
- Test: `tests/test_layout_optimizer_contracts.py`

**Interfaces:**
- Consumes current immutable registries.
- Produces registry pointers to optimizer façade/config/result schema.

- [ ] **Step 1: Write failing contract tests asserting the canonical stage sequence is unchanged and `LAYOUT` references the new optimizer implementation/result schema.**

- [ ] **Step 2: Add `LAYOUT_OPTIMIZER_V1` metadata under the existing LAYOUT stage rather than adding/reordering canonical stages.**

- [ ] **Step 3: Register the LAYOUT_OPTIMIZER agent implementation path, config path, result schema, and human-decision behavior.**

- [ ] **Step 4: Re-run contract tests and existing conversation/quality tests; expected PASS.**

- [ ] **Step 5: Commit `chore(layout): register optimizer in canonical contracts`.**

---

### Task 12: CI, deterministic fixtures, and full regression

**Files:**
- Modify: `.github/workflows/aut-panel-learning.yml`
- Modify: `.github/workflows/aut-panel-quality.yml` if necessary
- Add: `tests/fixtures/layout_optimizer/*.json`
- Modify/add optimizer tests listed above.

**Interfaces:**
- Consumes full implementation.
- Produces reproducible CI evidence.

- [ ] **Step 1: Add pinned dependency installation and optimizer test paths to CI.**

- [ ] **Step 2: Add fixtures for easy fit, tight fit, impossible enclosure, larger enclosure, power/control split, main/remote-I/O split, cable-entry bottleneck, thermal metadata, conflicting hard constraints, and missing dimensions.**

- [ ] **Step 3: Run locally/CI: `python -m compileall -q pipeline tests`. Expected PASS.**

- [ ] **Step 4: Run `pytest -q tests/test_layout_optimizer_*.py`. Expected PASS.**

- [ ] **Step 5: Run the existing regression suite required by AUT Panel Quality. Expected PASS.**

- [ ] **Step 6: Run optimizer twice against the deterministic synthetic fit fixture and compare normalized result JSON excluding timestamps; expected byte-identical normalized solver/placement output.**

- [ ] **Step 7: Run the optimizer against PN-AUT-01/PN-AUT-02 current project data. If critical component dimensions remain missing in the canonical catalog, expected result is `HOLD_LAYOUT_INPUT`; do not fabricate dimensions to force a PASS.**

- [ ] **Step 8: Verify no approved LI quantity, enclosure baseline, workbook fingerprint, image fingerprint, or Golden Rule changed.**

- [ ] **Step 9: Commit `test(layout): add optimizer CI and historical regression gates`.**

---

## Self-Review

### Spec coverage

This plan implements the Layout Optimizer-specific portions of the approved spec: normalized physical model, hard/soft constraints, DIN rails, wireways, terminals, glands, single-enclosure solve, capacity diagnostics, larger-enclosure alternatives, multi-panel split analysis, human decision gate, deterministic render bridge, status model, error handling, and regression/CI.

The following approved-spec subsystems are intentionally **not implemented in this plan** because they are independently reviewable systems and should have separate plans:

- persistent GitHub/JSONL/YAML memory event store and hash chain;
- SQLite rebuild/bootstrap from repository memory;
- River training/model evolution pipeline beyond existing cold-start code;
- MLflow/DVC/Evidently/Qdrant deferred integrations;
- plugin promotion automation.

The optimizer emits structured diagnostics and artifacts so those later systems can ingest them without changing the optimizer interface.

### Type consistency

All downstream tasks consume the model types introduced in Task 1. The single-panel solver returns `LayoutResult`; capacity and partition analysis return `CapacityAlternative`; export/CLI consume the same records.

### Review Focus coverage

- grouped LI quantity expansion -> Task 2;
- missing dimensions -> Tasks 2 and 12;
- solver timeout -> Tasks 4 and 10;
- invalid dependency split -> Task 8;
- reserve/lower-zone false-positive layout -> Tasks 5 and 6.

### Scope/proportion

The plan deliberately keeps persistent memory and ML evolution out of the Layout Optimizer implementation boundary. Those will receive separate implementation plans after the optimizer core is reviewed and stable.
