# WhiteChronos Connection + TinyFish Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add an evidence-based WhiteChronos connection preflight and a thin TinyFish controller so GitHub, GitLab, TinyFish, Arena, Superpowers and runtime claims are classified truthfully without storing credentials or treating configuration as live proof.

**Architecture:** Extend the existing whitechronos-control-plane with a separate connection-state model, registry metadata, a deterministic evidence-normalization CLI, and a reusable Connection Controller Skill. Add a separate local tinyfish-controller plugin for provider-specific routing, cost, Browser Profile and recovery rules while leaving actual TinyFish authentication in the official ChatGPT app. Native GitHub/GitLab connectors remain the preferred repository API path; TinyFish browser automation is secondary and user-directed.

**Tech Stack:** Python 3.12, pytest, the repository JSON Schema subset, TOML project configuration, Codex local plugin manifests/Skills, GitHub Actions, and the existing GitHub/GitLab mirror/parity workflow.

**Spec:** docs/superpowers/specs/2026-10-08-whitechronos-connection-tinyfish-design.md

## Global Constraints

- Do not store GitHub, GitLab or TinyFish passwords, tokens, cookies or browser storage in Git.
- Do not request passwords in chat.
- Repository configuration is not proof of host discovery, authentication or live capability.
- Keep GitHub/GitLab mirror parity independent from current ChatGPT connector authentication.
- Prefer native GitHub/GitLab connectors for repository API reads/writes.
- TinyFish Browser Profile authentication is an optional secondary capability unless the current task explicitly requires authenticated browser UI work.
- Routine TinyFish preflight must not start Agent runs, Browser runs, monitors, top-ups or auto-reload changes.
- TinyFish service PASS plus Browser Profile API failure is DEGRADED, not whole-service FAIL.
- HOST_POLICY_BLOCKED must never trigger a bypass or a source-code change presented as a workaround.
- Keep existing Runtime Doctor semantics intact; do not add connection-only states to CheckStatus.
- Preserve all existing Superpowers, Arena, ECC, Matt Pocock, Broker, Awesome LLM Apps and engineering-governance behavior.
- Do not merge, deploy, canary, stable, run live smoke, R2/R3 or declare PRODUCTION COMPLETE without separate authorization.
- Implementation starts from the then-current authoritative main, not from the documentation branch; carry the approved spec and plan into the implementation branch as provenance.
- Use TDD for every code change and make task-level commits.

## Review Focus

1. **Unknown host inventory:** missing host evidence must remain UNAVAILABLE/unverified rather than inferred from repository config; Task 1 tests this.
2. **TinyFish partial outage:** service authentication can pass while Browser Profiles fail; Tasks 1 and 4 pin this to DEGRADED with non-browser capabilities still usable.
3. **Optional vs required capability:** an optional degraded profile must not fail REQUIRED_TASK_CONNECTIONS; Task 3 tests the aggregate report.
4. **Schema backward compatibility:** existing v1 Arena/Broker descriptors must continue loading unchanged after the optional connection block is added; Task 2 tests this.
5. **Secrets/cost leakage:** preflight input/output and controller policy must not persist secrets or trigger metered TinyFish operations; Tasks 3 and 4 test both behaviors.

---

### Task 1: Connection state model and deterministic evaluator

**Files:**
- Create: plugins/whitechronos-control-plane/runtime/connection_models.py
- Create: plugins/whitechronos-control-plane/runtime/connections.py
- Create: plugins/whitechronos-control-plane/tests/test_connections.py

**Interfaces:**
- Produces ConnectionStatus enum with PASS, DEGRADED, FAIL, UNAVAILABLE, HOST_RELOAD_REQUIRED, USER_ACTION_REQUIRED, HOST_POLICY_BLOCKED, SECURITY_REVIEW_REQUIRED, NOT_APPLICABLE.
- Produces ConnectionEvidence(source: str, operation: str, observed_at: str, target: str | None, summary: str).
- Produces ConnectionSignals(configured: bool, host_visible: bool | None, authenticated: bool | None, target_accessible: bool | None, live_verified: bool | None, authentication_required: bool, target_required: bool, live_verification_required: bool, host_absence_status: ConnectionStatus, required_blocker: ConnectionStatus | None, optional_degradations: tuple[str, ...]).
- Produces ConnectionObservation(integration_id: str, configured: bool, host_visible: bool | None, authenticated: bool | None, target_accessible: bool | None, live_verified: bool | None, status: ConnectionStatus, detail: str, evidence: tuple[ConnectionEvidence, ...]).
- Produces evaluate_connection(integration_id: str, signals: ConnectionSignals, evidence: tuple[ConnectionEvidence, ...] = ()) -> ConnectionObservation.
- Consumes no Runtime Doctor interface; this module is intentionally independent of CheckStatus.

