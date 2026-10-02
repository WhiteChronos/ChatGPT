# Upstream provenance

Primary upstream: https://github.com/Jakeschincariol/arena-skill

Observed on 2026-10-02:

- public repository;
- default branch `main`;
- implementation language: Python;
- MIT license reported by GitHub;
- core files: `skills/arena/SKILL.md`, `skills/arena/bracket.py`, `skills/arena/strategies.json`, `skills/arena/rubric.md`;
- design space: 15 reasoning modes x 12 workflows x 12 strategies = 2,160 cards;
- upstream default: 100 competitors; `--quick`: 16;
- upstream orchestration depends on Claude Code's Agent/Task tool for isolated subagents.

The original system gives every competitor the same task plus a different strategy card, then runs attack, defense, revision and judging rounds.

Upstream rubric: correctness 30, completeness 25, robustness 20, specificity 15, clarity 10.

Re-check the upstream license before importing future substantive source changes.
