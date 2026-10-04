# Runtime Contract

The Runtime Doctor distinguishes four evidence levels:

1. `CONFIGURED`: repository declarations exist.
2. `LOCAL_RUNTIME_HEALTHY`: the declared local MCP server initializes and its `tools/list` matches the expected contract.
3. `HOST_DISCOVERED`: the current Codex host inventory contains the expected tool names.
4. `LIVE_VERIFIED`: the approved real-runtime verification has completed.

`LIVE_SMOKE_READY=YES` is Broker-specific. It requires a matching expected commit when supplied, a clean tracked worktree, healthy Broker config/local MCP, `codex exec --json`, a trusted remote/Codex Cloud runtime, and all eight Broker tools visible in the current host.

Native `spawn_agent` can change the selected workflow route, but it does not substitute for the Broker-specific smoke gate.
