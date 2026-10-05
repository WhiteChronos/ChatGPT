# Capability Resolver, Adapter Semantics, and Dependency Boundary Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement WhiteChronos Phase 2 as a deterministic, fail-closed structural Capability Resolver with first-class Adapter semantics and CI-enforced provider isolation, without adding runtime invocation, authorization, health routing, or live activation.

**Architecture:** Phase 2 builds on the integrated Registry v2 foundation at `feat/cloud-runtime-foundation`. Resolution remains a pure, side-effect-free planning operation over source-controlled Registry v2 state: exact contracts and provider versions are immutable, lifecycle state determines structural eligibility, adapter records describe explicit semantic bridges, and a repository policy blocks direct provider-to-provider implementation coupling. Runtime authorization, health/circuit inputs, Execution Leases, evidence persistence, and actual invocation remain later phases.

**Tech Stack:** Python 3.12 standard library, existing WhiteChronos Runtime Foundation, JSON Schema subset already implemented by `runtime.schema.validate_schema_subset`, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-04-whitechronos-extensible-capability-knowledge-fabric-design.md`

## Global Constraints

- GitHub remains the authoritative Control Plane; this phase MUST NOT create a parallel source of truth.
- Registry v1 remains unchanged and authoritative for the current Runtime Doctor integration path.
- Registry v2 accepted records remain append-only; Phase 2 extends that rule to `registry/capabilities/v2/adapters/**/*.json`.
- Capability Contracts and provider implementation identities remain immutable and semantically versioned.
- A consumer requests a capability contract/version range; it does not depend on a concrete provider unless an exact provider pin is explicitly supplied.
- Direct provider-to-provider implementation dependency remains forbidden by default.
- Adapter records are first-class immutable registry records; adapter provenance/lifecycle are inherited from the exact implementation provider they reference rather than duplicated.
- ACTIVE means structurally eligible for resolution in this phase; it does not grant runtime authorization or global trust.
- Unknown/malformed version ranges, unknown adapter references, unresolved pins, missing lifecycle state, and ambiguous structural records fail closed.
- No Runtime Doctor routing changes, no live smoke, no provider activation, no secrets/network/filesystem authorization, no Knowledge/Evolution Ledger work, and no `LIVE_VERIFIED` claim are part of this phase.
- No new third-party runtime dependency is introduced for SemVer/range handling.
- PR #57 stays DRAFT throughout Phase 2 planning and implementation unless the user separately authorizes a status change.

## File Structure

Phase 2 owns the following focused units:

- `plugins/whitechronos-control-plane/runtime/capability_versioning.py` — SemVer precedence and the limited, explicit version-range grammar used by Resolver/Registry validation.
- `plugins/whitechronos-control-plane/runtime/capability_adapter.py` — typed Adapter descriptor semantics and graph helpers.
- `plugins/whitechronos-control-plane/runtime/capability_resolver.py` — pure structural resolution request/decision models and deterministic route selection.
- `plugins/whitechronos-control-plane/runtime/capability_registry.py` — loads immutable Adapter records and validates contract/provider/adapter references.
- `plugins/whitechronos-control-plane/runtime/capability_model.py` — extends `CapabilityRegistry` with adapters; existing Phase 1 types remain compatible.
- `registry/capabilities/v2/adapter.schema.json` — source schema for Adapter records.
- `pipeline/capability_dependency_policy.py` — static provider-boundary scanner driven by local provider manifests.
- `pipeline/capability_registry_policy.py` — extends append-only protection to Adapter records.
- `.github/workflows/whitechronos-runtime-foundation.yml` — runs Resolver/Adapter/boundary gates whenever their source or policy changes.
- Dedicated pytest files keep versioning, Adapter, Resolver, and boundary-policy behavior independent.

## Core Phase 2 Interfaces

### Versioning

```python
@dataclass(frozen=True)
class SemVer:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    @classmethod
    def parse(cls, value: str) -> "SemVer": ...
    def precedence_key(self) -> tuple[object, ...]: ...


@dataclass(frozen=True)
class VersionComparator:
    operator: str
    version: SemVer


@dataclass(frozen=True)
class VersionRange:
    comparators: tuple[VersionComparator, ...]

    @classmethod
    def parse(cls, value: str) -> "VersionRange": ...
    def matches(self, version: str | SemVer) -> bool: ...
