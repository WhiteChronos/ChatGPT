# Awesome LLM Apps Full-System Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the full useful system surface of `Shubhamsaboo/awesome-llm-apps` into `WhiteChronos/ChatGPT` with seven canonical project Skills, a complete agent/app/component catalog, a controlled functional source mirror, runtime safety gates, a Codex controller, automated upstream synchronization, and a ChatGPT `skill.zip`.

**Architecture:** A Python ingestion library owns deterministic cataloging, source-inclusion policy, external-reference discovery, execution-risk classification, and Skill projection. A thin Bash synchronizer clones upstream without executing it, invokes the Python pipeline, updates provenance/lock data, and is wrapped by a GitHub Actions workflow that pushes review branches. The controller consumes generated metadata and participates in the existing routing order: Superpowers -> ECC -> Matt Pocock -> Awesome LLM Apps -> GitHub -> GitHub Arena.

**Tech Stack:** Python 3.11+ standard library, Bash, JSON/JSON Schema, TOML, YAML/GitHub Actions, Git, existing WhiteChronos Codex marketplace conventions, ChatGPT Skill packaging tools.

**Spec:** `docs/superpowers/specs/2026-10-03-awesome-llm-apps-full-system-integration-design.md`

## Global Constraints

- Preserve upstream Apache-2.0 licensing and any more-specific notices found below the upstream root.
- Initial audited upstream snapshot is commit `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`.
- Account for the audited snapshot invariants: 2531 tree entries, 1976 blobs, 10 total `SKILL.md`, 7 canonical registry Skills, 223 README files, 194 dependency manifests, 65 environment examples, 8 Dockerfiles, 139 MCP-related files, and 996 audited code files.
- Do not execute upstream source during synchronization.
- Do not automatically install dependencies, register MCP servers, create credentials, launch browser automation, start daemons, deploy cloud resources, or run self-modifying systems.
- Exclude nested `.git`, generated build/cache/dependency directories, and binary demo media larger than 10 MiB from the WhiteChronos mirror; preserve an exclusion record for every omitted upstream file.
- Project-internal Skills remain scoped to their containing example and are never projected globally.
- Canonical Skill projection is collision-safe and ownership-tracked; never overwrite Matt Pocock-managed or unmanaged project Skills.
- External linked agent/application projects are catalogued as `external_reference` only and are never recursively cloned or executed by synchronization.
- Discoverability never grants execution authority; every projected Skill and catalog entry carries deterministic execution-risk metadata.
- Preserve `multi_agent = true` and the existing Superpowers, ECC, Matt Pocock, and GitHub Arena integrations.
- Do not claim that an upstream example is a native Codex subagent, native ChatGPT agent, MCP connector, or background automation unless that runtime surface actually exists.
- All repository governance/CI gates must be green before merge.
- The final ChatGPT controller package must be named exactly `skill.zip` and remain under 25 MiB.

## Review Focus

- **Symlinks/path traversal:** an upstream symlink must not escape the mirror root or cause copying from outside the clone; Task 3 pins this with an escape-symlink rejection test.
- **Catalog ambiguity:** nested READMEs/manifests must attach to the nearest qualifying application rather than the wrong ancestor; Task 2 pins nested ownership behavior.
- **External-link overcapture:** sponsor/social/translation/documentation URLs must not become AI-agent entries; Task 2 pins allow/deny examples.
- **Skill collision across controllers:** an Awesome LLM Apps Skill name that matches a Matt-managed or unmanaged Skill must fail closed; Task 4 pins both cases.
- **Upstream drift:** a future upstream change to license/registry/layout must produce an auditable sync failure or changed review branch, never silently weaken constraints; Tasks 5 and 9 pin the drift checks.

---

## File Structure

### Core ingestion library

- Create `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_catalog.py` — pure Python catalog discovery, stable IDs, execution-risk classification, external-reference parsing, snapshot statistics.
- Create `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_mirror.py` — inclusion/exclusion policy, safe file/symlink copying, excluded-file ledger.
- Create `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_skills.py` — canonical registry validation, risk metadata, ownership manifest, collision-safe Skill projection.
- Create `plugins/awesome-llm-apps-controller/scripts/build_catalog.py` — CLI around catalog generation and schema validation.
- Create `plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh` — clone/orchestrate only; never execute upstream code.

### Tests and fixtures

