---
name: whitechronos-connection-controller
description: Verify task-scoped connection state for WhiteChronos GitHub, GitLab, TinyFish, Superpowers, Arena, and Runtime Doctor workflows. Use when a conversation needs to know whether plugins/connectors are actually visible, authenticated, or target-accessible; when a provider is partially degraded; before relying on GitHub/GitLab/TinyFish; or when preparing fail-closed connection preflight evidence.
---

# WhiteChronos Connection Controller

Use fresh host/provider evidence before relying on a connection. Repository configuration is not authentication proof.

## Workflow

1. Keep Superpowers as the software-process owner. Before software execution, verify the relevant Superpowers capability is available/configured and follow its gates.
2. Inspect the actual current host tool/plugin inventory. Never infer host visibility from `.codex/config.toml`, marketplace metadata, or a past conversation.
3. Run only safe provider probes needed by the task:
   - GitHub: identity/profile, then repository metadata when target access matters.
   - GitLab: current user, then project metadata when target access matters.
   - TinyFish: service/account evidence such as wallet state; keep Browser Profile health separate.
4. Treat GitHub/GitLab mirror parity as separate evidence. An identity link or successful authentication is not parity proof.
5. Classify TinyFish service health separately from Browser Profile health. Service PASS plus profile failure is DEGRADED, not whole-service FAIL.
6. When current Codex, Arena MCP, Broker, or native multi-agent runtime capability is material, use Runtime Doctor. Do not infer runtime capability from config.
7. Pass only non-secret evidence to `plugins/whitechronos-control-plane/scripts/connection_preflight.py` when the local normalizer is available.
8. For high-impact repository work, require Arena availability/configuration before final review. Arena is review, not a substitute for runtime agents.

## Safety boundaries

- Never request passwords, tokens, cookies, or browser storage in chat.
- Never persist provider credentials in Git, evidence files, or Skill resources.
- Prefer native GitHub/GitLab connectors for repository API work.
- Use TinyFish browser automation only for a concrete user-directed browser workflow.
- Do not create TinyFish Browser Profiles, Agent runs, Browser runs, monitors, top-ups, or auto-reload changes as routine health checks.
- Treat `HOST_POLICY_BLOCKED` as a platform boundary, not a source-code defect to bypass.
- Fail closed only for the capability the task requires; optional degraded capabilities must not block unrelated native connector work.

Read [connection-contract.md](references/connection-contract.md) for evidence dimensions and [recovery-matrix.md](references/recovery-matrix.md) when a required check is not PASS.