```

Supported range grammar in this phase:

```text
1.2.3
=1.2.3
==1.2.3
>=1.2.3
>=2.1 <3
>=1.2.0 <2.0.0
>1 <=2.5
```

Rules:

- a bare version MUST be a full SemVer and means exact equality;
- comparator operands MAY use one, two, or three numeric release components and are zero-filled for comparison (`2` -> `2.0.0`, `2.1` -> `2.1.0`);
- prerelease/build syntax is accepted only on a full three-component operand;
- whitespace-separated comparators are ANDed;
- `^, ~, *, x, ||` and comma syntax are rejected rather than guessed;
- SemVer build metadata does not affect precedence;
- SemVer prerelease ordering follows SemVer 2.0.0.

### Adapter descriptor

```python
@dataclass(frozen=True)
class ErrorMapping:
    source_error: str
    target_error: str


@dataclass(frozen=True)
class CapabilityAdapter:
    adapter_id: str
    version: str
    implementation_provider_id: str
    implementation_version: str
    source_contract_id: str
    source_version: str
    target_contract_id: str
    target_version: str
    transformation: str
    lossiness: str
    information_loss: tuple[str, ...]
    unsupported_cases: tuple[str, ...]
    error_mapping: tuple[ErrorMapping, ...]
    conformance_tests: tuple[str, ...]
    extensions: dict[str, object]
```

Adapter direction is defined as:

```text
consumer/source contract
    -> adapter
    -> provider/target contract
```

This matches the architecture example `Consumer v1 -> Adapter 1->2 -> Provider v2`.

`lossiness` is exactly `LOSSLESS` or `LOSSY`. `LOSSLESS` requires an empty `information_loss`; `LOSSY` requires at least one declared loss item.

### Structural Resolver

```python
ProviderKey = tuple[str, str]
AdapterKey = tuple[str, str]


@dataclass(frozen=True)
class ResolutionRequest:
    contract_id: str
    version_range: str
    provider_pin: ProviderKey | None = None
    preferred_provider_ids: tuple[str, ...] = ()
    allow_adapters: bool = True
    allow_lossy_adapters: bool = False


@dataclass(frozen=True)
class ResolutionDecision:
    requested_contract_id: str
    requested_version_range: str
    selected_consumer_contract_version: str
    provider_id: str
    implementation_version: str
    provider_contract_id: str
    provider_contract_version: str
    adapter_chain: tuple[AdapterKey, ...]
    candidate_count: int
    selection_reason: str


class ResolutionError(ValueError): ...
class NoCompatibleProvider(ResolutionError): ...
class PinnedProviderUnavailable(ResolutionError): ...


def resolve_capability(
    registry: CapabilityRegistry,
    request: ResolutionRequest,
) -> ResolutionDecision: ...
```

Phase 2 resolution is deliberately structural:

- provider and Adapter implementation providers MUST have a materialized lifecycle state of `ACTIVE`;
- runtime authorization, policy decisions, health/circuit status, environment availability, cost, and execution leases are not fabricated in this phase;
- later phases may supply those gates before invocation without changing the contract-selection semantics defined here.

Deterministic candidate ordering is:

```text
1. exact provider pin, when present
2. direct route before adapted route
3. fewer adapter hops
4. fewer LOSSY adapters
5. preferred_provider_ids order
6. higher consumer-selected contract version
7. higher provider contract version
8. higher provider implementation version
9. adapter-chain identity lexicographically
10. provider_id lexicographically
```

The Resolver returns the winning route plus enough identity to make the decision reproducible. It does not invoke the provider.

## Review Focus

1. **Range ambiguity:** malformed/unsupported range syntax must fail closed instead of silently widening compatibility. Owning tests: Task 1.
2. **Adapter graph corruption:** missing contracts/providers, inactive adapter implementations, self-loops, cycles, and lossy routes must not produce an apparently valid route. Owning tests: Tasks 2 and 4.
3. **Determinism:** registry file order or Python dictionary insertion order must not change the selected provider/adapter chain. Owning tests: Tasks 3 and 4.
4. **Pin/preference semantics:** an exact pin must fail when unavailable rather than falling back silently; preference may rank only otherwise-compatible candidates. Owning tests: Task 3.
5. **Boundary-policy bypass:** a local provider must not import/load/read another local provider's private implementation through direct imports, `importlib`, `__import__`, `sys.path`, or literal filesystem access. Owning tests: Task 5.

---

### Task 1: Add SemVer Precedence and Fail-Closed Version Ranges

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/capability_versioning.py`
- Create: `plugins/whitechronos-control-plane/tests/test_capability_versioning.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_model.py`
- Modify: `plugins/whitechronos-control-plane/tests/test_capability_contracts.py`