- Create `plugins/awesome-llm-apps-controller/tests/fixtures/upstream/` — minimal deterministic fake upstream with canonical Skills, nested apps, internal Skill, external README links, manifests, env examples, symlinks, generated build output, and a synthetic >10 MiB media file generated at test runtime.
- Create `plugins/awesome-llm-apps-controller/tests/test_catalog.py` — catalog discovery/classification/external-reference tests.
- Create `plugins/awesome-llm-apps-controller/tests/test_mirror.py` — mirror inclusion/exclusion/symlink tests.
- Create `plugins/awesome-llm-apps-controller/tests/test_skills_projection.py` — registry/projection/collision/risk tests.
- Create `plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh` — end-to-end fake-upstream synchronization test.

### Generated schema/catalog/provenance

- Create `registry/awesome-llm-apps/catalog.schema.json` — versioned schema for catalog entries.
- Generated by sync: `registry/awesome-llm-apps/catalog.json`.
- Generated by sync: `registry/awesome-llm-apps/catalog.summary.json`.
- Generated by sync: `.agents/skills/.awesome-llm-apps-managed.json`.
- Generated by sync: `vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-mirror.json`.
- Generated by sync: `vendor/shubhamsaboo-awesome-llm-apps/.whitechronos-excluded.json`.
- Create/update `plugins/awesome-llm-apps-controller/upstream.lock.json` — pinned provenance and generated counts.

### Controller / Codex integration

- Create `plugins/awesome-llm-apps-controller/.codex-plugin/plugin.json` — WhiteChronos local controller plugin.
- Create `plugins/awesome-llm-apps-controller/README.md` — runtime/mirror/update policy.
- Create `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/SKILL.md` — router and activation contract.
- Create `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/agents/openai.yaml` — ChatGPT metadata.
- Create controller references under `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/references/` for provenance, routing, activation classes, and catalog navigation.
- Modify `.agents/plugins/marketplace.json` — register `awesome-llm-apps-controller`.
- Modify `.codex/config.toml` — enable the controller.
- Modify `AGENTS.md` — add routing, risk, mirror, external-reference, and activation rules.

### Synchronization and release

- Create `.github/workflows/sync-awesome-llm-apps.yml` — scheduled/manual/push-triggered sync branch + best-effort PR creation.
- Produce, but do not commit, `/mnt/data/awesome-llm-apps-controller-dist/skill.zip`.

---

### Task 1: Define the Catalog Schema and Stable Entry Model

**Files:**
- Create: `registry/awesome-llm-apps/catalog.schema.json`
- Create: `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_catalog.py`
- Create: `plugins/awesome-llm-apps-controller/tests/test_catalog.py`
- Create: `plugins/awesome-llm-apps-controller/tests/fixtures/upstream/README.md`
- Create: `plugins/awesome-llm-apps-controller/tests/fixtures/upstream/agent_skills/registry.json`

**Interfaces:**
- Produces: `normalize_id(source_type: str, key: str) -> str`
- Produces: `classify_execution(entry: dict) -> dict`
- Produces: `scan_internal_entries(root: pathlib.Path, commit: str) -> list[dict]`
- Produces: `extract_external_references(readme_text: str, commit: str) -> list[dict]`
- Produces: catalog entry objects validated by `registry/awesome-llm-apps/catalog.schema.json`
- Consumes: only Python standard library and an already-cloned upstream tree.

- [ ] **Step 1: Write failing catalog-model tests**

Add tests that assert:

```python
def test_normalize_id_is_stable_and_source_scoped():
    assert normalize_id("upstream_internal", "rag_tutorials/vision_rag") == (
        "upstream-internal:rag-tutorials-vision-rag"
    )
    assert normalize_id("external_reference", "https://example.com/agent") != (
        "upstream-internal:rag-tutorials-vision-rag"
    )

def test_execution_flags_classify_background_credentials_and_high_stakes():
    entry = {
        "title": "Insurance Claim Live Agent Team",
        "upstream_path": "voice_ai_agents/insurance_claim_live_agent_team",
        "manifest_paths": [".env.example"],
        "mcp_related_paths": [],
    }
    risk = classify_execution(entry)
    assert risk["credentials_required"] is True
    assert risk["high_stakes_domain"] is True
```

