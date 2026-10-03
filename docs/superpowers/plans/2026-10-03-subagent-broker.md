# WhiteChronos Real Subagent Broker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a real, native-first subagent runtime that falls back to independent Codex CLI processes with isolated Git worktrees, persistent lifecycle state, MCP lifecycle tools, and truthful Superpowers SDD integration.

**Architecture:** A pure-Node stdio MCP plugin owns lifecycle orchestration while a `codex_cli` backend launches independent `codex exec --json` processes with `shell:false`. Focused modules separate state transitions, persistence/recovery, Git worktree isolation, CLI capability probing/session resume, queue scheduling, redaction, and MCP protocol handling. Native Codex multi-agent remains first choice; the broker is only the fallback when native spawn tools are absent.

**Tech Stack:** Node.js 22+ ESM and standard library only, `node:test`, Git CLI, Codex CLI, JSON-RPC/MCP stdio, TOML/JSON repository configuration, Linux process groups for v1 cancellation containment.

**Spec:** `docs/superpowers/specs/2026-10-03-subagent-broker-design.md`

## Global Constraints

- Initial deployment target is a trusted Codex remote/network workspace on Linux.
- `multi_agent = true` must remain enabled; its presence alone is never treated as proof that native spawn tools exist.
- Native Codex multi-agent tools are preferred when the actual current harness exposes them.
- Broker fallback is used only when native multi-agent tools are absent and the broker MCP is healthy.
- If neither native tools nor broker are available, use the official Superpowers inline fallback and state that independent subagents were unavailable.
- A real broker child must have a distinct OS process, independent Codex execution/session context, explicit task brief, stable `agent_id`, independent trace/result state, and isolated Git snapshot/worktree.
- The broker never accepts arbitrary shell commands, raw unrestricted Codex CLI arguments, arbitrary environment variables, or arbitrary caller-selected models through MCP.
- v1 workspace modes are exactly `read_only` and `worktree_write`; no MCP argument may expose `danger-full-access`.
- Read-only agents use detached isolated Git worktrees/snapshots; they do not review a mutable parent checkout.
- Write agents use branch `subagent/<agent_id>` and worktree `.worktrees/subagents/<agent_id>/`; they never write directly to `main` or the parent task branch.
- Default `max_concurrent_agents = 3`; minimum 1; hard ceiling 8.
- Default `max_queued_agents = 32`.
- Default `default_timeout_seconds = 1800`.
- Default `cancel_grace_seconds = 10`.
- `subagent_wait.timeout_ms` is bounded to 1,000–600,000.
- Lifecycle states are exactly `QUEUED`, `SPAWNING`, `RUNNING`, `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCEL_REQUESTED`, `CANCELLED`, and `ORPHANED`.
- Terminal states are exactly `COMPLETED`, `FAILED`, `TIMED_OUT`, `CANCELLED`, and `ORPHANED`.
- Illegal lifecycle transitions fail closed and are append-audited.
- `subagent_followup` must reuse the same recorded Codex session when resume is supported; it never silently creates a new unrelated session and calls it a follow-up.
- The current Codex CLI's actual `--help`/event output is authoritative over stale assumptions.
- The implementation supports the documented current non-interactive forms `codex exec --json ...` and `codex exec resume <session-id> <prompt>`, but live capability probing must confirm accepted flags/order before the broker advertises follow-up support.
- Child process launch uses an argument array and `shell:false`; task text is delivered on stdin, not interpolated into shell commands.
- Child environment is filtered to required OS execution variables plus explicitly supported Codex authentication/runtime variables; the full parent environment is never logged.
- Raw `events.jsonl` is sensitive local trace data: owner-only permissions where supported, never returned wholesale through MCP, never committed automatically.
- Runtime state lives under `.superpowers/subagents/` and worktrees under `.worktrees/subagents/`; both are ignored by Git.
- Cancellation/timeout targets only the attributable agent process/process-group; broad process-name killing is forbidden.
- Restart recovery may adopt a live process only when PID plus start-identity evidence match; otherwise nonterminal stale state becomes `ORPHANED`.
- Windows-native process-tree support is not a v1 acceptance criterion and must not be claimed as verified.
- No OpenAI API key creation, hosted Agents API billing setup, or `codex exec-server` deployment occurs in v1.
- The broker preserves Superpowers task briefs, report files, review packages, progress ledger, and fix-round semantics.
- GitHub Arena remains a review layer, not an agent runtime; Arena strategy counts never become claimed real child counts.
- Existing Superpowers, ECC, Matt Pocock, GitHub Arena, engineering governance, and Codex plugin configuration must remain intact.
- All repository CI/governance gates must pass before merge.
- Only after the real post-merge Codex smoke test demonstrates independent children may project documentation call the broker fallback "real subagents."
- Awesome LLM Apps implementation remains paused until the broker is merged and passes that real smoke test.

## Review Focus

- **PID reuse / restart recovery:** a stale state file with the same PID but different Linux process start identity must become `ORPHANED`, never attach to the unrelated process; Task 2 pins this.
- **Shell/environment injection:** hostile task text, base refs, and environment-shaped strings must remain data and must not become shell/CLI/env injection surfaces; Tasks 3, 4, and 8 pin this.
- **Resume identity:** follow-up must reuse the same session/worktree and must return `CAPABILITY_UNAVAILABLE` rather than fabricating continuity when resume is unavailable; Task 4 pins this.
- **Cancellation containment:** cancelling one agent with descendants must not kill another broker agent or unrelated process; Task 4 pins process-group ownership.
- **Mutable-review race:** reviewers must see an exact detached snapshot even while the parent branch changes; Task 3 pins this.

