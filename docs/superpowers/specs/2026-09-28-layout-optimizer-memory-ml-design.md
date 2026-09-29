# AUT Panel Layout Optimizer V1 + Persistent Memory + Controlled ML — Design Specification

**Date:** 2026-09-28  
**Repository:** WhiteChronos/ChatGPT  
**Branch:** feat/aut-panel-control-v1  
**Status:** DESIGN APPROVED IN PRINCIPLE / USER REVIEW REQUIRED  
**Canonical engineering standard:** AUT-PAINEL-COMPACT-V2.4

## 1. Intent

Create a deterministic panel-engineering subsystem that automatically calculates and validates physical panel layouts from approved engineering data, while preserving the project's locked standards, traceability, revision history, and human control.

The system must:

- calculate DIN rails, wireways, clearances, functional zones, terminal blocks, cable glands, reserve, and component placement from real dimensions;
- generate the engineering vector drawing from the solved layout;
- detect when a locked enclosure cannot physically accommodate the approved BOM;
- when capacity fails, evaluate technically valid alternatives such as a larger enclosure or controlled division into multiple panels;
- present alternatives for joint human decision without selecting one automatically;
- maintain persistent project memory independent of chat history;
- learn from reviewed QA/correction history without allowing ML to become an engineering authority;
- continuously propose process improvements through a controlled, reviewable evolution loop.

## 2. Governing principles

The existing canonical engineering pipeline remains authoritative:

`BOOTSTRAP -> DATACENTER -> DATASHEET -> SELECT -> LI_QUANTITY -> LOAD_BALANCE -> BOM -> LAYOUT -> RENDER_IMAGE -> QA -> MEMORY_SYNC -> RELEASE`

The new optimizer is implemented inside the existing `LAYOUT` stage and feeds `RENDER_IMAGE`.

The separate learning/evolution loop remains:

`OBSERVE -> FEATURE_EXTRACT -> TRAIN -> EVALUATE -> PROPOSE -> SANDBOX_SIMULATE -> HUMAN_GATE -> APPLY -> VERSION`

The learning loop may improve heuristics, QA prioritization, search order, layout objectives, and tooling. It may not create engineering facts, change locked standards, approve missing evidence, or override deterministic failures.

## 3. Hard constraints

1. LI remains the single quantity source.
2. BOM must match the frozen LI exactly.
3. The optimizer may not delete, replace, resize, or distort BOM components.
4. Real manufacturer dimensions and mounting constraints are mandatory when available.
5. A missing critical dimension or mounting requirement results in `HOLD`.
6. HMI remains on the approved door/front surface.
7. The external enclosure geometry remains locked unless a controlled change is explicitly approved.
8. The optimizer may calculate a larger enclosure candidate but may not apply it automatically.
9. The optimizer may calculate multi-panel split alternatives but may not choose one automatically.
10. Generated images are not engineering truth; the deterministic vector model derived from the validated BOM/layout is the visual engineering authority.
11. ML is advisory only.
12. Released memory/evidence is append-only and reconstructible.

## 4. Approved open-source core

The initial production core is limited to:

- **Google OR-Tools** — constraint programming and placement optimization;
- **SQLite** — local relational operational database;
- **NetworkX** — connection, communication, I/O, and dependency graphs;
- **OpenCV** — visual QA and geometric comparison;
- **CairoSVG** — deterministic SVG conversion for raster/PDF QA;
- **Pandera** — validation of structured datasets used by optimization and ML;
- **River** — incremental machine learning after the cold-start threshold is satisfied.

The following remain deferred integrations until project data volume or operational need justifies them:

- MLflow;
- DVC;
- Evidently;
- Qdrant;
- Prefect/Dagster or another workflow orchestrator.

Every open-source dependency requires pinned version/commit, license review, security review, and integration tests before becoming active in the canonical pipeline.

## 5. Layout Optimizer V1 architecture

