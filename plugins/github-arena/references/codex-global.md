# Codex global installation

Codex can read user-level instructions from `AGENTS.md` or `AGENTS.override.md` under `$CODEX_HOME`, in addition to project-local instructions. A global install therefore has two parts:

1. copy this Skill into `$CODEX_HOME/skills/github-arena`;
2. add an idempotent Arena instruction block to `$CODEX_HOME/AGENTS.md`.

The bundled `scripts/install_codex_global.py` performs both steps. It uses `$CODEX_HOME` when set, otherwise `~/.codex`.

## Scope and precedence

- This is a user-level Codex instruction layer, not an OpenAI system prompt.
- More specific project instructions may add constraints and should be preserved.
- The global Arena block never erases unrelated user instructions.

## ChatGPT scope

Installing the Skill in ChatGPT makes it eligible for automatic selection based on its broad description. A user-created Skill does not rewrite ChatGPT's internal system behavior, so product routing still determines when a Skill is loaded.