Also assert the schema requires `id`, `source_type`, `category`, `execution_class`, and `upstream_commit`.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_catalog.py -k "normalize_id or execution_flags"
```

Expected: FAIL because the module/schema do not exist.

- [ ] **Step 3: Implement the catalog model and schema**

Implement:

```python
def normalize_id(source_type: str, key: str) -> str: ...
def classify_execution(entry: dict) -> dict: ...
```

Use deterministic lower-case IDs; for external URLs, append a 12-hex SHA-256 suffix so two identical titles cannot collide.

Define schema version `1` and the exact spec-required entry fields, including `external_url`, `license_status`, execution booleans, and `execution_class`.

- [ ] **Step 4: Run the focused tests and confirm GREEN**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add registry/awesome-llm-apps/catalog.schema.json   plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_catalog.py   plugins/awesome-llm-apps-controller/tests/test_catalog.py   plugins/awesome-llm-apps-controller/tests/fixtures/upstream
git commit -m "feat: define Awesome LLM Apps catalog model"
```

---

### Task 2: Discover Internal Apps, Components, and External Agent References

**Files:**
- Modify: `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_catalog.py`
- Modify: `plugins/awesome-llm-apps-controller/tests/test_catalog.py`
- Expand: `plugins/awesome-llm-apps-controller/tests/fixtures/upstream/`

**Interfaces:**
- Consumes: Task 1 catalog model.
- Produces: `build_catalog(root: pathlib.Path, commit: str) -> dict`
- Produces: `build_summary(catalog: dict) -> dict`
- Produces: nearest-qualifying-ancestor attachment for manifests/configs/internal Skills.
- Produces: `external_reference` records only for recognized upstream README app/agent list items.

- [ ] **Step 1: Write failing discovery tests**

Cover:

- nested app README/manifests attach to the nearest qualifying directory;
- canonical registry Skills appear as `canonical_skill`;
- a non-registry `SKILL.md` inside an example appears as `project_internal_skill`;
- a bullet external app link under an agent/app heading becomes `external_reference`;
- sponsor, translation, badge, social, and generic docs URLs are ignored;
- catalog output order is deterministic;
- summary counts by `category` and `source_type` match the catalog.

- [ ] **Step 2: Run discovery tests and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_catalog.py -k "discover or external or nearest or deterministic or summary"
```

Expected: FAIL on missing discovery behavior.

- [ ] **Step 3: Implement discovery**

Implement:

```python
def build_catalog(root: pathlib.Path, commit: str) -> dict: ...
def build_summary(catalog: dict) -> dict: ...
```

Rules:

- scan only spec-approved roots plus relevant `docs/`;
- use nearest qualifying directory ownership for attached components;
- parse Markdown list links using stdlib regex/state, with heading-aware external-reference filtering;
- never follow or fetch external URLs;
- attach `source_type="external_reference"`, `license_status="UNVERIFIED"`, and `execution_class="REFERENCE_ONLY"` to outbound entries.

- [ ] **Step 4: Run full catalog tests**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_catalog.py
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_catalog.py   plugins/awesome-llm-apps-controller/tests/test_catalog.py   plugins/awesome-llm-apps-controller/tests/fixtures/upstream
git commit -m "feat: discover Awesome LLM Apps agents and components"
```

---

### Task 3: Build the Functional Mirror Inclusion/Exclusion Engine

**Files:**
- Create: `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_mirror.py`
- Create: `plugins/awesome-llm-apps-controller/tests/test_mirror.py`
- Expand: `plugins/awesome-llm-apps-controller/tests/fixtures/upstream/`

**Interfaces:**
- Consumes: a cloned upstream root and commit SHA.
- Produces: `plan_mirror(root: pathlib.Path) -> list[dict]`
- Produces: `copy_mirror(root: pathlib.Path, dest: pathlib.Path, plan: list[dict]) -> dict`
- Produces: exclusion records `{path, git_sha, size, reason, upstream_commit}`.

- [ ] **Step 1: Write failing mirror-policy tests**

Assert:

- normal source/manifests/README/Skills are included;
- `.git/**`, `node_modules/**`, `.venv/**`, `venv/**`, `__pycache__/**`, `.pytest_cache/**`, `.next/**`, `dist/**`, and `build/**` are excluded with deterministic reasons;
- a synthetic 10 MiB + 1 byte media file with extension `.gif` is excluded as `large_demo_media`;
- a small image remains included;
- a symlink that resolves inside the upstream clone is reproduced as a symlink;
- a symlink that resolves outside the upstream clone is rejected and recorded as `unsafe_symlink` rather than followed.