- [ ] **Step 1: Write the failing evaluator tests**

Add tests named:

~~~
def test_configured_does_not_imply_host_visible(): ...
def test_missing_observed_host_can_be_host_reload_required(): ...
def test_auth_failure_requires_user_action(): ...
def test_target_failure_is_fail_closed(): ...
def test_optional_degradation_returns_degraded_without_blocking_base_capability(): ...
def test_required_host_policy_block_wins_over_optional_degradation(): ...
def test_live_verification_is_required_only_when_requested(): ...
~~~

Assert exact ConnectionStatus values and preserve None for dimensions that were not observed.

- [ ] **Step 2: Run the new tests and verify RED**

Run:

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_connections.py
~~~

Expected: FAIL because connection_models / connections do not exist.

- [ ] **Step 3: Implement the connection model and evaluator**

Evaluation precedence is:

1. required_blocker when present;
2. required integration not configured -> FAIL;
3. observed host absence -> host_absence_status;
4. required authentication explicitly false -> USER_ACTION_REQUIRED;
5. required target access explicitly false -> FAIL;
6. required live verification explicitly false -> FAIL;
7. any optional_degradations -> DEGRADED;
8. otherwise -> PASS.

Do not coerce None to False.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_connections.py
~~~

Expected: PASS.

- [ ] **Step 5: Run existing Runtime Doctor model tests**

Run:

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_doctor.py plugins/whitechronos-control-plane/tests/test_codex_probe.py
~~~

Expected: PASS; no CheckStatus regression.

- [ ] **Step 6: Commit**

~~~
git add plugins/whitechronos-control-plane/runtime/connection_models.py
git add plugins/whitechronos-control-plane/runtime/connections.py
git add plugins/whitechronos-control-plane/tests/test_connections.py
git commit -m "feat: add connection state evaluator"
~~~

### Task 2: Backward-compatible integration registry connection metadata

**Files:**
- Modify: plugins/whitechronos-control-plane/runtime/model.py
- Modify: plugins/whitechronos-control-plane/runtime/registry.py
- Modify: registry/integrations/schema.json
- Modify: registry/integrations/index.json
- Create: registry/integrations/github-connector.json
- Create: registry/integrations/gitlab-connector.json
- Create: registry/integrations/tinyfish.json
- Modify: plugins/whitechronos-control-plane/tests/test_schema_registry.py

**Interfaces:**
- Produces ConnectionSpec(surfaces: tuple[str, ...], auth_required: bool, safe_probe: str, target_probe: str | None, paid_probe_forbidden: bool, credential_storage: str).
- Modifies IntegrationDescriptor.connection: ConnectionSpec | None.
- Preserves schema_version == 1; connection is optional so existing v1 descriptors remain valid.

- [ ] **Step 1: Write failing registry compatibility tests**

Add:

~~~
def test_existing_v1_descriptors_still_load_without_connection_metadata(): ...
def test_registry_loads_github_gitlab_and_tinyfish_connection_specs(): ...
def test_connection_schema_rejects_unknown_surface(): ...
def test_connection_schema_rejects_extra_properties(): ...
def test_connection_target_probe_may_be_null(): ...
~~~

Expected descriptor values:

- github-connector: source_type official_plugin, execution_class MCP_OR_CONNECTOR, controller_plugin whitechronos-control-plane, safe_probe github.get_profile, target_probe github.get_repo, provider-managed credentials, paid probe forbidden.
- gitlab-connector: same controller/execution class, safe_probe gitlab.get_current_user, target_probe gitlab.get_project.
- tinyfish: source_type official_plugin, execution_class MCP_OR_CONNECTOR, controller_plugin tinyfish-controller, safe_probe tinyfish.get_wallet, target_probe null, provider-managed credentials, paid probe forbidden.

