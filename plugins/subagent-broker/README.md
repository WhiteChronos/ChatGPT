# WhiteChronos Subagent Broker

Native-first fallback runtime for independent Codex subagents.

## Routing

1. If the current Codex harness exposes native multi-agent spawn/follow-up/wait tools, use those.
2. Otherwise use this plugin's `subagent_broker` MCP server.
3. If neither is available, use the official Superpowers inline fallback and state that independent subagents were unavailable.

## Runtime guarantees

The broker starts independent `codex exec --json` processes, creates isolated Git snapshots/worktrees, persists lifecycle state under `.superpowers/subagents/`, and never treats a prompt persona as a subagent. Write agents never work directly on `main`.

v1 targets trusted Linux Codex remote/network workspaces. It does not create API keys, enable hosted-agent billing, or claim Windows-native process-tree verification.


## Repository binding

The independent Broker requires `SUBAGENT_BROKER_REPO_ROOT` to be set to the **absolute canonical root** of the consumer Git repository before the MCP server starts.

The Broker fails closed when this variable is missing, relative, points outside a Git repository, or points to a subdirectory instead of the repository root. It never infers the consumer repository from the plugin installation directory.

Example:

```bash
export SUBAGENT_BROKER_REPO_ROOT=/absolute/path/to/consumer-repository
```

Authentication for child Codex processes should rely on host-native/Codex-home state where available. The Broker does not forward `CODEX_ACCESS_TOKEN` into the child environment.
