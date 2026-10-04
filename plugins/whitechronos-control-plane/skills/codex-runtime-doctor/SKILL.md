---
name: codex-runtime-doctor
description: Diagnose WhiteChronos Codex runtime readiness when users ask whether Arena, Subagent Broker, Superpowers, Skills, MCP tools, native multi-agent tools, or the Broker live smoke are actually loaded or running. Use for missing arena_* or subagent_* tools, stale Codex sessions, config-vs-runtime questions, and live-smoke readiness checks.
---

# Codex Runtime Doctor

Use the deterministic Runtime Doctor before making claims about live Codex capabilities.

## Evidence levels

Keep these states separate:

- `CONFIGURED` — repository files request a capability.
- `LOCAL_RUNTIME_HEALTHY` — the declared local MCP process initializes and exposes the expected tools.
- `HOST_DISCOVERED` — the current Codex host actually exposes the tools.
- `LIVE_VERIFIED` — the capability passed its approved real-runtime verification.

Never treat repository configuration as runtime proof.

## Workflow

1. Run the Doctor from the repository root:

   ```bash
   python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
   ```

2. When the current harness exposes its real tool inventory, pass each observed name with repeatable `--host-tool`. If the harness was explicitly inspected and the observed inventory is empty, add `--host-inventory-observed` so empty evidence is not confused with missing evidence. Never invent host tools from `.codex/config.toml`.
3. Read local MCP and host-discovery checks separately.
4. If the result is `HOST_RELOAD_REQUIRED`, instruct the user to start a fresh Codex environment/session and **do not change source** merely to repair a stale host.
5. If a local/config check is a verified failure, use Superpowers systematic debugging and TDD on an isolated branch.
6. Run the existing Broker smoke only when `LIVE_SMOKE_READY=YES`:

   ```bash
   SUBAGENT_BROKER_LIVE=1 node plugins/subagent-broker/scripts/smoke_real_codex.mjs
   ```

7. Preserve the approved Broker acceptance criteria. Do not weaken distinct PID, `agent_id`, worktree/branch isolation, reviewer, cancellation, or follow-up requirements.

## Truthfulness rules

- Do not call Arena strategy cards independent agents.
- Do not infer native multi-agent availability from `multi_agent = true`.
- Do not infer Broker availability from its plugin manifest or MCP config.
- Do not let CI claim host discovery or live smoke readiness without real host/runtime evidence.

Read [runtime-contract.md](references/runtime-contract.md) for status semantics and [recovery-matrix.md](references/recovery-matrix.md) when a check is not PASS.
