# Capability Contract + Registry v2 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the first independently testable slice of the WhiteChronos extensibility architecture: immutable Capability Contract/Manifest v2 schemas, a deterministic Registry v2 loader, and append-only lifecycle-event projection while preserving the existing Registry v1 and Runtime Doctor behavior.

**Architecture:** Add Registry v2 alongside `registry/integrations`; do not mutate v1 semantics or route existing runtime behavior through v2 yet. Keep v2 source-controlled authority in immutable contract/provider/event JSON records, derive current lifecycle views in Python, and fail closed on unknown/malformed identity, version, risk, cross-reference, or event-chain data.

**Tech Stack:** Python 3.11+ standard library (`dataclasses`, `enum`, `json`, `pathlib`, `re`, `datetime`), the existing `runtime.schema.validate_schema_subset` validator, pytest 8.4.1, GitHub Actions, JSON source-controlled registry records.

**Spec:** `docs/superpowers/specs/2026-10-04-whitechronos-extensible-capability-knowledge-fabric-design.md`

## Global Constraints

- GitHub remains the authoritative Control Plane for accepted source-controlled state; this slice must not create a parallel authority.
- Preserve `registry/integrations/schema.json`, `registry/integrations/index.json`, `runtime.registry.load_registry()`, existing descriptors, and current Runtime Doctor semantics unchanged.
- Registry v2 is additive. Do not rewrite Registry v1 in place.
- Capability contracts are semantically versioned and immutable; incompatible behavior requires a new major contract version.
- Provider manifests are immutable source records; lifecycle/current state is derived from append-only lifecycle events.
- Direct system-to-system dependencies remain forbidden; this slice models contract references only and does not add runtime invocation.
- Unknown risk, malformed identity, unresolved provided-contract references, duplicate identities, and ambiguous lifecycle chains fail closed.
- Generated/materialized current-state views are derived and are not source authority.
- Do not add a manually maintained Registry v2 index; loader discovery must be deterministic from sorted source-controlled paths.
- Do not add a Resolver, Adapter execution, Knowledge Ledger, Evolution Ledger, Zero-Trust enforcement, Secret Broker, or Conformance Harness in this slice. Those are later independent plans.
- Do not alter `AGENTS.md` integration routing in this slice.
- Do not mark PR #57 ready, merge it, run live smoke, or claim `LIVE_VERIFIED`.
- Every implementation task follows TDD: failing test, observed RED, minimal implementation, observed GREEN, commit.
- Existing GitHub path-policy, Runtime Foundation, engineering-governance, and full regression gates must remain green.

## File Structure

### Create

- `registry/capabilities/README.md` — v2 source layout, authority rules, append-only event policy, and migration boundary.
- `registry/capabilities/v2/contract.schema.json` — Capability Contract v2 source schema.
- `registry/capabilities/v2/manifest.schema.json` — Capability Manifest v2 source schema with multidimensional risk.
- `registry/capabilities/v2/lifecycle-event.schema.json` — append-only provider lifecycle event schema.
- `plugins/whitechronos-control-plane/runtime/capability_model.py` — typed v2 contract/manifest/event/view dataclasses and identity/version validators.
- `plugins/whitechronos-control-plane/runtime/capability_registry.py` — deterministic v2 file discovery, loading, duplicate/cross-reference validation.
- `plugins/whitechronos-control-plane/runtime/capability_lifecycle.py` — append-only event-chain validation and materialized current-state derivation.
- `plugins/whitechronos-control-plane/tests/test_capability_contracts.py` — schema/model/identity/version/risk tests.
- `plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py` — deterministic loader, duplicates, cross-references, and v1 coexistence.
- `plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py` — lifecycle chain and projection tests.
- `pipeline/capability_registry_policy.py` — Git-diff gate enforcing immutable/append-only accepted v2 registry records.
- `tests/test_capability_registry_policy.py` — policy-gate unit tests for add/modify/delete/rename behavior.

### Modify

- `.github/workflows/whitechronos-runtime-foundation.yml` — include `registry/capabilities/**` in path triggers; existing test command already runs all Control Plane tests.
- `plugins/whitechronos-control-plane/tests/test_repository_integration.py` — pin the new workflow trigger without changing existing runtime claims.
- `tests/test_github_path_policy.py` — explicitly prove `registry/capabilities/**` remains `DURABLE_STATE`.

