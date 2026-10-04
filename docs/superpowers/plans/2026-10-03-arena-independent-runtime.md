# Arena Independent Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `WhiteChronos/arena-mcp-runtime` as the independent canonical home of GitHub Arena, preserving the exact four-tool contract while adding portable plugin packaging, a local stdio runtime, and a locally testable Streamable HTTP adapter.

**Architecture:** Extract the current Arena behavior from `WhiteChronos/ChatGPT@ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988` into a public MIT-licensed repository with one shared core and two transport adapters. The plugin package registers only the stdio MCP in this slice so the host never sees duplicate Arena tool names; the HTTP adapter is tested and deployment-ready but remains opt-in until the later Runtime Marketplace/consumer-migration plans.

**Tech Stack:** Node.js 22, ECMAScript modules, Node built-in test runner, `@modelcontextprotocol/sdk@1.32.0`, `zod@3.25.76`, portable Agent Plugins manifests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-03-runtime-independent-architecture-design.md`

## Global Constraints

- New repository: `WhiteChronos/arena-mcp-runtime`.
- Repository visibility: **public**.
- Default branch: **main**.
- License: **MIT**, preserving attribution to `Jakeschincariol/arena-skill`.
- Canonical plugin ID remains `github-arena`.
- Initial independent-runtime release version: **1.2.0**.
- Source extraction baseline: `WhiteChronos/ChatGPT@ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988`, path `plugins/github-arena/`, plugin version `1.1.0`.
- Preserve exact tool names:
  - `arena_plan`
  - `arena_cards`
  - `arena_rubric`
  - `arena_review_checklist`
- Preserve Arena rubric weights exactly: correctness 30, completeness 25, robustness 20, specificity 15, clarity 10.
- Preserve maximum Arena strategy count at 2,160.
- Preserve read-only MCP safety annotations for all four tools.
- Do not create or expose any GitHub mutation tool in Arena.
- Do not create any subagent execution tool in Arena.
- Use root `plugin.json` and `mcp.json` as portable source manifests.
- Generate/validate `.codex-plugin/plugin.json` and `.mcp.json` as compatibility artifacts; never hand-maintain divergent definitions.
- Only the stdio server is registered in the portable/compatibility plugin package in this slice.
- The Streamable HTTP adapter must run and pass tests locally, but **production deployment is out of scope** for this plan.
- Do not modify `WhiteChronos/ChatGPT` consumer marketplace/config in this plan; consumer migration has its own later plan.
- Do not delete or weaken the existing in-repo Arena plugin.
- Do not rerun or rewrite historical PR/CI/TDD evidence from the original implementation.
- Because the `github-arena` Skill is being migrated/updated, implementation must invoke the installed `skill-creator`, validate the completed self-contained Skill, and package it as exactly `skill.zip`; the ZIP is a release/user artifact and must not be committed.
- If the active GitHub connector/runtime cannot create a repository, stop at repository creation with `USER_ACTION_REQUIRED`; use an authenticated GitHub admin surface such as `gh` or GitHub UI/Work. Never simulate repository creation by creating a folder inside `WhiteChronos/ChatGPT`.
- Do not claim host discovery or live ChatGPT/Codex loading from CI.
- No public HTTP hosting, credentials, DNS, cloud project, or paid infrastructure is created in this plan.

## Repository Settings

When creating `WhiteChronos/arena-mcp-runtime`, use:

```text
owner              WhiteChronos
name               arena-mcp-runtime
visibility         public
default branch     main
issues             enabled
wiki               disabled
projects           disabled unless inherited policy requires them
license            MIT
description        Independent GitHub Arena MCP runtime for WhiteChronos ChatGPT and Codex integrations.
```

If repository creation is performed by `gh`, use the authenticated WhiteChronos account and verify the resulting owner/name and visibility before any source is pushed.

## File Structure

### Create in `WhiteChronos/arena-mcp-runtime`

```text
README.md
LICENSE
package.json
package-lock.json
plugin.json
mcp.json
.codex-plugin/plugin.json
.mcp.json
runtime-contract.json
provenance/source-lock.json

src/core/arena.mjs
src/core/tool-contract.mjs
src/mcp/create-arena-server.mjs
src/transports/stdio.mjs
src/transports/http.mjs

