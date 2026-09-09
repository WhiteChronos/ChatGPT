# LESSON — Dúvidas devem ser sanadas antes da elaboração

Data: 2026-09-09
Categoria: REGRESSION
Status: ACTIVE

## Ocorrência

Durante a elaboração de uma planilha de verificação, questões ainda não conclusivas foram inseridas na própria planilha como `DÚVIDA`/pontos a confirmar. Algumas também apareceram destacadas em vermelho junto com erros confirmados.

## Falha conceitual

A camada interna de raciocínio e esclarecimento foi misturada com a camada de emissão. Isso obrigou o usuário a corrigir perguntas dentro de um documento que deveria conter somente objetivos formais e erros já demonstrados.

## Regra preventiva

- Toda dúvida é interna ao pré-flight.
- Antes de perguntar, tentar resolver a questão usando todos os documentos, cruzamentos e memória técnica disponível.
- Se a evidência continuar insuficiente, interromper a elaboração e perguntar ao solicitante.
- Enquanto houver pergunta aberta, não gerar Excel, Word, PDF, Power BI ou pacote de emissão.
- Após a resposta, converter a dúvida em `CONFIRMED_ERROR`, `DISMISSED` ou `FORMAL_OBJECTIVE`.
- Perguntas, `DÚVIDA`, `A CONFIRMAR` e hipóteses nunca entram na planilha final.
- Uma divergência objetiva entre documentos pode ser apresentada como erro mesmo quando ainda não se sabe qual valor deve prevalecer; a ação é compatibilizar, não perguntar na planilha.
- A resposta que sane a dúvida deve possuir texto de resolução, tipo de resolução, responsável pela resolução e data/hora antes de liberar a emissão.

## Decisões incorporadas desta revisão

- Não inferir existência de pavimento térreo pela convenção de nomenclatura; seguir a definição real do projeto.
- Instrumentos de campo podem utilizar sinais diferentes da rede XYE; isso, isoladamente, não é erro.
- Texto semelhante/copiado não é erro por si só; deve existir incompatibilidade funcional demonstrada.
- ET e FD têm finalidades diferentes e não precisam repetir toda a mesma especificação ou referência comercial.
- Referências comerciais diferentes com `ou similar técnico` não caracterizam erro sem incompatibilidade técnica demonstrada.
- Quando o solicitante define a nomenclatura oficial de um componente, essa nomenclatura passa a ser a referência de compatibilização para aquele projeto.
- Uma UTR pode possuir simultaneamente Ethernet/Modbus TCP e RS-485/Modbus RTU; se o solicitante confirmar as duas interfaces como requisito do projeto, a omissão de uma delas em outro documento do mesmo conjunto é erro de compatibilização.
- Modelos comerciais diferentes para sensor de CO₂ podem estar corretos quando dependem do equipamento existente ou da solução específica do projeto. A diferença de fabricante/modelo, isoladamente, não é erro sem conflito obrigatório de especificação.

## Teste de regressão

`tests/test_comment_control.py` deve garantir:

1. pergunta aberta bloqueia `build_workbook`;
2. nova divergência com marcador `DÚVIDA`, `A CONFIRMAR` ou pergunta é rejeitada;
3. Excel final não contém abas/colunas removidas;
4. artefato só é gerado com zero perguntas abertas;
5. pergunta marcada como resolvida sem texto/tipo/responsável/data continua bloqueada;
6. resposta `DISMISSED` não cria linha exportável;
7. resposta `CONFIRMED_ERROR` cria nova divergência e remove a dúvida do fluxo de emissão.
