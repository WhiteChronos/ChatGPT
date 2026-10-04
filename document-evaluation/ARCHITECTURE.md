# Architecture

## Evaluation flow

```text
SOURCE PACKAGE
  -> immutable ingestion
  -> document identity + SHA-256
  -> normalization
  -> project baseline reconciliation
  -> Protocol Zero questions
  -> evidence-backed assessments
  -> source-governed external references
  -> Automation/Data hyperfocus
  -> red-team / viability
  -> findings
  -> compatibility + coverage
  -> release gate
  -> complete visual report
```

## Trust boundaries

1. **Project evidence**: authoritative for project facts.
2. **Official engineering references**: authoritative for external requirements within scope.
3. **Open-source tooling**: implementation, simulation and validation support only.
4. **Agent inference**: never silently promoted to source fact.

## Agent boundary
The agent may analyze, compare, question and propose corrections. It may not self-waive, alter immutable raw evidence, fabricate references, or merge changes automatically.

## Extraction target
This directory is intentionally self-contained enough to become a dedicated repository without changing the conceptual contracts.