### Do Not Modify

- `registry/integrations/schema.json`
- `registry/integrations/index.json`
- `registry/integrations/github-arena.json`
- `registry/integrations/subagent-broker.json`
- `plugins/whitechronos-control-plane/runtime/registry.py`
- `plugins/whitechronos-control-plane/runtime/doctor.py`
- `AGENTS.md`

## Core Interfaces

### `runtime/capability_model.py`

```python
class LifecycleState(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUARANTINED = "QUARANTINED"
    VALIDATING = "VALIDATING"
    COMPATIBLE = "COMPATIBLE"
    PROMOTABLE = "PROMOTABLE"
    CANARY = "CANARY"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    REVALIDATION_REQUIRED = "REVALIDATION_REQUIRED"
    REGRESSED = "REGRESSED"
    ROLLED_BACK = "ROLLED_BACK"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class ContractRef:
    contract_id: str
    version: str


@dataclass(frozen=True)
class ContractRequirement:
    contract_id: str
    version_range: str
    role: str  # REQUIRED | OPTIONAL | ENHANCEMENT


@dataclass(frozen=True)
class CapabilityContract:
    contract_id: str
    version: str
    stability: str
    input_schema_ref: str | None
    output_schema_ref: str | None
    error_codes: tuple[str, ...]
    side_effect_class: str
    invariants: tuple[str, ...]


@dataclass(frozen=True)
class RiskProfile:
    filesystem: str
    network: bool
    credentials: bool
    subprocess: bool
    background_execution: bool
    mutation_scope: str
    external_side_effects: bool
    sensitive_data: bool
    control_plane_impact: bool


@dataclass(frozen=True)
class CapabilityManifest:
    provider_id: str
    display_name: str
    implementation_version: str
    source_type: str
    source: str
    revision: str
    digest: str
    license_status: str
    provides: tuple[ContractRef, ...]
    requires: tuple[ContractRequirement, ...]
    risk_profile: RiskProfile
    extensions: dict[str, object]


@dataclass(frozen=True)
class LifecycleEvent:
    event_id: str
    provider_id: str
    implementation_version: str
    state: LifecycleState
    occurred_at: str
    actor_type: str
    actor_id: str
    reason: str
    evidence_refs: tuple[str, ...]
    predecessor_event_id: str | None


@dataclass(frozen=True)
class ProviderLifecycleView:
    provider_id: str
    implementation_version: str
    current_state: LifecycleState
    last_event_id: str
    event_count: int


@dataclass(frozen=True)
class CapabilityRegistry:
    contracts: dict[tuple[str, str], CapabilityContract]
    providers: dict[tuple[str, str], CapabilityManifest]
    events: tuple[LifecycleEvent, ...]
    lifecycle: dict[tuple[str, str], ProviderLifecycleView]
```

Required helpers:

```python
def validate_capability_id(value: str) -> str: ...
def validate_provider_id(value: str) -> str: ...
def validate_semver(value: str, *, label: str) -> str: ...
```

Identity rules for this slice:

- `contract_id` must begin with `capability://`, contain at least one namespace/name separator after the scheme, contain no whitespace, backslash, `..`, query, or fragment component.
- `provider_id` must be a non-empty lowercase slug made only of ASCII letters, digits, `.`, `_`, and `-`; it must not contain `..`.
- A provider implementation is uniquely identified by `(provider_id, implementation_version)` so multiple immutable versions of the same provider family may coexist.
- Contract and implementation versions are full SemVer strings `MAJOR.MINOR.PATCH` with optional SemVer prerelease/build suffixes.
- Manifest `digest` is normalized as `sha256:<64 lowercase hexadecimal characters>` in this slice.
- Requirement `version_range` is stored as a non-empty declarative string in this slice; range resolution is deferred to the Resolver plan.

### `runtime/capability_registry.py`

```python
def load_contract(path: Path, schema_path: Path) -> CapabilityContract: ...
def load_manifest(path: Path, schema_path: Path) -> CapabilityManifest: ...
def load_lifecycle_event(path: Path, schema_path: Path) -> LifecycleEvent: ...

def load_capability_registry(repo_root: Path) -> CapabilityRegistry: ...
```