Allowed surfaces are exactly chatgpt_plugin, connector, and codex_plugin.

- [ ] **Step 2: Run registry tests and verify RED**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_schema_registry.py
~~~

Expected: FAIL because ConnectionSpec and new descriptors/schema fields are absent.

- [ ] **Step 3: Extend model, parser and schema**

Add ConnectionSpec to runtime/model.py, parse it in runtime/registry.py, and add optional connection to schema.json.

Keep the schema validator unchanged unless a failing test proves an unsupported keyword is required; the planned schema uses only the validator's existing type, enum, required, properties, additionalProperties, items and minLength subset.

- [ ] **Step 4: Add provider descriptors and index entries**

Append github-connector.json, gitlab-connector.json and tinyfish.json after the existing descriptors. Do not remove or rewrite existing descriptors.

- [ ] **Step 5: Run registry tests and verify GREEN**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_schema_registry.py
~~~

Expected: PASS, including unchanged Arena/Broker descriptor semantics.

- [ ] **Step 6: Commit**

~~~
git add plugins/whitechronos-control-plane/runtime/model.py
git add plugins/whitechronos-control-plane/runtime/registry.py
git add plugins/whitechronos-control-plane/tests/test_schema_registry.py
git add registry/integrations/schema.json registry/integrations/index.json
git add registry/integrations/github-connector.json registry/integrations/gitlab-connector.json registry/integrations/tinyfish.json
git commit -m "feat: describe provider connection contracts"
~~~

### Task 3: Connection preflight report, CLI and reusable Skill

**Files:**
- Create: plugins/whitechronos-control-plane/runtime/connection_preflight.py
- Create: plugins/whitechronos-control-plane/scripts/connection_preflight.py
- Create: plugins/whitechronos-control-plane/tests/test_connection_preflight.py
- Create: plugins/whitechronos-control-plane/skills/whitechronos-connection-controller/SKILL.md
- Create: plugins/whitechronos-control-plane/skills/whitechronos-connection-controller/agents/openai.yaml
- Create: plugins/whitechronos-control-plane/skills/whitechronos-connection-controller/references/connection-contract.md
- Create: plugins/whitechronos-control-plane/skills/whitechronos-connection-controller/references/recovery-matrix.md
- Modify: plugins/whitechronos-control-plane/.codex-plugin/plugin.json
- Modify: plugins/whitechronos-control-plane/README.md
- Modify: plugins/whitechronos-control-plane/tests/test_repository_integration.py

**Interfaces:**
- Produces ConnectionRequirement(integration_id: str, target_required: bool, live_verification_required: bool).
- Produces ConnectionReport(observations: tuple[ConnectionObservation, ...], required_task_connections_pass: bool, blockers: tuple[str, ...]).
- Produces build_connection_report(repo_root: Path, payload: dict[str, object]) -> ConnectionReport.
- CLI: python plugins/whitechronos-control-plane/scripts/connection_preflight.py --repo . --input evidence.json --json.
- The CLI consumes host/provider evidence supplied by the current harness; it does not attempt to call ChatGPT connectors or TinyFish from local Python.
- JSON output key: required_task_connections_pass. DEGRADED alone is non-blocking.

- [ ] **Step 1: Write failing report tests**

Cover:

~~~
def test_preflight_passes_required_github_and_gitlab_with_fresh_signals(): ...
def test_optional_tinyfish_profile_degradation_does_not_fail_required_connections(): ...
def test_required_tinyfish_browser_policy_block_fails_required_connections(): ...
def test_unknown_integration_id_fails_closed(): ...
def test_preflight_output_does_not_echo_secret_fields(): ...
def test_cli_emits_deterministic_json(): ...
def test_acceptance_matrix_can_combine_connections_with_process_layer_evidence(): ...
~~~

For the secret test include token, password, cookie and authorization-like keys and assert they do not appear in serialized output.

- [ ] **Step 2: Run preflight tests and verify RED**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_connection_preflight.py
~~~

Expected: FAIL because report/CLI code does not exist.

- [ ] **Step 3: Implement report builder and CLI**

build_connection_report must:

- load the repository registry;
- reject unknown integration IDs;
- derive configured and authentication_required from the descriptor rather than caller input;
- use caller evidence only for current host/auth/target/live observations;
- strip/ignore unrecognized evidence fields instead of serializing them;
- treat DEGRADED as non-blocking unless the payload marks the degraded capability as required through required_blocker;
- preserve deterministic integration ordering from the request.

