# Recovery Matrix

| Finding | Action |
| --- | --- |
| Current `[agents] enabled=true` config missing or legacy `features.multi_agent` present | Treat as repository config drift; use debugging/TDD in an isolated branch. |
| Local MCP probe fails | Treat as verified local defect; debug the failing server/probe boundary. |
| Native lifecycle complete | `HOST_SUBAGENT_DISCOVERY=PASS`; use the native route even if the Broker fallback is not host-loaded. |
| Native lifecycle incomplete + Broker lifecycle complete | `HOST_SUBAGENT_DISCOVERY=PASS`; use the Broker route. |
| No complete native or Broker lifecycle, while local config/runtime is healthy | `HOST_RELOAD_REQUIRED`; start a fresh supported Codex environment/session and do not mutate source merely to repair a stale host. |
| Broker stdio manifest omits `SUBAGENT_BROKER_REPO_ROOT` passthrough | Treat as repository defect; the fallback cannot safely bind the consumer repository. |
| Codex CLI unavailable or lacks `exec --json` | Capability/environment action; do not fabricate equivalent evidence. |
| Runtime is not trusted remote/Codex Cloud | `USER_ACTION_REQUIRED` before Broker live smoke. |
| `LIVE_SMOKE_READY=YES` | The existing `smoke_real_codex.mjs` may run only when live-smoke authority exists; preserve its original acceptance criteria. |
| Live smoke fails | Isolate the verified defect before opening a bugfix/TDD cycle. |
