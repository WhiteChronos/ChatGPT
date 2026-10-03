# Awesome LLM Apps Full-System Integration — Design Spec

**Date:** 2026-10-03  
**Repository:** `WhiteChronos/ChatGPT`  
**Upstream:** `Shubhamsaboo/awesome-llm-apps`  
**Status:** Design for user review  
**Scope class:** Architectural

## 1. Intent

Integrate the useful system surface of `Shubhamsaboo/awesome-llm-apps` into the WhiteChronos ChatGPT/Codex environment so that the system can discover and use:

- all canonical upstream Agent Skills;
- all AI-agent examples and agent teams;
- always-on agents;
- voice agents;
- MCP agents and MCP-related examples;
- Generative UI agents;
- RAG applications and tutorials;
- advanced LLM applications;
- agent-framework crash courses;
- scripts, manifests, environment templates, Docker/config files, prompts, tests/evals, and other reusable system components;
- project-internal Skills that belong to a particular example, without incorrectly promoting them to global Skills;
- external AI-agent/application projects explicitly linked from the upstream catalog/README, represented as linked references rather than silently mirrored or executed.

The goal is **full discoverability and controlled usability**, not indiscriminate execution.

A source example is not automatically a native Codex subagent, ChatGPT Skill, MCP connector, or background automation. The integration must preserve that distinction and create an explicit activation path for each runtime class.

## 2. User-required outcome

The finished integration must make the upstream ecosystem available through the existing WhiteChronos routing stack:

```text
ChatGPT / Codex
      |
      v
Superpowers Controller
      |
      v
Superpowers official process
      |
      v
ECC specialist layer
      |
      v
Matt Pocock specialist layer
      |
      v
Awesome LLM Apps Controller
      |
      +--> canonical Agent Skills
      |
      +--> AI-agent / multi-agent catalog
      |
      +--> RAG / MCP / voice / always-on / Generative UI catalog
      |
      +--> framework / app / component references
      |
      v
GitHub evidence and mutations
      |
      v
GitHub Arena final review
```

The Awesome LLM Apps layer is primarily a **library of executable examples, agent architectures, and reusable system components**. It must complement the existing process and specialist layers rather than replace them.

## 3. Verified upstream snapshot

Audit snapshot at design time:

- repository: `Shubhamsaboo/awesome-llm-apps`;
- branch: `main`;
- commit: `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`;
- license: Apache-2.0;
- GitHub repository size reported: 221953 KB;
- recursive tree entries: 2531;
- blobs: 1976;
- total `SKILL.md` files: 10;
- canonical Skills in `agent_skills/registry.json`: 7;
- total README files: 223;
- dependency manifests detected: 194;
- environment example files detected: 65;
- Dockerfiles detected: 8;
- MCP-related source/config/documentation files detected: 139;
- code files detected by common executable/source extensions: 996.

The largest observed blobs include:

- a GIF of approximately 24.9 MB;
- an MP4 of approximately 20.0 MB.

These large media artifacts are evidence that a literal byte-for-byte runtime mirror would add substantial repository weight without improving agent capability.

## 4. Canonical upstream Skills

The canonical installable Skills are defined by `agent_skills/registry.json` and currently are:

1. `advisor-orchestrator-worker`
2. `commit-archaeologist`
3. `dependency-doctor`
4. `first-reader`
5. `project-graveyard`
6. `scope-creep-detector`
7. `thinking-out-loud`

The directory `agent_skills/self-improving-agent-skills/` is currently an application with backend/frontend code and does **not** contain a canonical `SKILL.md`. It must therefore be catalogued as an application/system component, not falsely installed as an Agent Skill.

Three additional `SKILL.md` files currently exist inside the `generative_ui_agents/ai-mcp-app-builder` example. They are **project-internal Skills** and must remain scoped to that example unless a future explicit design promotes them.

## 5. Agent/application families that must be linked

The catalog and controller must cover the following upstream roots recursively:

- `starter_ai_agents/`
- `advanced_ai_agents/`
- `always_on_agents/`
- `voice_ai_agents/`
- `mcp_ai_agents/`
- `generative_ui_agents/`
- `rag_tutorials/`
- `advanced_llm_apps/`
- `ai_agent_framework_crash_course/`
- `agent_skills/`
- relevant documentation under `docs/`

Initial snapshot signals by major root:

| Root | Files | READMEs | Manifests | Docker | SKILL.md | Code files |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| starter_ai_agents | 58 | 16 | 18 | 0 | 0 | 22 |
| advanced_ai_agents | 545 | 58 | 59 | 1 | 0 | 353 |
| always_on_agents | 23 | 2 | 2 | 0 | 0 | 16 |
| voice_ai_agents | 33 | 4 | 4 | 0 | 0 | 21 |
| mcp_ai_agents | 23 | 7 | 7 | 0 | 0 | 7 |
| generative_ui_agents | 555 | 15 | 20 | 6 | 3 | 298 |
| rag_tutorials | 106 | 24 | 25 | 2 | 0 | 40 |
| advanced_llm_apps | 272 | 28 | 29 | 0 | 0 | 92 |
| ai_agent_framework_crash_course | 250 | 58 | 28 | 0 | 0 | 112 |
| agent_skills | 91 | 10 | 2 | 0 | 7 | 35 |

These counts are snapshot evidence, not hard-coded future limits.

### 5.1 External linked agents and applications

The upstream README also contains selected AI-agent/application entries whose implementation lives in another repository or external project.

To satisfy the requirement to **link all upstream-listed AI agents**, the generated catalog must capture those outbound entries when they appear in recognized agent/application sections.

External entries are catalogued with:

- `source_type = "external_reference"`;
- upstream README section/category;
- display title and description from the upstream listing;
- destination URL;
- host/repository identity when detectable;
- license status = `UNVERIFIED` until separately audited;
- execution status = `REFERENCE_ONLY` until separately audited.

The synchronization process must **not** recursively clone, mirror, install, or execute external repositories merely because the upstream README links to them. Any later use of an external reference requires a fresh provenance, license, dependency, and security audit for that external project.

## 6. Design alternatives considered

### Alternative A — literal full byte mirror plus automatic activation

Copy the entire upstream repository and attempt to expose every example directly to Codex/ChatGPT.

**Advantages**

- maximal local availability;
- simplest archival story.

**Rejected because**

- adds roughly hundreds of MB including demo media and generated artifacts;
- examples use many unrelated dependency stacks and API credentials;
- automatically exposing every agent/app as executable would blur the distinction between sample code, Skills, MCPs, subagents, and background services;
- increases clone, CI, indexing, and security cost.

### Alternative B — selective Skills only

Install only the seven canonical Skills and leave every other upstream application as an external link.

**Advantages**

- lightweight;
- low maintenance.

**Rejected because**

- does not meet the requirement to link and use all AI-agent and system components;
- loses local provenance and discoverability for the larger agent/app ecosystem.

### Alternative C — functional source mirror + full catalog + controlled activation

Maintain a functional source mirror of the upstream system, install the canonical Skills, index every agent/app/component, and activate executable examples only when a task needs them.

**Selected.**

This gives the user access to the complete upstream system while keeping runtime execution explicit and bounded.

## 7. Selected architecture

The integration will contain five independent layers.

### 7.1 Provenance / functional source mirror

Target:

```text
vendor/shubhamsaboo-awesome-llm-apps/
```

The mirror preserves source material needed to understand, adapt, test, and use upstream examples.

It must include:

- source code;
- README/documentation;
- Skills;
- tests and evals;
- prompts and templates;
- dependency manifests;
- environment examples;
- Docker/configuration files;
- MCP-related source/configuration;
- schemas and small runtime assets;
- data files required by examples where practical.

It must exclude from the WhiteChronos Git history by default:

- nested `.git` metadata;
- binary demo media larger than 10 MiB;
- generated build artifacts that have reproducible source equivalents;
- caches and dependency install directories.

