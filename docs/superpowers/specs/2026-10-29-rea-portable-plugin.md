# Design: standalone REA portable plugin

Goal: convert the existing independent REA engine into a plugin package for ChatGPT and Codex, without changing the engine or mixing in MCE.

Acceptance: portable plugin.json with correct schema/name; onboarding and safe-operation Skills; compatibility .codex-plugin/plugin.json; no invented remote URL/tunnel, no public listener, no credential; registration of the private MCP endpoint is an explicitly separate user/admin action. Bundle the existing read-only REA code. Test manifests and packaging as code, and source SHA pinning against the GitHub PR head.

Scope: systems/rea/plugin.json, systems/rea/.codex-plugin/plugin.json, systems/rea/skills/rea-setup and rea-operacao, tests and docs. Publish in PR #119 only. Portable ZIP is source/plugin artifact, not a live ChatGPT MCP connection.
