# WhiteChronos Real Subagent Broker — Design Spec

**Date:** 2026-10-03  
**Repository:** `WhiteChronos/ChatGPT`  
**Status:** Written design for user review  
**Scope class:** Architectural  
**Initial deployment target:** trusted Codex remote/network workspace on Linux  
**Related paused work:** Awesome LLM Apps full-system integration

## 1. Intent

Create a **real subagent runtime** for WhiteChronos so Superpowers
`subagent-driven-development` can use independent agents even when the
current Codex harness does not expose its native multi-agent tools.

"Real subagent" in this design means all of the following are true:

- the child runs in a distinct operating-system process;
- the child owns an independent Codex execution/session context;
- the child receives an explicit task brief instead of silently inheriting the parent conversation;
- a write-capable child works in an isolated Git worktree/branch;
- the child emits its own structured trace and terminal result;
- the parent can identify the child by a stable `agent_id`;
- status, wait, continuation/follow-up, cancellation, and result collection are backed by actual child lifecycle state;
- the system never reports a subagent as having run unless an independent child process/session really existed.

This subsystem is a fallback and coordination layer. It does **not** replace
native Codex multi-agent support when native `spawn_agent`/follow-up/wait
tools are actually present in the current runtime.

## 2. User-required outcome

The routing order for subagent workflows becomes:

```text
Subagent workflow requested
        |
        v
Does current Codex harness expose native multi-agent tools?
        |
   +----+----+
   |         |
  yes        no
   |         |
   v         v
Native Codex  WhiteChronos Subagent Broker MCP
multi-agent          |
   |                 v
   |          independent codex processes
   |                 |
   +--------+--------+
            |
            v
      Superpowers SDD
            |
            v
      repository workflow
```

The general WhiteChronos development stack remains:

```text
System / developer / user / repository constraints
  -> Superpowers process
  -> native subagents OR Subagent Broker fallback when SDD needs them
  -> ECC specialist capability
  -> Matt Pocock specialist capability
  -> Awesome LLM Apps specialist/example layer when installed
  -> GitHub evidence and mutation
  -> GitHub Arena final review
```

## 3. Current platform facts and limits

The repository already has:

```toml
[features]
multi_agent = true
```

That feature flag enables native multi-agent support only in Codex runtimes
whose selected harness/preset actually exposes those tools. It does not add
`spawn_agent` to an already-running ChatGPT conversation or to a harness that
did not expose it.

The current ChatGPT session used to author this spec does not expose a real
spawn/wait/follow-up subagent tool. Therefore this spec must not claim that
subagents were already executed here.

OpenAI documentation currently establishes these useful primitives:

- `codex exec --json` emits JSONL structured events for non-interactive
  Codex execution;
- Codex supports `exec resume` as an automation interface on supported
  versions;
- native Codex multi-agent V2 uses spawn/follow-up/wait primitives when
  those tools are exposed by the harness;
- self-hosted `codex exec-server` is available for remote environments,
  but is a separate deployment path and is not required for v1.

The implementation must trust the **actual installed Codex CLI help and
runtime tool list** over stale documentation.

## 4. Design approaches considered

### Approach A — Prompt-only simulated subagents

Pretend multiple roles exist by asking the same model/context to behave as
implementer/reviewer/researcher.

**Rejected.**

It violates the user's requirement and the repository's existing rule that
independent subagents may only be claimed when the runtime really executed
them.

### Approach B — Hosted external agent API only

Require a separate API/application backend for every subagent.

**Advantages**

- strong session primitives;
- naturally remote;
- scalable.

**Rejected as the mandatory v1 path** because it introduces additional
credential, billing, organization/project, and environment configuration
before the already-authenticated Codex runtime can be used.

The architecture leaves a backend adapter point for a future hosted agent API
implementation, but no hosted credential is required for v1.

### Approach C — Native-first router + local/remote Codex-process broker

Use native Codex multi-agent tools when the harness exposes them. Otherwise,
route through a local MCP server that launches independent `codex exec`
processes, persists their state, and uses isolated worktrees.

**Selected.**

This provides genuine independent execution without duplicating native
multi-agent functionality.

## 5. Repository layout

Planned layout:

```text
WhiteChronos/ChatGPT/
  .agents/
    plugins/
      marketplace.json

  .codex/
    config.toml

  .gitignore

  plugins/
    subagent-broker/
      .codex-plugin/
        plugin.json
      .mcp.json
      README.md

      mcp-server/
        mcp_server.mjs
        broker.mjs
        state_store.mjs
        codex_cli_backend.mjs
        worktree_manager.mjs
        redaction.mjs
        protocol.mjs

      roles/
        implementer.md
        reviewer.md
        researcher.md
        tester.md
        security-reviewer.md

      skills/
        subagent-broker/
          SKILL.md
          agents/
            openai.yaml
          references/
            routing.md
            lifecycle.md
            security.md
            superpowers-sdd.md

      tests/
        fake-codex.mjs
        mcp-protocol.test.mjs
        spawn.test.mjs
        followup.test.mjs
        concurrency.test.mjs
        worktree.test.mjs
        cancellation.test.mjs
        security.test.mjs
        controller-contract.test.mjs
```

Runtime state is **not committed**:

```text
.superpowers/subagents/
  <agent_id>/
    state.json
    prompt.txt
    events.jsonl
    stderr.log
    result.json
    result.txt
```

Write-capable child worktrees are also not committed as directories:

```text
.worktrees/subagents/<agent_id>/
```

The implementation adds ignore rules for:

```gitignore
.superpowers/subagents/
.worktrees/
```

If a future repository already contains `.gitignore`, the installer/change
must preserve every existing rule and append only missing entries.

## 6. Plugin architecture

Create a WhiteChronos local Codex plugin named:

```text
subagent-broker
```

The plugin owns:

- one Skill that routes subagent workflows;
- one stdio MCP server;
- no hooks;
- no unrelated MCP servers;
- no GitHub credentials;
- no OpenAI secret committed to repository state.

Proposed plugin manifest capabilities:

```json
{
  "name": "subagent-broker",
  "version": "1.0.0",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json"
}
```

The exact manifest must follow the repository's current plugin schema at
implementation time.

## 7. MCP tool contract

The MCP server exposes these tools.

### 7.1 `subagent_spawn`

Create one real child.

Inputs:

```json
{
  "task": "string",
  "role": "implementer",
  "workspace_mode": "worktree_write",
  "base_ref": "optional git ref",
  "timeout_seconds": 1800,
  "priority": "normal"
}
```

Rules:

- `task` is required and nonblank;
- `role` is one of the registered role profiles;
- `workspace_mode` is `read_only` or `worktree_write`;
- default timeout is bounded;
- raw arbitrary shell commands are not accepted as tool input;
- arbitrary environment variables are not accepted as tool input;
- raw unrestricted Codex command-line arguments are not accepted as tool input;
- model names are not accepted as arbitrary caller input in v1;
- `base_ref` must resolve inside the current repository.

Returns immediately after the child is successfully created or queued:

```json
{
  "agent_id": "sa_...",
  "state": "RUNNING",
  "backend": "codex_cli",
  "pid": 12345,
  "session_id": null,
  "branch": "subagent/sa_...",
  "worktree": ".worktrees/subagents/sa_..."
}
```

If concurrency is full, state is `QUEUED` and no PID exists yet.

### 7.2 `subagent_status`

Input: `agent_id`.

Returns current lifecycle data without waiting.

### 7.3 `subagent_wait`

Inputs:

- `agent_id`;
- `timeout_ms`, minimum 1,000 and maximum 600,000.

Behavior:

- returns immediately if the agent is terminal;
- otherwise blocks only until terminal state or timeout;
- a timeout is not an agent failure;
- returned payload always contains the current state.

### 7.4 `subagent_result`

Input: `agent_id`.

Returns:

- terminal state;
- final answer text when available;
- exit code;
- backend;
- session identifier when available;
- branch/worktree;
- commit list for the child branch relative to its base;
- diff/stat summary;
- paths to local structured trace/result artifacts;
- bounded stderr/trace tail, with secret redaction.

It must not dump an unbounded JSONL trace into MCP output.

### 7.5 `subagent_followup`

Inputs:

```json
{
  "agent_id": "sa_...",
  "message": "address reviewer findings..."
}
```

Semantics:

- follow-up is only allowed after the prior child turn reached a resumable
  terminal state;
- it must continue the **same Codex session** when the installed CLI provides
  resumable `codex exec` support;
