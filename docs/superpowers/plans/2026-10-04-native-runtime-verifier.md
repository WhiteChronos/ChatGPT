# Native Runtime Verifier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `WhiteChronos/codex-native-runtime-verifier` as the independent evidence-first verifier for hosted OpenAI/Codex native multi-agent capability, proving only the runtime surface actually observed and never publishing lookalike native tools.

**Architecture:** Build a standalone Python verifier with one canonical evidence model and four adapters: Agents API event streams, Responses Multi-agent output/events, current-host tool inventory, and Codex CLI/config capability probing. Offline fixtures and mocked clients test parsers/classification, while live verification is an explicit opt-in path that requires pre-existing authorization and records scoped session evidence; CI can never produce `LIVE_VERIFIED`.

**Tech Stack:** Python 3.12, `openai==3.24.0`, `jsonschema==4.26.0`, `pytest==9.1.1`, Python standard library subprocess/JSON/dataclasses, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-03-runtime-independent-architecture-design.md`

## Global Constraints

- New repository: `WhiteChronos/codex-native-runtime-verifier`.
- Repository visibility: **public**.
- Default branch: **main**.
- License: **MIT**.
- Initial verifier release version: **0.1.0**.
- Runtime contract: `whitechronos-runtime/v1`.
- Runtime component: `native-verifier`.
- This repository is **not an MCP server** and publishes no MCP tools.
- It MUST NOT publish or emulate `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, `interrupt_agent`, `list_agents`, or any other hosted collaboration action.
- It MUST NOT infer native multi-agent availability from `multi_agent = true` alone.
- It MUST distinguish configuration, hosted-action visibility, actual subagent creation, lifecycle evidence, and live verification.
- `LIVE_VERIFIED` is always scoped to the exact surface/runtime/session in the evidence report; Agents API proof is not proof that the current ChatGPT/Codex conversation loaded native actions, and host-inventory proof is not proof that a child actually ran.
- Current Agents API proof baseline (verified 2026-10-04): session creation enables delegation with `agent.multi_agent.enabled = true`; the harness supplies collaboration actions; `agent.session.subagent.created` includes a subagent ID.
- Current Responses Multi-agent baseline (verified 2026-10-04): the six hosted collaboration actions are exactly `spawn_agent`, `send_message`, `followup_task`, `wait_agent`, `interrupt_agent`, and `list_agents`; they are hosted actions and MUST NOT be executed by the application as function calls.
- Current Responses Multi-agent evidence items include `multi_agent_call`, `multi_agent_call_output`, and `agent_message`.
- If authoritative OpenAI docs at implementation time materially contradict the baselines above, stop with a plan-drift finding; do not silently rename evidence or weaken acceptance.
- Live Agents API verification requires a pre-existing authorized credential and explicit `--live`; the verifier never creates, persists, prints, or uploads credentials.
- Live verification MUST require an explicit model argument or environment value; no hidden paid request is launched from ordinary commands.
- CI MUST use only fixtures/mocks/local process probes and MUST NOT invoke paid model work.
- CI MUST NEVER emit `LIVE_VERIFIED`.
- No raw prompts, raw full event streams, model output bodies, authorization headers, API keys, access tokens, cookies, or credential IDs are persisted in evidence.
- Evidence export is allowlist-based and redacts values whose field names match `TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY|PRIVATE_KEY|AUTHORIZATION|COOKIE`.
- Do not modify `WhiteChronos/ChatGPT` Runtime Doctor or routing in this plan; consumer integration has its own later plan.
- Do not modify Arena or Broker runtime repositories in this plan.
- Do not run the historical Broker Task 12 smoke in this plan.
- Do not represent fixture evidence, mocked SDK behavior, `multi_agent=true`, tool-name presence, or CI as a real subagent execution.
- Repository creation is authorized only after this plan is approved and an execution method is selected.
- If the active GitHub runtime cannot create the repository, stop at repository creation with `USER_ACTION_REQUIRED`; never simulate it as a subdirectory of `WhiteChronos/ChatGPT`.

## Repository Settings

Create:

```text
owner              WhiteChronos
name               codex-native-runtime-verifier
visibility         public
default branch     main
issues             enabled
wiki               disabled
projects           disabled
license            MIT
description        Evidence-first verifier for hosted OpenAI/Codex native multi-agent runtime capability.
```

## File Structure

### Create in `WhiteChronos/codex-native-runtime-verifier`

