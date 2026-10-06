# Runtime Contract

The Runtime Doctor distinguishes four evidence levels:

1. `CONFIGURED`: repository declarations exist.
2. `LOCAL_RUNTIME_HEALTHY`: the declared local MCP server initializes and its `tools/list` matches the expected contract.
3. `HOST_DISCOVERED`: the current Codex host inventory contains a complete eligible tool lifecycle.
4. `LIVE_VERIFIED`: the separately approved real-runtime verification has completed.

For independent subagents, `HOST_SUBAGENT_DISCOVERY=PASS` is the route-level discovery gate. It passes when either:

- the complete native lifecycle is visible: `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, `interrupt_agent`, and `list_agents`; or
- all eight Subagent Broker lifecycle tools are visible, `SUBAGENT_BROKER_REPO_ROOT` resolves to the diagnosed repository, `codex exec resume` is available, and the Broker host check is PASS.

A partial native lifecycle never counts as discovered. If the native route is complete, a missing Broker fallback does not block the selected native route; the Broker check remains separately visible for fallback diagnostics.

`LIVE_SMOKE_READY=YES` is Broker-specific. It requires a matching expected commit when supplied, a clean tracked worktree, healthy Broker config/local MCP, an exact consumer-repository binding, `codex exec --json`, `codex exec resume`, a trusted remote/Codex Cloud runtime, and all eight Broker tools visible in the current host.

Therefore:

```text
HOST_SUBAGENT_DISCOVERY=PASS != LIVE_SMOKE_READY=YES
HOST_SUBAGENT_DISCOVERY=PASS != LIVE_VERIFIED
```

The first is sufficient to select a real independent-subagent execution route. The latter two remain separate Broker-specific verification gates.