---

## File Structure

### Runtime protocol and lifecycle

- Create `plugins/subagent-broker/mcp-server/protocol.mjs` — lifecycle states, transition validation, tool argument validation, stable error codes, bounded result shaping.
- Create `plugins/subagent-broker/mcp-server/redaction.mjs` — minimal child environment construction and secret/text redaction.
- Create `plugins/subagent-broker/mcp-server/process_identity.mjs` — Linux PID/start-identity inspection and attributable process-group termination helpers.

### Persistence and repository isolation

- Create `plugins/subagent-broker/mcp-server/state_store.mjs` — atomic agent state/result/transition persistence and restart reconciliation.
- Create `plugins/subagent-broker/mcp-server/worktree_manager.mjs` — exact base resolution, detached read-only snapshots, write branches/worktrees, dirty-state inspection, safe cleanup.

### Codex backend and broker

- Create `plugins/subagent-broker/mcp-server/codex_cli_backend.mjs` — CLI probe, spawn, JSONL/session extraction, resume, cancellation.
- Create `plugins/subagent-broker/mcp-server/broker.mjs` — queue, concurrency, timeouts, waits, results, follow-up orchestration, cleanup.
- Create `plugins/subagent-broker/mcp-server/mcp_server.mjs` — stdio JSON-RPC/MCP adapter exposing exactly eight approved tools.

### Plugin / roles / Skill

- Create `plugins/subagent-broker/.codex-plugin/plugin.json`.
- Create `plugins/subagent-broker/.mcp.json`.
- Create `plugins/subagent-broker/README.md`.
- Create `plugins/subagent-broker/roles/implementer.md`.
- Create `plugins/subagent-broker/roles/reviewer.md`.
- Create `plugins/subagent-broker/roles/researcher.md`.
- Create `plugins/subagent-broker/roles/tester.md`.
- Create `plugins/subagent-broker/roles/security-reviewer.md`.
- Create `plugins/subagent-broker/skills/subagent-broker/SKILL.md`.
- Create `plugins/subagent-broker/skills/subagent-broker/agents/openai.yaml`.
- Create `plugins/subagent-broker/skills/subagent-broker/references/routing.md`.
- Create `plugins/subagent-broker/skills/subagent-broker/references/lifecycle.md`.
- Create `plugins/subagent-broker/skills/subagent-broker/references/security.md`.
- Create `plugins/subagent-broker/skills/subagent-broker/references/superpowers-sdd.md`.

### Repository integration and CI

- Create or modify `.gitignore` — append `.superpowers/subagents/` and `.worktrees/` without removing any existing rules.
- Modify `.agents/plugins/marketplace.json`.
- Modify `.codex/config.toml`.
- Modify `AGENTS.md`.
- Create `.github/workflows/subagent-broker.yml` — Linux Node test job plus repository governance gates that are already required for affected files.
- Create `plugins/subagent-broker/scripts/smoke_real_codex.mjs` — explicit, non-CI real-runtime smoke harness.

### Tests

- Create `plugins/subagent-broker/tests/helpers.mjs`.
- Create `plugins/subagent-broker/tests/fake-codex.mjs`.
- Create `plugins/subagent-broker/tests/protocol.test.mjs`.
- Create `plugins/subagent-broker/tests/redaction.test.mjs`.
- Create `plugins/subagent-broker/tests/state-store.test.mjs`.
- Create `plugins/subagent-broker/tests/worktree.test.mjs`.
- Create `plugins/subagent-broker/tests/codex-backend.test.mjs`.
- Create `plugins/subagent-broker/tests/broker.test.mjs`.
- Create `plugins/subagent-broker/tests/mcp-protocol.test.mjs`.
- Create `plugins/subagent-broker/tests/controller-contract.test.mjs`.
- Create `plugins/subagent-broker/tests/repository-integration.test.mjs`.

---

### Task 1: Define Lifecycle, Tool Contracts, and Redaction

**Files:**
- Create: `plugins/subagent-broker/mcp-server/protocol.mjs`
- Create: `plugins/subagent-broker/mcp-server/redaction.mjs`
- Create: `plugins/subagent-broker/tests/protocol.test.mjs`
- Create: `plugins/subagent-broker/tests/redaction.test.mjs`

**Interfaces:**
- Produces: `AGENT_STATES: ReadonlySet<string>`
- Produces: `TERMINAL_STATES: ReadonlySet<string>`
- Produces: `canTransition(from: string, to: string) -> boolean`
- Produces: `assertTransition(from: string, to: string, reason?: string) -> void`
- Produces: `validateSpawnArgs(value: unknown) -> SpawnSpec`
- Produces: `validateWaitArgs(value: unknown) -> { agent_id: string, timeout_ms: number }`
- Produces: equivalent validators for result/status/followup/list/cancel/cleanup.
- Produces: `brokerError(code: string, message: string, details?: object) -> Error`
- Produces: `buildChildEnv(parentEnv: object) -> object`
- Produces: `redactText(text: string, inheritedEnv?: object) -> string`
- Consumes: Node standard library only.

