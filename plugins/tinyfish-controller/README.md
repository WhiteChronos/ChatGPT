# TinyFish Controller

WhiteChronos policy layer for using the official TinyFish ChatGPT app without turning TinyFish into a credential store, repository connector replacement, or automatic paid health probe.

## Responsibilities

- Prefer native GitHub/GitLab connectors for repository API work.
- Use TinyFish search/fetch for public web work when selected.
- Use browser automation only for concrete user-directed website interactions.
- Keep TinyFish service authentication separate from Browser Profile health.
- Treat service PASS plus Browser Profile failure as `DEGRADED`.
- Require explicit user intent before monitors or other ongoing operations.
- Never request or persist passwords, tokens, cookies, browser storage, or session credentials.
- Never use Agent runs, Browser runs, monitors, top-up, or auto-reload changes as routine health checks.
- On browser timeout/error, poll the same run rather than starting a duplicate automatically.

The plugin exposes Skills only. It intentionally has no `.mcp.json`; the actual TinyFish runtime provider remains the installed ChatGPT app.
