# AGENTS.md — Engineering Compatibility / Codex

This repository contains engineering-governance rules for Automation, HVAC, Electrical and related disciplines.

## Mandatory rule
Before creating, editing, reviewing or approving compatibility-analysis code, schemas, reports, pipelines or documentation, read:

1. `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
2. `governance/AUTOMATION_HYPERFOCUS_GOLDEN_RULE_v1_0.md`
3. `governance/ENGINEERING_COMPATIBILITY_HARDENING_v1_1.md`
4. `schemas/engineering_compatibility.schema.json`
5. `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
6. `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`
7. `memory/ENGINEERING_COMPATIBILITY_MEMORY.md`

## Codex operating contract
Codex SHALL:

- apply Protocol Zero: explicit technical question before promoting a suspected discrepancy to a finding;
- keep unanswered questions as NOT_VERIFIABLE/pending and never promote them to confirmed findings;
- apply Automation/Data hyperfocus through TAG -> I/O -> PLC/RTU -> logic -> network/protocol -> data quality -> HMI/SCADA -> FAT/SAT;
- preserve the master-discipline authority for physical attributes and never silently override it from a derived discipline;

- preserve all source evidence and provenance;
- require SHA-256 provenance for every baseline document and every evidence record;
- compare valid hexadecimal SHA-256 digests case-insensitively;
- never convert `/visualize` into a short summary;
- keep compatibility and coverage as separate metrics;
- treat `assessment_records` as the authoritative complete criterion inventory;
- require every assessment record, including VERIFIED records, to carry provenance-bearing evidence and structured evidence quality before contributing to coverage or compatibility;
- require evidence documents declared by an assessment to belong to that assessment's `document_ids` and baseline inventory;
- derive `scope_summary` from `assessment_records` so unsupported counts cannot inflate coverage;
- derive coverage from structured assessment classifications so `NOT_VERIFIABLE` reduces coverage;
- recompute global, interface, discipline and document compatibility from `assessment_records` and mandatory status weights;
- classify every assessment as VERIFIED, PARTIAL, DIVERGENT, NOT_VERIFIABLE or NOT_APPLICABLE;
- require every PARTIAL, DIVERGENT or NOT_VERIFIABLE assessment record to be represented by a corresponding complete finding;
- treat `interface=true` only as a multidisciplinary interface assessment: it must identify at least two distinct baseline disciplines and provenance evidence must cover at least two distinct interface disciplines;
- identify document, revision, sheet/page, TAG/location and evidence for every engineering claim;
- require every baseline discipline and every baseline document to have an explicit compatibility score;
- require a structured calculation method with denominator definition and status weights;
- perform `/factcheck`, `/thenvsnow`, `/comparison`, `/deepdive`, `/rootcause`, `/audit`, `/redteam`, `/premortem`, `/viability` and `/actionplan` when relevant;
- treat CRITICAL findings with status `OPEN` or `IN_REVIEW` as release blockers regardless of classification;
- accept `WAIVED` findings only when `waiver.approval_record_id` resolves to an independently trusted human approval record in configuration;
- never accept self-declared waiver metadata as authorization;
- block unreconciled baselines, missing mandatory documents, non-current mandatory documents and failed discipline interfaces;
- validate finding and assessment disciplines against `baseline.disciplines`;
- require structured evidence quality and confidence for every finding;
- distinguish source-derived fact from inference and external knowledge;
- evaluate simpler, safer, lower-cost and more maintainable alternatives when system architecture is involved;
- require explicit nonblank lifecycle impact text for design, procurement, fabrication, programming, commissioning, operation, maintenance, safety, cost and schedule; use `NONE` when there is no impact;
- require nonblank comparison, root cause, solution and closure criterion;
- never overwrite raw Data Center sources;
- reject NaN/Infinity and other non-standard numeric values;
- validate generated datasheets against `schemas/engineering_compatibility.schema.json`;
- use `pipeline/engineering_compatibility_gate.py` as the canonical release validator;
- ensure any secondary compatibility CLI delegates to the canonical gate rather than duplicating thresholds or blocker logic.

## Required validation commands
Before proposing merge, Codex SHALL run or ensure CI runs:

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

The no-argument gate validates the permanent known-good fixture at `datasheet/projects/example-project.json`. Real projects MUST also be validated explicitly:

```bash
python pipeline/engineering_compatibility_gate.py datasheet/projects/<project>.json
```

## Visualization contract
Every final engineering report SHALL expose all relevant findings using a complete visual hierarchy. Required elements include:

- overall gate and compatibility;
- compatibility by discipline and interface;
- coverage;
- document-by-document assessment;
- complete finding cards;
- evidence quality and confidence;
- evidence vs comparison;
- root cause;
- impact by lifecycle stage;
- primary and secondary documents to adjust;
- proposed correction text where applicable;
- feasibility alternatives for architecture/system-design findings;
- closure criterion;
- missing documents and NOT_VERIFIABLE items;
- action plan and release gate.

Use severity semantics consistently:

- CRITICAL = red
- HIGH = orange
- MEDIUM = yellow
- LOW / NOT_VERIFIABLE = blue
- VERIFIED / COMPATIBLE = green
- NOT_APPLICABLE = gray

These color mappings are machine-enforced and must not be remapped.