Discovery roots:

```text
registry/capabilities/v2/contracts/**/*.json
registry/capabilities/v2/providers/**/*.json
registry/capabilities/v2/events/**/*.json
```

The three schema files themselves are outside those data subdirectories and must never be interpreted as registry records.

### `runtime/capability_lifecycle.py`

```python
def derive_lifecycle_view(
    providers: dict[tuple[str, str], CapabilityManifest],
    events: tuple[LifecycleEvent, ...],
) -> dict[tuple[str, str], ProviderLifecycleView]: ...
```

The first slice validates event-chain integrity, not full promotion-policy transition semantics. State-transition policy belongs to the later promotion/governance plan.

## Review Focus

1. **Registry v1 coexistence** — adding Registry v2 must not change the two current v1 descriptors or Runtime Doctor loading behavior. Owning test: Task 4.
2. **Unknown or malformed risk/identity data** — v2 must reject undeclared risk keys, unsafe IDs, malformed SemVer, and arbitrary top-level fields except namespaced `extensions`. Owning tests: Task 1.
3. **Missing/duplicate contract references** — two source files may not define the same `(contract_id, version)` or `(provider_id, implementation_version)`, and every exact contract listed in `provides` must exist. Owning tests: Task 2.
4. **Ambiguous/corrupt lifecycle history** — missing predecessors, cross-provider-version predecessor links, duplicate event IDs, multiple roots, branches, and cycles must fail rather than choosing an arbitrary current state. Owning tests: Task 3.
5. **Immutability or CI blind spot** — accepted contract/provider/event records may only be added, never modified/deleted/renamed in place; `registry/capabilities/**` must trigger Runtime Foundation CI and remain `DURABLE_STATE`. Owning tests: Task 4.

---

### Task 1: Define Capability Contract/Manifest v2 Schemas and Typed Models

**Files:**
- Create: `registry/capabilities/README.md`
- Create: `registry/capabilities/v2/contract.schema.json`
- Create: `registry/capabilities/v2/manifest.schema.json`
- Create: `registry/capabilities/v2/lifecycle-event.schema.json`
- Create: `plugins/whitechronos-control-plane/runtime/capability_model.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_contracts.py`

**Interfaces:**
- Consumes: existing `runtime.schema.validate_schema_subset(value, schema, path="$")`.
- Produces: all v2 dataclasses plus `validate_capability_id()`, `validate_provider_id()`, and `validate_semver()` for Tasks 2-3.

- [ ] **Step 1: Write failing identity/version/risk tests**

Add tests with these exact assertions:

```python
@pytest.mark.parametrize(
    "value",
    [
        "capability://knowledge/search",
        "capability://engineering/bim",
        "capability://agent/delegate",
    ],
)
def test_validate_capability_id_accepts_namespaced_ids(value):
    assert validate_capability_id(value) == value


@pytest.mark.parametrize(
    "value",
    [
        "knowledge/search",
        "capability://single",
        "capability://knowledge/../secret",
        "capability://knowledge/search?x=1",
        "capability://knowledge/search#frag",
        "capability://knowledge\\search",
        "capability://knowledge/white space",
    ],
)
def test_validate_capability_id_rejects_unsafe_or_non_namespaced_ids(value):
    with pytest.raises(ValueError):
        validate_capability_id(value)


@pytest.mark.parametrize("value", ["0.1.0", "1.0.0", "2.7.3-alpha.1", "2.7.3+build.5"])
def test_validate_semver_accepts_full_semver(value):
    assert validate_semver(value, label="version") == value


@pytest.mark.parametrize("value", ["1", "1.2", "01.2.3", "v1.2.3", "1.2.x", ""])
def test_validate_semver_rejects_non_semver(value):
    with pytest.raises(ValueError, match="version"):
        validate_semver(value, label="version")
```

Add a manifest-schema test that accepts a multidimensional combination:

```python
risk_profile = {
    "filesystem": "WRITE",
    "network": True,
    "credentials": True,
    "subprocess": False,
    "background_execution": True,
    "mutation_scope": "WORKSPACE",
    "external_side_effects": True,
    "sensitive_data": False,
    "control_plane_impact": False,
}
```