- the broker capability-probes the local CLI instead of assuming command
  syntax;
- if the installed CLI cannot resume the recorded session, the tool returns
  a structured `CAPABILITY_UNAVAILABLE` error;
- it must never silently spawn a new unrelated session and call that a
  follow-up;
- the same worktree/branch is reused for write-capable agents.

### 7.6 `subagent_list`

Returns bounded metadata for known agents, optionally filtered by lifecycle
state.

### 7.7 `subagent_cancel`

Requests cancellation of a queued/running child.

Behavior:

- queued child -> remove from queue and mark `CANCELLED`;
- running child -> graceful termination first, force termination after a
  bounded grace period;
- cancellation must target the child process tree owned by that `agent_id`;
- it must never use broad process-name killing.

### 7.8 `subagent_cleanup`

Explicitly release terminal agent runtime files/worktree when safe.

Default behavior:

- refuse cleanup of a worktree containing uncommitted changes;
- refuse cleanup when collected result metadata is incomplete;
- preserve final compact audit metadata unless `purge_metadata=true` is
  explicitly requested;
- never auto-delete a dirty child workspace.

## 8. Agent roles

v1 ships with five role profiles.

### `implementer`

Purpose:

- implement one bounded task;
- follow provided plan/spec;
- run named tests;
- commit scoped changes when the task requires commits;
- report exact verification evidence.

### `reviewer`

Purpose:

- inspect a specified range/ref/package;
- no code mutation by default;
- return spec-compliance and quality findings;
- do not fix findings.

Default workspace: `read_only`.

### `researcher`

Purpose:

- inspect repository/source material;
- gather evidence;
- no code mutation unless a later explicit task changes role.

Default workspace: `read_only`.

### `tester`

Purpose:

- run/extend verification in an isolated worktree;
- may create test-only changes when explicitly tasked.

### `security-reviewer`

Purpose:

- inspect changes for concrete security risks;
- read-only by default;
- no secret discovery sweep outside the authorized repository.

Role profiles are prompt/control templates. A role name is not proof of an
independent agent; independence is established by the broker process/session
record.

## 9. Child context isolation

The broker must not forward the entire parent transcript.

Each child receives only:

1. role instructions;
2. explicit task text;
3. repository path/worktree;
4. explicit plan/spec/brief paths named by the caller;
5. explicit review/result artifact paths when applicable;
6. repository `AGENTS.md` instructions available through the child workspace.

This matches the context-hygiene goal of native isolated subagent forks.

The broker must not automatically include:

- previous chat history;
- unrelated user memories;
- credentials;
- parent tool outputs;
- other agents' traces.

## 10. Codex CLI backend

The mandatory v1 backend is named:

```text
codex_cli
```

### 10.1 Capability probe

At server start and on explicit refresh, the backend probes the installed
binary using read-only commands such as:

```text
codex --version
codex exec --help
codex exec resume --help
```

The implementation must derive supported features from actual output.

The probe records:

- Codex version string;
- whether `exec` exists;
- whether JSON/JSONL event output is supported;
- whether resumable exec exists;
- optional supported sandbox/approval flags required by the broker.

If required spawn primitives are absent, the broker reports itself
unavailable instead of emulating a fake child.

### 10.2 Spawn process

The backend launches Codex with Node's process-spawn API using:

- an executable path determined by configuration/path lookup;
- an argument array;
- `shell: false`;
- child working directory set to the authorized read-only workspace or child
  worktree;
- structured JSON/JSONL output enabled.

No task text is interpolated into a shell command.

The backend persists stdout structured events incrementally.

### 10.3 Session identity

A spawn is not considered fully resumable until a Codex session/thread
identifier has been observed from structured output or another supported
machine-readable interface.

The implementation must not hard-code an event-field name from this spec.
Tests use fixture traces, and the live integration test verifies the actual
installed CLI event shape.

If the child can complete but no resumable identifier is exposed:

- the spawn/result is still a real independent subagent run;
- `subagent_followup` is reported unavailable for that agent;
- no synthetic "same session" claim is allowed.

### 10.4 Resume/follow-up

When resumable exec is supported, the backend invokes the installed CLI's
supported resume interface for the recorded session ID.

The implementation plan must pin the exact syntax from the CLI version used
in CI/smoke testing instead of guessing it during design.

