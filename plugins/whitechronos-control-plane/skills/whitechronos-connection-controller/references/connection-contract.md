# Connection contract

Keep these dimensions separate for every integration:

- `configured`: repository/project registration exists.
- `host_visible`: the current product surface exposes the integration.
- `authenticated`: a safe provider probe succeeds.
- `target_accessible`: the task's required repository/project/resource is readable with the current connection.
- `live_verified`: the exact task-specific live capability was demonstrated when that proof is required.

Use statuses: `PASS`, `DEGRADED`, `FAIL`, `UNAVAILABLE`, `HOST_RELOAD_REQUIRED`, `USER_ACTION_REQUIRED`, `HOST_POLICY_BLOCKED`, `SECURITY_REVIEW_REQUIRED`, `NOT_APPLICABLE`.

`DEGRADED` is non-blocking unless the degraded sub-capability is required by the current task.

Provider-safe probes registered by WhiteChronos include `github.get_profile`, `github.get_repo`, `gitlab.get_current_user`, `gitlab.get_project`, and `tinyfish.get_wallet`. These names describe evidence contracts; the local Python normalizer does not invoke ChatGPT tools.

Process-layer evidence (`SUPERPOWERS`, `ARENA`, `RUNTIME_DOCTOR`) is displayed separately from connection observations. It never manufactures provider authentication or mirror parity.


## Freshness and binding

The normalizer accepts provider evidence only when it is fresh: at most 15 minutes old, with at most 5 minutes of future clock skew. Older or implausibly future-dated evidence is rejected.

A target-required requirement must name the exact expected target. The registered target probe must carry evidence for that exact target; evidence for a different repository/project never satisfies the requirement.

A live-verification-required requirement must declare the exact live operation. A true boolean without evidence for that operation (and the required target when one exists) is rejected.

`MIRROR_PARITY` is an explicit process layer. `HEALTHY` is non-blocking; failure, divergence, stale, or unavailable parity blocks mirror-sensitive work. Unknown process-layer names are rejected.