- [ ] **Step 1: Write failing lifecycle and argument-validation tests**

Pin all nine states, five terminal states, legal representative transitions, illegal transition rejection, role enum, workspace-mode enum, timeout defaults/bounds, priority enum, and rejection of unknown tool fields such as `command`, `env`, `model`, or `args`.

A completed turn may reopen only through the explicit follow-up path:

```js
assert.equal(canTransition("COMPLETED", "SPAWNING"), false);
assert.doesNotThrow(() => assertTransition("COMPLETED", "SPAWNING", "followup"));
assert.throws(() => assertTransition("FAILED", "SPAWNING", "followup"));
```

v1 follow-up is therefore allowed only from `COMPLETED`, with a recorded session ID and confirmed resume capability.

Example assertions:

```js
assert.equal(canTransition("QUEUED", "SPAWNING"), true);
assert.equal(canTransition("RUNNING", "COMPLETED"), true);
assert.equal(canTransition("COMPLETED", "RUNNING"), false);
assert.throws(
  () => validateSpawnArgs({ task: "x", role: "implementer", command: "rm -rf /" }),
  /unknown field/i
);
```

- [ ] **Step 2: Write failing redaction/environment tests**

Assert:

- only explicit safe OS variables plus supported Codex auth/runtime variable names survive `buildChildEnv`;
- variables whose names contain `TOKEN`, `SECRET`, `PASSWORD`, `API_KEY`, `ACCESS_KEY`, or `PRIVATE_KEY` are never copied merely because they exist;
- inherited secret values are replaced in text with `[REDACTED]`;
- nonsecret stderr remains readable.

- [ ] **Step 3: Run focused tests and confirm RED**

Run:

```bash
node --test   plugins/subagent-broker/tests/protocol.test.mjs   plugins/subagent-broker/tests/redaction.test.mjs
```

Expected: FAIL because modules do not exist.

- [ ] **Step 4: Implement protocol and redaction modules**

Use exact defaults:

```text
timeout_seconds=1800
priority=normal
wait min=1000 ms
wait max=600000 ms
```

The child env allowlist must include only OS execution basics needed on Linux plus Codex-supported authentication/runtime variables actually required by the installed runtime; tests pin the initial allowlist and prevent wildcard pass-through.

- [ ] **Step 5: Run focused tests and confirm GREEN**

Run the command from Step 3.

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/subagent-broker/mcp-server/protocol.mjs   plugins/subagent-broker/mcp-server/redaction.mjs   plugins/subagent-broker/tests/protocol.test.mjs   plugins/subagent-broker/tests/redaction.test.mjs
git commit -m "feat: define subagent broker protocol and redaction"
```

---

### Task 2: Persist Agent State and Recover Safely After Restart

**Files:**
- Create: `plugins/subagent-broker/mcp-server/process_identity.mjs`
- Create: `plugins/subagent-broker/mcp-server/state_store.mjs`
- Create: `plugins/subagent-broker/tests/state-store.test.mjs`
- Create: `plugins/subagent-broker/tests/helpers.mjs`

**Interfaces:**
- Consumes: Task 1 transition helpers and redaction.
- Produces: `readLinuxProcessIdentity(pid: number) -> Promise<{ pid: number, start_ticks: string } | null>`
- Produces: `isSameProcessIdentity(recorded, current) -> boolean`
- Produces: `terminateProcessGroup(pid: number, signal: string) -> void` on Linux only.
- Produces: `class StateStore` with:
  - `create(record: AgentRecord) -> Promise<AgentRecord>`
  - `get(agentId: string) -> Promise<AgentRecord | null>`
  - `update(agentId: string, patch: object, nextState?: string) -> Promise<AgentRecord>`
  - `list(filter?: { state?: string }) -> Promise<AgentRecord[]>`
  - `writePrompt(agentId: string, text: string) -> Promise<void>`
  - `appendEvent(agentId: string, line: string) -> Promise<void>`
  - `writeResult(agentId: string, result: object, finalText: string) -> Promise<void>`
  - `reconcileNonterminal(processProbe) -> Promise<AgentRecord[]>`
- Runtime root: `.superpowers/subagents/`.

- [ ] **Step 1: Write failing persistence tests**

Assert atomic JSON replacement, append-audited transition history, terminal-result persistence, owner-only permissions (`0o600`) for `state.json`, `prompt.txt`, `events.jsonl`, `stderr.log`, `result.json`, and `result.txt` on POSIX.

- [ ] **Step 2: Write failing restart/PID-reuse tests**

Pin the Review Focus case:

- matching PID + matching start identity may remain attributable;
- same PID + different start identity becomes `ORPHANED`;
- missing process becomes `ORPHANED`;
- already terminal records remain unchanged.

- [ ] **Step 3: Run Task 2 tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/state-store.test.mjs
```

Expected: FAIL because modules do not exist.

- [ ] **Step 4: Implement Linux process identity and StateStore**

Use `/proc/<pid>/stat` field 22 for Linux start ticks. Do not infer identity from PID alone.

Atomic writes use temp file + rename within the same agent directory.

