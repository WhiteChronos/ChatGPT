# WhiteChronos Runtime Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first WhiteChronos Control Plane slice: a minimal typed integration registry plus a deterministic Runtime Doctor that distinguishes repository configuration, local MCP health, Codex CLI capability, current-host discovery, and readiness for the already-existing Subagent Broker live smoke.

**Architecture:** Implement the foundation as a small Python 3.11+ standard-library package under `plugins/whitechronos-control-plane/`, with JSON registry descriptors and safe subprocess probes. The Doctor reads the current repository as evidence, starts only allowlisted local stdio MCP servers without a shell, probes Codex CLI capability without running a model task, accepts host-tool inventory as explicit input, and produces structured status without modifying source. The first slice registers one project plugin containing the `codex-runtime-doctor` Skill but does not create a new MCP server.

**Tech Stack:** Python 3.11+ standard library (`dataclasses`, `enum`, `json`, `tomllib`, `subprocess`, `selectors`, `pathlib`), pytest, existing Node.js Arena/Broker MCP servers, existing `plugins/subagent-broker/tests/fake-codex.mjs`.

**Spec:** `docs/superpowers/specs/2026-10-03-whitechronos-control-plane-design.md`

## Global Constraints

- Preserve official Superpowers as the development-process source of truth.
- Preserve GitHub Arena as review/quality control, never as a substitute for independent subagent execution.
- Do not modify or reimplement completed Arena, Subagent Broker, ECC, Matt Pocock, or Awesome LLM Apps behavior in this slice.
- Do not rerun the existing Broker TDD/Arena/PR/CI/merge history; this slice only builds the preflight needed to resume the existing post-merge smoke later.
- Never infer runtime availability from `.codex/config.toml` alone.
- Never execute arbitrary commands discovered in an MCP manifest. Runtime probes are allowlisted, shell-free, and constrained to the declared plugin root.
- Never forward the full parent environment to a probed MCP process.
- Never create credentials, cloud resources, paid infrastructure, or background services.
- Never commit raw private conversation history, secrets, environment dumps, or Broker runtime traces.
- A stale host session must produce `HOST_RELOAD_REQUIRED`, not a source-code fix.
- CI may prove repository/config/local MCP behavior but must never claim `HOST_DISCOVERED` or `LIVE_SMOKE_READY` without explicit host/runtime evidence.
- All repository mutations occur on an isolated implementation branch/worktree at execution time; never write directly to `main`.
- Existing repository governance and CI gates must remain green.

## File Structure

### Create

- `registry/integrations/schema.json` — machine-readable contract for WhiteChronos integration descriptors.
- `registry/integrations/index.json` — deterministic list of descriptors managed by the foundation slice.
- `registry/integrations/github-arena.json` — descriptor for the Arena runtime target.
- `registry/integrations/subagent-broker.json` — descriptor for the Broker runtime target.
- `plugins/whitechronos-control-plane/.codex-plugin/plugin.json` — project plugin manifest exposing control-plane Skills.
- `plugins/whitechronos-control-plane/README.md` — runtime-foundation usage and limitations.
- `plugins/whitechronos-control-plane/runtime/__init__.py`
- `plugins/whitechronos-control-plane/runtime/model.py` — enums/dataclasses shared by registry and probes.
- `plugins/whitechronos-control-plane/runtime/schema.py` — small JSON-schema-subset validator used by the registry.
- `plugins/whitechronos-control-plane/runtime/registry.py` — load and validate integration descriptors.
- `plugins/whitechronos-control-plane/runtime/mcp_probe.py` — safe stdio MCP launch resolution and `initialize` + `tools/list`.
- `plugins/whitechronos-control-plane/runtime/codex_probe.py` — read-only Codex CLI capability probe.
- `plugins/whitechronos-control-plane/runtime/doctor.py` — repository/runtime orchestration and readiness classification.
- `plugins/whitechronos-control-plane/scripts/runtime_doctor.py` — CLI entry point.
- `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/SKILL.md`
- `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/agents/openai.yaml`
- `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/references/runtime-contract.md`
- `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/references/recovery-matrix.md`
- `plugins/whitechronos-control-plane/tests/test_schema_registry.py`
- `plugins/whitechronos-control-plane/tests/test_mcp_probe.py`
- `plugins/whitechronos-control-plane/tests/test_codex_probe.py`
- `plugins/whitechronos-control-plane/tests/test_doctor.py`
- `plugins/whitechronos-control-plane/tests/test_repository_integration.py`
- `.github/workflows/whitechronos-runtime-foundation.yml`