**Interfaces:**
- Consumes: Phase 1 full-SemVer validation semantics.
- Produces: `SemVer.parse()`, `VersionRange.parse()`, and `VersionRange.matches()` for Registry and Resolver tasks.

- [ ] **Step 1: Write failing SemVer precedence tests**

Add tests covering:

```python
assert SemVer.parse("1.0.0") < SemVer.parse("1.0.1")
assert SemVer.parse("1.9.9") < SemVer.parse("2.0.0")
assert SemVer.parse("1.0.0-alpha") < SemVer.parse("1.0.0")
assert SemVer.parse("1.0.0-alpha.1") < SemVer.parse("1.0.0-alpha.beta")
assert SemVer.parse("1.0.0+build.1") == SemVer.parse("1.0.0+build.2")
```

The implementation may use `functools.total_ordering` or explicit comparison methods, but build metadata MUST be ignored by equality/ordering semantics used for resolution.

- [ ] **Step 2: Run the new test file and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_versioning.py
```

Expected: FAIL because `capability_versioning.py` does not exist.

- [ ] **Step 3: Implement `SemVer` parsing and precedence**

Implement exactly the interface under **Core Phase 2 Interfaces**. Reuse the Phase 1 SemVer grammar rather than introducing a third-party package.

- [ ] **Step 4: Write failing VersionRange grammar tests**

Pin these behaviors:

```python
assert VersionRange.parse("1.2.3").matches("1.2.3")
assert not VersionRange.parse("1.2.3").matches("1.2.4")
assert VersionRange.parse(">=2.1 <3").matches("2.9.9")
assert not VersionRange.parse(">=2.1 <3").matches("3.0.0")
assert VersionRange.parse(">1 <=2.5").matches("2.5.0")
```

Reject each of:

```text
""
"^1.2.3"
"~1.2.3"
"1.2.x"
">=1.0.0 || <2.0.0"
">=1.0.0,<2.0.0"
">=1.2-alpha"
```

- [ ] **Step 5: Implement `VersionRange.parse()` and `matches()`**

Do not add OR ranges, wildcards, caret, tilde, or comma syntax in this phase.

- [ ] **Step 6: Make `validate_semver()` delegate full-version parsing to the shared versioning primitive**

Preserve the public Phase 1 signature:

```python
def validate_semver(value: str, *, label: str) -> str: ...
```

All existing Phase 1 tests must continue to pass.

- [ ] **Step 7: Run Task 1 tests and Phase 1 regression tests**

Run:

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_capability_versioning.py   plugins/whitechronos-control-plane/tests/test_capability_contracts.py   plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add   plugins/whitechronos-control-plane/runtime/capability_versioning.py   plugins/whitechronos-control-plane/runtime/capability_model.py   plugins/whitechronos-control-plane/tests/test_capability_versioning.py   plugins/whitechronos-control-plane/tests/test_capability_contracts.py
git commit -m "feat: add capability version range semantics"
```

---

### Task 2: Add First-Class Immutable Adapter Records to Registry v2

**Files:**
- Create: `registry/capabilities/v2/adapter.schema.json`
- Create: `plugins/whitechronos-control-plane/runtime/capability_adapter.py`
- Create: `plugins/whitechronos-control-plane/tests/test_capability_adapters.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_model.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_registry.py`
- Modify: `plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py`
- Modify: `registry/capabilities/README.md`
- Modify: `pipeline/capability_registry_policy.py`
- Modify: `tests/test_capability_registry_policy.py`

**Interfaces:**
- Consumes: `SemVer.parse()`, `VersionRange.parse()`, Phase 1 provider/lifecycle identities.
- Produces: `CapabilityAdapter`, `ErrorMapping`, `load_adapter()`, and `CapabilityRegistry.adapters` for Task 4.

- [ ] **Step 1: Write failing Adapter schema/model tests**

