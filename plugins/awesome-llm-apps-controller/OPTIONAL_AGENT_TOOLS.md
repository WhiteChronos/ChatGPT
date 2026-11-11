# Optional external agent tools — Awesome LLM Apps and Unwind AI

## Scope and authority

WhiteChronos remains the primary system. The public [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps) repository is an **optional, independently maintained source of agent examples and components**, not the runtime authority, replacement controller, or mandatory dependency. [Unwind AI](https://www.theunwindai.com/) is an educational/tutorial/news source connected to this ecosystem; it is **not** an agent runtime or an authenticated WhiteChronos MCP service.

Existing integration: `plugins/awesome-llm-apps-controller/`, provenance `upstream.lock.json`, catalog `registry/awesome-llm-apps/catalog.json`, and read-only vendor mirror. The mirror is already associated with upstream and pinned by a recorded commit; a user-owned fork is optional and has **not** been created by this change.

## Git association and isolated checkout

To work on a selected example in a GitHub Actions runner, Codespace, or Codex workspace with Git installed (no user's Windows connection required):

```bash
git clone --no-checkout https://github.com/Shubhamsaboo/awesome-llm-apps.git /tmp/whitechronos-optional-agents
git -C /tmp/whitechronos-optional-agents checkout --detach "$(python -c 'import json; print(json.load(open("plugins/awesome-llm-apps-controller/upstream.lock.json"))["commit"])')"
git -C /tmp/whitechronos-optional-agents rev-parse HEAD
```

Run from the WhiteChronos repository root. For a private persistent checkout, replace `/tmp` with an authorized workspace folder. **Inspect the selected example's readme, manifests, dependency scripts and license before any installation.** Do not execute repository-wide install, arbitrary curl-to-shell, background agents, or unreviewed Docker builds. Mount the selected example with least-privilege filesystem and network access. Any credentials must be supplied by an approved secret manager only when that agent actually requires them.

This is a plain clone of a public upstream into a **separate** directory. It does not fork into the user's GitHub account. Creating a user-owned fork requires an authorized GitHub operation with the correct account scope; do not claim it exists unless independently verified.

## Selection and invocation contract

1. Search `registry/awesome-llm-apps/catalog.json` for the requested task; prefer a minimal, explicitly approved example.
2. Inspect `execution_class`, `source_type`, license, required credentials, high-stakes flags, upstream path, and pinned SHA. `REFERENCE_ONLY` examples are not executable by default.
3. Use an isolated checkout; create a Python virtual environment for Python examples. Follow project-specific lockfiles and prerequisites; do not install all catalog entries.
4. Require explicit permission for mutations, network calls, external costs, credentials, or autonomous/background execution.
5. Run focused tests and a bounded no-secret smoke test, preserving exit code and logs; record whether the agent actually ran, and any failures.
6. Invoke Arena and Superpowers as WhiteChronos's review/process layer. Do **not** describe these sample agents as native Codex subagents unless host discovery and a genuine independent lifecycle are observed.
7. Submit any WhiteChronos adapter modifications via protected PR and CI. Never write upstream example changes into the vendor mirror directly.

## Unwind AI usage

Read or cite tutorials for research and design selection. Do not scrape behind login, submit user data, authenticate, or claim it exposes an MCP/API integration without verifying official documentation and permission. No newsletter subscription or account linkage is needed for this architecture.

## Acceptance evidence

Record: exact WhiteChronos SHA, upstream SHA, selected catalog ID/path and execution class, dependencies and license review, host (Codespace/runner/Codex) identity, commands run, test outcome, any actual process/tool IDs, and constraints. `RUNTIME_COMPLETE` still needs evidence from the actual chosen runtime; a catalog entry or git clone is not sufficient.