- [ ] **Step 2: Run mirror tests and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_mirror.py
```

Expected: FAIL because the mirror module does not exist.

- [ ] **Step 3: Implement mirror planning and copying**

Implement:

```python
def plan_mirror(root: pathlib.Path) -> list[dict]: ...
def copy_mirror(root: pathlib.Path, dest: pathlib.Path, plan: list[dict]) -> dict: ...
```

Use `os.lstat`/path containment checks; never dereference an escaping symlink. Do not run files from upstream.

- [ ] **Step 4: Run mirror tests and confirm GREEN**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_mirror.py   plugins/awesome-llm-apps-controller/tests/test_mirror.py   plugins/awesome-llm-apps-controller/tests/fixtures/upstream
git commit -m "feat: add safe Awesome LLM Apps mirror policy"
```

---

### Task 4: Project Canonical Skills with Ownership and Risk Metadata

**Files:**
- Create: `plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_skills.py`
- Create: `plugins/awesome-llm-apps-controller/tests/test_skills_projection.py`

**Interfaces:**
- Consumes: upstream `agent_skills/registry.json`, upstream root, current Awesome ownership manifest, optional Matt ownership manifest.
- Produces: `load_canonical_skills(root: pathlib.Path) -> list[dict]`
- Produces: `risk_for_skill(name: str) -> dict`
- Produces: `project_skills(root: pathlib.Path, dest: pathlib.Path, previous_manifest: dict | None, matt_manifest: dict | None) -> dict`
- Produces: `.agents/skills/.awesome-llm-apps-managed.json`.

- [ ] **Step 1: Write failing projection tests**

Cover:

- valid registry entry + matching `SKILL.md` projects byte-for-byte;
- registry entry without `SKILL.md` is reported under `inconsistencies` and not installed;
- non-registry project-internal Skill is not projected;
- existing unmanaged destination fails with a clear collision error;
- destination listed in Matt manifest fails with a controller-specific collision error;
- previously Awesome-managed Skill may be replaced or removed;
- risk metadata for all seven canonical names matches the spec.

- [ ] **Step 2: Run projection tests and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_skills_projection.py
```

Expected: FAIL because projection code does not exist.

- [ ] **Step 3: Implement canonical registry validation and projection**

Implement the interfaces above. Use staging directories and atomic rename for each Skill so a failed copy cannot leave a partial Skill.

The manifest must store, per Skill:

```json
{
  "name": "project-graveyard",
  "upstream_path": "agent_skills/project-graveyard",
  "execution_class": "LOCAL_READ_ONLY",
  "network_required": false,
  "credentials_required": false,
  "broad_filesystem_access": true,
  "explicit_user_request_required": true
}
```

- [ ] **Step 4: Run projection tests and confirm GREEN**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/awesome-llm-apps-controller/scripts/awesome_llm_apps_skills.py   plugins/awesome-llm-apps-controller/tests/test_skills_projection.py
git commit -m "feat: project canonical Awesome LLM Apps skills safely"
```

---

### Task 5: Add the Catalog CLI and End-to-End Synchronizer

**Files:**
- Create: `plugins/awesome-llm-apps-controller/scripts/build_catalog.py`
- Create: `plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh`
- Create: `plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh`
- Create: `plugins/awesome-llm-apps-controller/upstream.lock.json`

**Interfaces:**
- Consumes: Tasks 1–4 modules and a Git clone URL/ref.
- Produces: mirror, excluded ledger, catalog, summary, Skill projection manifest, updated lock.
- CLI: `python build_catalog.py --root <upstream> --commit <sha> --catalog <path> --summary <path> --schema <path>`.
- Sync env: `AWESOME_LLM_APPS_UPSTREAM_URL` default `https://github.com/Shubhamsaboo/awesome-llm-apps.git`.
- Sync env: `AWESOME_LLM_APPS_UPSTREAM_REF` default `main`.

- [ ] **Step 1: Write failing end-to-end sync test**

The fake upstream must include:

- root Apache-2.0 `LICENSE`;
- canonical registry + valid/invalid entries;
- one internal app Skill;
- an external README agent link;
- an escaping symlink;
- generated build content;
- normal source;
- a large media fixture created during test setup.

