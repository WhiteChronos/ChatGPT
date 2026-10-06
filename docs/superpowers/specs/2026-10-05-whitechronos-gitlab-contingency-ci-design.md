# WhiteChronos GitLab Mirror + Contingency CI Design

**Status:** Proposed written specification for user review  
**Date:** 2026-10-05  
**Architecture class:** ADDITIVE_EXTENSION  
**Core baseline:** WhiteChronos v1.0 sealed baseline `2f6fd7a785999ef7827e74f35167a452c98d7920`  
**Extension-plane baseline:** `c5321b17a69148e4f48c1fe3eefd84dfde112a1c`  
**Primary authority:** GitHub  
**Contingency provider:** GitLab  

## 1. Authorization record

The user selected the following architecture on 2026-10-05:

> GitLab as mirror + contingency CI. GitHub remains the authority. GitLab replicates the SHA and executes a secondary CI suite. GitLab results are additional evidence and do not grant merge or deploy authority. Future active failover may be designed separately.

This approval authorizes writing this specification only under the Superpowers architectural workflow.

It does **not** authorize:

- creation of the GitLab project;
- credential creation or exchange;
- repository mirroring activation;
- GitLab pipeline activation;
- merge of this specification;
- merge of any other PR;
- deploy;
- canary;
- stable promotion;
- live smoke;
- R2/R3 execution;
- `PRODUCTION COMPLETE`.

## 2. Decision summary

WhiteChronos SHALL add a non-authoritative GitLab redundancy plane.

The governing rule is:

> **GitHub remains the source-controlled authority; GitLab provides replica continuity and independent CI evidence.**

The redundancy rule is:

> **Provider redundancy must not create authority redundancy.**

The evidence rule remains:

```text
VERIFIED != AUTHORIZED
AUTHORIZED != EXECUTED
EXECUTED != SUCCESSFUL
```

The release-authority rule remains:

```text
CI SUCCESS != MERGE AUTHORIZED
MERGE      != DEPLOY AUTHORIZED
DEPLOY     != CANARY AUTHORIZED
CANARY     != STABLE AUTHORIZED
STABLE     != PRODUCTION COMPLETE
```

## 3. Goals

This design SHALL:

1. reduce operational dependence on GitHub-hosted Actions runners;
2. preserve GitHub as the authoritative repository and governance surface;
3. maintain an exact GitLab replica of eligible Git refs;
4. allow GitLab CI to execute validation against the exact same immutable commit SHA;
5. record GitLab CI results as additional technical evidence;
6. detect and fail closed on mirror divergence;
7. avoid duplicated test logic between GitHub Actions and GitLab CI;
8. preserve all existing WhiteChronos authorization gates;
9. prepare a clean path for a future separately authorized active-failover architecture;
10. keep the Sealed Core v1.0 unchanged.

## 4. Non-goals

This design does not:

- replace GitHub with GitLab;
- make GitLab a second source of truth;
- permit direct authoritative development in GitLab;
- allow GitLab CI to satisfy a GitHub required check automatically;
- authorize GitLab to merge GitHub pull requests;
- authorize GitLab to deploy WhiteChronos;
- make GitLab evidence sufficient for `PRODUCTION COMPLETE`;
- weaken fail-closed semantics;
- move secrets into GitHub or GitLab repository contents;
- activate future failover mode;
- alter the frozen Core baseline.

## 5. Architecture classification

This integration is classified as:

```text
ADDITIVE_EXTENSION
```

It adds a repository/CI provider capability without changing frozen Core semantics.

If any future implementation requires GitLab to become an alternative authoritative merge source, substitute a required GitHub gate, or reinterpret WhiteChronos authority semantics, that change SHALL be treated as a new architecture decision and SHALL NOT be smuggled into this v1 design.

## 6. Current observed precondition

At specification time, no visible WhiteChronos/ChatGPT GitLab project exists in the connected GitLab account.

Therefore implementation begins from:

```text
gitlab_mirror_project = ABSENT
gitlab_ci             = NOT_CONFIGURED
gitlab_authority      = NONE
```

The absence of the mirror does not affect the existing GitHub authority model.

## 7. Logical topology

```text
                         +----------------------+
                         |  WhiteChronos Core   |
                         |  Sealed v1.0         |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |  GitHub Authority    |
                         |  Repo / PR / Rules   |
                         +----------+-----------+
                                    |
                         immutable refs / SHAs
                                    |
                    +---------------+----------------+
                    |                                |
                    v                                v
        +----------------------+         +----------------------+
        | GitHub Actions       |         | GitLab Mirror        |
        | Primary CI evidence  |         | Non-authoritative    |
        +----------+-----------+         +----------+-----------+
                   |                                |
                   |                                v
                   |                     +----------------------+
                   |                     | GitLab CI            |
                   |                     | Contingency evidence |
                   |                     +----------+-----------+
                   |                                |
                   +---------------+----------------+
                                   |
                                   v
                         +----------------------+
                         | Evidence / Ledger    |
                         | exact SHA required   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Authorization Gate   |
                         +----------------------+
```