### 5.1 Inputs

The optimizer consumes only validated upstream artifacts:

- panel ID and revision;
- frozen LI;
- BOM;
- Data Center component registry;
- exact component dimensions;
- enclosure and mounting-plate dimensions;
- door-mounted devices;
- DIN-rail mounting requirements;
- terminal-block dimensions;
- wireway dimensions;
- cable-gland dimensions;
- minimum clearances;
- thermal/EMC segregation rules when proven;
- bottom cable-entry constraints;
- reserve target;
- I/O/network dependency graph;
- approved visual-template contract.

Any critical missing engineering input results in `HOLD_LAYOUT_INPUT`.

### 5.2 Internal model

Each physical object is represented as a geometric/engineering entity:

- `component_instance`;
- `din_rail`;
- `wireway`;
- `terminal_strip`;
- `pe_bar`;
- `cable_gland`;
- `door_device`;
- `reserved_zone`;
- `thermal_zone`;
- `emc_zone`;
- `cable_exit_zone`.

Each entity stores:

- width, height, depth;
- mounting surface;
- allowed orientation;
- minimum neighbor clearance;
- preferred functional group;
- rail requirement;
- heat/loss data when verified;
- connectivity/dependency metadata;
- source reference and engineering status.

### 5.3 Constraint model

OR-Tools must model at least:

- enclosure bounds;
- mounting-plate bounds;
- door bounds;
- non-overlap;
- reserved cable-exit region;
- lower wireway separation;
- terminal zone separation;
- minimum bend clearance;
- rail compatibility;
- door-only devices;
- required physical clearances;
- orientation permissions;
- functional grouping;
- access/maintenance space;
- cable-gland count and feasible edge placement;
- protected/forbidden regions;
- panel reserve target.

Constraints are separated into:

- **hard constraints** — violation makes the candidate invalid;
- **soft objectives** — used to improve a valid candidate.

### 5.4 Objective function

The solver must seek a valid layout before optimizing quality.

Candidate soft objectives include:

- minimize occupied envelope;
- maximize usable reserve;
- minimize cable-routing distance;
- minimize communication/power crossings;
- group related devices;
- minimize rail count where practical;
- minimize wireway complexity;
- preserve service access;
- keep terminals close to cable-entry zones;
- reduce thermal concentration;
- improve visual readability.

Weights must be versioned and traceable. Machine learning may propose weight changes, but cannot apply them to the canonical solver without the controlled evolution process.

## 6. DIN rails and wireways

The optimizer may determine rail count, length, and y-position from the actual placed components, but must honor:

- real mounting widths;
- manufacturer mounting requirements;
- minimum edge clearances;
- wireway clearances;
- functional segregation;
- service accessibility;
- lower cable zone.

Wireways are physical objects, not decorative lines. Their width and routing consume layout area and participate in collision tests.

The solver must never reduce wireway dimensions solely to make the BOM fit.

## 7. Terminals and cable glands

Terminal strips must be derived from the frozen LI/BOM and I/O/field requirements.

The solver must:

- place terminal groups in the approved terminal zone;
- preserve PE/FE separation when required;
- associate terminals with field cable groups;
- reserve downstream cable routing area;
- calculate feasible gland placement;
- detect gland overcrowding;
- preserve minimum spacing and bend radius constraints when known.

Cable-gland layout must be traceable to the cable/field connection model rather than arbitrary visual spacing.

## 8. Single-enclosure capacity failure

If no feasible layout exists after exhausting all permitted arrangements within the locked enclosure, the optimizer returns:

`HOLD_LAYOUT_CAPACITY`

It must not:

- distort components;
- reduce scale;
- remove BOM items;
- reduce mandatory clearance;
- eliminate wireways;
- alter the LI;
- silently substitute components;
- enlarge the enclosure automatically.

The failure record must identify the binding constraints that prevented feasibility.

## 9. Capacity alternatives

