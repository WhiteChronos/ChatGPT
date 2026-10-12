# DefAPI Jev-1.13 — optional WhiteChronos decision adapter

**State: ACTIVATION_GATED.** The repository contains an optional Python adapter and a ChatGPT Action OpenAPI schema. This does not install or connect the model to the current ChatGPT session.

## Contract and privacy

- Source of truth: https://defapi.org/api/model/en/typesafe/jev-1.13
- Endpoint: POST https://api.defapi.org/api/v1/decisions
- Model: typesafe/jev-1.13 — a typed decision model, **not** a chat-completions model.
- State may be text, object or array. Each named question uses noul, choice or score. Replies include answers, usage, task_id and consumed.
- Every API request sends state and instructions to the third-party provider; **never** submit credentials, private engineering documents, personal data, repository secrets or proprietary code without separately approved sharing.
- Jev output is advisory only. It **cannot** approve or execute a PR merge, deployment, release, live smoke or runtime readiness declaration.

## Manual ChatGPT connection: Custom GPT Action

1. Obtain a **DefAPI** API key through your DefAPI account; never paste it into chat, repository source, PR, issues or documentation.
2. In a ChatGPT Custom GPT editor with Actions enabled, select **Actions > Create new action** and paste/import [chatgpt-action.openapi.json](chatgpt-action.openapi.json).
3. Set **Authentication > API key > Bearer**. Enter your DefAPI key in the editor's protected authentication field (omit the literal Bearer prefix if the editor supplies it). **Do not** use an OpenAI API key.
4. Add GPT instructions: call the action only after an explicit request; get authorization before transmitting third-party state; pass only nonconfidential data; treat output as an estimate and never an action or release gate.
5. Test in Preview with synthetic data, and verify answers, usage, task_id, and consumed. A 401 means authentication failed; a 400 suggests input validation.

This is a manual compatibility bridge. **It does not change the ChatGPT model selector and does not connect this existing conversation automatically.** Some ChatGPT workspaces restrict Action domains or modes. OpenAI has announced a migration from Custom GPTs toward plugins for affected workspaces; future production use should employ a separately built/reviewed/hosted ChatGPT plugin or MCP app with secret management. See https://help.openai.com/en/articles/9442513 .

## Python adapter: opt-in, zero third-party dependencies

The [defapi_jev.py](defapi_jev.py) module reads DEFAPI_API_KEY from the OS environment **at call time**. It never stores credentials, schedules calls or enables a worker. Example, after adding this directory to PYTHONPATH and configuring the secret **outside** the repository:

```python
from defapi_jev import decide
result = decide(
    {"ticket": "Synthetic page renders incorrectly"},
    {"owner": {
        "type": "choice",
        "instructions": "Which synthetic group should investigate?",
        "criteria": {"frontend": "Rendering", "data": "Data pipeline"},
    }},
)
print(result["answers"]["owner"])
```

A real request requires an API key and can incur fees. All repository tests use mocks and do **not** contact DefAPI.

Local tests: `python -m pytest -q tests/test_jev_decisions.py`.

## GitHub registration and security gates

The registry entry `registry/integrations/defapi-jev.json` is `CREDENTIALLED` / `ACTIVATION_GATED`; it has **no** active MCP server or host runtime probe. The PR cannot grant runtime health or production-ready status. This integration adds no GitHub secrets, no paid network workflow, no auto-merge, no deployment and no GitLab components. The existing GitHub-only ruleset, security checks, and exact-SHA merge gate remain authoritative.

## Outstanding work

- Configure the DefAPI key only in a supported secret UI or external secret manager.
- Import and manually verify the Action in an eligible ChatGPT host with an approved synthetic live request.
- Before real business usage, review data-sharing and privacy boundaries.
- If the Custom GPT migration disables Actions, design/host/register a proper ChatGPT plugin/MCP adapter separately.
- Merge, deployment, secret provisioning, and any external live smoke are blocked pending their independent approvals.

Rollback: before merge, close this draft PR; after any independently authorized merge, revert with an ordinary reviewed PR. No provider credentials are created here.
