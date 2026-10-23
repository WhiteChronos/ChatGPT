# fast-jev-compaction — integration assessment

Source: https://github.com/tamaratran/fast-jev-compaction
Upstream package: fast-jev-compaction 0.2.0, MIT; default branch main.
Target: WhiteChronos/ChatGPT (GitHub-only), with pre-existing independent TypeSafe/Jev PR #91.

## Scope
This document connects the upstream source by an auditable reference, not by silently vendoring, installing or executing third-party code. The original plugin is for Claude Code function hooks; ChatGPT Web and Codex do not support that hook API by assumption.

## Candidate architecture
- Evaluate a separate opt-in Node.js adapter using the exported library `compact(messages, asker, options)` or `compactMessages`; validate input/output shape before touching transcripts.
- Implement a format translation from authorized WhiteChronos transcript events into the library's Message subset; preserve system/user constraints, precise errors, sources, recent messages, and tool call/result pairing.
- Retain original event history in authorized private storage; compacted context is derived, reversible, and cannot become a source of truth.
- On missing key, failed Jev response, wrong format, insufficient gain or timeout, use untouched history. Never silently drop safety-critical instructions.
- Keep TypeSafe/Jev credentials distinct from SponsoredTokens. No keys in GitHub, logs, artifacts, or repository configs.
- Control model cost: Jev input contains conversation material; obtain consent and data classification before remote transmission.

## Validation gates
1. Record exact upstream commit / package integrity, dependency licensing and supply-chain review.
2. Offline unit tests against synthetic transcripts: pairing, ordering, pinning, corrupted answers, budgets, failure fallback, prompt-injection payloads, and token/key redaction.
3. Benchmark at least three sizes of real-world *sanitized* session transcripts comparing wall-clock time, total tokens, answer correctness and constraint retention with/without compaction.
4. Confirm Codex host APIs actually allow the integration; otherwise restrict to a separate supported local application.
5. Require GitHub ruleset, CI at exact PR SHA, independent review and explicit SHA-specific merge authorization.
6. Separately authorize any paid live TypeSafe inference or local host installation. No live tests in CI.

## Current evidence / constraints
The upstream README describes a Claude Code plugin that removes or truncates older tool calls and tool results based on Jev responses; it leaves user and assistant text intact. This can reduce prompt length, but increased network calls and repeated state can also increase latency. It is not a drop-in latency fix for ChatGPT Web.


## REA-based reverse engineering (verified upstream)
- Authoritative REA project: https://github.com/morluto/rea (npm `rea-agents` 6.5.0, MIT as inspected 2026-10-15).
- REA supports static JavaScript / Electron inspection and exposes CLI / MCP tooling; it explicitly supports Codex setup. It is **not** itself a Jev compaction engine or a ChatGPT Web hook.
- REA setup requires Node.js ^22.19, ^24.11 or >=26. Setup previews configuration changes and requires approval; do not silently run its installer in CI or on a user's machine.
- Use REA against an authorized checkout of `fast-jev-compaction` to trace `src/compact.ts`, `src/state.ts`, `src/messages.ts`, `src/request.ts`, `src/client.ts` and `hooks/fast-jev.ts`. Verify actual files and commit SHAs before analysis.
- Map call/result identity and ordering, pinning, question batches, Jev answer validation, fallback, retry behavior and state budgets. Label each output as direct evidence, inference or unknown; retain exact file/line and upstream commit.
- Implement a **new** adapter for a separately controlled GPT application only after confirming its official, supported transcript/compaction API. Do not change ChatGPT Web's internal context handling or pretend its interface exposes plugin hooks.
- Compare the original library against the adapter on synthetic fixtures and malicious/malformed content; preserve initial/recent messages, user constraints, tool call/result pairs and untouched fallback.
- Record quality, latency and token usage on sanitized benchmarks. Reduced text length alone does not establish improved performance.
- Keep REA analysis local where possible. Do not transmit confidential data to TypeSafe/Jev without explicit data-sharing approval or provision secrets in any workflow.

### Proposed proof sequence
1. Pin exact REA and Jev source versions and check relevant licenses.
2. Run `rea setup --client codex --skill=false --dry-run` on an **authorized Codex host** to review proposed settings; do not call this runtime-verified based on GitHub files.
3. Run authorized static REA analysis in a controlled environment; store evidence paths, hashes, and limitations.
4. Implement adapter, add offline tests and independent review in a separate PR.
5. Run tests/CI at exact SHA, obtain human review, and request separate SHA-scoped merge authorization.
6. Validate the GPT host integration independently; default to no modifications and no paid inference.

## STOP
No merge, deploy, API calls, credential provisioning, Codex runtime configuration, automatic skill installation, or PRODUCTION_COMPLETE in this proposal.
