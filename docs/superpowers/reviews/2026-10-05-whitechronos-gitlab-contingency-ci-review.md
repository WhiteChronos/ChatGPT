# WhiteChronos GitLab Contingency CI Implementation Review

**Date:** 2026-10-07  
**Architecture:** GitHub authority + non-authoritative GitLab mirror/evidence plane  
**Implementation transport:** `neutral_worker`  
**GitLab project:** `chronoswhite-group/ChronosWhite-project` (`86465539`)  
**Review status:** pre-merge implementation review; merge authority not granted by this document

## 1. Authority invariants

```text
sealed_core_sha        = 2f6fd7a785999ef7827e74f35167a452c98d7920
core_modified          = NO
github_authority       = AUTHORITATIVE
gitlab_authority       = NONE
active_failover        = DISABLED
merge_authority        = NOT_GRANTED_BY_IMPLEMENTATION
deploy_authority       = NOT_GRANTED_BY_IMPLEMENTATION
production_complete    = NO
```

The implementation does not change the WhiteChronos authority model. GitLab
receives replicated Git objects and provider-scoped validation evidence only.

## 2. Superpowers execution record

Execution used the official Superpowers inline fallback because the current
runtime exposed neither native Codex subagent lifecycle tools nor Subagent Broker
lifecycle tools. No prompt persona or Arena card is represented as an independent
agent.

TDD was applied task-by-task. Observed RED states included:

- policy module/schema absent;
- ref classifier absent;
- remote observation/parity modules absent;
- CI evidence module absent;
- mirror worker absent;
- contingency gate absent;
- `.gitlab-ci.yml` absent;
- provisioned GitLab identity not recorded;
- retry classifier absent;
- two Arena-discovered pipeline regressions (Broker image missing Git and
  non-push pipelines able to look artificially fresh).

Each RED was followed by a minimal GREEN implementation. The final focused
pre-publication suite result was:

```text
65 passed
```

## 3. Full Arena

Full Arena used the repository-installed ChatGPT adapter with 16 strategy cards,
4 rounds and bracket shape `16 -> 8 -> 4 -> 2 -> 1`. The adapter reports an
upstream-equivalent call estimate of 91, but no such independent calls are
claimed: this runtime had no isolated subagent surface, so the cards were applied
sequentially in the same model context.

The 16 cards covered systems thinking, constraints, working backwards,
evidence-first testing, decomposition, first principles, expert-panel,
Socratic and worked-example perspectives with robustness/completeness/simplicity
trade-offs.

### Candidate architectures reviewed

1. **GitLab native pull mirror / external repository CI.** Technically simple,
   but feature/tier and connector configuration availability are not guaranteed.
2. **GitHub Actions pushes the GitLab mirror.** Rejected as the sole worker
   because it makes the contingency plane depend on the primary CI provider it
   is intended to outlive.
3. **Recreate repository files through GitLab repository APIs.** Rejected
   because provider-generated commits would not preserve the authoritative Git
   commit SHA.
4. **One-time GitLab import.** Rejected as an ongoing transport because it does
   not maintain continuous exact-ref parity.
5. **Independent neutral Git worker.** Selected. It fetches the authoritative
   commit object, rejects target divergence, pushes without force, and verifies
   exact post-sync SHA equality.

### Arena findings fixed

**Important A-01 — Broker container did not explicitly provide Git.**  
The Node slim image may not include Git while Broker repository tests exercise
Git behavior. A regression test was added, observed RED, then the Broker GitLab
job was changed to install Git before tests. GREEN: pipeline contract suite.

**Important A-02 — manual/scheduled/API pipelines could fabricate freshness.**  
Using the new pipeline creation time as mirror receipt time for every pipeline
would allow a manual rerun to reset the 3600-second freshness window without a
new mirror push. A regression test was added, observed RED, then parity input was
changed so only `push` pipelines use the pipeline creation time. Non-push sources
use an epoch receipt timestamp and therefore become `STALE`/ineligible while
remaining useful for diagnostics. GREEN: pipeline contract suite.

**Important A-03 — trigger-derived freshness was replayable on job retry.**  
A retried job from an old push pipeline can have a new job creation timestamp,
so using job creation time as mirror freshness could renew stale evidence without
a new synchronization. The final design no longer trusts trigger timestamps for
freshness. The parity job live-observes the current GitHub branch ref and the
current GitLab `origin` branch ref with sanitized Git execution and requires
GitHub tip = GitLab tip = checkout HEAD. The dual-observation time is the
freshness timestamp; a retry must therefore re-prove current exact-SHA parity.

