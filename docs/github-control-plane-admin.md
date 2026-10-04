# GitHub Control Plane Admin Runbook — Chronos Phase 1

This runbook applies the first administrative hardening slice for the WhiteChronos GitHub Control Plane.

## Preconditions

- Repository: `WhiteChronos/ChatGPT`
- Ruleset name: `Chronos`
- Ruleset id: `21770911`
- Current REST evidence at this runbook revision: `enforcement: disabled`
- Pull request `PR #57` MUST remain `DRAFT`.
- The real check-run context `github-control-plane-policy` has already been observed on the feature branch and completed successfully.
- Do not activate or modify `Chronos` until the source-controlled policy gate is green.

Source-controlled desired state:

`governance/GITHUB_CONTROL_PLANE_POLICY.json`

## Protected target refs

Configure the ruleset to include exactly:

```text
~DEFAULT_BRANCH
refs/heads/spec/**
refs/heads/release/**
```

Excluded refs remain empty.

Do not target `~ALL`.

## Phase-1 rule set

Enable only:

```text
deletion
non_fast_forward
required_linear_history
pull_request
required_status_checks
```

Remove or defer these rules before activation:

```text
creation
update
required_signatures
required_deployments
```

`creation` and `update` are lockout-prone with no bypass actors. `required_signatures` remains deferred until all legitimate write paths prove signing support. `required_deployments` belongs to the later GitHub Environments slice.

## Pull request parameters — solo mode

Use these values:

```text
required_approving_review_count: 0
require_code_owner_review: false
require_last_push_approval: false
require_extra_approval_for_unattributed_changes: false
required_review_thread_resolution: true
dismiss_stale_reviews_on_push: false
allowed_merge_methods:
  - squash
  - rebase
```

Do not require a fake self-approval. Traceability comes from PR-only integration, required checks, path policy and resolved conversations.

## Required status check

Require exactly this phase-1 context:

```text
github-control-plane-policy
```

Before adding it to the ruleset, verify a real GitHub check run exists with that exact name.

Do not add `runtime-foundation` or `cloud-runtime-foundation` as universal required checks in this slice because those workflows are currently path-filtered.

## Bypass actors

Keep `bypass_actors` empty.

Do not add a broad bypass to make a blocked merge succeed.

## Activation procedure

1. Open repository Settings -> Rules -> Rulesets.
2. Open `Chronos` and confirm id `21770911`.
3. Confirm the protected refs are exactly the three entries above.
4. Remove `creation`, `update`, `required_signatures`, and `required_deployments`.
5. Add/configure the pull-request rule with the exact solo-mode parameters above.
6. Add required status check `github-control-plane-policy` only after confirming the real check-run name.
7. Keep bypass actors empty.
8. Set enforcement to active.
9. Save the ruleset.
10. Verify the live REST state before considering the activation complete.

## REST verification

Fetch the live ruleset:

```bash
curl -fsSL \
  https://api.github.com/repos/WhiteChronos/ChatGPT/rulesets/21770911 \
  > /tmp/chronos.json
```

Validate it against the repository policy:

```bash
python pipeline/github_control_plane_policy_gate.py \
  --policy governance/GITHUB_CONTROL_PLANE_POLICY.json \
  --ruleset-json /tmp/chronos.json \
  --require-live
```

Expected:

```text
GITHUB_CONTROL_PLANE_POLICY=PASS
CHRONOS_ENFORCEMENT=ACTIVE
```

If the GitHub UI says active but the REST response still reports `enforcement: disabled`, stop. Do not claim enforcement.

## Branch canary verification

Use the current GitHub Rules API to inspect effective rules for representative branches.

Default branch:

```bash
curl -fsSL \
  "https://api.github.com/repos/WhiteChronos/ChatGPT/rules/branches/main" \
  > /tmp/rules-main.json
```

Protected spec branch:

```bash
curl -fsSL \
  "https://api.github.com/repos/WhiteChronos/ChatGPT/rules/branches/spec%2Fwhitechronos-cloud-control-plane" \
  > /tmp/rules-spec.json
```

Work branch candidate:

```bash
curl -fsSL \
  "https://api.github.com/repos/WhiteChronos/ChatGPT/rules/branches/feat%2Fcloud-runtime-foundation" \
  > /tmp/rules-feat.json
```

The intended result is:

- `main`: phase-1 `Chronos` rules apply.
- `spec/whitechronos-cloud-control-plane`: phase-1 `Chronos` rules apply.
- `feat/cloud-runtime-foundation`: this ruleset does not impose protected-target restrictions.

Do not prove this with a destructive force push, deletion or non-fast-forward update.

## Rollback

If legitimate integration is locked out after activation:

1. Stop all merge attempts.
2. Capture the current live ruleset JSON as incident evidence.
3. Set `Chronos` enforcement back to disabled.
4. Re-fetch ruleset id `21770911` and confirm the rollback through REST.
5. Record the mismatch and affected branch/check context on `PR #57`.
6. Correct the source-controlled desired state or GitHub configuration through a new reviewed change.
7. Re-run the canary before re-activating.

Do not add a broad bypass as a shortcut.

## Evidence record for PR #57

After successful activation, record only non-secret evidence:

- ruleset id: `21770911`
- verification timestamp
- enforcement value
- protected ref patterns
- required check context
- policy-gate output
- representative branch-rule verification result

Do not include cookies, tokens, Authorization headers, environment dumps, device codes or secret values.

PR #57 remains DRAFT after this administrative verification. Later hardening slices must still complete before it can become merge-ready.
