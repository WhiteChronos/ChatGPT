# Obsidian + WhiteChronos — integration runbook (proposal)

## Objective and ownership
Obsidian is a local Markdown knowledge workspace; GitHub is the sole authoritative source for approved code and skills. Notes must not be executed as instructions or auto-installed as skills. This document does not grant permission to install software or change credentials.

## Local Windows prerequisites (manual installation)
1. Download Obsidian only from https://obsidian.md/download; inspect installer publisher and sign-in prompts.
2. Install Git for Windows from https://git-scm.com/download/win; verify `git --version`.
3. Create a dedicated, non-privileged local vault, outside the repository checkout, e.g. `%USERPROFILE%\Documents\WhiteChronos-Knowledge`.
4. Within Obsidian Community plugins, browse for `Git` (`obsidian-git`) by Vinzent; review permissions and enable only after trust review.
5. Never paste API keys, tokens, private engineering baselines, personal data, or company confidential notes into a public repository.

## Recommended repository boundaries
- Keep the GitHub WhiteChronos/ChatGPT repository as authority for workflows, code, approval and versioned skill entrypoints.
- Keep private vault on disk; optionally sync to a *separate private repository* after explicit authorization and secret-scanning. Never activate auto-push to a public repository.
- Sync approved, sanitized documentation from vault via reviewed PRs; avoid bidirectional automatic editing of `main`.
- A proposed lesson/defect note should contain date, reproduction, expected vs actual, source URLs, privacy class, owner, status, and closure evidence.
- Reuse existing skills before proposing a new one. Validate SKILL.md, tests, licensing, provenance and regression results.

## Validation matrix
- LOCAL_INSTALLED: Obsidian executable starts on target Windows host.
- VAULT_READY: Markdown note created/read in approved vault.
- GIT_READY: local git CLI works and plugin can show repository status.
- SYNC_VERIFIED: controlled commit and fetch to separately authorized private target; check conflicts and secrets.
- SKILL_PROPOSAL_VERIFIED: generated skill candidate passes validation and review without modifying approved skills.
- HOST_INSTALLED: real target ChatGPT/Codex host confirms skill availability, independently of GitHub CI.

## Rollback
Disable Obsidian Git auto-sync; disconnect any authorized remote; restore versioned notes from backup. Never delete a vault as a repair step.

## Security and performance
Use a small dedicated vault instead of opening the full WhiteChronos software checkout (many files). Prefer manual synchronization initially. Enable interval-based sync only after conflict, data exposure, CPU and disk impact are measured. No merge, deployment, silent installation, autonomous approvals or `PRODUCTION_COMPLETE` implied.