After `HOLD_LAYOUT_CAPACITY`, the system launches the **Capacity Alternative Analyzer**.

It evaluates at least:

### 9.1 Larger single enclosure

Calculate:

- minimum mathematically feasible envelope;
- next suitable commercial enclosure candidates from the validated catalog;
- occupancy;
- reserve;
- rail/wireway arrangement;
- cable-entry impact;
- door/HMI impact;
- thermal impact;
- installation impact;
- LI/BOM/revision impact.

The proposed enclosure remains a candidate only.

### 9.2 Multi-panel division

The analyzer is authorized to study all technically valid partitions supported by the data, including:

- power vs automation/control;
- VFD/motor-drive section vs control section;
- floor/area-based division;
- main controller vs remote I/O;
- thermal segregation;
- EMC segregation;
- cable-concentration-based division;
- maintenance/availability-based division;
- other technically valid partitions discovered by the dependency graph and engineering constraints.

The analyzer may generate multiple candidate architectures but may not approve one automatically.

### 9.3 Graph-based partitioning

NetworkX represents:

- electrical dependencies;
- controller/I/O dependencies;
- communication links;
- shared power supplies;
- field-device relationships;
- interlocks;
- signal concentration by area/floor.

Candidate partitions must preserve required connectivity and explicitly account for inter-panel communication, power, control wiring, and field-cable impacts.

### 9.4 Candidate metrics

Every capacity alternative must report at least:

- panel count;
- enclosure size per panel;
- occupancy per panel;
- reserve per panel;
- rail count;
- wireway count/length;
- terminal count;
- gland count;
- estimated inter-panel links;
- communication requirements;
- remote-I/O requirements;
- power-supply/UPS/battery impact;
- verified heat-loss estimate when data exists;
- routing complexity;
- service-access metric;
- impacted LI/BOM items;
- engineering HOLDs.

The system may calculate a Pareto set of non-dominated alternatives. It must not produce an automatic final choice.

Final status:

`USER_DECISION_REQUIRED`

## 10. Human decision gate

The user selects or requests modification of an alternative.

Only after explicit selection may the system create the controlled downstream engineering change:

- new enclosure revision; or
- new panel architecture;
- revised Data Center/Data Sheet;
- new LI revision;
- recalculated load balance;
- new BOM;
- new layout;
- new deterministic drawing;
- new QA.

Historical revisions remain unchanged.

## 11. Deterministic rendering

The validated solver result becomes a normalized layout model.

The renderer consumes that model and generates SVG using one physical scale.

The renderer must:

- use actual enclosure dimensions;
- use actual component bounding boxes;
- preserve door/internal/side-view geometry;
- render DIN rails and wireways from solver output;
- render terminals and glands from solved positions;
- preserve one panel per engineering image;
- retain the approved visual composition and engineering sheet identity;
- generate stable identifiers for visual regression.

CairoSVG may produce PNG/PDF renderings for QA.

OpenCV/Pillow may compare:

- enclosure geometry;
- component count;
- bounding boxes;
- overlaps;
- spacing;
- template alignment;
- text/label regions;
- visual differences between revisions.

The SVG/layout JSON is canonical; PNG/PDF are derived artifacts.

## 12. Persistent memory independent of chat

### 12.1 Canonical storage model

The approved memory architecture is:

- **GitHub** — canonical, auditable source;
- **JSONL append-only** — immutable event history;
- **YAML** — current-state snapshots;
- **SQLite** — rebuildable query/index database;
- **ML** — proposal-only writer; never writes canonical state directly.

### 12.2 Repository structure

```text
memory/
  index.yaml
  events/
    YYYY/
      AUT_PANEL_EVENTS_YYYY_MM.jsonl
  panels/
    <PANEL_ID>/
      state.yaml
      decisions.jsonl
      qa_history.jsonl
      learning_events.jsonl
  global/
    engineering_lessons.jsonl
    repeated_failures.jsonl
    approved_patterns.yaml
  snapshots/
```

