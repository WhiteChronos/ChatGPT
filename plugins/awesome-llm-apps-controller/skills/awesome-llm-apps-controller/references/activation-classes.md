# Activation classes

Apply the primary class plus all orthogonal risk booleans from the catalog.

- `REFERENCE_ONLY`: inspect as documentation/source reference; do not execute.
- `LOCAL_READ_ONLY`: local inspection code may run when relevant after source inspection.
- `LOCAL_MUTATING`: require the user's task to authorize the mutation; keep changes scoped/reviewable.
- `NETWORKED`: require relevant permitted network access; do not broaden access just to make an example work.
- `CREDENTIALLED`: never auto-run; require authorized credentials already available for the task. Never invent/configure credentials silently.
- `MCP_OR_CONNECTOR`: do not globally register/enable a server or connector because an example references it; setup requires the current task and authorized environment.
- `BACKGROUND_AUTONOMOUS`: never auto-run; watchers, schedulers, daemons, radars, consumers, or always-on services require an explicit user request and supported automation/runtime.
- `SELF_MODIFYING`: never auto-run; require explicit selection, isolation, and diff/review before accepting generated changes.
- `external_reference`: never auto-run, clone, install, or execute. First perform a separate provenance/license/dependency/security audit of the external project.

`high_stakes_domain` is an independent flag. Medical, financial, legal, mental-health, insurance, or similar examples remain software examples and do not gain authority to bypass applicable safety/domain requirements.
