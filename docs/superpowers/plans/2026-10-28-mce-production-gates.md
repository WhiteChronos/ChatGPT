# MCE Production Evidence Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an independent read-only fail-closed technical release gate for MCE.

**Architecture:** Reuse the canonical MCE workbook workflow for source hashes, contract rules and OOXML audit. Keep operator/engineering acceptance outside automation; no REA dependencies.

**Tech Stack:** Python >=3.12, openpyxl, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-28-mce-production-gates-design.md`

## Global Constraints

- Preserve master XLSX SHA and allow edits only in approved derived copies.
- Maximum 50 cause items per worksheet; no invented project, SS or safety logic.
- External human approval/FAT/SAT cannot be replaced by a local JSON flag.

## Review Focus

1. Corrupt `state.json` must not produce a traceback or green status.
2. Corrupt `analysis.json` must fail closed.
3. Forged approval and missing output cannot bypass OOXML audit.
4. Mutated master digest must block, without touching the original.
5. Missing/empty workspace must remain BLOCKED, never imply release.

### Task 1: Add fail-closed workspace readiness (implemented locally, pending PR CI)

**Files:** Create `systems/mce/scripts/production_readiness.py`, `systems/mce/tests/test_production_readiness.py`.

- [x] Write tests covering no workspace, changed master, premature phase, forged approval, invalid JSON and no automatic acceptance.
- [x] Run tests red and confirm failures before implementing missing gate and malformed-analysis fix.
- [x] Implement read-only `assess(workspace: Path) -> dict`, report statuses, and exit code 2 for blockers.
- [x] Rerun focused tests locally; verify technical-status and non-mutating behavior.
- [ ] Verify new tests on exact PR HEAD via GitHub Actions.

### Task 2: Finalize approved release and real engineering acceptance (gated)

**Files:** `systems/mce/docs/PRODUCTION_ACCEPTANCE.md` and external authorized project records.

- [ ] Verify protected-branch PR review, main SHA and required check; stop without fresh SHA-specific merge authority.
- [ ] Install reproducible CLI release on authorized engineering host and verify operator checksum.
- [ ] Supply real approved project/SS/master/docs and run technical gate + separate engineering review.
- [ ] Obtain formal multidisciplinary review and FAT/SAT where applicable, plus rollback proof.
- [ ] Record operational owner acceptance before `PRODUCTION_COMPLETE`.