Assert after sync:

- unrelated repository files remain untouched;
- nested upstream `.git` is absent;
- mirror/exclusion ledgers exist;
- catalog and summary validate;
- canonical Skills project safely;
- lock records source/ref/commit/license/counts/schema version/exclusion policy version;
- a second upstream commit removes stale mirrored source and updates provenance;
- no upstream executable is run (fixture contains a marker script that would create a sentinel if executed; sentinel must remain absent).

- [ ] **Step 2: Run sync test and confirm RED**

```bash
bash plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh
```

Expected: FAIL because the CLI/synchronizer do not exist.

- [ ] **Step 3: Implement `build_catalog.py`**

Implement `main(argv: list[str] | None = None) -> int`; validate generated output against the repository schema using a small in-repo validator that checks the supported schema subset, so synchronization adds no third-party dependency.

- [ ] **Step 4: Implement `sync_mirror.sh`**

The script must:

1. `git clone --depth 1 --branch "$REF"` when `REF` is a branch/tag, with fallback to shallow clone + detached checkout for a commit SHA;
2. verify root `LICENSE` contains `Apache License` and `Version 2.0`;
3. get `UPSTREAM_SHA` from Git;
4. call the Python mirror/catalog/Skill modules only;
5. write all generated outputs in temporary staging paths;
6. replace generated destinations only after every stage succeeds;
7. never invoke an upstream package manager, script, Makefile, Dockerfile, test, hook, or executable.

- [ ] **Step 5: Run end-to-end test and module tests**

```bash
bash plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh
pytest -q plugins/awesome-llm-apps-controller/tests/test_catalog.py   plugins/awesome-llm-apps-controller/tests/test_mirror.py   plugins/awesome-llm-apps-controller/tests/test_skills_projection.py
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add plugins/awesome-llm-apps-controller/scripts/build_catalog.py   plugins/awesome-llm-apps-controller/scripts/sync_mirror.sh   plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh   plugins/awesome-llm-apps-controller/upstream.lock.json
git commit -m "feat: synchronize Awesome LLM Apps source and catalog"
```

---

### Task 6: Build the Awesome LLM Apps Controller Skill and Plugin

**Files:**
- Create: `plugins/awesome-llm-apps-controller/.codex-plugin/plugin.json`
- Create: `plugins/awesome-llm-apps-controller/README.md`
- Create via Skill Creator initializer: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/`
- Create: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/references/upstream.md`
- Create: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/references/routing.md`
- Create: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/references/activation-classes.md`
- Create: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/references/catalog-navigation.md`
- Create: `plugins/awesome-llm-apps-controller/tests/test_controller_contract.py`

**Interfaces:**
- Consumes: generated `registry/awesome-llm-apps/catalog.json` and ownership/risk manifest when present.
- Produces: local Codex plugin `awesome-llm-apps-controller`.
- Produces: ChatGPT-compatible Skill directory with compact control-plane instructions only.

- [ ] **Step 1: Initialize the Skill directory with Skill Creator**

Run the current Skill Creator `init_skill.py` for `awesome-llm-apps-controller` into the plugin's `skills/` directory, then remove unused generated example assets/scripts.

Expected: valid baseline Skill structure exists before custom content is written.

- [ ] **Step 2: Write failing controller contract tests**

Tests must assert that controller text:

- routes concrete RAG/MCP/voice/always-on/Generative-UI/example requests to catalog discovery;
- preserves Superpowers -> ECC -> Matt -> Awesome precedence;
- forbids auto-running credentialled, background, self-modifying, or external-reference entries;
- forbids claiming sample apps are native subagents;
- requires explicit request before `project-graveyard` scanning and external advisor/worker dispatch;
- references the catalog and provenance lock.

- [ ] **Step 3: Run controller tests and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_controller_contract.py
```

Expected: FAIL until controller files are authored.

- [ ] **Step 4: Implement plugin and controller**

Use frontmatter containing only `name` and `description`. Keep `SKILL.md` under 500 lines; move catalog/risk detail into the four reference files.

Plugin capabilities: `["Interactive", "Read"]`; no hooks and no MCP servers.

- [ ] **Step 5: Validate controller Skill**

Run Skill Creator's `quick_validate.py` against the controller Skill directory.

