---
name: awesome-llm-apps-controller
description: >-
  Discover and route concrete agent, RAG, MCP, voice, always-on, Generative UI,
  memory, multi-agent, and LLM application patterns from the audited
  Shubhamsaboo/awesome-llm-apps catalog. Use when a task would benefit from an
  upstream example, architecture, tutorial, or canonical Skill. Preserve the
  repository routing order: Superpowers first, then ECC, Matt Pocock, Awesome
  LLM Apps, GitHub evidence/mutation, and GitHub Arena review. Treat discovery
  separately from execution and enforce catalog execution-risk gates before
  running, adapting, installing, or connecting anything.
---

# Awesome LLM Apps Controller

Use this Skill as a control plane for the WhiteChronos Awesome LLM Apps integration. Do not treat catalog discoverability as execution authorization.

## Sources of truth

1. Read `registry/awesome-llm-apps/catalog.json` for generated entries when it exists.
2. Read `plugins/awesome-llm-apps-controller/upstream.lock.json` for upstream commit, license, schema, mirror, and count provenance.
3. Read `.agents/skills/.awesome-llm-apps-managed.json` for projected canonical-Skill ownership and risk metadata when present.
4. Use `vendor/shubhamsaboo-awesome-llm-apps/` only as a read-only functional source mirror. Never edit the mirror manually.

See `references/catalog-navigation.md` for catalog lookup rules and `references/upstream.md` for provenance.

## Routing precedence

Preserve this order for software-development work:

`Superpowers -> ECC -> Matt Pocock -> Awesome LLM Apps -> GitHub -> GitHub Arena`

Use Awesome LLM Apps when it contributes a concrete upstream implementation, agent architecture, RAG tutorial, MCP example, voice/always-on pattern, Generative UI example, or canonical upstream Skill. Do not start overlapping TDD/debug/review workflows when a higher-priority layer already owns the process.

See `references/routing.md` for family and canonical-Skill routing.

## Discovery before activation

For a request involving RAG, MCP, voice AI, always-on agents, Generative UI, memory, multi-agent systems, or another LLM app/example:

1. Search the catalog for relevant entries and preserve the recorded upstream commit.
2. Distinguish `upstream_internal` from `external_reference` entries.
3. Inspect the entry's `execution_class` and risk booleans.
4. If source is needed, inspect the read-only mirror at the recorded path.
5. Only activate code after the current task and environment satisfy the matching execution gate.

Never claim that a sample application, advisor/worker example, or catalog entry is a native Codex subagent or native ChatGPT agent merely because it demonstrates agents. Do not claim a native Codex subagent ran without actual native lifecycle evidence.

## Execution gates

Do not auto-run `CREDENTIALLED`, `BACKGROUND_AUTONOMOUS`, `SELF_MODIFYING`, or `external_reference` entries. `MCP_OR_CONNECTOR` setup also requires the current task and an authorized connection/runtime.

Use the complete gates in `references/activation-classes.md` before running or adapting an entry. Never invent credentials, silently register MCP servers, start daemons, deploy cloud resources, or launch self-modifying systems.

## Canonical Skill special cases

- `project-graveyard`: broad filesystem/repository scanning requires an explicit user request.
- `advisor-orchestrator-worker`: external advisor/worker dispatch requires an explicit user request plus authorized credentials/runtime; do not use it to replace native Codex multi-agent or Superpowers subagent workflows automatically.
- `dependency-doctor`: local checks are read-only by default; upstream opt-in network checks remain opt-in.
- `commit-archaeologist` and `scope-creep-detector`: use for local repository inspection within task scope.
- `first-reader`: use for reader-experience review, not generic code review.
- `thinking-out-loud`: conversational control flow only; it grants no unrelated file, network, or execution authority.

## External references

An `external_reference` is only a link recorded from the upstream catalog. Never clone, install, execute, or treat it as licensed by the root Apache-2.0 repository without a fresh provenance, license, dependency, and security audit for that external project.
