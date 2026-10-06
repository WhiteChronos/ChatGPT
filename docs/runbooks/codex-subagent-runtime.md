# Codex Subagent Runtime Bootstrap

## Purpose

Use this runbook to move WhiteChronos from repository configuration to a real independent-subagent runtime without conflating configuration, host discovery, Broker smoke, deployment, or production closure.

The required evidence chain is:

```text
CONFIGURED
-> LOCAL_RUNTIME_HEALTHY
-> HOST_SUBAGENT_DISCOVERY
-> separately authorized execution
-> post-verification
```

`LIVE_SMOKE_READY` and `LIVE_VERIFIED` remain separate Broker-specific gates.

## 1. Start from the authoritative repository state

Use the current `main` after all separately authorized prerequisite PRs have merged.

Confirm:

```bash
git status --porcelain
git rev-parse HEAD
```

Do not use a stale planning branch as an implementation baseline.

## 2. Verify current Codex native-agent configuration

WhiteChronos keeps the current stable Codex V1 feature explicit while leaving the host free to select V2 through model metadata or an explicit V2 feature:

```toml
[agents]
enabled = true

[features]
multi_agent = true
```

In current upstream Codex, `features.multi_agent` is the canonical **Stable** V1 collaboration feature and defaults to enabled. `agents.enabled` is also enabled by default and can disable native agents when set to false. The stable `features.multi_agent_v2` selector, when explicitly enabled (or when selected by model/runtime metadata), takes precedence and exposes the V2 lifecycle.

Repository configuration is eligibility evidence only. It does not prove that the current host loaded native subagent tools.

## 3. Refresh the local WhiteChronos plugin marketplace

Inspect the marketplaces visible to Codex:

```bash
codex plugin marketplace list
```

The repository marketplace `whitechronos-repo` is local, so do not use `codex plugin marketplace upgrade`; that command refreshes configured Git marketplaces. Reinstall the affected local plugins to refresh their materialized plugin cache:

```bash
codex plugin remove subagent-broker@whitechronos-repo
codex plugin add subagent-broker@whitechronos-repo
codex plugin remove whitechronos-control-plane@whitechronos-repo
codex plugin add whitechronos-control-plane@whitechronos-repo
```

The repository marketplace is `.agents/plugins/marketplace.json`. Project `.codex/config.toml` is loaded only for a trusted project.

Local-marketplace plugin installation materializes a plugin into Codex local plugin state. After repository plugin or MCP manifest changes, reinstall the affected local plugin, restart the supported local client, and start a new session; an already-open session does not gain newly loaded tools.

## 4. Native route: preferred

A native route is host-discovered only when one complete upstream Codex lifecycle is visible. A partial or mixed lifecycle is not sufficient.

**V1** (stable `features.multi_agent`, namespace `multi_agent_v1` in Codex internals):

```text
spawn_agent
send_input
wait_agent
resume_agent
close_agent
```

**V2** (stable `features.multi_agent_v2`, default namespace `collaboration`):

```text
spawn_agent
send_message
followup_task
wait_agent
interrupt_agent
list_agents
```

When either complete lifecycle is observed:

```text
HOST_NATIVE_SUBAGENT_DISCOVERY = PASS
HOST_SUBAGENT_DISCOVERY = PASS
selected_subagent_path = native_codex_multi_agent
```

Runtime Doctor accepts the plain action names and the known upstream namespaced forms (for example, `multi_agent_v1__spawn_agent` or `collaboration__spawn_agent`). The Broker fallback may remain absent without blocking a complete native route.

## 5. Broker fallback: explicit repository binding

If the native lifecycle is unavailable, the fallback Broker may be used only when its eight lifecycle tools are host-visible and healthy.

Before starting a local/remote Codex environment that must use the Broker, provide the canonical consumer repository root:

```bash
export SUBAGENT_BROKER_REPO_ROOT="$(git rev-parse --show-toplevel)"
```

The bundled stdio MCP manifest allowlists this name with `env_vars`, so the plugin host can pass the value from the execution environment to the Broker process.

The Broker fails closed if the variable is missing, relative, points to a subdirectory, or identifies a different repository.

Expected Broker lifecycle tools:

```text
subagent_spawn
subagent_status
subagent_wait
subagent_result
subagent_followup
subagent_list
subagent_cancel
subagent_cleanup
```

## 6. Run Runtime Doctor against the real host inventory

From the authoritative repository root:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py \
  --repo . \
  --expected-commit "$(git rev-parse HEAD)" \
  --runtime-kind trusted_remote \
  --host-tool spawn_agent \
  --host-tool send_message \
  --host-tool followup_task \
  --host-tool wait_agent \
  --host-tool interrupt_agent \
  --host-tool list_agents \
  --json
```

The example above represents a host where the complete native **V2** lifecycle was actually observed. For a V1 host, pass `spawn_agent`, `send_input`, `wait_agent`, `resume_agent`, and `close_agent` instead. Pass only tool names that are visible in the current harness. If the harness was explicitly inspected and contains zero relevant tools, use `--host-inventory-observed` without inventing `--host-tool` values.

For the Broker route, `SUBAGENT_BROKER_REPO_ROOT` must resolve to this exact repository, `codex exec resume` must be available, and all eight Broker lifecycle tools must be visible before host discovery can PASS.

Interpret the result literally:

- `HOST_SUBAGENT_DISCOVERY=PASS`: a complete real independent-subagent route exists.
- `HOST_RELOAD_REQUIRED`: start a fresh supported Codex environment/session; do not mutate source merely to repair a stale host.
- `HOST_BROKER_DISCOVERY=HOST_RELOAD_REQUIRED` with native route PASS: Broker fallback needs reload, but the selected native route is still ready.
- `LIVE_SMOKE_READY`: Broker-specific prerequisite status only. It is not authority to run the smoke.

## 7. Safe handoff to implementation plan #68

PR #68 is an approved plan artifact, not the execution baseline. Its branch diverged from the hardened `main` and predates the merged Broker security work.

Therefore, once `HOST_SUBAGENT_DISCOVERY=PASS`:

1. create a fresh implementation branch/worktree from the then-current `main`;
2. carry the approved #67 spec and #68 plan into the execution context as provenance;
3. preserve their task ordering, authority boundaries, and exact gates;
4. execute Task 1 in real Subagent-driven mode with independent implementer/reviewer evidence;
5. never rebase execution onto the stale #68 planning branch just to reuse its ancestry.

Task 8 external GitLab project/credential/mirror/CI activation remains a separate side-effect authority even though Tasks 1-10 implementation work was previously authorized.

## 8. Gates that remain independent

None of these are implied by configuration, CI, host discovery, or implementation success:

```text
MERGE
DEPLOY
CANARY
STABLE
LIVE SMOKE
R2/R3
PRODUCTION COMPLETE
```

The governance invariant remains:

```text
VERIFIED != AUTHORIZED != EXECUTED != SUCCESSFUL
```
