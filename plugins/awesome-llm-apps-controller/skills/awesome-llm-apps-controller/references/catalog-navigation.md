# Catalog navigation

Primary file: `registry/awesome-llm-apps/catalog.json`.

1. Match user intent against `title`, `category`, `subtype`, `upstream_path`, framework/provider metadata, and attached component paths.
2. Prefer `upstream_internal` entries because their source is represented in the audited functional mirror.
3. Treat `external_reference` as discovery-only until separately audited.
4. Preserve `upstream_commit` in any technical recommendation or adaptation so the source snapshot is reproducible.
5. Read `readme_path`, `skill_paths`, manifests, MCP paths, Docker paths, and environment examples only as needed.
6. Check `execution_class`, credential/network/background/self-modifying flags, and any high-stakes flag before activation.
7. For excluded source/media, consult `registry/awesome-llm-apps/.whitechronos-excluded.json`; do not silently commit excluded upstream assets into the repository.
