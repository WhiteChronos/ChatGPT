# AGENTS.md — Engineering Compatibility / Codex

This repository contains engineering-governance rules for Automation, HVAC, Electrical and related disciplines.

## Mandatory rule
Before creating, editing, reviewing or approving compatibility-analysis code, schemas, reports, pipelines or documentation, read:

1. `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`
2. `governance/AUTOMATION_HYPERFOCUS_GOLDEN_RULE_v1_0.md`
3. `governance/ENGINEERING_COMPATIBILITY_HARDENING_v1_1.md`
4. `schemas/engineering_compatibility.schema.json`
5. `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`
6. `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`
7. `memory/ENGINEERING_COMPATIBILITY_MEMORY.md`

## Codex operating contract
Codex SHALL:

- apply Protocol Zero: explicit technical question before promoting a suspected discrepancy to a finding;
- keep unanswered questions as NOT_VERIFIABLE/pending and never promote them to confirmed findings;
- apply Automation/Data hyperfocus through TAG -> I/O -> PLC/RTU -> logic -> network/protocol -> data quality -> HMI/SCADA -> FAT/SAT;
- preserve the master-discipline authority for physical attributes and never silently override it from a derived discipline;

- preserve all source evidence and provenance;
- require SHA-256 provenance for every baseline document and every evidence record;
- compare valid hexadecimal SHA-256 digests case-insensitively;
- never convert `/visualize` into a short summary;
- keep compatibility and coverage as separate metrics;
- treat `assessment_records` as the authoritative complete criterion inventory;
- require every assessment record, including VERIFIED records, to carry provenance-bearing evidence and structured evidence quality before contributing to coverage or compatibility;
- require evidence documents declared by an assessment to belong to that assessment's `document_ids` and baseline inventory;
- derive `scope_summary` from `assessment_records` so unsupported counts cannot inflate coverage;
- derive coverage from structured assessment classifications so `NOT_VERIFIABLE` reduces coverage;
- recompute global, interface, discipline and document compatibility from `assessment_records` and mandatory status weights;
- classify every assessment as VERIFIED, PARTIAL, DIVERGENT, NOT_VERIFIABLE or NOT_APPLICABLE;
- require every PARTIAL, DIVERGENT or NOT_VERIFIABLE assessment record to be represented by a corresponding complete finding;
- treat `interface=true` only as a multidisciplinary interface assessment: it must identify at least two distinct baseline disciplines and provenance evidence must cover at least two distinct interface disciplines;
- identify document, revision, sheet/page, TAG/location and evidence for every engineering claim;
- require every baseline discipline and every baseline document to have an explicit compatibility score;
- require a structured calculation method with denominator definition and status weights;
- perform `/factcheck`, `/thenvsnow`, `/comparison`, `/deepdive`, `/rootcause`, `/audit`, `/redteam`, `/premortem`, `/viability` and `/actionplan` when relevant;
- treat CRITICAL findings with status `OPEN` or `IN_REVIEW` as release blockers regardless of classification;
- accept `WAIVED` findings only when `waiver.approval_record_id` resolves to an independently trusted human approval record in configuration;
- never accept self-declared waiver metadata as authorization;
- block unreconciled baselines, missing mandatory documents, non-current mandatory documents and failed discipline interfaces;
- validate finding and assessment disciplines against `baseline.disciplines`;
- require structured evidence quality and confidence for every finding;
- distinguish source-derived fact from inference and external knowledge;
- evaluate simpler, safer, lower-cost and more maintainable alternatives when system architecture is involved;
- require explicit nonblank lifecycle impact text for design, procurement, fabrication, programming, commissioning, operation, maintenance, safety, cost and schedule; use `NONE` when there is no impact;
- require nonblank comparison, root cause, solution and closure criterion;
- never overwrite raw Data Center sources;
- reject NaN/Infinity and other non-standard numeric values;
- validate generated datasheets against `schemas/engineering_compatibility.schema.json`;
- use `pipeline/engineering_compatibility_gate.py` as the canonical release validator;
- ensure any secondary compatibility CLI delegates to the canonical gate rather than duplicating thresholds or blocker logic.

## Required validation commands
Before proposing merge, Codex SHALL run or ensure CI runs:

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

The no-argument gate validates the permanent known-good fixture at `datasheet/projects/example-project.json`. Real projects MUST also be validated explicitly:

```bash
python pipeline/engineering_compatibility_gate.py datasheet/projects/<project>.json
```