The source schema MUST require exactly:

```text
schema_version = 2
record_type = capability_adapter
adapter_id
version
implementation_provider_id
implementation_version
source_contract_id
source_version
target_contract_id
target_version
transformation
lossiness
information_loss
unsupported_cases
error_mapping
conformance_tests
extensions
```

Pin semantic tests for:

- valid `LOSSLESS` with empty `information_loss`;
- valid `LOSSY` with at least one declared loss;
- reject `LOSSLESS` with declared loss;
- reject `LOSSY` with empty loss list;
- reject exact self-loop `source_contract_id@source_version == target_contract_id@target_version`;
- reject malformed adapter ID/version.

- [ ] **Step 2: Run Adapter tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_adapters.py
```

Expected: FAIL because Adapter schema/model support does not exist.

- [ ] **Step 3: Implement `adapter.schema.json` and typed Adapter models**

Use only keywords supported by the existing schema subset.

`error_mapping` items are objects with exactly:

```text
source_error
target_error
```

Adapter provenance and lifecycle are referenced through `implementation_provider_id + implementation_version`; do not duplicate source/digest/license/lifecycle fields in the Adapter record.

- [ ] **Step 4: Extend `CapabilityRegistry` and Registry v2 loading**

Change the registry model to include:

```python
adapters: dict[tuple[str, str], CapabilityAdapter]
```

Add:

```python
def load_adapter(path: Path, schema_path: Path) -> CapabilityAdapter: ...
```

Discover:

```text
registry/capabilities/v2/adapters/**/*.json
```

Registry load MUST reject:

- duplicate `(adapter_id, version)`;
- missing source contract/version;
- missing target contract/version;
- missing implementation provider version;
- malformed `requires[].version_range`;
- any manifest requirement contract ID for which no registered contract version matches its declared range.

The last rule validates contract-definition availability only; it does not require an ACTIVE provider for a requirement.

- [ ] **Step 5: Add Registry fixtures proving Adapter references are file-order independent**

Use temporary registries where Adapter/contract/provider filenames sort in intentionally different orders. The final in-memory registry must be identical.

- [ ] **Step 6: Extend append-only Registry policy to Adapter records**

Add:

```text
registry/capabilities/v2/adapters/
```

to `_RECORD_PREFIXES`.

Tests MUST prove new Adapter files may be added while modify/delete/rename/copy of accepted Adapter records fail.

- [ ] **Step 7: Update Registry v2 README**

Document:

- Adapter record location;
- immutable source/target semantics;
- implementation provider as provenance/lifecycle owner;
- no runtime invocation in Phase 2.

- [ ] **Step 8: Run Task 2 and Phase 1 Registry/policy regressions**

Run:

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_capability_adapters.py   plugins/whitechronos-control-plane/tests/test_capability_registry_v2.py   tests/test_capability_registry_policy.py
```

Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add registry/capabilities plugins/whitechronos-control-plane/runtime   plugins/whitechronos-control-plane/tests   pipeline/capability_registry_policy.py tests/test_capability_registry_policy.py
git commit -m "feat: register immutable capability adapters"
```

---

### Task 3: Implement Deterministic Direct Provider Resolution

**Files:**
- Create: `plugins/whitechronos-control-plane/runtime/capability_resolver.py`
- Create: `plugins/whitechronos-control-plane/tests/test_capability_resolver.py`

**Interfaces:**
- Consumes: `CapabilityRegistry`, `LifecycleState.ACTIVE`, `VersionRange`, provider manifests.
- Produces: `ResolutionRequest`, `ResolutionDecision`, `ResolutionError`, `NoCompatibleProvider`, `PinnedProviderUnavailable`, and `resolve_capability()` for Task 4.

- [ ] **Step 1: Write failing direct-resolution tests**

Build synthetic Registry objects and pin these cases:

1. only `ACTIVE` providers are candidates;
2. a provider without lifecycle state is ineligible;
3. requested version range filters provider contract versions;
4. exact `provider_pin=("provider-a", "1.2.0")` selects that identity when compatible;
5. unavailable/incompatible exact pin raises `PinnedProviderUnavailable` and MUST NOT silently fall back;
6. direct candidate ordering is deterministic across reversed dictionary insertion order;
7. `preferred_provider_ids` influences ranking only among compatible, ACTIVE candidates;
8. no compatible candidate raises `NoCompatibleProvider`.

- [ ] **Step 2: Run Resolver tests and verify RED**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_resolver.py
```