- [ ] **Step 5: Run Task 2 tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/subagent-broker/mcp-server/process_identity.mjs   plugins/subagent-broker/mcp-server/state_store.mjs   plugins/subagent-broker/tests/state-store.test.mjs   plugins/subagent-broker/tests/helpers.mjs
git commit -m "feat: persist and recover subagent lifecycle state"
```

---

### Task 3: Create Isolated Read-Only Snapshots and Write Worktrees

**Files:**
- Create: `plugins/subagent-broker/mcp-server/worktree_manager.mjs`
- Create: `plugins/subagent-broker/tests/worktree.test.mjs`

**Interfaces:**
- Consumes: repository root, `agent_id`, `base_ref`, and workspace mode.
- Produces: `discoverRepoRoot(startCwd: string) -> Promise<string>` using `git rev-parse --show-toplevel` and verifying the resolved root contains the plugin path.
- Produces: `resolveBase(repoRoot: string, baseRef?: string) -> Promise<string>` returning exact commit SHA.
- Produces: `createWorkspace({ repoRoot, agentId, baseSha, mode }) -> Promise<WorkspaceRecord>`
- Produces: `statusWorkspace(workspace: WorkspaceRecord) -> Promise<{ dirty: boolean, porcelain: string, commits: string[], diff_stat: string }>`
- Produces: `cleanupWorkspace(workspace: WorkspaceRecord, { purgeBranch?: boolean }) -> Promise<void>`
- Uses `git` through argument arrays with `shell:false`.

- [ ] **Step 1: Write failing read-only snapshot tests**

Create a temporary Git repo and prove:

- read-only workspace is a detached worktree at exact `baseSha`;
- parent branch may advance after workspace creation without changing the reviewer's checked-out commit;
- no branch named `subagent/<agent_id>` is created for read-only mode;
- paths outside `.worktrees/subagents/<agent_id>` are rejected;
- starting discovery from `plugins/subagent-broker/` resolves the owning WhiteChronos repository root, while a cwd outside any Git repository fails closed.

- [ ] **Step 2: Write failing write-worktree tests**

Prove:

- branch is exactly `subagent/<agent_id>`;
- worktree is unique;
- two agents from the same base get different worktrees/branches;
- `main` and parent task branch remain unchanged;
- invalid/path-traversal agent IDs/base refs cannot create paths outside the repository namespace;
- dirty cleanup refuses and returns status evidence.

- [ ] **Step 3: Run worktree tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/worktree.test.mjs
```

Expected: FAIL because manager does not exist.

- [ ] **Step 4: Implement worktree manager**

Use `git rev-parse --verify <ref>^{commit}`, `git worktree add --detach` for read-only snapshots, and `git worktree add -b subagent/<id>` for write agents.

Do not use `git clean -fdx` or any broad deletion command.

- [ ] **Step 5: Run worktree tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/subagent-broker/mcp-server/worktree_manager.mjs   plugins/subagent-broker/tests/worktree.test.mjs
git commit -m "feat: isolate subagent git workspaces"
```

---

### Task 4: Implement the Real Codex CLI Backend

**Files:**
- Create: `plugins/subagent-broker/mcp-server/codex_cli_backend.mjs`
- Create: `plugins/subagent-broker/tests/fake-codex.mjs`
- Create: `plugins/subagent-broker/tests/codex-backend.test.mjs`

**Interfaces:**
- Consumes: Task 1 env/redaction, Task 2 process identity/state artifacts, Task 3 workspace path.
- Produces: `class CodexCliBackend` with:
  - `probe() -> Promise<CodexCapabilities>`
  - `spawn(spec: BackendSpawnSpec) -> Promise<BackendHandle>`
  - `followup(handle: BackendHandle, message: string) -> Promise<BackendHandle>`
  - `cancel(handle: BackendHandle, { graceSeconds: number }) -> Promise<void>`
- `CodexCapabilities` includes `version`, `exec`, `json`, `resume`, `sandboxReadOnly`, `sandboxWorkspaceWrite`, and `approvalNever`.
- Produces: `extractSessionId(event: object) -> string | null` that supports fixture-proven event shapes without assuming one undocumented field.
- Uses current documented base forms:
  - spawn: `codex exec --json --sandbox <read-only|workspace-write> --ask-for-approval never -`
  - resume: `codex exec --json --sandbox <mode> --ask-for-approval never resume <session-id> -`
- The live smoke test later confirms those forms against the installed CLI before follow-up is advertised as healthy.

- [ ] **Step 1: Implement the fake Codex executable fixture only**

The fake executable must support:

- `--version`;
- `exec --help`;
- `exec resume --help`;
- spawn mode emitting JSONL including a deterministic fake session ID;
- resume mode validating the provided session ID;
- sleep mode;
- chosen nonzero exit code;
- descendant-process mode for cancellation tests;
- optional marker/commit behavior inside the supplied worktree.

This fixture is test infrastructure, not production backend code.

- [ ] **Step 2: Write failing capability-probe tests**

Assert the backend derives capabilities from fake help output and returns unavailable when required `exec --json` features are missing.

- [ ] **Step 3: Write failing spawn/session tests**

Assert:

- Node spawn receives an argument array;
- `shell:false`;
- task prompt is sent on stdin and absent from argv;
- child runs in exact workspace cwd;
- child has a distinct PID and recorded Linux process-start identity;
- child prompt contains role + explicit task only and does not contain a supplied fake parent-transcript sentinel;
- JSONL is appended incrementally;
- session ID is extracted;
- sensitive stderr is redacted before compact result exposure.

- [ ] **Step 4: Write failing follow-up tests**

Assert:

- resume uses recorded session ID;
- same workspace is reused;
- resume input goes through stdin;
- if probe says resume unsupported, return `CAPABILITY_UNAVAILABLE`;
- no fresh-session fallback is silently substituted.

- [ ] **Step 5: Write failing cancellation-containment test**

Start two fake agents; one fake agent spawns a descendant. Cancelling agent A must terminate A's attributable process group/descendant while agent B remains alive.

- [ ] **Step 6: Run backend tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/codex-backend.test.mjs
```