and rejects an unknown risk key such as `"trust_me": true`.

- [ ] **Step 2: Run Task 1 tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_contracts.py
```

Expected: FAIL because the v2 schemas and `capability_model.py` do not exist.

- [ ] **Step 3: Create the three v2 source schemas**

Use only JSON-schema keywords supported by the current `validate_schema_subset` implementation.

`contract.schema.json` required fields:

```text
schema_version = 2
record_type = capability_contract
contract_id
version
stability
input_schema_ref
output_schema_ref
error_codes
side_effect_class
invariants
extensions
```

Allowed `stability`:

```text
EXPERIMENTAL
STABLE
DEPRECATED
```

Allowed `side_effect_class`:

```text
PURE
READ_ONLY
LOCAL_MUTATING
EXTERNAL_MUTATING
CONTROL_PLANE
```

`manifest.schema.json` required fields:

```text
schema_version = 2
record_type = capability_manifest
provider_id
display_name
implementation_version
source_type
source
revision
digest
license_status
provides
requires
risk_profile
extensions
```

Allowed `source_type`:

```text
local
upstream_git
external_reference
official_plugin
component_repository
```

`provides` items are objects with exactly `contract_id` and exact `version`.

`requires` items are objects with exactly `contract_id`, non-empty `version_range`, and `role`; allowed roles are `REQUIRED`, `OPTIONAL`, and `ENHANCEMENT`.

`risk_profile` must have `additionalProperties: false` and exactly the nine fields defined by `RiskProfile`. Allowed `filesystem` values are `NONE`, `READ`, and `WRITE`. Allowed `mutation_scope` values are `NONE`, `WORKSPACE`, `EXTERNAL`, and `CONTROL_PLANE`.

`lifecycle-event.schema.json` required fields:

```text
schema_version = 2
record_type = capability_lifecycle_event
event_id
provider_id
implementation_version
state
occurred_at
actor_type
actor_id
reason
evidence_refs
predecessor_event_id
extensions
```

Allowed `actor_type`:

```text
HUMAN
SYSTEM
WORKFLOW
```

- [ ] **Step 4: Implement typed models and semantic validators**

Implement the exact interfaces under **Core Interfaces**.

Do not add a third-party SemVer dependency. Use one compiled regular expression implementing SemVer 2.0.0 syntax for full versions.

The model layer validates semantics that the existing schema subset cannot express:

- capability/provider ID shape;
- SemVer shape;
- non-empty requirement range;
- allowed requirement roles;
- digest exactly `sha256:<64 lowercase hex>`;
- ISO-8601 timestamp parseability for lifecycle events.

Do not implement version-range comparison in this task.

- [ ] **Step 5: Write the Registry v2 README**

Document:

- v1 is still authoritative for current Runtime Doctor integrations;
- v2 is additive and initially may contain no production providers;
- contracts/providers/events are immutable source records once accepted;
- lifecycle changes append new event files rather than editing a provider status field;
- no manual v2 `index.json`;
- materialized lifecycle state is derived;
- direct provider-to-provider dependency is not introduced by these records.

- [ ] **Step 6: Run Task 1 tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_contracts.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add registry/capabilities plugins/whitechronos-control-plane/runtime/capability_model.py plugins/whitechronos-control-plane/tests/test_capability_contracts.py
git commit -m "feat: define WhiteChronos capability registry v2 contracts"
```

---

### Task 2: Implement Deterministic Registry v2 Loading and Cross-Reference Validation

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py`

**Interfaces:**
- Consumes: Task 1 schemas/models and existing `validate_schema_subset()`.
- Produces: `load_contract()`, `load_manifest()`, `load_lifecycle_event()`, and `load_capability_registry()`.

- [ ] **Step 1: Write a temporary v2-registry fixture builder**

In `test_capability_registry_v2.py`, add a helper that creates:

```text
repo/
  registry/
    integrations/        # copied unchanged from the real repo
    capabilities/
      v2/
        contract.schema.json
        manifest.schema.json
        lifecycle-event.schema.json
        contracts/
        providers/
        events/
