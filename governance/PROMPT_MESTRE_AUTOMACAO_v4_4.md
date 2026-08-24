# PROMPT-MESTRE — AUTOMAÇÃO / FFIC / DIAGRAMAS DE MALHA — v4.4

## REGRA DE OURO
- Nunca sair da simbologia AUTOMAÇÃO DM R00-05.
- Todos os símbolos funcionais devem ter envoltória externa nominal de 12 mm.
- O símbolo nunca pode ser achatado, alongado ou redimensionado para acomodar texto.
- A sequência de classificação é: função → plataforma → localização → variante AUTOMAÇÃO DM → 12 mm → posicionamento.
- Toda tag/bloco deve possuir nome funcional explícito no desenho ou em legenda rastreável.
- CMD, RUN, FAULT e AVAILABLE são informações independentes.
- CMD != RUN; RUN != FAULT; AVAILABLE não é inferido de CMD ou RUN.
- MAN/AUTO != LOCAL/REMOTO.
- Nenhuma linha pode ser órfã; toda interligação precisa de origem, destino, direção, tipo, finalidade e evidência.
- Intertravamentos exigem causa, condição, equipamento afetado, efeito, feedback, reset, estado seguro e fonte.
- Alarme não implica trip.
- Informação sem evidência permanece TBD/PROPOSTO.

## MEMÓRIA E REGRESSÃO
Toda correção relevante deve gerar: (1) memória da ocorrência e lição aprendida; (2) regra preventiva; (3) caso de regressão. Regra aprovada nunca é sobrescrita sem nova versão e histórico.

## ORDEM DO PIPELINE
1. Entendimento documental.
2. Evidência e rastreabilidade.
3. Separação ativo/função/I/O.
4. Nome funcional.
5. Simbologia e 12 mm.
6. Integridade dos sinais.
7. Intertravamentos.
8. Redundância A/B.
9. Cobertura multidisciplinar.
10. Memória/regressão.
11. Auditoria final.

## PRÉ-CONDIÇÃO PARA DESENHAR
Somente desenhar depois de inventário de fontes, entendimento documental, matriz de ativos, dicionário de funções, matriz de sinais, intertravamentos, redundância quando aplicável e pipeline sem finding crítico.

## REGRA CONTRA SIMPLIFICAÇÃO INDEVIDA
CI, Copilot, scripts, agentes, prompts auxiliares e sugestões automáticas não podem substituir o conteúdo de engenharia por texto genérico de software apenas para satisfazer testes. O contrato do CI deve validar a engenharia; nunca redefini-la.