Expected: validation succeeds.

- [ ] **Step 6: Run controller tests and confirm GREEN**

Run the command from Step 3.

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add plugins/awesome-llm-apps-controller/.codex-plugin/plugin.json   plugins/awesome-llm-apps-controller/README.md   plugins/awesome-llm-apps-controller/skills   plugins/awesome-llm-apps-controller/tests/test_controller_contract.py
git commit -m "feat: add Awesome LLM Apps controller"
```

---

### Task 7: Register the Controller in Codex and Repository Governance

**Files:**
- Modify: `.agents/plugins/marketplace.json`
- Modify: `.codex/config.toml`
- Modify: `AGENTS.md`
- Create: `plugins/awesome-llm-apps-controller/tests/test_codex_integration.py`

**Interfaces:**
- Consumes: Task 6 plugin name `awesome-llm-apps-controller`.
- Produces: marketplace entry `awesome-llm-apps-controller@whitechronos-repo`.
- Produces: repository-level routing/safety instructions.

- [ ] **Step 1: Write failing Codex integration tests**

Assert:

```python
def test_marketplace_registers_controller(): ...
def test_codex_config_enables_controller_and_preserves_existing_plugins(): ...
def test_agents_md_defines_awesome_layer_after_matt_and_before_github_arena(): ...
def test_agents_md_forbids_auto_execution_of_gated_classes(): ...
```

Parse marketplace JSON and TOML rather than string-matching those files.

- [ ] **Step 2: Run integration tests and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
```

Expected: FAIL because registration does not exist.

- [ ] **Step 3: Register the local plugin**

Add a local marketplace entry with `products: ["CODEX"]` and `INSTALLED_BY_DEFAULT`.

Append:

```toml
[plugins."awesome-llm-apps-controller@whitechronos-repo"]
enabled = true
```

Do not change `[features] multi_agent = true` or existing plugin settings.

- [ ] **Step 4: Add the Awesome LLM Apps governance section to `AGENTS.md`**

State:

- routing precedence;
- mirror/catalog ownership;
- external-reference audit requirement;
- canonical Skill execution gates;
- no automatic dependency/MCP/credential/background/self-modifying execution;
- no false claims of native subagents;
- GitHub Arena final review.

- [ ] **Step 5: Run integration tests and repository parsers**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
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
git add .agents/plugins/marketplace.json .codex/config.toml AGENTS.md   plugins/awesome-llm-apps-controller/tests/test_codex_integration.py
git commit -m "feat: enable Awesome LLM Apps controller in Codex"
```

---

### Task 8: Add the Upstream Synchronization Workflow

**Files:**
- Create: `.github/workflows/sync-awesome-llm-apps.yml`
- Create: `plugins/awesome-llm-apps-controller/tests/test_sync_workflow.py`

**Interfaces:**
- Consumes: Task 5 `sync_mirror.sh`.
- Produces: manual + daily + relevant-push synchronization.
- Produces: branch `chore/sync-awesome-llm-apps-<12-char-sha>`.
- Produces: best-effort PR creation with policy-blocked fallback.

- [ ] **Step 1: Write failing workflow tests**

Parse YAML and assert:

- `workflow_dispatch` exists;
- daily `schedule` exists;
- push paths include the workflow and controller;
- permissions are `contents: write` and `pull-requests: write`;
- sync tests run before real upstream synchronization;
- only generated mirror/catalog/manifest/lock paths are staged;
- PR-creation failure after a successful branch push emits a warning and does not fail the job.

- [ ] **Step 2: Run workflow test and confirm RED**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_sync_workflow.py
```

Expected: FAIL because workflow does not exist.

- [ ] **Step 3: Implement workflow**

Follow the proven ECC/Matt pattern. The workflow must not execute upstream tests or installers.

When changes exist, stage only:

```text
vendor/shubhamsaboo-awesome-llm-apps/
registry/awesome-llm-apps/
.agents/skills/.awesome-llm-apps-managed.json
.agents/skills/<Awesome-managed skill directories>
plugins/awesome-llm-apps-controller/upstream.lock.json
```

Use the generated ownership manifest to derive Awesome-managed Skill paths; do not `git add .agents/skills` wholesale.

