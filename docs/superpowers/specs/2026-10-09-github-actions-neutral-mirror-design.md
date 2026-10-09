# GitHub Actions Neutral Mirror + GitLab Evidence Plane Design

**Status:** Written specification awaiting user review  
**Date:** 2026-10-09  
**Repository:** `WhiteChronos/ChatGPT`  
**Baseline:** `feat/gitlab-contingency-ci-v1@e2d5c282223564adb6f2fbda15a063c4b7fd536b`  
**Related PR:** #76  
**Architecture approval:** GitHub Actions neutral worker + GitLab write_repository + TinyFish observer + GitHub AI advisory

## 1. Purpose

Close the remaining GitHub-to-GitLab exact-SHA mirror/evidence gap without weakening the repository's existing governance, Superpowers workflow, Arena review layer, or merge/deploy gates.

The system must produce a real GitLab branch pipeline from an authenticated Git push of the exact GitHub commit SHA, while preserving GitHub as the only source-control and merge authority.

The design deliberately separates four responsibilities:

1. **GitHub** — authoritative source repository, pull requests, source CI and merge authority.
2. **GitLab** — non-authoritative exact-SHA mirror and contingency evidence provider.
3. **TinyFish** — external observer/research/browser automation surface; never an evidence-minter or merge authority.
4. **GitHub AI / Codex reviewer** — advisory review surface; useful when available, but not a required availability dependency for source correctness.

Superpowers remains the software-development process owner. GitHub Arena remains the adversarial quality/review layer.

## 2. Existing Baseline and Already-Resolved Defects

This architecture builds on PR #76 rather than replacing it.

The baseline already contains and must preserve these fixes:

- `pipeline/ci_provider_evidence.py` imports `Path` from `pathlib`, so persisted evidence loading cannot fail with `NameError: Path is not defined`.
- `.gitlab-ci.yml` is syntactically valid and uses RE2-compatible full-text anchors.
- `mirror_pipeline_ref` is a **branch/ref input**, not a 40-character commit SHA.
- eligible GitLab evidence is `push`-only;
- tag jobs cannot establish branch receipt evidence;
- same-SHA freshness uses a reserved `whitechronos-refresh/<digest>` branch;
- final evidence re-observes GitHub and GitLab and recomputes parity/freshness;
- source and target credential helpers are independently scoped;
- SCP-style remotes are treated as network remotes;
- persisted mirror records carry full-record integrity digests;
- mandatory test globs fail closed;
- provider evidence binds input artifact SHA-256 digests;
- retry attempt comes from trusted CI runtime state;
- provider evidence is retained durably;
- persisted evidence loading normalizes timestamp strings to timezone-aware datetimes.

The new subsystem must not regress or duplicate these behaviors.

## 3. Problem Statement

The remaining live-binding problem is not source code correctness. It is transport and evidence provenance.

A valid closure requires:

```text
GitHub authoritative commit SHA
        ==
GitLab mirrored branch SHA
        ==
GitLab push-pipeline SHA
```

plus:

```text
pipeline source = push
tag = false
fresh receipt
final parity = HEALTHY
evidence_eligible = true
```

The previous GitLab controller/bootstrap path cannot be the final transport because the final evidence contract requires a real push-triggered pipeline. A controller that merely writes repository state or starts API/pipeline workflows cannot substitute for the authenticated Git push.

The neutral mirror worker therefore moves to GitHub Actions, where the authoritative SHA already exists and the source repository does not need to be rediscovered through a second control plane.

## 4. Selected Architecture

### 4.1 Control flow

```text
GitHub PR / branch
      |
      | exact authoritative commit SHA
      v
GitHub Actions Neutral Mirror Worker
      |
      | hardened git fetch/checkout
      | hardened ephemeral GitLab credential helper
      | non-force git push
      | Git push options: ci.input=...
      v
GitLab exact-SHA mirror
      |
      | source=push
      | tag=false
      v
GitLab parity / governance / broker / evidence pipeline
      |
      | receipt + final parity + provider evidence
      v
WhiteChronos Control Plane
      |
      | corroboration only
      v
Pre-merge gate
```

### 4.2 Authority model