skills/github-arena/SKILL.md
skills/github-arena/agents/openai.yaml
skills/github-arena/references/upstream.md
skills/github-arena/references/chatgpt-adaptation.md
skills/github-arena/references/rubric.md
skills/github-arena/references/codex-global.md
skills/github-arena/scripts/arena_review.py
skills/github-arena/scripts/install_codex_global.py

scripts/generate-compat-manifests.mjs
scripts/healthcheck-stdio.mjs
scripts/healthcheck-http.mjs
scripts/package-skill.sh

tests/fixtures/legacy-tool-contract.json
tests/fixtures/legacy-golden-output.json
tests/contract/repository-contract.test.mjs
tests/contract/arena-core-parity.test.mjs
tests/contract/tool-contract.test.mjs
tests/contract/skill-package.test.mjs
tests/manifests/manifest-equivalence.test.mjs
tests/stdio/stdio-runtime.test.mjs
tests/http/http-runtime.test.mjs

.github/workflows/ci.yml
```

No root-level duplicate `SKILL.md` is created. The canonical Skill is only `skills/github-arena/`.

## Core Interfaces

### `src/core/arena.mjs`

```js
export function planArena({ agents }) {}
export function dealArenaCards({ agents, seed }) {}
export function getArenaRubric() {}
export function getArenaReviewChecklist({ highImpact, github }) {}
```

Required semantics:

- `agents` clamps to integer range 1..2160.
- `planArena({agents:16})` returns:
  - strategies 16
  - rounds 4
  - alive_per_round [16, 8, 4, 2, 1]
  - upstream_equivalent_calls 91
  - mode "review"
- card generation is deterministic for the same `agents` + `seed`.
- rubric is exactly the current 30/25/20/15/10 contract.
- checklist always starts with:
  - evidence-first
  - constraint-first
  - edge-cases-first
  - built-to-last
- GitHub checklist adds the current repository/provenance checks.

### `src/core/tool-contract.mjs`

```js
export const ARENA_TOOL_NAMES = [
  "arena_plan",
  "arena_cards",
  "arena_rubric",
  "arena_review_checklist",
];