```

Copy the three v2 schema files from `REPO`, then let each test write only the records it needs.

- [ ] **Step 2: Write failing deterministic-load tests**

Required tests:

```python
def test_empty_v2_registry_loads_without_affecting_v1():
    ...

def test_registry_loads_contract_and_provider_independent_of_filename_order():
    ...

def test_registry_rejects_duplicate_contract_identity():
    ...

def test_registry_rejects_duplicate_provider_version():
    ...

def test_registry_rejects_provider_that_claims_missing_provided_contract():
    ...

def test_registry_rejects_json_record_outside_expected_record_type():
    ...

def test_registry_rejects_path_escape_and_symlink_escape():
    ...
```

For the valid provider, use exactly:

```text
contract_id: capability://test/echo
contract version: 1.0.0
provider_id: test-echo-provider
implementation_version: 1.0.0
```

The valid manifest must list `capability://test/echo@1.0.0` in `provides`.

- [ ] **Step 3: Run Task 2 tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
```

Expected: FAIL because `capability_registry.py` does not exist.

- [ ] **Step 4: Implement safe record loading**

Each loader must:

1. resolve its schema path under `registry/capabilities/v2`;
2. read UTF-8 JSON;
3. require an object;
4. validate with `validate_schema_subset`;
5. run Task 1 semantic validators;
6. return the typed dataclass;
7. never execute provider code;
8. never follow a registry data symlink outside the expected v2 root.

If symlink resolution leaves the v2 root, raise `ValueError`.

- [ ] **Step 5: Implement deterministic discovery**

`load_capability_registry(repo_root)` discovers `*.json` using recursively sorted POSIX relative paths from:

```text
contracts/
providers/
events/
```

It must not require or create an `index.json`.

It must reject:

- duplicate `(contract_id, version)`;
- duplicate `(provider_id, implementation_version)`;
- duplicate `event_id`;
- an exact `provides` contract reference absent from loaded contracts;
- lifecycle events whose `(provider_id, implementation_version)` is absent from loaded providers.

`requires.version_range` is not resolved yet; preserve it for the Resolver phase.

- [ ] **Step 6: Keep v1 loader behavior byte-for-behavior compatible**

Add this explicit regression in `test_capability_registry_v2.py`:

```python
def test_v1_registry_remains_unchanged_when_v2_exists():
    legacy = load_registry(REPO)
    assert tuple(legacy) == ("github-arena", "subagent-broker")
    assert legacy["github-arena"].execution_class == "MCP_OR_CONNECTOR"
    assert legacy["subagent-broker"].execution_class == "LOCAL_MUTATING"
```

Do not modify `runtime/registry.py` to make this pass.

- [ ] **Step 7: Run Task 2 tests and verify GREEN**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
```

Expected: PASS.

- [ ] **Step 8: Commit Task 2**

```bash
git add plugins/whitechronos-control-plane/runtime/capability_registry.py plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
git commit -m "feat: load WhiteChronos capability registry v2"
```

---

### Task 3: Derive Current Lifecycle from Append-Only Event Chains

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/capability_lifecycle.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Test: `plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py`

**Interfaces:**
- Consumes: `dict[tuple[str, str], CapabilityManifest]` and `tuple[LifecycleEvent, ...]`.
- Produces: `derive_lifecycle_view(...)->dict[tuple[str, str], ProviderLifecycleView]`; `load_capability_registry()` returns the derived `lifecycle` map.

- [ ] **Step 1: Write failing happy-path lifecycle test**

Use one provider implementation `(provider_id="test-echo-provider", implementation_version="1.0.0")` and this exact event chain:

```text
evt-001  DISCOVERED    predecessor = null
evt-002  QUARANTINED   predecessor = evt-001
evt-003  VALIDATING    predecessor = evt-002
evt-004  COMPATIBLE    predecessor = evt-003
```

Assert:

```python
view = derive_lifecycle_view(providers, events)
key = ("test-echo-provider", "1.0.0")
assert view[key].current_state is LifecycleState.COMPATIBLE
assert view[key].last_event_id == "evt-004"
assert view[key].event_count == 4
```

- [ ] **Step 2: Write failing corrupt-history tests**

Required tests:

```python
def test_lifecycle_rejects_missing_predecessor():
    ...

def test_lifecycle_rejects_cross_provider_predecessor():
    ...

def test_lifecycle_rejects_multiple_roots_for_one_provider():
    ...

def test_lifecycle_rejects_branching_history():
    ...

def test_lifecycle_rejects_cycle():
    ...

def test_provider_without_events_has_no_materialized_lifecycle_entry():
    ...
```

Do not invent a current state for a provider with no events.

- [ ] **Step 3: Run Task 3 tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py
```

Expected: FAIL because `capability_lifecycle.py` does not exist.

- [ ] **Step 4: Implement chain-integrity validation**

For each exact provider implementation `(provider_id, implementation_version)`:

1. gather its events;
2. require at most one root event with `predecessor_event_id is None`;
3. every non-root predecessor must exist;
4. predecessor must belong to the same provider;
5. each event may have at most one successor in this first linear event model;
6. walk root -> successor and reject cycles;
7. require every event to be reachable from the root;
8. set the final reachable event's `state` as current state.

Do not enforce business transition legality such as whether `PROMOTABLE -> CANARY` is permitted. That belongs to the later promotion-policy plan.

- [ ] **Step 5: Integrate lifecycle projection into `load_capability_registry()`**

After contracts/providers/events pass source validation, call:

```python
lifecycle = derive_lifecycle_view(providers, events)
```

Return it as `CapabilityRegistry.lifecycle`.

Do not write a generated lifecycle file to the repository in this slice.

- [ ] **Step 6: Run Task 3 tests and Registry v2 tests**

Run:

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py   plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
```

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```bash
git add plugins/whitechronos-control-plane/runtime/capability_lifecycle.py plugins/whitechronos-control-plane/runtime/capability_registry.py plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py
git commit -m "feat: derive capability lifecycle from append-only events"
```

---

### Task 4: Enforce Append-Only Registry Records and Wire CI Governance

**Files:**
- Create: `pipeline/capability_registry_policy.py`
- Create: `tests/test_capability_registry_policy.py`
- Modify: `.github/workflows/whitechronos-runtime-foundation.yml`
- Modify: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`
- Modify: `tests/test_github_path_policy.py`

**Interfaces:**
- Consumes: Git name-status diff records for `registry/capabilities/v2/{contracts,providers,events}/**/*.json`.
- Produces: `validate_registry_changes(changes: tuple[RegistryChange, ...]) -> tuple[str, ...]` plus a CLI that returns non-zero when accepted v2 source records are modified, deleted, or renamed in place.

- [ ] **Step 1: Write failing append-only policy tests**

Create `tests/test_capability_registry_policy.py` with exact behaviors:

```python
def test_new_contract_provider_and_event_files_are_allowed():
    ...

def test_modifying_existing_contract_is_rejected():
    ...

def test_modifying_existing_provider_version_is_rejected():
    ...

def test_modifying_existing_event_is_rejected():
    ...

def test_deleting_or_renaming_accepted_record_is_rejected():
    ...

def test_schema_and_readme_changes_are_not_treated_as_append_only_records():
    ...
```

Use synthetic Git name-status inputs such as `A\tpath`, `M\tpath`, `D\tpath`, and `R100\told\tnew`. The policy must reject any non-add status for JSON records below `contracts/`, `providers/`, or `events/`.

- [ ] **Step 2: Run append-only policy tests and verify RED**

Run:

```bash
python -m pytest -q tests/test_capability_registry_policy.py
```

Expected: FAIL because `pipeline/capability_registry_policy.py` does not exist.

- [ ] **Step 3: Implement the pure policy interface and CLI**

Define:

```python
@dataclass(frozen=True)
class RegistryChange:
    status: str
    old_path: str | None
    new_path: str | None

