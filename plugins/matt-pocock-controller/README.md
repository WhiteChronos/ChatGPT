# Matt Pocock Skills Controller

WhiteChronos integration for `mattpocock/skills`.

## Purpose

Keep Matt Pocock's upstream repository intact and updateable while making its promoted stable Engineering and Productivity skills available to Codex at project scope.

This controller is complementary to the official Superpowers workflow:

1. **Superpowers** remains the default software-development process layer.
2. **Matt Pocock skills** add specialized engineering/productivity disciplines.
3. **GitHub connector** provides repository evidence and mutations.
4. **GitHub Arena** remains the final adversarial review layer for high-impact work.

## Upstream

- Repository: `mattpocock/skills`
- License: MIT
- Observed version: `1.2.3`
- Observed main commit: `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`
- Native Codex plugin: not published upstream at the observed revision
- Upstream Codex route: `npx skills@latest add mattpocock/skills`

The WhiteChronos repository does **not** run that installer automatically, because doing so would create a second independently managed copy. Instead, the sync workflow copies the promoted stable skill directories byte-for-byte into `.agents/skills/` and keeps the entire upstream repository in a read-only mirror.

## Layout

- `skills/matt-pocock-controller/` — routing/provenance Skill.
- `scripts/sync_mirror.sh` — byte mirror + stable-skill projection.
- `tests/test_sync_mirror.sh` — deterministic sync/collision tests.
- `upstream.lock.json` — observed upstream version/commit.
- `vendor/mattpocock-skills/` — full upstream mirror, read only.
- `.agents/skills/` — promoted stable Engineering/Productivity skills managed by the sync workflow.

## Invocation policy

The upstream distinction is preserved:

- **Model-invoked** skills may be selected automatically when the task fits.
- **User-invoked** skills remain explicit-only. The controller may recommend one, but must not silently execute it.

See `skills/matt-pocock-controller/references/skills-index.md`.

## Updating

`.github/workflows/sync-matt-pocock-skills.yml` refreshes the mirror and project skills, then opens a pull request. Upstream code is copied but not executed during synchronization.

Never edit `vendor/mattpocock-skills/` or Matt-managed directories under `.agents/skills/` manually.
