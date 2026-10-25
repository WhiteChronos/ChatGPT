# Replica, Superpowers and Arena Implementation Plan

> For agentic workers: use Superpowers executing-plans sequentially. No independent agents are required for this bounded integration.

**Goal:** Add the eleven pinned Replica skills and six offline tools, coordinated with the existing official Superpowers plugin and GitHub Arena, with reproducible installation and tests.

**Architecture:** Keep Jakeschincariol/replica-skill, obra/superpowers and Jakeschincariol/arena-skill as separate upstreams. Package a WhiteChronos Replica controller and a selective router; preserve the official Superpowers runtime and existing Arena MCP. GitHub integration uses a reviewed branch/PR, never automatic publication of chat contents.

**Tech Stack:** Python standard library, Markdown skills, JSON plugin/registry metadata, Windows command launchers, existing GitHub connector.

**Spec:** User-approved direct implementation, 2026-10-25; source audit is retained outside this repository under the user's setup directory.

## Global Constraints

- Native Windows. No Linux/WSL/Docker installation, paid API, credential copying or model change.
- Preserve upstream license and commit provenance. Do not duplicate the official Superpowers plugin.
- Eleven Replica skills plus one integration router. Only load the skill relevant to the task.
- Scripts run only when explicitly selected; no hooks, persistent shell service or automatic deploy.
- Preserve human changes and use a draft PR for shared changes.
- Installation and skill retrieval do not prove every host or all conversations.

## Review Focus

- Tampered vendored file: installation/tool dispatch must stop on digest mismatch.
- Existing personal skill: refuse overwrite unless the managed installation owns matching bytes.
- Host lacks Python/browser/connectors: report unavailable, never simulate execution.
- Deployment/publication/payment instructions: scoped authorization and project constraints remain authoritative.
- Paths with spaces and native Windows Python: invoke subprocess argv, not shell strings.

## Tasks

- [x] Package pinned Replica source, license and controller/marketplace metadata.
- [x] Add the routing skill with repository roles, GitHub review flow and Windows adaptation.
- [x] Test and implement integrity-checked CLI/installer; preserve existing skills and provide rollback manifest.
- [x] Run 57 upstream tests plus integration regression tests and registry checks.
- [x] Install audited skills locally; verify files and actual CLI outputs. Package a portable plugin artifact.
- [ ] Refresh existing seven local system checks and the separately authorized real-model/web proofs.
- [ ] Review Arena evidence, inspect diff, commit and open/attach a draft GitHub PR. Do not merge automatically.

## Execution ledger

- User chose direct inline implementation; no extra reviewer agents or model changes were launched. Arena review perspectives were applied sequentially.
- 57 upstream tests, 5 controller tests and 68 control-plane tests passed. The pinned source matches the supplied ZIP after line-ending normalization.
- Twelve personal skills installed without overwriting existing skills. The portable package is prepared; account installation on ChatGPT web is not asserted.
- Local system checks renewed. Real-model renewal is gated on native-account execution; a host attempt failed before model launch. The web renewal returned Unknown error, so no fresh web PASS is claimed.
