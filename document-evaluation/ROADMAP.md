# Roadmap

## Phase 0 — Repository partition
- isolate contracts under `document-evaluation/`;
- delegate to mature root gates;
- define product architecture and agent boundary.

## Phase 1 — Standalone repository
- create dedicated repository;
- copy governed contracts with provenance;
- establish CI, package layout and release policy;
- pin dependency versions.

## Phase 2 — Ingestion engine
- PDF/DOCX/XLSX ingestion adapters;
- immutable object storage abstraction;
- document identity/revision detection;
- SHA-256 manifest generation;
- normalized evidence extraction.

## Phase 3 — Evaluation engine
- criterion inventory;
- Protocol Zero question graph;
- evidence graph;
- cross-document comparison;
- Automation/Data hyperfocus;
- scoring and release-gate engine.

## Phase 4 — Agent runtime
- tool-constrained document-evaluation agent;
- source lookup;
- question generation;
- finding promotion rules;
- action-plan generation;
- human approval workflow.

## Phase 5 — Reporting/UI
- complete visual engineering report;
- evidence drill-down;
- question/answer workflow;
- TAG/interface traceability;
- gate dashboard.

## Phase 6 — Hardening
- security model;
- audit log;
- tenancy/project isolation;
- deterministic regression fixtures;
- packaging and versioned releases.
