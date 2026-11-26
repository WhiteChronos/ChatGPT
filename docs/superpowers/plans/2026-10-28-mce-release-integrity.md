# MCE release archive attestation — implementation plan

> For agentic workers: REQUIRED SUB-SKILL `superpowers:executing-plans` or `superpowers:subagent-driven-development`. Preserve TDD and independent review gates.

**Goal:** Verify standalone MCE ZIPs without extraction, fail closed and report provenance only.

**Architecture:** Standalone `release_integrity.py` uses Python standard-library ZIP/hash readers. Tests create synthetic safe/corrupt ZIPs. No XLSX edits and no REA imports.

**Tech Stack:** Python 3.12+, `hashlib`, `zipfile`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-28-mce-release-integrity-design.md`.

## Global constraints

- Preserve the existing original workbook and human engineering approval gates.
- Do not publish real project or SS files, or claim Petrobras homologation.
- Do not merge protected main or deploy without separate permission.

## Review focus

1. Duplicate members must fail rather than choose one.
2. ZIP-slip path traversal and links must fail before any reading or extraction.
3. Extra or missing manifest members must fail.
4. Oversized decompression must fail before reading content.
5. A valid manifest must not mark production approved.

### Task 1 — TDD integrity checking

**Files:** `systems/mce/tests/test_release_integrity.py` (test), `systems/mce/scripts/release_integrity.py` (code).

- [x] RED: write tests for good hash, wrong hash, unsafe path, unexpected member.
- [x] Execute tests and observe missing module failure.
- [x] GREEN: implement strict ZIP validation with SHA-256 and no extraction.
- [x] Run changed tests and complete existing suite on separated groups.
- [ ] Run the complete MCE suite on current GitHub PR SHA and inspect CI logs.

### Task 2 — Release operations

**Files:** `systems/mce/docs/RELEASE_INTEGRITY.md`, `systems/mce/README.md`.

- [x] Document exact command, exit codes, provenance limits and required human gates.
- [x] Verify the prior MCE preproduction ZIP as an external, explicitly named input.
- [ ] Obtain human release and engineering acceptance for actual host and project.

### Task 3 — Protected GitHub and deployment

- [ ] Review PR and current SHA, rerun required checks and resolve findings.
- [ ] Merge only with exact-SHA user authorization and Chronos policy gates.
- [ ] Install approved package on actual host and verify accepted project/SS workbook, FAT/SAT and rollback.
