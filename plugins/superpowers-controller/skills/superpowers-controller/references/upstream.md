# Upstream provenance and policy

Primary upstream: `https://github.com/obra/superpowers`

Verified during integration:

- license: MIT, copyright Jesse Vincent (2025);
- upstream package version observed: 6.4.2;
- upstream commit observed: `8ca22dba9a94f28898bbce59f2537ff4d87c747d`;
- upstream contains a native `.codex-plugin/plugin.json`;
- OpenAI's official `openai/plugins` marketplace contains `superpowers` for CODEX;
- official marketplace version observed during integration: 6.3.0;
- the official plugin is the preferred runtime source;
- the WhiteChronos mirror must preserve upstream files without controller-specific edits.

## Version drift

The upstream repository and the OpenAI-curated marketplace may temporarily expose different versions. Treat that as normal publication lag. Record both versions rather than rewriting either distribution.

## Mirror purpose

Use `vendor/obra-superpowers/` for:

- full-text search and architecture research;
- provenance and license inspection;
- recovery if upstream is temporarily unavailable;
- comparing upstream changes before updating local integration rules.

Do not execute the mirror as a substitute for the official plugin when the official plugin is available.
