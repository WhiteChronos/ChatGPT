# Repositórios GitHub de apoio ao MCE — proveniência e limites

A fonte de verdade do código MCE é **WhiteChronos/ChatGPT**. As demais fontes públicas ajudam somente a obter/avaliar dados auxiliares de P&ID, OCR e benchmarks; **nenhum desses projetos é fonte contratual da lógica de intertravamento**. Ver pesquisa original `systems/mce/research/top10_verificados.json` e `systems/mce/.agents/skills/engenharia-mce-projeto/references/pesquisa-pid-github.md`.

| Repositório | Papel no processo MCE | Licença registrada no GitHub (29/10/2026) | Estado histórico no MCE (28/10/2026) | Regra |
| --- | --- | --- | --- | --- |
| [WhiteChronos/ChatGPT](https://github.com/WhiteChronos/ChatGPT) | Código principal, Skills, testes, PR #118, memória Issue #120 | Regras próprias do projeto | Fonte canônica | HEAD e CI atuais antes de agir |
| [Azure-Samples/digitization-of-piping-and-instrument-diagrams](https://github.com/Azure-Samples/digitization-of-piping-and-instrument-diagrams) | Grafo P&ID e relações de ativos | MIT | Adaptador **JSON próprio testado** | Adjacência ≠ lógica causa/efeito; não enviar dados industriais à nuvem |
| [S-Houston/digitised-pid-mlops](https://github.com/S-Houston/digitised-pid-mlops) | OCR, CSV `filename,consolidated_text` | Não identificada | Adaptador **CSV próprio testado** sem copiar código | Revisão humana de TAG/texto; não redistribuir código sem licença |
| [ZzzJjt/Industrial-Control](https://github.com/ZzzJjt/Industrial-Control) | Exemplo didático de interlock | Não identificada | Referência **não normativa**, bug de sombreamento em `effect_list` observado | Nunca importar como validador de segurança |
| [hkoziolek/DiagEx-Repro](https://github.com/hkoziolek/DiagEx-Repro) | Benchmark P&ID→DEXPI | Apache-2.0 | Benchmark offline **planejado**, não executado neste workflow | Fixar versão, direitos sobre dados e reprovação de OCR não validado |
| [process-intelligence-research/pyDEXPI](https://github.com/process-intelligence-research/pyDEXPI) | Proteus/DEXPI e grafo | AGPL-3.0 | Contrato opcional **futuro** | Licença AGPL exige análise jurídica antes de integrar código |
| [mgupta70/PIDQA](https://github.com/mgupta70/PIDQA) | Benchmark de perguntas sobre P&ID | CC0-1.0 para repositório | Benchmark planejado | Verificar direitos dos datasets de terceiros separadamente |

## Fluxo de evidência externa

1. Conferir URL, owner, ramo, commit SHA, licença, README, formato e escopo via GitHub; snapshots antigos não garantem funcionamento atual.
2. Aplicar **adaptadores MCE próprios**, somente quando já suportados e com arquivos locais autorizados. SHA-256 de cada entrada/saída; evidência de origem em documento/folha/revisão.
3. Comparar OCR/grafo com P&ID real e lista I/O. Classificar derivações `INFERIDO_PARA_REVISAO` até revisão humana; discrepâncias bloqueiam promoção a `DOCUMENTADO`.
4. Para qualquer relação funcional C→E exigir narrativa, SRS ou filosofia **aprovadas**, independentemente do candidato OCR.
5. Não executar código de outros repositórios, clonar, instalar dependências cloud ou transmitir arquivos sem autorização explícita. Licença permissiva **não** autoriza divulgar dados do cliente.

Pesquisa editorial da própria pasta `research/`: 151 distintos vistos, 100 amostrados e 10 revisados em detalhe; pontuação editorial **não é prova de auditoria independente, conformidade normativa ou execução dos 100**. O inventário não substitui normas contratuais IEC/ISA aplicáveis ao projeto.