export const ARENA_TOOL_DEFINITIONS = [];
```

The tool definitions must preserve current names, descriptions, JSON input schemas, and read-only/destructive/open-world annotations.

### `src/mcp/create-arena-server.mjs`

```js
export function createArenaMcpServer({ version = "1.2.0" } = {}) {}
```

Returns an MCP SDK server with the exact four tools registered over the shared core functions.

### `src/transports/stdio.mjs`

Executable entrypoint that connects `createArenaMcpServer()` to the official SDK stdio transport.

### `src/transports/http.mjs`

```js
export function createArenaHttpServer({
  host = "127.0.0.1",
  port = 8787,
  path = "/mcp",
} = {}) {}
```

Returns a Node HTTP server exposing Streamable HTTP MCP at `/mcp` plus a bounded `/healthz` endpoint.

No authentication is needed for local tests because the server exposes only deterministic read-only Arena logic. Production hosting/auth is a later plan.

## Review Focus

The five highest-risk failure classes for this slice are:

1. **Contract drift during extraction** — one of the four tool names/schemas/annotations or deterministic outputs changes; expected behavior: contract/golden tests fail.
2. **Duplicate transport registration** — stdio and HTTP are both declared active in the plugin package, creating duplicated tools; expected behavior: manifest-equivalence test fails.
3. **Portable/compatibility manifest divergence** — root manifests and Codex fallback disagree on name/version/server; expected behavior: generated compatibility diff fails CI.
4. **Skill becomes incomplete after extraction** — references/scripts referenced by `SKILL.md` are missing; expected behavior: Skill Creator validation/package test fails.
5. **HTTP lifecycle leak** — tests leave listening servers/sockets or accept paths other than the declared endpoint; expected behavior: HTTP test closes server deterministically and rejects unsupported routes.

---

### Task 1: Create the Independent Repository and Freeze Provenance

**Files:**
- Create repository: `WhiteChronos/arena-mcp-runtime`
- Create: `README.md`
- Create: `LICENSE`
- Create: `package.json`
- Create: `package-lock.json`
- Create: `runtime-contract.json`
- Create: `provenance/source-lock.json`
- Create: `tests/contract/repository-contract.test.mjs`

**Interfaces:**
- Consumes: approved Runtime Independente spec and the source snapshot `WhiteChronos/ChatGPT@ef3b5fd...`.
- Produces: independent repository identity, Node toolchain, source provenance, and runtime contract consumed by all later tasks.

- [ ] **Step 1: Create the GitHub repository with the exact settings in this plan**

Verify after creation:

```text
full_name = WhiteChronos/arena-mcp-runtime
private = false
default_branch = main
```

If the active harness cannot create repositories, stop with `USER_ACTION_REQUIRED` and use an authenticated GitHub admin surface; do not continue in a fake local substitute.

- [ ] **Step 2: Create the Node package skeleton only**

Create `package.json` with:

```json
{
  "name": "@whitechronos/arena-mcp-runtime",
  "version": "1.2.0",
  "private": true,
  "type": "module",
  "engines": {
    "node": ">=22 <23"
  },
  "scripts": {
    "test": "node --test tests/**/*.test.mjs"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "1.32.0",
    "zod": "3.25.76"
  }
}
```

Run `npm install --package-lock-only` to create a deterministic lockfile. Do not publish to npm in this plan.

- [ ] **Step 3: Write the failing repository-contract test**

The test must assert:

- package name/version/Node range;
- `runtime-contract.json.contract_version === "whitechronos-runtime/v1"`;
- `runtime-contract.json.component === "arena"`;
- plugin name is `github-arena`;
- four exact tool names;
- source lock points to the exact source repository/SHA/path/version;
- LICENSE exists and is MIT;
- provenance identifies `Jakeschincariol/arena-skill` as upstream inspiration/adaptation source.

- [ ] **Step 4: Run the repository-contract test and verify RED**

Run:

```bash
npm test -- --test-name-pattern="repository contract"
```

Expected: FAIL because runtime-contract/provenance are not complete yet.

- [ ] **Step 5: Implement runtime contract, source lock, README, and MIT license**

`provenance/source-lock.json` must include exactly:

```json
{
  "source_repository": "WhiteChronos/ChatGPT",
  "source_commit": "ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988",
  "source_path": "plugins/github-arena",
  "source_plugin_version": "1.1.0",
  "upstream_repository": "https://github.com/Jakeschincariol/arena-skill",
  "upstream_license": "MIT"
}
```

`runtime-contract.json` declares component `arena`, component version `1.2.0`, plugin `github-arena`, exact four-tool contract, supported transports `stdio` and `streamable-http`.

- [ ] **Step 6: Run the repository-contract test and verify GREEN**

Run:

```bash
npm test -- --test-name-pattern="repository contract"
```

Expected: PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add .
git commit -m "chore: bootstrap independent Arena runtime"
```

---

### Task 2: Extract the Arena Core with Golden Parity

**Files:**
- Create: `src/core/arena.mjs`
- Create: `tests/fixtures/legacy-golden-output.json`
- Create: `tests/contract/arena-core-parity.test.mjs`

**Interfaces:**
- Consumes: behavior frozen from `plugins/github-arena/mcp-server/mcp_server.mjs` at the source lock SHA.
- Produces: transport-neutral Arena functions used by both MCP adapters.

- [ ] **Step 1: Build the frozen golden fixture from the source snapshot**

Record representative legacy outputs for:

- `arena_plan`: agents 1, 4, 16, 17, 2160, 0, 2161;
- `arena_cards`: agents 4, seed 7 and seed "7";
- `arena_rubric`;
- `arena_review_checklist`: all four combinations of `highImpact` and `github`.

The fixture is evidence from the source snapshot; do not compute expected values by calling the new core.

- [ ] **Step 2: Write the failing parity tests**

Tests call:

```js
planArena()
dealArenaCards()
getArenaRubric()
getArenaReviewChecklist()
```

and deep-compare against the frozen fixture.

Also assert deterministic repeated card generation for the same inputs.

- [ ] **Step 3: Run parity tests and verify RED**

Run:

```bash
node --test tests/contract/arena-core-parity.test.mjs
```

Expected: FAIL because the new core does not exist.

- [ ] **Step 4: Implement the minimal transport-neutral core**

Move only deterministic Arena calculation behavior from the source snapshot.

Do not add GitHub access, subprocess execution, network calls, filesystem mutation, or subagent spawning.

- [ ] **Step 5: Run parity tests and verify GREEN**

Expected: all golden cases PASS.

- [ ] **Step 6: Commit Task 2**