### 10.5 Authentication

The child Codex process inherits the host's supported Codex authentication
context.

Allowed examples include:

- existing Codex/ChatGPT login state;
- `CODEX_ACCESS_TOKEN`;
- supported workload identity;
- other Codex authentication mechanisms available to the host.

The broker:

- does not create credentials;
- does not write credentials to repository files;
- does not expose credential values through MCP output;
- does not log the full child environment.

## 11. Backend abstraction

The internal broker interface must allow another real agent backend later.

Conceptual interface:

```text
probe() -> capabilities
spawn(agent_spec) -> backend_handle
status(backend_handle) -> state
wait(backend_handle, timeout) -> state
result(backend_handle) -> result
followup(backend_handle, message) -> backend_handle
cancel(backend_handle) -> state
```

v1 required implementation:

```text
codex_cli
```

Future optional implementation:

```text
openai_agents_api
```

A future hosted backend requires a separate reviewed design/credential setup
if it needs API keys, organization/project selection, billing, or
self-hosted `codex exec-server`.

The current spec does **not** authorize automatic API-key creation or hosted
agent billing configuration.

## 12. Native-first routing

The `subagent-broker` Skill must tell Codex:

1. inspect the actual current tool list;
2. if native Codex multi-agent tools are exposed, use the official native
   Superpowers subagent flow;
3. otherwise, if Subagent Broker MCP tools are exposed and healthy, use the
   broker;
4. otherwise use Superpowers inline/native execution fallback and state that
   independent subagents were unavailable.

The broker MCP itself does not attempt to call parent-harness native
`spawn_agent`; that decision belongs to the controller/Skill.

This prevents recursion and duplicate subagent layers.

## 13. Lifecycle state machine

Allowed lifecycle states:

```text
QUEUED
SPAWNING
RUNNING
COMPLETED
FAILED
TIMED_OUT
CANCEL_REQUESTED
CANCELLED
ORPHANED
```

Terminal states:

```text
COMPLETED
FAILED
TIMED_OUT
CANCELLED
ORPHANED
```

State transitions are append-audited with timestamps.

Representative transitions:

```text
QUEUED -> SPAWNING -> RUNNING -> COMPLETED
QUEUED -> CANCELLED
RUNNING -> FAILED
RUNNING -> TIMED_OUT
RUNNING -> CANCEL_REQUESTED -> CANCELLED
RUNNING -> ORPHANED
```

Illegal transitions are rejected and recorded.

## 14. Concurrency and queue

Default:

```text
max_concurrent_agents = 3
```

Configuration limits:

- minimum 1;
- maximum configurable hard ceiling 8 in v1;
- values above the hard ceiling fail validation.

Queue policy:

- FIFO within priority class;
- priorities: `normal` and `high`;
- high priority may move ahead of queued normal tasks but never interrupts an
  already-running task;
- no unlimited queue; default maximum queued agents = 32;
- overflow returns `RESOURCE_EXHAUSTED`.

These are broker limits, not claims about native Codex multi-agent slot
limits.

## 15. Repository and worktree isolation

### Read-only agents

A read-only child receives a repository/worktree path that it may inspect
under the active sandbox policy.

It must not be granted write-mode by the broker.

### Write agents

A write-capable spawn:

1. resolves `base_ref` to an exact commit;
2. creates branch:
   `subagent/<agent_id>`;
3. creates worktree:
   `.worktrees/subagents/<agent_id>`;
4. verifies the worktree belongs to the current repository;
5. launches the child in that worktree.

The broker must never create a child on `main` or directly mutate the
parent task branch.

The parent/controller decides whether to cherry-pick, merge, or reject child
commits after review.

### Collision rules

- one running write agent per worktree;
- two agents may start from the same base only in different worktrees;
- follow-up uses the original agent worktree;
- reviewer agents do not write into implementer worktrees.

## 16. Sandbox and permissions

v1 follows least privilege.

Workspace modes:

```text
read_only
worktree_write
```

The broker may map these to supported Codex sandbox/approval settings only
after capability probing.

The broker must not expose a tool parameter equivalent to unrestricted
`danger-full-access`.

Network access remains governed by the host Codex/sandbox configuration.
The broker does not silently broaden it.

Any action outside the authorized repository/worktree follows normal Codex
approval/sandbox rules.

