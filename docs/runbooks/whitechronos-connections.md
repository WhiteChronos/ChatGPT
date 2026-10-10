# WhiteChronos Connections Runbook

## Purpose

Use this runbook to verify task-scoped connection state for GitHub, GitLab, TinyFish, Superpowers, GitHub Arena, and Runtime Doctor without confusing repository configuration with live provider state.

The governing boundaries are:

```text
CONFIGURED != HOST_VISIBLE
HOST_VISIBLE != AUTHENTICATED
AUTHENTICATED != TARGET_ACCESSIBLE
MIRROR_PARITY is separate from connector authentication
```

A historical PASS is evidence for that historical observation only. Provider evidence accepted by the local preflight must be no older than 15 minutes and no more than 5 minutes ahead of the evaluator clock (clock-skew allowance). Re-probe the capability required by the current task immediately before a sensitive or mutating action.

## Safe preflight sequence

### GitHub

1. Confirm the GitHub connector/tool surface is visible in the current conversation.
2. Run the safe identity probe `github.get_profile`.
3. When repository access matters, run the target probe `github.get_repo` for the required repository.
4. Bind repository evidence to the exact required target (for example, `WhiteChronos/ChatGPT`); evidence for another repository cannot satisfy the task.
5. Verify the permission required by the planned action immediately before a write.

Do not infer GitHub authentication from `.codex/config.toml`, marketplace registration, a previous conversation, or GitLab identity metadata.

### GitLab

1. Confirm the GitLab connector/tool surface is visible.
2. Run `gitlab.get_current_user`.
3. When project access matters, run `gitlab.get_project` for the required project.
4. Bind project evidence to the exact required project; evidence for another project cannot satisfy the task.
5. Read task-specific pipeline/MR/project evidence only when needed.

A GitLab account linked to a GitHub identity is identity evidence only. It is not mirror parity.

### TinyFish

1. Confirm TinyFish tools are visible in the current product surface.
2. Use a non-mutating service/account probe such as `tinyfish.get_wallet` when service authentication must be verified.
3. Keep Browser Profile health separate from service authentication.
4. Never start Agent runs, Browser runs, monitors, top-up, or auto-reload merely to prove health.

If `list_profiles` returns an internal error while the service/account probe succeeds:

```text
TINYFISH_SERVICE_AUTH=PASS
TINYFISH_PROFILE_API=DEGRADED
TINYFISH_BROWSER_READY=UNVERIFIED
```

`DEGRADED` profile state does not block TinyFish search/fetch or unrelated native GitHub/GitLab connector work.

If profile creation or a profile action is blocked by platform policy, classify the required profile capability as `HOST_POLICY_BLOCKED`. Do not bypass the platform and do not change source code to fabricate support.

If authenticated browser state is truly required and the profile API is healthy, the user completes login through the provider-managed UI. Never request a password, token, cookie, or browser storage value in chat.

## Connection status recovery

| Finding | Status | Recovery |
| --- | --- | --- |
| Required tool/plugin is not visible and host inventory was not observed | `UNAVAILABLE` | Inspect the current product surface; do not infer visibility from config. |
| Local Codex plugin/config is healthy but current Codex host lacks expected runtime tools | `HOST_RELOAD_REQUIRED` | Start a fresh supported Codex environment/new session and re-run Runtime Doctor. Do not edit source only to change host discovery. |
| Provider tool is visible but safe authentication probe fails | `USER_ACTION_REQUIRED` | Reconnect through the ChatGPT plugin/connector provider UI. |
| Required repository/project cannot be read | `FAIL` | Stop only the action that requires that target and repair provider access/permissions. |
| TinyFish service works but Browser Profile API fails | `DEGRADED` | Continue non-profile capabilities; stop only profile-dependent browser work. |
| Host/platform blocks required TinyFish profile action | `HOST_POLICY_BLOCKED` | Use a supported product surface or wait for provider/platform support; no bypass. |

## Non-secret evidence format

When using the local connection normalizer, supply only non-secret observations such as:

```json
{
  "source": "current-host",
  "operation": "github.get_repo",
  "observed_at": "RFC3339 timestamp",
  "target": "WhiteChronos/ChatGPT",
  "summary": "repository metadata read succeeded"
}
```

Never put access tokens, refresh tokens, passwords, cookies, authorization headers, browser storage, or provider session material in evidence files.

The local normalizer is:

```bash
python plugins/whitechronos-control-plane/scripts/connection_preflight.py \
  --repo . \
  --input evidence.json \
  --json
```

It normalizes evidence; it does not call ChatGPT connectors by itself.

## Mirror parity

`MIRROR_PARITY` is separate from GitHub authentication, GitLab authentication, and the GitLab-to-GitHub identity link.

For mirror-sensitive work, use the existing canonical WhiteChronos mirror/parity mechanism and require:

1. expected GitHub provider identity;
2. expected GitLab provider identity;
3. exact GitHub commit SHA;
4. exact GitLab commit SHA;
5. an evidence-eligible result whose exact SHAs match.

Do not reuse `HEALTHY` evidence from a different SHA. When `MIRROR_PARITY` is supplied as a required process layer, any value other than `HEALTHY` (or explicit `NOT_APPLICABLE` for a non-mirror task) blocks the aggregate preflight. Unknown process-layer names are rejected rather than silently discarded.

When task-specific live verification is required, declare the expected live operation in the requirement and provide fresh evidence for that exact operation and target. A bare `live_verified=true` flag is not sufficient.

## Codex plugin refresh

After repository plugin/Skill/config changes, project files alone do not prove that an already-running Codex host loaded the new capability.

From the authoritative repository root, refresh only the affected local plugins using the supported remove/add flow, for example:

```bash
codex plugin remove whitechronos-control-plane@whitechronos-repo
codex plugin add whitechronos-control-plane@whitechronos-repo
codex plugin remove tinyfish-controller@whitechronos-repo
codex plugin add tinyfish-controller@whitechronos-repo
```

Then restart the supported local client/start a new session and use Runtime Doctor with the host inventory actually observed.

## Product-surface boundary

Repository code can govern WhiteChronos/Codex tasks that load these project instructions and can package supported Skills. It cannot force unrelated ChatGPT conversations to expose every plugin, cannot force unrelated ChatGPT conversations to keep every OAuth session alive, and cannot override provider/platform security policy.

The durable contract is therefore task-scoped: required integrations are freshly checked before they are relied upon, optional degradation is reported precisely, and only the dependent action is stopped when a required capability cannot be proven.


## Structured trust boundary

Positive authentication, target-access, or live-verification claims are accepted only when the matching registered probe has `outcome=success` and the evidence source is allowlisted in the integration descriptor.

Raw provider diagnostic bodies are not emitted verbatim. Do not place OAuth tokens, Authorization headers, cookies, or other credentials in evidence. Optional degradation values use safe identifiers such as `profile_api_error`, not raw error text.

Process layers that would allow work to continue require structured fresh evidence rather than bare status strings. Mirror `HEALTHY` additionally binds `evidence_eligible=true` to the exact subject SHA; only the canonical mirror/parity mechanism can establish that evidence.
