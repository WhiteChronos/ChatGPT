# WhiteChronos Codex Cloud Runbook

This runbook publishes the first WhiteChronos cloud execution environment without depending on a user desktop or third-party VM.

## Required repositories

The initial environment contains exactly:

- `WhiteChronos/ChatGPT`
- `WhiteChronos/subagent-broker-runtime`

The repository-backed contract is `datacenter/WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json`.

## What is not required

Desktop Commander is not required for the WhiteChronos Cloud Control Plane.

DigitalOcean is not required for the WhiteChronos Cloud Control Plane.

Neither should be added as a hidden prerequisite for Cloud readiness.

## 1. Create the Codex Cloud environment

In Codex on the web or desktop, create a personal or workspace cloud environment and include the two required repositories above. A published environment makes its prepared configuration reusable by new cloud tasks; it is not the durable project history. GitHub remains the source of truth.

If cloud controls are unavailable, verify the current ChatGPT plan/workspace Cloud access setting before changing repository code.

## 2. Configure dependency network access

Use only the hosts declared by the profile for bootstrap dependency installation:

- `registry.npmjs.org`
- `pypi.org`
- `files.pythonhosted.org`

Do not add wildcard hosts. Repository checkout/access is provided by the Codex Cloud GitHub connection and environment repository selection rather than by storing a GitHub credential in this profile.

## 3. Keep credentials outside Git

Long-lived credentials belong in the supported Codex/OpenAI secret or vault controls, never in Git, `memory/`, `datacenter/`, `datasheet/`, `history/`, command output, or screenshots. The profile records secret requirement names only.

## 4. Run the bounded setup

After the environment shows the actual checkout locations, run the setup command with those paths. The paths below are examples only; use the paths shown by the cloud workspace:

```bash
python plugins/whitechronos-control-plane/scripts/setup_codex_cloud.py \
  --repo-root /workspace/ChatGPT \
  --repo-path WhiteChronos/ChatGPT=/workspace/ChatGPT \
  --repo-path WhiteChronos/subagent-broker-runtime=/workspace/subagent-broker-runtime \
  --apply \
  --json
```

Without `--apply`, `setup_codex_cloud.py` is a dry-run and does not execute dependency installation.

## 5. Publish and start a fresh task

Publish the environment after setup/configuration is correct. Changes to a published environment apply to new tasks; existing tasks keep their own workspace state. Start a **new** Codex Cloud task from the published environment before performing the runtime handoff.

## 6. Run Cloud preflight

In the fresh cloud task, run:

```bash
python plugins/whitechronos-control-plane/scripts/cloud_preflight.py \
  --repo-root /workspace/ChatGPT \
  --repo-path WhiteChronos/ChatGPT=/workspace/ChatGPT \
  --repo-path WhiteChronos/subagent-broker-runtime=/workspace/subagent-broker-runtime \
  --require-ready \
  --json
```

The preflight proves repository/toolchain readiness only. It does **not** prove host discovery or live agent execution.

## 7. Runtime Doctor handoff

After Cloud preflight is ready, continue with Runtime Doctor. Runtime Doctor remains the authority for runtime evidence. If it returns `HOST_RELOAD_REQUIRED`, create another fresh cloud task/session from the published environment instead of rewriting source.

Do not run the Subagent Broker real smoke until Runtime Doctor reports `LIVE_SMOKE_READY=YES`.

The real smoke remains the final proof for real child processes, distinct PIDs and agent IDs, isolated writer worktrees, reviewer isolation, follow-up continuity when supported, cancellation, and redacted evidence.

## Recovery

If a task becomes stale or its VM is no longer recoverable, start a fresh task from the published environment, recover the branch/commit from GitHub, rerun `cloud_preflight.py`, then rerun Runtime Doctor. Uncommitted state from another task is not assumed to exist.

## Official OpenAI platform references

- https://help.openai.com/pt-br/articles/20001545-using-codex-cloud
- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted
- https://developers.openai.com/api/docs/guides/agents-api/environments/security

These links describe the current OpenAI product/platform behavior. Repository tests and Runtime Doctor remain the evidence for WhiteChronos project state.