Expected: FAIL because `capability_resolver.py` does not exist.

- [ ] **Step 3: Implement request/decision/error models**

Implement the exact interfaces under **Structural Resolver**.

`provider_pin` is an exact provider-version identity, not a fuzzy family preference.

- [ ] **Step 4: Implement direct candidate generation**

A direct candidate exists when:

- manifest provides the requested `contract_id`;
- exact provided contract version matches the parsed request range;
- provider lifecycle state is exactly `ACTIVE`;
- exact pin matches if supplied.

The Resolver MUST NOT inspect or invent runtime authorization, health, cost, network, credentials, or execution status.

- [ ] **Step 5: Implement deterministic ranking and decision explanation**

For direct routes the generic ordering reduces to:

```text
pin
-> preferred provider rank
-> higher selected contract version
-> higher implementation version
-> provider_id lexical
```

`selection_reason` must name the winning route class (`DIRECT`) and the deterministic tie-break fields used. Do not store evidence outside the returned value in this phase.

- [ ] **Step 6: Run Task 3 tests**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests/test_capability_resolver.py
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add   plugins/whitechronos-control-plane/runtime/capability_resolver.py   plugins/whitechronos-control-plane/tests/test_capability_resolver.py
git commit -m "feat: add deterministic capability resolver"
```

---

### Task 4: Add Adapter-Chain Resolution Without Hidden Semantic Bridges

**Files:**
- Modify: `plugins/whitechronos-control-plane/runtime/capability_adapter.py`
- Modify: `plugins/whitechronos-control-plane/runtime/capability_resolver.py`
- Modify: `plugins/whitechronos-control-plane/tests/test_capability_adapters.py`
- Modify: `plugins/whitechronos-control-plane/tests/test_capability_resolver.py`

**Interfaces:**
- Consumes: Adapter registry, direct Resolver, exact contract/version graph nodes.
- Produces: complete `ResolutionDecision.adapter_chain` route semantics.

- [ ] **Step 1: Write failing single-Adapter route tests**

Create:

```text
request capability://demo/search >=1 <2
adapter A: demo/search@1.0.0 -> demo/search@2.0.0
provider P: provides demo/search@2.0.0
```

With A's implementation provider and P both ACTIVE, `allow_adapters=True` must resolve through A.

With `allow_adapters=False`, the same registry must raise `NoCompatibleProvider`.

- [ ] **Step 2: Write failing chain/cycle tests**

Pin these cases:

- two-Adapter chain resolves in source-to-target order;
- graph cycles terminate and do not loop;
- inactive Adapter implementation provider makes that edge unusable;
- missing source/target reference is already rejected at Registry load;
- direct route always outranks any Adapter route;
- among Adapter routes, fewer hops wins;
- equal-hop LOSSLESS route wins over LOSSY route;
- LOSSY route is excluded unless `allow_lossy_adapters=True`;
- Adapter route selection is identical after reversing Adapter/provider dictionary insertion order.

- [ ] **Step 3: Run Resolver/Adapter tests and verify RED**

Run:

```bash
python -m pytest -q   plugins/whitechronos-control-plane/tests/test_capability_adapters.py   plugins/whitechronos-control-plane/tests/test_capability_resolver.py
```

Expected: failures in route-search tests.

- [ ] **Step 4: Implement Adapter graph traversal**

Graph nodes are exact `(contract_id, contract_version)`.

Edges are immutable Adapter descriptors oriented:

```text
source node -> target node
```

Start nodes are registered versions of the requested contract that match `ResolutionRequest.version_range`.

Traverse only Adapter edges whose implementation provider is ACTIVE. Use a visited-node/path strategy so cycles cannot recurse indefinitely.

The graph is finite and source-controlled; do not introduce an arbitrary hard-coded hop ceiling in this phase.

- [ ] **Step 5: Generate adapted provider candidates**

A route is complete when the current graph node matches a contract/version provided by an ACTIVE provider.

Do not invoke the Adapter or provider.

- [ ] **Step 6: Apply the full deterministic ordering**

Use the ordering in **Structural Resolver** exactly. Adapter-chain lexical identity is the tuple:

```python
((adapter_id, version), ...)
```

- [ ] **Step 7: Run Tasks 3-4 tests and full Control Plane unit tests**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add   plugins/whitechronos-control-plane/runtime/capability_adapter.py   plugins/whitechronos-control-plane/runtime/capability_resolver.py   plugins/whitechronos-control-plane/tests/test_capability_adapters.py   plugins/whitechronos-control-plane/tests/test_capability_resolver.py
git commit -m "feat: resolve explicit capability adapter chains"
```