def parse_name_status(lines: list[str]) -> tuple[RegistryChange, ...]: ...
def validate_registry_changes(changes: tuple[RegistryChange, ...]) -> tuple[str, ...]: ...
```

CLI:

```text
python pipeline/capability_registry_policy.py --base <sha> --head <sha>
```

The CLI may invoke `git diff --name-status --find-renames <base>...<head> -- registry/capabilities` with `shell=False`, parse the result, print deterministic violations, and exit `1` on any immutable-record violation.

Rules:

- new record file under `contracts/`, `providers/`, or `events/`: `A` allowed;
- `M`, `D`, `R*`, or `C*` touching an already accepted record path: reject;
- schema files and `registry/capabilities/README.md`: not subject to append-only record rule, but remain ordinary reviewed source;
- paths must be normalized and must remain under `registry/capabilities/v2`.

This gate enforces source-control immutability; it does not decide lifecycle transitions.

- [ ] **Step 4: Write the workflow-trigger and path-policy regressions**

Add to `test_repository_integration.py`:

```python
def test_runtime_foundation_workflow_triggers_on_capability_registry_v2():
    text = (REPO / ".github/workflows/whitechronos-runtime-foundation.yml").read_text()
    assert '"registry/capabilities/**"' in text
    assert "capability_registry_policy.py" in text
```

Add this parameter to `tests/test_github_path_policy.py`:

```python
("registry/capabilities/v2/providers/test-echo-provider/1.0.0.json", "DURABLE_STATE")
```

Do not modify `pipeline/github_path_policy.py`; the existing `registry/` rule should already satisfy the classification.

- [ ] **Step 5: Run Task 4 tests and verify RED only where expected**

Run:

```bash
python -m pytest -q   tests/test_capability_registry_policy.py   plugins/whitechronos-control-plane/tests/test_repository_integration.py::test_runtime_foundation_workflow_triggers_on_capability_registry_v2   tests/test_github_path_policy.py
```

Expected before workflow edit:

- append-only policy tests: PASS after Step 3;
- new workflow-trigger test: FAIL because the workflow is not wired yet;
- path-policy suite: PASS.

If path-policy fails, stop and investigate; do not broaden classifications casually.

- [ ] **Step 6: Extend Runtime Foundation workflow**

Add exactly:

```yaml
- "registry/capabilities/**"
```

to both `pull_request.paths` and `push.paths`.

Add a policy step that calculates a base SHA appropriate to the GitHub event and runs:

```bash
python pipeline/capability_registry_policy.py --base "$BASE_SHA" --head "$GITHUB_SHA"
```

Preserve:

- `permissions: contents: read`;
- existing Runtime Foundation test commands;
- current Runtime Doctor non-live CI behavior;
- no live smoke.

- [ ] **Step 7: Run Task 4 tests and verify GREEN**

Run:

```bash
python -m pytest -q   tests/test_capability_registry_policy.py   plugins/whitechronos-control-plane/tests/test_repository_integration.py   tests/test_github_path_policy.py
```

Expected: PASS.

- [ ] **Step 8: Commit Task 4**

```bash
git add pipeline/capability_registry_policy.py tests/test_capability_registry_policy.py .github/workflows/whitechronos-runtime-foundation.yml plugins/whitechronos-control-plane/tests/test_repository_integration.py tests/test_github_path_policy.py
git commit -m "ci: enforce append-only capability registry records"
```
---

### Task 5: Full Verification, Compatibility Regression, and Review Arena

**Files:**
- Modify only if RED/GREEN fixes reveal a defect in Tasks 1-4.
- No new feature scope.

**Interfaces:**
- Consumes: the complete Phase 1 implementation.
- Produces: verified Phase 1 evidence suitable for PR review; no activation.

- [ ] **Step 1: Run the complete new Registry v2 test set**

Run:

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_capability_contracts.py   plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py   plugins/whitechronos-control-plane/tests/test_capability_lifecycle.py
```

Expected: PASS.

