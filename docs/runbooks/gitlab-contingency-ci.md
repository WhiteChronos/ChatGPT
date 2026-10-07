# GitLab Contingency CI Runbook

## Status and authority

This runbook operates the WhiteChronos non-authoritative GitLab mirror.
GitHub repository `WhiteChronos/ChatGPT` remains the sole source-controlled
authority. GitLab project `chronoswhite-group/ChronosWhite-project` (project
ID `86465539`) may hold replicated Git objects and provider-scoped CI evidence,
but it does not gain merge, release, or production authority.

The selected transport is `neutral_worker` because the connected GitLab project
is available on the current account while native pull mirroring and GitHub
external-repository CI are plan/feature-gated. The neutral worker preserves the
same Git commit object and therefore the same immutable SHA.

## Verified preflight facts

At execution planning time the connected environment reported:

- GitLab authentication: available as `WhiteChronos`.
- Project creation permission: available.
- Existing mirror destination: private project
  `chronoswhite-group/ChronosWhite-project`, ID `86465539`.
- Destination repository state before activation: empty.
- Shared runners: enabled for the project/group.
- GitLab CI/CD jobs: enabled.
- GitLab-to-repository job-token push: disabled.
- GitHub source repository: `WhiteChronos/ChatGPT`.
- Connector project-creation action: unavailable; no duplicate project is needed.
- Native GitLab pull-mirror configuration action: unavailable in the connected tool surface.
- GitLab CI-variable/token administration action: unavailable in the connected tool surface.

Re-run these checks before changing transport or credentials.

Latest connected-project preflight (project `86465539`) also verified:

- repository remains empty before live mirror binding: no commits, branches, or pipelines;
- `restrict_user_defined_variables = true`;
- `ci_pipeline_variables_minimum_override_role = no_one_allowed`;
- `ci_push_repository_for_job_token_allowed = false`;
- shared/group runners remain enabled.

The contingency path deliberately preserves that variable lockdown. The neutral
worker passes only non-secret receipt metadata through typed/validated GitLab
pipeline inputs (`ci.input`); it does not relax pipeline-variable permissions.

## Security posture

The GitLab project is a **private, non-authoritative mirror**. Operational rules:

1. Mirror direction is one-way: GitHub -> GitLab.
2. Direct development against mirrored refs is prohibited by policy.
3. Every mirrored ref class must be protected against ordinary direct writes:
   `main`, `spec/*`, `plan/*`, `feat/*`, `fix/*`, and `release/*`.
   Configure transport-only write permission for the neutral mirror credential;
   human Developer/Maintainer workflows must not push directly to mirrored refs.
4. Do not configure a GitLab -> GitHub mirror.
5. Never store a GitHub branch-write credential in GitLab.
6. The source side requires only read access to `WhiteChronos/ChatGPT` when
   anonymous/public fetch is insufficient.
7. The target credential is restricted to writing repository objects only to
   `chronoswhite-group/ChronosWhite-project`, with expiration and rotation.
8. No release or production credential belongs in this mirror path.
9. Credential material is supplied through an external credential helper or
   approved secret store. Never pass tokens on the worker command line and never
   commit them to either repository.
10. Mirror divergence fails closed; normal operation never force-pushes.
11. Git subprocess environment is fail-closed: user-controlled `GIT_*` and
    `SSH_*` variables are removed before Git execution, then only the required
    non-interactive Git controls are set by the worker.
12. Remote arguments are validated before Git execution; option-like values,
    control characters, inline credentials, reversed providers, and mixed
    local/network endpoint pairs are rejected.

## Transport selection

The v1 transport decision is deterministic:

```text
native pull mirror available and explicitly configured -> gitlab_native_pull
otherwise                                          -> neutral_worker
```

For the current environment the recorded transport is:

```text
mirror_transport = neutral_worker
```

The neutral worker is `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py`.
It must run outside GitHub Actions as the sole execution environment. Suitable
hosts include an approved workstation, self-hosted runner, VM, NAS, or other
independent automation host with Git and Python 3.12+.

## Minimal host requirements

The independent worker host requires only:

- Git 2.x;
- Python 3.12+;
- network reachability to GitHub and GitLab;
- this repository checkout containing the reviewed worker script and policy;
- source read authentication only if public fetch is unavailable;
- target repository write authentication limited to project `86465539`.

A local GitLab server, Kubernetes, Docker, Jenkins, or a second source-control
platform is not required by this design.

## One-way synchronization