---

### Task 5: Enforce Provider Isolation in CI

**Files:**
- Create: `pipeline/capability_dependency_policy.py`
- Create: `tests/test_capability_dependency_policy.py`
- Modify: `.github/workflows/whitechronos-runtime-foundation.yml`
- Modify: `plugins/whitechronos-control-plane/tests/test_repository_integration.py`
- Modify: `registry/capabilities/README.md`

**Interfaces:**
- Consumes: Registry v2 local provider manifests (`source_type == "local"`, `source` path), repository filesystem.
- Produces:

```python
@dataclass(frozen=True)
class DependencyViolation:
    provider_id: str
    implementation_version: str
    source_file: str
    target_provider_id: str
    reason: str


def scan_provider_boundaries(
    repo_root: Path,
    registry: CapabilityRegistry,
) -> tuple[DependencyViolation, ...]: ...
```

CLI:

```bash
python pipeline/capability_dependency_policy.py --repo .
```

Exit 0 with `CAPABILITY_DEPENDENCY_POLICY=PASS`; exit 1 with sorted violations otherwise.

- [ ] **Step 1: Write failing synthetic provider-boundary tests**

Use a temporary repo with two local provider manifests and source roots:

```text
plugins/provider-a/
plugins/provider-b/
```

Provider A must be rejected for each of:

```python
from provider_b import internal
import provider_b.internal
importlib.import_module("provider_b.internal")
__import__("provider_b.internal")
sys.path.append("plugins/provider-b")
Path("plugins/provider-b/private.json")
open("plugins/provider-b/private.json")
```

The same provider may reference files within its own source root.

- [ ] **Step 2: Add fail-closed source-root tests**

Reject registry/provider layouts where:

- a local provider source escapes repository root;
- two provider source roots are identical;
- one provider root is nested inside another provider root;
- a local provider source path does not exist when the scanner runs.

These conditions make boundary enforcement ambiguous and therefore fail closed.

- [ ] **Step 3: Run boundary-policy tests and verify RED**

Run:

```bash
python -m pytest -q tests/test_capability_dependency_policy.py
```

Expected: FAIL because the policy does not exist.

- [ ] **Step 4: Implement AST/static-literal boundary scanning**

For Python files under each registered local provider root, inspect:

- `ast.Import`;
- `ast.ImportFrom`;
- literal argument to `importlib.import_module()`;
- literal argument to `__import__()`;
- literal paths passed to `open()` and `pathlib.Path()`;
- literal paths appended/inserted into `sys.path`.

For import-name matching, derive the other provider's common module aliases from its source-directory basename:

```text
provider-b
provider_b
```

The policy deliberately targets direct private implementation coupling. It does not try to prove all possible dynamic behavior or network access; Zero-Trust runtime enforcement is a later phase.

- [ ] **Step 5: Ensure empty/current Registry v2 passes**

The integrated repository currently has no accepted local provider records under Registry v2. The policy must therefore return PASS without inventing provider boundaries from Registry v1.

- [ ] **Step 6: Wire the policy into Runtime Foundation CI**

Add workflow triggers for:

```text
pipeline/capability_dependency_policy.py
tests/test_capability_dependency_policy.py
```

Add a step after append-only Registry validation:

```bash
python pipeline/capability_dependency_policy.py --repo .
```

Keep `permissions: contents: read`.

- [ ] **Step 7: Add repository integration tests for the new gate**

Tests must assert:

- the workflow triggers when dependency-policy source/tests change;
- the workflow executes `capability_dependency_policy.py --repo .`;
- Registry v1 loader and current Runtime Doctor route tests remain unchanged.

- [ ] **Step 8: Update Registry README with the isolation invariant**

Document that local placement never grants permission for private cross-provider imports/filesystem access; provider communication is contract-based and runtime invocation remains outside Phase 2.