```text
README.md
LICENSE
pyproject.toml
requirements.lock
runtime-contract.json
provenance/platform-contract.json

verifier/
├── __init__.py
├── model.py
├── classify.py
├── redact.py
├── validate.py
├── report.py
└── surfaces/
    ├── __init__.py
    ├── agents_api.py
    ├── responses_api.py
    ├── host_inventory.py
    └── codex_cli.py

schemas/
└── runtime-evidence.schema.json

fixtures/
├── agents-api/
│   ├── session-with-subagent.jsonl
│   ├── session-config-only.jsonl
│   ├── session-created-no-completion.jsonl
│   └── session-malformed.jsonl
├── responses-api/
│   ├── hosted-actions.json
│   ├── spawn-output.json
│   └── malformed-items.json
└── host-inventory/
    ├── native-complete.json
    ├── native-partial.json
    └── empty.json

scripts/
├── verify_native.py
├── export_evidence.py
└── probe_codex.py

tests/
├── contract/
│   ├── test_repository_contract.py
│   ├── test_runtime_evidence_schema.py
│   ├── test_runtime_contract.py
│   └── test_ci_contract.py
├── evidence/
│   ├── test_classification.py
│   ├── test_redaction.py
│   └── test_report.py
├── agents_api/
│   ├── test_agents_events.py
│   └── test_agents_live_contract.py
├── responses_api/
│   └── test_responses_items.py
├── host_inventory/
│   └── test_host_inventory.py
└── codex_cli/
    └── test_codex_cli.py

.github/workflows/ci.yml
```

## Canonical Evidence Model

### `verifier/model.py`

Define:

```python
class EvidenceState(str, Enum):
    CONFIG_REQUESTED = "CONFIG_REQUESTED"
    SESSION_CREATED = "SESSION_CREATED"
    MULTI_AGENT_ENABLED = "MULTI_AGENT_ENABLED"
    HOSTED_ACTIONS_AVAILABLE = "HOSTED_ACTIONS_AVAILABLE"
    SUBAGENT_CREATED = "SUBAGENT_CREATED"
    SUBAGENT_EVENT_OBSERVED = "SUBAGENT_EVENT_OBSERVED"
    SUBAGENT_COMPLETED = "SUBAGENT_COMPLETED"
    LIVE_VERIFIED = "LIVE_VERIFIED"

class VerificationVerdict(str, Enum):
    LIVE_VERIFIED = "LIVE_VERIFIED"
    CAPABILITY_UNAVAILABLE = "CAPABILITY_UNAVAILABLE"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"
    FAILED = "FAILED"
    NOT_RUN = "NOT_RUN"
```

Define immutable records:

```python
@dataclass(frozen=True)
class EvidenceItem:
    kind: str
    source: str
    event_type: str | None
    event_id: str | None
    session_id: str | None
    subagent_id: str | None
    agent_name: str | None
    action: str | None
    timestamp: str | None
    details: dict[str, object]

@dataclass(frozen=True)
class NativeVerificationReport:
    schema_version: str
    runtime_contract_version: str
    verifier_version: str
    verification_id: str
    surface: str
    live: bool
    started_at: str
    completed_at: str
    session_id: str | None
    states: tuple[EvidenceState, ...]
    verdict: VerificationVerdict
    evidence: tuple[EvidenceItem, ...]
    blockers: tuple[str, ...]
```

Allowed `surface` values:

```text
agents_api
responses_api
codex_host_inventory
codex_cli
```

### Truth table

`LIVE_VERIFIED` requires all of:

```text
live == true
surface is an approved live surface
SESSION_CREATED
MULTI_AGENT_ENABLED
HOSTED_ACTIONS_AVAILABLE
SUBAGENT_CREATED
SUBAGENT_EVENT_OBSERVED
SUBAGENT_COMPLETED
nonblank session_id
nonblank subagent_id
no credential/security blocker
```

Additional rules:

- `live == false` can never yield `LIVE_VERIFIED`, regardless of fixture contents.
- `codex_host_inventory` alone can reach `HOSTED_ACTIONS_AVAILABLE` but not `SUBAGENT_CREATED` or `LIVE_VERIFIED`.
- `codex_cli` config/probe alone can reach `CONFIG_REQUESTED` / `MULTI_AGENT_ENABLED` but not runtime creation evidence.
- `responses_api` parser can recognize hosted actions and subagent-related output, but it reaches `LIVE_VERIFIED` only if the observed payload contains a stable nonblank subagent identifier plus completion/lifecycle evidence satisfying the schema.
- Agents API is the primary v0.1 live-verification path because `agent.session.subagent.created` explicitly exposes a subagent ID.
- Missing authorization for an explicitly requested live Agents API run returns `USER_ACTION_REQUIRED`, never fake success and never auto-creates a key.
- A malformed or contradictory live event stream returns `FAILED`; absence of a capability on a valid surface returns `CAPABILITY_UNAVAILABLE`.

## Runtime Contract

`runtime-contract.json` must contain:

```json
{
  "contract_version": "whitechronos-runtime/v1",
  "component": "native-verifier",
  "component_version": "0.1.0",
  "plugin_name": null,
  "tool_contract": [],
  "supported_transports": [],
  "required_host_capabilities": [],
  "minimum_codex_version": null,
  "consumer_compatibility": {
    "whitechronos-chatgpt": ">=0"
  },
  "verification_surfaces": [
    "agents_api",
    "responses_api",
    "codex_host_inventory",
    "codex_cli"
  ]
}
```

## Platform Provenance Contract

`provenance/platform-contract.json` records only public contract metadata:

```text
verified_at = 2026-10-04
agents_api_multi_agent_enabled_path = agent.multi_agent.enabled
agents_api_subagent_created_event = agent.session.subagent.created
responses_hosted_actions =
  spawn_agent
  send_message
  followup_task
  wait_agent
  interrupt_agent
  list_agents
responses_item_types =
  multi_agent_call
  multi_agent_call_output
  agent_message
```

Include current authoritative OpenAI documentation URLs. This file contains no credentials and no copied SDK source.

## Review Focus

The five highest-risk failure classes are:

1. **False live proof** — fixtures, config, CI, or visible tool names accidentally classify as `LIVE_VERIFIED`; expected behavior: classifier refuses because live/session/subagent/completion requirements are incomplete.
2. **Cross-surface overclaim** — an Agents API live result is described as proof of the current Codex/ChatGPT session; expected behavior: every report binds verdict to one explicit `surface`, session ID, and verification ID.
3. **Hosted-action masquerading** — repository code accidentally publishes or executes hosted collaboration action names as local tools; expected behavior: contract scan fails on MCP/tool registration or developer-defined execution of `multi_agent_call`.
4. **Credential or raw-event leakage** — API key, auth headers, prompt/output body, or sensitive trace is written to evidence; expected behavior: allowlist serializer drops raw fields and redaction tests fail on any known secret.
5. **Incomplete lifecycle classified complete** — subagent-created evidence exists but no terminal/completion evidence follows; expected behavior: verdict remains `CAPABILITY_UNAVAILABLE` or `FAILED`, never `LIVE_VERIFIED`.

---

### Task 1: Create Repository, Toolchain, Runtime Contract, and Provenance

**Files:**
- Create repository: `WhiteChronos/codex-native-runtime-verifier`
- Create: `README.md`
- Create: `LICENSE`
- Create: `pyproject.toml`
- Create: `requirements.lock`
- Create: `runtime-contract.json`
- Create: `provenance/platform-contract.json`
- Test: `tests/contract/test_repository_contract.py`
- Test: `tests/contract/test_runtime_contract.py`

**Interfaces:**
- Consumes: approved Runtime Independente spec plus current public OpenAI multi-agent contracts.
- Produces: repository identity/version/dependency/provenance/runtime contract used by every later task.

- [ ] **Step 1: Create the GitHub repository with the exact settings in this plan**

Verify:

```text
full_name = WhiteChronos/codex-native-runtime-verifier
private = false
default_branch = main
```

- [ ] **Step 2: Create the Python package metadata**

`pyproject.toml` must declare Python `>=3.12,<3.13`, package version `0.1.0`, and runtime dependencies:

```text
openai==3.24.0
jsonschema==4.26.0
```

Dev dependency:

```text
pytest==9.1.1
```

Generate a real lock artifact from the selected package manager. Do not hand-author resolved transitive versions.

- [ ] **Step 3: Write RED repository/runtime contract tests**

Assert exact repository/package/version/license/runtime-contract fields and the platform provenance names listed above.

Also scan repository source and fail if any executable MCP/server registration publishes one of the six hosted action names.

