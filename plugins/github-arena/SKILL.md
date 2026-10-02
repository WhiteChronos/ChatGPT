---
name: github-arena
description: >-
  Apply an Arena-inspired multi-strategy review as a global quality layer for
  ChatGPT and Codex tasks, with additional GitHub-specific safeguards. Use
  automatically for every user task when this Skill is installed. Routine
  requests get a lightweight four-lens review; complex, high-impact, coding,
  repository, architecture, security, CI/CD, or explicitly requested arena or
  competition tasks get a larger strategy review. For GitHub URLs, repositories,
  commits, branches, pull requests, issues, Actions, code review, repository
  files, or GitHub connector operations, also apply the GitHub workflow and
  repository-local instructions. Adapted from Jakeschincariol/arena-skill with
  provenance and MIT license notes.
---

# GitHub Arena

Use this skill as a global quality-control layer. It adds structured adversarial review before finalizing work and preserves more specific task and project constraints.

## Operating modes

### 1. Micro Arena — default for every task

Before finalizing any answer or mutation, review the proposed result through four lenses:

1. **Evidence-first** — separate verified facts from inference; inspect authoritative sources or task inputs when material.
2. **Constraint-first** — preserve explicit user constraints, governing instructions, formats, policies, standards, tests, and compatibility requirements.
3. **Edge-cases-first** — identify likely failure modes, regressions, stale assumptions, unsafe actions, missing cases, or ambiguous dependencies.
4. **Built-to-last** — prefer maintainable, reversible, documented, extensible solutions with minimal unnecessary complexity.

Reconcile conflicts between these lenses before presenting or writing the result. Report only material findings, assumptions, trade-offs, and decisions.

### 2. Review Arena — complex or high-impact work

Use when the task affects architecture, code, repositories, CI/CD, security-sensitive configuration, public APIs, governance, many files, production systems, or other high-impact surfaces.

1. Create at least 4 distinct strategy cards with `scripts/arena_review.py cards --agents 4`.
2. Develop materially different candidate approaches, not paraphrases.
3. Attack each candidate for correctness, completeness, specificity, robustness, and clarity.
4. Revise the strongest candidates.
5. Select the result by `references/rubric.md`.
6. Verify the selected approach against the actual source of truth before any irreversible action.

If the runtime provides true isolated subagents, strategy cards may be assigned to them. Otherwise execute the passes sequentially and accurately describe them as review perspectives, not independent agents.

### 3. Full Arena — explicit request only

Use when the user explicitly asks for "arena", competing solutions, many strategies, tournament-style review, or a very high-assurance comparison.

- Read `references/upstream.md` and `references/chatgpt-adaptation.md` first.
- Run `scripts/arena_review.py plan --agents N` before starting.
- Default to 16 strategies unless the user specifies another number.
- Never claim that independent agents ran unless the runtime actually executed them.
- If isolated subagents are unavailable, state that the run is a structured single-model adaptation and use strategy cards sequentially.

## GitHub-specific workflow

When GitHub is involved:

1. Inspect repository state before proposing writes.
2. Read repository-local instructions such as `AGENTS.md`, contribution docs, CI config, and relevant code.
3. Prefer a feature branch and pull request for non-trivial changes unless the user explicitly requests direct writes.
4. Confirm repository, branch, and target path from current connector results rather than memory.
5. After mutation, verify the resulting file, commit, PR, workflow, or status.
6. Preserve external upstream provenance.
7. Verify licensing before redistributing substantive third-party source.

## Codex global installation

For Codex-wide use, read `references/codex-global.md` and run:

```bash
python scripts/install_codex_global.py
```

The installer copies this Skill into `$CODEX_HOME/skills/github-arena` (falling back to `~/.codex`) and idempotently adds a global Arena instruction block to `$CODEX_HOME/AGENTS.md`.

## Arena rubric

Use these weights:

- Correctness: 30
- Completeness: 25
- Robustness: 20
- Specificity: 15
- Clarity: 10

A verified fatal flaw makes a candidate ineligible to beat a non-fatal candidate, regardless of weighted score.

## Provenance

This skill is an adaptation of `Jakeschincariol/arena-skill`, an MIT-licensed project. See:

- `references/upstream.md`
- `references/chatgpt-adaptation.md`
- `references/rubric.md`
- `references/codex-global.md`

Do not imply that this adaptation is the upstream author's official ChatGPT or Codex port.
