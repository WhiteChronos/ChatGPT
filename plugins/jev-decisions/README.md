# WhiteChronos Jev — official TypeSafe + optional DefAPI + LLM comparisons

**Activation state: `ACTIVATION_GATED`.** These modules and schemas are **source code and documentation only**. A repository commit or PR does **not** install a ChatGPT plugin, enable hosted inference, make a model appear in ChatGPT, or start a background service.

## Source of truth / identity

- **Original model vendor:** TypeSafe AI — https://typesafe.ai/ (the Jev author, not `jev-ai.org` or an unrelated SEO mirror).
- **Official docs:** https://docs.typesafe.ai/
- **Official API:** `POST https://api.typesafe.ai/v1/systemone`, model `jev-1.13.0` (pinned); `jev-latest` is a moving alias, not recommended for reproducible governance.
- **Official console:** https://console.typesafe.ai/ (acquire/configure `TYPESAFE_API_KEY` privately).
- **First-party Python SDK:** https://github.com/typesafe-ai/typesafe-sdk-python (package `typesafe-sdk`; Python 3.10+).
- **First-party JS SDK:** https://github.com/typesafe-ai/typesafe-sdk-js (`@typesafe-ai/sdk`).
- **First-party System One LLM adapter:** https://github.com/typesafe-ai/system-one-adapter-python (`system-one-adapter` with optional `openai`, `anthropic`, and `gemini` extras).
- **First-party agent skills:** https://github.com/typesafe-ai/skills (referenced, **not automatically installed or vendored**).
- **TypeSafe compatible gateways, documented by vendor:** OpenRouter, Vercel AI Gateway, Pydantic AI Gateway: https://docs.typesafe.ai/sdk/python/usage#configuring-the-base-url . They require their **own** credentials and model IDs and are NOT automatically activated.
- **Third-party DefAPI:** https://defapi.org/api/model/en/typesafe/jev-1.13 . Earlier client `defapi_jev.py` and `chatgpt-action.openapi.json` stay separate and read `DEFAPI_API_KEY`. Do **not** send a DefAPI key to the TypeSafe API or vice versa.

Jev is **not a generative LLM**. Its choice/score/noul values serve as bounded advisory decisions for ordinary code. OpenAI, Anthropic and Gemini are separately configured LLM backends used for **comparison** or downstream specialist handling, not claims of TypeSafe-owned or Jev-native LLM models.

## What is in this PR

| File | Role |
|---|---|
| `typesafe_bridge.py` | Explicit official Jev evaluation (`evaluate_jev`), optional LLM comparison through upstream System One adapter (`evaluate_llm_comparison`), pure allowlisted route selection (`choose_llm_handler`), and a bounded Jev-to-LLM recommendation (`route_with_jev`) |
| `chatgpt-action-typesafe.openapi.json` | Optional legacy Custom GPT Action schema for official TypeSafe endpoint — private Bearer key configured in a supported GPT editor, **not** auto-activated |
| `defapi_jev.py` / `chatgpt-action.openapi.json` | Existing alternative third-party gateway, unchanged |
| `registry/integrations/typesafe-jev.json` | Separate official adapter descriptor, `CREDENTIALLED` / `ACTIVATION_GATED`; no enabled MCP server, host probe, worker, or default installation |
| `tests/test_typesafe_bridge.py` | Offline fake-client TDD for request validation, official response shape, LLM optional integrations, uncertainty gating, and credential leak resistance |

## How to use (authorized development environment only)

**Dependencies are optional and are not installed by this PR.** Following review and explicit consent to run paid external calls:

```bash
python -m pip install typesafe-sdk
python -m pip install 'system-one-adapter[openai,anthropic,gemini]'
```

Use only the extras you intend to operate; validate and pin versions according to your lockfile/security policy. Set secrets through a supported **external** secret manager or interactive environment; never commit `.env`/keys, post keys in ChatGPT, or put them in GitHub Actions logs. The SDK's own logger may include request/response bodies; do not enable debug logging for real user state.

```python
from typesafe_bridge import evaluate_jev, route_with_jev

# Safe example uses intentionally synthetic data.
result = evaluate_jev("A fictional customer needs help with a refund.", {
    "department": {"type": "choice", "instructions": "Which team handles this?",
                   "criteria": {"billing": "charges/refunds", "technical": "bugs"}}
})

# User/app controls the allowlisted candidates and the LLM model IDs.
catalog = {
    "openai": {"provider": "openai", "model": "your-allowed-openai-model", "description": "Short coding requests"},
    "anthropic": {"provider": "anthropic", "model": "your-allowed-anthropic-model", "description": "Long document analysis"},
    "human": {"provider": "human", "model": "", "description": "Ambiguous, unsafe or high-impact requests"}
}
route = route_with_jev("A synthetic request to classify", catalog)
# route.status is SUGGESTED_ONLY or REVIEW_REQUIRED; no LLM was invoked.
```

For opt-in A/B comparison against a generative LLM using the **official TypeSafe System One adapter**:

```python
from typesafe_bridge import evaluate_llm_comparison
alternative = evaluate_llm_comparison(
    "Fictional sample", {"urgent": {"type": "noul", "instructions": "Does this sound urgent?"}},
    provider="openai", model="your-configured-model-id",
)
```

These are **separate calls**; comparison does not imply Jev ran OpenAI, Claude or Gemini inside the TypeSafe service. The LLM adapter's debug traces may contain state and prompts; the WhiteChronos wrapper intentionally omits debug fields from returned data.

`route_with_jev` suggests a provider only; the host/application is responsible for approved credentials, permission checks, model call, costs, human review and redaction. Example thresholds (0.80 confidence / 0.75 selected-option probability) are not production-calibrated. If the choice is uncertain, absent, not on the allowlist or selects a human/no-match path, it returns `REVIEW_REQUIRED`. There is no auto-merge, code write, tool dispatch, deployment, production approval or fallback-to-external API.

## ChatGPT connection (manual only)

For a Custom GPT that still supports Actions, use `chatgpt-action-typesafe.openapi.json` in **Actions > Create new action**, choose protected API Key/Bearer authentication and store only the **TypeSafe** key there. Test with synthetic data in Preview. These custom GPT Actions are being retired/migrated to plugins and **will not be preserved automatically**: https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq . A durable ChatGPT integration needs a separately developed, hosted, reviewed and connected **MCP plugin/app**, with server-side secret handling and workspace authorization: https://developers.openai.com/api/docs/guides/custom-mcp-server . No such hosted MCP server is created by this source PR.

## Gates / data boundary

- Never send engineering baselines, private projects, confidential files, health records, source code or identifiable user information to TypeSafe/DefAPI/other LLM vendors without separate legal/privacy approval. This repository is public.
- Keep the official and DefAPI responses separate: **TypeSafe does not require `task_id` or `consumed`**; those fields are specific to the earlier DefAPI integration. Do not conflate model IDs or service keys.
- Use a pinned Jev model for repeatable measurement. The official documentation notes that Jev's primary training language is English; benchmark Portuguese workflows using labeled examples before operational routing.
- All network calls are explicit opt-in; this PR includes **only mocked/offline tests**.
- No merge, secrets provisioning, runtime/host discovery claim, external live smoke, deployment, GitLab reactivation, or `PRODUCTION_COMPLETE`.
- Stop at **READY FOR MERGE REVIEW**, subject to exact-HEAD CI/security/review and explicit SHA-specific merge authorization.

Offline tests: `python -m pytest -q tests/test_typesafe_bridge.py tests/test_jev_decisions.py` in a full checkout. New tests can be run in isolation without the optional vendor SDKs.