- [ ] **Step 9: Run the full Phase 2 verification suite**

Run:

```bash
python -m pytest -q plugins/whitechronos-control-plane/tests
python -m pytest -q
python pipeline/capability_registry_policy.py --base HEAD^ --head HEAD
python pipeline/capability_dependency_policy.py --repo .
node --test   plugins/subagent-broker/tests/mcp-protocol.test.mjs   plugins/subagent-broker/tests/repository-integration.test.mjs
python -m pytest -q plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
```

Expected:

```text
all pytest suites PASS
CAPABILITY_REGISTRY_POLICY=PASS
CAPABILITY_DEPENDENCY_POLICY=PASS
Broker compatibility PASS
Awesome Codex integration PASS
engineering compatibility gate PASS
Protocol Zero gate PASS
```

Runtime Doctor/live-smoke status is not promoted by this phase.

- [ ] **Step 10: Commit**

```bash
git add   pipeline/capability_dependency_policy.py   tests/test_capability_dependency_policy.py   .github/workflows/whitechronos-runtime-foundation.yml   plugins/whitechronos-control-plane/tests/test_repository_integration.py   registry/capabilities/README.md
git commit -m "ci: enforce capability dependency boundaries"
```

---

## Phase 2 Acceptance Checklist

Implementation is ready for branch review only when all of these are demonstrated:

1. Version ranges support the architecture's `>=2.1 <3` form with deterministic SemVer precedence and reject unsupported syntax.
2. Registry v2 loads immutable Adapter records without changing Registry v1 behavior.
3. Accepted Adapter records are protected by the append-only Git-diff gate.
4. Adapter source/target contracts and implementation provider versions are validated exactly.
5. Manifest requirement ranges are parseable and reference at least one defined contract version.
6. Direct Resolver selection is deterministic and uses only ACTIVE provider versions.
7. Exact provider pinning fails closed when unavailable.
8. Adapter routes are explicit in `ResolutionDecision.adapter_chain`.
9. Direct routes beat adapted routes.
10. Adapter cycles terminate safely; inactive Adapter implementations cannot participate.
11. LOSSY Adapters are excluded by default and require explicit opt-in.
12. Resolution remains side-effect-free and does not claim runtime authorization, health, or execution.
13. Local provider roots cannot directly import/load/read another provider's private implementation using the covered static patterns.
14. Ambiguous/escaping/overlapping provider roots fail closed.
15. Runtime Foundation CI runs both append-only and dependency-boundary gates.
16. Full repository regression remains green.
17. Runtime Doctor routing and Registry v1 descriptors remain unchanged.
18. No live smoke is run and `LIVE_VERIFIED` is not claimed.
19. PR #57 remains DRAFT unless separately authorized.

## Self-Review Results

**Spec coverage:** This plan covers implementation-decomposition item 2 from the approved umbrella spec: Resolver, Adapter semantics, and dependency-boundary enforcement. Policy/authorization, health/circuit data, execution/invocation, Knowledge/Evolution Ledgers, Runtime Evidence, and Zero-Trust runtime enforcement remain intentionally deferred to their later phases.

**Step scan:** Each task has a RED test step, a minimal implementation boundary, a GREEN verification step, and a commit boundary. No task requires the implementer to invent interface names or unsupported version syntax.

**Type consistency:** Adapter identity is consistently `(adapter_id, version)`; provider identity remains `(provider_id, implementation_version)`; contract graph nodes remain exact `(contract_id, version)`; Resolver returns Adapter identities in source-to-target order.

**Review Focus coverage:** All five listed failure classes are assigned explicit tests in Tasks 1-5.

**Proportion:** The plan specifies interfaces, ranking semantics, gates, and tests that the umbrella architecture leaves open, while deliberately omitting implementation bodies except where a command or exact grammar is itself the requirement.

## Execution Boundary

This plan does **not** authorize implementation.

After the user reviews and explicitly approves this written Phase 2 plan, execution must use either:

- `superpowers:executing-plans` for Native execution; or
- `superpowers:subagent-driven-development` only if true independent subagents are actually available and verified.

Implementation should occur on a new feature branch forked from the then-current `feat/cloud-runtime-foundation`; Phase 2 must not be implemented directly on the PR #57 head branch.
