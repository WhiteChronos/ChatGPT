# AGENTS.md — Engineering Compatibility / Codex

This repository contains engineering-governance rules for Automation, HVAC, Electrical and related disciplines.

## Mandatory rule
Before creating, editing, reviewing or approving compatibility-analysis code, schemas, reports, pipelines or documentation, read:

1. `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
2. `governance/ENGINEERING_COMPATIBILITY_HARDENING_v1_1.md`
3. `schemas/engineering_compatibility.schema.json`
4. `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
5. `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`

## Codex operating contract
Codex SHALL:

- preserve all source evidence and provenance;
- require SHA-256 provenance for every baseline document and every evidence record;
- compare valid hexadecimal SHA-256 digests case-insensitively;
- never convert `/visualize` into a short summary;
- keep compatibility and coverage as separate metrics;
- treat `assessment_records` as the authoritative complete criterion inventory;
- derive `scope_summary` from `assessment_records` so unsupported counts cannot inflate coverage;
- derive coverage from structured assessment classifications so `NOT_VERIFIABLE` reduces coverage;
- recompute global, interface, discipline and document compatibility from `assessment_records` and mandatory status weights;
- classify every assessment as VERIFIED, PARTIAL, DIVERGENT, NOT_VERIFIABLE or NOT_APPLICABLE;
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
pytest -q tests/test_engineering_compatibility_gate.py
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
