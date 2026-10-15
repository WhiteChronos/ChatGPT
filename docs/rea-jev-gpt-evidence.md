# REA + Jev + GPT: evidence ledger and adapter contract

## Provenance, verified source inspection (15 October 2026)
- REA original: https://github.com/morluto/rea; reviewed README, package.json, AGENTS.md and installation guide through GitHub. Its source advertises `rea-agents` 6.5.0, MIT, static JS analysis and Codex MCP integration.
- Jev original: https://github.com/tamaratran/fast-jev-compaction; source inspected: `src/index.ts`, `src/compact.ts`, `src/types.ts` and README.
- OpenAI official Responses compaction item reference: https://platform.openai.com/docs/api-reference/responses; the documented `/v1/responses/compact` returns compaction items containing opaque encrypted content.

## Static source-derived observations (NOT a completed REA execution)
The Jev `src/compact.ts` source defines `keepThreshold=0.5`, `preserveRecentMessages=6`, `maxStateTokens=25000`, `maxRequestTokens=30000`, and `truncateHeadChars=300`. It scores tool-call and tool-result retention separately and keeps pinned items. User/assistant text is not a candidate for deletion in the returned transcript, per README.

REA's advertised static analysis is suitable for verifying the call graph and boundaries, but **REA MCP/CLI was not executed on the user's Windows/Codex host**. This document is a traceable manual static inspection and an REA investigation plan, not an invented tool transcript.

## REA proof still needed
1. Pin exact commits for both upstream repositories.
2. On an authorized host, run REA static JavaScript analysis against a local, authorized Jev checkout; record invocation, timestamps, content hashes, output snippets and limits.
3. Cross-check mapping from `collectToolCalls` -> `fitState` -> `batchCalls` -> `askBatch` -> `decideCall` -> `applyDecisions` against real symbol references.
4. Confirm adversarial fixtures and measure quality, tokens, latency, including network overhead.

## Minimal compatible GPT implementation
`tools/gpt_compaction_adapter.py` is an explicit Python HTTP transport for the official Responses compaction route. It validates the request and the existence of a compaction item in the response. The original input remains unchanged on failure. No Jev dependency, key, remote inference, or ChatGPT Web hook is installed. No secret is logged.

Offline regression tests use an injected fake transport. They prove only request shape, fail-closed behavior, original-input preservation and key guard. They are **not** a live API contract guarantee; supported models, exact live payload format, retention quality and production suitability need API integration testing with explicit consent.

## Governance
Source: WhiteChronos GitHub-only. Branch/PR review, complete CI, security review and exact HEAD SHA authorization required. Never merge, run paid inference, deploy or claim LIVE_VERIFIED without independent evidence. Preserve input and private data; never commit credentials.
