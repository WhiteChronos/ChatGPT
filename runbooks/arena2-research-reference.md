# ARENA 2.0 — optional research reference for WhiteChronos

## Verified identity and scope

- Project: [callummcdougall/ARENA_2.0](https://github.com/callummcdougall/ARENA_2.0)
- Git source: `https://github.com/callummcdougall/ARENA_2.0.git`
- Observed `main` commit at registration: `e805ad8772b81fa44252ab3b7590ac614aa29376`
- Source type: `external_reference`; execution class: `REFERENCE_ONLY`
- License: **UNVERIFIED** — no repository-root `LICENSE` file was present at inspection. Do not redistribute or vendor its code without separate licensing confirmation.
- Purpose: educational exercises and Streamlit material about ML fundamentals, transformers, mechanistic interpretability, reinforcement learning and training at scale.

This **is not GitHub Arena**, not a Codex agent catalog, not a replacement for Superpowers, and not an MCP/subagent service. WhiteChronos remains the primary project and sole GitHub CI/merge authority. Do not register ARENA 2.0 as a live agent, plugin, MCP server, or required runtime dependency.

## Four requested WhiteChronos operational roles

These are human-facing references to existing local components, **not newly created native @-mention shortcuts, independent child agents, or proof of Codex-host availability**.

| Requested role | Local source of truth | Responsibility |
| --- | --- | --- |
| @GitHub Arena | `plugins/github-arena/skills/github-arena/SKILL.md` | Structured review and GitHub quality gates |
| @Codex Runtime Doctor | `plugins/whitechronos-control-plane/scripts/runtime_doctor.py` | Differentiate CONFIGURED, LOCAL_RUNTIME_HEALTHY, HOST_DISCOVERED, LIVE_VERIFIED |
| @Subagent Broker | `plugins/subagent-broker/skills/subagent-broker/SKILL.md` | Independent child lifecycle when actual broker MCP tools are discovered |
| @Superpowers Controller | `plugins/superpowers-controller/skills/superpowers-controller/SKILL.md` | Route work to official Superpowers processes when actually available |

Runtime load and tool discovery must be checked in the **real current Codex host**, not inferred from `.codex/config.toml` or from GitHub Actions.

## Safe optional Git inspection

The reference is already linked through `registry/integrations/arena-2.0.json`. No fork or local clone is required to use the link for research. For an authorized isolated GitHub/Codex workspace only, one may inspect exactly the recorded upstream commit:

```bash
mkdir -p /tmp/arena2-reference
git -C /tmp/arena2-reference init
git -C /tmp/arena2-reference remote add origin https://github.com/callummcdougall/ARENA_2.0.git
git -C /tmp/arena2-reference fetch --depth 1 origin e805ad8772b81fa44252ab3b7590ac614aa29376
git -C /tmp/arena2-reference checkout --detach FETCH_HEAD
git -C /tmp/arena2-reference rev-parse HEAD
```

This optional clone is not an instruction for automatic execution. Do not install the repository-wide `requirements.txt`, run notebooks, activate GPU training, start services, publish content, create credentials, or connect a user's Windows device as part of routine reference registration. The requirements include legacy package pins and Git-hosted dependencies; evaluate each selected exercise separately before execution.

## Gates and evidence

Any proposal to execute or incorporate individual ARENA 2.0 exercises requires verified licensing for the intended use, version/pin review, dependency and security audit, isolated environment, and explicit task scope. If a specific exercise is approved, record repository SHA, command, host, dependencies, result and evidence. Curriculum exercises do not count as native Codex subagents.

Normal WhiteChronos gates remain unchanged: Superpowers owns software development process, GitHub Arena owns review, Runtime Doctor owns host evidence, and Subagent Broker owns independent child lifecycle only if discovered. CI success is not `HOST_DISCOVERED`, `LIVE_VERIFIED` or `RUNTIME_COMPLETE`.
