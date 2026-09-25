# Codex / GitHub Workflow Research Notes

## Purpose
Short adoption notes from public repositories and current OpenAI documentation. These notes are reference-only and do not override repository Golden Rules.

## High-value patterns

### openai/codex (official)
- Codex CLI is an open-source local coding agent/harness.
- Durable repository instructions belong in `AGENTS.md`; project settings can live in `.codex/config.toml`.
- Choose the smallest integration surface: `codex exec` for bounded jobs, SDK for programmatic flows, app-server for persistent/product-embedded sessions.
- Keep context bounded and verification explicit.

### duduaguiaarr-source/miniguia-estudos-sistemas-operacionais
- Treat AI as support, not a substitute for source material.
- Curate a bounded source set before synthesis.
- Prompts improve when they specify audience/level, output structure, comparison target, source-only constraint and uncertainty handling.

### Agent workflow templates
- `crisxuan/agent-workflow-kit`: evaluate repository risk first; choose the smallest workflow that reduces actual risk.
- `dev-hara0004/codex-agent-workflow-template`: separate roles/work modes; use one source of truth and explicit requirement→design→test traceability.
- `hdtinh57/codex-orchestrated-project-template`: thin agents + reusable skills/rules/hooks instead of one oversized prompt.

## Applied to this repository
- Keep engineering authority in project evidence and applicable standards.
- Keep durable operating rules in AGENTS/governance/machine-readable policy.
- Keep reusable technical knowledge in Data Center/skills/reference catalogs.
- Keep user-facing XLSX compact; do not multiply tabs when one document-action matrix is clearer.
- Use CI regression tests to prevent presentation/model drift.
