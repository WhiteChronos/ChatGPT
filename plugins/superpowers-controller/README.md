# Superpowers Controller

WhiteChronos integration layer for the official [obra/superpowers](https://github.com/obra/superpowers) software-development methodology.

## Runtime policy

The controller does **not** copy or rewrite Superpowers Skills for runtime use.

Runtime order:

1. use the official `Superpowers` plugin from the OpenAI/Codex marketplace;
2. use `superpowers-controller` only for routing, provenance and WhiteChronos integration;
3. use `vendor/obra-superpowers/` only as a read-only mirror for search, audit and recovery;
4. apply repository `AGENTS.md` and GitHub Arena constraints when GitHub work is involved.

## Observed versions at integration

- upstream `obra/superpowers`: **6.4.2**, commit `8ca22dba9a94f28898bbce59f2537ff4d87c747d`;
- OpenAI official marketplace package: **6.3.0**.

Version drift is recorded, not patched locally.

## Mirror

`.github/workflows/sync-superpowers-mirror.yml` clones the upstream repository without executing upstream code and mirrors every file except `.git/` into `vendor/obra-superpowers/`.

The workflow runs on schedule, can be started manually, and also runs after controller installation changes. It opens a PR when upstream bytes change.

## ChatGPT

The packaged `superpowers-controller` Skill uses a broad routing trigger so it can check every conversation, but it only applies software-development workflows when relevant. Product-level routing still determines whether a user Skill is loaded in a given ChatGPT surface.
