---
name: matt-pocock-controller
description: Route software-engineering and technical workflow tasks to the stable skills from mattpocock/skills as a complementary layer after the repository's primary Superpowers workflow. Use when the user explicitly asks for Matt Pocock, mattpocock/skills, grill-with-docs, domain modeling, codebase design, research, prototypes, TDD, diagnosing bugs, code review, PR shaping, setup wizards, specs, tickets, implementation, wayfinding, retrospectives, handoffs, teaching, questionnaires, or writing for agents. Preserve upstream invocation policy: model-invoked Matt skills may be selected automatically; user-invoked Matt skills require explicit user invocation. For overlapping TDD, debugging, and review workflows, prefer Superpowers unless the user explicitly requests the Matt Pocock variant or repository instructions say otherwise.
---

# Matt Pocock Controller

Treat `mattpocock/skills` as the behavioral upstream for the Matt Pocock skill set. Preserve its invocation semantics and do not silently rewrite upstream skills.

## Routing contract

1. Follow higher-priority system, user, and repository `AGENTS.md` instructions.
2. Keep the official Superpowers workflow as the default development-process layer when it is available.
3. Use a Matt Pocock skill when the user explicitly requests it, or when a model-invoked Matt skill adds specialized capability that does not conflict with the active Superpowers process.
4. Preserve upstream invocation policy:
   - model-invoked skills may be selected automatically;
   - user-invoked skills require explicit user invocation and must not be fired silently by this controller.
5. When the selected Matt skill is available in the current harness, invoke/read the current installed skill rather than relying on this controller's summary.
6. If the current harness cannot expose that skill, use the WhiteChronos mirror as a read-only reference and state that the upstream skill itself did not execute.
7. Apply GitHub Arena after implementation/review for high-impact GitHub or coding changes.

## Overlap with Superpowers

Default to Superpowers for overlapping process disciplines:

- TDD: Superpowers `test-driven-development` before Matt `tdd`.
- Debugging: Superpowers `systematic-debugging` before Matt `diagnosing-bugs`.
- Code review: Superpowers review workflow before Matt `code-review`.
- Planning/execution/branch completion: preserve Superpowers gates.

Use the Matt version instead when the user explicitly asks for it or a repository-local rule selects it.

## Matt-specialized strengths

Prefer Matt model-invoked skills for specialized needs such as:

- active domain-model sharpening;
- deep-module/codebase-design discipline;
- cited primary-source engineering research;
- throwaway prototypes as evidence;
- PR narrative/merge-danger shaping;
- human-only setup/cutover wizard generation;
- concise writing intended for agents.

For user-invoked orchestration such as `grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `implement-spec`, `wayfinder`, `retro`, `grill-me`, `handoff`, `teach`, `to-questionnaire`, or `wait-what`, tell the user which command fits and wait for explicit invocation.

## Project-scoped Codex source

The synchronization workflow projects the promoted stable Engineering and Productivity skill directories into `.agents/skills/` byte-for-byte from upstream.

Do not edit Matt-managed directories there manually. Read `references/upstream.md` for provenance and `references/skills-index.md` for the stable catalog.

The full upstream repository mirror lives at `vendor/mattpocock-skills/`. `in-progress` and `deprecated` content is mirror-only by default.

## ChatGPT scope

Use this controller as a router when installed in ChatGPT `/skills`. A user-installed Skill cannot replace ChatGPT system instructions or guarantee invocation on every product surface.
