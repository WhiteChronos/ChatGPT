# GitHub Neutral Mirror Runbook

## Purpose and authority

This runbook operates the trusted GitHub Actions Neutral Mirror for
`WhiteChronos/ChatGPT`.

Authority is intentionally asymmetric:

- GitHub is the source repository and merge authority.
- GitLab project `chronoswhite-group/ChronosWhite-project` (ID `86465539`)
  is a non-authoritative exact-SHA mirror and CI evidence plane.
- TinyFish is an observer/research surface only.
- GitHub AI/Codex is advisory review only.
- Superpowers owns the development process; Arena supplies adversarial review.

A mirror success never grants merge or deploy authority.

## Bootstrap gate

The trusted workflow is:

```text
.github/workflows/gitlab-neutral-mirror.yml
```

and the protected GitHub Environment is:

```text
gitlab-neutral-mirror
```

Before any secret is provisioned, verify all of the following:

1. the reviewed workflow exists on a **protected trusted ref**, initially
   `refs/heads/main`;
2. that trusted ref contains the exact reviewed worker implementation;
3. the GitHub Environment deployment branch policy permits only the protected
   trusted ref;
4. third-party Actions are pinned to reviewed immutable commit SHAs;
5. the subject feature branch is not the executable workflow revision.

The environment policy is the authoritative secret-release boundary. A YAML
condition such as `github.ref == 'refs/heads/main'` is defense-in-depth, not a
replacement for deployment branch protection.

If these conditions are not proven:

```text
TRUSTED_WORKER_INSTALLED=NO
GITLAB_MIRROR_TOKEN=NOT_EXPOSED
```

STOP.

## GitLab credential

Use a dedicated credential limited to Git-over-HTTPS repository write for only
`chronoswhite-group/ChronosWhite-project`.

Preferred capability when the GitLab tier supports project access tokens:

```text
write_repository
```

Store only the token as the GitHub Actions environment secret:

```text
GITLAB_MIRROR_TOKEN
```

The non-secret Git username for access-token authentication is `oauth2`.

Do **not broaden** the token to the `api` scope merely for convenience.
Do not reuse a personal password or a human day-to-day token.

A GitLab **deploy token** is not the solution for this write path: its
repository capability is normally `read_repository`, not the required
Git-over-HTTPS repository push capability.

A GitLab **CI_JOB_TOKEN** is also not the final transport credential. `CI_JOB_TOKEN` does not trigger the new pipeline required by the push-only evidence contract when used for the repository push. GitLab may still use `CI_JOB_TOKEN`
internally to authenticate the running job identity.

If a project access token is unavailable on the current GitLab tier, use an
alternative project-scoped/fine-grained credential that grants only the
repository push capability required for this single mirror project. Do not
broaden permissions beyond repository write without a separate reviewed need.

Never paste the token into chat.

## Secret handling

The GitHub workflow exposes `GITLAB_MIRROR_TOKEN` only to the mirror step.

The Python runtime:

1. reads the token once;
2. creates mode-`0600` temporary credential material;
3. creates a mode-`0700` Git credential helper that contains no token literal;
4. removes `GITLAB_MIRROR_TOKEN` from the child process environment before
   invoking Git;
5. scopes the helper to the target Git commands;
6. deletes helper, credential material and temporary directory in `finally`.

The token must never appear in:

- a Git remote URL;
- command-line arguments;
- repository files;
- receipt JSON;
- uploaded artifacts;
- GitHub job summaries;
- GitLab `ci.input`;
- logs or exception text.

## Manual dispatch

The workflow is intentionally `workflow_dispatch` only.

Inputs:

```text
subject_ref=<eligible authoritative branch>
subject_sha=<exact 40-hex current GitHub branch SHA>
```

Examples of eligible ref classes remain bounded by the mirror policy:
`main`, `spec/*`, `plan/*`, `feat/*`, `fix/*`, `release/*`.

Before dispatch, re-read the GitHub branch and record its current SHA. Do not
reuse a historical SHA from an earlier review or CI run.

The trusted workflow revision is not supplied by the subject branch. It is the
GitHub revision executing the installed trusted workflow and is carried through
the mirror contract as `mirror_worker_revision`.