Every excluded upstream file must still be represented in the generated catalog with:

- upstream path;
- upstream Git object SHA when available;
- size;
- exclusion reason;
- upstream commit.

If a task genuinely needs an excluded asset, the controller may materialize it from upstream into an ephemeral task workspace after the task requires it. Excluded content is not silently committed to `main`.

### 7.2 Canonical Skill projection

The seven canonical entries from `agent_skills/registry.json` are projected to project-scoped Codex Skills under:

```text
.agents/skills/<skill-name>/
```

The projection must preserve the upstream Skill folder contents.

Ownership is recorded in:

```text
.agents/skills/.awesome-llm-apps-managed.json
```

Rules:

- never overwrite an unmanaged Skill;
- never overwrite a Matt Pocock-managed Skill;
- never overwrite a future Skill owned by another controller;
- fail synchronization on a name collision instead of silently renaming or mutating upstream behavior;
- remove a previously managed upstream Skill only when the new upstream registry no longer contains it and the ownership manifest proves WhiteChronos owns that projection.

The project-internal Skills inside example applications are **not** projected globally.

Every projected canonical Skill must also receive catalog/ownership metadata describing its execution risk and required gate. Projection means **discoverable**, not permission to perform network calls, scan broad filesystem locations, launch external model CLIs, or mutate user state.

At minimum:

- `advisor-orchestrator-worker`: external-model/network/credential capable; external CLI/API dispatch requires an explicit user request for that orchestration workflow and available authorized credentials;
- `commit-archaeologist`: local repository read-only;
- `dependency-doctor`: local read-only by default; upstream opt-in network checks remain opt-in;
- `first-reader`: reasoning/text analysis only unless a specific input source requires another tool;
- `project-graveyard`: broad local filesystem/repository inspection; requires an explicit user request before scanning;
- `scope-creep-detector`: local repository read-only;
- `thinking-out-loud`: conversational control-flow Skill; it does not authorize unrelated file or network actions.

Repository `AGENTS.md` and the Awesome LLM Apps controller must enforce these gates even when the Skill itself is discoverable.


### 7.3 Full agent/app/component catalog

A deterministic catalog generator creates:

```text
registry/awesome-llm-apps/catalog.json
registry/awesome-llm-apps/catalog.summary.json
```

Every relevant upstream project/component is represented. Upstream-listed external agent/application links are also represented as `external_reference` catalog entries.

A catalog entry must include at least:

```json
{
  "id": "stable-normalized-id",
  "source_type": "upstream_internal",
  "upstream_path": "path/in/upstream",
  "external_url": null,
  "license_status": "VERIFIED_ROOT_LICENSE",
  "category": "agent_app",
  "subtype": "multi_agent",
  "title": "Human-readable title",
  "readme_path": "path/README.md",
  "skill_paths": [],
  "manifest_paths": [],
  "env_example_paths": [],
  "docker_paths": [],
  "mcp_related_paths": [],
  "languages": [],
  "frameworks": [],
  "providers": [],
  "external_services": [],
  "network_required": false,
  "credentials_required": false,
  "background_capable": false,
  "self_modifying": false,
  "high_stakes_domain": false,
  "execution_class": "REFERENCE_ONLY",
  "upstream_commit": "..."
}
```

The exact catalog schema will be versioned in the repository.

### 7.4 Awesome LLM Apps Controller

Create:

```text
plugins/awesome-llm-apps-controller/
```

The controller does not rewrite upstream examples. It performs:

- routing;
- catalog search;
- provenance reporting;
- activation-class enforcement;
- collision protection;
- source materialization policy;
- handoff to the appropriate existing process layer;
- safe selection of the most relevant upstream example.

The controller Skill triggers for requests involving:

- example AI agents;
- multi-agent teams;
- RAG;
- voice agents;
- MCP agents/apps;
- Generative UI;
- memory-based LLM apps;
- OpenAI Agents SDK and other agent frameworks represented upstream;
- always-on/background agents;
- agent templates;
- upstream example discovery;
- canonical upstream Agent Skills.