| Component | May read | May write mirror | May mint evidence | May merge GitHub | May deploy |
| --- | --- | --- | --- | --- | --- |
| GitHub source workflows | Yes | Through dedicated worker only | GitHub evidence | No automatic merge | No |
| GitHub neutral mirror worker | Yes | Yes, GitLab mirror refs only | Mirror receipt only | No | No |
| GitLab | Yes | Receives Git push | GitLab contingency evidence | No | No |
| TinyFish | Yes | No | No | No | No |
| GitHub AI/Codex | Yes | Review comments only | Advisory review only | No | No |
| Superpowers/Arena | Review/process | No direct mirror authority | Process/review evidence | No | No |

No component other than GitHub's normal human-authorized merge workflow gains merge authority.

## 5. GitHub Actions Neutral Mirror Worker

### 5.1 Workflow

Create a dedicated workflow, proposed path:

```text
.github/workflows/gitlab-neutral-mirror.yml
```

The workflow must be callable intentionally and must never run as an unrestricted automatic mirror of arbitrary refs.

Allowed triggers should be limited to one or both of:

- `workflow_dispatch` with strongly validated branch/ref input;
- `workflow_call` from a repository-controlled gate workflow.

It must not run on arbitrary fork-controlled workflow code with access to the GitLab write credential.

### 5.2 Source SHA

The worker must resolve the authoritative source SHA from the GitHub runner context and then prove that:

- the requested ref belongs to `WhiteChronos/ChatGPT`;
- the commit exists in the authoritative repository;
- the commit SHA is exactly the subject intended for mirror verification;
- a later source-ref re-observation still resolves to the same SHA before evidence is accepted.

Caller-provided SHA text alone is not authority.

### 5.3 GitLab credential

Use a dedicated GitLab credential with the least privilege that still permits Git-over-HTTPS push.

Preferred permission:

```text
write_repository
```

The credential must:

- be stored only as a GitHub Actions secret;
- never be committed;
- never be echoed;
- never be embedded in the remote URL;
- never appear in process arguments, logs, artifacts, receipts or job summaries;
- be exposed only to the mirror step;
- be consumed through a temporary credential helper or equivalent stdin-based Git credential mechanism;
- be removed at the end of the job even on failure.

Do not grant GitLab API authority when `write_repository` is sufficient.

### 5.4 Git hardening

The worker must reuse the hardening semantics of `sync_gitlab_mirror.py`:

- `GIT_CONFIG_NOSYSTEM=1`;
- isolated/global config suppression;
- `GIT_TERMINAL_PROMPT=0`;
- strip unsafe inherited `GIT_*` and `SSH_*` environment variables;
- no shell-interpolated credential values;
- no force push;
- no tag transport for branch evidence;
- canonical GitHub source and GitLab target identity validation;
- explicit source and target credential scopes.

### 5.5 Push behavior

Normal case:

```text
source ref -> same target branch
```

If the target branch does not already contain the source SHA, push the exact commit to the original branch.

Same-SHA refresh case:

If the original GitLab branch is already at the authoritative SHA but a new freshness window is required, push the same commit to:

```text
whitechronos-refresh/<sha256>
```

The refresh digest remains derived from the receipt claim fields defined by the existing worker contract.

The original mirrored branch remains the parity subject. The refresh branch exists only to cause a new authenticated `source=push` pipeline.

### 5.6 CI inputs

The Git push must carry the typed GitLab CI inputs required by the existing `.gitlab-ci.yml` contract, including:

- `mirror_transport=neutral_worker`;
- authoritative source repository;
- target project;
- original mirror ref;
- actual pipeline ref;
- source SHA;
- target SHA;
- receipt timestamp;
- receipt claim SHA-256.

`mirror_pipeline_ref` is a ref name and must continue to accept the normal branch classes plus the reserved `whitechronos-refresh/<64 hex>` class. It must never be redefined as a commit SHA.

## 6. Receipt Contract

The worker writes a local, non-secret receipt artifact after the push.

The receipt must distinguish:

- original parity ref;
- pipeline-trigger ref;
- source SHA;
- target SHA before push;
- target SHA after push;
- source repository identity;
- target project identity;
- timestamp;
- dry-run state;
- claim digest;
- full-record digest.

The claim digest is the exact value transported through GitLab `ci.input`.

The full-record digest protects the persisted audit record after semantic fields such as identities and target-before/after values are known.

Receipt data must contain no credentials.

## 7. GitLab Pipeline Contract

The existing final pipeline remains the evidence authority for the GitLab side.

### 7.1 Eligibility

Eligible evidence requires:

```text
CI_PIPELINE_SOURCE == "push"
tag == false
```

No API, web, schedule, `source=pipeline`, tag pipeline or manual repository-file mutation can establish mirror parity evidence.

