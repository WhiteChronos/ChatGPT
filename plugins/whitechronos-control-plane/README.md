# WhiteChronos Control Plane

The Runtime Foundation separates repository configuration from live Codex runtime evidence.

## Runtime Doctor

Run a local diagnostic without host inventory:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
```

When the current harness exposes tool names, pass each as `--host-tool`. Use `--require-live-smoke-ready` only when deciding whether the existing Subagent Broker live smoke can run.

The Doctor never runs the model-backed smoke itself and never mutates repository source. A healthy local MCP with missing host tools is classified as `HOST_RELOAD_REQUIRED`, which calls for a fresh Codex environment/session rather than a code fix.