The ChatGPT package for the controller must remain below the 25 MiB Skill upload limit and therefore contains only control-plane instructions plus compact catalog metadata/references, not the full upstream mirror.

### 7.5 Activation adapter

Agent/app examples are not installed as native global subagents by default.

When the user asks to **use**, **adapt**, **run**, or **build from** a catalog entry, the controller applies an activation workflow:

1. identify the exact catalog entry and upstream commit;
2. inspect README, manifests, environment examples, Docker/MCP configs, scripts, and relevant source;
   - for an `external_reference`, first perform a separate provenance/license/security audit of the destination and do not treat the upstream root Apache-2.0 license as applying to that external project;
3. classify dependencies, network use, credentials, filesystem mutation, background behavior, and external services;
4. choose one of:
   - reference-only use;
   - source adaptation into the current codebase;
   - ephemeral local execution;
   - sandbox/container execution;
   - MCP/connector setup requiring explicit connection;
   - automation/background setup requiring explicit scheduling;
5. materialize only the selected example into an ephemeral task workspace;
6. run its own tests/evals where available before relying on it;
7. never mutate the read-only mirror;
8. never persist credentials in the repository;
9. report the exact upstream path and commit used.

## 8. Catalog discovery rules

The generator must enumerate the upstream tree deterministically.

### 8.1 Canonical Skills

Entries in `agent_skills/registry.json` are authoritative canonical Skill entries.

A registry entry without a corresponding valid `SKILL.md` is catalogued as an upstream registry inconsistency and is **not** projected as a Skill.

### 8.2 Project-internal Skills

Any other `SKILL.md` is catalogued with subtype `project_internal_skill` and attached to its nearest containing application entry.

### 8.3 Agent/app entries

Within the required roots, a directory becomes an application/component catalog entry when it contains at least one of:

- a README at that directory level;
- a dependency manifest;
- executable source that represents an independent example;
- a Dockerfile or service configuration;
- an internal Skill.

Nested applications are allowed. The nearest qualifying ancestor owns associated manifests/configs unless a deeper directory independently qualifies.

### 8.4 External-reference discovery

The catalog generator must parse recognized agent/application sections in the upstream README and detect list entries whose destination leaves `Shubhamsaboo/awesome-llm-apps`.

Those entries become `external_reference` records. The generator must not treat sponsor, translation, social, badge, or general documentation links as agent/application entries.

External entries are linked but not mirrored, installed, or executed by synchronization.

### 8.5 Component attachment

Files such as:

- `requirements.txt`;
- `pyproject.toml`;
- `package.json`;
- Dockerfiles;
- compose files;
- `.env.example`;
- MCP configuration;
- scripts;
- tests;
- prompt/template files;

are attached to the nearest catalog entry and remain independently searchable by path/type.

## 9. Runtime classification and gates

Every catalog entry receives an execution class. Canonical projected Skills receive the same risk metadata so discovery never implies execution authority.

### REFERENCE_ONLY

Documentation, architecture, examples, or source used only as reference.

No execution approval is required because nothing is executed.

### LOCAL_READ_ONLY

Local scripts that inspect data/repositories and do not write or use the network.

They may run when the task requires them after source inspection.

### LOCAL_MUTATING

Code that writes files, modifies a repository, changes state, or creates artifacts.

Run only when the user's task authorizes that mutation.

### NETWORKED

Code that makes network calls but does not require private credentials.

Use only when network access is relevant and allowed.

### CREDENTIALLED

Code requiring API keys, OAuth, wallets, cloud credentials, databases, messaging systems, or other authenticated services.

Never invent credentials or silently configure them.

### MCP_OR_CONNECTOR

Code that registers or uses MCP servers/connectors.

Do not globally enable connectors merely because an example references them. Connection/setup requires the current task and user-authorized environment.

### BACKGROUND_AUTONOMOUS

Always-on agents, schedulers, release radars, watchers, event consumers, or services that continue after the immediate request.