## Release integrity contract
A datasheet may declare `PASS` only when all of the following are true:

- baseline documents are present and the baseline is reconciled;
- every mandatory document has an eligible current/approved status;
- `blocking_missing_documents` exactly matches the computed mandatory missing/non-current inventory and is empty;
- `scope_summary` exactly matches `assessment_records`;
- every assessment record has source evidence, matching revision/hash provenance and structured evidence quality;
- every issue-classified assessment (`PARTIAL`, `DIVERGENT`, `NOT_VERIFIABLE`) has a corresponding finding;
- every interface assessment represents at least two baseline disciplines and has evidence spanning at least two interface disciplines;
- coverage is reproducible from `assessment_records` and meets threshold;
- global, interface, discipline and document compatibility values match recomputed weighted scores;
- no open CRITICAL finding remains;
- any waiver references a trusted human approval record outside the datasheet;
- evidence provenance hashes match corresponding baseline document hashes regardless of hexadecimal case;
- findings reference valid assessment records and valid baseline disciplines;
- every finding includes evidence quality and nonblank required technical text;
- architecture-impact findings include alternatives and viability analysis;
- schema and semantic validation return no errors.

## Pull request compatibility
A pull request that changes compatibility-analysis logic, engineering schemas, Data Center manifests, datasheets, report-generation code or either compatibility validator MUST pass the Engineering Compatibility Visualize Gate and repository governance checks before merge.

# AUT Panel Control extension

## Scope
This branch implements AUT - Paineis de Automacao e Controle.

## Mandatory bootstrap
Before changing engineering logic, data contracts, panel layout, LI/BOM, normative data, QA, ML or evolution behavior, read:
1. prompts/PROMPT_MASTER_AUT_PANEL_GITHUB_CODEX_V1.md
2. context/AUT_PANEL_CONTEXT_MANIFEST_V1.yaml
3. datacenter/AUT_PANEL_NORMATIVE_REFERENCES.yaml
4. datacenter/AUT_PANEL_NORMATIVE_SUPPLEMENT_2026.yaml
5. datacenter/LI_MATERIAL_CONTROL.json
6. configs/layout_optimizer_v1.yaml

## Authority
Repository canonical files and approved technical evidence override chat memory.
Conflict or missing evidence => HOLD.

## Locked behavior
- Do not rewrite approved baselines in place.
- Do not mutate historical LI revisions.
- Do not alter frozen R02 quantities in place. Authorized engineering changes must create a new candidate revision with evidence and delta traceability.
- Enclosure size, component selection, quantities and panel split may be changed automatically only inside a governed candidate revision under `configs/auto_engineering_v1.yaml`.
- Historical LI revisions and released/frozen artifacts remain immutable.
- Do not let ML override deterministic gates.
- Do not auto-merge PR #23.

## Codex execution contract
Every substantive change must report:
- files changed;
- canonical inputs and SHAs;
- tests run and results;
- engineering HOLDs;
- regressions/risks;
- rollback path.

CI green is not engineering approval.

## Routing
Known intent -> deterministic router.
Ambiguous intent -> ML_ROUTE_HINT only.
Conflict -> deterministic rules win.

## Panel render integrity
Before any AUT panel render is treated as dimensional or fabrication-relevant, agents SHALL:
- prove official manufacturer dimensions and mounting clearances for every drawable component;
- use one common millimetre scale;
- reconcile physical instance counts against LI/BOM;
- keep the HMI as one door-mounted physical instance only;
- never duplicate a door-mounted component on the backplate;
- validate door/backplate interference, cable-exit space, gland access and bend radius;
- return HOLD_DIMENSIONAL_DATA or HOLD_LAYOUT_CAPACITY instead of visually shrinking components;
- record confirmed mistakes in project memory and add a regression test before closure.

## Raster proportion guard
For dimensional raster views, Codex SHALL use `pipeline/corrigir_proporcao_imagem.py` or equivalent validated gate before composition. A fixed frame may not force any resize of engineering geometry. Required invariants:
- `scale_x = scale_y = 1.0`;
- smaller target frame => grow canvas or REPROVADO;
- aspect ratio must match the engineering width/height;
- letterbox/pillarbox may add empty space only;
- no raster utility may be used to hide an upstream CAD/3D geometry error.

When this guard or its tests change, Codex SHALL run the AUT panel agent-system regression suite and report the result in PR #23.

## Automatic engineering candidate revisions
Codex MAY create and modify new engineering candidate revisions using `pipeline/aut_panel_candidate_revision.py`, `pipeline/aut_panel_candidate_runner.py` and `pipeline/aut_panel_candidate_gate.py`. Candidate automation may revise enclosure, components, quantities, load sizing, I/O, communication, layout and candidate PLC logic when supported by validated evidence.

Codex SHALL NOT overwrite historical R02/released revisions, weaken deterministic gates, auto-merge, issue fabrication release, create binding procurement, or download to production PLC hardware. A candidate that passes deterministic QA ends at `CANDIDATE_READY_FOR_HUMAN_REVIEW`. Human approval may create a release-authorization artifact but does not itself execute merge, fabrication or PLC deployment.

## Release
RELEASE is allowed only after required deterministic gates, source validation, normative reverification, QA and human approval.
