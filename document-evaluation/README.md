# Document Evaluation System

This partition is the product-facing nucleus for governed multidisciplinary document evaluation.

## Purpose
Turn the repository's engineering compatibility controls into an independent system and future agent for document review.

## Core guarantees
- project evidence remains authoritative for project-specific facts;
- official standards/specifications govern external engineering requirements;
- open-source repositories are supporting-only and never normative;
- Protocol Zero applies before promoting a discrepancy to a finding;
- source provenance is immutable and SHA-256 traceable;
- coverage and compatibility remain separate;
- release decisions are fail-closed.

## Internal structure
- `agent/` — agent contract and operating model.
- `config/` — system policy and canonical runtime configuration.
- `datacenter/` — ingestion, raw/normalized evidence and provenance contract.
- `datasheet/` — project evaluation data contract.
- `governance/` — policy inherited from the engineering compatibility system.
- `pipeline/` — orchestration entrypoints.
- `schemas/` — standalone schemas owned by this subsystem.
- `tests/` — regression and contract tests.
- `ROADMAP.md` — staged product plan.

## Relationship with repository root
During incubation this subsystem delegates release-critical validation to the repository-root canonical gates. Once extracted into its own repository, those contracts become first-class components of the standalone system.
