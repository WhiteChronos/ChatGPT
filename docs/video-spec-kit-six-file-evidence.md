# Evidence: supplied Instagram video / six-file method / GitHub Spec Kit

## Source and scope
User-supplied video: `savekit-video-b16f4f342676601d.mp4` (41.961375 seconds, 720x1280, audio present). Contact sheet sampled at approximately 5 second intervals; no assertion about unseen details, narration or omitted frames. Publication: https://www.instagram.com/p/DeW-QAoAT0i/.

## Directly observed visual sequence (sampling may omit transitions)
- Opening: "6 arquivos para criar antes de programar com IA"; displayed `docs/` files: `prd.md`, `arquitetura.md`, `regras.md`, `tarefas.md`, `memoria.md`, `cenario.md`.
- `prd.md`: problem, target audience, first version and out-of-scope.
- `arquitetura.md`: system layers (client, web, API, database), technology stack and folder organization.
- `regras.md`: coding rules, what the agent must not do, structure.
- `tarefas.md`: phases, tasks, priority and status.
- `memoria.md`: project status/decisions and where the work stopped.
- Final frames: "github / spec-kit"; principles, specification, plan, tasks and implementation.
- The short video is explanatory, not evidence of running code, installation or cloud parity. Audio has not been transcribed here.

## Verified upstream
https://github.com/github/spec-kit ; MIT (LICENSE inspected). Current README describes official Spec-Driven Development using constitution -> specify -> plan -> tasks -> implement -> converge. Video six markdown documents are an illustrative organizational approach, **not** official one-to-one replacements for Spec Kit's built-in commands. Do not alter upstream; version the WhiteChronos-specific skills.

## Mapping to the WhiteChronos repository
| Video artifact | Skill | Official Spec Kit touchpoint |
|---|---|---|
| prd.md | spec-kit-requisitos-prd | specify |
| arquitetura.md | spec-kit-arquitetura-sistema | plan |
| regras.md | spec-kit-regras-desenvolvimento | constitution |
| tarefas.md | spec-kit-tarefas-planejamento | tasks |
| memoria.md | spec-kit-memoria-projeto | keep audited session records; no exact official command |
| cenario.md | spec-kit-cenario-validacao | specify/test checklists and converge; no exact official command |

## Acceptance and truthfulness
- Six entrypoints with metadata, maintainable instructions, and source provenance.
- GitHub actions at exact HEAD, then independent human review. No auto-merge.
- Before claiming full runtime, run actual Spec Kit commands on a compatible, authorized cloud/host with captured logs, versions, and outputs.
- A ChatGPT skill coordinates supported tools; it is not a cloud computer, local terminal, Spec Kit installation or always-on autonomous process.
- No secret provisioning, paid inference, Codex-only dependency, deployment or PRODUCTION_COMPLETE.