### Modify

- `.agents/plugins/marketplace.json` — register `whitechronos-control-plane` for Codex.
- `.codex/config.toml` — enable `whitechronos-control-plane@whitechronos-repo` without changing existing plugin/MCP settings.
- `AGENTS.md` — add the Runtime Doctor truthfulness rule for runtime claims.

## Core Interfaces

### `runtime/model.py`

```python
class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    HOST_RELOAD_REQUIRED = "HOST_RELOAD_REQUIRED"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"
    SECURITY_REVIEW_REQUIRED = "SECURITY_REVIEW_REQUIRED"

@dataclass(frozen=True)
class CheckResult:
    name: str
    status: CheckStatus
    detail: str
    evidence: dict[str, object]

@dataclass(frozen=True)
class RuntimeProbeSpec:
    plugin_root: str
    mcp_config: str
    mcp_server: str
    expected_tools: tuple[str, ...]
    required_for_broker_smoke: bool

@dataclass(frozen=True)
class IntegrationDescriptor:
    id: str
    display_name: str
    source_type: str
    source: str
    license_status: str
    execution_class: str
    status: str
    controller_plugin: str | None
    skill_paths: tuple[str, ...]
    mcp_servers: tuple[str, ...]
    runtime_probe: RuntimeProbeSpec | None

@dataclass(frozen=True)
class McpProbeResult:
    server_name: str
    status: CheckStatus
    server_info: dict[str, object]
    tools: tuple[str, ...]
    missing_tools: tuple[str, ...]
    unexpected_tools: tuple[str, ...]
    stderr_tail: str

@dataclass(frozen=True)
class CodexCapabilities:
    version: str
    exec: bool
    json: bool
    resume: bool
    sandbox_read_only: bool
    sandbox_workspace_write: bool
    approval_never: bool

@dataclass(frozen=True)
class DoctorInput:
    repo_root: Path
    expected_commit: str | None
    codex_path: str
    host_tools: frozenset[str]
    runtime_kind: str

@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[CheckResult, ...]
    selected_subagent_path: str
    live_smoke_ready: bool
    blockers: tuple[str, ...]
```

### `runtime/registry.py`

```python
def load_registry(repo_root: Path) -> dict[str, IntegrationDescriptor]: ...
def load_descriptor(repo_root: Path, descriptor_path: Path) -> IntegrationDescriptor: ...
```

### `runtime/mcp_probe.py`

```python
@dataclass(frozen=True)
class McpLaunchSpec:
    command: str
    args: tuple[str, ...]
    cwd: Path
    env: dict[str, str]

def resolve_mcp_launch(
    repo_root: Path,
    descriptor: IntegrationDescriptor,
    *,
    codex_path: str = "codex",
) -> McpLaunchSpec: ...

def probe_stdio_mcp(
    launch: McpLaunchSpec,
    *,
    expected_tools: tuple[str, ...],
    timeout_seconds: float = 5.0,
) -> McpProbeResult: ...
```

### `runtime/codex_probe.py`

```python
def probe_codex_cli(
    codex_path: str,
    *,
    timeout_seconds: float = 5.0,
) -> CodexCapabilities: ...
```

The capability semantics must match the existing Broker backend:

- `version`: `codex --version` exit 0;
- `exec`: `codex exec --help` exit 0;
- `json`: `--json` appears in exec help;
- `resume`: `codex exec resume --help` exits 0 and identifies resume;
- sandbox/approval flags are detected from exec help.