- [ ] **Step 4: Run workflow and sync tests**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests/test_sync_workflow.py
bash plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/sync-awesome-llm-apps.yml   plugins/awesome-llm-apps-controller/tests/test_sync_workflow.py
git commit -m "ci: sync Awesome LLM Apps through review branches"
```

---

### Task 9: Verify the Approved Upstream Snapshot and Drift Behavior

**Files:**
- Modify tests only if the audited snapshot exposes a fixture-independent edge case.
- Generated in a temporary verification workspace; do not commit mirror/catalog output yet.

**Interfaces:**
- Consumes: approved commit `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`.
- Produces: verification ledger for the spec's audited counts.
- Produces: current-main drift assessment before first live synchronization.

- [ ] **Step 1: Run the ingestion pipeline against the approved commit**

Use `AWESOME_LLM_APPS_UPSTREAM_REF=4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2` in an isolated temporary repository root.

Expected audited counts:

```text
tree_entries=2531
blobs=1976
skill_md=10
canonical_skills=7
readmes=223
dependency_manifests=194
env_examples=65
dockerfiles=8
mcp_related=139
code_files=996
```

- [ ] **Step 2: Verify catalog/schema/provenance against the real snapshot**

Assert:

- 7 canonical Skill records;
- project-internal Skills are not in global projection;
- root license is Apache-2.0;
- both known >10 MiB media blobs are excluded and traceable;
- external-reference records have `UNVERIFIED` license status and are not mirrored recursively.

- [ ] **Step 3: Compare current upstream `main` with the approved commit**

If current `main` differs, run catalog generation for both revisions and report changes in:

- root license;
- canonical Skill registry;
- top-level required roots;
- catalog counts;
- new executable/runtime classes.

If license disappears/changes incompatibly, registry becomes invalid, or required roots are removed, stop for human review before live sync. Ordinary additions/removals proceed through the sync PR.

- [ ] **Step 4: Run the complete local test suite for this integration**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests
bash plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh
```

Expected: PASS.

- [ ] **Step 5: Commit only test hardening discovered from the real snapshot**

If no code/test change was needed, do not make an empty commit. If a real snapshot exposed a missing deterministic case, add the minimal regression test/fix and commit:

```bash
git commit -m "test: harden Awesome LLM Apps snapshot ingestion"
```

---

### Task 10: Package the ChatGPT Controller Skill

**Files:**
- Source: `plugins/awesome-llm-apps-controller/skills/awesome-llm-apps-controller/`
- Output artifact only: `/mnt/data/awesome-llm-apps-controller-dist/skill.zip`

**Interfaces:**
- Consumes: validated Task 6 Skill directory.
- Produces: exact filename `skill.zip`, <= 25 MiB.
- Produces: SHA-256 digest recorded in release verification notes.

- [ ] **Step 1: Package with Skill Creator**

Run the current `package_skill.py` against the controller Skill directory with output directory `/mnt/data/awesome-llm-apps-controller-dist`.

Expected: validator passes and creates exactly `skill.zip`.

- [ ] **Step 2: Verify package contents and size**

Assert:

- ZIP contains `awesome-llm-apps-controller/SKILL.md`;
- ZIP contains `agents/openai.yaml` and the four references;
- ZIP does not contain `vendor/`, generated catalog bulk data, credentials, or executable upstream examples;
- ZIP size < 25 MiB.

- [ ] **Step 3: Hash artifact**

```bash
sha256sum /mnt/data/awesome-llm-apps-controller-dist/skill.zip
```

Record the digest in the final implementation report, not in source unless repository policy requires it.

---

### Task 11: Open and Merge the Infrastructure PR

**Files:**
- All non-generated implementation files from Tasks 1–8 plus the approved spec and this plan.

**Interfaces:**
- Produces: reviewed infrastructure PR into `main`.
- Does not yet commit the live upstream mirror/catalog/projected Skills.

- [ ] **Step 1: Run pre-PR verification**

```bash
pytest -q plugins/awesome-llm-apps-controller/tests
bash plugins/awesome-llm-apps-controller/tests/test_sync_mirror.sh
python pipeline/engineering_compatibility_gate.py
python pipeline/protocol_zero_gate.py datasheet/projects/example-project.json
pytest -q tests/test_engineering_compatibility_gate.py
pytest -q tests/test_protocol_zero_gate.py
```

Expected: all commands PASS.

- [ ] **Step 2: Run GitHub Arena review on the actual branch diff**