### 7.2 Trusted runtime identity

The GitLab job proves:

- project ID;
- project path;
- checkout HEAD;
- pipeline SHA;
- job ref;
- pipeline source;
- tag/branch classification.

This runtime identity must match the provisioned mirror policy and receipt.

### 7.3 Original ref vs pipeline ref

For ordinary pushes:

```text
pipeline_ref == mirror_ref
```

For same-SHA refresh:

```text
pipeline_ref == whitechronos-refresh/<expected digest>
mirror_ref == original branch
```

Parity is always evaluated against `mirror_ref`, never the refresh branch.

### 7.4 Final re-observation

Immediately before publishing eligible evidence, the final job re-observes:

- GitHub authoritative original ref;
- GitLab original mirrored ref.

It then recomputes:

- provider availability;
- exact SHA equality;
- receipt freshness;
- final mirror parity.

Only this final parity result may set `evidence_eligible=true`.

## 8. Evidence Plane

GitLab provider evidence continues to require:

- configured GitLab project identity;
- exact subject SHA;
- pipeline/run identity;
- gate name;
- result;
- timezone-aware timestamp;
- CI config revision;
- `mirror_parity_status=HEALTHY`;
- actual retry attempt;
- SHA-256 digests of all consumed artifacts;
- complete provenance SHA-256.

Persisted JSON must be read through the normalized loader so timestamp strings become timezone-aware datetimes before evidence validation.

Evidence from GitLab remains corroborating/contingency evidence only. It never grants GitHub merge authority.

## 9. TinyFish Role

TinyFish is an observer, not a trust root.

Allowed uses:

- research current GitHub/GitLab documentation;
- verify public documentation or product behavior;
- inspect user-directed website flows;
- optionally monitor external UI/API behavior when explicitly requested;
- help diagnose provider-side changes that are not visible through repository APIs.

Disallowed uses for this architecture:

- holding the GitLab mirror credential;
- performing the authoritative Git push;
- minting mirror receipts;
- declaring `MIRROR_PARITY=HEALTHY`;
- replacing native GitHub/GitLab connectors for repository API operations;
- bypassing provider or host security policy.

TinyFish Browser Profile availability is optional and non-blocking for the mirror architecture.

## 10. GitHub AI / Codex Role

GitHub AI review is advisory.

When available:

- request code review;
- request security review;
- surface findings in the PR;
- fix verified findings through normal TDD.

When quota-limited or unavailable:

- record that state truthfully;
- use the approved Superpowers review fallback;
- use GitHub Arena for adversarial review;
- keep CI, regression, governance and security gates mandatory.

The system must not become unavailable solely because the advisory reviewer is quota-limited.

## 11. Superpowers and Arena

Superpowers remains the process controller:

```text
brainstorming
-> written spec
-> implementation plan
-> isolated implementation branch/worktree
-> TDD
-> code review
-> verification
-> finish branch
```

Arena remains an additional review layer:

- Micro Arena for routine decisions;
- Review Arena for implementation/review;
- Full Arena when explicitly requested.

If the runtime does not expose genuine isolated subagents, Arena strategies are sequential review perspectives and must never be described as independent agents.

## 12. Failure Handling

The system fails closed on:

- missing GitLab write credential;
- source or target identity mismatch;
- invalid/unapproved branch class;
- force-push requirement;
- push to a tag;
- receipt digest mismatch;
- refresh-ref digest mismatch;
- GitLab pipeline not created by Git push;
- GitLab pipeline SHA different from the mirrored SHA;
- GitHub original ref moved before final evidence;
- GitLab original ref moved before final evidence;
- stale receipt;
- non-HEALTHY final parity;
- missing required evidence artifact;
- malformed provenance digest;
- attempts to use TinyFish or advisory AI as an authority source.

A failed mirror never triggers merge, rollback, deploy or force-push automatically.

## 13. Secret and Permission Model

Required secret footprint is one dedicated GitLab repository-write credential in GitHub Actions.

Security requirements:

- least privilege;
- mirror project only;
- Git repository write scope only when supported;
- rotate/revoke independently from human credentials;
- do not reuse personal login credentials;
- redact secret-bearing command output;
- ephemeral credential helper files with restrictive permissions;
- cleanup in an always-run step;
- artifacts are secret-free;
- no credential material in GitLab CI inputs.

## 14. Files Expected in Implementation