### 12.3 Event integrity

Every canonical event contains:

- event ID;
- timestamp;
- agent ID;
- panel ID when applicable;
- panel revision;
- event type;
- summary;
- evidence;
- input/output artifact hashes;
- previous-event SHA-256;
- current-event SHA-256;
- human approval reference when required.

The previous-event hash forms a tamper-evident chain.

Released revision history is append-only.

### 12.4 Cross-conversation bootstrap

A new conversation must restore context from repository state rather than depend on chat memory.

Bootstrap order:

1. Golden Rules;
2. canonical pipeline;
3. Data Center registry;
4. Data Sheet registry;
5. memory index;
6. global engineering lessons;
7. selected panel snapshot;
8. recent panel decisions;
9. open HOLDs;
10. current LI/BOM;
11. latest QA;
12. active ML model metadata;
13. current task context.

Chat content may add new working context but cannot silently override repository state.

## 13. SQLite rebuild

SQLite is treated as an operational index, not the immutable truth source.

A rebuild command must be able to reconstruct the operational database from:

- Data Center files;
- Data Sheets;
- LI/BOM artifacts;
- memory JSONL;
- QA records;
- model registry;
- plugin registry;
- artifact manifests.

A database corruption or deletion must therefore be recoverable from versioned repository data.

## 14. Machine learning

### 14.1 Role

ML predicts risk and identifies improvement opportunities.

It does not:

- create component dimensions;
- approve component compatibility;
- select an enclosure as final;
- select a panel partition as final;
- clear an engineering HOLD;
- change a Golden Rule;
- rewrite a released revision;
- auto-merge code.

### 14.2 Training data

Only human-reviewed outcomes may become canonical training examples.

Each example stores:

- panel/revision;
- input features;
- deterministic QA result;
- candidate layout metrics;
- reviewer outcome;
- correction type;
- cause classification;
- provenance;
- dataset fingerprint.

### 14.3 Cold start

The deterministic system remains primary.

The ML layer remains `LEARNING_COLD_START` until the configured minimum number of human-reviewed examples is available.

### 14.4 Improvement targets

ML may help identify:

- high-risk layouts;
- recurring capacity failures;
- likely routing problems;
- repeated catalog/lifecycle issues;
- frequently corrected solver objectives;
- QA checks with high defect yield;
- candidate default solver-weight improvements;
- repeated process bottlenecks;
- useful new deterministic rules.

When a statistical pattern becomes a stable engineering rule, it must be promoted through evidence, human review, tests, and the controlled change process.

## 15. Controlled evolution

The autoevolution engine remains proposal-only.

Every proposal contains:

- problem;
- evidence;
- recurrence frequency;
- candidate change;
- affected files;
- affected rules;
- expected benefit;
- risk;
- test plan;
- historical replay set;
- rollback plan;
- confidence;
- required approval.

The proposal is sandbox-tested against historical projects before human review.

Changes to locked contracts always require explicit approval.

## 16. Plugin/tool improvement system

The repository maintains a controlled plugin registry.

States:

- `DISCOVERED`;
- `EVALUATING`;
- `APPROVED_OPTIONAL`;
- `APPROVED_CORE`;
- `REJECTED`;
- `RETIRED`.

Promotion to an active state requires:

- repository identity;
- pinned release/commit;
- license status;
- security review;
- compatibility test;
- reproducibility test;
- fallback behavior;
- owner/purpose;
- review date.

The system may continuously discover candidate repositories but only proposes promotion.

## 17. Status model

The optimizer introduces:

- `HOLD_LAYOUT_INPUT`;
- `HOLD_LAYOUT_CAPACITY`;
- `HOLD_LAYOUT_THERMAL`;
- `HOLD_LAYOUT_EMC`;
- `HOLD_LAYOUT_CABLE_ENTRY`;
- `USER_DECISION_REQUIRED`;
- `LAYOUT_FEASIBLE`;
- `LAYOUT_VALIDATED`.

