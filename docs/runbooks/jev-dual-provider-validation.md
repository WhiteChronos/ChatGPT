# Jev dual-provider validation — WhiteChronos

## Scope and authority

This procedure verifies two **separate** interfaces to Jev-1.13 using synthetic fixtures:

| Source | Transport and pinned model | Credential |
|---|---|---|
| Original vendor, TypeSafe AI | `POST https://api.typesafe.ai/v1/systemone` via `typesafe-sdk`, `jev-1.13.0` | `TYPESAFE_API_KEY` |
| Third-party DefAPI gateway | `POST https://api.defapi.org/api/v1/decisions` via the stdlib client, `typesafe/jev-1.13` | `DEFAPI_API_KEY` |

The vendor and gateway may have different response envelopes, token usage, cost information, incidents, calibration, latency and access requirements. Do **not** silently substitute one for the other. They are not separate LLMs; Jev returns typed `choice`, `score`, or `noul` answers. OpenAI, Anthropic and Gemini are optional **comparators** provided by TypeSafe's separately maintained `system-one-adapter`, not engines owned by Jev.

## Current evidence, 2026-10-12

- The code is staged in the **draft** WhiteChronos [PR #91](https://github.com/WhiteChronos/ChatGPT/pull/91), not merged or deployed.
- Local tests use synthetic text, fake TypeSafe SDK clients and patched DefAPI transports only. No vendor credentials, external inference or non-public data were used.
- TDD uncovered: DefAPI insufficient probability-distribution validation; untrusted gateway debug echoed into results; possible bearer-bearing HTTP redirects; TypeSafe LLM comparator did not verify returned model; Jev recommendation logic could trust incomplete distributions; official SDK permits missing token usage.
- Regressions cover binary, choice and score contracts, input/answer matching, distinct Bearer boundaries, missing tokens, no secrets in exceptions, cost/task metadata, denial of 30x redirects and rejection of malformed answers.
- CI workflow: `.github/workflows/jev-dual-contract.yml` runs the same offline tests without secrets. CI green is code evidence **only**, not network or host runtime proof.

## Offline verification

From a checked-out repository, run:

```bash
python -m pytest -q tests/test_jev_decisions.py tests/test_typesafe_bridge.py tests/test_jev_dual_contract.py
python -m json.tool plugins/jev-decisions/chatgpt-action.openapi.json > /dev/null
python -m json.tool plugins/jev-decisions/chatgpt-action-typesafe.openapi.json > /dev/null
```

Each provider's test asserts its distinct URL, model identifier and authentication contract. Identical synthetic probability values are not evidence of matching real-world output quality. If the gateway and official provider disagree in a later approved live comparison, record it as **DIFFERENT_RESULT**, not a code failure or a vote authorizing an action.

## Live verification is a separate authorization gate

Only after an authorized human explicitly permits a paid/networked synthetic request and the runtime has independently supplied the secrets from an approved secret manager:

1. Verify TypeSafe account entitlement and DefAPI account entitlement independently (no shared keys); review provider terms and egress destinations.
2. Run one documented **synthetic** input through `evaluate_jev` and `decide`, with a fixed question set of Noul, Choice, Score; never send engineering documents, credentials, customer data or internal code.
3. Observe each provider's real HTTP status, exact model ID, question IDs/types, valid probability mass (when provided), response time and reported usage/billing. Record task IDs only when appropriate; do not store tokens or raw private prompts.
4. Treat absent token usage as `UNKNOWN`, not zero. Verify retry, timeout, rate limit and data egress limits before wider use.
5. Compare functional outputs, record observed differences, and calibrate any routing thresholds using approved labeled-domain samples. No inference authorizes tool calls, merges or releases.
6. Keep independent evidence for `CONFIGURED`, local runtime, connected host discovery and paid live verification. Never infer a connected ChatGPT plugin from a committed OpenAPI file.

No live request, credential provisioning, installation, merge, deploy, canary/stable promotion or `PRODUCTION_COMPLETE` is part of this PR.

## Evidence sources

- TypeSafe AI: https://typesafe.ai and https://docs.typesafe.ai/
- TypeSafe Python SDK: https://github.com/typesafe-ai/typesafe-sdk-python (`Usage` fields are `int | None`; optional credentials from the environment).
- TypeSafe System One LLM adapter: https://github.com/typesafe-ai/system-one-adapter-python (separate opt-in providers).
- DefAPI schema and examples: https://defapi.org/api/model/en/typesafe/jev-1.13 (OpenAPI 3.0.3; custom envelope includes `task_id` and `consumed`).
- GitHub-only policy: `runbooks/github-only-ci.md` and active ruleset `Chronos`.
