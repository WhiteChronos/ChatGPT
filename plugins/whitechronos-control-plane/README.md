# WhiteChronos Control Plane

The Runtime Foundation separates repository configuration from live Codex runtime evidence.

## Runtime Doctor

Run a local diagnostic without host inventory:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
```

When the current harness exposes tool names, pass each as `--host-tool`. Use `--require-live-smoke-ready` only when deciding whether the existing Subagent Broker live smoke can run.

The Doctor never runs the model-backed smoke itself and never mutates repository source. A healthy local MCP with missing host tools is classified as `HOST_RELOAD_REQUIRED`, which calls for a fresh Codex environment/session rather than a code fix.

## Current Codex subagent configuration

WhiteChronos keeps the stable V1 route explicit:

```toml
[agents]
enabled = true

[features]
multi_agent = true
```

Current upstream Codex treats `multi_agent` as the Stable V1 collaboration feature (default enabled). Stable `multi_agent_v2` can select the V2 lifecycle and may also be selected by model/runtime metadata. Runtime Doctor therefore accepts a complete observed V1 or V2 lifecycle. No configuration setting is runtime proof: host discovery still requires the actual lifecycle tools to be visible.

For fresh-session bootstrap, plugin refresh, Broker fallback binding, and the safe handoff into the approved GitHub-only implementation plan, follow `docs/runbooks/codex-subagent-runtime.md`.

