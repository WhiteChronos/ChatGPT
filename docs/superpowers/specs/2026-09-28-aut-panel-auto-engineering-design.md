# AUT Panel — Auto-Engineering Revision System

**Status:** Design approved in chat; implementation not started  
**Date:** 2026-09-28  
**Repository:** WhiteChronos/ChatGPT  
**Target branch:** feat/aut-panel-control-v1  
**Scope:** PN-AUT-01, PN-AUT-02 and future AUT panels using the same governed pipeline

## 1. Objective

Allow the AUT Panel system to modify engineering automatically when deterministic checks show that the current candidate design is not feasible, while preserving historical baselines, source traceability, deterministic QA and human control of fabrication and operational release.

The system SHALL create a new candidate engineering revision instead of modifying an approved or historical revision in place.

## 2. Non-negotiable authority hierarchy

The system SHALL preserve the following authority order:

1. approved repository contracts and Golden Rules;
2. approved LI revision and engineering baselines;
3. validated manufacturer documentation and official CAD/dimensional evidence;
4. applicable official standards and normative registry;
5. deterministic calculations and gates;
6. candidate optimization/evolution proposals;
7. Mem0 or other agent-memory retrieval as contextual assistance only;
8. ML/LLM suggestions as advisory only.

Memory, ML, image generation, Blender, Revit, or optimization engines SHALL NOT override higher-authority engineering evidence.

## 3. Automatic engineering changes that are authorized

When a deterministic gate detects a technically justified incompatibility, the system MAY automatically create a new candidate revision containing one or more of the following changes:

- internal component placement;
- DIN rail and wiring-duct placement;
- cable-entry and cable-routing arrangement;
- enclosure selection or enlargement;
- component substitution with technically equivalent current products;
- LI/BOM quantities in the new candidate revision;
- 24 Vdc and AC load calculations;
- power-supply and DC-UPS sizing;
- battery sizing;
- I/O allocation and module selection;
- communication architecture;
- gateway/interface selection;
- panel split proposal when required by capacity or architecture;
- derived drawings, dimensional views, BOM, load schedule, I/O matrix and render artifacts;
- PLC software changes in a candidate software revision, with compile/test evidence when the engineering environment is available.

Every automatic change SHALL be traceable to:
- trigger condition;
- source evidence;
- calculation or deterministic rule;
- previous value;
- proposed value;
- affected downstream artifacts;
- tests executed;
- result status.

## 4. Historical preservation

The following SHALL NOT be overwritten:

- PN-AUT-01 / PN-AUT-02 historical LI revisions;
- frozen R02 historical records;
- previous BOM/layout/render artifacts associated with released or frozen revisions;
- approval records;
- raw source documents;
- source hashes;
- prior QA evidence.

If the system changes a quantity, exact model, enclosure, topology, or engineering decision, it SHALL create a new revision identifier and append a memory/history event.

## 5. Human-controlled release boundary

The system MAY autonomously generate, optimize and test candidate engineering revisions.

The system SHALL NOT autonomously:

- release a panel for fabrication;
- issue a purchase order or binding procurement decision;
- mark engineering as approved for issue;
- merge PR #23 automatically;
- download or transfer PLC logic to production hardware;
- energize or command physical equipment;
- bypass an engineering HOLD or REPROVADO result;
- change Golden Rules or release thresholds to make a candidate pass.

Final fabrication/release approval remains human-controlled.

## 6. Candidate revision lifecycle

The canonical lifecycle SHALL be:

```text
DETECTED_INCOMPATIBILITY
        ↓
CREATE_CANDIDATE_REVISION
        ↓
SOURCE_AND_NORMATIVE_REVALIDATION
        ↓
ENGINEERING_RECALCULATION
        ↓
LI/BOM/LOAD/I-O/COMMUNICATION UPDATE
        ↓
LAYOUT OPTIMIZATION
        ↓
3D/CAD GEOMETRY VALIDATION
        ↓
DRAWINGS / RENDER / DOCUMENTS
        ↓
DETERMINISTIC QA + REGRESSION
        ↓
MEMORY_SYNC
        ↓
CANDIDATE_READY_FOR_HUMAN_REVIEW
        ↓
HUMAN APPROVAL
        ↓
RELEASE
```

