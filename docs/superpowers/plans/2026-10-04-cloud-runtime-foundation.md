# Cloud Runtime Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a repository-backed Codex Cloud environment contract, safe deterministic bootstrap, and non-live preflight for `WhiteChronos/ChatGPT` plus `WhiteChronos/subagent-broker-runtime`, without Desktop Commander, DigitalOcean, or a required user PC.

**Architecture:** Extend the existing Python control-plane package with a versioned cloud profile loader, read-only environment preflight, and bounded bootstrap executor. Store the environment profile under `datacenter/`, validate it against a schema, document the Codex Cloud UI setup/publish flow, and add CI that proves repository/config behavior without claiming live runtime capability.

**Tech Stack:** Python 3.11+ standard library, existing `runtime/schema.py`, existing `probe_codex_cli()`, pytest 8.4.1, Node.js 22.x, npm, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-04-whitechronos-cloud-control-plane-design.md`

## Global Constraints

- Codex Cloud is the preferred execution surface; GitHub is the durable source of truth.
- Desktop Commander and DigitalOcean are not dependencies.
- Preserve Runtime Doctor evidence levels and do not modify host-discovery/live-smoke behavior in this slice.
- Do not rebuild completed Arena, Broker, ECC, Matt Pocock, Awesome LLM Apps, Runtime Foundation, or independent-runtime work.
- Initial required repositories are exactly `WhiteChronos/ChatGPT` and `WhiteChronos/subagent-broker-runtime`.
- Python floor: 3.11.
- Node runtime for Arena/Broker: `>=22 <23`; preflight therefore requires Node major 22.
- Codex probing is read-only: version/help capability checks only, no model task and no credential creation.
- Bootstrap operations are hard-coded from approved repository roles; JSON must never provide executable shell.
- Never use `shell=True`.
- Never persist credential values, device codes, tokens, environment dumps, or raw Broker traces.
- Cloud profile stores secret requirement names only, never values.
- Network policy is explicit allowlist metadata; wildcards are forbidden.
- Cloud preflight proves environment preparation only. It never proves host discovery, native multi-agent, Broker host discovery, or live verification.
- CI must not run the real Broker smoke or claim live runtime proof.
- Implementation uses an isolated branch/worktree and PR/CI before merge.
- Repository-required engineering governance commands remain mandatory.

## File Structure

### Create

- `schemas/whitechronos_codex_cloud_environment_v1.schema.json`
- `datacenter/WHITECHRONOS_CODEX_CLOUD_ENVIRONMENT.json`
- `plugins/whitechronos-control-plane/runtime/cloud_model.py`
- `plugins/whitechronos-control-plane/runtime/cloud_profile.py`
- `plugins/whitechronos-control-plane/runtime/cloud_preflight.py`
- `plugins/whitechronos-control-plane/runtime/cloud_bootstrap.py`
- `plugins/whitechronos-control-plane/scripts/cloud_preflight.py`
- `plugins/whitechronos-control-plane/scripts/setup_codex_cloud.py`
- `plugins/whitechronos-control-plane/tests/test_cloud_profile.py`
- `plugins/whitechronos-control-plane/tests/test_cloud_preflight.py`
- `plugins/whitechronos-control-plane/tests/test_cloud_bootstrap.py`
- `plugins/whitechronos-control-plane/tests/test_cloud_cli.py`
- `docs/codex-cloud.md`
- `.github/workflows/whitechronos-cloud-runtime-foundation.yml`

### Modify

- `plugins/whitechronos-control-plane/README.md`
- `docs/index.md`

### Explicitly not modified

- `plugins/whitechronos-control-plane/runtime/doctor.py`
- `plugins/whitechronos-control-plane/scripts/runtime_doctor.py`
- `plugins/subagent-broker/**`
- `.codex/config.toml`
- `registry/integrations/**`

Runtime Doctor cloud handoff and registry activation-state extension are later slices.

## Core Interfaces

### `runtime/cloud_model.py`

```python
@dataclass(frozen=True)
class CloudRepositorySpec:
    full_name: str
    role: str
    required: bool

@dataclass(frozen=True)
class CloudToolchainSpec:
    python_min: tuple[int, int]
    node_major: int
    require_git: bool
    require_npm: bool
    require_codex_exec: bool
    require_codex_json: bool
    require_codex_resume: bool

@dataclass(frozen=True)
class CloudNetworkPolicy:
    mode: str
    allowed_hosts: tuple[str, ...]

@dataclass(frozen=True)
class CloudEnvironmentProfile:
    schema_version: str
    environment_name: str
    runtime_kind: str
    repositories: tuple[CloudRepositorySpec, ...]
    toolchain: CloudToolchainSpec
    network: CloudNetworkPolicy
    required_secret_names: tuple[str, ...]

@dataclass(frozen=True)
class CloudPreflightInput:
    profile: CloudEnvironmentProfile
    repo_paths: dict[str, Path]
    codex_path: str

@dataclass(frozen=True)
class CloudPreflightReport:
    checks: tuple[CheckResult, ...]
    ready: bool
    blockers: tuple[str, ...]
```

Reuse `CheckResult` and `CheckStatus` from `runtime/model.py`.

### `runtime/cloud_profile.py`

```python
def load_cloud_profile(repo_root: Path, profile_path: Path) -> CloudEnvironmentProfile: ...
def validate_allowed_host(host: str) -> None: ...
def validate_secret_name(name: str) -> None: ...
```

### `runtime/cloud_preflight.py`

```python
def run_cloud_preflight(inputs: CloudPreflightInput) -> CloudPreflightReport: ...
def cloud_report_to_json(report: CloudPreflightReport) -> dict[str, object]: ...
def render_cloud_report(report: CloudPreflightReport) -> str: ...
```

### `runtime/cloud_bootstrap.py`

```python
@dataclass(frozen=True)
class BootstrapStep:
    repository: str
    cwd: Path
    argv: tuple[str, ...]

@dataclass(frozen=True)
class BootstrapResult:
    step: BootstrapStep
    returncode: int
    stdout_tail: str
    stderr_tail: str

def build_bootstrap_plan(
    profile: CloudEnvironmentProfile,
    repo_paths: dict[str, Path],
) -> tuple[BootstrapStep, ...]: ...

def execute_bootstrap_plan(
    steps: tuple[BootstrapStep, ...],
    *,
    apply: bool,
    timeout_seconds: float = 300.0,
) -> tuple[BootstrapResult, ...]: ...
```

Approved role mapping:

```text
consumer -> python -m pip install -r requirements-dev.txt
broker   -> npm ci
```

No command string comes from JSON. Unknown roles fail closed.

## Initial Cloud Profile Values

```text
schema_version: whitechronos-codex-cloud/v1
environment_name: whitechronos-control-plane
runtime_kind: codex_cloud

repositories:
- WhiteChronos/ChatGPT, role=consumer, required=true
- WhiteChronos/subagent-broker-runtime, role=broker, required=true

toolchain:
- python_min = 3.11
- node_major = 22
- git required
- npm required
- Codex exec required
- Codex JSON output required
- Codex resume required

network:
- mode = explicit_allowlist
- allowed metadata hosts:
  - registry.npmjs.org
  - pypi.org
  - files.pythonhosted.org

required_secret_names: []
```

GitHub access is provided by the Codex Cloud/GitHub connection and repository inclusion, not by storing a GitHub credential in this profile.

## Review Focus

1. **Wrong/missing repository or wrong Git remote:** fail with the exact repository as blocker.
2. **Secret material in profile:** reject unknown fields; accept secret names only; never serialize environment values.
3. **Unsupported toolchain:** Python <3.11, Node !=22, missing npm/Git, or missing Codex JSON capability means `ready=false`.
4. **Over-broad network metadata:** reject wildcards, URLs, empty/duplicate hosts.
5. **False runtime proof:** Cloud preflight output must not claim host/live verification; CI enforces the separation.

---

### Task 1: Versioned Codex Cloud Profile Contract

**Files:** schema, Data Center profile, `cloud_model.py`, `cloud_profile.py`, `test_cloud_profile.py`.

**Interfaces:** Produces the cloud dataclasses and profile loader used by every later task.

- [ ] **Step 1: Write failing profile tests**

```python
def test_profile_loads_exact_initial_repositories():
    profile = load_cloud_profile(REPO, PROFILE)
    assert tuple(repo.full_name for repo in profile.repositories) == (
        "WhiteChronos/ChatGPT",
        "WhiteChronos/subagent-broker-runtime",
    )
    assert tuple(repo.role for repo in profile.repositories) == ("consumer", "broker")
    assert profile.runtime_kind == "codex_cloud"
    assert profile.toolchain.python_min == (3, 11)
    assert profile.toolchain.node_major == 22
    assert profile.required_secret_names == ()

def test_profile_rejects_unknown_top_level_field(tmp_path): ...
def test_profile_rejects_secret_value_field(tmp_path): ...
def test_profile_rejects_wildcard_or_url_allowed_host(tmp_path): ...
def test_profile_rejects_duplicate_repository_or_host(tmp_path): ...
def test_profile_accepts_secret_names_only(tmp_path): ...
```

- [ ] **Step 2: Verify RED**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_profile.py`

Expected: FAIL because cloud profile modules do not exist.

- [ ] **Step 3: Implement cloud dataclasses** in `cloud_model.py`.

- [ ] **Step 4: Add schema** with `additionalProperties: false`, fixed schema/runtime values, roles `consumer|broker`, Python 3.11, Node 22, explicit allowlist mode, and string-only secret names. Use only features supported by the existing subset validator.

- [ ] **Step 5: Implement semantic validation**

`load_cloud_profile()` must resolve profile under repo root, validate schema, reject duplicate repositories/hosts, require the exact initial repository set, accept only bare DNS hosts, reject wildcards/schemes/ports/paths, validate secret names with `^[A-Z][A-Z0-9_]*$`, return immutable dataclasses, and never inspect environment values.

- [ ] **Step 6: Add the initial Data Center profile** with exactly the pinned values above.

- [ ] **Step 7: Verify GREEN**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_profile.py`

Expected: PASS.

- [ ] **Step 8: Commit**

`git commit -m "feat: define WhiteChronos Codex Cloud environment contract"`

---

### Task 2: Read-only Cloud Repository and Toolchain Preflight

**Files:** `cloud_preflight.py`, `test_cloud_preflight.py`.

**Interfaces:** Consumes validated profile + explicit repo-path mapping + existing `probe_codex_cli()`; produces a deterministic preflight report.

- [ ] **Step 1: Write failing tests**

```python
def test_preflight_passes_with_expected_repositories_and_toolchain(fake_runtime): ...
def test_missing_broker_repo_is_named_blocker(tmp_path): ...
def test_wrong_git_remote_is_failure(tmp_path): ...
def test_python_below_311_blocks_readiness(monkeypatch): ...
def test_node_not_major_22_blocks_readiness(fake_runtime): ...
def test_missing_npm_or_git_blocks_readiness(fake_runtime): ...
def test_missing_codex_json_blocks_readiness(fake_runtime): ...
def test_cloud_preflight_never_claims_host_or_live_verification(fake_runtime): ...
```

- [ ] **Step 2: Verify RED**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_preflight.py`

- [ ] **Step 3: Implement repository identity checks**

Require explicit path per required repository, valid Git worktree, `git remote get-url origin`, normalization of GitHub HTTPS/SSH remotes, and exact `owner/name` match. Never search arbitrary parent directories.

- [ ] **Step 4: Implement toolchain checks**

Checks: Python version, Node 22, Git, npm, Codex version/exec/JSON/resume. All subprocess calls are shell-free and bounded; Codex reuse is read-only.

- [ ] **Step 5: Implement readiness**

`ready=True` only when profile + both repositories + full toolchain pass. No host-tool inventory is accepted.

- [ ] **Step 6: Verify GREEN**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_preflight.py`

- [ ] **Step 7: Commit**

`git commit -m "feat: add Codex Cloud environment preflight"`

---

### Task 3: Bounded, Idempotent Cloud Bootstrap

**Files:** `cloud_bootstrap.py`, `test_cloud_bootstrap.py`.

**Interfaces:** Consumes validated profile and explicit repo paths; produces deterministic setup steps and optional bounded execution.

- [ ] **Step 1: Write failing tests**

```python
def test_bootstrap_plan_contains_only_approved_role_commands(): ...
def test_unknown_repository_role_fails_closed(tmp_path): ...
def test_dry_run_executes_nothing(monkeypatch): ...
def test_apply_uses_shell_false_and_expected_cwd(monkeypatch): ...
def test_failed_step_stops_later_steps(monkeypatch): ...
def test_output_is_bounded_and_has_no_environment_dump(monkeypatch): ...
```

- [ ] **Step 2: Verify RED**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_bootstrap.py`

- [ ] **Step 3: Implement deterministic plan generation**

Hard-code role mapping in Python source. Require dependency files before producing runnable steps. Unknown roles fail closed. No pipes, redirects, interpolation, or arbitrary extra args.

- [ ] **Step 4: Implement execution**

Dry-run is default. `apply=True` executes sequentially with `shell=False`, bounded timeout, bounded output tails, stops after first failure, and does not create credentials.

- [ ] **Step 5: Verify GREEN**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_bootstrap.py`

- [ ] **Step 6: Commit**

`git commit -m "feat: add bounded Codex Cloud bootstrap"`

---

### Task 4: Cloud CLI Entry Points and Stable Output

**Files:** `scripts/cloud_preflight.py`, `scripts/setup_codex_cloud.py`, `test_cloud_cli.py`.

**Interfaces:** Stable CLIs for environment setup and task-start preflight.

- [ ] **Step 1: Write failing CLI tests**

Contract:

```text
cloud_preflight.py
  --repo-root PATH
  --profile PATH
  --repo-path OWNER/NAME=PATH  # repeatable
  --codex-path PATH
  --json
  --require-ready

setup_codex_cloud.py
  --repo-root PATH
  --profile PATH
  --repo-path OWNER/NAME=PATH
  --apply
  --json
```

Tests must cover stable JSON fields, exit 2 for valid-but-not-ready, dry-run default, malformed mapping exit 1, and absence of live-runtime claims.

- [ ] **Step 2: Verify RED**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_cli.py`

- [ ] **Step 3: Implement preflight CLI**

Default profile is Data Center profile. Duplicate repo mappings fail. Exit codes: 0 ready, 1 malformed/failure, 2 valid but not ready under `--require-ready`. JSON is deterministic. No secret values printed.

- [ ] **Step 4: Implement setup CLI**

Dry-run default; `--apply` required for execution. Validate profile/mappings before starting any step. JSON records argv arrays and cwd only.

- [ ] **Step 5: Verify GREEN**

`python -m pytest -q plugins/whitechronos-control-plane/tests/test_cloud_cli.py`

- [ ] **Step 6: Commit**

`git commit -m "feat: expose Codex Cloud bootstrap commands"`

---

### Task 5: Codex Cloud Publish and Recovery Runbook

**Files:** create `docs/codex-cloud.md`; modify Control Plane README and docs index; extend `test_cloud_cli.py`.

**Interfaces:** Converts repository contract into exact human/admin steps for creating and publishing a reusable Codex Cloud environment.

- [ ] **Step 1: Add failing documentation assertions**

Require the runbook to name both repositories, setup/preflight commands, Runtime Doctor, `HOST_RELOAD_REQUIRED`, `LIVE_SMOKE_READY`, and to say Desktop Commander/DigitalOcean are not required.

- [ ] **Step 2: Verify RED**

Run `test_cloud_cli.py`.

- [ ] **Step 3: Write the runbook**

It must separate repository-controlled work from Codex Cloud UI steps and instruct the user to:

1. create a personal/workspace cloud environment;
2. include exactly the two initial repositories;
3. configure only profile-declared dependency hosts;
4. keep long-lived credentials in supported secret/vault controls, never Git;
5. run `setup_codex_cloud.py --apply` with actual workspace repo paths;
6. publish the environment;
7. start a **new** task from the published environment;
8. run `cloud_preflight.py --require-ready`;
9. continue to Runtime Doctor Cloud Handoff only after preflight passes;
10. never run Broker live smoke before Runtime Doctor reports `LIVE_SMOKE_READY=YES`.

State that published-environment changes apply to new tasks; existing tasks retain their current workspace state.

- [ ] **Step 4: Add current official OpenAI references**

Include the current Codex Cloud help page, Codex plan/access help page, OpenAI-hosted environment guide, and environment security guide.

- [ ] **Step 5: Update README/index** with profile location, dry-run setup, preflight, runbook link, and the statement that preflight is not live-runtime proof.

- [ ] **Step 6: Verify GREEN**

Run `test_cloud_cli.py`.

- [ ] **Step 7: Commit**

`git commit -m "docs: add WhiteChronos Codex Cloud runbook"`

---

### Task 6: CI Contract, Regression Gates, and Final Review

**Files:** create `.github/workflows/whitechronos-cloud-runtime-foundation.yml`; extend tests only as needed for workflow contract.

**Interfaces:** CI proof for Cloud profile/preflight/bootstrap without live overclaiming.

- [ ] **Step 1: Write failing workflow-contract assertions**

Require the workflow to run the four Cloud test files and forbid the real Broker smoke, live-smoke enablement, or literal credential assignments.

- [ ] **Step 2: Verify RED**

Run the owning test file; expected FAIL because workflow is absent.

- [ ] **Step 3: Add workflow**

Use Python 3.11 and Node 22. Install `requirements-dev.txt`, run all Cloud tests, run the full Control Plane suite, and run existing Runtime Doctor with fake Codex/no host inventory only as a regression check. Do not execute live smoke.

- [ ] **Step 4: Run Cloud suite**

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_cloud_profile.py   plugins/whitechronos-control-plane/tests/test_cloud_preflight.py   plugins/whitechronos-control-plane/tests/test_cloud_bootstrap.py   plugins/whitechronos-control-plane/tests/test_cloud_cli.py
```

Expected: PASS.

- [ ] **Step 5: Run full Control Plane suite**

`python -m pytest -q plugins/whitechronos-control-plane/tests`

Expected: PASS.

- [ ] **Step 6: Run Broker compatibility regression**

`node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs`

Expected: PASS. If the execution branch consumes the independent Broker repo directly, also run that repo's normal test suite; never duplicate live smoke.

- [ ] **Step 7: Run repository governance commands**

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

Expected: PASS.

- [ ] **Step 8: Run non-live Runtime Doctor regression**

Use fake Codex and `--runtime-kind unknown --json`. Expected: no host discovery without host inventory and `live_smoke_ready=false`.

- [ ] **Step 9: Apply final Review Arena**

Review secret hygiene, shell safety, network wildcard rejection, Git remote identity, toolchain errors, proof-level separation, CI truthfulness, and absence of Desktop Commander/DigitalOcean dependencies. Fix any verified defect through a new RED/GREEN cycle before PR.

- [ ] **Step 10: Commit**

`git commit -m "ci: verify WhiteChronos Cloud Runtime Foundation"`

---

## Post-Implementation Handoff — Not Part of This Plan

After implementation, review, merge, and publication of the Codex Cloud environment:

1. start a **fresh** Codex Cloud task;
2. run `cloud_preflight.py --require-ready`;
3. do not infer Broker/native host tools from the profile;
4. move to the separately planned **Runtime Doctor Cloud Handoff** slice;
5. only after Runtime Doctor reports `LIVE_SMOKE_READY=YES` run the existing real Broker smoke.

Existing smoke acceptance criteria remain unchanged: simultaneous real children, distinct PIDs and agent IDs, isolated writer worktree/branch, independent reviewer snapshot, follow-up continuity when supported, cancellation to `CANCELLED`, and redacted evidence.

## Self-Review Results

- **Spec coverage:** Covers only Slice 1: environment contract, repo set, deterministic setup, non-secret config, preflight, docs, CI. Memory/history, registry activation, Runtime Doctor handoff, Broker live proof, and recovery automation remain separate plans.
- **Step scan:** Every task has a RED/GREEN cycle and independently reviewable commit boundary.
- **Type consistency:** Cloud-only types live in `cloud_model.py`; every later task consumes the exact Task 1 interfaces.
- **Review Focus:** All five risk classes map to concrete tests.
- **Proportion:** The plan pins interfaces, tests, commands, and values without writing implementation bodies.

## Review Arena Conclusions

Four sequential review perspectives were used because the current ChatGPT host does not expose real independent subagent lifecycle tools:

1. Systems thinking / build-then-break / completeness — ephemeral Cloud compute, durable GitHub state.
2. Constraint-first / requirements checklist / explicit trade-offs — keep Desktop Commander/DigitalOcean out; do not change Runtime Doctor/live smoke here.
3. Working backwards / iterative deepening — prove correct repos/toolchain/setup first, then later runtime proof.
4. Evidence-first / test-first / edge-cases-first — CI and profile validation never become host/live proof.