Do not start them as background services during ordinary chat. Scheduling/monitoring requires an explicit user request and the supported automation/runtime surface.

### SELF_MODIFYING

Self-improving/evolving agents or code that rewrites workflows/prompts/code.

Use only after explicit user selection, in an isolated workspace, with a diff/review gate before any changes are accepted.

### HIGH_STAKES_DOMAIN

Examples involving medical, financial, legal, mental-health, insurance, or similar high-stakes decisions receive this flag in addition to another execution class.

They remain software examples and must not bypass ChatGPT's domain/safety requirements or be treated as authoritative professional advice.

## 10. Routing precedence

Default software-development routing remains:

```text
System / developer / user / repository rules
  -> Superpowers process layer
  -> ECC specialist capability
  -> Matt Pocock specialist capability
  -> Awesome LLM Apps example/agent/component library
  -> GitHub evidence and mutation
  -> GitHub Arena final review
```

The Awesome LLM Apps layer is selected when it contributes a relevant concrete implementation, agent architecture, tutorial, or canonical upstream Skill.

Do not execute three overlapping TDD/debug/review workflows by default.

### Canonical Skill overlap rules

- `advisor-orchestrator-worker`: do not replace native Codex multi-agent or Superpowers subagent workflows automatically. Use when the user explicitly requests that architecture or its external advisor/worker model strategy is materially required.
- `commit-archaeologist`: may be used for local Git history questions.
- `dependency-doctor`: may be used for dependency-manifest diagnostics; network checks remain opt-in where upstream defines them as opt-in.
- `first-reader`: use for reader-experience review, not generic code review.
- `project-graveyard`: filesystem-wide project scanning requires an explicit user request because it inspects personal/local repositories.
- `scope-creep-detector`: may be used for diff-vs-intent scope analysis.
- `thinking-out-loud`: may trigger on the upstream-described ramble/voice-dictation conditions, subject to higher-priority instructions.

## 11. Codex integration

Codex project integration will use:

- `.agents/skills/` for the seven canonical Skills;
- the controller plugin in the WhiteChronos local marketplace;
- `.codex/config.toml` to enable the controller;
- existing `multi_agent = true`;
- `AGENTS.md` to define routing and safety;
- the generated catalog for discovery;
- the functional mirror for source/provenance.

The upstream repository is **not** treated as a single native Codex plugin unless upstream later publishes a compatible plugin manifest.

## 12. ChatGPT /skills integration

Create one user-installable Skill package:

```text
awesome-llm-apps-controller/skill.zip
```

It provides:

- routing;
- compact catalog/navigation references;
- provenance policy;
- activation classes;
- upstream lookup instructions.

The package must not include the full functional mirror.

The seven canonical upstream Skills may also be packaged individually for ChatGPT import if validation confirms they satisfy the current ChatGPT Skill format. They must remain separate Skills so their trigger descriptions remain usable.

This session cannot guarantee programmatic installation into the user's global `/skills` library; package generation and verification are the repository-side deliverables.

## 13. Synchronization

Add a workflow:

```text
.github/workflows/sync-awesome-llm-apps.yml
```

Triggers:

- manual;
- daily scheduled check;
- relevant controller/sync-script changes.

The synchronization job:

1. clones upstream `main` without executing upstream code;
2. records upstream commit;
3. validates root Apache-2.0 license presence;
4. regenerates the functional source mirror;
5. regenerates catalog and summary;
6. validates canonical Skill registry vs actual `SKILL.md` files and derives their execution-risk metadata;
7. projects canonical Skills with collision checks and writes their ownership/risk manifest;
8. catalogs recognized external agent/application links without cloning them;
9. records excluded binary/generated artifacts;
10. updates a version/provenance lock;
11. runs sync/catalog tests;
12. pushes a review branch if anything changed;
13. attempts to open a PR;
14. if repository policy blocks Actions-created PRs, leaves the branch ready and completes with a warning instead of failing.

No upstream installer is executed during synchronization.

