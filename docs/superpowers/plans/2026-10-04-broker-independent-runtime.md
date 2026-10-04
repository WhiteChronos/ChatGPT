# Broker Independent Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `WhiteChronos/subagent-broker-runtime` as the independent canonical home of the WhiteChronos Subagent Broker, preserving the exact eight-tool/lifecycle/security contract while making the consumer repository binding explicit and safe outside `WhiteChronos/ChatGPT`.

**Architecture:** Extract the current Broker from `WhiteChronos/ChatGPT@ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988` into a public MIT repository. Keep the Broker local-first and stdio-only, run it with the official MCP SDK, preserve Codex CLI process/worktree/state behavior, and require `SUBAGENT_BROKER_REPO_ROOT` so an independently installed plugin cannot accidentally treat its own plugin directory as the consumer repository.

**Tech Stack:** Node.js 22, ECMAScript modules, Node built-in test runner, `@modelcontextprotocol/sdk@1.32.0`, `zod@3.25.76`, Git CLI, Linux `/proc` process identity, Codex CLI, portable Agent Plugins manifests, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-03-runtime-independent-architecture-design.md`

## Global Constraints

- New repository: `WhiteChronos/subagent-broker-runtime`.
- Repository visibility: **public**.
- Default branch: **main**.
- License: **MIT**.
- Canonical plugin ID remains `subagent-broker`.
- Source extraction baseline: `WhiteChronos/ChatGPT@ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988`, path `plugins/subagent-broker/`, plugin version `1.0.0`.
- Initial independent-runtime release version: **1.1.0**.
- Initial supported runtime platform: **trusted Linux Codex remote/network workspace**.
- Preserve exact Broker tool names:
  - `subagent_spawn`
  - `subagent_status`
  - `subagent_wait`
  - `subagent_result`
  - `subagent_followup`
  - `subagent_list`
  - `subagent_cancel`
  - `subagent_cleanup`
- Preserve exact lifecycle states:
  - `QUEUED`
  - `SPAWNING`
  - `RUNNING`
  - `COMPLETED`
  - `FAILED`
  - `TIMED_OUT`
  - `CANCEL_REQUESTED`
  - `CANCELLED`
  - `ORPHANED`
- Preserve terminal states exactly: `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCELLED`, `ORPHANED`.
- `COMPLETED -> SPAWNING` remains legal **only** when transition reason is `followup`.
- Preserve roles exactly: `implementer`, `reviewer`, `researcher`, `tester`, `security-reviewer`.
- Preserve workspace modes exactly: `read_only`, `worktree_write`.
- Preserve priorities exactly: `normal`, `high`.
- Preserve defaults: `maxRunning=3`, `maxQueued=32`, `defaultTimeoutSeconds=1800`, `cancelGraceSeconds=10`, `rehydratedCheckMs=1000`.
- Preserve constructor bounds: `maxRunning 1..8`, `maxQueued 0..32`.
- Preserve spawn timeout bounds: `1..86400` seconds.
- Preserve wait timeout bounds: `1000..600000` ms.
- Preserve state directory: `<consumer repo>/.superpowers/subagents/`.
- Preserve worktree namespace: `<consumer repo>/.worktrees/subagents/`.
- Write-capable children never write directly to `main` or the parent task branch.
- Preserve directory mode `0700` and private state/result/prompt/log file mode `0600` where supported.
- Preserve child environment allowlist and secret redaction semantics.
- Preserve PID reuse protection using Linux process identity `pid + /proc/<pid>/stat start_ticks`.
- Preserve process-group cancellation: SIGTERM, grace period, then SIGKILL when identity still matches.
- Preserve restart reconciliation: missing/mismatched process identity becomes `ORPHANED`, never falsely `RUNNING`.
- Preserve native-first routing in the Skill: native Codex multi-agent → Broker → Superpowers inline fallback.
- Never publish or emulate native hosted tools such as `spawn_agent`, `wait_agent`, or `send_message`.
- Do not add Streamable HTTP in this plan.
- Do not deploy public infrastructure in this plan.
- Do not publish to the universal ChatGPT/Codex plugin directory in this plan; this local stdio runtime is for later Git-backed Runtime Marketplace consumption.
- Use root `plugin.json` and `mcp.json` as portable source manifests.
- Generate/validate `.codex-plugin/plugin.json` and `.mcp.json` as compatibility artifacts; do not hand-maintain divergent definitions.
- Portable and compatibility MCP packages declare exactly one active server: `subagent_broker`, type `stdio`.
- Independent runtime requires explicit consumer binding through `SUBAGENT_BROKER_REPO_ROOT`.
- `SUBAGENT_BROKER_REPO_ROOT` must be an absolute path and must resolve to a valid Git repository root. Missing/invalid binding fails closed; the runtime must never silently substitute the plugin repository.
- `SUBAGENT_BROKER_CODEX_PATH` remains optional and defaults to `codex`.
- The later Runtime Marketplace/bootstrap plan owns exporting `SUBAGENT_BROKER_REPO_ROOT=$REPO_ROOT` before launching a fresh Codex session.
- Do not modify `WhiteChronos/ChatGPT` consumer marketplace/config in this plan.
- Do not delete or weaken the current in-repo Broker implementation.
- Do not rerun historical implementation/TDD/PR/CI solely because code is extracted.
- Preserve the existing real smoke criteria unchanged.
- CI must use fake Codex/local fixtures and must never set `SUBAGENT_BROKER_LIVE=1`.
- CI must never claim host discovery, live Codex child execution, or independent reviewer evidence.
- The real smoke remains explicitly post-merge/post-install in a fresh trusted runtime.
- Because the `subagent-broker` Skill is being migrated/updated, implementation must invoke the installed `skill-creator`, validate the self-contained Skill, and package it as exactly `skill.zip`; the ZIP stays outside Git tracking.
- No credentials, API keys, raw sensitive traces, or real child prompts/results are committed.
- If current tooling cannot create the repository, stop at repository creation with `USER_ACTION_REQUIRED`; never simulate it as a subdirectory of `WhiteChronos/ChatGPT`.

## Repository Settings

Create:

```text
owner              WhiteChronos
name               subagent-broker-runtime
visibility         public
default branch     main
issues             enabled
wiki               disabled
projects           disabled
license            MIT
description        Independent native-first fallback runtime for isolated Codex subagents.
```

## Independent Runtime Boundary

The original Broker lived inside the consumer repository and discovered that repository through the plugin path. The independent runtime cannot rely on that coupling.

The new startup contract is:

```text
SUBAGENT_BROKER_REPO_ROOT
        ↓