- [ ] **Step 4: Run RED**

```bash
pytest -q tests/contract/test_repository_contract.py tests/contract/test_runtime_contract.py
```

Expected: FAIL until contracts/provenance exist.

- [ ] **Step 5: Implement minimum repository metadata/contracts**

README must state:

- evidence-first verifier, not a subagent runtime;
- no fake hosted tools;
- surface-scoped verdicts;
- live verification is explicit and may consume authorized API usage;
- CI never proves live native capability.

- [ ] **Step 6: Run GREEN and full current tests**

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "chore: bootstrap native runtime verifier"
```

---

### Task 2: Define Evidence Schema, Model, Redaction, and Truthful Classifier

**Files:**
- Create: `schemas/runtime-evidence.schema.json`
- Create: `verifier/model.py`
- Create: `verifier/classify.py`
- Create: `verifier/redact.py`
- Create: `verifier/validate.py`
- Test: `tests/contract/test_runtime_evidence_schema.py`
- Test: `tests/evidence/test_classification.py`
- Test: `tests/evidence/test_redaction.py`

**Interfaces:**
- Consumes: runtime contract version `whitechronos-runtime/v1`.
- Produces: `EvidenceItem`, `NativeVerificationReport`, `classify_report(...)`, `redact_evidence(...)`, and schema validation used by all adapters.

- [ ] **Step 1: Write RED schema/model tests**

Assert required fields, exact enums, unique state values, nonblank IDs when present, and rejection of unknown verdict/surface values.

- [ ] **Step 2: Write RED classifier tests**

Cover:

```text
fixture with all-looking-good events + live=false -> never LIVE_VERIFIED
multi_agent=true only -> NOT_RUN/CAPABILITY_UNAVAILABLE
hosted action names only -> HOSTED_ACTIONS_AVAILABLE only
created event with no completion -> not LIVE_VERIFIED
live Agents API + session + subagent ID + completion -> LIVE_VERIFIED
missing explicit live credentials request -> USER_ACTION_REQUIRED
contradictory/malformed live evidence -> FAILED
```

- [ ] **Step 3: Write RED secret/raw-content tests**

Inputs containing keys/values such as:

```text
OPENAI_API_KEY
Authorization
Cookie
token
password
raw_prompt
raw_output
raw_event_body
```

must not survive evidence serialization.

- [ ] **Step 4: Implement model/schema/classifier/redaction minimally**

`classify_report(...)` receives normalized evidence only; adapters do not invent verdicts independently.

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add schemas verifier tests/contract tests/evidence
git commit -m "feat: define native verification evidence contract"
```

---

### Task 3: Parse Agents API Native Subagent Events

**Files:**
- Create: `verifier/surfaces/agents_api.py`
- Create: `fixtures/agents-api/*.jsonl`
- Test: `tests/agents_api/test_agents_events.py`

**Interfaces:**
- Consumes: iterable JSON/event objects from an Agents API session stream.
- Produces: `parse_agents_api_events(events, *, live, session_id_hint=None) -> tuple[EvidenceItem, ...]`.

- [ ] **Step 1: Freeze fixture evidence from public event shapes**

Fixtures must cover:

- session created;
- multi-agent requested/enabled evidence where observable;
- `agent.session.subagent.created` with a stable subagent ID;
- subsequent subagent active/closed or other terminal/lifecycle evidence;
- config/session without delegation;
- created subagent without completion;
- malformed/unknown events.

Do not include real user prompts, API keys, model outputs, or private traces.

- [ ] **Step 2: Write RED parser tests**

Assert:

- session ID extraction;
- subagent ID extraction from `agent.session.subagent.created`;
- unknown events ignored or normalized safely;
- duplicated event IDs do not create duplicated evidence;
- completion evidence is tied to the same subagent identity;
- parser alone does not set a final verdict.

- [ ] **Step 3: Run RED**

- [ ] **Step 4: Implement normalized parser**