Expected: FAIL because production backend does not exist.

- [ ] **Step 7: Implement CodexCliBackend**

Launch Linux children in their own process group (`detached:true`) so cancellation can target `-pid` for that agent only.

Use bounded stderr buffering; persist the full raw JSONL trace locally but never return it wholesale.

- [ ] **Step 8: Run backend tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add plugins/subagent-broker/mcp-server/codex_cli_backend.mjs   plugins/subagent-broker/tests/fake-codex.mjs   plugins/subagent-broker/tests/codex-backend.test.mjs
git commit -m "feat: launch independent Codex subagent processes"
```

---

### Task 5: Add Broker Queue, Wait, Result, Follow-Up, Timeout, and Cleanup

**Files:**
- Create: `plugins/subagent-broker/mcp-server/broker.mjs`
- Create: `plugins/subagent-broker/tests/broker.test.mjs`

**Interfaces:**
- Consumes: `StateStore`, `CodexCliBackend`, and worktree manager.
- Produces: `class SubagentBroker` with:
  - `start() -> Promise<void>`
  - `spawn(args) -> Promise<AgentPublicRecord>`
  - `status(agentId) -> Promise<AgentPublicRecord>`
  - `wait(agentId, timeoutMs) -> Promise<AgentPublicRecord>`
  - `result(agentId) -> Promise<AgentResult>`
  - `followup(agentId, message) -> Promise<AgentPublicRecord>`
  - `list(filter?) -> Promise<AgentPublicRecord[]>`
  - `cancel(agentId) -> Promise<AgentPublicRecord>`
  - `cleanup(agentId, options?) -> Promise<CleanupResult>`
  - `shutdown() -> Promise<void>`
- Constructor defaults: `maxRunning=3`, `maxQueued=32`, `defaultTimeoutSeconds=1800`, `cancelGraceSeconds=10`.

- [ ] **Step 1: Write failing concurrency/queue tests**

Prove:

- first three agents can run;
- fourth becomes `QUEUED` with no PID;
- completion of one starts the next;
- high priority moves ahead of queued normal work but never preempts running work;
- queue 33 returns `RESOURCE_EXHAUSTED`;
- `maxRunning > 8` is rejected.

- [ ] **Step 2: Write failing wait/timeout tests**

Prove:

- wait returns immediately for terminal agent;
- wait timeout returns current nonterminal state and does not mark failure;
- execution timeout transitions RUNNING -> TIMED_OUT and terminates attributable process group.

- [ ] **Step 3: Write failing result/follow-up tests**

Prove `result(agentId)` returns `NOT_READY` for every nonterminal state rather than presenting partial data as a final result.

For a terminal agent, prove result includes bounded redacted excerpts, exact worktree/branch, session ID if available, exit code, commit list/diff stat, and artifact paths.

Prove follow-up starts only from `COMPLETED` with a recorded session ID and confirmed resume capability, transitions through SPAWNING/RUNNING to a new terminal turn, and retains the same agent identity, worktree, and session ID.

- [ ] **Step 4: Write failing queued/running cancel and cleanup tests**

Prove:

- queued cancel never launches process;
- running cancel enters `CANCEL_REQUESTED` then `CANCELLED`;
- dirty write worktree cleanup refuses;
- incomplete result metadata cleanup refuses;
- safe cleanup can remove terminal worktree/trace data while preserving compact metadata unless `purge_metadata=true`.

- [ ] **Step 5: Run broker tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/broker.test.mjs
```

Expected: FAIL because broker does not exist.

- [ ] **Step 6: Implement SubagentBroker**

Use event/promise waiters keyed by `agent_id`; do not poll with short intervals.

Start queued work when capacity frees.

- [ ] **Step 7: Run broker tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add plugins/subagent-broker/mcp-server/broker.mjs   plugins/subagent-broker/tests/broker.test.mjs
git commit -m "feat: orchestrate subagent lifecycle and queue"
```

---

### Task 6: Expose Exactly Eight Stateful MCP Tools

**Files:**
- Create: `plugins/subagent-broker/mcp-server/mcp_server.mjs`
- Create: `plugins/subagent-broker/tests/mcp-protocol.test.mjs`

**Interfaces:**
- Consumes: `SubagentBroker` and Task 1 validators.
- Produces stdio JSON-RPC methods `initialize`, `ping`, `tools/list`, and `tools/call`.
- Exposes exactly:
  - `subagent_spawn`
  - `subagent_status`
  - `subagent_wait`
  - `subagent_result`
  - `subagent_followup`
  - `subagent_list`
  - `subagent_cancel`
  - `subagent_cleanup`

- [ ] **Step 1: Write failing protocol tests**

Launch the MCP server as a subprocess and assert:

- initialize negotiates supported protocol version;
- stdout lines are JSON only;
- operational logs go to stderr/files;
- tool list contains exactly the eight names;
- schemas reject arbitrary `command`, `env`, `args`, and `model` fields;
- malformed JSON returns parse error without server crash;
- unknown tool returns structured error;
- stateful calls reach the fake-backed broker;
- server startup discovers the repository root from the plugin cwd and does not accept an arbitrary repository-root path from MCP callers.

- [ ] **Step 2: Pin MCP annotations**

Mark status/wait/result/list as read-only; spawn/followup/cancel/cleanup as mutating. `destructiveHint` is true for cleanup and cancel where applicable. `openWorldHint` is false because the broker itself targets the bounded local Codex/workspace surface; child network remains governed by Codex sandbox.

- [ ] **Step 3: Run MCP tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs
```