resolve real absolute path
        ↓
git rev-parse --show-toplevel
        ↓
canonical consumer repo root
        ↓
state/worktrees/child cwd
```

If the variable is absent, relative, nonexistent, or not a Git repository, startup fails with a deterministic configuration error before any child process or worktree can be created.

Explicitly pointing `SUBAGENT_BROKER_REPO_ROOT` at the Broker repository itself is allowed for controlled development/smoke use; **implicit fallback to it is forbidden**.

## File Structure

### Create in `WhiteChronos/subagent-broker-runtime`

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

roles/
├── implementer.md
├── reviewer.md
├── researcher.md
├── tester.md
└── security-reviewer.md

src/
├── broker/
│   ├── broker.mjs
│   └── protocol.mjs
├── codex-cli/
│   └── codex-cli-backend.mjs
├── git-isolation/
│   ├── worktree-manager.mjs
│   └── process-identity.mjs
├── state/
│   └── state-store.mjs
├── security/
│   └── redaction.mjs
├── runtime/
│   └── consumer-repo.mjs
├── mcp/
│   ├── tool-contract.mjs
│   └── create-broker-server.mjs
└── transports/
    └── stdio.mjs

skills/subagent-broker/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── lifecycle.md
    ├── routing.md
    ├── security.md
    └── superpowers-sdd.md

scripts/
├── generate-compat-manifests.mjs
├── healthcheck-stdio.mjs
├── smoke_real_codex.mjs
└── check-skill-package.mjs

tests/
├── contract/
│   ├── repository-contract.test.mjs
│   ├── tool-contract.test.mjs
│   ├── protocol-parity.test.mjs
│   ├── skill-package.test.mjs
│   ├── manifest-equivalence.test.mjs
│   ├── consumer-binding.test.mjs
│   └── ci-contract.test.mjs
├── lifecycle/
│   ├── state-store.test.mjs
│   ├── broker.test.mjs
│   └── broker-failure.test.mjs
├── isolation/
│   ├── worktree.test.mjs
│   └── process-identity.test.mjs
├── security/
│   └── redaction.test.mjs
├── codex/
│   ├── codex-backend.test.mjs
│   └── fake-codex.mjs
├── stdio/
│   └── stdio-runtime.test.mjs
└── smoke/
    └── smoke-contract.test.mjs

.github/workflows/ci.yml
```

## Core Interfaces

### `src/runtime/consumer-repo.mjs`

```js
export async function resolveConsumerRepoRoot({
  configuredRoot = process.env.SUBAGENT_BROKER_REPO_ROOT,
} = {}) {}
```

Required behavior:

- configured root must be a nonblank absolute path;
- canonicalize with realpath;
- run `git rev-parse --show-toplevel` with `shell:false`;
- return canonical Git toplevel;
- reject missing/relative/non-Git paths with a Broker configuration error;
- never fall back to `process.cwd()` or `PLUGIN_ROOT`.