## Visualization contract
Every final engineering report SHALL expose all relevant findings using a complete visual hierarchy. Required elements include:

- overall gate and compatibility;
- compatibility by discipline and interface;
- coverage;
- document-by-document assessment;
- complete finding cards;
- evidence quality and confidence;
- evidence vs comparison;
- root cause;
- impact by lifecycle stage;
- primary and secondary documents to adjust;
- proposed correction text where applicable;
- feasibility alternatives for architecture/system-design findings;
- closure criterion;
- missing documents and NOT_VERIFIABLE items;
- action plan and release gate.

Use severity semantics consistently:

- CRITICAL = red
- HIGH = orange
- MEDIUM = yellow
- LOW / NOT_VERIFIABLE = blue
- VERIFIED / COMPATIBLE = green
- NOT_APPLICABLE = gray

These color mappings are machine-enforced and must not be remapped.

## Release integrity contract
A datasheet may declare `PASS` only when all of the following are true:

- baseline documents are present and the baseline is reconciled;
- every mandatory document has an eligible current/approved status;
- `blocking_missing_documents` exactly matches the computed mandatory missing/non-current inventory and is empty;
- `scope_summary` exactly matches `assessment_records`;
- every assessment record has source evidence, matching revision/hash provenance and structured evidence quality;
- every issue-classified assessment (`PARTIAL`, `DIVERGENT`, `NOT_VERIFIABLE`) has a corresponding finding;
- every interface assessment represents at least two baseline disciplines and has evidence spanning at least two interface disciplines;
- coverage is reproducible from `assessment_records` and meets threshold;
- global, interface, discipline and document compatibility values match recomputed weighted scores;
- no open CRITICAL finding remains;
- any waiver references a trusted human approval record outside the datasheet;
- evidence provenance hashes match corresponding baseline document hashes regardless of hexadecimal case;
- findings reference valid assessment records and valid baseline disciplines;
- every finding includes evidence quality and nonblank required technical text;
- architecture-impact findings include alternatives and viability analysis;
- schema and semantic validation return no errors.

## Pull request compatibility
A pull request that changes compatibility-analysis logic, engineering schemas, Data Center manifests, datasheets, report-generation code or either compatibility validator MUST pass the Engineering Compatibility Visualize Gate and repository governance checks before merge.


## Global Arena review layer

For every Codex task in this repository, agents SHALL read `plugins/github-arena/SKILL.md` and apply its Micro Arena before finalizing the result.

Agents SHALL:

- apply the four default lenses: evidence-first, constraint-first, edge-cases-first and built-to-last;
- use Review Arena for code, architecture, CI/CD, repository governance, security-sensitive configuration, public API or other high-impact changes;
- use Full Arena only when explicitly requested;
- never claim that independent subagents were executed unless the runtime actually provided and executed them;
- preserve the engineering governance rules in this `AGENTS.md`;
- preserve upstream attribution and verify licensing before copying substantive third-party source;
- when the `github_arena` MCP server is available, call `arena_review_checklist` for GitHub work before finalizing;
- for high-impact GitHub or coding changes, call `arena_plan` and `arena_cards` before choosing the implementation approach;
- use the GitHub connector for repository reads/writes and the Arena MCP only for review/planning; never duplicate GitHub credentials inside Arena.

## Official Superpowers workflow layer

For every Codex software-development task in this repository, agents SHALL prefer the official `Superpowers` plugin from the OpenAI Codex marketplace and SHALL treat `plugins/superpowers-controller` as a routing/provenance layer, not as a fork of upstream behavior.

Agents SHALL:

- consult the official `using-superpowers` bootstrap before development work and invoke the relevant official Superpowers Skill before acting;
- use `brainstorming` before implementing a new feature or architecture when that Skill applies;
- preserve Superpowers planning, worktree, TDD, systematic-debugging, code-review, verification and finish-the-branch gates;
- use real subagents only when the runtime actually provides them; otherwise follow the official fallback workflow rather than fabricating subagent execution;
- never edit `vendor/obra-superpowers/` manually; that tree is a read-only byte mirror maintained by `.github/workflows/sync-superpowers-mirror.yml`;
- use the mirror only for search, provenance, audit, recovery and upstream comparison;
- record upstream/runtime version drift instead of modifying official Superpowers Skills to close the gap;
- continue applying this repository's engineering-governance rules and GitHub Arena review layer alongside Superpowers.




## Official ECC specialized engineering layer