### `runtime/doctor.py`

```python
def run_doctor(inputs: DoctorInput) -> DoctorReport: ...
def report_to_json(report: DoctorReport) -> dict[str, object]: ...
def render_report(report: DoctorReport) -> str: ...
```

## Review Focus

These five failure modes must be explicitly pinned by tests:

1. **Malicious or unsupported MCP launch command** — descriptor points to a shell/arbitrary executable; expected behavior: never execute it, return `SECURITY_REVIEW_REQUIRED`.
2. **Local MCP healthy but current host tool inventory is incomplete** — expected behavior: `HOST_RELOAD_REQUIRED`, no source mutation recommendation.
3. **Codex binary missing or lacks `exec --json`** — expected behavior: capability check reports unavailable and `LIVE_SMOKE_READY=false` without crashing.
4. **Commit mismatch or dirty worktree when strict smoke readiness is requested** — expected behavior: block live smoke even if local MCPs are healthy.
5. **CI/no-host context** — host tools are not supplied; expected behavior: local checks may pass, host checks stay `UNAVAILABLE`, and CI never reports live smoke ready.

---

### Task 1: Minimal Integration Registry and Typed Validation

**Files:**
- Create: `registry/integrations/schema.json`
- Create: `registry/integrations/index.json`
- Create: `registry/integrations/github-arena.json`
- Create: `registry/integrations/subagent-broker.json`
- Create: `plugins/whitechronos-control-plane/runtime/__init__.py`
- Create: `plugins/whitechronos-control-plane/runtime/model.py`
- Create: `plugins/whitechronos-control-plane/runtime/schema.py`
- Create: `plugins/whitechronos-control-plane/runtime/registry.py`
- Test: `plugins/whitechronos-control-plane/tests/test_schema_registry.py`

**Interfaces:**
- Consumes: current Arena/Broker plugin paths and their existing MCP tool contracts.
- Produces: `IntegrationDescriptor`, `RuntimeProbeSpec`, and `load_registry(repo_root)` for all later tasks.

- [ ] **Step 1: Write the failing registry tests**

Create tests with these exact behaviors:

```python
def test_registry_loads_arena_and_broker_descriptors():
    registry = load_registry(REPO)
    assert tuple(registry) == ("github-arena", "subagent-broker")
    assert registry["github-arena"].runtime_probe.expected_tools == (
        "arena_plan", "arena_cards", "arena_rubric", "arena_review_checklist",
    )
    assert registry["subagent-broker"].runtime_probe.expected_tools == (
        "subagent_spawn", "subagent_status", "subagent_wait", "subagent_result",
        "subagent_followup", "subagent_list", "subagent_cancel", "subagent_cleanup",
    )

def test_registry_rejects_duplicate_ids(tmp_path):
    ...

def test_registry_rejects_unknown_execution_class(tmp_path):
    ...

def test_registry_rejects_runtime_probe_outside_declared_plugin_root(tmp_path):
    ...
```

- [ ] **Step 2: Run the registry tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_schema_registry.py
```

Expected: FAIL because the control-plane registry/runtime modules do not exist yet.

- [ ] **Step 3: Implement the minimal schema subset validator**

Implement:

```python
def validate_schema_subset(value: object, schema: dict[str, object], path: str = "$") -> None: ...
```

Supported schema keywords in this slice:

- `type`;
- `enum`;
- `const`;
- `required`;
- `properties`;
- `additionalProperties`;
- `items`;
- `minLength`.

Raise `ValueError` with the failing JSON path.

Do not import the Awesome controller validator; the Control Plane owns a small generic validator so later factory/history schemas can reuse it without cross-plugin coupling.

- [ ] **Step 4: Implement the registry schema and loader**

Define `registry/integrations/schema.json` with:

- `schema_version = 1`;
- deterministic integration IDs;
- source types: `local`, `upstream_git`, `external_reference`, `official_plugin`;
- execution classes compatible with existing WhiteChronos risk vocabulary;
- optional `runtime_probe`;
- `runtime_probe.plugin_root`, `mcp_config`, and referenced server path constrained by loader logic to the declared repository plugin root.

Create only two initial descriptors:

- `github-arena`;
- `subagent-broker`.

Do not migrate Superpowers/ECC/Matt/Awesome in this slice.

- [ ] **Step 5: Run the registry tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_schema_registry.py
```

