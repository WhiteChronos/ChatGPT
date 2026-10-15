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

## STOP
No merge, deploy, API calls, credential provisioning, Codex runtime configuration, automatic skill installation, or PRODUCTION_COMPLETE in this proposal.