## Normal mirror

The worker:

1. validates the trusted workflow ref/revision;
2. re-observes `subject_ref` on authoritative GitHub;
3. requires the observed SHA to equal `subject_sha`;
4. fetches the source commit;
5. validates canonical GitHub -> GitLab direction;
6. validates that any existing GitLab target is an ancestor;
7. performs a non-force Git push with typed `ci.input` receipt fields;
8. re-observes the original GitLab target branch and GitHub source branch;
9. writes a secret-free receipt only when the exact-SHA contract still holds.

A normal mirror never uses force-push.

## Same-SHA refresh

If GitLab's original mirror branch already equals `subject_sha`, a normal push
may not create a fresh pipeline. The worker then pushes the same commit to the
deterministic reserved trigger ref:

```text
whitechronos-refresh/<digest>
```

This is **same-SHA** refresh only.

The receipt keeps:

- `mirror_ref` = original parity branch;
- `mirror_pipeline_ref` = reserved refresh branch;
- `mirror_worker_revision` = trusted GitHub worker revision.

GitLab verifies the refresh digest. Parity is still evaluated against the
original mirror branch, never against the refresh branch.

## GitLab evidence verification

Accept evidence only when the resulting GitLab pipeline proves:

```text
source=push
tag=false
pipeline.sha=subject_sha
```

and final artifacts prove:

```text
mirror-parity-final.json.status=HEALTHY
contingency-gate.json.evidence_eligible=true
ci-provider-evidence.json.subject_sha=subject_sha
ci-provider-evidence.json.worker_revision=<trusted worker revision>
```

The final evidence job re-observes both original provider refs and recomputes
freshness/parity immediately before publication.

Final success requires:

```text
GITHUB_SHA == GITLAB_MIRROR_SHA == GITLAB_PIPELINE_SHA == subject_sha
RECEIPT_VALID=YES
FINAL_PARITY=HEALTHY
EVIDENCE_ELIGIBLE=true
MIRROR_PARITY=HEALTHY
```

## TinyFish

TinyFish may be used to verify current provider documentation or diagnose
website-only behavior. It is not required for a successful mirror and is not a
trust root.

Do not use TinyFish to hold `GITLAB_MIRROR_TOKEN`, perform the authoritative
push, create a receipt, or declare `MIRROR_PARITY=HEALTHY`.

## Rotation and revocation

**Rotate** the GitLab repository-write credential on its normal lifecycle or
after any suspected exposure.

**Revoke** it immediately when:

- the trusted worker is retired;
- the GitHub Environment policy cannot be proven;
- logs/artifacts indicate possible credential exposure;
- GitLab project ownership or mirror policy changes.

After rotation:

1. update only the protected GitHub Environment secret;
2. run no broad `api` bootstrap;
3. dispatch one exact-SHA mirror;
4. require a fresh push pipeline and fresh receipt/parity evidence.

## Recovery and forbidden shortcuts

On failure, preserve evidence and fail closed.

Never repair parity by:

- force-push;
- an **API commit** that creates a different Git object;
- GitLab repository-file API writes;
- web/API/scheduled pipeline starts presented as push evidence;
- disabling branch/ref protection;
- broadening the credential to `api` without a separate reviewed need;
- making TinyFish or GitHub AI an evidence authority.

If a ref diverges, stop and investigate. Do not erase the divergent GitLab
state automatically.

## Stop conditions

Before trusted worker installation/secret provisioning:

```text
TRUSTED_WORKER_INSTALLED=NO
LIVE_MIRROR_AUTHORIZED=NO
```

After a successful exact-SHA live verification:

```text
MIRROR_PARITY=HEALTHY
MERGE_AUTHORIZED=NO
DEPLOY_AUTHORIZED=NO
PRODUCTION_COMPLETE=NO
```

A separate explicit authorization is required for every later merge/deploy
gate.


## Reviewed GitHub Action pins

The secret-bearing worker uses only reviewed immutable Action commit SHAs:

```text
actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1
actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97
actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9
```

A **separate review before updating** any of these SHAs is mandatory. Do not
replace them with mutable major/minor tags in the secret-bearing workflow.