CLI exits:
- 0 when all required connections pass;
- 2 when a required connection is blocked/unavailable/user-action-required;
- 1 for malformed input or internal validation failure.

- [ ] **Step 4: Write the Connection Controller Skill and references**

The Skill directs a host agent to:

1. inspect actual tool/plugin inventory;
2. run safe provider identity probes using current native tools;
3. read target repository/project metadata when needed;
4. keep mirror parity separate;
5. classify TinyFish service and Browser Profile health separately;
6. never infer host visibility/authentication from .codex/config.toml;
7. never request or persist credentials;
8. pass only non-secret evidence to the local preflight normalizer when available;
9. verify Superpowers availability/configuration before software execution and preserve it as the process owner;
10. verify Arena availability/configuration before high-impact final review, and delegate Codex/Arena/Broker/native runtime claims to Runtime Doctor rather than inferring them from config.

- [ ] **Step 5: Update plugin metadata and repository-integration tests**

Bump whitechronos-control-plane version from 0.1.0 to 0.2.0.

Change the manifest test to assert exactly:

~~~
["codex-runtime-doctor", "whitechronos-connection-controller"]
~~~

Add assertions that README documents both CLIs, the new Skill states repository config is not authentication proof, and the Skill explicitly checks Superpowers/Arena while routing runtime-capability claims to Runtime Doctor.

- [ ] **Step 6: Run focused tests and verify GREEN**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_connection_preflight.py plugins/whitechronos-control-plane/tests/test_repository_integration.py
~~~

Expected: PASS.

- [ ] **Step 7: Commit**

~~~
git add plugins/whitechronos-control-plane/runtime/connection_preflight.py
git add plugins/whitechronos-control-plane/scripts/connection_preflight.py
git add plugins/whitechronos-control-plane/tests/test_connection_preflight.py
git add plugins/whitechronos-control-plane/skills/whitechronos-connection-controller
git add plugins/whitechronos-control-plane/.codex-plugin/plugin.json
git add plugins/whitechronos-control-plane/README.md plugins/whitechronos-control-plane/tests/test_repository_integration.py
git commit -m "feat: add WhiteChronos connection preflight"
~~~

### Task 4: TinyFish controller policy plugin

**Files:**
- Create: plugins/tinyfish-controller/.codex-plugin/plugin.json
- Create: plugins/tinyfish-controller/README.md
- Create: plugins/tinyfish-controller/skills/tinyfish-controller/SKILL.md
- Create: plugins/tinyfish-controller/skills/tinyfish-controller/agents/openai.yaml
- Create: plugins/tinyfish-controller/skills/tinyfish-controller/references/provider-contract.md
- Create: plugins/tinyfish-controller/skills/tinyfish-controller/references/recovery-matrix.md
- Create: plugins/tinyfish-controller/tests/test_policy.py
- Create: plugins/tinyfish-controller/tests/test_repository_integration.py
- Modify: .agents/plugins/marketplace.json
- Modify: .codex/config.toml
- Modify: AGENTS.md

**Interfaces:**
- Produces local Codex controller tinyfish-controller; Skills only, no MCP server.
- Provider remains the official TinyFish ChatGPT app/tool surface; repository plugin stores no provider credentials.
- Routing: public search/read -> TinyFish search/fetch when selected; repository API work -> native GitHub/GitLab; concrete user-directed UI -> TinyFish browser automation; authenticated UI -> Browser Profile only after provider-managed login and healthy profile APIs.
- Browser timeout/error must be polled through the existing run rather than automatically starting a duplicate run.
- Monitors are created only for explicit monitoring intent.

- [ ] **Step 1: Write failing policy and registration tests**

Assert rules for:

- no passwords in chat;
- no automatic profile creation during preflight;
- no paid Agent/Browser/monitor health checks;
- no wallet top-up/auto-reload mutation;
- native GitHub/GitLab preferred for repository work;
- TinyFish profile failure degradable independently of service auth;
- browser/profile policy block is not a source-code bug;
- monitor operations require explicit user intent;
- no duplicate browser run after timeout/error.