Expected: FAIL because server does not exist.

- [ ] **Step 4: Implement MCP server**

Follow the repository's existing GitHub Arena line-oriented stdio pattern, but instantiate one persistent broker for the server lifetime.

- [ ] **Step 5: Run MCP tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/subagent-broker/mcp-server/mcp_server.mjs   plugins/subagent-broker/tests/mcp-protocol.test.mjs
git commit -m "feat: expose real subagent broker MCP tools"
```

---

### Task 7: Add Role Profiles and Native-First Controller Skill

**Files:**
- Create: `plugins/subagent-broker/.codex-plugin/plugin.json`
- Create: `plugins/subagent-broker/.mcp.json`
- Create: `plugins/subagent-broker/README.md`
- Create: `plugins/subagent-broker/roles/implementer.md`
- Create: `plugins/subagent-broker/roles/reviewer.md`
- Create: `plugins/subagent-broker/roles/researcher.md`
- Create: `plugins/subagent-broker/roles/tester.md`
- Create: `plugins/subagent-broker/roles/security-reviewer.md`
- Create: `plugins/subagent-broker/skills/subagent-broker/SKILL.md`
- Create: `plugins/subagent-broker/skills/subagent-broker/agents/openai.yaml`
- Create: four reference files listed in File Structure.
- Create: `plugins/subagent-broker/tests/controller-contract.test.mjs`

**Interfaces:**
- Produces local plugin `subagent-broker`.
- Produces MCP server key `subagent_broker`.
- Produces controller contract: native Codex tools -> broker -> inline fallback.

- [ ] **Step 1: Write failing controller contract tests**

Assert the Skill text requires:

- actual tool-list inspection;
- native multi-agent first;
- broker second;
- inline fallback third;
- no prompt-persona subagent claims;
- no direct write to `main`;
- Superpowers SDD task brief/report/review/ledger preservation;
- Arena is review, not runtime;
- broker result/state evidence is required before claiming a child ran.

- [ ] **Step 2: Write failing role tests**

Assert each role exists and has explicit mutation policy:

- implementer: write-capable when task chooses `worktree_write`;
- reviewer/researcher/security-reviewer: read-only default;
- tester: read-only unless task explicitly uses write worktree.

No role file may contain credentials or arbitrary model name.

- [ ] **Step 3: Run controller tests and confirm RED**

```bash
node --test plugins/subagent-broker/tests/controller-contract.test.mjs
```

Expected: FAIL until files exist.

- [ ] **Step 4: Implement plugin, MCP manifest, roles, Skill, and references**

`.mcp.json` follows:

```json
{
  "mcpServers": {
    "subagent_broker": {
      "type": "stdio",
      "command": "node",
      "args": ["./mcp-server/mcp_server.mjs"],
      "cwd": "."
    }
  }
}
```

Plugin has no hooks.

- [ ] **Step 5: Run controller tests and confirm GREEN**

Expected: PASS.

- [ ] **Step 6: Validate Skill structure**

Run the current Skill Creator `quick_validate.py` against `plugins/subagent-broker/skills/subagent-broker`.

Expected: `Skill is valid!`

- [ ] **Step 7: Commit**

```bash
git add plugins/subagent-broker/.codex-plugin   plugins/subagent-broker/.mcp.json   plugins/subagent-broker/README.md   plugins/subagent-broker/roles   plugins/subagent-broker/skills   plugins/subagent-broker/tests/controller-contract.test.mjs
git commit -m "feat: add native-first subagent broker controller"
```

---

### Task 8: Register Broker in Codex and Repository Governance

**Files:**
- Create or Modify: `.gitignore`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.codex/config.toml`
- Modify: `AGENTS.md`
- Create: `plugins/subagent-broker/tests/repository-integration.test.mjs`

**Interfaces:**
- Consumes plugin name `subagent-broker` and MCP key `subagent_broker`.
- Produces repository-level enabled plugin/tool configuration and routing policy.

- [ ] **Step 1: Write failing repository integration tests**

Parse JSON/TOML/text and assert:

- marketplace registers local `./plugins/subagent-broker` for CODEX;
- `multi_agent = true` remains present;
- every existing plugin currently enabled remains enabled;
- broker MCP is enabled;
- `enabled_tools` contains exactly the eight approved broker tools;
- `.gitignore` contains `.superpowers/subagents/` and `.worktrees/`;
- `AGENTS.md` states native -> broker -> inline fallback;
- `AGENTS.md` forbids fake subagent claims and write children on `main`.

- [ ] **Step 2: Run integration test and confirm RED**

```bash
node --test plugins/subagent-broker/tests/repository-integration.test.mjs
```

