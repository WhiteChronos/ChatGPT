# ECC upstream provenance

- Repository: `https://github.com/affaan-m/ECC`
- Default branch: `main`
- Observed version: `2.2.3`
- Observed commit: `ef648e01899ba3e8dc6371642deaaf64b4477775`
- License: MIT, Copyright (c) 2026 Affaan Mustafa
- Observed canonical surfaces: 293 Skills, 68 agents, 94 command shims
- Native Codex plugin: yes (`.codex-plugin/plugin.json`)
- Native Codex marketplace metadata: yes (`.agents/plugins/marketplace.json`)
- Native Codex hook surface: yes (`hooks/codex-hooks.json`)

The WhiteChronos integration prefers the upstream-native Codex plugin for runtime behavior. The mirror under `vendor/affaan-m-ecc/` is for provenance, audit, recovery, and upstream comparison only.

ECC's upstream MCP policy intentionally keeps the default connector set small. Do not enable every optional MCP merely because the mirror contains configuration for it.