GitLab SHALL remain downstream of GitHub authority.

## 8. Source-of-truth rules

The following rules are mandatory:

1. GitHub is the authoritative repository for WhiteChronos v1.x.
2. GitHub pull requests remain the authoritative review and merge surface.
3. GitHub branch/ruleset governance remains authoritative.
4. GitLab is a replica and CI provider only.
5. GitLab SHALL NOT push authoritative changes back to GitHub in this architecture.
6. A GitLab merge request SHALL NOT constitute WhiteChronos merge authority.
7. A GitLab branch name SHALL NOT override a GitHub ref identity.
8. An exact Git commit SHA is the cross-provider artifact identity.
9. If provider refs disagree, the system SHALL classify the mirror as diverged.
10. Diverged GitLab results SHALL NOT be accepted as evidence for the affected GitHub SHA.

## 9. Immutable identity rule

Cross-provider evidence is valid only when all of the following match:

```text
github_commit_sha == gitlab_commit_sha
repository_identity == expected_whitechronos_repository
pipeline_subject_sha == expected_commit_sha
ci_config_revision == declared_config_revision
```

Branch names alone are insufficient.

Tag names alone are insufficient.

Human-readable commit messages are insufficient.

The exact immutable Git object identity is required.

## 10. Mirror synchronization model

The mirror SHALL be one-way:

```text
GitHub -> GitLab
```

The implementation SHALL prefer a synchronization transport that does not depend on GitHub Actions availability.

Acceptable implementation classes include:

1. GitLab-native pull mirroring where supported;
2. an independent neutral synchronization worker;
3. an independently hosted trusted runner/service that reads GitHub and writes the exact refs to GitLab.

A GitHub Actions-only mirror job MAY exist as convenience automation but SHALL NOT be the sole contingency path because that would couple redundancy to the failed subsystem.

## 11. Mirror scope

Only policy-approved refs SHALL be mirrored.

The implementation plan SHALL define an explicit allowlist for at least:

- `main`;
- approved specification branches;
- approved feature/fix branches under WhiteChronos policy;
- release refs when such refs become authorized.

Unknown refs SHALL NOT become authoritative merely because they appear in GitLab.

The mirror transport SHALL preserve commit identity and SHALL NOT rewrite commits.

## 12. Drift and split-brain detection

The system SHALL detect at minimum:

- GitHub ref missing in GitLab;
- GitLab ref missing in GitHub;
- same ref name with different SHA;
- unexpected GitLab-only commit on a protected mirrored ref;
- force-pushed mirror history;
- pipeline result attached to the wrong SHA;
- stale mirror beyond the allowed freshness window.

The required fail-closed state is:

```text
MIRROR_DIVERGED
 -> GitLab evidence ineligible
 -> GitHub authority unchanged
 -> no automatic reconciliation by choosing a side
```

Reconciliation SHALL explicitly restore GitLab to the expected GitHub identity.

## 13. CI architecture

GitHub Actions and GitLab CI SHOULD be thin orchestrators over shared repository-owned validation commands.

The preferred shape is:

```text
canonical test/gate scripts
        |
        +--> GitHub Actions
        |
        +--> GitLab CI
```

This prevents two providers from silently testing different systems.

Provider YAML SHALL describe scheduling, runner setup, environment preparation, and artifact publication.

Business validation and governance logic SHOULD live in reusable repository scripts/modules.

## 14. Required CI equivalence

The GitLab pipeline SHALL execute the applicable canonical validation commands for the mirrored SHA.

At minimum, contingency coverage SHALL include the security/governance checks required for the affected change class.

The implementation plan SHALL define a provider-neutral CI contract that maps:

- canonical gate name;
- command;
- expected inputs;
- allowed environment;
- artifacts/evidence produced;
- timeout;
- deterministic exit semantics.

A provider-specific green badge SHALL NOT substitute for command-level equivalence.

## 15. Evidence semantics

WhiteChronos SHALL distinguish provider evidence explicitly.

Example evidence classes:

```text
GITHUB_PRIMARY_CI
GITLAB_CONTINGENCY_CI
LOCAL_VERIFICATION
```

Every CI evidence record SHALL include at minimum:

- provider;
- repository/project identity;
- exact commit SHA;
- pipeline/run identifier;
- job/gate name;
- result;
- timestamp;
- CI configuration revision;
- runner/environment identity where available;
- evidence artifact references;
- whether the mirror parity check passed.

GitLab success means:

```text
technical_evidence.gitlab = AVAILABLE
```

It does not mean:

```text
merge_authority  = GRANTED
deploy_authority = GRANTED
```

## 16. Normal operating mode

Under normal conditions:

```text
GitHub commit
 -> mirror parity check
 -> GitHub CI
 -> GitLab CI
 -> evidence comparison
 -> ordinary authorization gates
```

GitLab CI MAY run continuously or on an explicitly defined policy schedule.

A GitLab result is additive evidence.

GitHub required checks remain required unless a future architecture explicitly changes that rule.

## 17. GitHub Actions degradation mode

When GitHub Actions is degraded but GitHub repository authority remains reachable:

```text
GitHub remains source of truth
 -> exact SHA mirrors to GitLab
 -> GitLab CI validates exact SHA
 -> GitLab evidence becomes available
 -> development can continue with additional confidence
 -> GitHub merge remains subject to existing GitHub gates
```

This architecture reduces engineering downtime but does not bypass GitHub governance.

## 18. Complete GitHub outage mode

If GitHub itself is unreachable:

1. GitLab MAY validate only an already mirrored exact SHA.
2. GitLab SHALL NOT manufacture a new authoritative WhiteChronos history.
3. GitLab SHALL NOT grant merge/deploy authority.
4. Any work performed outside GitHub authority is non-authoritative until reconciled through a separately authorized procedure.
5. WhiteChronos SHALL remain fail closed for authority-sensitive operations.

This is intentionally more conservative than future active failover.

## 19. Future active failover boundary

The user selected this design with an explicit future path toward active failover.

That future path is **not active in this specification**.

A future active-failover design SHALL require a separate written specification and authorization before GitLab can substitute for a normally required GitHub technical gate.

At minimum, future failover SHALL require:

- explicit outage trigger conditions;
- exact subject SHA;
- failover authorization receipt;
- bounded validity period;
- anti-split-brain controls;
- no authority broadening;
- recovery/reconciliation procedure;
- post-recovery verification;
- auditable declaration of which gate, if any, was temporarily substituted.

## 20. Security model

The GitLab integration SHALL use least privilege.

Mandatory requirements:

1. Mirror credentials SHALL be capability-scoped.
2. Raw credentials SHALL NOT be committed to either repository.
3. Tokens SHALL be stored only in provider secret stores or an approved external secret store.
4. GitLab CI SHALL NOT receive deployment credentials merely because it can run tests.
5. Untrusted code SHALL NOT receive privileged mirror credentials.
6. Credentials SHALL be rotatable and revocable.
7. GitLab SHALL have no write-back credential to authoritative GitHub branches in this architecture.
8. Secret material SHALL NOT be persisted in CI artifacts or evidence ledgers.
9. Pipeline logs SHALL redact secret values.
10. Unknown credential state SHALL fail closed.

## 21. Public-repository safety

Because WhiteChronos/ChatGPT is public, contingency CI SHALL treat untrusted contributions as hostile input.

The design SHALL avoid exposing privileged credentials to:

- fork pipelines;
- untrusted merge-request code;
- arbitrary branch code;
- user-controlled scripts executed with privileged context.

Mirror credentials and any future control-plane credentials SHALL be isolated from untrusted jobs.

## 22. Availability model

The redundancy target is provider diversity, not merely runner diversity.

The desired dependency model is:

```text
GitHub repository/control plane
        |
        +--> GitHub-hosted CI path
        |
        +--> independent GitLab CI path
```

A failure of GitHub-hosted runner assignment SHOULD NOT prevent GitLab from validating an already mirrored SHA.

A failure of GitLab SHALL NOT invalidate GitHub authority or healthy GitHub CI evidence.

## 23. Result reconciliation

When both providers complete, WhiteChronos SHALL compare evidence.

Examples:

```text
GitHub PASS + GitLab PASS
 -> corroborated technical evidence

GitHub PASS + GitLab FAIL
 -> discrepancy requires investigation
 -> no claim of equivalent CI health

GitHub FAIL + GitLab PASS
 -> discrepancy requires investigation
 -> GitLab does not override GitHub failure

GitHub unavailable + GitLab PASS
 -> contingency technical evidence only
 -> no automatic merge authority

mirror mismatch
 -> GitLab evidence rejected
```

Provider disagreement SHALL never be resolved by selecting whichever result is more convenient.

## 24. Failure classification