**Important A-04 — Git transport environment remained partially injectable.**  
The initial hardening removed known configuration variables but still allowed
other executable Git/SSH controls such as `GIT_ASKPASS` and `SSH_ASKPASS`.
The neutral worker now strips every inherited `GIT_*` and `SSH_*` variable,
sets its own non-interactive Git controls, and rejects option-like/control-
character remote arguments before any Git subprocess runs.

**Important A-05 — GitLab origin URL could contain credentials in subprocess argv.**  
The runner's configured `origin` URL can contain ephemeral authentication.
The parity job still uses the origin URL only inside the Python process to
validate host/path identity, but Git probes now execute `git ls-remote origin`
rather than passing that URL in argv. This keeps remote authentication in Git's
local remote configuration instead of process arguments.

No standing Critical or Important Arena finding remains in the local
implementation review.

## 4. Security review

Verified before publication:

- no committed GitHub/GitLab token or private-key literal;
- no normal `git push --force` path;
- no GitLab-to-GitHub or bidirectional mirror implementation;
- no `active_failover = true`;
- no GitLab merge-authority or deploy-authority grant;
- no `shell=True` in new Python subprocess execution;
- HTTPS inline credentials are rejected by the mirror worker;
- target divergence is rejected before write;
- provider disagreement fails closed;
- GitLab evidence is not eligible unless mirror parity is `HEALTHY`;
- retry is limited to provider-infrastructure and runner-assignment failures;
- `.gitlab-ci.yml` contains no deployment stage or environment;
- Python and Node CI images are pinned by SHA-256 digest.

The official ECC plugin was not exposed in the current harness, so no ECC runtime
execution is claimed. The repository ECC controller requirements were applied as
a focused security/CI review checklist only.

## 5. Implemented components

### Policy and schemas

- `governance/GITLAB_CONTINGENCY_CI_POLICY.json`
- `schemas/gitlab_contingency_ci.schema.json`
- `schemas/ci_provider_evidence.schema.json`

### Runtime logic

- `pipeline/gitlab_contingency_policy.py`
- `pipeline/git_mirror_observation.py`
- `pipeline/git_mirror_parity.py`
- `pipeline/ci_provider_evidence.py`
- `pipeline/contingency_ci_gate.py`
- `plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py`

### CI and operations

- `.gitlab-ci.yml`
- `docs/runbooks/gitlab-contingency-ci.md`
- `docs/runbooks/gitlab-contingency-drill.md`

### Tests

- `tests/test_gitlab_contingency_policy.py`
- `tests/test_git_mirror_observation.py`
- `tests/test_git_mirror_parity.py`
- `tests/test_ci_provider_evidence.py`
- `tests/test_contingency_ci_gate.py`
- `tests/test_gitlab_pipeline_contract.py`
- `plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py`

## 6. Environment-binding gap

Source code can prepare and verify the mirror, but a live exact-SHA mirror still
requires an external Git credential binding and a host capable of running the
neutral worker. The connected ChatGPT GitLab surface can inspect repository and
pipeline state, but it does not expose project-access-token, CI-variable, mirror,
or schedule administration actions. No credential or host is fabricated in
order to claim completion.

Therefore these states remain distinct:

```text
IMPLEMENTATION_VERIFIED     != LIVE_MIRROR_BOUND
LIVE_MIRROR_BOUND           != MERGE_AUTHORIZED
MERGE_AUTHORIZED            != RELEASE_AUTHORIZED
```

A live mirror can be called active only after the worker produces an exact-SHA
receipt and GitLab independently reports the same commit for the mirrored ref.

## 7. External verification evidence

The implementation was published as one commit directly on the authoritative
`main@8a3f175b92e6355dabd8ab11f19ba93a457de059` baseline:

```text
implementation_head = cfb196c5643b9ebe00b68227d1ae54a2446f8837
branch              = feat/gitlab-contingency-ci-v1
main_ahead_by        = 1
main_behind_by       = 0
```

GitHub Actions verified the published implementation commit. The push-triggered
WhiteChronos Runtime Foundation job completed successfully with:

```text
Runtime Foundation tests       = 68 passed
full repository regression     = 226 passed
Subagent Broker compatibility  = 5 passed
Awesome Codex integration      = 3 passed
Engineering Compatibility      = 39 passed
Protocol Zero                  = 4 passed
repository governance commands = PASS
local runtime health           = PASS
```

The pull-request validation surface also completed successfully on the same
implementation HEAD:

```text
GitHub Control Plane Policy = success
Document Governance v4.7    = success
Engineering Governance      = success
Glossary Engine              = success
WhiteChronos Runtime Foundation = success
```

Together with the two successful push workflows, all seven observed GitHub
workflow runs for the implementation HEAD concluded `success`. No deploy,
canary, stable, live-smoke, R2/R3, or production workflow was part of this
verification path.


### Immutable workflow-run provenance for implementation HEAD

The seven workflow results cited above are bound to
`cfb196c5643b9ebe00b68227d1ae54a2446f8837` by their GitHub Actions run IDs:

| Run ID | Workflow | Event | Created (UTC) | Conclusion | URL |
| ---: | --- | --- | --- | --- | --- |
| 37552159196 | GitHub Control Plane Policy | push | 2026-10-07T00:28:38Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552159196 |
| 37552159288 | WhiteChronos Runtime Foundation | push | 2026-10-07T00:28:38Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552159288 |
| 37552196087 | GitHub Control Plane Policy | pull_request | 2026-10-07T00:29:06Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552196087 |
| 37552196153 | Document Governance v4.7 | pull_request | 2026-10-07T00:29:06Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552196153 |
| 37552196098 | Engineering Governance | pull_request | 2026-10-07T00:29:06Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552196098 |
| 37552196099 | Glossary Engine | pull_request | 2026-10-07T00:29:06Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552196099 |
| 37552196221 | WhiteChronos Runtime Foundation | pull_request | 2026-10-07T00:29:06Z | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37552196221 |


### Final hardening verification head

After the Codex review and subsequent Full Arena rounds, the final source-code
hardening head was:

```text
source_hardening_head = 3f748a1f086ff3285015ae4d864dd3165551b04d
branch                = feat/gitlab-contingency-ci-v1
```

Fresh GitHub Actions verification on that exact SHA produced:

```text
Runtime Foundation tests       = 73 passed
full repository regression     = 248 passed
Subagent Broker compatibility  = 5 passed
Awesome Codex integration      = 3 passed
Engineering Compatibility      = 39 passed
Protocol Zero                  = 4 passed
repository governance commands = PASS
local runtime health           = PASS
```

All five pull-request workflows for that source head completed successfully:

| Run ID | Workflow | Conclusion | Canonical run |
| ---: | --- | --- | --- |
| 37558725942 | WhiteChronos Runtime Foundation | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37558725942 |
| 37558726024 | Engineering Governance | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37558726024 |
| 37558726120 | Document Governance v4.7 | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37558726120 |
| 37558726023 | Glossary Engine | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37558726023 |
| 37558726128 | GitHub Control Plane Policy | success | https://github.com/WhiteChronos/ChatGPT/actions/runs/37558726128 |

The final Full Arena used 16 sequential strategy cards, four elimination rounds
(`16 -> 8 -> 4 -> 2 -> 1`) and the repository rubric. No isolated subagents
were available or claimed. The final Arena review left no standing Critical or
Important finding after A-01 through A-05 were closed with RED -> GREEN
regressions.

This document commit records evidence only; it does not modify source behavior
or grant merge/release authority.

## 8. Final gate

The source implementation is fully verified for the repository scope. The live
mirror remains an explicit environment-binding gate because this runtime cannot
create or install the external GitLab write credential/independent worker host.
No evidence is fabricated for that missing external binding.

```text
SOURCE_IMPLEMENTATION_VERIFIED = YES
LIVE_MIRROR_BOUND              = NO
MERGE_AUTHORIZED               = NO
DEPLOY_AUTHORIZED              = NO
PRODUCTION_COMPLETE            = NO
```

```text
IMPLEMENTATION VERIFIED != LIVE MIRROR BOUND != MERGE AUTHORIZED
```

Stop at the merge-authorization/environment-binding gates. No deploy, canary,
stable promotion, live smoke, R2/R3 or production closure is authorized by this
implementation.