Expected: FAIL because registration is absent.

- [ ] **Step 3: Modify marketplace/config without removing existing entries**

Append:

```toml
[plugins."subagent-broker@whitechronos-repo"]
enabled = true

[plugins."subagent-broker@whitechronos-repo".mcp_servers.subagent_broker]
enabled = true
default_tools_approval_mode = "approve"
enabled_tools = [
  "subagent_spawn",
  "subagent_status",
  "subagent_wait",
  "subagent_result",
  "subagent_followup",
  "subagent_list",
  "subagent_cancel",
  "subagent_cleanup"
]
```

- [ ] **Step 4: Add Git ignore and AGENTS governance**

If `.gitignore` does not exist, create it with only the two runtime rules; if it exists at execution time, append only missing rules.

- [ ] **Step 5: Run integration test and config parsers**

```bash
node --test plugins/subagent-broker/tests/repository-integration.test.mjs
python - <<'PY'
import json, tomllib
json.load(open(".agents/plugins/marketplace.json", encoding="utf-8"))
with open(".codex/config.toml", "rb") as f:
    tomllib.load(f)
print("CONFIG PASS")
PY
```

Expected: PASS and `CONFIG PASS`.

- [ ] **Step 6: Commit**

```bash
git add .gitignore .agents/plugins/marketplace.json .codex/config.toml AGENTS.md   plugins/subagent-broker/tests/repository-integration.test.mjs
git commit -m "feat: enable real subagent broker in Codex"
```

---

### Task 9: Add Linux CI and Full Fake-Codex Integration Coverage

**Files:**
- Create: `.github/workflows/subagent-broker.yml`
- Expand: `plugins/subagent-broker/tests/*.test.mjs`

**Interfaces:**
- Produces Linux CI job using Node 22.
- Runs no real model inference and needs no Codex/OpenAI credential.
- Consumes fake Codex executable from Task 4.

- [ ] **Step 1: Add one end-to-end fake runtime test**

Exercise MCP server -> broker -> fake Codex process -> worktree -> result:

1. create temp Git repo;
2. start MCP server with fake Codex path;
3. spawn two read-only children concurrently;
4. assert distinct PIDs and trace directories;
5. spawn one write child;
6. assert separate branch/worktree;
7. follow up same fake session;
8. spawn independent read-only reviewer at write-child head;
9. cancel long-running child;
10. safely clean terminal workspaces.

- [ ] **Step 2: Run entire test suite locally**

```bash
node --test plugins/subagent-broker/tests/*.test.mjs
```

Expected: PASS.

- [ ] **Step 3: Create workflow**

Workflow triggers on PR/push changes under `plugins/subagent-broker/**`, `.codex/config.toml`, `.agents/plugins/marketplace.json`, `.gitignore`, `AGENTS.md`, and its workflow file.

Use `actions/setup-node@v4` with Node 22 and run:

```bash
node --test plugins/subagent-broker/tests/*.test.mjs
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/subagent-broker.yml plugins/subagent-broker/tests
git commit -m "ci: verify subagent broker on Linux"
```

---

### Task 10: Add Real-Codex Smoke Harness Without Running It in CI

**Files:**
- Create: `plugins/subagent-broker/scripts/smoke_real_codex.mjs`
- Create: `plugins/subagent-broker/tests/smoke-contract.test.mjs`

**Interfaces:**
- Consumes the real installed `codex` CLI and current repository only when explicitly invoked.
- Produces a timestamped local smoke report under `.superpowers/subagents/smoke-<timestamp>/summary.json`.
- Requires explicit environment opt-in `SUBAGENT_BROKER_LIVE=1`.

- [ ] **Step 1: Write failing smoke-contract tests**

Assert the script:

- exits without spawning Codex when `SUBAGENT_BROKER_LIVE != 1`;
- probes `codex --version`, `codex exec --help`, and `codex exec resume --help`;
- refuses to run if real `exec --json` support is absent;
- records the exact observed version/help capability summary;
- never runs in CI by default;
- uses the broker API, not bespoke child-launch code.

- [ ] **Step 2: Run smoke-contract test and confirm RED**

```bash
node --test plugins/subagent-broker/tests/smoke-contract.test.mjs
```

Expected: FAIL until script exists.

- [ ] **Step 3: Implement smoke harness**

The live sequence is exactly:

1. spawn two read-only children with distinct harmless repository-analysis tasks;
2. require different agent IDs, PIDs, and trace paths;
3. wait for both and capture outputs;
4. spawn one write implementer on a broker-created subagent branch/worktree with a deliberately disposable file-change task;
5. require a real commit/diff on that child branch;
6. if probe confirms resume, follow up the same session/worktree with a harmless request and verify session identity is unchanged;
7. spawn independent reviewer at the implementer branch head;
8. spawn/cancel a long-running child;
9. collect redacted bounded results;
10. cleanup only safe worktrees and leave compact smoke evidence.

Do not merge/cherry-pick the disposable child branch into the main task branch.

- [ ] **Step 4: Run contract tests only**

```bash
node --test plugins/subagent-broker/tests/smoke-contract.test.mjs
```

Expected: PASS. Do **not** run live smoke before infrastructure merge.

- [ ] **Step 5: Commit**