- [ ] **Step 2: Run all WhiteChronos Control Plane tests**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
```

Expected: PASS.

- [ ] **Step 3: Run the full repository Python regression suite**

Run:

```bash
python -m pytest -q
```

Expected: PASS.

- [ ] **Step 4: Run existing Subagent Broker compatibility tests**

Run:

```bash
node --test   plugins/subagent-broker/tests/mcp-protocol.test.mjs   plugins/subagent-broker/tests/repository-integration.test.mjs
```

Expected: PASS.

- [ ] **Step 5: Run repository-required GitHub Control Plane gates**

Run:

```bash
python pipeline/github_control_plane_policy_gate.py --policy governance/GITHUB_CONTROL_PLANE_POLICY.json
python -m pytest -q tests/test_github_control_plane_policy_gate.py
python -m pytest -q tests/test_github_path_policy.py
python -m pytest -q tests/test_capability_registry_policy.py
```

Expected: PASS.

- [ ] **Step 6: Run repository-required engineering governance gates**

Run:

```bash
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
```

Expected: PASS.

- [ ] **Step 7: Apply Review Arena to the completed Phase 1 diff**

Use at least four structured Arena perspectives. Review specifically:

- evidence-first: v1 behavior and source-of-truth claims are actually preserved;
- constraint-first: no Resolver/activation/Knowledge/Evolution scope leaked into Phase 1;
- edge-cases-first: duplicate IDs, unsafe paths, malformed versions, missing contract refs, cycles/branches fail closed;
- built-to-last: no manual v2 index, no unnecessary provider-specific logic, later phases have stable interfaces.

If a verified defect is found, add a failing regression test before fixing it.

- [ ] **Step 8: Verify no runtime activation occurred**

Confirm the diff does not:

- add a v2 provider to Runtime Doctor routing;
- modify `.codex/config.toml`;
- modify `AGENTS.md`;
- modify current v1 descriptors;
- create secrets;
- run live smoke;
- mark PR #57 ready.

Expected: all false.

- [ ] **Step 9: Commit any final review fixes**

Only if Steps 1-8 required a change:

```bash
git add <review-fix-files>
git commit -m "test: harden capability registry v2 foundation"
```

If no fixes were required, do not create an empty commit.

---

## Phase 1 Acceptance Criteria

Phase 1 is complete only when all are verified:

1. Registry v1 still loads exactly `github-arena` and `subagent-broker` through the unchanged `load_registry()` path.
2. Registry v2 exists beside v1 with separate schemas and runtime modules.
3. An empty Registry v2 is valid and causes no runtime activation.
4. A test provider implementing `capability://test/echo@1.0.0` can be loaded without any Kernel/provider-specific code change.
5. Duplicate contract/provider-version/event identities fail closed.
6. Unsafe IDs, malformed SemVer, unknown risk fields, and path/symlink escape fail closed.
7. A provider cannot claim an exact `provides` contract that is absent.
8. Lifecycle current state is derived independently for each `(provider_id, implementation_version)` from an append-only linear event chain.
9. Missing predecessors, cross-provider links, multiple roots, branches, and cycles fail closed.
10. No manually maintained v2 index is introduced.
11. `registry/capabilities/**` is classified as `DURABLE_STATE`.
12. Accepted contract/provider/event files cannot be modified, deleted, copied, or renamed in place without the append-only policy gate failing.
13. Registry v2 changes trigger the existing Runtime Foundation workflow.
14. Control Plane, repository, Broker, GitHub policy, and engineering governance regressions are green.
15. No Resolver, provider activation, Knowledge/Evolution Ledger, Zero-Trust runtime enforcement, or live verification is claimed by this slice.
16. PR #57 remains DRAFT.

## Subsequent Implementation Plans

The umbrella spec remains intentionally decomposed. After Phase 1 is implemented and reviewed, write a fresh detailed plan against the then-current repository state for each independent slice, in this order:

1. **Resolver + Adapter semantics + dependency-boundary enforcement**
2. **Knowledge Record + append-only Knowledge Ledger + materialized-view foundation**
3. **Truth Resolver + Context Engine**
4. **Evolution Ledger + permanent Capability Roadmap + gap detection**
5. **Skill/Capability Factory + quarantine/promotion lifecycle**
6. **Zero-Trust policy model + Execution Leases + Secret Broker interfaces**
7. **Runtime isolation/enforcement integration**
8. **Operational Evidence Fabric + health/circuit/failover model**
9. **Runtime Doctor capability-probe extension**
10. **Continuous Verification + Conformance Harness + Promotion Evidence**
11. **AGENTS.md constitutional consolidation and structured-routing migration**
12. **System-level recovery, replay, canary, chaos, and umbrella acceptance validation**

Do not pre-write those detailed plans now: each one must use the verified repository state produced by the prior slice so exact interfaces, migrations, and tests are not based on stale assumptions.