Use field allowlists; never retain an entire SDK event object.

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add verifier/surfaces/agents_api.py fixtures/agents-api tests/agents_api
git commit -m "feat: parse Agents API native subagent evidence"
```

---

### Task 4: Parse Responses Multi-agent Hosted Actions Without Executing Them

**Files:**
- Create: `verifier/surfaces/responses_api.py`
- Create: `fixtures/responses-api/*.json`
- Test: `tests/responses_api/test_responses_items.py`

**Interfaces:**
- Consumes: normalized Responses API output items/events.
- Produces: `parse_responses_multi_agent(items, *, live, response_id=None) -> tuple[EvidenceItem, ...]`.

- [ ] **Step 1: Freeze current hosted-action fixtures**

Cover exact six actions:

```text
spawn_agent
send_message
followup_task
wait_agent
interrupt_agent
list_agents
```

Cover item types:

```text
multi_agent_call
multi_agent_call_output
agent_message
```

- [ ] **Step 2: Write RED safety tests**

Assert the adapter:

- recognizes hosted actions;
- correlates call/output by `call_id`;
- never asks application code to execute a `multi_agent_call`;
- never registers the six action names as local/MCP tools;
- does not claim a stable subagent ID when only a task path/name exists;
- does not classify a spawn output as child completion.

- [ ] **Step 3: Run RED**

- [ ] **Step 4: Implement parser**

Return normalized evidence only.

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add verifier/surfaces/responses_api.py fixtures/responses-api tests/responses_api
git commit -m "feat: parse hosted Responses multi-agent evidence"
```

---

### Task 5: Add Host Inventory and Codex CLI/Config Adapters

**Files:**
- Create: `verifier/surfaces/host_inventory.py`
- Create: `verifier/surfaces/codex_cli.py`
- Create: `fixtures/host-inventory/*.json`
- Create: `scripts/probe_codex.py`
- Test: `tests/host_inventory/test_host_inventory.py`
- Test: `tests/codex_cli/test_codex_cli.py`

**Interfaces:**
- Consumes:
  - an explicitly observed current-host tool/action inventory;
  - a Codex executable path and optional config document.
- Produces:
  - `classify_host_inventory(tool_names, *, observed) -> tuple[EvidenceItem, ...]`;
  - `probe_codex_cli(codex_path, config_path=None) -> tuple[EvidenceItem, ...]`.

- [ ] **Step 1: Write RED host-inventory tests**

Required cases:

```text
inventory not observed -> CAPABILITY_UNAVAILABLE evidence
observed empty -> explicit no-hosted-actions evidence
spawn_agent only -> partial hosted-action evidence, never live
all six Responses actions -> HOSTED_ACTIONS_AVAILABLE, never child-created
unknown similarly named local tool -> must not count
```

- [ ] **Step 2: Write RED Codex/config tests**

Probe only non-model capability commands such as version/help/config parsing.

Assert:

- `multi_agent=true` produces configuration evidence only;
- missing executable -> CAPABILITY_UNAVAILABLE evidence;
- no model task is launched;
- no API/network credential is required for this probe;
- output cannot become `LIVE_VERIFIED`.

- [ ] **Step 3: Run RED**

- [ ] **Step 4: Implement both adapters with `shell=False` and bounded subprocess timeout**

No arbitrary command pass-through.

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add verifier/surfaces/host_inventory.py verifier/surfaces/codex_cli.py fixtures/host-inventory scripts/probe_codex.py tests/host_inventory tests/codex_cli
git commit -m "feat: add native host and Codex capability probes"
```

---

### Task 6: Build Deterministic Report Rendering and Evidence Export

**Files:**
- Create: `verifier/report.py`
- Create: `scripts/export_evidence.py`
- Test: `tests/evidence/test_report.py`

**Interfaces:**
- Consumes: validated `NativeVerificationReport`.
- Produces:
  - `report_to_json(report) -> dict[str, object]`;
  - `render_report(report) -> str`;
  - redacted JSON evidence artifact validated by `schemas/runtime-evidence.schema.json`.

- [ ] **Step 1: Write RED rendering/export tests**

Assert stable ordering and explicit output lines for:

```text
SURFACE
LIVE
SESSION_ID
SUBAGENT_ID
VERDICT
STATES
BLOCKERS
```

- [ ] **Step 2: Add scope-truth tests**

A report for `agents_api` must state that it proves only that Agents API session; a `codex_host_inventory` report must not be phrased as child execution proof.

- [ ] **Step 3: Add redacted artifact tests**

Export must contain normalized evidence only and schema validation must pass.

- [ ] **Step 4: Implement renderer/exporter**

- [ ] **Step 5: Run GREEN**

- [ ] **Step 6: Commit**

```bash
git add verifier/report.py scripts/export_evidence.py tests/evidence/test_report.py
git commit -m "feat: render and export scoped native evidence"
```

---

### Task 7: Add Explicit Opt-In Agents API Live Verification

**Files:**
- Modify/Create: `verifier/surfaces/agents_api.py`
- Create: `scripts/verify_native.py`
- Test: `tests/agents_api/test_agents_live_contract.py`

**Interfaces:**
- Consumes: existing `OPENAI_API_KEY` authorization, explicit model, `--live`, and optional bounded timeout.
- Produces: one scoped `NativeVerificationReport` for `surface="agents_api"`.

- [ ] **Step 1: Write RED live-contract tests with a mocked OpenAI client**

Assert:

- no `--live` -> no network/API client call;
- `--live` without existing credential -> `USER_ACTION_REQUIRED`;
- model is mandatory for live run;
- no credential creation flow exists;
- session config requests multi-agent;
- test task requests exactly one bounded delegation;
- no environment/tool access is required for the default live probe;
- streamed events are passed through the canonical parser/classifier;
- event stream with one real subagent ID + completion can yield `LIVE_VERIFIED`;
- missing created/completion evidence cannot yield `LIVE_VERIFIED`;
- report is scoped to returned session ID;
- API key never appears in stdout/stderr/report.

- [ ] **Step 2: Define the live probe request**

Default live probe uses an Agents API session with:

```text
environment.type = none
multi_agent.enabled = true
max_concurrent_subagents = 1
stream = true
```

Prompt/instructions ask the coordinator to delegate one tiny text-only subtask and return a short result. Do not configure MCP, filesystem, shell, or external tools in the default probe.

- [ ] **Step 3: Run mocked RED**

- [ ] **Step 4: Implement the opt-in live path using the official OpenAI Python SDK**

Use `openai==3.24.0`.

No ordinary unit/CI command may pass `--live`.

- [ ] **Step 5: Run mocked GREEN**

- [ ] **Step 6: Add non-live CLI examples to README**

Document live syntax without embedding credentials:

```bash
OPENAI_API_KEY=... python scripts/verify_native.py --surface agents-api --live --model <authorized-model>
```

Also document that API usage may incur cost and proves only the tested Agents API session.

- [ ] **Step 7: Commit**

```bash
git add verifier/surfaces/agents_api.py scripts/verify_native.py tests/agents_api/test_agents_live_contract.py README.md
git commit -m "feat: add opt-in Agents API native verification"
```

---

### Task 8: Add Unified Non-Live CLI and Runtime-Doctor Handoff Artifact

**Files:**
- Modify: `scripts/verify_native.py`
- Create: `tests/contract/test_cli_contract.py`
- Create: `tests/contract/test_runtime_doctor_handoff.py`

**Interfaces:**
- Consumes: one selected adapter and normalized evidence.
- Produces: deterministic CLI exit codes and a consumer-neutral JSON artifact for the later Runtime Doctor integration plan.

- [ ] **Step 1: Write RED CLI contract tests**

Supported modes:

```text
--surface agents-api --fixture <path>
--surface responses-api --fixture <path>
--surface codex-host-inventory --inventory <path>
--surface codex-cli --codex-path <path> [--config <path>]
--json
--output <path>
--require-live-verified
```

Exit codes:

```text
0 = diagnostic/report completed and requested condition satisfied
1 = malformed/contradictory evidence or verifier failure
2 = requested live proof requires user action/capability and is not satisfied
```

- [ ] **Step 2: Write RED Runtime Doctor handoff tests**

The exported JSON must expose stable top-level fields sufficient for a later consumer to read:

```text
runtime_contract_version
verifier_version
surface
live
session_id
states
verdict
blockers
```

No WhiteChronos/ChatGPT import or reverse dependency is allowed.

- [ ] **Step 3: Implement unified CLI/handoff format**

- [ ] **Step 4: Run GREEN**

- [ ] **Step 5: Commit**

```bash
git add scripts/verify_native.py tests/contract/test_cli_contract.py tests/contract/test_runtime_doctor_handoff.py
git commit -m "feat: add native verifier CLI contract"
```

---

### Task 9: Add Independent CI, Review Arena, and Pull Request

**Files:**
- Create: `.github/workflows/ci.yml`
- Create: `tests/contract/test_ci_contract.py`
- Modify: `README.md` only for verified usage/limitations.

**Interfaces:**
- Consumes: complete independent verifier.
- Produces: repository CI evidence and a reviewed PR to `main`; no live API proof is produced here.

- [ ] **Step 1: Write RED CI-contract tests**

Required CI commands:

```bash
python -m pip install --require-hashes -r requirements.lock
pytest -q
python scripts/verify_native.py --surface agents-api --fixture fixtures/agents-api/session-with-subagent.jsonl --json
python scripts/verify_native.py --surface responses-api --fixture fixtures/responses-api/hosted-actions.json --json
```

If the chosen lock tool uses a different immutable install command, record the plan ruling and preserve deterministic dependency installation.

CI permissions:

```text
contents: read
```

CI MUST NOT:

- set `OPENAI_API_KEY`;
- pass `--live`;
- create Agents API sessions;
- run paid model work;
- emit `LIVE_VERIFIED`;
- publish MCP/native action names as local tools;
- mutate `WhiteChronos/ChatGPT`;
- run Broker live smoke.

- [ ] **Step 2: Run RED**

- [ ] **Step 3: Add CI and complete README limitations**

README must explicitly distinguish:

```text
fixture verification
config/capability probe
host inventory observation
live Agents API session proof
current ChatGPT/Codex host proof
```

- [ ] **Step 4: Run complete local verification**

Expected:

```bash
pytest -q
```

all GREEN with no live API request.

- [ ] **Step 5: Apply Review Arena whole-branch**

Review at minimum:

- no fixture/mock path can yield live proof;
- no cross-surface overclaim;
- no hosted-action implementation/registration;
- credential/raw-event leakage;
- lifecycle completeness;
- stable subagent identity requirement;
- explicit user authorization for live run;
- no hidden paid invocation;
- deterministic evidence schema;
- Runtime Doctor handoff has no consumer coupling;
- no sensitive evidence/artifacts committed.

Any Critical/Important finding gets one TDD RED→GREEN fix pass before PR.

- [ ] **Step 6: Request independent code review only if a real reviewer subagent is available**

If no real `spawn_agent`/Broker reviewer surface is exposed, record structured self-review + Review Arena and do not label it independent review evidence.

- [ ] **Step 7: Open PR to `WhiteChronos/codex-native-runtime-verifier:main`**

PR must state:

- current public OpenAI contract baseline date;
- verifier version;
- supported surfaces;
- evidence truth table;
- no MCP/native-tool publication;
- credential policy;
- CI evidence;
- live API verification not executed in CI;
- whether any manual live run was performed separately;
- consumer Runtime Doctor integration remains out of scope.

- [ ] **Step 8: Require PR CI SUCCESS**

Do not merge on pending/failing checks.

---

## Post-Merge Handoff — Not Part of This Plan

After the Native Runtime Verifier PR is merged and its `main` CI is green:

1. record the verifier `main` SHA and version;
2. do not claim the current ChatGPT/Codex conversation has native subagents merely because the verifier exists;
3. do not run paid/live Agents API proof unless explicitly authorized in that runtime;
4. write/approve the next plan: **Runtime Marketplace**;
5. later register Arena, Broker, and Native Verifier versions/contracts in the marketplace;
6. later update WhiteChronos/ChatGPT Runtime Doctor to consume the verifier handoff artifact;
7. only a fresh-session/post-install proof can influence the current-session native → Broker → inline routing decision;
8. historical Broker Task 12 remains pending until the fresh-runtime gate and required Broker smoke are satisfied.

## Self-Review Checklist

- Native verifier is an independent repository: covered Task 1.
- It publishes no MCP/fake native tools: global constraint + Tasks 1, 4, 9.
- Config is not runtime proof: Tasks 2 and 5.
- Agents API subagent ID evidence: Task 3.
- Responses hosted actions are observed, never client-executed: Task 4.
- Host inventory is scoped and non-live: Task 5.
- Codex CLI/config cannot claim live: Task 5.
- Evidence is schema-validated and redacted: Tasks 2 and 6.
- Live proof requires explicit user authorization and existing credential: Task 7.
- Live proof is surface/session scoped: Tasks 2, 6, 7.
- CI never performs live model work: Task 9.
- CI never emits `LIVE_VERIFIED`: Tasks 2 and 9.
- Runtime Doctor integration is deferred but a stable handoff format exists: Task 8.
- Runtime Marketplace remains the next slice: post-merge handoff.
- No historical Broker/Arena work is redone: global constraints.
- Review Arena and truthful reviewer-evidence rules are preserved: Task 9.
