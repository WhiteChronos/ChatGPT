# Automation Cable Active Prompt

## Fonte de verdade
- WhiteChronos/ChatGPT
- branch feature/automation-cable-ml
- memory/AUTOMATION_CABLE_METHOD_V1.md
- skills/automation-cable-orchestrator/SKILL.md
- agents/automation-cable-engineer/AGENT.md
- codex/automation-cable/AGENTS.md

## Invariantes
- Ler método, estado, desenhos e action log antes de trabalhar.
- Usar a skill do passo aplicável.
- Separar eletrocalha, eletroduto e cabos.
- HART: um cabo por endpoint.
- Digital HVAC: cascata e retorno ao quadro.
- Usar geometria real e escala.
- Regra não ensinada = pendente.
- Salvar checkpoint após ação substantiva.

## Estado
Os 18 passos estão consolidados. Próxima fase: implementar e validar cálculos de produção contra os desenhos sem alterar a semântica ensinada.