### `src/broker/protocol.mjs`

Exports:

```js
AGENT_STATES
TERMINAL_STATES
canTransition(from, to)
assertTransition(from, to, reason)
brokerError(code, message, details)
validateSpawnArgs(value)
validateStatusArgs(value)
validateWaitArgs(value)
validateResultArgs(value)
validateFollowupArgs(value)
validateListArgs(value)
validateCancelArgs(value)
validateCleanupArgs(value)
```

Behavior remains source-parity with plugin v1.0.0.

### `src/state/state-store.mjs`

```js
export class StateStore {
  constructor(root)
  agentDir(agentId)
  statePath(agentId)
  async create(record)
  async get(agentId)
  async update(agentId, patch, nextState, reason)
  async list(filter)
  async writePrompt(id, text)
  async readPrompt(id)
  async appendEvent(id, line)
  async appendStderr(id, text)
  async writeResult(id, result, finalText)
  async readResult(id)
  async reconcileNonterminal(processProbe)
}
```

### `src/codex-cli/codex-cli-backend.mjs`

```js
export class CodexCliBackend {
  constructor({ codexPath, stateStore, parentEnv, processProbe })
  async probe({ refresh } = {})
  spawn(spec)
  async followup(handle, message)
  async cancel(handle, { graceSeconds } = {})
}
```

Probe contract remains:

```text
version
exec
json
resume
sandboxReadOnly
sandboxWorkspaceWrite
approvalNever
```

### `src/broker/broker.mjs`

```js
export class SubagentBroker {
  constructor(options)
  async start()
  async spawn(args)
  async status(agentId)
  async wait(agentId, timeoutMs)
  async result(agentId)
  async followup(agentId, message)
  async list(filter)
  async cancel(agentId)
  async cleanup(agentId, options)
  async shutdown()
}
```

### `src/mcp/tool-contract.mjs`

Exports:

```js
export const BROKER_TOOL_NAMES = [
  "subagent_spawn",
  "subagent_status",
  "subagent_wait",
  "subagent_result",
  "subagent_followup",
  "subagent_list",
  "subagent_cancel",
  "subagent_cleanup",
];

export const BROKER_TOOL_DEFINITIONS = [];
```

Definitions preserve the exact source descriptions, JSON input schemas, order, and annotations.

### `src/mcp/create-broker-server.mjs`

```js
export async function createBrokerMcpServer({
  repoRoot,
  codexPath = process.env.SUBAGENT_BROKER_CODEX_PATH || "codex",
  parentEnv = process.env,
} = {}) {}
```

It:

1. receives an already validated consumer repo root;
2. creates `StateStore(<repo>/.superpowers/subagents)`;
3. creates `CodexCliBackend`;
4. creates/starts `SubagentBroker`;
5. registers exact eight tools with the official MCP SDK;
6. returns `{ server, broker }` so stdio shutdown can stop Broker cleanly.

## Exact Tool Annotation Contract

Preserve current annotations:

| Tool | readOnlyHint | destructiveHint | idempotentHint | openWorldHint |
| --- | --- | --- | --- | --- |
| `subagent_spawn` | false | false | false | false |
| `subagent_status` | true | false | true | false |
| `subagent_wait` | true | false | true | false |
| `subagent_result` | true | false | true | false |
| `subagent_followup` | false | false | false | false |
| `subagent_list` | true | false | true | false |
| `subagent_cancel` | false | true | false | false |
| `subagent_cleanup` | false | true | false | false |

Tool success envelope preserves:

```json
{
  "content": [{"type": "text", "text": "<JSON string>"}],
  "structuredContent": {},
  "isError": false
}
```

Compatibility note: source v1.0.0 omitted `isError` on success. The independent SDK adapter may omit it or return explicit `false`; tests must treat both as success but must require `structuredContent` parity.

Tool errors preserve structured payload:

```json
{
  "code": "BROKER_ERROR_CODE",
  "message": "message",
  "details": null
}
```

with MCP tool result `isError: true`.

## Review Focus

The five highest-risk failure classes are:

1. **Wrong consumer repository** — independent plugin starts from its own install/cache directory and mutates the wrong repository; expected behavior: missing/invalid `SUBAGENT_BROKER_REPO_ROOT` fails closed before state/worktree creation.
2. **PID reuse / cancellation containment** — stale PID could terminate an unrelated process; expected behavior: recorded Linux process identity must match before cancellation, otherwise `PROCESS_IDENTITY_MISMATCH` / `ORPHANED`.
3. **Dirty worktree cleanup** — cleanup could destroy uncommitted child work; expected behavior: dirty worktree cleanup refuses and retains branch/worktree.
4. **Secret leakage** — parent environment or stderr/events could expose credentials; expected behavior: child env is allowlisted and sensitive values are redacted before persistence/results.
5. **False live-agent proof** — fake Codex/CI could be described as real subagent execution; expected behavior: CI never sets live flag, smoke stays opt-in, and live evidence is post-merge only.