Expected: PASS.

- [ ] **Step 6: Commit Task 1**

```bash
git add registry/integrations plugins/whitechronos-control-plane/runtime plugins/whitechronos-control-plane/tests/test_schema_registry.py
git commit -m "feat: add WhiteChronos runtime integration registry"
```

---

### Task 2: Safe Local MCP stdio Probe

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/mcp_probe.py`
- Create: `plugins/whitechronos-control-plane/tests/test_mcp_probe.py`
- Reuse: `plugins/github-arena/mcp-server/mcp_server.mjs`
- Reuse: `plugins/subagent-broker/mcp-server/mcp_server.mjs`
- Reuse: `plugins/subagent-broker/tests/fake-codex.mjs`

**Interfaces:**
- Consumes: `IntegrationDescriptor.runtime_probe` from Task 1.
- Produces: `McpLaunchSpec`, `resolve_mcp_launch()`, and `probe_stdio_mcp()` for the Doctor.

- [ ] **Step 1: Write failing MCP probe tests**

Required tests:

```python
def test_arena_local_probe_lists_exact_expected_tools():
    ...

def test_broker_local_probe_lists_exact_expected_tools_with_fake_codex():
    ...

def test_probe_rejects_shell_or_unknown_command_without_execution(tmp_path):
    ...

def test_probe_reports_missing_tool_as_failure(tmp_path):
    ...

def test_probe_times_out_and_terminates_child(tmp_path):
    ...
```

For the real repository Broker probe test, set `SUBAGENT_BROKER_CODEX_PATH` to the existing `plugins/subagent-broker/tests/fake-codex.mjs`.

- [ ] **Step 2: Run MCP tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_mcp_probe.py
```

Expected: FAIL because `mcp_probe.py` does not exist.

- [ ] **Step 3: Implement secure launch resolution**

`resolve_mcp_launch()` must:

1. read only the descriptor-declared `.mcp.json`;
2. resolve the declared server by exact name;
3. require `type == "stdio"`;
4. reject shell launchers or unsupported commands with `SECURITY_REVIEW_REQUIRED`;
5. in this slice, allow executable `node` only for repository MCP probes;
6. resolve `cwd` and script arguments under the declared `plugin_root`;
7. never pass `shell=True`;
8. build a minimal environment containing only safe process variables required for Node/Git/Codex lookup plus explicit `SUBAGENT_BROKER_CODEX_PATH` when probing Broker.

Do not forward arbitrary parent secret variables.

- [ ] **Step 4: Implement the MCP protocol probe**

`probe_stdio_mcp()` must:

1. spawn the child with pipes;
2. send line-delimited JSON-RPC `initialize`;
3. wait for matching response ID;
4. send `tools/list`;
5. parse exact tool names;
6. compare them to the descriptor's expected tools;
7. capture bounded stderr tail;
8. terminate the child on success, error, or timeout;
9. return structured `McpProbeResult`;
10. never call any discovered MCP tool.

Use `selectors.DefaultSelector` or an equivalently bounded standard-library mechanism; no blocking read without timeout.

- [ ] **Step 5: Run MCP tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_mcp_probe.py
```

Expected: PASS and exact Arena/Broker tool lists match current repository contracts.

- [ ] **Step 6: Commit Task 2**

```bash
git add plugins/whitechronos-control-plane/runtime/mcp_probe.py plugins/whitechronos-control-plane/tests/test_mcp_probe.py
git commit -m "feat: add safe WhiteChronos MCP runtime probes"
```

---

### Task 3: Codex CLI Capability Probe

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/codex_probe.py`
- Create: `plugins/whitechronos-control-plane/tests/test_codex_probe.py`
- Reuse: `plugins/subagent-broker/tests/fake-codex.mjs`
- Reference behavior: `plugins/subagent-broker/mcp-server/codex_cli_backend.mjs`

