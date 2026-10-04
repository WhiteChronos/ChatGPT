# WhiteChronos Control Plane

The Runtime Foundation separates repository configuration from live Codex runtime evidence.

## Runtime Doctor

Run a local diagnostic without host inventory:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
```

When the current harness exposes tool names, pass each as `--host-tool`. Use `--require-live-smoke-ready` only when deciding whether the existing Subagent Broker live smoke can run.

The Doctor never runs the model-backed smoke itself and never mutates repository source. A healthy local MCP with missing host tools is classified as `HOST_RELOAD_REQUIRED`, which calls for a fresh Codex environment/session rather than a code fix.


## Codex Cloud Runtime Foundation

The cloud environment contract lives at:

`datacenter/WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json`

Preview the bounded setup without executing dependency installation:

```bash
python plugins/whitechronos-control-plane/scripts/setup_codex_cloud.py \
  --repo-root . \
  --repo-path WhiteChronos/ChatGPT=/path/to/ChatGPT \
  --repo-path WhiteChronos/subagent-broker-runtime=/path/to/subagent-broker-runtime \
  --json
```

Validate a prepared environment:

```bash
python plugins/whitechronos-control-plane/scripts/cloud_preflight.py \
  --repo-root . \
  --repo-path WhiteChronos/ChatGPT=/path/to/ChatGPT \
  --repo-path WhiteChronos/subagent-broker-runtime=/path/to/subagent-broker-runtime \
  --require-ready \
  --json
```

Cloud preflight proves repository/toolchain readiness only; it is not host discovery or live-runtime proof.

See `docs/codex-cloud.md` for the publish and recovery runbook.