---

### Task 1: Create Independent Repository, Toolchain, and Provenance

**Files:**
- Create repository: `WhiteChronos/subagent-broker-runtime`
- Create: `README.md`
- Create: `LICENSE`
- Create: `package.json`
- Create: `package-lock.json`
- Create: `runtime-contract.json`
- Create: `provenance/source-lock.json`
- Test: `tests/contract/repository-contract.test.mjs`

**Interfaces:**
- Consumes: approved Runtime Independente spec and source snapshot `WhiteChronos/ChatGPT@ef3b5fd...`.
- Produces: independent repository identity/version/provenance consumed by all later tasks.

- [ ] **Step 1: Create GitHub repository with exact settings above**

Verify:

```text
full_name = WhiteChronos/subagent-broker-runtime
private = false
default_branch = main
```

- [ ] **Step 2: Create Node package skeleton**

`package.json`:

```json
{
  "name": "@whitechronos/subagent-broker-runtime",
  "version": "1.1.0",
  "private": true,
  "type": "module",
  "engines": {"node": ">=22 <23"},
  "scripts": {"test": "node --test"},
  "dependencies": {
    "@modelcontextprotocol/sdk": "1.32.0",
    "zod": "3.25.76"
  }
}
```

Generate a real lockfile with `npm install --package-lock-only`. If local registry access is unavailable, use a temporary GitHub Actions dependency-bootstrap workflow exactly as with Arena, commit the real lockfile, then remove the bootstrap workflow before final CI.

- [ ] **Step 3: Write failing repository-contract test**

Assert:

- package identity/version/Node range;
- `component === "broker"`;
- `component_version === "1.1.0"`;
- plugin `subagent-broker`;
- supported transport is exactly `["stdio"]`;
- required host capabilities include `git`, `codex-cli`, `linux-process-identity`, and explicit consumer repo binding;
- tool contract lists exactly eight names in order;
- source lock:
  - repository `WhiteChronos/ChatGPT`;
  - commit `ef3b5fd77ab96dc3c0950725cd6f5c57b49a8988`;
  - path `plugins/subagent-broker`;
  - source plugin version `1.0.0`;
- LICENSE is MIT.

- [ ] **Step 4: Run RED**

```bash
node --test tests/contract/repository-contract.test.mjs
```

Expected: FAIL until runtime contract/provenance exist.

- [ ] **Step 5: Implement minimum repository contract/provenance/README/license**

README must state:

- native-first fallback;
- Linux v1 scope;
- `SUBAGENT_BROKER_REPO_ROOT` required;
- stdio-only;
- no hosted billing/API-key creation;
- no live-proof claim from CI.

