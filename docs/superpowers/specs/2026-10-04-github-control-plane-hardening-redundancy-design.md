# GitHub Control Plane Hardening + Redundancy Design

**Status:** Approved architecture captured for written review  
**Date:** 2026-10-04  
**Repository:** `WhiteChronos/ChatGPT`  
**Working branch:** `feat/cloud-runtime-foundation`  
**Draft PR:** `#57`  
**Parent architecture:** `docs/superpowers/specs/2026-10-04-whitechronos-cloud-control-plane-design.md`

## 1. Decision summary

WhiteChronos SHALL use **GitHub as the single authoritative Control Plane and Source of Truth**.

The runtime chain is:

```text
change
-> isolated feature branch
-> pull request
-> path ownership / policy checks
-> security + governance gates
-> required status checks
-> approved GitHub Environment boundary
-> Codex Cloud executor
-> Cloud preflight
-> Runtime Doctor
-> verified host discovery
-> Subagent Broker when selected by routing policy
-> LIVE_SMOKE_READY=YES
-> real live smoke
-> redacted evidence / artifacts bound to commit SHA
-> GitHub history / release evidence
-> one-way external cold mirror
```

The external mirror is **disaster-recovery only**. It is never an authority, never writes back, never approves changes, never owns runtime configuration, and never receives the GitHub repository's general secret set.

## 2. Current verified state

The following state is verified from GitHub at the time of this design:

- Pull request `#57` is open and draft, from `feat/cloud-runtime-foundation` to `spec/whitechronos-cloud-control-plane`.
- The PR head is currently `82379a0c289fbe8acef625121db7266114bb9324`.
- The repository ruleset `Chronos` exists but its enforcement is `disabled`.
- `Chronos` currently contains rules for deletion, non-fast-forward updates, creation, update, required linear history, required signatures, and required deployments.
- The current `Chronos` ref conditions have empty include/exclude lists.
- The current required-deployments rule has no required deployment environments configured.
- The current `.github/CODEOWNERS` covers:
  - `/datacenter/`
  - `/datasheet/`
  - `/schemas/`
  - `/governance/`
  - `/pipeline/`
  - `/tests/`
  - `/.github/workflows/`
  - `/mkdocs.yml`
  - `/docs/`
- The current CODEOWNERS file does not explicitly cover `/memory/`, `/history/`, `/registry/`, `/plugins/`, `/.codex/`, or `/.agents/`.
- The current ChatGPT GitHub integration can read rulesets but does not have repository-administration permission to read all branch-protection details or to mutate repository-admin settings.

The implementation SHALL therefore not claim hardening is active merely because policy files or a disabled ruleset exist.

## 3. Problem statement

The objective is not simply to run Codex Cloud from a repository.

The objective is to ensure that:

1. GitHub is the sole authority for accepted source state, governance state, runtime evidence, release state, and disaster-recovery provenance.
2. Codex Cloud, GitHub Actions, Runtime Doctor, Subagent Broker, human operators, and future integrations cannot silently bypass that authority.
3. critical directories have explicit ownership and path-aware validation;
4. repository settings and workflow gates fail closed rather than relying on conventions;
5. redundancy improves recovery without introducing a second writable source of truth;
6. runtime claims remain bound to evidence, commit identity, and GitHub review history.

## 4. Architectural alternatives considered

### 4.1 GitHub-only redundancy

Use protected branches, releases, Actions artifacts, history records, tags, and repository snapshots only inside GitHub.

**Advantages**

- one provider;
- simple governance;
- no cross-provider credentials;
- zero risk of mirror write-back.

**Disadvantages**

- account, organization, repository, or provider-wide failure remains a common failure domain;
- a destructive administrative event can affect both working state and internal backups.

### 4.2 Active dual-control repositories

Operate GitHub and another Git provider as equal writable repositories.

**Advantages**

- high infrastructure redundancy.

**Rejected because**