A candidate failing any deterministic gate SHALL remain HOLD or REPROVADO and SHALL NOT be promoted.

## 7. Enclosure auto-selection

Automatic enclosure change is authorized only in a new candidate revision.

The selection process SHALL:

1. prove current enclosure capacity failure;
2. preserve component dimensions and required clearances;
3. query validated manufacturer catalog data;
4. compare feasible enclosure candidates;
5. choose the smallest technically compliant candidate under configured constraints;
6. recalculate thermal, electrical, cable and mechanical impacts;
7. invalidate and regenerate downstream artifacts;
8. record the change as a candidate-revision delta.

If no validated enclosure satisfies the constraints, return HOLD_LAYOUT_CAPACITY.

## 8. Automatic component substitution

A component may be substituted automatically only when:

- the current component is obsolete, unavailable, incompatible, or cannot satisfy the candidate design;
- manufacturer documentation is validated;
- voltage/current/protocol/function and environmental compatibility are checked;
- lifecycle status is acceptable;
- dimensions and mounting are available;
- downstream electrical, I/O, communication and layout effects are recalculated.

A substitution with unresolved equivalence SHALL remain HOLD_COMPONENT_EQUIVALENCE.

## 9. LI/BOM automatic revision policy

The historical LI is immutable.

The system MAY create a new LI candidate revision containing changed quantities or models when supported by evidence.

Required outputs:
- previous revision;
- candidate revision;
- line-by-line delta;
- reason for each delta;
- source reference;
- downstream invalidation list;
- QA result.

The candidate SHALL never silently replace R02.

## 10. Automatic PLC/programming changes

Candidate PLC logic changes are permitted when the automation architecture changes.

Required controls:
- source-controlled candidate branch/revision;
- compile or syntax validation when toolchain is available;
- deterministic I/O parity against candidate matrix;
- simulation/unit test where feasible;
- explicit list of changed blocks/tags/functions;
- no automatic download to a production PLC;
- human approval before operational deployment.

## 11. Memory integration

Mem0 may be used as an auxiliary retrieval layer for:
- prior engineering decisions;
- confirmed historical mistakes;
- regression-test references;
- prior source-validation outcomes;
- panel-specific contextual facts.

Mem0 SHALL NOT be the authoritative source of engineering truth.

Before acting on a retrieved memory, the system SHALL reconcile it against current canonical repository files and source evidence.

Old or superseded memories SHALL be classified as historical context and SHALL NOT override the current baseline.

## 12. Memory benchmarking

Agent Memory Benchmark or an equivalent evaluation harness may be used to test:
- correct panel/revision isolation;
- retrieval of current versus superseded decisions;
- prevention of cross-panel contamination;
- exclusion of invalid or unsupported historical claims;
- retrieval precision for regression-relevant facts.

Memory benchmark scores SHALL NOT be treated as engineering-release evidence.

## 13. Geometric and rendering invariants

Automatic engineering changes SHALL preserve the existing geometric rules:

- one physical 3D assembly governs all dimensional views;
- all engineering geometry uses millimetres;
- manufacturer CAD/dimensional evidence is the geometry authority;
- dimensional views use a common scale;
- no object may be squeezed, stretched, or independently rescaled;
- canvas grows instead of shrinking engineering content;
- the door is a single physical object;
- the HMI is a single physical instance mounted on the door;
- fixed enclosure features and approved cable-entry geometry remain consistent between views;
- final SVG/PNG delivered to the user must be the same artifact that passed QA.

## 14. Agent separation of duties