Repository tests assert marketplace entry, .codex/config.toml enablement and preservation of every existing plugin.

- [ ] **Step 2: Run TinyFish controller tests and verify RED**

~~~
python -m pytest -q plugins/tinyfish-controller/tests
~~~

Expected: FAIL because the plugin does not exist.

- [ ] **Step 3: Implement controller plugin, Skill and references**

Create version 1.0.0 local plugin with name tinyfish-controller and skills ./skills/, plus normal WhiteChronos author/license/interface metadata.

Do not add .mcp.json or provider secrets.

- [ ] **Step 4: Register controller in project config and routing rules**

Add tinyfish-controller to .agents/plugins/marketplace.json with local source ./plugins/tinyfish-controller, INSTALLED_BY_DEFAULT, ON_INSTALL, product CODEX.

Add:

~~~
[plugins."tinyfish-controller@whitechronos-repo"]
enabled = true
~~~

to .codex/config.toml.

Add an AGENTS.md TinyFish layer preserving:

~~~
repository/system/user constraints
-> Superpowers
-> specialized capabilities/controllers
-> Connection Controller / TinyFish policy when relevant
-> native GitHub/GitLab evidence and mutation
-> GitHub Arena final review
~~~

- [ ] **Step 5: Run tests and verify GREEN**

~~~
python -m pytest -q plugins/tinyfish-controller/tests
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py
~~~

Expected: PASS.

- [ ] **Step 6: Commit**

~~~
git add plugins/tinyfish-controller
git add .agents/plugins/marketplace.json .codex/config.toml AGENTS.md
git commit -m "feat: add TinyFish controller policy"
~~~

### Task 5: Connection runbook and CI regression coverage

**Files:**
- Create: docs/runbooks/whitechronos-connections.md
- Modify: .github/workflows/whitechronos-runtime-foundation.yml
- Modify: plugins/whitechronos-control-plane/tests/test_repository_integration.py
- Modify: plugins/tinyfish-controller/tests/test_repository_integration.py

**Interfaces:**
- Runbook documents exact states and recovery actions; it never promises permanent OAuth connectivity.
- Existing Runtime Foundation workflow remains the single CI entry for this integration slice; do not create a second overlapping workflow.
- CI is local/offline with respect to provider authentication. It validates policy/config/code only and must not call live GitHub/GitLab/TinyFish accounts.

- [ ] **Step 1: Write failing documentation/CI tests**

Assert runbook contains:

~~~
CONFIGURED != HOST_VISIBLE
HOST_VISIBLE != AUTHENTICATED
AUTHENTICATED != TARGET_ACCESSIBLE
MIRROR_PARITY is separate
DEGRADED
HOST_POLICY_BLOCKED
USER_ACTION_REQUIRED
~~~

Assert workflow:

- includes plugins/tinyfish-controller/** in PR and push filters;
- runs python -m pytest -q plugins/tinyfish-controller/tests;
- contains no TinyFish browser/agent/monitor invocation or live provider credential;
- preserves full regression, Broker compatibility and engineering governance steps.

- [ ] **Step 2: Run focused tests and verify RED**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests/test_repository_integration.py plugins/tinyfish-controller/tests/test_repository_integration.py
~~~

Expected: FAIL until runbook/workflow changes exist.

- [ ] **Step 3: Write runbook**

Document normal preflight, safe probe names, non-secret evidence format, expired-auth recovery, TinyFish list_profiles failure, HOST_POLICY_BLOCKED, canonical mirror parity, Codex refresh after plugin changes, and the product-surface limitation.

- [ ] **Step 4: Extend Runtime Foundation CI**

Add TinyFish controller paths and tests; leave detached Runtime Doctor verification unchanged.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run the Step 2 command again.

Expected: PASS.

- [ ] **Step 6: Commit**

~~~
git add docs/runbooks/whitechronos-connections.md
git add .github/workflows/whitechronos-runtime-foundation.yml
git add plugins/whitechronos-control-plane/tests/test_repository_integration.py
git add plugins/tinyfish-controller/tests/test_repository_integration.py
git commit -m "test: cover connection and TinyFish integration"
~~~

### Task 6: Full repository regression and governance verification

**Files:** no product-code changes expected. Fix only verified regressions caused by Tasks 1-5.

- [ ] **Step 1: Run Control Plane suite**

~~~
python -m pytest -q plugins/whitechronos-control-plane/tests
~~~

Expected: PASS.

- [ ] **Step 2: Run TinyFish controller suite**

~~~
python -m pytest -q plugins/tinyfish-controller/tests
~~~

Expected: PASS.

- [ ] **Step 3: Run full Python regression**

~~~
python -m pytest -q
~~~

Expected: PASS.

- [ ] **Step 4: Run Subagent Broker compatibility regression**

~~~
node --test plugins/subagent-broker/tests/mcp-protocol.test.mjs plugins/subagent-broker/tests/repository-integration.test.mjs
~~~

Expected: PASS.

- [ ] **Step 5: Run engineering-governance gates**

~~~
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
python -m pytest -q tests/test_engineering_compatibility_gate.py
python -m pytest -q tests/test_protocol_zero_gate.py
~~~

Expected: all PASS.

- [ ] **Step 6: Run Runtime Doctor locally without claiming host discovery**

~~~
python plugins/whitechronos-control-plane/scripts/runtime_doctor.py --repo . --json
~~~

Expected: local/config checks reflect the environment; host tools are not invented from config.

- [ ] **Step 7: Verify diff contains no secrets or provider state**

~~~
git status --short
git diff --check
git diff --stat
git grep -nEi "(password|access[_-]?token|refresh[_-]?token|cookie|authorization: bearer)" -- .
~~~

Expected: no credential value introduced. Documentation/test policy words may match and must be manually inspected rather than blindly treated as secrets.

- [ ] **Step 8: Commit only if verification required a legitimate fix**

Use a focused fix commit if needed. Do not create an empty commit.

### Task 7: Review, PR, GitHub CI and GitLab parity evidence

**Files:** no direct main mutation; PR metadata and provider evidence only.

**Interfaces:**
- Consumes verified implementation branch.
- Produces a GitHub PR and exact-SHA CI/parity evidence.
- Does not authorize merge/deploy/live smoke.

- [ ] **Step 1: Run Superpowers code-review workflow**

Review the whole implementation branch. If true isolated subagents are available, use the approved real subagent route; otherwise use the official fallback and describe it truthfully.

Expected: no unresolved correctness/security defects.

- [ ] **Step 2: Run GitHub Arena high-impact review**

Review connection-state correctness, schema compatibility, fail-closed semantics, credential handling, TinyFish cost policy, CI scope and product-surface truthfulness.

Expected: any fatal flaw is fixed and re-verified before PR creation.

- [ ] **Step 3: Open GitHub pull request**

Base: then-current main. Head: implementation branch created at execution time.

PR body links approved spec, this plan, task commits, test results, and states that merge/deploy/canary/stable/live smoke/R2/R3/PRODUCTION COMPLETE are not implied.

- [ ] **Step 4: Wait for GitHub CI and inspect exact head SHA**

All workflows applicable to touched paths must PASS on the current PR head. If head changes after fixes, discard stale CI evidence.

- [ ] **Step 5: Verify GitLab mirror/parity on exact PR head SHA when eligible**

Use the existing canonical parity mechanism. Require exact provider identities and exact commit SHA match before recording MIRROR_PARITY=HEALTHY.

Do not substitute account identity link, historical parity from another SHA, or unrelated pipeline success.

- [ ] **Step 6: Record gate state and STOP**

Expected pre-merge state:

~~~
SPEC_APPROVED=YES
PLAN_APPROVED=YES
TDD=PASS
REGRESSION=PASS
SECURITY_REVIEW=PASS
ARENA=PASS
GITHUB_CI=PASS
MIRROR_PARITY=HEALTHY   # only if exact-head evidence exists
MERGE_AUTHORIZED=NO     # unless separately authorized
PRODUCTION_COMPLETE=NO
~~~

Do not merge or start downstream production gates without separate authority.

## Execution bootstrap

At implementation time:

1. invoke superpowers:using-git-worktrees;
2. fetch and inspect the then-current authoritative main;
3. create an isolated implementation worktree/branch, suggested name feat/whitechronos-connection-tinyfish;
4. if the approved spec/plan commits are not yet in main, carry only those documentation commits into the implementation branch as provenance;
5. invoke the selected execution skill;
6. execute Tasks 1-7 in order, preserving TDD and review gates.
