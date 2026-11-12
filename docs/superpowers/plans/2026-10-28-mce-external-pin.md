# MCE external release provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task by task.

**Goal:** Reject MCE release artifacts that differ from a trusted external digest or approved commit.

**Architecture:** Extend only the existing MCE ZIP verifier; no REA imports, Excel writes or runtime deployment.

**Tech Stack:** Python 3.12+, stdlib, pytest.

**Spec:** `docs/superpowers/specs/2026-10-28-mce-external-pin-design.md`

## Global Constraints
- Preserve status `INTEGRITY_PASS` for self-consistent legacy archives but report external trust separately.
- Never output `production_complete=true` or approve MCE workbook changes.

## Review Focus
- Trusted hash typo or mismatch -> BLOCKED.
- Missing claimed commit when expected -> BLOCKED.
- Missing external pins -> technical integrity only, no provenance claim.
- Existing release fixtures and CLI -> backward compatible.
- ZIP member traversal and tampering -> remain blocked.

### Task 1: Tests for external digest and commit pins

**Files:** `systems/mce/tests/test_release_integrity.py`

- [x] Add tests for matching/mismatched/invalid expected SHA-256.
- [x] Run tests before implementation and capture expected failures.
- [x] Add tests for absent and matching external source commit; confirm failures.

### Task 2: Extend verifier and CLI

**Files:** `systems/mce/scripts/release_integrity.py`

- [x] Extend `assess_archive(... expected_sha256, expected_git_sha)` and `--expected-*` arguments.
- [x] Fail closed on malformed or mismatched trusted values.
- [x] Re-run new negative tests after implementing the change.

### Task 3: Docs and release verification

**Files:** `systems/mce/docs/RELEASE_INTEGRITY.md`, `systems/mce/README.md`

- [x] Explain external independent channel, no self-signing or production declaration.
- [ ] Run full GitHub Actions MCE suite at new SHA and validate check statuses.
- [ ] Obtain engineering owner approval, merged release and production FAT/SAT evidence separately.