**Interfaces:**
- Consumes: explicit `codex_path`.
- Produces: `CodexCapabilities` using the same capability semantics as Broker.

- [ ] **Step 1: Write failing Codex capability tests**

```python
def test_fake_codex_reports_broker_compatible_capabilities():
    caps = probe_codex_cli(str(FAKE_CODEX))
    assert caps.version == "codex-cli 99.0.0"
    assert caps.exec is True
    assert caps.json is True
    assert caps.resume is True
    assert caps.sandbox_read_only is True
    assert caps.sandbox_workspace_write is True
    assert caps.approval_never is True

def test_missing_codex_is_unavailable_without_exception():
    ...

def test_exec_without_json_is_not_smoke_capable(tmp_path):
    ...

def test_probe_never_runs_a_model_task(tmp_path):
    ...
```

The last test uses a fake executable that records argv and fails if invoked without `--help` or `--version`.

- [ ] **Step 2: Run Codex probe tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_codex_probe.py
```

Expected: FAIL because `codex_probe.py` does not exist.

- [ ] **Step 3: Implement read-only capability probing**

`probe_codex_cli()` runs only:

```text
codex --version
codex exec --help
codex exec resume --help
```

with:

- `shell=False`;
- bounded timeout;
- minimal environment;
- no prompt/model execution;
- no credential creation.

Match the existing Broker capability definitions exactly.

- [ ] **Step 4: Run Codex probe tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_codex_probe.py
```

Expected: PASS.

- [ ] **Step 5: Commit Task 3**

```bash
git add plugins/whitechronos-control-plane/runtime/codex_probe.py plugins/whitechronos-control-plane/tests/test_codex_probe.py
git commit -m "feat: add Codex runtime capability probe"
```

---

### Task 4: Runtime Doctor Classification and Smoke Readiness

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/doctor.py`
- Create: `plugins/whitechronos-control-plane/tests/test_doctor.py`

**Interfaces:**
- Consumes: registry, MCP probe, Codex probe, repository Git/config state, explicit host tool inventory, runtime kind.
- Produces: `DoctorReport`, JSON representation, human-readable table, and the truthfully gated `live_smoke_ready` boolean.

- [ ] **Step 1: Write failing Doctor tests for repository/runtime separation**

Required tests:

```python
def test_configured_is_not_host_discovered():
    ...

def test_local_mcp_pass_plus_missing_host_tools_requires_reload():
    ...

def test_partial_broker_host_tool_set_is_not_pass():
    ...

def test_no_host_inventory_is_unavailable_not_fail():
    ...

def test_missing_codex_json_blocks_live_smoke():
    ...

def test_commit_mismatch_blocks_strict_smoke_readiness():
    ...

def test_dirty_worktree_blocks_strict_smoke_readiness():
    ...

def test_trusted_remote_with_complete_broker_tools_is_live_smoke_ready():
    ...

def test_stale_host_never_recommends_source_mutation():
    ...
```

- [ ] **Step 2: Run Doctor tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_doctor.py
```

Expected: FAIL because `doctor.py` does not exist.

- [ ] **Step 3: Implement repository/config checks**

The Doctor must create named checks for at least:

```text
REPOSITORY_ROOT
GIT_HEAD
WORKTREE_STATE
CODEX_CONFIG_PARSE
MARKETPLACE_PARSE
SUPERPOWERS_CONFIG
ARENA_PLUGIN_MANIFEST
ARENA_MCP_CONFIG
ARENA_MCP_LOCAL_INITIALIZE
ARENA_MCP_LOCAL_TOOLS
BROKER_PLUGIN_MANIFEST
BROKER_MCP_CONFIG
BROKER_MCP_LOCAL_INITIALIZE
BROKER_MCP_LOCAL_TOOLS
NODE_VERSION
GIT_VERSION
CODEX_VERSION
CODEX_EXEC
CODEX_EXEC_JSON
CODEX_RESUME
NATIVE_MULTI_AGENT_CONFIG
HOST_ARENA_DISCOVERY
HOST_BROKER_DISCOVERY
HOST_NATIVE_SUBAGENT_DISCOVERY
LIVE_SMOKE_READY
```

