# TinyFish provider contract

## Preferred surfaces

- Repository API and repository mutations: use native GitHub/GitLab connectors.
- Public web search/read: TinyFish search/fetch may be used when selected.
- Interactive UI automation: TinyFish browser automation only for a concrete user-directed browser workflow.
- Authenticated browser UI: Browser Profile only after provider-managed login and only when profile APIs are healthy.

## Browser run lifecycle

A browser run is a durable provider operation. After starting one, keep its returned run/session identity.

If the provider reports a timeout or error, poll the same run through the supported wait/get interface. Do not start a duplicate run automatically, because duplicate runs can repeat external side effects and consume additional credits.

Only start a replacement run when the previous run is definitively terminal and the user-directed workflow still requires a new attempt under the provider contract.

## Monitors and paid operations

Monitoring is never implied by a one-time request. Create, resume, or run a monitor only after explicit user intent for ongoing monitoring. Agent runs, Browser runs, monitor runs, wallet top-up, and auto-reload changes are not routine health probes.
