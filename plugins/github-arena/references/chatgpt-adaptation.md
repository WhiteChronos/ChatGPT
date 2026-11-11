# ChatGPT adaptation

The original Arena implementation assumes Claude Code can spawn many isolated subagents. A ChatGPT conversation must not pretend that capability exists when the runtime does not expose it.

## Rules

- Activate for all GitHub-related tasks through the broad Skill trigger.
- Run four-lens Micro Arena by default.
- Use a larger strategy set only for high-impact work or explicit Arena requests.
- When true subagents are unavailable, execute multiple strategy passes sequentially in the same model.
- Never report upstream call counts as calls actually executed unless they were executed.
- Keep the upstream method as a reference architecture for runtimes that later gain isolated-agent orchestration.

This keeps the GitHub review discipline global without multiplying cost on simple operations.