```bash
git add src/core/arena.mjs tests/fixtures/legacy-golden-output.json tests/contract/arena-core-parity.test.mjs
git commit -m "feat: extract Arena core with golden parity"
```

---

### Task 3: Freeze the Exact Four-Tool Contract

**Files:**
- Create: `src/core/tool-contract.mjs`
- Create: `tests/fixtures/legacy-tool-contract.json`
- Create: `tests/contract/tool-contract.test.mjs`

**Interfaces:**
- Consumes: current MCP tool definitions at the source lock SHA.
- Produces: one canonical `ARENA_TOOL_DEFINITIONS` array for all transports.

- [ ] **Step 1: Freeze the current tool definitions into the fixture**

Capture exact:

- name;
- description;
- inputSchema;
- annotations.

Do not include implementation handlers in the fixture.

- [ ] **Step 2: Write failing contract tests**

Assert:

```js
ARENA_TOOL_NAMES.deepEqual([
  "arena_plan",
  "arena_cards",
  "arena_rubric",
  "arena_review_checklist",
])
```

and deep-equality of definitions against the source fixture.

Additionally assert every tool:

```text
readOnlyHint = true
destructiveHint = false
openWorldHint = false
```

- [ ] **Step 3: Run and verify RED**

Run:

```bash
node --test tests/contract/tool-contract.test.mjs
```

- [ ] **Step 4: Implement the canonical tool contract**

The core contract module contains definitions only; handlers remain in the MCP server factory.

- [ ] **Step 5: Run and verify GREEN**

Expected: exact four-tool parity PASS.

- [ ] **Step 6: Commit Task 3**

```bash
git add src/core/tool-contract.mjs tests/fixtures/legacy-tool-contract.json tests/contract/tool-contract.test.mjs
git commit -m "feat: freeze Arena MCP tool contract"
```

---

### Task 4: Migrate and Validate the Self-Contained GitHub Arena Skill

**Files:**
- Create: `skills/github-arena/SKILL.md`
- Create: `skills/github-arena/agents/openai.yaml`
- Create: `skills/github-arena/references/upstream.md`
- Create: `skills/github-arena/references/chatgpt-adaptation.md`
- Create: `skills/github-arena/references/rubric.md`
- Create: `skills/github-arena/references/codex-global.md`
- Create: `skills/github-arena/scripts/arena_review.py`
- Create: `skills/github-arena/scripts/install_codex_global.py`
- Create: `tests/contract/skill-package.test.mjs`

**Interfaces:**
- Consumes: existing GitHub Arena Skill content and the installed `skill-creator` validation/packaging workflow.
- Produces: one self-contained Skill directory that can be packaged independently of `WhiteChronos/ChatGPT`.

- [ ] **Step 1: Invoke the installed Skill Creator for the update/migration path**

Because `github-arena` already exists, do **not** initialize a brand-new skill template.

Use Skill Creator as an update: preserve the existing name/frontmatter semantics and build a complete self-contained directory.

- [ ] **Step 2: Write the failing Skill package test**

Assert:

- only one canonical `SKILL.md` exists under the plugin skill tree;
- all references/scripts linked from `SKILL.md` exist;
- `agents/openai.yaml` exists;
- frontmatter name is exactly `github-arena`;
- no reference points back to `WhiteChronos/ChatGPT/plugins/github-arena/` as a required runtime path;
- Skill instructions still prohibit claiming independent agents when none ran.

- [ ] **Step 3: Run and verify RED**

Run:

```bash
node --test tests/contract/skill-package.test.mjs
```

- [ ] **Step 4: Migrate the Skill and supporting resources**

Use the existing content as the behavioral baseline.

Update provenance/homepage links to the independent repository where appropriate while retaining upstream attribution.

Keep `SKILL.md` under 500 lines; detailed provenance and runtime notes stay in references.

- [ ] **Step 5: Validate and package using Skill Creator**

Run the active Skill Creator validator/package script against:

```text
skills/github-arena
```

Requirements:

- validation PASS;
- package filename exactly `skill.zip`;
- archive <=25 MB;
- ZIP stored outside the Git worktree or under ignored build output;
- ZIP not committed.

- [ ] **Step 6: Run Skill package test and verify GREEN**

- [ ] **Step 7: Commit Task 4**

```bash
git add skills/github-arena tests/contract/skill-package.test.mjs
git commit -m "feat: migrate self-contained GitHub Arena skill"
```

---