For an eligible ref, invoke the worker from the authoritative checkout:

```bash
python plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py \
  --repo-root . \
  --source-url https://github.com/WhiteChronos/ChatGPT.git \
  --target-url https://gitlab.com/chronoswhite-group/ChronosWhite-project.git \
  --target-credential-helper /absolute/path/to/git-credential-whitechronos \
  --ref main \
  --receipt mirror-receipt.json
```

The network GitLab target requires an explicit executable credential-helper path.
The worker clears inherited Git/SSH controls and applies the helper only through
per-command `git -c credential.helper=...` settings after first clearing the
helper list. Relative helper names, shell snippets, whitespace-bearing values,
and non-executable paths are rejected before any Git command runs. The command
must not contain an embedded username/token/password.

Success requires all of the following:

- the ref is policy-eligible;
- for a network GitLab target, the worker attaches a non-secret mirror receipt
  contract to the push through GitLab `ci.input` push options;
- any pre-existing target ref is an ancestor of the source ref;
- the push completes without force;
- post-sync target SHA exactly equals source SHA;
- the authoritative GitHub ref is re-observed after the push and still resolves
  to that exact source SHA before a success receipt is written;
- the receipt records `transport = neutral_worker` and contains no secret.

## GitLab CI evidence

`.gitlab-ci.yml` executes only validation/evidence stages:

```text
parity -> validate -> evidence
```

Only a branch pipeline created by the neutral worker's Git push is accepted by
workflow rules. Web, API and scheduled starts are rejected. The pipeline observes
the authoritative GitHub ref, compares it with the mirrored GitLab commit and CI
subject SHA, runs the canonical repository gates, and writes provider-scoped evidence. A green GitLab pipeline is not an authority
grant. GitLab evidence is eligible for corroboration only while parity is
`HEALTHY`.

### Trusted GitLab runtime identity

Do not trust `CI_PROJECT_ID`, `CI_PROJECT_PATH`, `CI_COMMIT_SHA`, or
`CI_PIPELINE_SOURCE` as standalone security evidence because GitLab pipeline
variables have higher precedence than most predefined variables. The parity job
therefore:

1. derives the project path and commit SHA from the actual Git checkout;
2. authenticates `GET https://gitlab.com/api/v4/job` with the current
   `CI_JOB_TOKEN`;
3. requires the token-bound job's project ID, commit SHA, ref and pipeline ID to
   match the checkout and provisioned policy; and
4. observes the authoritative GitHub branch tip and the actual GitLab `origin`
   branch tip live during the job; and
5. requires GitHub tip = GitLab tip = checkout HEAD before parity can be
   `HEALTHY`; and
6. probes the GitLab ref through the local remote name `origin`, so a
   credential-bearing URL is not copied into the process arguments.

Freshness is bound to the neutral worker receipt timestamp carried by the
worker's push options. The parity job accepts it only when the job-token API
proves the job source is `push`, the receipt digest matches, its source/target
identities and ref match policy, and receipt source/target SHAs equal the live
GitHub tip, live GitLab tip and checkout HEAD. The receipt is delivered as mandatory `spec:inputs` values and validated before
pipeline creation. Web, API and scheduled pipeline sources are rejected by
workflow rules; a direct push without the required receipt inputs fails input
validation rather than becoming eligible evidence.

## Failure handling

- `DIVERGED`: stop mirroring and investigate; do not force overwrite.
- `STALE`: evidence is ineligible until a fresh exact-SHA receipt exists.
- `UNAVAILABLE`: GitLab validation may remain diagnostic only.
- GitHub/GitLab result disagreement: block for investigation.
- Code/policy/mirror failures: no automatic retry.
- Provider infrastructure or runner-assignment failure: retry only within the
  bounded policy limit.

## Credential bootstrap boundary

The current ChatGPT GitLab connector can inspect the project and run pipelines,
but it cannot create project access tokens, CI variables, repository mirrors, or
pipeline schedules. Therefore the first live neutral-worker credential binding
must occur on an authorized external host or through GitLab's own credential UI/API.
This is an environment-binding step, not a source-code change. Do not claim the
live mirror is active until the worker returns an exact-SHA receipt and GitLab
shows that same commit.

## Rotation and recovery

- Rotate target write credentials on expiry or suspected exposure.
- After rotation, execute one dry run, then one normal synchronization.
- Verify source SHA == target SHA == CI subject SHA before accepting evidence.
- If a target ref diverges, preserve it for investigation; never erase divergence
  automatically.