CI failures SHOULD distinguish:

```text
CODE_FAILURE
POLICY_FAILURE
MIRROR_FAILURE
PROVIDER_INFRA_FAILURE
RUNNER_ASSIGNMENT_FAILURE
CONFIGURATION_FAILURE
UNKNOWN
```

`UNKNOWN` fails closed.

A runner cancellation before any job step may be classified as provider infrastructure failure only when evidence supports that diagnosis.

## 25. Recovery policy

Transient infrastructure failure MAY be retried under bounded policy.

Retry SHALL NOT:

- alter the tested SHA;
- mutate test expectations;
- skip required gates;
- convert a failure into success without a new execution;
- grant authority.

Retry evidence SHALL preserve attempt numbers and previous outcomes.

## 26. Required implementation controls

The implementation plan SHALL include, at minimum:

1. creation/configuration of the GitLab mirror project;
2. immutable cross-provider repository identity;
3. one-way mirror transport;
4. explicit mirrored-ref policy;
5. mirror parity checker;
6. divergence detection;
7. provider-neutral canonical CI command contract;
8. GitLab CI pipeline;
9. GitHub/GitLab evidence normalization;
10. provider disagreement detection;
11. bounded retry classification;
12. secret isolation;
13. untrusted-pipeline restrictions;
14. audit/evidence retention policy;
15. tests proving GitLab cannot grant merge/deploy authority;
16. documentation for outage/degraded operation;
17. future-active-failover boundary tests ensuring it remains disabled.

## 27. Acceptance criteria

This architecture is correctly implemented when all of the following are demonstrated:

- GitHub remains the sole authoritative repository;
- an eligible GitHub SHA is mirrored to GitLab without commit rewriting;
- GitLab verifies the exact same SHA;
- mirror parity is machine-checked before GitLab evidence is accepted;
- divergent mirror state makes GitLab evidence ineligible;
- canonical validation logic is shared rather than independently reimplemented;
- GitLab CI can execute while GitHub-hosted Actions runners are unavailable, provided the SHA is mirrored;
- a GitLab PASS cannot merge or deploy WhiteChronos;
- a GitLab FAIL cannot silently be ignored when GitHub passes;
- credentials are not present in repository content or ordinary evidence records;
- untrusted jobs cannot access privileged mirror credentials;
- removing the GitLab extension leaves GitHub authority intact;
- future active failover remains disabled;
- the Sealed Core v1.0 baseline remains unchanged.

## 28. Migration and adoption

Adoption SHALL be incremental.

Recommended sequence:

```text
Phase 1: mirror project + parity check
Phase 2: shared provider-neutral CI commands
Phase 3: GitLab contingency pipeline
Phase 4: evidence normalization + discrepancy handling
Phase 5: resilience drills for GitHub Actions degradation
```

Each phase SHALL preserve independent authorization gates.

No phase authorizes merge, deploy, canary, stable, live smoke, R2/R3, or production closure by implication.

## 29. Operational state model

After implementation, the desired state vocabulary is:

```text
github_authority      = AUTHORITATIVE
gitlab_mirror         = HEALTHY | STALE | DIVERGED | UNAVAILABLE
github_ci             = PASS | FAIL | INFRA_FAILURE | UNKNOWN
gitlab_ci             = PASS | FAIL | INFRA_FAILURE | UNKNOWN
technical_evidence    = PROVIDER_SCOPED
merge_authority       = INDEPENDENT_GATE
deploy_authority      = INDEPENDENT_GATE
active_failover       = DISABLED
```

No field SHALL be inferred from another without explicit evidence.

## 30. Governance preservation

The existing governance chain remains unchanged:

```text
Superpowers executes
 -> Arena challenges
 -> Verification validates
 -> Authorization Gate authorizes
 -> Executor acts
 -> Post-Verification confirms
```

This GitLab extension adds a second evidence-producing provider. It does not add a second Authorization Gate authority.

## 31. Core preservation

This design SHALL NOT modify the WhiteChronos v1.0 Sealed Core baseline:

```text
2f6fd7a785999ef7827e74f35167a452c98d7920
```

It is an Extension Plane capability layered on top of the frozen foundation.

Any implementation that requires a Core semantic change SHALL stop and reclassify that proposal.

## 32. Next gate

Per the Superpowers architectural workflow, this written specification requires user review before an implementation plan may be authored.

Approval of this written specification authorizes only the next planning step.

It still does not authorize:

- creation of the GitLab project;
- credential changes;
- mirror activation;
- CI activation;
- merge;
- deploy;
- canary;
- stable;
- live smoke;
- R2/R3;
- `PRODUCTION COMPLETE`.
