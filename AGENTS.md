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
- never convert `/visualize` into a short summary;
- keep compatibility and coverage as separate metrics;
- derive coverage from the structured scope summary so `NOT_VERIFIABLE` reduces coverage;
- classify every finding as VERIFIED, PARTIAL, DIVERGENT, NOT_VERIFIABLE or NOT_APPLICABLE;
- identify document, revision, sheet/page, TAG/location and evidence for every engineering claim;
- require every baseline discipline and every baseline document to have an explicit compatibility score;
- require a structured calculation method with denominator definition and status weights;
- perform `/factcheck`, `/thenvsnow`, `/comparison`, `/deepdive`, `/rootcause`, `/audit`, `/redteam`, `/premortem`, `/viability` and `/actionplan` when relevant;
- treat CRITICAL findings with status `OPEN` or `IN_REVIEW` as release blockers regardless of classification;
- accept `WAIVED` findings only with recorded approver, reason, approval evidence and approval date/time;
- block unreconciled baselines, missing mandatory documents and failed discipline interfaces;
- distinguish source-derived fact from inference and external knowledge;
- evaluate simpler, safer, lower-cost and more maintainable alternatives when system architecture is involved;
- require explicit lifecycle impact text for design, procurement, fabrication, programming, commissioning, operation, maintenance, safety, cost and schedule; use `NONE` when there is no impact;
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

The no-argument gate invocation intentionally validates the permanent known-good fixture at `datasheet/projects/example-project.json`. Real projects MUST also be validated explicitly:

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
- `blocking_missing_documents` exactly matches the mandatory document inventory and is empty;
- coverage is reproducible from `scope_summary` and meets the configured threshold;
- global and interface compatibility meet configured thresholds;
- discipline-level and document-level compatibility maps cover the complete baseline;
- no open CRITICAL finding remains;
- any waiver has explicit human approval metadata;
- evidence provenance hashes match the corresponding baseline document hashes;
- architecture-impact findings include alternatives and viability analysis;
- schema and semantic validation return no errors.

## Pull request compatibility
A pull request that changes compatibility-analysis logic, engineering schemas, Data Center manifests, datasheets, report-generation code or either compatibility validator MUST pass the engineering compatibility workflow and Golden Rule gate before merge.
