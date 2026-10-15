# Selective Integration Registry — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Register only four vetted external capability families with pinned provenance and default-deny activation, preserving separate provider runtimes, without altering the active Codex host or launching external code.

**Architecture:** Reuse `registry/integrations/schema.json`, `runtime.registry.load_registry`, and the existing project plugin/controllers. New descriptor records carry capability provenance; a separate checked-in selection policy binds activation safeguards and Issue #95. CI's normal root pytest suite validates the policy and pins without touching runtime services.

**Tech Stack:** Python 3.12, pytest, JSON descriptors and schema, GitHub Actions.

**Spec:** https://github.com/WhiteChronos/ChatGPT/issues/95

## Global Constraints

- GitHub-only authority; protected `main`; no direct edit, merge, deploy, live smoke or credential provisioning.
- Treat mirror trees `vendor/` as read-only and never execute mirrored code.
- The official Superpowers plugin remains the preferred process layer; only proven host tools count as loaded.
- External providers, JEV and SponsoredTokens remain independent. Do not share provider credentials or enable integrations by registry presence alone.
- Keep Arena 2.0 reference-only with license unverified; Arena and Broker stay unchanged.
- A descriptor at `REGISTERED_PROJECT` or `ACTIVATION_GATED` is NOT `ACTIVE_RUNTIME_VERIFIED`.
- Require review and a new exact-SHA approval for any later merge.

## Review Focus

1. Adding a selected entry must not implicitly expose an MCP server or process — checked in root registry test.
2. Changing an upstream provenance lock without reviewing its descriptor must fail tests — pin comparison.
3. Enabling provider cross-credential sharing must fail policy tests — exact security flags.
4. Unverified ARENA 2.0 must not be selected for execution — reference-only assertions.
5. JEV/SponsoredTokens must remain deferred and independently gated while Issue #94 remains open — deferred-service assertions.

---

### Task 1: Failing CI tests for curated integration contract

**Files:**
- Create: `tests/test_selective_integration_registry.py`
- Test: `tests/test_selective_integration_registry.py`

**Interfaces:** `runtime.registry.load_registry(root: Path)` and `registry/integrations/selection-policy.json`.

- [ ] Write expectations for precise selected IDs, plugin runtime separation, provenance lock matching, and default-deny status.
- [ ] Run `python -m pytest -q tests/test_selective_integration_registry.py` on the initial branch; expect RED due missing selection policy/descriptors.

### Task 2: Minimal curated descriptors and explicit policy

**Files:**
- Modify: `registry/integrations/index.json`
- Create: `registry/integrations/{superpowers-official,ecc-specialists,matt-pocock-stable,awesome-llm-apps-curated}.json`
- Create: `registry/integrations/selection-policy.json`
- Modify: `plugins/whitechronos-control-plane/tests/test_schema_registry.py`

**Interfaces:** standard descriptor schema v1, SHA pins from existing controller `upstream.lock.json` files; controller paths already in repository.

- [ ] Register only the four families, no other upstream applications or MCP tools.
- [ ] Store the selection policy with default activation DENY, service isolation, Issue #95 linkage and deferred high-risk services.
- [ ] Re-run root and Control Plane test suites; expect GREEN after implementation.
- [ ] Validate that the Runtime Doctor still accesses unchanged `github-arena` and `subagent-broker` probes.

### Task 3: Documentation, evidence and PR gate

**Files:**
- Create: `runbooks/selective-integrations.md`

- [ ] Explain role, trust boundary, allowed modes, pinned provenance, and verifiable status for each provider.
- [ ] Run `python -m pytest -q` in CI on the exact PR SHA. If not runnable or failing, report BLOCKED.
- [ ] Apply structured four-lens GitHub Arena review and preserve the PR as draft until independent review.
- [ ] Link PR status/evidence back to Issue #95; no merge/deploy or runtime completion claim.