- creates competing authorities;
- introduces conflict resolution and split-brain risk;
- weakens auditability;
- makes branch policy, secrets, workflow state, and approvals diverge;
- violates the requirement that GitHub remain the single Control Plane.

### 4.3 GitHub-authoritative + external cold mirror

GitHub owns all write authority and governance. A second provider receives one-way, non-pruning recovery copies.

**Selected.**

This model keeps one source of truth while covering provider/account/repository disaster scenarios.

## 5. Control-plane invariants

The following are non-negotiable:

1. **GitHub is authoritative.**
2. **Protected target branches are changed only through pull requests.**
3. **Codex Cloud is an executor, not an authority.**
4. **GitHub Actions is controlled automation, not an alternate source of truth.**
5. **Runtime Doctor is the authority for runtime evidence levels.**
6. **Subagent Broker remains subordinate to runtime routing and Doctor readiness.**
7. **No live smoke runs before `LIVE_SMOKE_READY=YES`.**
8. **The external mirror never writes back to GitHub.**
9. **The external mirror never receives general repository/runtime credentials.**
10. **No deletion/prune operation is automatically propagated to the cold mirror.**
11. **Repository config is never treated as runtime proof.**
12. **Manual Codex activity is not authoritative until its resulting code/evidence is bound to a GitHub commit/PR/check.**
13. **Raw Data Center sources are never silently overwritten.**
14. **Secrets never enter Git, durable memory, Data Center records, runtime evidence, or backup manifests.**
15. **A disabled ruleset is not a protection.**
16. **CODEOWNERS without an enforced PR policy is documentation, not sufficient protection.**

## 6. Branch topology and integration model

### 6.1 Protected targets

The intended protected-target classes are:

```text
main
spec/**
release/**
```

Feature/task branches remain usable for development:

```text
feat/**
fix/**
docs/**
subagent/**
chore/**
```

The implementation plan may refine names to match existing repository practice, but SHALL preserve the distinction between mutable work branches and protected integration targets.

### 6.2 Pull-request-only integration

For protected targets:

- direct updates are forbidden;
- force pushes are forbidden;
- branch deletion is forbidden except an explicitly authorized recovery operation;
- required checks must complete successfully;
- unresolved review conversations block merge;
- merge must preserve linear history or an explicitly approved equivalent;
- automation must not push directly to protected targets.

### 6.3 Solo and team review modes

The repository currently appears to be operated primarily by one owner. Therefore the hardening design must avoid a self-inflicted review deadlock.

Two modes are supported:

**Solo mode**

- PR is mandatory;
- code-owner paths are still classified;
- required status checks are mandatory;
- path-policy workflow is mandatory;
- review conversations must be resolved;
- no fake/self-approval requirement is introduced.

**Team mode**

When a second trusted human/team is configured:

- require at least one approving review;
- require CODEOWNER review for critical paths;
- dismiss stale approvals after material changes.

The system must not pretend that a single PR author can independently approve their own change.

## 7. Chronos ruleset redesign

The existing `Chronos` ruleset SHALL NOT simply be switched from disabled to active.

Before activation it must be redesigned and verified.

### 7.1 Explicit target conditions

The ruleset SHALL explicitly target the intended protected refs.

Empty targeting conditions must not be relied on as an implicit policy.

### 7.2 Required rules

For protected targets, the intended policy is:

- pull request required before merge;
- required status checks;
- block force pushes / non-fast-forward updates;
- block deletion;
- require linear history;
- require conversation resolution;
- optional required review rules according to solo/team mode;
- signed-commit enforcement only after the repository's actual GitHub/Codex/automation write path has verified signature support.

### 7.3 Signature rollout

The current ruleset already contains a required-signatures rule, while recent connector-created commits are unsigned.

Therefore signature enforcement must be phased:

1. verify how GitHub web merges, Codex-created branches, bots, and permitted automation produce signatures;
2. make signing support operational;
3. test on a non-critical protected canary branch;
4. only then enforce signatures on production integration targets.

No ruleset may be activated in a way that locks the repository out of legitimate recovery or integration paths.