For Codex software-development and technical workflow tasks in this repository, agents SHALL use the official upstream-native `affaan-m/ECC` plugin as a specialized engineering library while keeping Superpowers as the default development-process layer.

Agents SHALL:

- treat `plugins/ecc-controller` as routing, provenance and safety policy, not as a behavioral fork of ECC;
- prefer the official ECC plugin loaded from `https://github.com/affaan-m/ECC.git` for current ECC Skills, hooks, MCP declarations, agents and runtime behavior;
- use ECC for specialized domain/framework/security/accessibility/agent-harness/verification/operations work when it contributes distinct evidence or capability;
- avoid rerunning generic TDD, debugging, planning and code-review workflows across Superpowers, ECC and Matt Pocock by default; Superpowers owns the primary process gate unless the user or a more specific repository rule selects another workflow;
- use ECC focused reviewers or security/verification Skills as additive specialist passes when justified by the change;
- never duplicate ECC native hooks into separate global configuration; duplicate hook registration can execute the same automation twice;
- preserve ECC's lean-MCP policy and never enable every optional MCP server automatically;
- treat hooks, MCP servers, shell scripts, autonomous loops, installers and credentialed integrations as executable configuration requiring explicit task/environment authority before execution;
- never execute code from `vendor/affaan-m-ecc/`; that tree is a read-only byte mirror maintained by `.github/workflows/sync-ecc-mirror.yml`;
- use the ECC mirror only for provenance, audit, recovery, source inspection and upstream comparison;
- only claim multi-agent/subagent execution when independent agents actually ran in the current runtime;
- use the GitHub connector for repository evidence and mutations;
- apply GitHub Arena after the applicable Superpowers/ECC/Matt workflow for high-impact GitHub or coding changes.

Default routing order for overlapping development tasks is: repository/system/user constraints -> Superpowers process -> ECC specialist capability -> Matt Pocock specialist capability -> GitHub evidence/mutation -> GitHub Arena final review.

## Matt Pocock complementary skills layer

For Codex software-development and technical workflow tasks in this repository, agents SHALL treat the promoted stable skills from `mattpocock/skills` as a complementary specialized library. Superpowers remains the default development-process layer unless the user explicitly requests a Matt Pocock workflow or a more specific repository instruction selects it.

Agents SHALL:

- preserve the upstream Matt Pocock distinction between model-invoked and user-invoked skills;
- never silently execute a Matt user-invoked skill; recommend the relevant explicit skill and wait for the user to invoke it;
- prefer Superpowers for overlapping TDD, debugging and code-review process unless the user explicitly asks for the Matt Pocock variant;
- use Matt model-invoked skills when their specialized discipline materially improves the task, including domain modeling, codebase design, cited engineering research, prototype evidence, PR framing, human-only setup wizards and writing for agents;
- treat `.agents/skills/.matt-pocock-managed.json` as the ownership manifest for Matt-managed project skills;
- never manually edit Matt-managed directories under `.agents/skills/`; they are synchronized byte-for-byte from upstream;
- never edit `vendor/mattpocock-skills/` manually; it is a read-only full upstream mirror maintained by `.github/workflows/sync-matt-pocock-skills.yml`;
- keep `skills/in-progress` and `skills/deprecated` mirror-only unless the user explicitly requests an experimental/deprecated skill;
- refuse automatic synchronization when an upstream Matt skill name would overwrite an unmanaged project skill;
- use the GitHub connector for repository evidence and mutations;
- apply GitHub Arena after the applicable Superpowers/Matt workflow for high-impact GitHub or coding changes.

## Real Subagent runtime layer

For workflows that require independent child agents, agents SHALL use the following runtime order:

1. Prefer native Codex multi-agent spawn/follow-up/wait tools when those tools are actually exposed by the current harness.
2. Otherwise use the `subagent-broker` MCP fallback when its tools are present and healthy.
3. Otherwise use the official Superpowers inline fallback and explicitly state that independent subagents were unavailable.

Agents SHALL:

- never infer native subagent availability from `agents.enabled = true` alone; repository configuration is not host-discovery evidence;
- never call a prompt persona, same-context role play, or GitHub Arena strategy card an independent subagent;
- require real lifecycle evidence (agent ID plus native/broker execution evidence) before claiming a child ran;
- keep write-capable broker children on isolated `subagent/<agent_id>` branches and `.worktrees/subagents/<agent_id>/` worktrees;
- never allow a child to write directly to `main` or the parent task branch;
- use detached isolated snapshots for broker reviewers/read-only children;
- preserve Superpowers task briefs, ledgers, report/review packages, TDD, fix rounds, and final review gates;
- review child commits before integrating them into the parent branch;
- never broaden filesystem, network, approval, credential, or sandbox permissions merely to make a child succeed;
- treat `.superpowers/subagents/` traces as sensitive local runtime evidence and never commit them automatically;
- use GitHub Arena as review/quality control, never as a substitute for actual subagent execution.

