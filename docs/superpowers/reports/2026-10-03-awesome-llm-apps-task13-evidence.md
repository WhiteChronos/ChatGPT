# Awesome LLM Apps Task 13 — Execution Evidence

**Date:** 2026-10-03  
**Repository:** `WhiteChronos/ChatGPT`  
**Task:** `docs/superpowers/plans/2026-10-03-subagent-broker.md` — Task 13  
**Status:** Native path complete; real Subagent-driven evidence still pending in a runtime that actually exposes native multi-agent or the merged Subagent Broker tools.

## Evidence classes

This report keeps the execution paths separate as required by Task 13.

### Native

Completed and merged:

- PR #50 — `feat: integrate Awesome LLM Apps system catalog and controller`
  - merge commit: `59ed3a165e39d00d216bbf8c519aa75646fbe815`
  - Native TDD evidence recorded in the PR: 20 Python tests passed, fake sync test passed, Skill validation passed.
  - approved upstream snapshot verification run: `37141740970`.
- PR #51 — `chore: sync Awesome LLM Apps 4bf51ab704fb`
  - merge commit: `8fefb87e812cdfa02a313c01b8948501d01c57cf`
  - live sync workflow run: `37141988700` — success.

Current generated state on `main` after PR #51:

- upstream commit: `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2`
- catalog entries: 434
- upstream-internal entries: 432
- external references: 2
- canonical projected Skills: 7
- project-internal Skills: 3
- included tracked upstream files: 1,957
- excluded tracked upstream files: 19
- included bytes: 39,430,805
- excluded bytes: 50,649,024

The seven canonical Skills are:

- `advisor-orchestrator-worker`
- `commit-archaeologist`
- `dependency-doctor`
- `first-reader`
- `project-graveyard`
- `scope-creep-detector`
- `thinking-out-loud`

The upstream `first-reader` registry license field remains recorded as the upstream inconsistency `license_metadata: empty_or_missing`.

### Native/Arena sequential review after merge

This ChatGPT harness still does not expose real `spawn_agent`, `subagent_spawn`, `subagent_wait`, or equivalent child-agent tools. GitHub Arena was therefore used only as sequential review perspectives, never described as independent agents.

Material findings from the post-merge review:

1. **Persistent schema deletion**
   - PR #51's generated sync had deleted `registry/awesome-llm-apps/catalog.schema.json`.
   - That schema is a source-controlled synchronization input, so a later scheduled sync would fail when trying to load it.
   - RED workflow run: `37150021741`.
   - Fix: restore the schema and stage/copy it into every generated registry replacement.
   - Regression: fake sync must preserve the schema after both first and second synchronization.

2. **Permissive default risk for future canonical Skills**
   - unknown future upstream canonical Skills defaulted to `LOCAL_READ_ONLY` with implicit-use permission.
   - That could grant a newly introduced Skill a more permissive execution assumption before WhiteChronos had reviewed its behavior.
   - RED workflow run: `37150156067` — 21 passed, 1 failed on the new fail-closed assertion.
   - Fix: unknown canonical Skills remain discoverable as `REFERENCE_ONLY` and require explicit user invocation until reviewed.
   - GREEN workflow run: `37150217806` — full Awesome controller test suite plus sync regression succeeded.

3. **Catalog schema contract was under-specified and shallowly validated**
   - The approved design requires the complete catalog execution/provenance model, but the persistent schema required only five entry fields and the in-repo validator checked only field presence.
   - RED workflow run `37151582362`: the complete-contract regression failed against the five-field schema.
   - RED workflow run `37151613086`: after expanding the schema, the new validator regression still failed because invalid boolean/enum values were accepted.
   - Fix: the schema now requires the full approved entry contract and declares types/enums; the dependency-free validator now enforces the supported JSON-Schema subset used by the repository.
   - GREEN workflow run `37151637373`: catalog schema tests plus repository governance gates succeeded.
   - The generated upstream snapshot, catalog counts, and commit `4bf51ab704fb2c5b3803cd5191b30d7dcdb51dc2` were not rewritten by this fix.

These findings belong to the Native/Arena review path, not to the Subagent-driven path.

### ChatGPT controller package

The controller package was rebuilt from the exact `main` Skill source using the current Skill Creator packaging workflow.

- artifact: `/mnt/data/awesome-llm-apps-controller-dist/skill.zip`
- size: 3,900 bytes
- SHA-256: `4f95e481be45571c5dcf7c42f9bd026e172472db626d4b5f68a5ddb487bb6036`
- validated contents: `SKILL.md`, `agents/openai.yaml`, and the four approved reference files only
- no vendor mirror, catalog bulk data, credentials, or executable upstream examples are packaged


### Native Codex multi-agent

**Not executed from this ChatGPT harness.**

The current tool list was inspected and no native Codex `spawn_agent` / wait / follow-up tools are exposed here.

No claim of native multi-agent execution is made.

### Subagent Broker `codex_cli`

**Not executed from this ChatGPT harness.**

The broker is merged and enabled in repository `.codex/config.toml`, but this already-running ChatGPT session has not reloaded the repository plugin/MCP toolset. Its current tool list does not expose `subagent_spawn` or related broker tools.

No connected remote device or authenticated local Codex CLI is available to this session, so no model-backed broker child is claimed.

## Remaining Task 13 gate

A fresh trusted Codex runtime must execute the real Subagent-driven pass before Task 13 is complete.

Minimum required evidence:

1. independent implementer or researcher where a bounded remaining/review task benefits;
2. independent task reviewer;
3. independent final whole-integration reviewer;
4. agent IDs and native/broker execution evidence proving the children actually ran;
5. any fix round attributed to the exact child path that produced it.

Preferred order:

```text
native Codex multi-agent, if exposed
    else
verified Subagent Broker codex_cli
```

The eventual final report must keep these labels distinct:

```text
Native
Native Codex multi-agent
Subagent Broker codex_cli
```

Do not convert this report's sequential Arena review into Subagent-driven evidence.
