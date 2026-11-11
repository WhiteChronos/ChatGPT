# PROMPT-MESTRE — AUTOMAÇÃO / FFIC / DIAGRAMAS DE MALHA — v4.5

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

## REGRA DE OURO DOCUMENTAL — MD / ET / LI / FD
- O arquivo original aprovado é a matriz de layout e deve permanecer intocado.
- O sistema pode alterar somente texto, valores técnicos, TAGs, códigos, referências, quantitativos textuais e imagens técnicas expressamente aprovadas.
- É proibido alterar margens, geometria de tabelas, largura de colunas, altura de linhas, mesclagens, bordas, estilos, fontes, cabeçalhos, rodapés, logo, assinatura, área de impressão, orientação, escala ou estrutura de seções sem autorização explícita.
- Em Excel, LI e FD/Data Sheet devem manter integralmente o layout interno; o texto deve ser adaptado ao espaço existente, nunca o template ao texto.
- Em Word, MD e ET devem preservar estilos, tabelas, margens, cabeçalhos, rodapés, imagens e objetos do modelo.
- A paginação é dinâmica: “Folha X de Y”, total de páginas/folhas e referências do sumário devem acompanhar a quantidade final efetivamente emitida.
- A paginação dinâmica é a única exceção automática à imutabilidade estrutural do layout.
- Toda revisão controlada deve registrar fingerprint do template original e bloquear emissão se houver mutação estrutural não autorizada.

## DATA CENTER E DATA SHEET
- O DatacenterStructureAgent deve registrar o template mestre, fingerprint, tipo documental, revisão, componentes protegidos, alterações autorizadas e quantidade final de folhas.
- O DataSheetConsistencyAgent deve atuar sobre LI e FD, validar TAGs, códigos, descrições, quantidades e referências contra desenhos/documentos de base e bloquear qualquer mudança de layout não autorizada.
- Nenhuma nova revisão pode sobrescrever silenciosamente o padrão anterior; todo aprendizado deve ser versionado e rastreável.

## MEMÓRIA E REGRESSÃO
Toda correção relevante deve gerar: (1) memória da ocorrência e lição aprendida; (2) regra preventiva; (3) caso de regressão. Regra aprovada nunca é sobrescrita sem nova versão e histórico.

## ORDEM DO PIPELINE
1. Entendimento documental.
2. Evidência e rastreabilidade.
3. Validação do template mestre e bloqueio de layout.
4. Separação ativo/função/I/O.
5. Nome funcional.
6. Simbologia e 12 mm.
7. Integridade dos sinais.
8. Intertravamentos.
9. Redundância A/B.
10. Cobertura multidisciplinar.
11. Data Sheet / LI / FD consistency check quando aplicável.
12. Paginação final e referências internas.
13. Memória/regressão.
14. Auditoria final.

## PRÉ-CONDIÇÃO PARA DESENHAR OU EMITIR DOCUMENTO
Somente desenhar ou emitir depois de inventário de fontes, entendimento documental, matriz de ativos, dicionário de funções, matriz de sinais, intertravamentos, redundância quando aplicável, validação do template mestre, paginação final consistente e pipeline sem finding crítico.

## REGRA CONTRA SIMPLIFICAÇÃO INDEVIDA
CI, Copilot, scripts, agentes, prompts auxiliares e sugestões automáticas não podem substituir o conteúdo de engenharia por texto genérico de software apenas para satisfazer testes. O contrato do CI deve validar a engenharia; nunca redefini-la.