## 17. Process containment

Every child record stores:

- PID;
- process start timestamp;
- backend handle/session identifier;
- working directory;
- state;
- timeout deadline.

Cancellation/timeout must only target processes attributable to that agent.

Where the operating system supports process groups, the implementation may
use them to terminate descendants safely.

The v1 CI target is Linux. Windows-native process-tree handling is not an
acceptance requirement for v1 and must not be claimed as verified.

## 18. Persistent state and restart recovery

The MCP server may restart while child processes exist.

On startup it scans `.superpowers/subagents/*/state.json`.

For each nonterminal record:

- if the recorded PID/start identity still matches a child owned by the
  broker, reconcile state;
- if the process is gone and no terminal result exists, mark `ORPHANED`;
- never attach to an arbitrary reused PID without start-identity evidence.

Terminal results remain readable after server restart.

No SQLite/database dependency is required in v1; atomic JSON file replacement
is sufficient.

## 19. Audit artifacts

Per agent:

```text
state.json
prompt.txt
events.jsonl
stderr.log
result.json
result.txt
```

`state.json` contains no raw secrets.

`prompt.txt` contains only the explicit child brief/control prompt, not the
parent transcript.

`result.json` contains structured lifecycle/result metadata.

The broker never commits these artifacts automatically.

## 20. Secret handling

The broker must not log the full inherited environment.

Before persisting stderr or a text event tail, redact:

- values of inherited environment variables whose names match sensitive
  classes such as `TOKEN`, `SECRET`, `PASSWORD`, `API_KEY`,
  `ACCESS_KEY`, `PRIVATE_KEY`;
- recognized credential-shaped values where practical.

Redaction is defense in depth, not permission to deliberately print secrets.

MCP result payloads contain bounded, redacted excerpts only.

## 21. MCP protocol implementation

The server follows the existing repository's stdio MCP pattern:

- JSON-RPC over stdin/stdout;
- `initialize`;
- `ping`;
- `tools/list`;
- `tools/call`;
- one JSON object per line.

Unlike GitHub Arena, the broker is stateful and asynchronous.

It must:

- never write debug prose to stdout outside JSON-RPC messages;
- send operational logs to stderr or files;
- validate tool arguments;
- return structured MCP errors without crashing the server.

## 22. Superpowers SDD integration

The primary reason for this subsystem is to enable real
`subagent-driven-development`.

Mapping:

```text
SDD implementer dispatch
  -> native spawn_agent when available
  -> otherwise subagent_spawn(role="implementer", workspace_mode="worktree_write")

SDD task reviewer
  -> native reviewer child when available
  -> otherwise subagent_spawn(role="reviewer", workspace_mode="read_only")

SDD fix round
  -> native followup_task when available
  -> otherwise subagent_followup(agent_id, findings)

SDD wait
  -> native wait_agent when available
  -> otherwise subagent_wait(agent_id)

SDD final reviewer
  -> same routing, using reviewer/security-reviewer as appropriate
```

The controller must preserve Superpowers' task briefs, report files, review
packages, ledger, and fix-round rules.

The broker does not replace Superpowers orchestration policy.

## 23. GitHub Arena integration

GitHub Arena remains a review layer, not an agent runtime.

The broker must not reinterpret Arena's strategy-card counts as actual child
counts.

A real child count is derived only from successful native spawn events or
Subagent Broker state records.

High-impact broker changes themselves require Arena review before merge.

## 24. Configuration

Proposed repository-level Codex configuration:

```toml
[features]
multi_agent = true

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

The implementation must preserve all existing plugin configuration.

Broker runtime defaults belong in a plugin-local nonsecret config file or
code constants, not user credentials.

## 25. Repository governance changes

`AGENTS.md` must add a Subagent Runtime layer.

Rules:

- prefer native Codex multi-agent tools when actually exposed;
- otherwise use Subagent Broker for workflows that require independent
  children;
- otherwise use official Superpowers inline fallback;
- never call prompt personas "subagents";
- never claim native tools existed merely because `multi_agent = true`;
- never run a write child directly on `main`;
- require review before integrating child commits;
- preserve per-agent audit evidence for high-impact tasks until branch
  completion;
- never broaden network/filesystem permissions just to make a child succeed.

## 26. Failure handling

### Codex executable missing

`subagent_spawn` returns capability unavailable. No fake child is created.

### Authentication failure

Agent enters `FAILED`; redacted error is preserved; queue continues.

### Worktree creation failure

No Codex process launches. Agent enters `FAILED`.

### Child crash

Agent enters `FAILED`; exit code and bounded redacted stderr are available.

### Timeout

Terminate the attributable child process tree and mark `TIMED_OUT`.

### MCP server restart

Reconcile process/state as defined in restart recovery.

### Resume unsupported

Initial independent runs continue to work. `subagent_followup` returns
`CAPABILITY_UNAVAILABLE`; it does not fabricate continuity.

### Dirty cleanup

Cleanup refuses and reports the changed paths/status summary.

## 27. Testing strategy

Implementation is TDD.

### Protocol tests

Use the MCP server as a subprocess and verify:

- initialization;
- exact tool list;
- malformed JSON handling;
- invalid tool args;
- unknown tool errors;
- stdout contains JSON-RPC only.

### Fake Codex executable

Tests use a deterministic fake `codex` executable that can:

- report version/help capabilities;
- emit JSONL events;
- expose a fake session identifier;
- sleep;
- fail with a chosen exit code;
- create a requested marker/commit;
- resume an existing fake session;
- spawn a descendant process for cancellation tests.

No unit test requires real model inference.

### Spawn tests

Prove:

- real distinct OS process exists while RUNNING;
- two concurrent agents have different PIDs;
- each agent has distinct state/trace/result directories;
- write agents have distinct worktrees and branches;
- parent transcript is not in child prompt.

### Follow-up tests

Prove:

- follow-up reuses the recorded session identifier;
- same child worktree is reused;
- unsupported resume returns capability error;
- a new unrelated session is never labeled follow-up.

### Queue tests

Prove:

- max 3 default concurrent agents;
- fourth agent queues;
- completing one starts the next;
- queue maximum is enforced;
- cancellation of queued agent prevents process launch.

### Worktree tests

Prove:

- base ref resolves to exact commit;
- no child branch is `main`;
- no shared write worktree;
- dirty cleanup is refused;
- unrelated worktrees are untouched.

### Security tests

Prove:

- task text cannot inject shell syntax because spawn uses `shell:false`;
- arbitrary command args/env vars cannot be passed through MCP;
- sensitive inherited env values are absent from persisted stderr/result
  excerpts;
- path traversal in base/workspace references is rejected;
- broad process-name cancellation is never used.

### Restart tests

Prove:

- completed results survive server restart;
- stale nonterminal record becomes `ORPHANED`;
- PID reuse without start identity is not adopted.

### Controller contract tests

Prove the Skill says:

- native first;
- broker second;
- inline fallback third;
- no simulated subagent claims.

## 28. Real Codex integration smoke test

Unit tests are not sufficient to claim a real subagent runtime.

After infrastructure is merged, use a supported trusted Codex remote
workspace and verify against the real installed Codex CLI.

Minimum smoke test:

1. start a fresh Codex session so the plugin/MCP tool list is reloaded;
2. verify `subagent_spawn` appears when broker plugin is enabled;
3. spawn two read-only children concurrently with different tasks;
4. record different PIDs;
5. record independent agent IDs;
6. record independent Codex session identifiers when exposed;
7. verify each trace is distinct;
8. wait for both and collect different outputs;
9. spawn a write implementer from a known base;
10. verify separate branch/worktree;
11. run a follow-up against the same session/worktree;
12. spawn an independent reviewer for that branch;
13. cancel a long-running test child and verify terminal cancellation;
14. cleanup only after worktree safety checks.

Only after this test may the project state that the fallback broker has
executed real subagents.

## 29. Native multi-agent coexistence test

In a Codex runtime that already exposes native `spawn_agent`:

- the controller must choose native tools;
- it must not start a broker child for the same dispatch;
- the broker may remain installed but idle;
- native Superpowers SDD behavior remains authoritative.

## 30. Performance and resource boundaries

Defaults:

```text
max_running = 3
max_queued = 32
default_timeout_seconds = 1800
cancel_grace_seconds = 10
wait_max_ms = 600000
```

Output boundaries:

- MCP text result excerpts are bounded;
- JSONL traces remain on disk;
- no unlimited in-memory event accumulation;
- completed child processes must release OS handles.

Configuration changes above safety ceilings require source/config review, not
a casual MCP tool argument.

## 31. Observability

`subagent_status` and `subagent_result` expose:

- agent ID;
- role;
- backend;
- lifecycle state;
- created/start/end times;
- PID while applicable;
- base ref;
- branch/worktree;
- session ID if available;
- exit code;
- timeout/cancel reason;
- commit/diff summary.

No secret or full environment data is included.

## 32. Optional future hosted backend

The internal backend abstraction intentionally allows a future
`openai_agents_api` adapter.

It is **not part of v1 acceptance** because enabling it may require:

- OpenAI API credentials;
- organization/project selection;
- separate billing;
- Agents API permissions;
- optional self-hosted sandbox / `codex exec-server` setup.

A future implementation must go through its own credential and deployment
approval. The current design does not authorize automatic API-key creation.

## 33. Initial implementation target

v1 target is:

```text
native Codex tools when exposed
        else