### 7.4 Break-glass

Routine bypass actors are not permitted.

An emergency bypass, if the GitHub account/plan supports it, must be:

- owner/admin controlled;
- disabled from normal workflows;
- accompanied by an incident record;
- followed by post-event review and restoration of the normal gate.

## 8. Directory and path control

### 8.1 Critical-path classes

The following areas are control-plane critical:

```text
/.github/workflows/
/.github/CODEOWNERS
/governance/
/pipeline/
/schemas/
/datacenter/
/datasheet/
/memory/
/history/
/registry/
/plugins/whitechronos-control-plane/
/plugins/subagent-broker/
/.codex/
/.agents/
AGENTS.md
```

Additional critical paths may be added, but not removed without architecture review.

### 8.2 CODEOWNERS

CODEOWNERS SHALL explicitly cover every critical path.

CODEOWNERS is one layer only. It becomes enforceable protection only when paired with PR/ruleset behavior and required checks.

### 8.3 Path-policy check

A dedicated required workflow SHALL inspect changed paths and classify the PR.

Examples:

- workflow/governance/rules changes -> highest-risk gate;
- memory/history changes -> provenance + schema/content gate;
- Data Center changes -> raw-source immutability + provenance gate;
- runtime/plugin changes -> Runtime Foundation + security gate;
- docs-only changes -> reduced but still deterministic checks.

The path-policy job must emit a machine-readable classification artifact.

## 9. GitHub Actions hardening

### 9.1 Default permissions

Repository workflows SHALL default to least privilege:

```yaml
permissions:
  contents: read
```

Any additional permission is granted per job and justified.

### 9.2 No protected-target writes

Workflows SHALL not push directly to protected targets.

Write automation uses one of:

- a generated branch + PR;
- a GitHub-native release/tag operation approved by policy;
- a specifically scoped recovery workflow.

### 9.3 Workflow supply chain

Sensitive workflows SHALL:

- pin third-party actions to reviewed immutable commit SHAs where practical;
- use bounded timeouts;
- use concurrency controls where duplicate execution is unsafe;
- avoid `pull_request_target` with untrusted checked-out code and secrets;
- avoid environment dumps;
- avoid broad repository tokens;
- run dependency integrity checks.

### 9.4 Security gates

The hardening plan SHALL include:

- secret scanning / push protection where available;
- dependency review or equivalent lockfile diff checks;
- static security analysis appropriate to Python/Node code;
- policy checks preventing literal credential assignment in workflows;
- validation that external Actions are pinned or explicitly allowlisted.

Availability of GitHub-hosted security features must be verified against the repository/account before claiming they are enabled.

## 10. GitHub Environments

Separate GitHub Environments SHALL be used for high-risk automation.

Proposed logical environments:

```text
codex-cloud-execution
codex-live-smoke
disaster-recovery-mirror
```

### 10.1 codex-cloud-execution

Used only for workflows/actions that need execution-scoped integration data.

It must not expose unrelated secrets.

### 10.2 codex-live-smoke

Used only for the transition from runtime readiness to real live smoke.

A live-smoke operation requires:

- current commit SHA;
- green required checks;
- Cloud preflight ready;
- Runtime Doctor evidence for that same runtime/session;
- `LIVE_SMOKE_READY=YES`;
- explicit environment authorization where GitHub's environment model supports it.

### 10.3 disaster-recovery-mirror

Contains only the credential needed to write to the external backup destination.

That credential:

- cannot write back to GitHub;
- cannot administer the backup provider;
- cannot access unrelated repositories;
- is unavailable to normal PR workflows.

## 11. Codex Cloud authority boundary

Codex Cloud may:

- clone/use authorized repositories;
- run tests;
- create isolated branches;
- propose PRs;
- run Cloud preflight;
- run Runtime Doctor when the environment exposes the necessary host inventory;
- run Broker live smoke only after the GitHub/Doctor gates permit it.

Codex Cloud may not:

