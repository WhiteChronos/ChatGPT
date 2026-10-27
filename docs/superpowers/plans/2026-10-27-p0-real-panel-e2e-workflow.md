# P0 Real Panel E2E Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Add a fail-closed GitHub Actions gate that proves the PN-AUT real-panel package has zero input gaps, frozen Step 2/Step 4/geometry, cryptographically linked evidence, and passing LI -> geometry -> CAD -> views -> QA stages.

**Architecture:** A pure-stdlib Python gate verifies the controlled artifact chain and SHA-256 links. A manual/reusable GitHub Actions workflow runs the gate plus the repository's existing geometry, multiview and final-image deterministic validators, then uploads evidence without auto-releasing engineering.

**Tech Stack:** Python 3.12, pytest, GitHub Actions, existing AUT deterministic validators.

**Spec:** datacenter/projects/25279/PN_AUT_01_PROJECT_CONTROL_V1.json and AUT Panel controls in AGENTS.md.

## Global Constraints

- Conflict or missing engineering evidence => HOLD.
- CI green is not engineering approval.
- No auto-merge and no automatic release.
- STEP2_PANEL_DEFINITION_FROZEN and STEP4_LI_LOAD_FROZEN are mandatory before P0 PASS.
- PANEL_GEOMETRY_MANIFEST_FROZEN requires zero input gaps.
- Every source reference and artifact linkage used by this gate uses SHA-256.
- Required P0 stages are exactly LI, GEOMETRY, CAD, VIEWS, QA.

## Review Focus

- A reopened Step 2 must remain HOLD even if downstream JSON says PASS.
- Any open input gap must remain HOLD.
- A changed gap register after manifest freeze must invalidate the manifest chain.
- A changed manifest after P0 execution must invalidate the P0 result.
- A failed or missing P0 stage must remain HOLD.

## Task 1: Deterministic P0 release gate

Files:
- Create pipeline/p0_real_panel_e2e_gate.py
- Test tests/test_p0_real_panel_e2e_gate.py

Interfaces:
- Consumes project-control JSON and a P0 artifact directory.
- Produces JSON gate report and process exit code 0 for PASS or 2 for HOLD.

- [x] Write failing tests for frozen-state success, reopened Step 2, open gaps, stale gap hash, stale manifest hash, failed QA stage, and missing manifest.
- [x] Run tests and confirm RED because the gate does not exist.
- [x] Implement minimal fail-closed gate.
- [x] Run tests and confirm GREEN.

## Task 2: GitHub Actions orchestration

Files:
- Create .github/workflows/p0-real-panel-e2e.yml
- Test tests/test_p0_real_panel_e2e_gate.py

Interfaces:
- Consumes the gate from Task 1 plus existing geometry/multiview/final-image validators.
- Produces a manual/reusable workflow and uploaded verification reports.

- [x] Add a failing static contract test for the missing workflow.
- [x] Create a least-privilege workflow with workflow_dispatch and workflow_call only.
- [x] Run the deterministic P0 gate, geometry gate, multiview gate and final-image gate without continue-on-error.
- [x] Upload evidence under if: always() without converting a failing engineering gate into success.
- [x] Re-run tests and YAML parse verification.
