---
name: awesome-llm-apps-controller
description: >-
  Route AI-agent, RAG, MCP, voice, always-on, Generative UI, agent-framework,
  and reusable LLM-app requests through the WhiteChronos Awesome LLM Apps
  catalog while preserving execution-risk, provenance, and upstream scope.
---

# Awesome LLM Apps Controller

Use this Skill when the user asks for a concrete AI-agent/application example, RAG pattern, MCP agent, voice agent, always-on agent, Generative UI, memory app, framework example, or one of the canonical upstream Agent Skills from `Shubhamsaboo/awesome-llm-apps`.

## Routing order

Preserve the repository stack:

1. Superpowers owns the software-development process.
2. ECC adds specialist engineering/security/runtime capability when relevant.
3. Matt Pocock adds specialized engineering/productivity skills when relevant.
4. Awesome LLM Apps contributes concrete examples, agent architectures, canonical upstream Skills, and reusable components.
5. GitHub provides source evidence/mutations.
6. GitHub Arena performs the high-impact final review.

Do not rerun overlapping TDD/debug/review workflows across layers by default.

## Catalog first

Search or inspect `registry/awesome-llm-apps/catalog.json` and `catalog.summary.json`. Report the selected entry's `upstream_path`, `source_type`, `execution_class`, and upstream commit before executing or adapting it.

Major families include RAG, MCP, voice, always-on/background agents, Generative UI, multi-agent teams, advanced LLM apps, memory apps, and framework crash-course examples.

## Execution gates

Discovery is not authority to run code.

- `REFERENCE_ONLY`: use as design/source reference only.
- `LOCAL_READ_ONLY`: may inspect locally when the task requires it.
- `LOCAL_MUTATING`: requires task authority for the mutation.
- `NETWORKED`: network use must be relevant and allowed.
- `CREDENTIALLED`: never invent credentials or silently configure authenticated services.
- `MCP_OR_CONNECTOR`: never globally register MCP/connectors merely because an example contains them.
- `BACKGROUND_AUTONOMOUS`: never start schedules/watchers/daemons during ordinary chat without an explicit monitoring/automation request.
- `SELF_MODIFYING`: use only after explicit user selection, isolated workspace, and diff/review gate.
- `external_reference`: link only until a separate provenance/license/security audit of the external repository is performed.

High-stakes examples remain software examples; they do not bypass medical, financial, legal, mental-health, or other domain requirements.

## Canonical Skill gates

- `advisor-orchestrator-worker`: external-model/network/credential capable. Use only on an explicit user request for that orchestration architecture and only with authorized credentials.
- `project-graveyard`: broad local filesystem/repository inspection. Run only after an explicit user request to scan for projects.
- `dependency-doctor`: local/offline by default; optional network checks stay opt-in.
- `commit-archaeologist`, `scope-creep-detector`: repository-local read-only analysis.
- `first-reader`, `thinking-out-loud`: text/control-flow skills; they grant no unrelated filesystem/network authority.

Do not claim an upstream sample app is a native Codex subagent, native ChatGPT agent, connector, or background automation. Native subagent status requires actual native/broker execution evidence from the current runtime.

## Mirror policy

`vendor/shubhamsaboo-awesome-llm-apps/` is a synchronized read-only source mirror. Never edit it manually. Large/generated exclusions stay traceable in `.whitechronos-excluded.json`.

Project-internal `SKILL.md` files remain scoped to their containing example and are not globally projected.

Read the references for provenance, routing, activation classes, and catalog navigation.
