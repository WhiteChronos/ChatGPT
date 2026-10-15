# WhiteChronos Process Gate v1 Design

**Status:** Written specification awaiting human review  
**Date:** 2026-10-06  
**Repository:** `WhiteChronos/ChatGPT`  
**Base:** `main` at `8a3f175b92e6355dabd8ab11f19ba93a457de059`

## 1. Purpose

Define a repository-wide process gate that makes the approved WhiteChronos engineering workflow explicit, machine-checkable where possible, and fail-closed where evidence is missing.

The gate exists to ensure that WhiteChronos development work consistently uses:

1. the official Superpowers process as the primary development workflow;
2. GitHub Arena as the mandatory adversarial quality layer;
3. truthful evidence classes that distinguish policy, attestation, CI verification, host/runtime verification, and human authorization;
4. the existing GitHub control-plane required check as the enforcement point before merge.

The Process Gate must strengthen process discipline without pretending that CI can observe events that only occurred inside a live Codex or ChatGPT runtime.

## 2. Approved outcome

For WhiteChronos repository work, the canonical flow is:

```text
repository / system / user constraints
-> official Superpowers routing
-> applicable Superpowers workflow
-> specialized capability when justified
-> GitHub evidence / mutation
-> GitHub Arena review
-> process evidence
-> github-control-plane-policy
-> merge gate
```

For the existing GitLab contingency work, the preserved checkpoint remains:

```text
PR #73 Task 1
-> native implementer
-> TDD RED
-> GREEN
-> independent reviewer
-> exact-head lease / fast-forward into PR #72
-> Tasks 2-10
-> GitLab exact-SHA parity
-> GitLab CI
-> full regression
-> security review
-> Full Arena
-> separate merge gate
```

This specification does not authorize those implementation steps by itself.

## 3. Problem statement

The repository already contains strong normative rules in `AGENTS.md`:

- Micro Arena for every Codex task;
- Review Arena for high-impact work;
- Full Arena when explicitly requested;
- official Superpowers as the primary development process;
- real-subagent truthfulness requirements;
- Runtime Doctor separation between configuration and host discovery.

The gap is enforcement.

Today, many of these obligations are instructions rather than independently checkable merge criteria. The existing `github-control-plane-policy` check validates branch protection and repository-control rules, but it does not yet validate whether the process used to produce a change satisfied the required Superpowers and Arena obligations.

A second gap is evidence semantics. A PR body, comment, configuration file, CI job, runtime tool inventory, and explicit human approval do not all prove the same thing. Without a typed evidence model, a process can accidentally treat:

```text
declared
```

as equivalent to:

```text
runtime verified
```

which is specifically forbidden by the Runtime Doctor model.

A third gap is stale evidence. If process evidence applies to commit A and the branch later moves to commit B, that evidence must not remain valid automatically.

## 4. Design goals

The Process Gate SHALL:

1. require an Arena process check for every repository task that enters the controlled WhiteChronos workflow;
2. require Superpowers routing for every repository task and the applicable official Superpowers workflow for software-development work;
3. require Review Arena for code, architecture, CI/CD, security-sensitive configuration, repository governance, runtime-control changes, and public interfaces;
4. require Full Arena when explicitly requested by the user or by a more specific repository policy;
5. preserve Micro Arena as the default quality layer for all other tasks;
6. distinguish process policy from process evidence;
7. distinguish process attestation from CI verification;
8. distinguish CI verification from live runtime verification;
9. distinguish all technical evidence from explicit human authorization;
10. bind process evidence to an exact subject commit SHA;
11. invalidate stale evidence whenever the subject branch head changes;
12. fail closed when required evidence is missing, contradictory, stale, or over-claimed;
13. preserve the existing `github-control-plane-policy` required status check rather than creating a competing branch-governance authority;
14. never treat Arena strategy cards, prompt personas, same-context role play, or configuration flags as proof that independent subagents ran;
15. require real lifecycle evidence before accepting an independent-agent claim;
16. preserve the Runtime Doctor evidence hierarchy;
17. remain compatible with the existing Superpowers, Arena, ECC, Matt Pocock, Awesome LLM Apps, Subagent Broker, and engineering-governance layers;
18. avoid retroactively rewriting or invalidating the existing PR #72 / #73 checkpoint;
19. avoid requiring new paid infrastructure or secrets merely to enforce repository process;
20. make failure reasons deterministic and actionable.

## 5. Non-goals

The Process Gate SHALL NOT:

- claim that this repository can force unrelated ChatGPT conversations to load WhiteChronos Skills;
- claim that CI can prove `HOST_DISCOVERED` merely because repository configuration requests a tool;
- claim that an Arena strategy card is an independent subagent;
- require Full Arena for every routine task;
- force TDD, worktrees, code review, or implementation workflows onto non-development tasks where the official Superpowers workflow does not require them;
- fork or rewrite official Superpowers behavior;
- modify `vendor/obra-superpowers/`;
- make GitHub Arena a development-process owner;
- make CI the authority for human approval;
- merge automatically;
- authorize deploy, canary, stable, live smoke, R2/R3, or `PRODUCTION COMPLETE`;
- require new external cloud infrastructure for baseline enforcement;
- store credentials, tokens, private runtime traces, or raw conversation transcripts in repository evidence.

## 6. Authority model

The Process Gate SHALL preserve five distinct evidence/authority classes.

### 6.1 POLICY_REQUIRED

A repository rule says an action or workflow is mandatory.

Examples:

- Micro Arena is required for every controlled repository task;
- Review Arena is required for high-impact work;
- `using-superpowers` routing is required before development work;
- TDD is required for production code changes when the official Superpowers workflow applies.

Policy is obligation, not proof of execution.

### 6.2 PROCESS_ATTESTED

A process participant records that a required step occurred.

Examples:

- PR evidence says `using-superpowers` was invoked;
- evidence says Review Arena was performed;
- evidence records a RED command and a GREEN command.

Attestation is structured process evidence, but is not automatically independent verification.

### 6.3 CI_VERIFIED

Repository-controlled CI independently verifies a fact it can actually observe.

Examples:

- schema validity;
- process-evidence syntax;
- subject SHA binding;
- changed-path classification;
- required test job success;
- repository policy compatibility;
- presence of a required review artifact.

CI must not elevate unobservable runtime facts into this class.

### 6.4 RUNTIME_VERIFIED

A live host or runtime produced evidence for a runtime-specific claim.

Examples:

- Runtime Doctor host discovery;
- observed Native V1/V2 lifecycle tools;
- observed Subagent Broker lifecycle tools;
- real independent-agent IDs;
- approved live smoke result.

Runtime evidence must identify its source and subject.

### 6.5 HUMAN_AUTHORIZED

An explicit human approval permits a gated action.

Examples:

- approval of an architectural spec;
- approval of an implementation plan;
- merge authorization;
- separate live-smoke authorization where required.

Technical evidence cannot manufacture human authorization.

## 7. Mandatory routing

### 7.1 Every controlled repository task

For every WhiteChronos task handled in a repository-aware agent runtime:

```text
constraints
-> Superpowers routing check
-> task-specific workflow if applicable
-> specialized capability if justified
-> GitHub evidence / mutation if needed
-> Arena
-> result
```

The process record SHALL include:

```text
superpowers_routing = PASS
arena_mode = micro | review | full
```

### 7.2 Non-development tasks

For explanation, inspection, read-only research, or other non-development work:

- Superpowers routing still occurs;
- Micro Arena still applies;
- development-only gates such as TDD, worktrees, or code-review workflows are `NOT_APPLICABLE` unless the task evolves into development work.

### 7.3 Development tasks

For software-development work, the official Superpowers workflow owns process routing.

Typical mappings remain:

```text
new feature / architecture -> brainstorming
approved architecture -> writing-plans
implementation with real independent agents -> subagent-driven-development
implementation without real independent agents -> executing-plans
production code -> test-driven-development
bug / unexpected failure -> systematic-debugging
review -> requesting-code-review / receiving-code-review
completion -> verification-before-completion
branch completion -> finishing-a-development-branch
```

The Process Gate records and verifies compatibility with this routing. It does not redefine upstream Superpowers.

## 8. Arena policy

### 8.1 Micro Arena

Micro Arena is required for every controlled WhiteChronos task.

Required lenses:

- evidence-first;
- constraint-first;
- edge-cases-first;
- built-to-last.

### 8.2 Review Arena

Review Arena is required for:

- source-code changes;
- architecture;
- repository governance;
- CI/CD;
- runtime-control code;
- plugin/MCP changes;
- security-sensitive configuration;
- public or shared interfaces;
- release-control logic.

The default Review Arena uses at least four materially distinct strategies.

### 8.3 Full Arena

Full Arena is required only when:

1. the user explicitly requests Arena / Full Arena / tournament-style comparison; or
2. a more specific approved repository policy explicitly requires it.

Default target when required:

```text
16 materially distinct strategies
```