### Task 5: Add Portable Plugin Manifests and Generated Codex Compatibility

**Files:**
- Create: `plugin.json`
- Create: `mcp.json`
- Create: `scripts/generate-compat-manifests.mjs`
- Create/generated: `.codex-plugin/plugin.json`
- Create/generated: `.mcp.json`
- Create: `tests/manifests/manifest-equivalence.test.mjs`

**Interfaces:**
- Consumes: runtime identity, version 1.2.0, stdio entrypoint path.
- Produces: portable plugin package plus deterministic compatibility artifacts.

- [ ] **Step 1: Write failing manifest-equivalence tests**

Assert:

- root `plugin.json` uses Agent Plugins schema `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`;
- name `github-arena`, version `1.2.0`, license `MIT`;
- repository URL points to `WhiteChronos/arena-mcp-runtime`;
- root `mcp.json` declares exactly one active server named `github_arena`;
- active portable transport for this slice is stdio/local package execution;
- generated compatibility manifest references `./.mcp.json`;
- generated `.mcp.json` resolves to the same stdio entrypoint;
- neither portable nor compatibility package activates the HTTP adapter;
- running the generator with a clean tree produces byte-identical compatibility files.

- [ ] **Step 2: Run and verify RED**

- [ ] **Step 3: Implement portable manifests**

Portable root metadata is canonical.

Do not copy the existing compatibility manifest and then edit both manually.

- [ ] **Step 4: Implement `generate-compat-manifests.mjs`**

```js
export function generateCompatibilityManifests({
  pluginManifestPath,
  portableMcpPath,
  outputRoot,
}) {}
```

The generator must fail closed if the portable package contains more than the one approved active Arena server.

- [ ] **Step 5: Generate compatibility manifests and run tests**

Expected: PASS and zero generated diff on a second run.

- [ ] **Step 6: Commit Task 5**

```bash
git add plugin.json mcp.json .codex-plugin/plugin.json .mcp.json scripts/generate-compat-manifests.mjs tests/manifests/manifest-equivalence.test.mjs
git commit -m "feat: add portable Arena plugin manifests"
```

---

### Task 6: Implement the SDK-Based stdio MCP Runtime

**Files:**
- Create: `src/mcp/create-arena-server.mjs`
- Create: `src/transports/stdio.mjs`
- Create: `scripts/healthcheck-stdio.mjs`
- Create: `tests/stdio/stdio-runtime.test.mjs`

**Interfaces:**
- Consumes: `ARENA_TOOL_DEFINITIONS` and core functions.
- Produces: the canonical local MCP runtime registered by the plugin package.

- [ ] **Step 1: Write failing stdio runtime tests**

Spawn:

```text
node src/transports/stdio.mjs
```

and verify MCP lifecycle:

1. initialize;
2. notifications/initialized;
3. tools/list;
4. one benign call to each tool;
5. clean shutdown.

Assertions:

- server name `github-arena`;
- version `1.2.0`;
- exact four tools in exact order;
- tool outputs equal golden core results;
- unknown tool returns MCP error/result error without process crash;
- no stderr secret/environment dump;
- child exits after test termination.

- [ ] **Step 2: Run and verify RED**

- [ ] **Step 3: Implement `createArenaMcpServer()` with the official MCP SDK**

Use `@modelcontextprotocol/sdk@1.32.0`.

Handlers call only transport-neutral core functions.

- [ ] **Step 4: Implement stdio entrypoint**

Use the SDK stdio transport; no custom line protocol remains canonical after this task.

- [ ] **Step 5: Implement stdio healthcheck**

Healthcheck performs initialize + tools/list only.

It must never invoke GitHub, network mutation, filesystem mutation, or agent spawning.

- [ ] **Step 6: Run stdio tests and verify GREEN**

- [ ] **Step 7: Commit Task 6**

```bash
git add src/mcp src/transports/stdio.mjs scripts/healthcheck-stdio.mjs tests/stdio
git commit -m "feat: add independent Arena stdio MCP runtime"
```

---

### Task 7: Add a Deployment-Neutral Streamable HTTP Adapter

**Files:**
- Create: `src/transports/http.mjs`
- Create: `scripts/healthcheck-http.mjs`
- Create: `tests/http/http-runtime.test.mjs`

**Interfaces:**
- Consumes: `createArenaMcpServer()`.
- Produces: local Streamable HTTP server for future remote deployment, without activating it in the plugin package.