## 14. Provenance and lock data

Create a lock file containing:

- upstream repository;
- branch/ref;
- observed commit;
- license;
- tree entry/blob counts;
- canonical Skill names/count;
- catalog entry counts by category and source type;
- external-reference count and unresolved-license count;
- included mirror file count/bytes;
- excluded file count/bytes;
- exclusion policy version;
- synchronization workflow path;
- catalog schema version.

Every catalog entry records the upstream commit.

## 15. License handling

Root upstream license is Apache-2.0.

The functional mirror must preserve the upstream `LICENSE` and notices.

If a subdirectory contains a more specific license/notice, the catalog must attach it to that entry and preserve it in the mirror.

An empty or inconsistent license field in an upstream registry is recorded as metadata inconsistency; it is not silently rewritten.

## 16. Security and dependency policy

Synchronization copies and indexes source but does not install dependencies.

No automatic:

- `pip install`;
- `npm install`;
- `pnpm install`;
- Docker build/run;
- global CLI install;
- MCP registration;
- API-key creation;
- wallet setup;
- browser automation launch;
- background daemon;
- cloud deployment;
- external database creation.

Those actions belong to a later task-specific activation after source inspection and user/environment authority.

Environment-example files are metadata and templates only. Secrets are never committed.

## 17. Testing strategy

Implementation must be test-first for synchronization/catalog logic.

Required test classes:

### Synchronizer tests

- initial mirror generation;
- update replaces stale upstream files;
- unrelated WhiteChronos files remain untouched;
- nested `.git` is removed;
- large excluded binary is represented in catalog/provenance;
- generated-artifact exclusion is deterministic;
- symlinks are handled predictably;
- upstream source is never executed by sync;
- external linked repositories are catalogued but never cloned or executed by sync.

### Skill projection tests

- all canonical registry entries with valid `SKILL.md` are projected;
- project-internal Skills are not globally projected;
- every projected canonical Skill receives deterministic execution-risk metadata;
- registry entry without `SKILL.md` is reported, not installed;
- unmanaged collision fails safely;
- Matt Pocock-managed collision fails safely;
- removed upstream managed Skill is cleaned only when ownership is proven.

### Catalog tests

- deterministic output ordering;
- stable IDs;
- every qualifying project/component is indexed;
- manifests and env examples attach to the correct entry;
- internal Skills attach to their containing project;
- recognized external agent/application links become external-reference entries while unrelated outbound links do not;
- runtime class flags derive predictably;
- catalog contains upstream commit/provenance;
- schema validates.

### Controller tests

- routes RAG requests to RAG entries;
- routes MCP requests to MCP entries;
- routes voice/always-on/Generative UI requests to their families;
- does not claim sample apps are native Codex subagents;
- does not auto-run background/credentialled/self-modifying examples;
- preserves Superpowers/ECC/Matt precedence.

### Repository validation

Existing WhiteChronos governance/CI must remain green before merge.

## 18. Initial snapshot acceptance invariants

For upstream commit `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`, initial implementation tests must be able to account for:

- 2531 recursive tree entries;
- 1976 blobs;
- 10 total `SKILL.md` files;
- 7 canonical registry Skills;
- 223 README files;
- 194 dependency manifests;
- 65 environment examples;
- 8 Dockerfiles;
- 139 MCP-related files;
- 996 code files under the audited extension set.

These values verify the cataloger against the audited snapshot. Future upstream syncs are allowed to change them.

## 19. Repository layout

Planned layout:

```text
WhiteChronos/ChatGPT/
  .agents/
    skills/
      .awesome-llm-apps-managed.json
      advisor-orchestrator-worker/
      commit-archaeologist/
      dependency-doctor/
      first-reader/
      project-graveyard/
      scope-creep-detector/
      thinking-out-loud/
    plugins/
      marketplace.json

  .codex/
    config.toml

  .github/
    workflows/
      sync-awesome-llm-apps.yml

  plugins/
    awesome-llm-apps-controller/
      .codex-plugin/
        plugin.json
      README.md
      upstream.lock.json
      scripts/
        sync_mirror.sh
        build_catalog.py
      tests/
      skills/
        awesome-llm-apps-controller/
          SKILL.md
          agents/
            openai.yaml
          references/

  registry/
    awesome-llm-apps/
      catalog.schema.json
      catalog.json
      catalog.summary.json

  vendor/
    shubhamsaboo-awesome-llm-apps/
      LICENSE
      README.md
      ...
      .whitechronos-mirror.json
      .whitechronos-excluded.json

  docs/
    superpowers/
      specs/
        2026-10-03-awesome-llm-apps-full-system-integration-design.md
```

## 20. Error handling

Synchronization must fail closed when:

- the upstream clone cannot be verified;
- root licensing disappears or becomes unrecognized;
- the canonical Skill registry is invalid JSON;
- a canonical Skill collides with a non-owned project Skill;
- catalog schema generation fails;
- an included source file cannot be copied faithfully;
- provenance metadata cannot be written.

Synchronization must not partially update `main`. Changes land through a review branch and PR.

A blocked automatic PR is not a synchronization failure if the branch was successfully pushed and the workflow clearly reports that a human/connected GitHub app must open the PR.

## 21. Update and drift behavior

The generated catalog is the current source of discovery for WhiteChronos.

When upstream changes:

- new canonical Skills are detected but still pass collision/format validation;
- new agent/app roots are indexed automatically if they match catalog rules;
- new dependency/runtime requirements update entry metadata;
- removed entries remain visible only in Git history, not active catalog;
- upstream commit drift is recorded;
- no local behavior fork is created to hide an upstream incompatibility.

## 22. Chat-level behavior

When a user asks for an AI-agent solution, the controller should:

1. identify whether an existing Superpowers/ECC/Matt Skill is already the more appropriate process/tool;
2. search Awesome LLM Apps catalog for concrete examples;
3. present/use the most relevant entry or small set of entries;
4. distinguish reference use from actual execution;
5. inspect prerequisites before execution;
6. ask only for required missing credentials/connections when execution truly needs them;
7. never enable unrelated examples.

The system should make **all** upstream agents/components discoverable without loading **all** of their source into every chat context.

## 23. Non-goals

This integration will not:

- claim every upstream example is a native ChatGPT agent;
- claim every upstream example is a native Codex subagent;
- run all examples at startup;
- enable every MCP server globally;
- install every dependency stack;
- create API keys or credentials;
- schedule all always-on agents;
- auto-run self-improving agents against `main`;
- replace Superpowers, ECC, Matt Pocock, or GitHub Arena;
- convert high-stakes demo applications into professional advice systems.

## 24. Acceptance criteria

The architecture is implemented successfully when:

1. the controller is registered and enabled for Codex;
2. all seven valid canonical upstream Skills are project-discoverable with provenance and ownership tracking;
3. every qualifying upstream agent/app/component is represented in the generated catalog;
4. the functional source mirror contains all required system source while excluded large/generated artifacts remain traceable;
5. all major upstream families are routable from the controller;
6. selected internal examples can be materialized and adapted without mutating the mirror, while external references require a separate audit before materialization;
7. credentialled/background/MCP/self-modifying examples are gated;
8. sync produces review branches/PRs and does not execute upstream code;
9. existing Superpowers/ECC/Matt/Arena routing remains intact;
10. all repository CI/governance gates pass;
11. a validated `awesome-llm-apps-controller/skill.zip` is produced for ChatGPT;
12. post-merge verification confirms main contains the expected controller, catalog, mirror metadata, Skill ownership manifest, and Codex enablement.

## 25. Implementation boundary

This document approves **architecture only**.

No production implementation, dependency installation, external service setup, runtime execution, or merge is authorized by this spec alone.

After the user reviews and approves this committed spec, the next required Superpowers step is to invoke `writing-plans` and produce the detailed implementation plan. Implementation begins only after that plan is also reviewed and the execution method is selected.
