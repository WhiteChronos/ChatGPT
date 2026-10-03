---
name: superpowers-controller
description: Use at the start of every conversation as a lightweight router. For development, coding, debugging, architecture, repository, planning, implementation, testing, code-review, or delivery tasks, route work through the official Superpowers plugin when available. Also use when the user asks for Superpowers, obra/superpowers, TDD, brainstorming before coding, systematic debugging, implementation plans, worktrees, subagent-driven development, code review, verification, or finishing a development branch. For unrelated non-development conversations, perform only the routing check and do not impose software workflows. Prefer the official Superpowers plugin/skills; never silently replace them with modified copies. Use the WhiteChronos mirror only for provenance, auditing, search, recovery, and upstream comparison.
---

# Superpowers Controller

Treat the official `Superpowers` plugin as the runtime source of truth. Do not rewrite, fork, or substitute its behavior-shaping Skills when the official plugin is available.

## Routing contract

1. Check whether the official Superpowers plugin/Skills are available in the current harness.
2. If available, invoke or follow `using-superpowers` first, then select the relevant official Superpowers Skill before implementation.
3. Preserve the upstream workflow order and mandatory gates. Do not weaken TDD, debugging, verification, code-review, planning, or worktree requirements.
4. If the official plugin is unavailable, explain that limitation and use the WhiteChronos mirror only as a read-only reference; do not claim that the official plugin executed.
5. When GitHub work is involved, combine Superpowers process guidance with the repository's `AGENTS.md`, GitHub connector, and GitHub Arena review layer. Repository-local instructions remain additional constraints.

## Preferred official workflows

- New feature or idea: `brainstorming` before code.
- Approved design: `using-git-worktrees` and `writing-plans`.
- Implementation: `subagent-driven-development` when real subagents exist; otherwise `executing-plans`.
- Code changes: `test-driven-development`.
- Bugs/failures: `systematic-debugging` before fixes.
- Review: `requesting-code-review` / `receiving-code-review`.
- Completion: `verification-before-completion`, then `finishing-a-development-branch`.
- Skill-system failures: `diagnosing-superpowers`.

## Upstream and mirror

Read `references/upstream.md` for provenance/version policy and `references/skills-index.md` for the upstream Skill catalog.

The mirror under `vendor/obra-superpowers/` is an archival/search surface. Never edit mirrored files directly. Changes belong either in the WhiteChronos controller or upstream through the upstream project's contribution process.

## ChatGPT scope

Use this controller broadly for software-development work. A user-installed Skill can request broad automatic triggering, but it cannot replace ChatGPT system instructions or guarantee invocation in every product surface or every non-development conversation.
