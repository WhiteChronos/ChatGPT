---
name: github-arena
description: Apply an Arena-inspired multi-strategy review to ANY task involving GitHub, repositories, GitHub URLs, commits, branches, pull requests, issues, Actions, code review, repository architecture, repository files, GitHub connector operations, or changes intended for GitHub. Use automatically whenever ChatGPT will read from, search, analyze, create, edit, or review content in GitHub. For routine work, run a lightweight multi-lens review; for high-impact or explicitly requested arena/competition tasks, use a larger strategy set and the bundled planner. Adapted from Jakeschincariol/arena-skill with provenance and MIT license notes.
---

# GitHub Arena

Use this skill as the control layer for GitHub work. It does not replace the GitHub connector; it improves how the task is reasoned about, checked, and reviewed.

## Operating modes

### 1. Micro Arena — default for every GitHub task

Before finalizing any GitHub answer or mutation, review the proposed result through four independent lenses:

1. **Evidence-first** — verify claims against repository files, diffs, issues, PRs, Actions, or official docs; distinguish verified fact from inference.
2. **Constraint-first** — preserve explicit constraints, repository conventions, branch policy, licenses, tests, and compatibility requirements.
3. **Edge-cases-first** — identify likely failure modes, regressions, stale assumptions, merge conflicts, missing tests, or unsafe writes.
4. **Built-to-last** — prefer changes that remain maintainable, reversible, documented, and easy to extend.

Reconcile disagreements before presenting or writing the result. Do not expose internal deliberation unless requested; report only material findings and decisions.

### 2. Review Arena — high-impact GitHub work

Use when the task changes architecture, CI/CD, security-sensitive configuration, repository governance, many files, public APIs, or other high-impact surfaces.

1. Create at least 4 strategy cards with `scripts/arena_review.py cards --agents 4`.
2. Develop materially different candidate approaches.
3. Attack each candidate for correctness, completeness, specificity, robustness, and clarity.
4. Revise the strongest candidates.
5. Select the result by `references/rubric.md`.
6. Verify the selected approach against the actual repository before any write.

If the runtime provides true isolated subagents, strategy cards may be assigned to them. Otherwise execute passes sequentially and do not call them independent agents.

### 3. Full Arena — explicit request only

Use when the user explicitly asks for arena, competing solutions, many strategies, or a tournament-style review.

- Read `references/upstream.md` and `references/chatgpt-adaptation.md`.
- Run `scripts/arena_review.py plan --agents N`.
- Default to 16 strategies for practical use unless the user asks otherwise.
- Never claim that 100 independent agents ran unless the runtime actually executed them.

## GitHub connector workflow

1. Inspect repository state before proposing writes.
2. Read repository-local instructions such as `AGENTS.md`, contribution docs, CI config, and relevant code.
3. Prefer a feature branch and pull request for non-trivial changes unless direct writes are explicitly requested.
4. Confirm repository, branch, and target path from connector results rather than memory.
5. Verify resulting file, commit, PR, or workflow state after mutation.
6. Preserve external upstream provenance.
7. Verify licensing before redistributing substantive third-party source.

## Arena rubric

- Correctness: 30
- Completeness: 25
- Robustness: 20
- Specificity: 15
- Clarity: 10

A verified fatal flaw cannot beat a non-fatal candidate.

## Provenance

This is an adaptation of `Jakeschincariol/arena-skill`, an MIT-licensed project. It is not an official ChatGPT port by the upstream author.