Parse `.codex/config.toml` with `tomllib`, not regex.

- [ ] **Step 4: Implement host discovery semantics**

Input is the explicit current-host tool inventory supplied to `DoctorInput.host_tools`.

Rules:

- all four Arena tools present -> `HOST_ARENA_DISCOVERY=PASS`;
- Arena local MCP PASS but one or more expected Arena tools absent from a supplied host inventory -> `HOST_RELOAD_REQUIRED`;
- all eight Broker tools present -> `HOST_BROKER_DISCOVERY=PASS`;
- Broker local MCP PASS but host inventory is partial/missing -> `HOST_RELOAD_REQUIRED`;
- no host inventory supplied -> host checks `UNAVAILABLE`, not `FAIL`;
- `spawn_agent` present -> `HOST_NATIVE_SUBAGENT_DISCOVERY=PASS`; otherwise informational `UNAVAILABLE`.

Do not call an Arena card or prompt persona an independent child.

- [ ] **Step 5: Implement Broker smoke readiness**

`live_smoke_ready=True` only when all are true:

1. repository exists;
2. expected commit matches when `expected_commit` is supplied;
3. worktree is clean;
4. Broker descriptor/config/local MCP checks PASS;
5. Codex `exec` and `--json` capabilities are true;
6. runtime kind is `trusted_remote` or `codex_cloud`;
7. all eight Broker host tools are actually present;
8. no `FAIL`, `SECURITY_REVIEW_REQUIRED`, or required `USER_ACTION_REQUIRED` blocker exists.

Native Codex multi-agent availability does **not** substitute for this Broker-specific smoke gate.

- [ ] **Step 6: Implement selected workflow path**

`selected_subagent_path`:

```text
native_codex_multi_agent  if spawn_agent is actually present
subagent_broker           else if all eight broker tools are actually present
superpowers_inline        otherwise
```

This field is for workflow routing only. It does not alter the Broker live-smoke requirements.

- [ ] **Step 7: Run Doctor tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_doctor.py
```

Expected: PASS.

- [ ] **Step 8: Run all foundation unit tests**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_schema_registry.py plugins/whitechronos-control-plane/tests/test_mcp_probe.py plugins/whitechronos-control-plane/tests/test_codex_probe.py plugins/whitechronos-control-plane/tests/test_doctor.py
```

Expected: PASS with zero failures.

- [ ] **Step 9: Commit Task 4**

```bash
git add plugins/whitechronos-control-plane/runtime/doctor.py plugins/whitechronos-control-plane/tests/test_doctor.py
git commit -m "feat: add WhiteChronos runtime readiness doctor"
```

---

### Task 5: CLI, Runtime Doctor Skill, and Codex Project Registration

**Files:**
- Create: `plugins/whitechronos-control-plane/scripts/runtime_doctor.py`
- Create: `plugins/whitechronos-control-plane/.codex-plugin/plugin.json`
- Create: `plugins/whitechronos-control-plane/README.md`
- Create: `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/SKILL.md`
- Create: `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/agents/openai.yaml`
- Create: `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/references/runtime-contract.md`
- Create: `plugins/whitechronos-control-plane/skills/codex-runtime-doctor/references/recovery-matrix.md`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.codex/config.toml`
- Modify: `AGENTS.md`
- Test: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`

**Interfaces:**
- Consumes: `run_doctor()`, `report_to_json()`, `render_report()`.
- Produces: user/agent-facing CLI and reusable project Skill.

- [ ] **Step 1: Write failing repository integration tests**