When real isolated subagents are not available, Full Arena may run as the truthful sequential ChatGPT adaptation described by the installed Arena Skill.

That adaptation MUST NOT be described as independent-agent execution.

## 9. Process evidence contract

The implementation SHALL define a machine-valid process evidence schema under:

```text
schemas/agent_process_evidence.schema.json
```

A conceptual evidence object contains at least:

```json
{
  "schema_version": "whitechronos-agent-process/v1",
  "subject": {
    "repository": "WhiteChronos/ChatGPT",
    "pull_request": 123,
    "subject_sha": "<exact commit SHA>"
  },
  "superpowers": {
    "routing_checked": true,
    "bootstrap": "using-superpowers",
    "workflow": ["test-driven-development"],
    "status": "PASS"
  },
  "arena": {
    "mode": "review",
    "status": "PASS",
    "independent_agents_claimed": false
  },
  "verification": {
    "status": "PASS",
    "evidence": []
  },
  "runtime": {
    "required": false,
    "status": "NOT_APPLICABLE",
    "evidence": []
  },
  "human_authority": {
    "merge_authorized": false
  }
}
```

Exact field names may be refined in the implementation plan, but the evidence classes and semantics in this specification are mandatory.

## 10. Evidence transport and SHA binding

The implementation SHALL NOT create a self-referential committed manifest that claims to contain its own final Git commit SHA.

Process evidence is instead bound to an external `subject_sha` representing the exact code/repository state being attested or verified.

Acceptable transport mechanisms may include:

- a machine-readable PR metadata block;
- a trusted GitHub issue/PR comment;
- a GitHub check/run artifact;
- a Runtime Doctor evidence record;
- another immutable or actor-attributed record approved in the implementation plan.

The gate SHALL require:

```text
evidence.subject_sha == current evaluated subject SHA
```

If the PR branch moves:

```text
old evidence -> STALE
```

New evidence must be produced for the new head.

## 11. Trust and provenance

Every evidence item SHALL declare enough provenance to classify its trust level.

Minimum concepts:

- evidence type;
- source actor or system;
- subject SHA;
- timestamp or stable record identifier;
- URI / comment ID / check ID / artifact ID where applicable;
- evidence class;
- claimed status.

The implementation plan SHALL define allowlists for trusted automated actors where necessary.

A user-editable PR body can satisfy structured attestation requirements but cannot, by itself, prove a live runtime claim.

## 12. Independent-agent claims

If process evidence states:

```text
independent_agents_claimed = true
```

the Process Gate SHALL require real lifecycle evidence.

At minimum, independent-agent evidence must establish:

- current runtime path;
- lifecycle capability actually observed;
- one or more real agent IDs;
- subject/task association;
- implementer/reviewer distinction when independent review is claimed.

Valid runtime paths may include:

```text
native_codex_multi_agent
subagent_broker
```

Invalid substitutes include:

- Arena strategy cards;
- role-play personas;
- same-context simulated reviewers;
- `agents.enabled=true` without host discovery;
- `multi_agent=true` without observed lifecycle tools;
- CI-only configuration evidence.

## 13. TDD and review evidence

When TDD is required, the process evidence SHALL identify:

- the focused RED command;
- the expected failure reason;
- the GREEN command;
- the result;
- applicable regression suite result.

CI may independently verify current tests, but a later green CI result is not proof that RED happened earlier.

Therefore:

```text
RED execution = PROCESS_ATTESTED or stronger
current GREEN = CI_VERIFIED when run in CI
```

When independent review is required, the evidence SHALL identify the reviewer source and result.

If a real independent reviewer is claimed, the independent-agent rules in Section 12 apply.

## 14. Gate decision model

The Process Gate SHALL evaluate the current task/PR in this order:

1. identify exact subject SHA;
2. classify affected paths and process risk;
3. determine required Superpowers obligations;
4. determine required Arena mode;
5. load process evidence;
6. validate evidence schema;
7. reject stale evidence;
8. validate claims against available independent CI/runtime evidence;
9. check unresolved critical/important process-review findings;
10. produce PASS or FAIL with deterministic findings.

Conceptual statuses:

```text
AGENT_PROCESS_GATE=PASS
AGENT_PROCESS_GATE=FAIL
```

## 15. Fail-closed findings

The implementation SHALL include deterministic failures equivalent to:

```text
SUPERPOWERS_ROUTING_MISSING
SUPERPOWERS_WORKFLOW_MISSING
ARENA_EVIDENCE_MISSING
ARENA_MODE_TOO_WEAK
PROCESS_EVIDENCE_INVALID
SUBJECT_SHA_MISMATCH
PROCESS_EVIDENCE_STALE
FALSE_INDEPENDENT_AGENT_CLAIM
RUNTIME_EVIDENCE_MISSING
TDD_EVIDENCE_MISSING
REVIEW_EVIDENCE_MISSING
VERIFICATION_EVIDENCE_MISSING
UNRESOLVED_PROCESS_BLOCKER
HUMAN_AUTHORITY_MISSING
```

Not every finding applies to every task.

The policy determines applicability.

## 16. GitHub control-plane integration

The implementation SHALL integrate the Process Gate into the existing required status check:

```text
github-control-plane-policy
```

The current repository ruleset already requires that check.

Therefore, the first implementation SHOULD prefer:

```text
existing required status check
-> existing policy validation
-> changed-path classification
-> agent process gate
```

over introducing another independent required check.

This avoids duplicating branch-governance authority.

A later ruleset change may be proposed separately only if evidence shows the single-check design is insufficient.

## 17. Proposed repository surfaces

The implementation plan should start from these surfaces:

```text
governance/AGENT_PROCESS_POLICY.json
schemas/agent_process_evidence.schema.json
pipeline/agent_process_gate.py
tests/test_agent_process_gate.py
.github/workflows/github-control-plane-policy.yml
.github/pull_request_template.md
AGENTS.md
```

The implementation plan may refine exact filenames while preserving the responsibility boundaries in this specification.

## 18. Policy model

`governance/AGENT_PROCESS_POLICY.json` SHALL define machine-readable requirements such as:

- global Micro Arena requirement;
- high-impact path classes requiring Review Arena;
- conditions requiring Full Arena;
- Superpowers routing requirement;
- software-development workflow obligations;
- runtime-evidence requirements for independent-agent claims;
- required verification classes;
- fail-closed behavior.

The policy SHALL NOT encode secrets.

The policy SHALL NOT duplicate official Superpowers Skill behavior line by line.

It records repository obligations and maps task/change classes to required process evidence.

## 19. Pull request evidence UX

The repository SHALL provide a standard PR evidence section or template so process evidence is not improvised for every change.

Human-readable output should make clear:

- exact subject SHA;
- applicable Superpowers workflow;
- Arena mode;
- TDD status if applicable;
- review status;
- runtime evidence if applicable;
- unresolved blockers;
- merge authorization state.

The human-readable template is not automatically the highest trust source. Trust comes from the evidence class and source provenance.

## 20. Runtime Doctor compatibility

The Process Gate SHALL preserve the Runtime Doctor hierarchy:

```text
CONFIGURED
LOCAL_RUNTIME_HEALTHY
HOST_DISCOVERED
LIVE_VERIFIED
```

A process gate may require a Runtime Doctor result.

It must not synthesize one.

In particular:

```text
CI config PASS != HOST_DISCOVERED
MCP manifest PASS != HOST_DISCOVERED
tool requested in config != tool observed in host
```

A stale host result remains a runtime recovery problem rather than a source-code defect unless separate defect evidence exists.

## 21. Existing PR #72 / #73 checkpoint

This project SHALL NOT rewrite, reset, close, merge, or invalidate the existing GitLab contingency checkpoint.

Current preserved checkpoint:

```text
PR #72 parent head:
76d9b8c8a85309d6bad161d2398c52461f360631

PR #73 Task 1 head:
76d9b8c8a85309d6bad161d2398c52461f360631
```

At the time this specification was written:

- Task 1 was not complete;
- Tasks 2-10 were not started;
- no GitLab mirror/CI execution had been completed;
- no merge had occurred.

The Process Gate implementation is a separate governance track.

After the Process Gate is implemented and approved, future #72/#73 execution must comply with the then-current process rules without inventing retroactive evidence for actions that did not occur.

## 22. Migration and rollout

The first release of the Process Gate SHALL use a staged rollout.

### Stage A — policy and tests

- add policy/schema/gate tests;
- integrate with local CI fixtures;
- verify no false runtime claims.

### Stage B — workflow integration

- invoke the gate from `github-control-plane-policy`;
- validate evidence for new or updated PR heads;
- preserve clear failure output.

### Stage C — operational adoption

- use the process evidence contract for new repository work;
- apply it to #72/#73 when those branches next move under the new policy;
- do not fabricate evidence for historical work.

The implementation plan SHALL define the exact compatibility behavior for PRs that predate the gate.

## 23. Security and privacy

