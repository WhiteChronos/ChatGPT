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


## DEC-MCE-087 — correção da extensão física: folha até linha 47

**Retificação explícita do proprietário com imagem visual:** o trecho de **causas termina na linha 40**, porém a **folha e a área impressa terminam na linha 47**, e nao na 40. Preservar as linhas 41:46 vazias e sem borda de matriz, seguida da faixa horizontal CINZA na linha 47 a partir da coluna B ate AR (na imagem a borda verde e selecao do Excel, nao uma borda funcional a copiar). Politica: `cause_first_row=8`, `cause_last_row=40`, `max_causes_per_sheet=33`, `physical_sheet_last_row=47`, `print_area=A1:AR47`, `blank_tail_rows=41:46`, `footer_band_row=47`, `footer_band_fill_rgb=D9D9D9`, H visual 3,00.

Esta decisao **corrige DEC-MCE-086 somente no termino fisico/area impressa**, sem alterar a capacidade por folha ou o conteudo das causas e X; preservar a referencia L50 existente sem substitui-la em outros projetos. Candidato privado PV 04 derivado foi confrontado em modo somente leitura contra a PV 04 anterior: valores/relacoes nas linhas 8:40 preservados nas 11 folhas; verificar novamente o acabamento visual e a paginacao no Excel Windows nativo antes de aceitar como documento de engenharia. Nao inserir documentos, tags, prints ou SHA privados no repo publico; nao promover como modelo oficial apenas por QA OOXML.


## DEC-MCE-088 — colunas da grade devem continuar ate a linha 47

**Falha de regressao verificada no arquivo derivado, por observacao do proprietario e leitura OOXML:** a DEC-MCE-087 prolongou impressao e faixa cinza para linha 47, mas deixou as celulas A41:AR46 SEM bordas e B47:AR47 SEM bordas verticais. Isso interrompia visualmente a matriz na linha 40. Correcao obrigatoria da variante `P09_L40_H_DISPLAY_3`: **estender toda a topologia das bordas de A41:AR47**, replicando as quatro bordas de cada coluna/celula da linha 40 para as linhas 41:47, com linhas horizontais e verticais continuas, mantendo as convencoes de borda de celula vizinha para colunas combinadas do modelo. Nao exigir `right` em uma celula se o divisor original e definido pelo `left` da seguinte. Bordas `thin` uniformes nos tracos existentes.

As linhas 41:46 sao **vazias em VALOR e sem novas causas, mas NAO sem formatacao nem sem grade**. A linha 47 mantem o preenchimento cinza B:AR (D9D9D9) E as divisorias verticais/horizontais correspondentes; a coluna A continua conforme a topologia da linha 40. Impressao A1:AR47; H exibida 3,00; ultimo item de causa na linha 40 (33 vagas). Nao copiar textos, marcas X, fundo amarelo de causas, formulas ou notas para a extensao. Nao misturar grupos de cabecalhos de efeitos. Preservar 259 X e 218 causas existentes no derivado privado, sem publicar contagens detalhadas, nomes de documentos ou hashes industriais. A versao anterior e original ficam intactos.

**Antirregressao:** checar em TODAS as folhas e em CADA coluna A:AR de 41:47 o valor vazio, a equivalencia do estilo das quatro bordas com a celula correspondente da linha 40, a continuidade visual, a faixa cinza, a area de impressao, a integridade OOXML e igualdade exata de valores de 1:40. Registrar QA de Excel Windows nativo e preview de impressao antes da aceitacao. Este contrato de layout nao autoriza preenchimento funcional ou alteracao do master.
