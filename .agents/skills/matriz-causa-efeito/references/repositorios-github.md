# Repositórios GitHub vinculados ao MCE

**Fonte de verdade da implementação:** [WhiteChronos/ChatGPT](https://github.com/WhiteChronos/ChatGPT), PR #118, memoria `systems/mce/spec/memoria.md` e Issue #120. Pesquisa de apoio controlada em `systems/mce/research/top10_verificados.json` e `systems/mce/.agents/skills/engenharia-mce-projeto/references/pesquisa-pid-github.md` (snapshot 28/10/2026).

| Repo | Papel / contrato | Licenca metadata GitHub consultada 29/10/2026 | Estado na pesquisa MCE |
| --- | --- | --- | --- |
| [Azure-Samples/digitization-of-piping-and-instrument-diagrams](https://github.com/Azure-Samples/digitization-of-piping-and-instrument-diagrams) | Grafo de ativos e conexoes P&ID | MIT | Adaptador JSON proprio testado; direcao/topologia nao implicam trip |
| [S-Houston/digitised-pid-mlops](https://github.com/S-Houston/digitised-pid-mlops) | OCR CSV `filename,consolidated_text` | Nao identificada | Adaptador CSV proprio testado; nao copiar codigo |
| [ZzzJjt/Industrial-Control](https://github.com/ZzzJjt/Industrial-Control) | Exemplo de codigo interlock | Nao identificada | Nao normativo; defeito conhecido em `effect_list`, nao usar para validar seguranca |
| [hkoziolek/DiagEx-Repro](https://github.com/hkoziolek/DiagEx-Repro) | Benchmark P&ID para DEXPI | Apache-2.0 | Benchmark offline planejado, nao executado pelo workflow |
| [process-intelligence-research/pyDEXPI](https://github.com/process-intelligence-research/pyDEXPI) | DEXPI/Proteus e NetworkX | AGPL-3.0 | Somente contrato futuro opcional, exige exame juridico |
| [mgupta70/PIDQA](https://github.com/mgupta70/PIDQA) | Benchmark de perguntas sobre P&ID | CC0-1.0 no repo | Benchmark planejado; direitos de datasets externos separados |

### Protocolo
1. Confirmar URL, commit, licença, README, versao e formato **antes de usar**; metadados atuais nao garantem que o snapshot do projeto continua compativel.
2. Usar somente adaptadores locais do MCE ja revisados e arquivos autorizados; nenhuma instalacao automatica, transmissao a Azure/AWS ou copia de fonte de terceiro sem autorizacao e licenca compativel.
3. Inventariar cada fonte e derivado com SHA-256, documento/folha/revisao e revisor. OCR/grafo = `INFERIDO_PARA_REVISAO` ate confirmacao humana.
4. Relacao causa→efeito e comando de trip so podem ser `DOCUMENTADO` com narrativa, filosofia ou SRS de projeto e revisao aplicavel. Nenhum dos repositorios externos homologa MCE.

A lista historica do MCE menciona 151 repos vistos, 100 amostrados e 10 avaliados em detalhe; essas contagens sao descricoes de pesquisa editorial, **nao** teste de 100 integracoes ou auditoria de seguranca dos terceiros.
