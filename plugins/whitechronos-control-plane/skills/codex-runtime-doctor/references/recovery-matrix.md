# Recovery Matrix

| Finding | Action |
| --- | --- |
| Config missing or drifted | Treat as repository defect; use debugging/TDD in an isolated branch. |
| Local MCP probe fails | Treat as verified local defect; debug the failing server/probe boundary. |
| Local MCP PASS + host tools missing | `HOST_RELOAD_REQUIRED`; start a fresh Codex environment/session and do not change source. |
| Codex CLI unavailable or lacks `exec --json` | Capability/environment action; do not fabricate equivalent evidence. |
| Runtime is not trusted remote/Codex Cloud | `USER_ACTION_REQUIRED` before Broker live smoke. |
| `LIVE_SMOKE_READY=YES` | The existing `smoke_real_codex.mjs` may run; preserve its original acceptance criteria. |
| Live smoke fails | Isolate the verified defect before opening a bugfix/TDD cycle. |
