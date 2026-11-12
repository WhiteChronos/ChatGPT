# DEC-MCE-081 — perfil H=3 e aprendizagem por ciclo MCE

Decisão de 2026-11-11; registro público de processo, sem arquivo ou TAG industrial.

## Largura

Para o perfil P09 L50 selecionado e contratado, a coluna H exibe largura 3.00 no Excel nativo. Na geometria MDW7 adotada, gravar width=3.7109375 em uma definição min=max=8 por folha. Antes, width=2.7109375 correspondia à exibição 2.00. Preservar todas as outras larguras, X, fórmulas, estilos, cabeçalhos e marcadores amarelos. Verificar diferencial ZIP e Excel Windows nativo antes de qualquer aprovação.

Essa largura é uma variante de perfil e não substitui silenciosamente modelos de outros projetos.

## Entregáveis e perguntas

Nome externo: CODIGO-REVISAO - PV NN.xlsx ou .docx; não acrescentar sufixos descritivos. As PV de Excel e Word evoluem independentemente conforme a alteração do respectivo arquivo. Pendências na MCE: amarelo somente, sem comentário. Word de perguntas: apenas Localização, Folha e Pergunta.

Perguntas claras, com condição observada e resposta funcional necessária à matriz. Consolidar perguntas repetidas por mesma decisão, preservando identificação de todas as células e TAGs envolvidas. Não perguntar o que já esteja comprovado por ET/MD/Arquitetura; manter dúvidas não documentadas como pendência. Não inventar um X ou um intertravamento.

## Aprendizado contínuo no fluxo

Para cada NOVA execução explicitamente solicitada do workflow MCE: comparar resultados, detectar defeito verificável, documentar evidência, propor correção, executar testes sintéticos, obter revisão humana e registrar decisão. A política está habilitada no workflow; não é serviço permanente rodando em segundo plano, não muda pesos do modelo nem autoriza edições autônomas.

DataCenter: somente o host privado real, quando conectado e verificado, pode confirmar ingestão/restauração. Até lá, conservar checkpoint privado e metadados públicos sanitizados em GitHub, sem declarar DATACENTER_OPERATIONAL.

## Gate

A matriz e seu modelo mestre continuam sob autorizações de engenharia e contrato de edição; a QA do formato não homologa lógica funcional.


## DEC-MCE-086 — variante P09 L40 / H visual 3,00 (por pedido de projeto)

O proprietario solicitou corrigir o layout da matriz para **terminar fisicamente na linha 40**, nao na 50, com causas nas linhas 8:40 (33 vagas/folha), area de impressao A1:AR40 e coluna H visual 3,00 (OOXML width=3.7109375 no perfil MDW7). O perfil legado P09 L50 permanece disponivel para outros projetos e nao deve ser alterado silenciosamente. O usuario enviou uma referencia visual e o modelo real de PV anterior foi verificado em contexto privado; esta memoria publica **nao contem arquivos, TAGs, hashes nem trechos industriais**.

**REGRA CRITICA DE REPAGINACAO:** nao usar `ceil(total_de_causas/33)` para misturar grupos com cabecalhos de efeitos diferentes. Cada grupo de efeitos original deve manter seu conjunto de colunas/titulos e seus X sem remapeamento funcional. Dividir uma folha cheia gera folhas de continuacao com o MESMO cabecalho daquele grupo. Preservar integralmente causas, linhas, sequencia, observacoes, rotulos e X por identidade, com manifesto privado de origem/destino e diff de invariantes; sem criar X ou aprovar logica. Emissao da PV seguinte e apenas **candidato derivado para revisao do layout** ate Excel Windows nativo, QA de impressao, contrato/revisao de engenharia e aceite.

Requisitos verificaveis: todas as folhas terminam em linha 40; os 35 slots de efeito I:AQ e suas descricoes originais ficam inalterados em cada grupo; H visual=3,00; nao ha conteudo alem da linha 40; print_area=A1:AR40; X historicos e causas devem ser preservados em igualdade exata. O agente de layout nao pode diminuir folhas por renomear ou misturar grupos de efeitos. `PRODUCTION_COMPLETE=NO` sem aceite real.