At minimum, the candidate workflow SHALL separate:

- ORCHESTRATOR;
- TECHNICAL_RESEARCH;
- SOURCE_VALIDATOR_A;
- SOURCE_VALIDATOR_B;
- NORMATIVE;
- ELECTRICAL_SIZING;
- AUTOMATION_IO;
- COMMUNICATION_ARCHITECTURE;
- LI_BOM;
- LAYOUT_OPTIMIZER;
- CAD_GEOMETRY_GUARDIAN;
- SCALE_PROPORTION_GUARDIAN;
- CABLE_ENTRY_GUARDIAN;
- BLENDER_RENDER_GUARDIAN;
- REVIT_BIM_INTEROP_GUARDIAN when applicable;
- CANVAS_COMPOSITION_GUARDIAN;
- MEMORY_CURATOR;
- QA;
- RELEASE_REVIEW.

The proposing agent SHALL NOT weaken the gate that evaluates its own proposal.

## 15. Failure behavior

The system is fail-closed.

Examples:
- missing official dimensions → HOLD_DIMENSIONAL_DATA;
- candidate does not physically fit → HOLD_LAYOUT_CAPACITY;
- unverified substitute → HOLD_COMPONENT_EQUIVALENCE;
- unresolved normative conflict → HOLD_NORMATIVE_CONFLICT;
- quantity mismatch → REPROVADO;
- duplicate physical device → REPROVADO;
- distorted render → REPROVADO;
- unsupported automatic baseline overwrite → REPROVADO;
- attempt to bypass human release → REPROVADO.

## 16. Audit trail

Every automatic candidate revision SHALL record:

- task/run ID;
- panel ID;
- source revision;
- candidate revision;
- triggering finding;
- canonical input hashes;
- source references;
- calculations;
- changes applied;
- tests and gates executed;
- HOLD/REPROVADO/PASS status;
- artifact hashes;
- memory events;
- rollback target.

## 17. GitHub/Codex behavior

Codex may:
- detect incompatibilities;
- generate candidate revisions;
- modify candidate engineering files;
- run tests;
- regenerate downstream artifacts;
- open/update PRs;
- report candidate changes.

Codex SHALL NOT:
- auto-merge the release PR;
- rewrite historical revisions;
- alter deterministic gate thresholds without separate explicit authorization;
- claim engineering approval from CI status alone.

GitHub Actions SHALL independently validate the generated candidate artifacts.

## 18. Acceptance criteria

The feature is acceptable only when tests demonstrate all of the following:

1. historical R02 remains byte-preserved;
2. a capacity failure creates a new candidate revision;
3. a candidate enclosure change invalidates all required downstream stages;
4. LI/BOM/load/layout/render stay mutually consistent in the candidate;
5. source evidence is attached to automatic substitutions;
6. a failed deterministic gate prevents candidate promotion;
7. a passing CI run does not mark fabrication/release approved;
8. memory retrieval cannot override repository authority;
9. old/superseded memory is not applied as current engineering;
10. rollback restores the previous candidate state without changing historical revisions;
11. final delivered render is verified against the same candidate geometry and BOM that passed QA;
12. no automatic workflow can merge PR #23 or deploy to production PLC hardware.

## 19. Out of scope for initial implementation

The initial implementation SHALL NOT include:
- autonomous procurement;
- automatic issuance to fabrication;
- automatic PLC download;
- automatic plant operation;
- unattended modification of Golden Rules;
- unattended release-threshold changes;
- automatic approval of safety-critical deviations.

Those capabilities require separate design and explicit authorization.

## 20. Rollback model

Every automatic engineering change SHALL be reversible by:
- candidate revision deletion/abandonment;
- git revert or equivalent VCS rollback;
- restoration of the preceding candidate pointer;
- preserving immutable historical revisions and evidence.

Rollback SHALL NOT require reconstructing the historical engineering state from memory.