Default subagent routing is: native Codex multi-agent -> Subagent Broker -> Superpowers inline fallback.


## Awesome LLM Apps full-system integration layer

For AI-agent/application examples, RAG, MCP agents, voice agents, always-on agents, Generative UI, memory apps, agent-framework examples and canonical Skills sourced from `Shubhamsaboo/awesome-llm-apps`, agents SHALL use `plugins/awesome-llm-apps-controller` as the routing, provenance and activation-safety layer.

Default routing order is: Superpowers -> ECC -> Matt Pocock -> Awesome LLM Apps -> GitHub -> GitHub Arena.

Agents SHALL:

- use `registry/awesome-llm-apps/catalog.json` as the discovery source and `plugins/awesome-llm-apps-controller/upstream.lock.json` as provenance;
- treat `vendor/shubhamsaboo-awesome-llm-apps/` as a read-only synchronized source mirror;
- never manually edit Awesome-managed Skills under `.agents/skills/`;
- preserve project-internal Skills inside their containing examples rather than globally projecting them;
- require a separate provenance/license/security audit before using any `external_reference` as executable source;
- never auto-run `CREDENTIALLED`, `BACKGROUND_AUTONOMOUS`, `SELF_MODIFYING`, `MCP_OR_CONNECTOR`, or other gated examples merely because they are discoverable;
- never create or persist credentials merely to execute an upstream example;
- require an explicit user request before `project-graveyard` performs broad filesystem/project scanning;
- require explicit orchestration intent and authorized credentials before `advisor-orchestrator-worker` dispatches external models/CLIs;
- never claim an upstream sample app is a native Codex subagent, native ChatGPT agent, connector, or background automation without actual runtime evidence;
- apply GitHub Arena after the applicable Superpowers/ECC/Matt/Awesome workflow for high-impact changes.


## WhiteChronos Runtime Doctor

For runtime claims about Codex, Arena MCP, Subagent Broker, or native multi-agent availability, agents SHALL use Runtime Doctor evidence when the Doctor is available. Repository config alone is never proof that the current host loaded a capability.

- `HOST_RELOAD_REQUIRED` must not trigger code changes; start a fresh Codex environment/session instead.
- Independent subagent claims still require real lifecycle evidence from the current runtime.
- Preserve the existing routing order: repository constraints -> Superpowers -> specialized capability -> GitHub -> GitHub Arena.


## TinyFish connection and browser policy layer

For TinyFish search, content retrieval, browser automation, Browser Profiles, monitors, and cost-sensitive actions, agents SHALL use `plugins/tinyfish-controller` as the routing and safety-policy layer while the official TinyFish ChatGPT app remains the runtime provider.

The routing order for relevant work is:

```text
repository/system/user constraints
-> Superpowers
-> specialized capabilities/controllers
-> Connection Controller / TinyFish policy when relevant
-> native GitHub/GitLab evidence and mutation
-> GitHub Arena final review
```

Agents SHALL:

- prefer native GitHub/GitLab connectors for repository API reads, writes, pull requests, pipelines, and project metadata;
- never use TinyFish as a credential broker for native GitHub/GitLab connectors;
- never request passwords in chat and never persist passwords, tokens, cookies, browser storage, or session credentials in Git or evidence files;
- keep TinyFish service authentication separate from Browser Profile health;
- classify service PASS plus Browser Profile failure as `DEGRADED`, not as whole-service failure;
- use TinyFish browser automation only for a concrete user-directed website interaction;
- use Browser Profiles only when authenticated browser state is required and the profile API is healthy;
- treat `HOST_POLICY_BLOCKED` as not a source-code defect and never mutate source merely to bypass platform policy;
- never create Browser Profiles, Agent runs, Browser runs, monitors, top-up operations, or auto-reload changes as routine health checks;
- create or run monitors only with explicit user intent for ongoing monitoring;
- after a TinyFish browser timeout or error, poll the same run and do not start a duplicate run automatically;
- preserve Runtime Doctor for Codex/Arena/Broker/native runtime claims and GitHub Arena for review rather than treating TinyFish as either runtime proof or an independent-agent substitute.
