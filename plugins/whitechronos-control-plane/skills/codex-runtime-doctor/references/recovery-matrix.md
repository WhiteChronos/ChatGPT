# Recovery Matrix

| Finding | Action |
| --- | --- |
| `[agents] enabled=true` is absent/false and no deterministic native route is configured, or V1 is explicitly disabled without V2 | Treat as repository config drift; use debugging/TDD in an isolated branch. |
| `features.multi_agent=true` present | Current Stable V1 configuration; do not classify it as legacy drift. |
| Complete V1 or V2 native lifecycle visible | `HOST_SUBAGENT_DISCOVERY=PASS`; record the observed version and use the native route. |
| Local MCP probe fails | Treat as verified local defect; debug the failing server/probe boundary. |
| Native lifecycle incomplete + Broker lifecycle complete + exact repository binding + `codex exec resume` | `HOST_SUBAGENT_DISCOVERY=PASS`; use the Broker route. |
| No complete native or Broker lifecycle, while local config/runtime is healthy | `HOST_RELOAD_REQUIRED`; start a fresh supported Codex environment/session and do not mutate source merely to repair a stale host. |
| Broker stdio manifest omits `SUBAGENT_BROKER_REPO_ROOT` or `SUBAGENT_BROKER_CODEX_PATH` passthrough | Treat as repository defect; the fallback cannot safely reproduce the diagnosed Broker environment. |
| `SUBAGENT_BROKER_REPO_ROOT` is unset, relative, or resolves to another repository | `USER_ACTION_REQUIRED`; set it to the exact canonical consumer repository root before using the Broker route. |
| `codex exec resume` is unavailable | Broker route is incomplete; do not report `HOST_SUBAGENT_DISCOVERY=PASS` through Broker and do not mark live smoke ready. |
| Codex CLI unavailable or lacks `exec --json` | Capability/environment action; do not fabricate equivalent evidence. |
| Runtime is not trusted remote/Codex Cloud | `USER_ACTION_REQUIRED` before Broker live smoke. |
| `LIVE_SMOKE_READY=YES` | The existing `smoke_real_codex.mjs` may run only when live-smoke authority exists; preserve its original acceptance criteria. |
| Live smoke fails | Isolate the verified defect before opening a bugfix/TDD cycle. |
