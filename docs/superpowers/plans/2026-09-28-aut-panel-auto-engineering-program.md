# AUT Panel Automatic Engineering Program — Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement these plans task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement governed automatic engineering candidate revisions, auxiliary Mem0 memory, memory benchmarking, and GitHub/Codex automation without overwriting historical engineering or bypassing human release approval.

**Architecture:** The program is split into four independently testable subsystems. The core candidate-revision engine owns engineering mutation; Mem0 is auxiliary context only; the benchmark validates memory behavior independently; GitHub/Codex automation orchestrates and verifies but cannot auto-release.

**Tech Stack:** Python 3.12, SQLite, YAML/JSON, pytest, GitHub Actions, existing AUT Panel pipeline, Mem0 OSS integration behind a feature flag, Agent Memory Benchmark as a separate evaluation harness.

**Spec:** `docs/superpowers/specs/2026-09-28-aut-panel-auto-engineering-design.md`

## Global Constraints

- Historical PN-AUT revisions and frozen R02 records are immutable.
- Automatic changes are permitted only in a new candidate revision.
- Repository canonical files and approved technical evidence outrank memory, ML and agent suggestions.
- Mem0 is auxiliary memory and never an engineering truth source.
- Deterministic HOLD/REPROVADO cannot be overridden by ML, memory, renderers or agents.
- Fabrication release, binding procurement, PR auto-merge and production PLC download remain human-controlled.
- Final delivered SVG/PNG must be the same artifact that passed deterministic QA.
- All candidate changes require provenance, delta, tests and rollback.
- PR #23 remains draft and auto-merge forbidden until explicit human release action.

## Implementation Order

1. `2026-09-28-aut-panel-candidate-revision-core.md`
2. `2026-09-28-aut-panel-mem0-integration.md`
3. `2026-09-28-aut-panel-memory-benchmark.md`
4. `2026-09-28-aut-panel-github-codex-automation.md`

Each plan produces working software independently and ends with its own regression gate. Do not start a later plan until the previous plan's public interfaces and tests are green.

## Review Focus

- Candidate revision created from R02 must never mutate the R02 files or database rows.
- A stale Mem0 result must never override the current candidate or canonical repository state.
- A memory benchmark PASS must never be interpreted as engineering QA/release PASS.
- GitHub/Codex automation must not acquire write authority over Golden Rules, release approval or production PLC deployment.
- A candidate revision rollback must restore the preceding candidate pointer without reconstructing historical state from memory.