Required assertions:

```python
def test_marketplace_registers_whitechronos_control_plane():
    ...

def test_codex_config_enables_control_plane_without_changing_existing_layers():
    ...

def test_plugin_manifest_exposes_runtime_doctor_skill_only_in_this_slice():
    ...

def test_agents_md_requires_runtime_doctor_for_runtime_claims():
    ...

def test_skill_forbids_config_only_success_claims():
    ...

def test_skill_routes_host_reload_without_source_changes():
    ...
```

- [ ] **Step 2: Write failing CLI tests**

Add subprocess tests for:

```text
--json
--expected-commit <sha>
--codex-path <path>
--runtime-kind unknown|trusted_remote|codex_cloud
--host-tool <name>        repeatable
--require-live-smoke-ready
```

Exit contract:

- exit `0`: requested diagnostic level is satisfied;
- exit `1`: verified local/config failure or security-review blocker;
- exit `2`: no verified defect, but user action/runtime reload/capability is required for the requested strict readiness.

- [ ] **Step 3: Run repository/CLI tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
```

Expected: FAIL.

- [ ] **Step 4: Implement CLI**

The CLI must:

- default repo root to the current repository;
- accept repeated `--host-tool`;
- print a compact human table by default;
- emit deterministic JSON under `--json`;
- never mutate source/config;
- never launch the live Broker smoke itself;
- emit the exact next action:
  - `HOST_RELOAD_REQUIRED` -> fresh Codex environment/session;
  - verified local failure -> debugging/bugfix path;
  - `LIVE_SMOKE_READY=YES` -> existing smoke command may run.

- [ ] **Step 5: Create the project plugin and Skill**

Plugin name: `whitechronos-control-plane`.

Version for first slice: `0.1.0`.

The plugin exposes `./skills/` and has no MCP server in this slice.

The Skill trigger description must cover:

- “is Arena/Broker/Superpowers really running?”;
- runtime/MCP/tool discovery problems;
- stale Codex sessions;
- “can we run the Broker smoke?”;
- requests to verify Codex runtime readiness.

The Skill must instruct agents to:

1. use evidence from the Doctor;
2. distinguish CONFIGURED / LOCAL_RUNTIME_HEALTHY / HOST_DISCOVERED / LIVE_VERIFIED;
3. never treat config as runtime proof;
4. avoid source changes for `HOST_RELOAD_REQUIRED`;
5. run the existing `smoke_real_codex.mjs` only when readiness says YES;
6. preserve the existing Broker smoke acceptance criteria.

- [ ] **Step 6: Register the plugin without changing existing plugin settings**

Append:

```toml
[plugins."whitechronos-control-plane@whitechronos-repo"]
enabled = true
```

Do not modify existing Arena, Superpowers, ECC, Matt, Awesome, or Broker settings.

Register the local plugin in `.agents/plugins/marketplace.json` with:

- local path `./plugins/whitechronos-control-plane`;
- `INSTALLED_BY_DEFAULT`;
- product `CODEX`;
- category `Developer Tools`.

- [ ] **Step 7: Add the Runtime Doctor rule to AGENTS.md**

Add a focused section stating:

- runtime claims require Runtime Doctor evidence when the Doctor is available;
- config alone is never runtime proof;
- `HOST_RELOAD_REQUIRED` must not trigger code changes;
- real subagent claims still require lifecycle evidence;
- existing routing order remains unchanged.

Do not duplicate the full bootstrap design from later slices.

- [ ] **Step 8: Run repository/CLI tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
```

Expected: PASS.

- [ ] **Step 9: Commit Task 5**

```bash
git add plugins/whitechronos-control-plane .agents/plugins/marketplace.json .codex/config.toml AGENTS.md
git commit -m "feat: register WhiteChronos Runtime Doctor"
```

---

### Task 6: Dedicated CI and End-to-End Local Verification