- [ ] **Step 6: Run GREEN and full current tests**

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: bootstrap independent Subagent Broker runtime"
```

---

### Task 2: Freeze Protocol, Lifecycle, Roles, and Eight-Tool Contract

**Files:**
- Create: `src/broker/protocol.mjs`
- Create: `src/mcp/tool-contract.mjs`
- Create: `roles/*.md`
- Create: `tests/fixtures/legacy-tool-contract.json`
- Create: `tests/fixtures/legacy-protocol-contract.json`
- Test: `tests/contract/tool-contract.test.mjs`
- Test: `tests/contract/protocol-parity.test.mjs`

**Interfaces:**
- Consumes: source `protocol.mjs`, `mcp_server.mjs`, and role files.
- Produces: canonical validation/lifecycle/tool definitions for later Broker/MCP tasks.

- [ ] **Step 1: Freeze source tool contract fixture**

Capture exact:

- eight names/order;
- descriptions;
- input schemas;
- annotations.

- [ ] **Step 2: Freeze protocol fixture**

Capture:

- all states and terminal states;
- legal normal transitions;
- follow-up exception;
- exact roles/modes/priorities;
- timeout/default/boundary values.

- [ ] **Step 3: Write RED contract tests**

Required assertions include:

```text
spawn default timeout = 1800
spawn default priority = normal
spawn timeout 1..86400
wait timeout 1000..600000
unknown spawn fields rejected
base_ref rejects NUL/CR/LF
agent_id pattern = ^sa_[A-Za-z0-9_-]+$
```

- [ ] **Step 4: Implement protocol/tool definitions by extraction, not redesign**

- [ ] **Step 5: Copy roles with content parity and test all five files exist**

- [ ] **Step 6: Run GREEN**

- [ ] **Step 7: Commit**

```bash
git add src/broker src/mcp/tool-contract.mjs roles tests/fixtures tests/contract
git commit -m "feat: freeze Broker protocol and tool contract"
```

---

### Task 3: Add Explicit Consumer Repository Binding and Git Isolation

**Files:**
- Create: `src/runtime/consumer-repo.mjs`
- Create: `src/git-isolation/worktree-manager.mjs`
- Test: `tests/contract/consumer-binding.test.mjs`
- Test: `tests/isolation/worktree.test.mjs`

**Interfaces:**
- Consumes: `SUBAGENT_BROKER_REPO_ROOT`.
- Produces: canonical consumer Git root and isolated read/write workspaces for Broker.

- [ ] **Step 1: Write RED consumer-binding tests**

Test:

1. missing variable → deterministic configuration error;
2. blank → error;
3. relative path → error;
4. nonexistent absolute path → error;
5. absolute non-Git directory → error;
6. absolute subdirectory inside Git repo → returns canonical toplevel;
7. explicit Broker repo root is allowed;
8. function never falls back to process cwd when configured root missing.

- [ ] **Step 2: Run RED**

- [ ] **Step 3: Implement `resolveConsumerRepoRoot()`**

Use `realpath` and `git rev-parse --show-toplevel` with `shell:false`.

- [ ] **Step 4: Port worktree manager with path-safety parity**

Preserve:

```text
read_only       -> git worktree add --detach <path> <baseSha>
worktree_write  -> git worktree add -b subagent/<agentId> <path> <baseSha>
namespace       -> .worktrees/subagents/<agentId>
```

`resolveBase()` keeps `git rev-parse --verify --end-of-options <ref>^{commit}`.

- [ ] **Step 5: Write/port worktree tests**

Assert:

- read snapshot detached;
- write branch exact naming;
- base is exact 40-char SHA;
- out-of-namespace path rejected;
- dirty cleanup refuses;
- clean cleanup removes worktree;
- branch purge only when explicitly requested.

- [ ] **Step 6: Run GREEN**

- [ ] **Step 7: Commit**

```bash
git add src/runtime src/git-isolation tests/contract/consumer-binding.test.mjs tests/isolation
git commit -m "feat: bind Broker to explicit consumer repository"
```

---

### Task 4: Port Private State, Process Identity, and Secret Redaction

**Files:**
- Create: `src/state/state-store.mjs`
- Create: `src/git-isolation/process-identity.mjs`
- Create: `src/security/redaction.mjs`
- Test: `tests/lifecycle/state-store.test.mjs`
- Test: `tests/isolation/process-identity.test.mjs`
- Test: `tests/security/redaction.test.mjs`

**Interfaces:**
- Consumes: protocol lifecycle definitions and consumer repo state root.
- Produces: restart-safe private Broker state and safe process/secret primitives.

- [ ] **Step 1: Write/port RED state-store tests**

Assert:

- atomic state writes;
- transition history parity;
- result/prompt/event/stderr files;
- list ordering;
- directory/file privacy modes where supported;
- PID identity mismatch on restart → `ORPHANED`.

- [ ] **Step 2: Write RED process-identity tests**

On Linux:

- parse PID and `start_ticks`;
- same PID + same ticks → true;
- same PID + different ticks → false;
- missing process → null;
- process group termination uses negative PID;
- invalid PID rejected.

On non-Linux, runtime health must report `CAPABILITY_UNAVAILABLE`; do not claim Windows-native containment.

- [ ] **Step 3: Write RED redaction tests**

Preserve child env allowlist:

```text
PATH HOME LANG LC_ALL LC_CTYPE TMPDIR TMP TEMP USER LOGNAME SHELL TERM CODEX_HOME CODEX_ACCESS_TOKEN
```

Assert unlisted secrets are removed and inherited values whose names match `TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY|PRIVATE_KEY` are redacted from persisted stderr/result text.

- [ ] **Step 4: Implement extracted modules**

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add src/state src/git-isolation/process-identity.mjs src/security tests/lifecycle/state-store.test.mjs tests/isolation/process-identity.test.mjs tests/security
git commit -m "feat: preserve Broker state and containment security"
```

---

### Task 5: Port Codex CLI Backend with Fake-Codex Capability Evidence

**Files:**
- Create: `src/codex-cli/codex-cli-backend.mjs`
- Create: `tests/codex/fake-codex.mjs`
- Test: `tests/codex/codex-backend.test.mjs`

**Interfaces:**
- Consumes: StateStore, redaction, process identity.
- Produces: real independent `codex exec --json` process handles and capability probe.

- [ ] **Step 1: Write RED capability-probe tests**

Fake Codex must cover:

- `codex --version`;
- `codex exec --help`;
- `codex exec resume --help`.

Assert probe booleans exactly:

```text
exec
json
resume
sandboxReadOnly
sandboxWorkspaceWrite
approvalNever
```

- [ ] **Step 2: Write RED spawn/resume tests**

Assert:

- `shell:false`;
- `codex exec --json`;
- correct sandbox from workspace mode when supported;
- `--ask-for-approval never` when supported;
- prompt sent over stdin;
- independent PID exists;
- process identity captured;
- JSONL events persisted;
- session ID extracted from supported nested/direct forms;
- final agent text extracted;
- stderr is redacted before persistence;
- followup uses `exec resume <session> -` and preserves session ID.

- [ ] **Step 3: Write RED cancel tests**

Assert:

- missing PID → `CAPABILITY_UNAVAILABLE`;
- identity mismatch → `PROCESS_IDENTITY_MISMATCH`;
- matching identity → SIGTERM;
- still alive after grace → SIGKILL.

- [ ] **Step 4: Implement backend by parity extraction**

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add src/codex-cli tests/codex
git commit -m "feat: port Broker Codex CLI backend"
```

---

### Task 6: Port Stateful Broker Orchestration and Failure Semantics

**Files:**
- Create: `src/broker/broker.mjs`
- Test: `tests/lifecycle/broker.test.mjs`
- Test: `tests/lifecycle/broker-failure.test.mjs`

**Interfaces:**
- Consumes: protocol, StateStore, CodexCliBackend, worktree manager, roles.
- Produces: full Broker lifecycle methods used by MCP handlers.

- [ ] **Step 1: Write/port RED queue tests**

Prove:

- first 3 children run by default;
- fourth queues;
- completion drains next queued child;
- high-priority queue drains before normal queue;
- queue exhaustion returns `RESOURCE_EXHAUSTED`.

- [ ] **Step 2: Write/port RED lifecycle tests**

Prove:

- workspace created from exact `base_sha`;
- write child gets `subagent/<agentId>`;
- result includes commits/diff/worktree/session/PID evidence;
- `wait` returns terminal state or bounded timeout;
- list filtering uses exact state;
- cleanup only terminal children;
- dirty cleanup refusal propagates without deleting work.

- [ ] **Step 3: Preserve failure semantics**

Tests must prove:

- followup launch failure → `FAILED`, never stuck `SPAWNING`;
- followup process rejection → `FAILED`, never stuck `RUNNING`;
- containment failure during timeout → `ORPHANED`, not falsely `TIMED_OUT`;
- cancel queued child → `CANCELLED`;
- cancel running child requires proven containment;
- rehydrated stale child → `ORPHANED`.

- [ ] **Step 4: Implement Broker by extraction**

Do not redesign scheduler/state transitions in this slice.

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add src/broker/broker.mjs tests/lifecycle
git commit -m "feat: port stateful Subagent Broker orchestration"
```

---

### Task 7: Replace Manual MCP Loop with SDK-Based stdio Adapter

**Files:**
- Create: `src/mcp/create-broker-server.mjs`
- Create: `src/transports/stdio.mjs`
- Create: `scripts/healthcheck-stdio.mjs`
- Test: `tests/stdio/stdio-runtime.test.mjs`

**Interfaces:**
- Consumes: exact tool definitions, validated consumer repo root, Broker.
- Produces: canonical stdio MCP runtime for plugin loading.

- [ ] **Step 1: Write RED SDK stdio tests**

Use `Client + StdioClientTransport` from SDK 1.32.0.

Create a temporary fixture Git repository and launch server with:

```text
SUBAGENT_BROKER_REPO_ROOT=<fixture repo absolute path>
SUBAGENT_BROKER_CODEX_PATH=<fake-codex absolute path>
```

Assert initialize:

```text
server name = subagent-broker
server version = 1.1.0
```

and `tools/list` returns exact eight tools/order/schemas/annotations.

- [ ] **Step 2: Add configuration failure tests**

Launching without `SUBAGENT_BROKER_REPO_ROOT` must fail closed with a deterministic message and no `.superpowers/subagents` created in plugin root.

- [ ] **Step 3: Add benign MCP lifecycle call tests using fake Codex**

Through MCP, verify at least:

- `subagent_spawn`;
- `subagent_status`;
- `subagent_wait`;
- `subagent_result`;
- `subagent_list`;
- `subagent_cleanup`.

Use fake Codex only.

- [ ] **Step 4: Add tool error envelope tests**

Unknown tool:

```json
{"code":"UNKNOWN_TOOL","message":"unknown tool: ..."}
```

Validation/Broker errors preserve `code`, `message`, `details` and `isError:true`.

- [ ] **Step 5: Implement `createBrokerMcpServer()` with official MCP SDK**

Use low-level SDK server registration so frozen JSON schemas remain exact.

- [ ] **Step 6: Implement stdio entrypoint**

Startup order:

```text
resolveConsumerRepoRoot()
→ createBrokerMcpServer()
→ StdioServerTransport
→ connect
→ SIGINT/SIGTERM broker.shutdown()
```

- [ ] **Step 7: Implement stdio healthcheck**

Healthcheck creates a temporary Git fixture, sets explicit consumer binding and fake Codex, then performs **initialize + tools/list only**.

It never starts a real child.

- [ ] **Step 8: Run GREEN**

- [ ] **Step 9: Commit**

```bash
git add src/mcp src/transports scripts/healthcheck-stdio.mjs tests/stdio
git commit -m "feat: add independent Broker stdio MCP runtime"
```

---

### Task 8: Migrate Skill, Portable Manifests, and Plugin Packaging

**Files:**
- Create: `skills/subagent-broker/**`
- Create: `plugin.json`
- Create: `mcp.json`
- Create: `scripts/generate-compat-manifests.mjs`
- Create/generated: `.codex-plugin/plugin.json`
- Create/generated: `.mcp.json`
- Create: `scripts/check-skill-package.mjs`
- Test: `tests/contract/skill-package.test.mjs`
- Test: `tests/contract/manifest-equivalence.test.mjs`

**Interfaces:**
- Consumes: current Broker Skill and stdio entrypoint.
- Produces: self-contained Skill + portable/compatibility plugin package.

- [ ] **Step 1: Invoke installed Skill Creator for update/migration path**

Do not initialize a new unrelated Skill. Preserve name `subagent-broker`.

- [ ] **Step 2: Write RED Skill tests**

Assert Skill:

- native-first routing preserved;
- checks actual current tool list;
- Broker fallback second;
- inline fallback third;
- never labels personas as subagents;
- never allows write child directly on `main`;
- references all four supporting docs;
- contains no required path back to `WhiteChronos/ChatGPT/plugins/subagent-broker`.

- [ ] **Step 3: Migrate Skill/references and validate/package**

Skill Creator requirements:

- validation PASS;
- `skill.zip` exact filename;
- <=25 MB;
- ZIP outside worktree;
- ZIP not committed.

- [ ] **Step 4: Write RED manifest-equivalence tests**

Portable `plugin.json`:

```text
name = subagent-broker
version = 1.1.0
license = MIT
repository = https://github.com/WhiteChronos/subagent-broker-runtime
```

Portable `mcp.json` must declare exactly one server:

```json
{
  "subagent_broker": {
    "type": "stdio",
    "command": "node",
    "args": ["${PLUGIN_ROOT}/src/transports/stdio.mjs"],
    "cwd": "${PLUGIN_ROOT}",
    "env_vars": [
      "SUBAGENT_BROKER_REPO_ROOT",
      "SUBAGENT_BROKER_CODEX_PATH",
      "CODEX_HOME",
      "CODEX_ACCESS_TOKEN"
    ]
  }
}
```

If the current portable schema names the env pass-through field differently at implementation time, follow the authoritative schema and ledger the plan ruling; semantics above are binding.

Compatibility `.mcp.json` preserves type `stdio`, entrypoint, cwd, and env pass-through semantics.

- [ ] **Step 5: Implement deterministic compatibility generator**

Second generation must be byte-identical.

Fail closed if:

- server count != 1;
- server name != `subagent_broker`;
- transport != stdio;
- command != node;
- HTTP/URL appears.

- [ ] **Step 6: Run GREEN + Skill Creator validation/package**

- [ ] **Step 7: Commit**

```bash
git add skills plugin.json mcp.json .codex-plugin .mcp.json scripts/generate-compat-manifests.mjs scripts/check-skill-package.mjs tests/contract
git commit -m "feat: package independent Subagent Broker plugin"
```

---

### Task 9: Preserve Real Smoke Harness, Add Independent CI, Review, and PR

**Files:**
- Create: `scripts/smoke_real_codex.mjs`
- Create: `tests/smoke/smoke-contract.test.mjs`
- Create: `.github/workflows/ci.yml`
- Test: `tests/contract/ci-contract.test.mjs`
- Modify: `README.md` only for tested usage/limitations.

**Interfaces:**
- Consumes: complete independent Broker runtime.
- Produces: CI evidence and a preserved, opt-in real smoke for the later post-merge runtime proof.

- [ ] **Step 1: Port smoke harness without weakening criteria**

The independent harness must keep the current acceptance sequence:

1. require `SUBAGENT_BROKER_LIVE=1`;
2. require real `codex exec --json`;
3. spawn 2 simultaneous independent read children;
4. require distinct PIDs and distinct agent IDs;
5. persist distinct trace/event paths;
6. require both complete;
7. spawn isolated writer;
8. require branch/worktree/commit evidence;
9. if resume supported and session ID exists, follow-up must preserve session/worktree identity;
10. otherwise report truthful capability unavailable/unsupported;
11. spawn independent reviewer on exact writer snapshot;
12. spawn long child and cancel it to `CANCELLED`;
13. cleanup terminal children without deleting dirty work;
14. persist redacted summary evidence;
15. no secret values in summary.

- [ ] **Step 2: Bind live smoke explicitly to a consumer repo**

The harness must call `resolveConsumerRepoRoot()`; it never infers the plugin repo unless explicitly configured.

The operational command becomes:

```bash
SUBAGENT_BROKER_REPO_ROOT=/absolute/consumer/repo \
SUBAGENT_BROKER_LIVE=1 \
node scripts/smoke_real_codex.mjs
```

For controlled development, setting the consumer root to the Broker repo itself is allowed explicitly.

- [ ] **Step 3: Write smoke-contract RED/GREEN tests**

Without live flag:

```text
SKIPPED: Set SUBAGENT_BROKER_LIVE=1 ...
```

CI test must prove no ordinary workflow contains `SUBAGENT_BROKER_LIVE=1`.

- [ ] **Step 4: Add final CI workflow**

Required commands:

```bash
npm ci
npm test
node scripts/generate-compat-manifests.mjs --check
node scripts/healthcheck-stdio.mjs
node scripts/check-skill-package.mjs
```

CI permissions: `contents: read`.

CI must not:

- run real Codex model tasks;
- set live smoke flag;
- deploy infrastructure;
- mutate `WhiteChronos/ChatGPT`;
- claim host discovery;
- claim native multi-agent proof.

- [ ] **Step 5: Run complete local verification**

Expected all GREEN with fake Codex only.

- [ ] **Step 6: Re-run Skill Creator validation/package**

- [ ] **Step 7: Apply Review Arena whole-branch**

Review at minimum:

- consumer repo binding cannot fall back to plugin repo;
- exact eight-tool parity;
- lifecycle/queue parity;
- PID reuse containment;
- dirty-worktree cleanup refusal;
- secret/env redaction;
- state file privacy;
- followup/session parity;
- portable/compatibility manifest drift;
- no HTTP/runtime duplication;
- no live-smoke execution in CI;
- no `skill.zip`, `node_modules`, raw traces, or state directories committed.

Any Critical/Important finding gets one TDD RED→GREEN fix pass before PR.

- [ ] **Step 8: Open PR to `WhiteChronos/subagent-broker-runtime:main`**

PR must state:

- source lock SHA/plugin version;
- exact eight-tool parity;
- Linux/stdin stdio scope;
- explicit `SUBAGENT_BROKER_REPO_ROOT` contract;
- lifecycle/isolation/security parity;
- Skill validation;
- CI evidence;
- real smoke not run yet;
- consumer migration remains out of scope.

- [ ] **Step 9: Require PR CI SUCCESS**

Do not merge on pending/failing required checks.

---

## Post-Merge Handoff — Not Part of This Plan

After the Broker Independent Runtime PR is merged and `main` is green:

1. record Broker independent `main` SHA;
2. do not run the real smoke merely because extraction merged;
3. do not switch `WhiteChronos/ChatGPT` consumer source yet;
4. write/approve the next plan: **Native Runtime Verifier**;
5. later implement **Runtime Marketplace**;
6. later implement **WhiteChronos/ChatGPT Consumer Migration**;
7. only after a fresh runtime consumes the independent Broker and Runtime Doctor reports readiness, run the exact real smoke against the selected consumer repository.

The historical Task 12 gate remains pending until that real host/runtime proof succeeds. CI, fake Codex, source extraction, and merge do not close Task 12.

## Self-Review Checklist

Before implementation begins, verify this plan against the architecture spec:

- Broker is independent and stdio-only: covered Tasks 1, 7, 8.
- Exact 8-tool parity: covered Tasks 2 and 7.
- Lifecycle parity: covered Tasks 2, 4, 6.
- Git isolation parity: covered Task 3.
- Cancellation/PID safety: covered Tasks 4, 5, 6.
- Secret redaction: covered Tasks 4 and 9.
- Native-first policy: covered Task 8.
- Smoke criteria unchanged: covered Task 9.
- No live smoke in CI: covered Task 9.
- No consumer migration: global constraint + post-merge handoff.
- Portable manifests: covered Task 8.
- Independent CI: covered Task 9.
- Runtime-proof honesty: global constraint + Task 9.
