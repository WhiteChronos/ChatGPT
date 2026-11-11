# Upstream provenance

## Source of truth

- Repository: `https://github.com/mattpocock/skills`
- Default branch: `main`
- License: MIT
- Version observed: `1.2.3`
- Commit observed: `d81f3a183412e71a5b1e84ca21bc1a35eea03a60`
- License copyright: Matt Pocock, 2026

Upstream describes the repository as composable engineering/productivity skills.

## Codex compatibility

At the observed revision, upstream states that a native Codex plugin is still on the roadmap. The documented Codex/other-agent install route is:

`npx skills@latest add mattpocock/skills`

Since version 1.2.0, every promoted skill also carries `agents/openai.yaml` metadata for Codex. User-invoked skills use `policy.allow_implicit_invocation: false`; model-invoked skills omit that restriction.

WhiteChronos therefore copies the promoted stable skill directories without modification into project-scoped `.agents/skills/`. This preserves upstream metadata while avoiding a second independently managed `skills.sh` install.

## Mirror policy

- Full upstream bytes are mirrored under `vendor/mattpocock-skills/`.
- Synchronization never executes upstream code.
- `skills/engineering` and `skills/productivity` directories containing `SKILL.md` are projected into `.agents/skills/`.
- `in-progress`, `deprecated`, and other repository content remain available in the full mirror but are not implicitly installed.
- The sync refuses to overwrite an unmanaged project skill with the same name.
- Upstream changes land through a synchronization PR, not directly on `main`.