**Files:**
- Create: `.github/workflows/whitechronos-runtime-foundation.yml`
- Modify only if test hardening requires it: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`

**Interfaces:**
- Consumes: all Runtime Foundation code/tests.
- Produces: deterministic PR/CI proof of registry, local MCP, Codex fake capability, Skill/plugin integration, and honest host-unavailable behavior.

- [ ] **Step 1: Write the failing CI contract test**

Extend repository integration tests to require the workflow file and assert it runs:

```text
python -m pytest -q plugins/whitechronos-control-plane/tests
```

and that it does not run:

```text
SUBAGENT_BROKER_LIVE=1
smoke_real_codex.mjs
```

in CI.

- [ ] **Step 2: Run the CI contract test and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
```

Expected: FAIL because the workflow does not exist.

- [ ] **Step 3: Add the dedicated workflow**

Trigger on:

- pull requests touching Runtime Foundation paths;
- pushes to its implementation branch paths;
- manual dispatch.

Required workflow checks:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
```

Then execute a repository-local Doctor integration probe using fake Codex and **no host tools**, verifying:

- Arena local MCP PASS;
- Broker local MCP PASS;
- host discovery UNAVAILABLE;
- live smoke readiness false.

The workflow must not claim host/runtime success and must not run the model-backed live smoke.

- [ ] **Step 4: Run the full Runtime Foundation suite locally**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
```

Expected: PASS.

- [ ] **Step 5: Run existing Broker protocol/repository tests as compatibility checks**

Run:

```bash
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
```

Expected: PASS.

- [ ] **Step 6: Run existing Awesome Codex integration regression**

Run:

```bash
python -m pytest -q plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
```

Expected: PASS.

- [ ] **Step 7: Run repository-required governance commands**

Run the commands required by current `AGENTS.md`:

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

Expected: PASS.

- [ ] **Step 8: Run Runtime Doctor against the implementation branch**

Run with fake Codex and no host tools:

```bash
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py \
  --repo . \
  --codex-path plugins/subagent-broker/tests/fake-codex.mjs \
  --runtime-kind unknown \
  --json
```

Expected:

- `ARENA_MCP_LOCAL_TOOLS=PASS`;
- `BROKER_MCP_LOCAL_TOOLS=PASS`;
- `HOST_ARENA_DISCOVERY=UNAVAILABLE`;
- `HOST_BROKER_DISCOVERY=UNAVAILABLE`;
- `LIVE_SMOKE_READY=false`.

- [ ] **Step 9: Apply final Review Arena before PR**

Use at least four Arena strategy cards and review:

- command-execution safety;
- runtime-vs-config truthfulness;
- failure classification;
- compatibility with existing Broker/Arena/Superpowers;
- absence of secret/environment leakage;
- stale-host behavior;
- CI not impersonating live runtime.

Any verified finding is fixed through a new RED/GREEN cycle before PR.

- [ ] **Step 10: Commit Task 6**

```bash
git add .github/workflows/whitechronos-runtime-foundation.yml plugins/whitechronos-control-plane/tests
git commit -m "ci: verify WhiteChronos runtime foundation"
```

---

## Post-Implementation Handoff — Not Part of This Plan

After Runtime Foundation is reviewed, merged, and loaded by a **fresh trusted Codex remote/network runtime**, start the next approved slice: **Post-merge Runtime Validation**.

That slice begins with the Runtime Doctor using the actual host tool inventory. If and only if the Doctor reports `LIVE_SMOKE_READY=YES`, execute the existing command:

```bash
SUBAGENT_BROKER_LIVE=1 node plugins/subagent-broker/scripts/smoke_real_codex.mjs
```

The existing smoke acceptance criteria remain unchanged:

- independent children;
- distinct PIDs;
- distinct `agent_id` values;
- isolated worktrees/branches for write children;
- independent reviewer;
- cancellation to `CANCELLED`;
- follow-up/session continuity when supported;
- truthful `CAPABILITY_UNAVAILABLE` when resume is not available.

Do **not** add a new source-code PR merely because a fresh runtime needs to reload plugin/MCP state.
