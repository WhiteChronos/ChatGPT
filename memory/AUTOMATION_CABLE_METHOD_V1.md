# Automation Cable Method V1 — método ensinado pelo usuário

1. **Registrar desenhos do projeto** — Use quando iniciar ou revisar cálculo de cabos, eletrodutos ou eletrocalhas de automação. Registrar desenhos, revisão, pavimento e escala antes de qualquer cálculo.
2. **Identificar quadro de automação** — Use para localizar o quadro de automação que será referência de origem das rotas.
3. **Classificar encaminhamentos pela legenda** — Use para identificar eletroduto e eletrocalhas pela legenda do desenho.
4. **Levantar instrumentos e disciplinas** — Use para identificar instrumentos, sinais, HVAC e outras disciplinas presentes.
5. **Confirmar símbolos na legenda** — Use para validar os símbolos antes de associá-los a rede, instrumentos ou sensores.
6. **Medir rotas de eletrocalha** — Use para calcular comprimento de eletrocalha desde o quadro usando a escala do desenho.
7. **Identificar reduções de eletrocalha** — Use para detectar transições de dimensão de eletrocalha.
8. **Continuar eletrocalha entre pavimentos** — Use quando o símbolo indicar subida ao pavimento superior.
9. **Identificar eletroduto** — Use para reconhecer o traçado de eletroduto e iniciar seu levantamento.
10. **Eletroduto direto do quadro** — Use quando o eletroduto sai diretamente do quadro.
11. **Eletroduto derivado da eletrocalha** — Use quando o eletroduto nasce da eletrocalha.
12. **Somar comprimento de eletroduto** — Use para calcular o quantitativo físico de eletroduto.
13. **Calcular cabos HART** — Use para chamadas de 1 polegada - 4-20mA + HART e cabos individuais de AT/TT.
14. **Somar rotas individuais de cabos** — Use para calcular cada cabo desde o quadro até seu endpoint.
15. **Subida do sinal digital HVAC** — Use quando a rota digital HVAC sobe de pavimento.
16. **Interpretar cabo digital HVAC** — Use para a chamada de 1 polegada - 1P#1,0mm+SH.
17. **Calcular cascata digital HVAC** — Use para a topologia em cadeia do sinal digital dos ar-condicionados.
18. **Interpretar cruzamento inferior** — Use quando um eletroduto passa por baixo de outro aparente.

## Regras específicas
- HART: um cabo individual por endpoint AT/TT.
- Cabos: trecho compartilhado conta uma vez por cabo no comprimento acumulado, mas uma vez fisicamente no encaminhamento.
- Digital HVAC: chamada `Ø1" - 1P#1,0mm+SH` e topologia em cascata painel -> equipamentos -> último -> painel.
- Cruzamento inferior: rota de eletroduto permanece contínua.

## Governança
Desenho/legenda são evidência primária. Regra não ensinada fica pendente. Toda ação substantiva gera checkpoint no GitHub.


## Toolchain integrado
- Adobe Acrobat: PDF/OCR e extração documental.
- Wolfram: verificação matemática, de escala e de unidades; nunca substitui regra de engenharia.
- tldraw: revisão visual/topológica de grafos, rotas, subidas, derivações e cascatas; nunca substitui DWG/DXF como fonte dimensional.
- GitHub/Codex: memória persistente, versionamento, skills, agente, código e checkpoints.
- Open source: SymPy, SciPy, Pint, NetworkX, Shapely, OpenCV, ezdxf, LibreCAD, LibreDWG, pdfplumber, OCRmyPDF e PyMuPDF conforme licença.

### Pipeline
Documento fonte -> interpretação visual -> grafo técnico -> cálculo determinístico -> verificação Wolfram -> revisão tldraw -> validação -> checkpoint GitHub.
