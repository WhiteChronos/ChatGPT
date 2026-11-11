# REA standalone release attestation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task by task.

**Goal:** Verify a standalone REA ZIP and two independent operator-pinned provenance values.

**Architecture:** A new self-contained Python stdlib validator under the REA product; no code or imports from MCE.

**Tech Stack:** Python 3.12+, zipfile, hashlib, json, stat, pytest.

**Spec:** `docs/superpowers/specs/2026-10-28-rea-release-attestation-design.md`

## Global Constraints
- Do not extract, execute or alter the source archive.
- No forced approval, no remote MCP activation and no secrets in logs.

## Review Focus
- Tampered payload and manifest missing -> BLOCKED.
- ZIP-slip, backslash, symlink, duplicate entry -> BLOCKED.
- Wrong product identifier -> BLOCKED.
- Wrong external SHA-256 or Git commit -> BLOCKED.
- Valid self-consistent archive without external proof -> integrity only, never production acceptance.

### Task 1: Red tests

**Files:** `systems/rea/tests/test_release_integrity.py`

- [x] Write standalone tests for all five review-focus cases.
- [x] Verify RED because new verifier file did not yet exist.

### Task 2: Implement independent validator

**Files:** `systems/rea/scripts/release_integrity.py`

- [x] Implement SHA-256 streamed archive hash, manifest-safe member validation, bounds and external pins.
- [x] Preserve `production_complete=false` in all branches and return exit 2 for blocked archives.
- [x] Verify GREEN tests and run full REA suite (SDK optional in local environment).

### Task 3: Documentation and reproducible CI

**Files:** `systems/rea/docs/RELEASE_INTEGRITY.md`, `systems/rea/README.md`

- [x] Document audit, trusted pin requirements and limitations.
- [ ] Confirm CI at exact new SHA with official MCP SDK installed.
- [ ] After approved merge, verify real host, tunnel-client, ChatGPT Web discovery, rollback and operational acceptance.