The implementation plan is expected to touch a bounded set such as:

```text
.github/workflows/gitlab-neutral-mirror.yml
plugins/whitechronos-control-plane/scripts/sync_gitlab_mirror.py
plugins/whitechronos-control-plane/tests/test_gitlab_mirror_sync.py
tests/test_gitlab_pipeline_contract.py
docs/runbooks/gitlab-contingency-ci.md
docs/runbooks/whitechronos-connections.md
```

Additional files may be required by tests or governance, but the implementation must not introduce a second competing mirror engine.

## 15. TDD Acceptance Matrix

The implementation plan must include RED->GREEN tests for at least:

1. missing GitLab secret fails before Git push;
2. credential value never appears in generated command arguments;
3. credential helper is ephemeral and cleaned up;
4. normal branch push carries all required `ci.input` values;
5. same-SHA refresh creates the deterministic reserved ref;
6. refresh ref never becomes the parity subject;
7. push is non-force;
8. tag target is rejected;
9. source/target identities are canonical;
10. target after push equals the exact authoritative SHA;
11. pipeline selected for evidence has `source=push`;
12. pipeline SHA equals authoritative SHA;
13. tag pipeline is rejected;
14. receipt claim digest matches GitLab input;
15. final parity re-observes both original provider refs;
16. moved source ref blocks evidence;
17. moved target ref blocks evidence;
18. stale receipt blocks evidence;
19. final parity must be `HEALTHY`;
20. required artifacts have provenance digests;
21. no credential appears in artifacts/log-normalization fixtures;
22. TinyFish is not needed for a successful mirror;
23. GitHub AI reviewer unavailability is non-blocking to source correctness;
24. existing PR #76 regression/governance suites remain green.

## 16. Rollout

Rollout order:

1. user approves this written specification;
2. Superpowers `writing-plans` creates the implementation plan;
3. user reviews the plan and selects execution method;
4. create isolated implementation branch/worktree from the authoritative baseline chosen at execution time;
5. RED tests;
6. GREEN implementation;
7. full regression/governance;
8. Superpowers review;
9. Arena review;
10. GitHub PR CI;
11. user or authorized administrator provisions the dedicated GitLab `write_repository` credential in GitHub Actions;
12. execute neutral mirror for exact PR head;
13. verify GitLab push pipeline and final artifacts;
14. prove exact SHA parity;
15. record `MIRROR_PARITY=HEALTHY`;
16. STOP at the explicit merge gate.

## 17. Non-Goals

This design does not authorize:

- merge into `main`;
- deploy;
- canary;
- stable promotion;
- live smoke;
- R2/R3;
- `PRODUCTION COMPLETE`;
- automatic credential creation;
- storing credentials in repository files;
- making GitLab authoritative;
- using TinyFish as credential broker;
- using GitHub AI as an availability-critical runtime dependency.

## 18. Acceptance Criteria

This architecture is complete when all of the following can be demonstrated for one exact subject SHA:

```text
GITHUB_AUTHORITY=PASS
GITHUB_CI=PASS
SUPERPOWERS_REVIEW=PASS
ARENA=PASS

NEUTRAL_WORKER=PASS
GITLAB_PUSH_SOURCE=PASS
GITLAB_TAG=false

GITHUB_SHA=<subject>
GITLAB_MIRROR_SHA=<subject>
GITLAB_PIPELINE_SHA=<subject>

RECEIPT_VALID=YES
FINAL_PARITY=HEALTHY
EVIDENCE_ELIGIBLE=true
MIRROR_PARITY=HEALTHY
```

and:

```text
MERGE_AUTHORIZED=NO
DEPLOY_AUTHORIZED=NO
PRODUCTION_COMPLETE=NO
```

until those later gates receive separate explicit authorization.

## 19. Design Decision

Selected:

**GitHub Actions neutral worker + least-privilege GitLab `write_repository` credential + GitLab push-only evidence plane + TinyFish observer + GitHub AI advisory.**

Rejected:

- GitLab `CI_JOB_TOKEN` as the final neutral mirror transport, because the final design requires a real push-triggered evidence pipeline;
- GitLab API/file-commit mirroring, because it does not preserve the authoritative Git commit SHA as the same commit object;
- TinyFish browser automation as mirror authority;
- direct default-branch edits;
- automatic merge/deploy as part of mirror success.

This keeps GitHub authoritative, makes GitLab evidence independently useful, minimizes credential scope, and preserves every existing review and production gate.