The Process Gate SHALL NOT:

- print secrets;
- store credentials in process evidence;
- copy raw environment variables;
- commit raw private runtime traces;
- commit raw private chat transcripts;
- expose authorization tokens in PR metadata;
- broaden GitHub permissions merely to make the gate pass.

GitHub workflow permissions should remain read-only unless the implementation plan proves a narrower write is required and receives separate review.

## 24. Testing strategy

Implementation SHALL be TDD-driven.

Tests must cover at minimum:

1. Micro Arena required for ordinary controlled task evidence;
2. Review Arena required for high-impact changes;
3. Full Arena required only under approved triggers;
4. Superpowers routing required;
5. non-development task can mark development workflows `NOT_APPLICABLE`;
6. code change missing TDD evidence fails;
7. valid exact-subject evidence passes;
8. stale subject SHA fails;
9. independent-agent claim without runtime evidence fails;
10. Arena strategy-card claim cannot satisfy subagent evidence;
11. CI-only tool configuration cannot satisfy host discovery;
12. missing human authorization blocks only actions that actually require it;
13. existing GitHub control-plane policy validation remains intact;
14. gate error output is deterministic;
15. malformed evidence fails closed;
16. runtime evidence and attestation are not conflated.

Full repository regression and existing engineering-governance gates remain mandatory before merge.

## 25. Acceptance criteria

WhiteChronos Process Gate v1 is complete when:

1. repository policy explicitly requires Arena + Superpowers routing on the controlled path;
2. Micro Arena is represented as mandatory baseline process evidence;
3. Review Arena is machine-required for high-impact change classes;
4. Full Arena is machine-required when explicitly triggered;
5. Superpowers routing is machine-required for repository tasks;
6. applicable development workflow evidence is required for development work;
7. non-development tasks are not incorrectly forced through TDD;
8. process evidence is schema validated;
9. process evidence is bound to an exact subject SHA;
10. stale evidence fails closed;
11. independent-agent claims require real runtime evidence;
12. CI cannot satisfy `HOST_DISCOVERED` by configuration alone;
13. TDD RED attestation and current GREEN verification remain separate facts;
14. unresolved required-review blockers fail the gate;
15. human authorization remains a distinct authority class;
16. the gate runs inside the existing `github-control-plane-policy` required status check;
17. no additional required ruleset authority is introduced without separate approval;
18. no new paid infrastructure or credentials are required for baseline enforcement;
19. PR #72 / #73 are not mutated by this governance-spec project;
20. documentation clearly states the boundary between repository-enforceable behavior and unrelated ChatGPT/product surfaces;
21. all existing repository regression/governance tests remain green.

## 26. Product-surface boundary

The repository can enforce this process for repository-aware workflows that load WhiteChronos instructions and for the GitHub merge path controlled by its CI/ruleset.

It cannot truthfully guarantee that every unrelated ChatGPT conversation, external IDE session, or third-party agent will load these instructions before interacting with the user.

Therefore the strongest truthful claim is:

```text
100% required on the WhiteChronos controlled repository process path
```

not:

```text
100% guaranteed across every external product surface
```

Where supported, global Codex Skills/bootstrap may increase coverage, but this project must never label that as universal enforcement without runtime evidence.

## 27. Review Arena conclusions incorporated

The Review Arena used four sequential strategy perspectives in this session because independent subagent lifecycle tools were not exposed in the current ChatGPT harness.

Material conclusions incorporated:

- preserve Superpowers as process owner;
- preserve Arena as adversarial review layer;
- integrate with the existing required GitHub check rather than create a second control authority;
- separate policy, attestation, CI verification, runtime verification, and human authorization;
- bind evidence to exact subject SHA;
- fail stale evidence closed;
- do not use committed self-referential SHA manifests;
- do not accept PR-body text alone as runtime proof;
- do not accept Arena cards as independent agents;
- do not retroactively fabricate evidence for #72/#73;
- keep Full Arena targeted rather than indiscriminate;
- keep non-development tasks out of development-only gates;
- preserve runtime truthfulness even when that means the gate remains blocked.

## 28. Implementation boundary

This document approves and defines architecture only.

It does not itself authorize:

- implementation code;
- workflow mutation;
- ruleset mutation;
- merge;
- deployment;
- canary;
- stable promotion;
- live smoke;
- R2/R3;
- `PRODUCTION COMPLETE`.

After the human reviews and approves this committed specification, the next allowed Superpowers step is:

```text
writing-plans
```

The implementation plan must then be reviewed separately before implementation begins.