```bash
git add plugins/subagent-broker/scripts/smoke_real_codex.mjs   plugins/subagent-broker/tests/smoke-contract.test.mjs
git commit -m "test: add explicit real Codex subagent smoke harness"
```

---

### Task 11: Infrastructure Verification, Arena Review, PR, and Merge

**Files:**
- All implementation files from Tasks 1–10.
- No live smoke evidence committed.

**Interfaces:**
- Produces one reviewed infrastructure PR and merged broker code on `main`.

- [ ] **Step 1: Run full pre-PR verification**

```bash
node --test plugins/subagent-broker/tests/*.test.mjs
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

Expected: all PASS.

- [ ] **Step 2: Verify no runtime artifacts are tracked**

```bash
git status --short -- .superpowers/subagents .worktrees
git ls-files '.superpowers/subagents/**' '.worktrees/**'
```

Expected: no tracked runtime files.

- [ ] **Step 3: Run GitHub Arena Review Arena on the whole branch**

Focus on:

- process containment;
- shell/env injection surface;
- dirty-worktree cleanup;
- PID reuse;
- secret/trace handling;
- native-first routing;
- false subagent claims.

Resolve every Critical/Important finding before opening PR.

- [ ] **Step 4: Open infrastructure PR**

PR body must state:

- no real-subagent claim yet;
- fake-Codex tests prove process/worktree mechanics only;
- live smoke is intentionally post-merge;
- native tools remain preferred;
- broker uses no OpenAI API key creation/billing setup;
- v1 Linux target.

- [ ] **Step 5: Wait for every applicable CI/governance check**

Do not merge while any required check is queued, running, or failed.

- [ ] **Step 6: Squash merge using expected head SHA**

After merge, verify `main` contains broker plugin/config/tests and no runtime state.

---

### Task 12: Execute the Real Post-Merge Codex Smoke Test

**Files:**
- No source change unless a verified defect requires a separate fix branch.
- Local evidence: `.superpowers/subagents/smoke-*/summary.json`.

**Interfaces:**
- Produces evidence required before calling the fallback broker a real subagent runtime.

- [ ] **Step 1: Start a fresh trusted Codex remote/network session**

A fresh session is mandatory so the merged plugin/MCP tool list reloads.

- [ ] **Step 2: Verify broker tool discovery**

Confirm all eight broker MCP tools are visible and health/capability probe reports the actual installed Codex version.

If the harness also exposes native `spawn_agent`, separately verify the controller chooses native tools and leaves broker idle for the same dispatch.

- [ ] **Step 3: Run live smoke harness**

Run:

```bash
SUBAGENT_BROKER_LIVE=1 node plugins/subagent-broker/scripts/smoke_real_codex.mjs
```

Required evidence:

- two simultaneous independent children;
- different PIDs;
- different `agent_id` values;
- different trace paths;
- different Codex session IDs when the CLI exposes them;
- write child uses separate branch/worktree;
- reviewer uses an exact isolated snapshot;
- cancellation reaches terminal `CANCELLED`;
- no secret values appear in compact result evidence.

- [ ] **Step 4: Verify follow-up semantics**

If the installed CLI probe reports resume support, require same session ID and same worktree after follow-up.

If resume is not supported, require honest `CAPABILITY_UNAVAILABLE` and still accept initial independent spawn capability.

- [ ] **Step 5: Run one manual Superpowers SDD mini-flow through the broker fallback**

Use a disposable, bounded repository task:

1. broker implementer;
2. broker reviewer;
3. one broker follow-up fix only if reviewer returns a real finding;
4. broker reviewer re-check;
5. discard or isolate disposable test commits after evidence collection.

This proves the integration path, not just low-level process spawning.

- [ ] **Step 6: Declare broker fallback verified only if evidence satisfies the spec**

Record:

- Codex CLI version;
- native tool availability;
- backend used;
- agent IDs/PIDs/session IDs;
- branch/worktree evidence;
- follow-up capability;
- cancellation evidence.

If any acceptance item fails, open a bugfix branch and do not call the fallback "real subagents" yet.

---

### Task 13: Resume Awesome LLM Apps With Both Execution Paths

**Files:**
- Existing approved Awesome LLM Apps spec/plan branches.
- No silent merge of the paused work.

**Interfaces:**
- Consumes verified Subagent Broker or native multi-agent availability.
- Produces separate Native and Subagent-driven evidence for the Awesome LLM Apps implementation.

- [ ] **Step 1: Reconcile the paused Awesome LLM Apps implementation branch with current `main`**

Do not discard prior Native TDD work. Rebase/update only after inspecting the existing branch diff and test evidence.

- [ ] **Step 2: Finish/verify the Native path**

Complete any remaining approved Awesome LLM Apps tasks with the existing Native execution evidence.

- [ ] **Step 3: Run a real Subagent-driven pass**

Use native Codex multi-agent if exposed; otherwise use the now-verified broker.

At minimum:

- independent implementer/researcher where a remaining task benefits;
- independent task reviewer;
- independent final whole-branch reviewer.

- [ ] **Step 4: Keep evidence separated**

The progress ledger/final report must state which commits/findings came from:

```text
Native
Native Codex multi-agent
Subagent Broker codex_cli
```

Never collapse these into a generic "agents ran" statement.

- [ ] **Step 5: Continue the existing Awesome LLM Apps PR/CI/merge process**

Use its approved plan and normal Superpowers finish-the-branch gates.

