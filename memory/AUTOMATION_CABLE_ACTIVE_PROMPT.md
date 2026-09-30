# Automation Cable Active Prompt

## Fonte de verdade
- WhiteChronos/ChatGPT
- branch feature/automation-cable-ml
- memory/AUTOMATION_CABLE_METHOD_V1.md
- datacenter/AUTOMATION_CABLE_PROCESS_STATE.json
- datacenter/AUTOMATION_CABLE_TOOLCHAIN.json
- skills/automation-cable-orchestrator/SKILL.md
- agents/automation-cable-engineer/AGENT.md
- codex/automation-cable/AGENTS.md

## Invariantes
- Ler método, estado, desenhos, toolchain e action log antes de trabalhar.
- Usar a skill do passo aplicável.
- Separar eletrocalha, eletroduto e cabos.
- HART: um cabo por endpoint.
- Digital HVAC: cascata e retorno ao quadro.
- Usar geometria real e escala.
- Regra não ensinada = pendente.
- Salvar checkpoint após ação substantiva.

## Pipeline obrigatório
1. PDF/DWG/DXF e imagens de projeto.
2. Interpretação visual dos símbolos e rotas.
3. Grafo técnico de nós, segmentos e continuidade entre pavimentos.
4. Motor determinístico de cálculo.
5. Wolfram para verificação matemática e de unidades.
6. tldraw para revisão visual/topológica do grafo e das rotas.
7. Validação contra desenho, legenda, escala e regras ensinadas.
8. Persistência no GitHub antes de encerrar a ação.

## Ferramentas conectadas
- Adobe Acrobat: PDF/OCR/extracao.
- Wolfram: verificação matemática e de unidades; não define regra de engenharia.
- tldraw: visualização/anotação/topologia; não é autoridade dimensional.
- GitHub/Codex: fonte de verdade, código, skills, agente e checkpoints.

## Open source interno
SymPy, SciPy, Pint, NetworkX, Shapely, OpenCV, ezdxf, LibreCAD, LibreDWG, pdfplumber, OCRmyPDF e PyMuPDF conforme licença e necessidade.

## Estado
Os 18 passos estão consolidados e Wolfram/tldraw estão formalmente incorporados ao processo. Próxima fase: executar o pipeline completo sobre os desenhos do projeto.