Existing project-wide `HOLD` and `REPROVADO` semantics remain authoritative.

## 18. Error handling

The subsystem is fail-closed.

Examples:

- missing exact dimensions -> HOLD;
- impossible hard constraints -> HOLD_LAYOUT_CAPACITY;
- solver timeout -> HOLD with best-known diagnostic, never PASS;
- invalid source provenance -> HOLD;
- LI/BOM mismatch -> REPROVADO;
- component overlap in claimed final layout -> REPROVADO;
- unauthorized enclosure change -> REPROVADO;
- unauthorized panel split -> REPROVADO;
- ML trying to override deterministic status -> REPROVADO;
- broken memory hash chain -> REPROVADO until repaired from trusted history.

## 19. Testing strategy

### Unit tests

- geometry;
- rotations;
- non-overlap;
- clearances;
- rail capacity;
- wireway placement;
- terminal/gland placement;
- dependency graph;
- memory hashing;
- database rebuild;
- ML advisory guardrails.

### Solver fixtures

Create deterministic fixtures for:

1. easy single-panel fit;
2. tight but feasible fit;
3. impossible locked enclosure;
4. feasible larger enclosure;
5. power/control split;
6. main/remote-I/O split;
7. cable-entry bottleneck;
8. thermal segregation case;
9. conflicting hard constraints;
10. missing dimension HOLD.

### Regression tests

Historical approved panels become replay fixtures.

The optimizer must reproduce or improve valid metrics without changing frozen engineering facts.

### Visual regression

Compare canonical SVG and derived render against approved geometry/template contracts.

## 20. Delivery boundaries for V1

V1 will include:

- normalized layout schema;
- OR-Tools single-panel solver;
- DIN rail and wireway placement;
- terminal/gland placement;
- hard/soft constraint framework;
- capacity diagnostics;
- larger-enclosure candidate generation;
- graph-based split candidate generation;
- alternative metrics;
- human decision gate;
- deterministic SVG data contract;
- persistent memory event store;
- YAML snapshot generation;
- SQLite rebuild/index;
- River cold-start/advisory integration points;
- plugin-registry promotion workflow;
- CI fixtures and regression tests.

V1 will not automatically:

- select a larger enclosure;
- approve a split;
- alter LI/BOM;
- modify Golden Rules;
- merge code;
- select manufacturer replacements;
- clear lifecycle/compatibility HOLDs;
- train from unreviewed generated outputs.

## 21. Acceptance criteria

The design is successful when:

1. the same frozen input produces the same validated layout or equivalent deterministic optimum under pinned solver settings;
2. no component appears outside the BOM;
3. no component is distorted;
4. no hard clearance is violated;
5. capacity failure produces diagnostics and alternatives rather than forced placement;
6. panel division alternatives preserve engineering connectivity and expose all new inter-panel requirements;
7. no candidate is automatically chosen;
8. memory can restore a panel's technical history in a new conversation without prior chat context;
9. SQLite can be rebuilt from repository state;
10. ML cannot bypass deterministic QA;
11. every model/tool/change remains versioned and auditable;
12. CI can replay representative historical fixtures.

## 22. Implementation sequencing

Implementation must be planned in independently testable increments:

1. layout data model and validation contracts;
2. OR-Tools single-panel solver;
3. rails/wireways/terminals/glands;
4. capacity diagnostics;
5. larger-enclosure alternatives;
6. graph-based split analyzer;
7. deterministic render contract;
8. persistent memory event chain;
9. SQLite rebuild/bootstrap;
10. ML feature capture and advisory loop;
11. open-source promotion workflow;
12. historical replay and visual regression.

No implementation increment may weaken the canonical Golden Rules or existing revision controls.
