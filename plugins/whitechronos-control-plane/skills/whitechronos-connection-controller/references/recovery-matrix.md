# Recovery matrix

| Finding | Action |
| --- | --- |
| Tool/plugin absent from observed host | `UNAVAILABLE` or `HOST_RELOAD_REQUIRED` according to real platform/runtime evidence; do not claim access. |
| Provider tool visible but safe auth probe fails | `USER_ACTION_REQUIRED`; reconnect through the provider/plugin UI. |
| Required target probe fails | `FAIL`; stop only the dependent action. |
| GitHub/GitLab authenticate but parity differs | `FAIL` for mirror-sensitive work; use the canonical mirror/parity workflow. |
| TinyFish service probe passes and Browser Profile API fails | `DEGRADED`; search/fetch may continue, profile-dependent browser work stops. |
| TinyFish profile creation is blocked by host policy | `HOST_POLICY_BLOCKED`; do not bypass or mutate source to fake support. |
| Runtime Doctor returns `HOST_RELOAD_REQUIRED` | Start a fresh supported Codex environment/session; do not edit source merely to change host discovery. |
