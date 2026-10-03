# WhiteChronos Subagent Broker

Native-first fallback runtime for independent Codex subagents.

## Routing

1. If the current Codex harness exposes native multi-agent spawn/follow-up/wait tools, use those.
2. Otherwise use this plugin's `subagent_broker` MCP server.
3. If neither is available, use the official Superpowers inline fallback and state that independent subagents were unavailable.

## Runtime guarantees

The broker starts independent `codex exec --json` processes, creates isolated Git snapshots/worktrees, persists lifecycle state under `.superpowers/subagents/`, and never treats a prompt persona as a subagent. Write agents never work directly on `main`.

v1 targets trusted Linux Codex remote/network workspaces. It does not create API keys, enable hosted-agent billing, or claim Windows-native process-tree verification.