- directly update protected integration branches;
- redefine accepted GitHub policy;
- treat local task state as durable project memory;
- bypass PR/status-check requirements;
- claim live verification without evidence bound to GitHub state.

A manually started Codex task may execute useful work, but its output is not accepted as authoritative until GitHub records the relevant branch/commit/PR/check/evidence.

## 12. Runtime evidence chain

Every authoritative runtime-verification record SHALL bind at least:

```json
{
  "repository": "WhiteChronos/ChatGPT",
  "commit_sha": "...",
  "pull_request": 57,
  "cloud_environment": "...",
  "runtime_doctor": {
    "configured": "...",
    "local_runtime_healthy": "...",
    "host_discovered": "...",
    "live_verified": "..."
  },
  "routing": "NATIVE|BROKER|INLINE",
  "live_smoke_ready": false,
  "artifact_hashes": {},
  "redaction_version": "...",
  "workflow_or_session_evidence": "..."
}
```

Secrets and raw sensitive traces are excluded.

The evidence record must not upgrade a state that Runtime Doctor did not prove.

## 13. Memory, Data Center, history, and datasheets

### 13.1 memory/

`memory/` stores concise durable current-state knowledge.

Changes require PR and path-policy validation.

### 13.2 history/

`history/` is append-oriented evidence and resume history.

Rewriting old history records is forbidden except a separately reviewed correction record that preserves the prior fact.

### 13.3 datacenter/

Raw Data Center evidence is immutable by policy.

A new revision is stored as a new object/revision with provenance rather than overwriting the original.

### 13.4 datasheet/

Datasheets are machine-readable current state and must remain reproducible from authoritative evidence.

### 13.5 registry/

Registry records define integration identity, provenance, permissions, activation state, and runtime evidence level.

A registry entry cannot self-declare `HOST_DISCOVERED` or `LIVE_VERIFIED`.

## 14. Internal GitHub redundancy

GitHub-internal recovery layers SHALL include:

- protected integration branches;
- immutable/reviewed release tags where appropriate;
- release artifacts for major verified runtime milestones;
- workflow artifacts for bounded CI evidence;
- repository-backed history/resume records;
- reproducible manifests containing commit/ref hashes;
- periodic recovery checks.

These mechanisms improve local recovery but do not replace the external cold mirror.

## 15. External cold mirror

### 15.1 Authority

The cold mirror is a one-way recovery target.

It has no:

- write-back workflow;
- inbound synchronization to GitHub;
- merge authority;
- GitHub-status authority;
- runtime authority;
- normal CI authority.

### 15.2 Provider independence

The architecture is provider-neutral.

The implementation must use a provider distinct from GitHub that supports a private Git destination and restricted credentials. The provider choice is operational configuration, not a second control plane.

### 15.3 Non-pruning replication

Automatic backup SHALL NOT use destructive pruning semantics.

In particular, the normal backup path must not automatically propagate source deletions or force-rewrites into the recovery history.

The backup design shall preserve timestamped recovery refs/snapshots so a destructive source event does not immediately destroy the backup copy.

### 15.4 Snapshot model

At backup time, capture:

- source repository identity;
- timestamp;
- source default branch SHA;
- all relevant branch/tag refs;
- repository object integrity result;
- backup destination refs;
- SHA-256 manifest of the backup metadata.

Recommended logical backup namespace:

```text
refs/backup/YYYY/MM/DD/<source-ref>
```

or an equivalent immutable provider-supported scheme.

### 15.5 Backup freshness

Normal development merges are not blocked solely by a temporary external-mirror outage.

However, high-risk release/live-runtime milestones SHALL require an acceptable recent backup state.

Initial target:

- latest successful cold-mirror snapshot no older than 24 hours for release/live-smoke authorization.

The implementation plan may adjust this threshold only with explicit rationale.

### 15.6 Restore drill

At least periodically, the recovery workflow SHALL:

1. fetch only from the external recovery target into a clean workspace;
2. run `git fsck --full` or equivalent integrity validation;
3. verify expected refs/hashes;
4. check out a known protected target snapshot;
5. run a bounded repository validation suite;
6. produce a restore evidence artifact in GitHub.

The restore drill does not make the external provider authoritative.

## 16. Redundancy without split brain

The system SHALL enforce this directionality:

```text
GitHub authoritative state
        |
        +--> Codex Cloud execution
        |
        +--> GitHub Actions validation
        |
        +--> releases / artifacts / history
        |
        '--> external cold mirror

external cold mirror --X--> GitHub automatic write-back
```

Recovery from the mirror is always a deliberate incident/recovery operation into a new or explicitly authorized repository state.

## 17. Required checks model

Before protected-target merge, the repository shall require the applicable check set.

Logical checks include:

```text
github-control-plane-policy
whitechronos-cloud-runtime-foundation
whitechronos-runtime-foundation
engineering-governance
security-policy
dependency-integrity
path-ownership-policy
```

The implementation SHALL discover the exact GitHub check-context names produced by the workflows before configuring required-status rules.

A ruleset must never require a status context that the target PR cannot actually produce.

## 18. Release/live-smoke gate

A real live smoke is permitted only when all are true:

1. source commit is in a PR or approved protected state;
2. GitHub policy checks are green;
3. critical path policy is green;
4. security/governance checks are green;
5. external cold-mirror freshness is within policy;
6. Codex Cloud preflight is ready;
7. Runtime Doctor has run against the intended runtime;
8. actual host discovery is proven;
9. routing selects Broker when Broker is the required path;
10. `LIVE_SMOKE_READY=YES`;
11. required GitHub Environment authorization is satisfied.

Only after smoke completes successfully may the evidence be promoted to `LIVE_VERIFIED`.

## 19. Failure behavior

### 19.1 GitHub policy failure

Stop before runtime execution or merge.

### 19.2 Ruleset configuration uncertainty

Do not enable enforcement blindly. Validate on a canary branch/ref first.

### 19.3 GitHub Environment unavailable

Do not move the secret to repository files. Stop and report the administrative/configuration gap.

### 19.4 External mirror unavailable

Normal low-risk development may continue if repository policy allows it.

Release/live-smoke promotion blocks when backup freshness exceeds policy.

### 19.5 Codex host stale

If Runtime Doctor returns `HOST_RELOAD_REQUIRED`, create a fresh Codex Cloud task/session. Do not change source merely to make stale host discovery pass.

### 19.6 Broker unavailable

Use the existing routing order:

```text
native verified runtime
-> Broker verified runtime
-> official Superpowers inline fallback
```

Do not claim independent subagents when Broker/native lifecycle tools are absent.

## 20. Administrative boundary

Some required controls are repository-administration settings rather than source files:

- ruleset enforcement and targeting;
- branch-protection/ruleset required checks;
- GitHub Environment creation/protection;
- repository security settings;
- secret-scanning/push-protection settings;
- environment secrets.

The current ChatGPT GitHub integration does not have sufficient repository-admin permission to mutate all of these settings.

Therefore implementation SHALL distinguish:

```text
code/config changes that can be implemented through PR
vs.
admin changes that require the repository owner or an explicitly authorized admin integration
```

No source-code workaround may weaken the intended control merely because the current connector lacks admin scope.

## 21. Pull request #57 policy

PR `#57` remains draft while this hardening architecture is being specified and planned.

It SHALL NOT be merged merely because its existing tests are green.

Before it can become merge-ready:

- this written spec must be reviewed and approved;
- an implementation plan must be written;
- required hardening changes must be implemented through PR-controlled work;
- administrative GitHub controls must be verified;
- the resulting required checks must be green;
- GitHub-first authority must be demonstrably fail-closed.

## 22. Acceptance criteria

The GitHub Control Plane Hardening + Redundancy architecture is complete when all of the following are verified:

1. GitHub remains the only accepted writable source of truth.
2. `Chronos` or successor rulesets are actively enforced on explicitly targeted protected refs.
3. Feature/task branches remain usable; protected targets reject direct mutation.
4. Required PR/status-check behavior is demonstrably active.
5. CODEOWNERS explicitly covers all critical control-plane paths.
6. A required path-policy workflow classifies sensitive changes.
7. Solo mode does not deadlock the owner; team mode supports independent code-owner approval.
8. Workflow permissions are least-privilege.
9. Sensitive Actions are pinned/allowlisted according to policy.
10. GitHub security features are enabled where verified available, with source-controlled fallback checks where needed.
11. Separate execution/live-smoke/backup environment boundaries exist or an equivalently strong verified mechanism is documented.
12. Runtime evidence is bound to commit SHA and cannot self-upgrade its proof level.
13. Manual Codex output cannot bypass protected-target PR gates.
14. Live smoke cannot run before the required GitHub and Runtime Doctor gates.
15. `memory/`, `history/`, `datacenter/`, `datasheet/`, and `registry/` have explicit path policies.
16. External cold mirror is one-way and cannot write back automatically.
17. Backup replication does not automatically prune deleted source state.
18. A recent backup freshness record exists before release/live-smoke promotion.
19. A restore drill from the external mirror succeeds in a clean workspace.
20. A destructive or unavailable mirror event cannot corrupt GitHub state.
21. PR `#57` remains draft until the hardening implementation and administrative verification gates are satisfied.

## 23. Review Arena conclusions

Four sequential review perspectives were used because this ChatGPT host does not expose verified independent subagent lifecycle tools.

### Perspective A — systems thinking / build-then-break / completeness

Primary conclusion:

- separate authority, execution, evidence, and recovery;
- keep GitHub authoritative;
- make backup directionality explicit;
- do not let mirror availability become an unnecessary dependency for ordinary development.

### Perspective B — constraint-first / requirements checklist / explicit trade-offs

Primary conclusion:

- path ownership alone is insufficient;
- rulesets, required checks, workflow permissions, environment boundaries, and CODEOWNERS must work together;
- administrative settings must be treated as explicit deployment work, not assumed from source files.

### Perspective C — working backwards / iterative deepening / explicit trade-offs

Primary conclusion:

Design backward from the final proof:

```text
LIVE_VERIFIED
requires real smoke
requires LIVE_SMOKE_READY
requires Runtime Doctor + host discovery
requires Cloud readiness
requires GitHub policy approval
requires protected commit/PR identity
```

Every layer must be independently auditable.

### Perspective D — evidence-first / test-first / edge-cases-first

Primary conclusion:

- do not enable the current disabled `Chronos` ruleset blindly;
- do not require signatures until legitimate automation signing is proven;
- do not require code-owner approval in a way that deadlocks a single-owner repository;
- do not use destructive mirror pruning;
- do not claim GitHub admin controls are active until GitHub itself proves them.

## 24. Implementation decomposition

This architecture should be implemented in separate planned slices:

1. **GitHub Rulesets + Protected Targets**
2. **Critical Path Ownership + Path Policy**
3. **Workflow Security + Required Checks**
4. **GitHub Environments + Runtime Authorization**
5. **Memory/Data Center/History Governance**
6. **External Cold Mirror + Restore Drill**
7. **Runtime Doctor GitHub Evidence Handoff**
8. **Subagent Broker Live-Smoke Gate**
9. **PR #57 Final Integration Readiness**

Each slice receives its own tests, review, CI evidence, and rollback path.

## 25. Implementation boundary

This document approves architecture only.

It does not itself authorize:

- activating or editing GitHub rulesets;
- modifying branch protection;
- changing repository security settings;
- creating or updating GitHub Environment secrets;
- creating an external backup-provider account;
- storing backup-provider credentials;
- running a real Codex Cloud live task;
- running the Broker real smoke;
- marking PR `#57` ready for review;
- merging PR `#57`.

After this written spec is reviewed and approved by the user, the next mandatory Superpowers step is `writing-plans`.
