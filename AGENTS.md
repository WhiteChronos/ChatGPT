# AGENTS.md — Engineering Compatibility / Codex

This repository contains engineering-governance rules for Automation, HVAC, Electrical and related disciplines.

## Mandatory rule
Before creating, editing, reviewing or approving compatibility-analysis code, schemas, reports, pipelines or documentation, read:

1. `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
2. `schemas/engineering_compatibility.schema.json`
3. `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
4. `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`

## Codex operating contract
Codex SHALL:

- preserve all source evidence and provenance;
- never convert `/visualize` into a short summary;
- keep compatibility and coverage as separate metrics;
- classify every finding as VERIFIED, PARTIAL, DIVERGENT, NOT_VERIFIABLE or NOT_APPLICABLE;
- identify document, revision, sheet/page, TAG/location and evidence for every engineering claim;
- perform `/factcheck`, `/thenvsnow`, `/comparison`, `/deepdive`, `/rootcause`, `/audit`, `/redteam`, `/premortem`, `/viability` and `/actionplan` when relevant;
- treat CRITICAL open findings as release blockers;
- distinguish source-derived fact from inference and external knowledge;
- evaluate simpler, safer, lower-cost and more maintainable alternatives when system architecture is involved;
- never overwrite raw Data Center sources;
- validate generated datasheets against `schemas/engineering_compatibility.schema.json`;
- run `python pipeline/engineering_compatibility_gate.py` before proposing merge.

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
- feasibility alternatives;
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

## Pull request compatibility
A pull request that changes compatibility-analysis logic, engineering schemas, Data Center manifests, datasheets or report-generation code MUST pass the engineering compatibility workflow and Golden Rule gate before merge.