WhiteChronos Subagent Broker MCP
        -> codex_cli backend
        -> Linux trusted remote/network workspace
        -> isolated worktrees
        -> structured JSONL audit
        -> resumable follow-up when local CLI capability confirms it
```

Windows-native fallback execution is not a v1 acceptance criterion.

## 34. Interaction with Awesome LLM Apps work

The Awesome LLM Apps integration is paused at its implementation stage while
this subagent runtime is designed/implemented.

The prior work remains on its existing branches/artifacts and is not
silently discarded.

After Subagent Broker is implemented, merged, and passes the real Codex
smoke test:

1. resume the Awesome LLM Apps implementation;
2. run the Native implementation path;
3. run an independent Subagent-driven review/implementation pass through
   native Codex tools if available, otherwise through this broker;
4. keep separate evidence showing which path produced which commits/findings.

This satisfies the user's request to use **both Native and real
Subagent-driven execution** rather than merely renaming inline execution.

## 35. Non-goals

v1 will not:

- add spawn tools to the already-running ChatGPT session retroactively;
- pretend `multi_agent = true` guarantees tools in every harness;
- simulate agents with prompt personas;
- auto-create OpenAI API keys;
- auto-enable hosted Agents API billing;
- expose unrestricted shell execution as an MCP tool;
- allow arbitrary environment injection;
- allow agents to write directly to `main`;
- auto-cherry-pick/merge child commits;
- automatically delete dirty worktrees;
- provide verified Windows-native process-tree support;
- replace native Codex multi-agent when it exists;
- replace Superpowers orchestration;
- replace GitHub Arena review.

## 36. Acceptance criteria

The subsystem is complete when all of the following are true:

1. `subagent-broker` is registered in the WhiteChronos local marketplace;
2. its stdio MCP server exposes exactly the approved lifecycle tools;
3. `.codex/config.toml` enables the plugin/server without removing existing
   integrations;
4. `AGENTS.md` defines native -> broker -> inline fallback routing;
5. unit/integration tests prove real child OS processes with distinct PIDs;
6. write agents are isolated in separate branches/worktrees;
7. queue/concurrency limits work;
8. follow-up reuses a real Codex session when resume is supported;
9. unsupported resume is reported honestly;
10. cancellation targets only the attributable child process tree;
11. secret values are not exposed in persisted/result excerpts;
12. restart recovery does not attach to arbitrary reused PIDs;
13. no raw shell/env/CLI injection surface exists in MCP inputs;
14. repository CI/governance gates pass;
15. GitHub Arena review passes for the broker implementation;
16. infrastructure PR is merged to `main`;
17. a fresh supported Codex remote session loads the broker tools;
18. the real smoke test demonstrates at least two simultaneous independent
    children;
19. implementer + follow-up + independent reviewer flow succeeds on an
    isolated test branch/worktree;
20. only after 17–19 may documentation/reporting call the fallback system
    "real subagents";
21. the Awesome LLM Apps plan is then resumed with Native + real
    Subagent-driven execution.

## 37. Implementation boundary

This document approves **architecture only**.

It does not yet authorize production implementation.

After the user reviews and approves this committed spec, the next
Superpowers step is `writing-plans` to produce the detailed TDD
implementation plan. Implementation starts only after that plan is reviewed
and the execution method is confirmed.