- [ ] **Step 1: Write failing HTTP tests**

Start on host `127.0.0.1`, port `0` so the OS assigns a free test port.

Verify:

- `GET /healthz` returns 200 with component/version/transport only;
- MCP endpoint is exactly `/mcp`;
- initialize succeeds over Streamable HTTP;
- tools/list returns exact four tools;
- representative tool calls match stdio/golden output;
- unsupported route returns 404;
- server closes cleanly after each test;
- no global listener survives the test.

- [ ] **Step 2: Run and verify RED**

- [ ] **Step 3: Implement the HTTP adapter using the official Streamable HTTP transport**

Do not add Express or another web framework; Node HTTP + official MCP transport is sufficient.

Default runtime options:

```text
host = 127.0.0.1
port = 8787
path = /mcp
health = /healthz
```

- [ ] **Step 4: Implement the HTTP healthcheck**

It starts or connects to a local test endpoint and verifies initialize + tools/list.

No public deployment.

- [ ] **Step 5: Run HTTP and full contract tests**

Expected: PASS.

- [ ] **Step 6: Commit Task 7**

```bash
git add src/transports/http.mjs scripts/healthcheck-http.mjs tests/http
git commit -m "feat: add Arena streamable HTTP adapter"
```

---

### Task 8: Independent CI, Packaging, and Whole-Repository Verification

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify if needed: `README.md`
- Modify if needed: package scripts only for deterministic verification.

**Interfaces:**
- Consumes: all prior tasks.
- Produces: independent evidence that `arena-mcp-runtime` is release-ready without consumer migration.

- [ ] **Step 1: Write a failing CI contract test or repository assertion**

Require CI to execute:

```bash
npm ci
npm test
node scripts/generate-compat-manifests.mjs --check
node scripts/healthcheck-stdio.mjs
node scripts/healthcheck-http.mjs
```

and Skill validation/package check.

CI must not:

- deploy HTTP;
- mutate `WhiteChronos/ChatGPT`;
- create credentials;
- claim host discovery;
- claim independent subagents ran.

- [ ] **Step 2: Add GitHub Actions workflow**

Use Node.js 22.

Permissions: `contents: read` for ordinary CI.

Run dependency install from the committed lockfile.

- [ ] **Step 3: Run the full local suite**

```bash
npm ci
npm test
node scripts/generate-compat-manifests.mjs --check
node scripts/healthcheck-stdio.mjs
node scripts/healthcheck-http.mjs
```

Expected: all PASS.

- [ ] **Step 4: Re-run Skill Creator validation/package**

Confirm `skill.zip` is valid and outside Git tracking.

- [ ] **Step 5: Apply Review Arena to the whole branch**

Review at minimum:

- contract parity;
- supply-chain/provenance correctness;
- portable/compatibility manifest drift;
- transport duplication;
- process/socket cleanup;
- no GitHub mutation surface;
- no subagent runtime claims;
- no secrets/environment leakage.

Any verified defect enters a new RED/GREEN cycle.

- [ ] **Step 6: Open PR to `WhiteChronos/arena-mcp-runtime:main`**

PR summary must state:

- source lock SHA;
- four-tool parity;
- portable + compatibility package;
- stdio active transport;
- HTTP adapter tested but not deployed/activated;
- Skill validation;
- CI evidence.

- [ ] **Step 7: Wait for PR CI and verify all checks green**

Do not merge on failing or pending required checks.

- [ ] **Step 8: Commit any final CI-only adjustment through TDD and re-run**

No direct-to-main fixes.

---

## Post-Merge Handoff — Not Part of This Plan

After the Arena Independent Runtime PR is merged and `main` is green:

1. record the independent repository main SHA;
2. create/tag `v1.2.0` only after final CI is green and release ownership is verified;
3. record the tag + immutable SHA for the future Runtime Marketplace;
4. do **not** switch `WhiteChronos/ChatGPT` to the new source yet;
5. proceed to the next approved plan: **Broker Independent Runtime**.

The later consumer-migration plan will run shadow contract checks between:

```text
WhiteChronos/ChatGPT/plugins/github-arena
and
WhiteChronos/arena-mcp-runtime
```

before changing the consumer marketplace source.

A fresh Codex/ChatGPT session and host-discovery proof happen only after the Runtime Marketplace and consumer migration are implemented.
