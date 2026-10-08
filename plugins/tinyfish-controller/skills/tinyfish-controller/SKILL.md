---
name: tinyfish-controller
description: Route TinyFish search, content fetch, browser automation, Browser Profiles, monitors, and cost-sensitive actions safely inside WhiteChronos. Use when a task involves TinyFish, authenticated browser workflows, profile health, browser run failures, website automation, TinyFish monitoring, wallet/cost checks, or deciding whether native GitHub/GitLab connectors should be preferred over TinyFish browser automation.
---

# TinyFish Controller

Use the official TinyFish ChatGPT app as the runtime provider. This controller defines routing, safety, cost, and recovery policy; it does not reimplement TinyFish or hold provider credentials.

## Routing

1. Prefer native GitHub/GitLab connectors for repository API reads, writes, pull requests, pipelines, and project metadata.
2. Use TinyFish `search` or `fetch_content` for public web discovery/read operations when TinyFish is the selected provider.
3. Use TinyFish browser automation only for a concrete user-directed website interaction that cannot be completed through the preferred native connector/API surface.
4. Use a Browser Profile only when the workflow requires authenticated browser state and the profile API is healthy.
5. Create or run monitors only when the user has explicit monitoring intent.

## Authentication and privacy

- Never request passwords in chat.
- Never persist passwords, tokens, cookies, browser storage, or session credentials in Git, Skill resources, reports, or evidence files.
- Let TinyFish/provider-managed authentication own login state.
- Do not create Browser Profiles during routine health checks or connection preflight.

## Cost and side-effect policy

Do not use paid or mutating operations as routine health checks. In particular, do not start Agent runs, Browser runs, monitors, top-up actions, or auto-reload changes merely to prove TinyFish is available.

Read wallet/cost state when a paid action is about to be used or when the user asks for it. Do not silently spend credits to establish service health.

## Degraded capability model

Treat TinyFish service authentication separately from Browser Profile health.

- Service authentication PASS plus Browser Profile API failure is `DEGRADED`, not whole-service `FAIL`.
- `DEGRADED` Browser Profile state does not block TinyFish search/fetch or unrelated native GitHub/GitLab work.
- `HOST_POLICY_BLOCKED` is not a source-code defect. Do not bypass platform policy or mutate repository code to fabricate support.

## Browser run recovery

When a browser run returns timeout or error, follow the provider contract in [provider-contract.md](references/provider-contract.md). Do not start a duplicate run automatically.

For provider/profile recovery states, read [recovery-matrix.md](references/recovery-matrix.md).
