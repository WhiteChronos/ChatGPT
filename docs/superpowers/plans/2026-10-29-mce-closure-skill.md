# MCE closure skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans when isolated subagents are unavailable.

**Goal:** Bundle a standalone read-only MCE closure Skill and testable digest verifier.

**Architecture:** The Skill coordinates the existing MCE readiness scripts and verifies a caller-supplied evidence inventory. External approvals and GitHub merge remain independent gates.

**Tech Stack:** Python stdlib, pytest, SKILL.md.

**Spec:** docs/superpowers/specs/2026-10-29-mce-closure-skill.md

## Tasks
1. [ ] Write failing tests for file hash match, corrupted hash, escaping relative path, symlink, duplicate, invalid input and CLI return code.
2. [ ] Implement smallest read-only verifier and pass tests; rerun all MCE tests.
3. [ ] Write Skill, reference and UI metadata; validate and package skill.zip.
4. [ ] Pin GitHub PR head; publish only isolated MCE changes; confirm current CI.
5. [ ] Report external approvals as BLOCKED, not production complete.