Use the repository's Arena layer. Resolve every material correctness, security, provenance, collision, or maintainability finding before PR creation.

- [ ] **Step 3: Open the infrastructure PR**

PR body must state:

- approved upstream snapshot;
- no upstream code executed during sync;
- seven canonical Skills are projected only after the workflow runs;
- all other agent/apps/components are catalogued and controlled;
- external references are not cloned;
- package artifact generated separately;
- workflow will create/push a second synchronization branch after merge.

- [ ] **Step 4: Wait for all applicable repository checks**

Do not merge while any required check is queued/in-progress/failed.

- [ ] **Step 5: Squash merge using expected head SHA**

After merge, verify `main` contains controller registration, workflow, tests, schema, spec, and plan.

---

### Task 12: Review and Merge the Initial Synchronization PR

**Files:**
- Generated by workflow after Task 11 merge:
  - `vendor/shubhamsaboo-awesome-llm-apps/**`
  - `registry/awesome-llm-apps/catalog.json`
  - `registry/awesome-llm-apps/catalog.summary.json`
  - `.agents/skills/.awesome-llm-apps-managed.json`
  - seven Awesome-managed canonical Skill directories
  - `plugins/awesome-llm-apps-controller/upstream.lock.json`

**Interfaces:**
- Produces: reviewed live catalog/mirror/Skill projection on `main`.
- Consumes: synchronization branch generated from current upstream after Task 11.

- [ ] **Step 1: Inspect sync workflow result**

Confirm:

- workflow tests passed before live sync;
- branch was pushed;
- if Actions PR creation was blocked, open the PR through the GitHub connector;
- generated commit's parent is current `main`.

- [ ] **Step 2: Verify generated provenance and ownership**

Assert:

- mirror and lock point to the same upstream commit;
- root Apache-2.0 license is preserved;
- excluded ledger accounts for every omitted upstream path;
- ownership manifest lists exactly the projected canonical Skills;
- no Matt-managed Skill was changed;
- external refs are catalog-only;
- project-internal Skills remain within mirrored examples only.

- [ ] **Step 3: Verify catalog completeness against the sync commit**

Run the generated summary/count checks and schema validation. For the approved snapshot, exact invariant counts must match Task 9. For a newer reviewed upstream commit, counts may differ but every delta must be explained by the drift report.

- [ ] **Step 4: Wait for all applicable CI/governance checks**

Do not merge while checks are incomplete or failed.

- [ ] **Step 5: Squash merge with expected head SHA**

Verify the merge result and resulting `main` SHA.

---

### Task 13: Post-Merge End-to-End Verification

**Files:**
- Read-only verification of `main`; no source changes unless a verified defect requires a new bugfix branch.

**Interfaces:**
- Produces: final verification ledger and user-facing completion report.

- [ ] **Step 1: Verify Codex configuration from `main`**

Confirm:

- `multi_agent = true`;
- Superpowers, Superpowers Controller, ECC, ECC Controller, Matt Pocock Controller, Awesome LLM Apps Controller, and GitHub Arena remain enabled;
- marketplace JSON parses and points Awesome controller to the local plugin.

- [ ] **Step 2: Verify live generated state**

Confirm:

- catalog + summary present;
- functional mirror metadata + exclusion ledger present;
- seven canonical projected Skills present and ownership-tracked;
- upstream lock matches generated provenance;
- no generated path escaped its intended namespace.

- [ ] **Step 3: Verify controller package**

Confirm `/mnt/data/awesome-llm-apps-controller-dist/skill.zip` still exists, is valid, and report its SHA-256.

- [ ] **Step 4: Verify automatic update loop**

Observe the post-merge `sync-awesome-llm-apps.yml` run. It must either:

- report no changes and succeed; or
- push a new review branch and succeed, with PR best-effort behavior.

- [ ] **Step 5: Run final Superpowers verification and branch-finishing workflow**

Use `verification-before-completion`, then `finishing-a-development-branch`. Report only claims supported by fresh post-merge evidence.

- [ ] **Step 6: Final user report**

Include:

- infrastructure and sync PR URLs;
- final `main` merge SHA;
- upstream commit integrated;
- canonical Skill count/names;
- catalog entry counts by category/source type;
- mirror included/excluded file counts and bytes;
- controller package link + SHA-256;
- any upstream inconsistencies or intentionally gated components.

