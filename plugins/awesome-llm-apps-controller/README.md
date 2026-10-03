# Awesome LLM Apps Controller

WhiteChronos control plane for the audited `Shubhamsaboo/awesome-llm-apps` ecosystem.

The controller provides catalog-based discovery and routing. It does not automatically execute upstream examples, register MCP servers, configure credentials, launch background services, or treat example agent architectures as native Codex/ChatGPT agents.

Generated runtime surfaces are owned by the synchronization pipeline:

- `registry/awesome-llm-apps/`
- `vendor/shubhamsaboo-awesome-llm-apps/`
- `.agents/skills/.awesome-llm-apps-managed.json`

See `upstream.lock.json` for pinned provenance.
