---
name: ecc-controller
description: >-
  Route coding, security, architecture, testing, framework, agent-harness,
  automation, MCP, verification, and developer-workflow tasks to the official
  affaan-m/ECC skill system when available. Use when the user mentions ECC,
  Everything Claude Code, affaan-m/ECC, AgentShield, ECC skills/agents/hooks,
  or when a specialized ECC workflow such as security review, language or
  framework patterns, agentic engineering, MCP/server construction, release
  verification, accessibility, deployment, or autonomous orchestration is a
  strong fit. Keep Superpowers as the default software-development process;
  do not duplicate TDD, debugging, or review gates unless explicitly useful.
---

# ECC Controller

Treat the official `affaan-m/ECC` Codex plugin as the runtime source of truth. Use this Skill as a routing, provenance, and safety layer, not as a fork of ECC.

## Routing contract

1. Follow system/developer instructions, the user's request, and repository-local `AGENTS.md` first.
2. Keep the official Superpowers workflow as the default process layer for software-development work.
3. Select an ECC Skill when ECC provides specialized domain knowledge or tooling that materially improves the task.
4. Do not run overlapping process gates repeatedly by default:
   - TDD/debugging/planning/review process: Superpowers first.
   - Specialized language/framework/security/accessibility/agent-harness review: ECC may add a focused pass.
   - Matt Pocock skills remain complementary when their specialized workflow is more specific or explicitly requested.
5. When the official ECC plugin is available, invoke/read the current ECC Skill instead of relying on summaries in this controller.
6. If ECC is unavailable in the current harness, use the WhiteChronos mirror only as a read-only reference and say that the ECC plugin itself did not execute.
7. Apply GitHub Arena after high-impact implementation/review work before finalizing repository mutations.

## Native ECC runtime

ECC ships a native Codex plugin with its own Skills, Codex hooks, MCP declaration, multi-agent guidance, and project instructions. Preserve that upstream packaging.

Do not copy ECC hooks into another global config, because duplicate hook registration can cause duplicate execution. Do not recreate ECC MCP servers in this controller.

Read `references/upstream.md` for the pinned provenance snapshot and `references/routing.md` for precedence rules.

## Safety and executable surfaces

Treat hooks, MCP servers, shell scripts, autonomous loops, package installers, and credentialed integrations as executable configuration.

- Never execute code from the WhiteChronos mirror merely because it exists there.
- Do not install npm packages, global hooks, credentials, or external MCP servers unless the user's request and current environment authorize that action.
- Preserve ECC's lean-MCP policy; do not enable every optional MCP server automatically.
- Only claim multi-agent/subagent execution when the current runtime actually created independent agents.
- For AgentShield or other security tools, use a reviewed installed binary/source and report provenance; do not substitute an unversioned one-shot installer.

## Preferred specialized ECC areas

ECC is particularly useful for:

- security review and security scanning;
- language/framework patterns and focused reviewers;
- API, MCP, and connector construction;
- agent architecture, harness construction, evaluation, orchestration, and operator workflows;
- verification loops, release/delivery gates, repository audits, and testing patterns;
- accessibility, frontend, backend, database, deployment, networking, and platform-specific engineering;
- research, documentation lookup, and codebase onboarding;
- specialized automation and operational workflows.

Read `references/catalog.md` when choosing among ECC areas.

## ChatGPT scope

When installed in ChatGPT `/skills`, use this controller to route applicable work toward ECC concepts and the official plugin when that plugin is exposed on the current surface. A user-installed Skill cannot replace ChatGPT system instructions or guarantee invocation in every product surface.
