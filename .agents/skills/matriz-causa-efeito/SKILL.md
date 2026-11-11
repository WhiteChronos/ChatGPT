---
name: matriz-causa-efeito
description: Elaborar, revisar e auditar Matrizes de Causa e Efeito (MCE) de automação industrial a partir de P&IDs, memoriais, narrativas, listas de I/O, filosofias de controle, HAZOP/LOPA/SRS e Excel mestre aprovado. Usar para mapear causas, efeitos, intertravamentos, alarmes, trips, votações, reset e bypass com evidências por TAG e revisão, pesquisar repositórios GitHub auxiliares e orquestrar as Skills MCE do WhiteChronos/ChatGPT. Não usar para engenharia reversa de software nem REA. Bloquear alterações do Excel sem autorização e manter histórico no GitHub.
---


## DEC-MCE-075 — Preparar automaticamente o contrato, sem repetir autorizacao

Ao receber autorizacao de TRABALHO e fontes disponiveis, nao perguntar novamente pela mesma autorizacao. No workspace privado autorizado, invocar o UNICO executor MCE: \`mce_workflow.py init\` e \`mce_workflow.py propose-contract --workspace WORKSPACE --annotation-policy IN_MATRIX --sp-policy UNUSED\` quando o projeto assim determinar (ADM Gamboa). O comando somente le o XLSX e cria \`contract.proposed.json\` com linhas pela coluna H, whitelist C/AR para textos, SP historico para revisao e efeito/X para auditoria; nao altera matriz, contrato oficial ou estado.

A aprovacao de modelo homologado, whitelist, efeito de seguranca, intertravamentos e QA Windows continua humana/tecnica, mas a PREPARACAO da matriz NAO deve ficar travada por uma pergunta repetida, nem pelo trabalho manual de listar centenas de coordenadas. Separar \`PREPARACAO_DOCUMENTAL\` de \`MCE_PRELIMINAR_PARA_REVISAO\` e \`ACEITE_FINAL_VERIFICADO\`; nunca declarar que proposta de contrato e matriz aprovada. Cada X/efeito novo precisa de evidencia e procedimento funcional especifico. Para ADM, observacoes na coluna AR prevalecem sobre orientacoes antigas EXTERNAL_ONLY de outras revisoes. Sempre distinguir copia de trabalho e emissao formal.


## REGRA DE OURO INVIOLAVEL — DEC-MCE-071 (2026-11-10)

**Contrato de entrega fail-closed do MCE.** Pedido de "criar/elaborar/corrigir/entregar a Matriz" = `MCE_XLSX`. O unico arquivo principal e Microsoft Excel `.xlsx` no perfil P09 **efetivamente contratado e homologado** para o projeto (L50, L57 ou outro aprovado). PDF e somente espelho fiel opcional do XLSX; PDF de auditoria, JSON, MD, CSV, planilha generica, template vazio e relatorio de pre-analise nunca substituem a Matriz.

1. **Antes de comecar e antes de responder:** classificar `MCE_XLSX` e conferir baseline por SHA, fontes revisadas, layout contratado, modelo mestre aprovado, lista exata de celulas, autorizacao formal `AUTORIZO_ELABORACAO_MCE`, observacao por causa, efeitos identificados, cada X/ausencia justificado, SP conforme contrato, QA OOXML, Excel Windows e PDF se solicitado. Consulta a fontes privadas somente por acesso autorizado.
2. **Gate faltando = STOP.** Dizer literalmente `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`, identificar bloqueios objetivos e proximo gate; nao anunciar "elaboracao entregue" e nao apresentar PDF/JSON ou o XLSX historico como substituto do arquivo atualizado. Se houver relatorio explicitamente pedido, rotular `AUXILIAR_NAO_E_MATRIZ`, nunca principal.
3. **Gate completo = copia derivada pelo unico executor canonico.** Verificar `FOLHA N`, geometria especifica do modelo homologado, texto, observacoes, X seletivos com evidencia, SP do projeto, formulas/mesclas/estilos, audit OOXML, Excel Windows e equivalencia PDF. Estado final do arquivo: `MCE_PRELIMINAR_PARA_REVISAO`, sem homologacao automatica de engenharia.
4. **Preflight de formato por ferramenta:** antes de declarar MCE entregue, executar no Windows `python systems/mce/scripts/mce_delivery_contract.py --manifest MANIFESTO_PRIVADO.json --root WORKSPACE_PRIVADO`. `FAIL_FORMAT_CONTRACT` e `FAIL_ENGINEERING_GATE` bloqueiam entrega. `PASS_BLOCKED_DECLARED` so confirma que o bloqueio foi comunicado, e `PASS_MCE_DELIVERY_PREFLIGHT_ONLY` nao substitui auditoria independente de engenharia.
5. **Falha de Skill espelhada = STOP:** atualizar `systems/mce/.agents/skills` E `.agents/skills` em mesmo commit. Testar igualdade binaria pelo `systems/mce/scripts/verify_mce_skill_mirrors.py` na CI Windows antes de considerar a mudanca validada.

Esta regra prevalece em novas emissoes sobre exemplos historicos de saida conflitantes, SEM apagar registros anteriores ou inventar logica. CI verde e testes sintéticos nao constituem autorizacao de engenharia. Nao fazer merge, deploy, editar master ou publicar documentos industriais sem autorizacoes proprias.


# Matriz de Causa e Efeito — orquestração MCE independente

**Escopo exclusivo:** `MCE_INDEPENDENTE`. Conduzir apenas elaboração, revisão, consistência, evidências, padronização e fechamento de MCE. Não usar motor, código, banco ou ferramentas REA; não utilizar Desktop Commander.

## Recuperar a fonte de verdade antes de agir

1. Consultar no GitHub `WhiteChronos/ChatGPT` o **HEAD atual** do PR [#118](https://github.com/WhiteChronos/ChatGPT/pull/118), sua CI, revisões e regras. Tratar SHA citado nos documentos como histórico, não como HEAD atual.
2. Ler `systems/mce/AGENTS.md`, `systems/mce/spec/memoria.md`, `systems/mce/docs/EXECUCAO.md`, `systems/mce/docs/GITHUB_MEMORY.md` e o índice [Issue #120](https://github.com/WhiteChronos/ChatGPT/issues/120), incluindo comentários estruturados ainda pendentes de espelhamento. Preservar DEC/PEND e seguir o último estado **comprovado**.
3. Para P&ID digital e integração GitHub, consultar [references/repositorios-github.md](references/repositorios-github.md). Repositórios de pesquisa só ajudam a extrair/conferir topologia e texto; não fornecem lógica operacional aprovada.
4. Carregar/seguir as Skills do mesmo sistema `engenharia-mce-projeto`, `padronizacao-mce` e, no fechamento, `mce-fechamento-operacional`. Não as substituir por um segundo editor de Excel.


## Contrato INVARIAVEL de entrega da Matriz — DEC-MCE-032 (2026-11-10)

**REGRA NAO NEGOCIAVEL:** toda Matriz de Causa e Efeito (MCE) produzida por este sistema e **exclusivamente arquivo Microsoft Excel `.xlsx` no modelo P09 vigente**. O tipo `MCE_XLSX` nunca e substituido por PDF, Markdown, DOCX, CSV, ODS, imagem, quadro em texto ou aplicativo. Esses formatos podem existir apenas como **documentos auxiliares separados**, claramente nomeados RELATORIO ou PENDENCIAS, e nunca ser oferecidos como "a matriz". Uma previa PDF, se solicitada expressamente, e apenas copia para visualizacao, nao o entregavel principal.

**Preflight antes de qualquer resposta "gerar a matriz":**
1. Classificar o pedido como `MCE_XLSX`; consultar o perfil P09 aprovado para o projeto. Para ADM Gamboa: `P09_L50_APROVADO_VISUALMENTE`, abas apenas `FOLHA N`, grade 8:50 (43 causas), efeitos I:AQ (35), Arial 10 titulos / 8 restante, 46 mesclagens, impressao A1:AR50, sem notas nas colunas (EXTERNAL_ONLY).
2. Exigir que o arquivo principal tenha extensao real `.xlsx`, abra como workbook XLSX valido, e mantenha exatamente as abas, estrutura, fontes, bordas, merges e area de impressao do perfil aplicavel. Nao chamar relatorio tabular de matriz.
3. **Se nao houver modelo mestre homologado, contrato de celulas, fontes vinculadas, autorizacao `AUTORIZO_ELABORACAO_MCE`, host Windows e QA exigidos:** aplicar **STOP**. Nao fabricar MCE preenchida, nao transformar PDF/Markdown em "entrega da matriz" e nao encaminhar template P09 vazio como se resolvesse o pedido. Relatorio separado pode explicitar evidencias e bloqueios, mas o item `MCE_XLSX` deve permanecer `NAO_EMITIDO_BLOQUEADO`.
4. Uma matriz aprovada para emissao preliminar deve ser `MCE_PRELIMINAR_PARA_REVISAO.xlsx` (ou numero/revisao documental coerente), criada apenas pelo executor unico, com auditoria OOXML e fonte; nunca por novo editor nao autorizado.
5. **Teste de regressao:** ao pedir "gerar a matriz", qualquer resposta que ofereca **somente** PDF/MD como matriz, qualquer arquivo `.pdf` denominado MCE principal, ou XLSX vazio anunciado como matriz preenchida recebe `FAIL_FORMAT_CONTRACT`. Corrigir antes de entregar. Relatorios/pendencias jamais entram como abas auxiliares do arquivo principal.

Esta decisao nao remove os gates humanos ou exige outros documentos do responsavel quando o conjunto de fontes foi declarado encerrado. Apenas fixa o contrato de formato e de classificacao do entregavel. Consultar Issue #120 e memoria canonica.


## Perfil de legibilidade e paginacao P09 L50 — DEC-MCE-033 / DEC-MCE-034 (2026-11-10)

**Aplicar por padrao quando o projeto selecionar o perfil `P09_L50_APROVADO_VISUALMENTE`**; nao propagar para P09 L57 ou outros modelos sem perfil contratado.

1. Paginar **pela contagem de causas efetivamente preenchidas**, jamais pelo numero de paginas das fontes. Cada aba `FOLHA N` comporta 43 causas nas linhas fisicas 8:50, cabeçalhos 1:7; FOLHA 2 inicia causa 44, FOLHA 3 inicia 87 etc. Não inserir linhas abaixo da 50 e não deixar folhas intermediarias parcialmente vazias.
2. Ajustar altura **de cada linha de causa** pelo maior numero de linhas visuais entre as celulas descritivas B, C e F:G mesclado, considerando quebras explicitas e quebra de linha causada pela largura/fonte. Formula `altura_pt = 20 + 10 * (n_linhas_visuais - 1)`, com n >= 1: 1=20 pt, 2=30 pt, 3=40 pt, 4=50 pt, 5=60 pt etc. Linhas de causa vazias ficam com 20 pt. Nao truncar. Limite Excel 409,5 pt: a partir de 40 linhas visuais, **STOP**, revisar descricao/largura.
3. No perfil de larguras **`P09_L50_20261110`**: B=25, C=56, F=34 (unidades de largura Excel; F:G e mesclada e G original nao e alterada). Nao redimensionar D/E/H, efeitos I:AQ, AR, margens ou cabecalhos. Revisar comprimento dos titulos de efeitos girados e quebra de linha; preferir ajuste da altura de causa a perder o padrao da grade.
4. A contagem de linhas calculada por largura/fonte e **estimativa**, nao prova do layout final do Excel. Registrar `LINHAS_ESTIMADAS` e validar manualmente quando possivel; sem Excel Windows, `QA_VISUAL_WINDOWS=NOT_RUN` e nunca afirmar ausencia de clipping.
5. Manter Arial 10 nos titulos e Arial 8 no restante, 35 efeitos I:AQ, 46 mesclagens por folha, girar texto para cima I5:AQ5 em 90 graus, A1:AR50, bordas thin, AR8:AR50 sem notas, sem novos X ou TAGs. Preservar toda associacao causa/efeito ao repaginar; auditar antes/depois.
6. A progressao de alturas e as larguras sao **politica visual**, nao autorizacao de engenharia. Modelo mestre, fonte, contrato `editable_cells`, `AUTORIZO_ELABORACAO_MCE` e editor unico permanecem condicionantes de uma MCE de projeto homologavel.

**Regressao obrigatoria:** rejeitar altura 10, 25, 35 ou 410 pt; aceitar 20, 30, 40, 50 ... ate 400 pt; rejeitar mudanca de efeitos ou X, colunas fora de B/C/F, mais que 43 causas por folha e quebra da continuacao de H.


## Revisao anti-falso-positivo de altura — DEC-MCE-035 (2026-11-10)

Ao aplicar o perfil **P09 L50** de DEC-MCE-034, **uma linha VISUAL = 20 pt**, mesmo que um calculo anterior tenha atribuido 30 pt. O texto que cabe realmente numa unica linha na largura vigente nao justifica altura maior. O caso ADM revelou 34 falsas quebras (30 pt) porque o algoritmo de pre-visualizacao subtraiu margem arbitraria de 18 pixels e mediu Arial 8 pt arredondado para 11 px, em vez de calcular o tamanho a 8 pt (aprox. 10,67 px para 96 DPI).

**Postflight visual obrigatorio para candidatos documentais:**
1. Para cada causa, conferir B, C e F:G mesclado. Medir a largura de coluna **a partir do XLSX** com a fonte e tamanho efetivos, quebras `\\n` e `wrap_text`; nao somar margem arbitraria ao calculo, nao assumir coluna F sozinha quando estiver mesclada com G. A conversao caractere→pixel e a fonte substituta devem ser registradas como **estimativa**.
2. Se as tres descricoes ocupam uma linha visual, altura **20 pt**, independentemente de altura anterior de 30 pt. Duas linhas = 30, tres = 40 etc. Nao inferir a contagem apenas pelo numero de caracteres; texto perto do limite de coluna requer inspeção ampliada e `QA_VISUAL_WINDOWS=NOT_RUN` se nao houver Excel Windows.
3. Examinar TODAS as abas `FOLHA N` e alturas 8:50; identificar explicitamente linhas de 30+ pt cujo texto ocupa so uma linha. Emitir arquivo XLSX derivado corrigindo **somente altura de linha** quando a tarefa for auditoria de altura, sem reformular conteudo, largura, formulas, cabecalhos, merges, fontes, TAGs ou X.
4. Exigir auditoria independente de valores, marcas X, mesclas, colunas, area de impressao, fontes e integridade ZIP antes/depois. Nao declarar que um agente/subagente real fez a revisao sem spawn, ID, status e resultado verificados.

Esta verificacao corrige estimativa tipografica de candidata **NAO HOMOLOGADA**, nao altera a obrigatoriedade de aprovacao de engenharia, editor unico/whitelist para alteracoes operacionais nem permite afirmar um QA Excel Windows nao executado.


## DEC-MCE-037: largura de COLUNA 2, nao borda 2 (2026-11-10)

O usuario corrigiu a interpretacao da imagem da grade: **tamanho 2 significa largura das colunas na barra superior A, B ... AR**. DEC-MCE-036, que determinou bordas `medium`, foi REVOGADA por erro de entendimento. Voltar as **bordas originais `thin`**, sem mudar espessura, inserir ou remover divisorias.

- Pedido literal: aplicar `width=2.0` para as **44 colunas A:AR de cada aba FOLHA N**. O Excel aplica largura a coluna inteira, nao apenas nas primeiras linhas. Isso estreita tambem B, C e F, prejudicando a legibilidade dos textos; registrar a limitacao sem prometer layout legivel. Perfil contratual opcional: `column_width_profile=P09_L50_ALL_COLUMNS_2`.
- Variante separada para legibilidade, caso aceita pelo responsavel: **somente I:AQ=2** (35 colunas dos efeitos), preservando B=25, C=56, F=34 e as demais larguras de origem; nao confundir com o pedido literal A:AR.
- Revisao visual: editar apenas larguras solicitadas em copia XLSX derivada; auditar valores, TAGs, X, bordas thin, 46 mesclas/aba, alturas, fontes, impressao A1:AR50, 43 causas/folha e 35 efeitos. Nao promover candidato documental a matriz homologada, nao mudar o modelo mestre nem dispensar gates de engenharia.


## DEC-MCE-038 — Largura G:AR = 2 e consistencia de causa->efeito (2026-11-10)

**Instrucao expressa e vigente do responsavel:** na MCE **P09 L50**, colunas **A:F mantem exatamente as larguras da copia de origem**, e **G:AR (38 colunas, incluindo H e as 35 I:AQ dos efeitos) tem `width=2.0`** em todas as `FOLHA N`. Bordas finas originais `thin` nao devem mudar. Este perfil `P09_L50_G_AR_2` **substitui a preferencia geral A:AR=2 da DEC-MCE-037 para o ADM**; nao alterar os perfis L57 nem modelos mestres sem aprovacao. A largura Excel vale para a coluna inteira, nao apenas para o cabecalho.

**Gate obrigatorio de cobertura funcional da grade:** se a coluna C (ou B/F) indicar uma causa/condicao preenchida, a linha deve ter **pelo menos um X vinculado a titulo de efeito existente na linha 5**. Linha com zero X nao pode ser apresentada como causa valida. Equipamento, switch, painel, UTR, instrumento passivo, interface externa ou divergencia documental **nao deve ganhar X inventado** para passar no gate. Esses itens sao registrados em **relatorio externo de pendencias/rastreabilidade**, sem aba auxiliar na MCE, ate que sua relacao de efeito tenha evidencia documental e revisao da engenharia. Distinguir monitoramento e indicacao de trip e comando; um X de aquisicao pode ser observacao, nao acao de seguranca.

**Reprocessamento sequencial:** compactar somente linhas com efeitos documentais, mantendo ordem relativa, limite de **43 causas por folha (linhas 8:50)**, ate 35 efeitos I:AQ, remapeando cada X pelo **texto completo do efeito na linha 5** (nunca copiar coluna I: AQ cegamente entre folhas com cabecalhos distintos). Validar 46 mesclagens, rotacao 90, Arial 10/8, alturas 20/30/40+, bordas finas, A1:AR50 e todas as larguras. Nao deixar folhas intermediarias parcialmente vazias; ultima pode ficar parcialmente vazia sem numero H fantasma. Nunca inserir X novo por inferencia.

**Historico de incidente (apenas ADM, nao contagens globais):** 218 registros e 175 X no XLSX anterior, sendo 76 registros **sem X**. Gerado candidato revisado com 142 causas/condicoes com X em 4 folhas (43/43/43/13), mantendo os 175 vinculos; os 76 sem X foram conservados em XLSX externo de pendencias e suas TAGs. `NAO_HOMOLOGADO`, Excel Windows/host `NOT_RUN`, DataCenter real `COPY_PENDING`, gates humanos originais preservados.

**Validador canonico:** `column_width_profile=P09_L50_G_AR_2` verifica G:AR=2 e contrato de campos descritivos A:F por diff contra copia aprovada; `require_effect_per_cause=true` verifica X+cabecalho por causa preenchida e paginacao continua, tolerando H vazio em linhas realmente vazias da ultima folha. Nenhuma dessas verificacoes equivale a aprovacao de intertravamento.


## DEC-MCE-039 — largura G:AR 2,00 gravada SEM faixas sobrepostas (2026-11-10)

O usuário constatou **largura aparente 1,29**, embora a MCE ADM anterior declarasse `width=2`. Auditoria de OOXML revelou colunas definidas com faixas sobrepostas: por exemplo, a entrada da coluna I abrangia **I:AL (min=9,max=38)** enquanto J..AL também possuíam elementos `<col>` próprios; AN abrangia AN:AQ com outras entradas individuais. Isso é inválido para uma grade determinística e pode gerar divergências de largura entre editores.

**Gate de normalização obrigatória para MCE P09 L50:**
- Em cada `FOLHA N`, gravar **exatamente uma definição física por coluna de G a AR** no `xl/worksheets/sheetN.xml`, com `min=max` igual ao índice Excel real, `width="2"` e `customWidth="1"`. Proibir qualquer faixa adicional que intercepte G:AR; não basta que `openpyxl.column_dimensions['I'].width == 2`.
- Conservar todas as colunas A:F, bordas originais `thin`, mesclas, fonte, alturas, impressão e valores/X. Colunas fora de AR não são alteradas.
- Perfil canônico de validação `column_width_profile=P09_L50_G_AR_2` deve **rejeitar sobreposições**, agrupamentos, dimensões ausentes e larguras diferentes de **2,00**, inclusive 1,29. Acrescentar testes sintéticos de sobreposição `I:AL` e de largura 1,29; a checagem precisa alcançar XML e não somente a largura reportada pelo wrapper.
- Nenhum editor deve afirmar que um viewer exibirá exatamente 2,00 sem abrir nesse aplicativo. `QA_EXCEL_NATIVO=NOT_RUN` quando só OOXML/openpyxl foram usados.
- Esta correção é visual e não altera os 142 registros com X, 175 cruzamentos, 4 folhas e 76 itens pendentes externos da MCE ADM. Preservar gates de engenharia, não instalar no Windows nem enviar documentos industriais ao GitHub.


## DEC-MCE-040 — Arena/Superpowers: 6 folhas e largura EXIBIDA 2,00 (2026-11-10)

**Origem do erro 4 vs 6:** no ADM a MCE documental possuia 218 registros, dos quais 142 com X e 76 sem X (inventario/pendencias). Um refatoramento REMOVEU os 76 da grade e paginou 142/43 em 4 folhas sem aprovacao. **Correcao de formatacao nao pode alterar a cardinalidade de causas ou numero de abas**. Com 218 registros, manter **6 folhas** (43/43/43/43/43/3), efeitos X existentes 175, folhas 8:50, pendencias 76 relatadas EXTERNAMENTE, sem inventar X, intertravamentos ou comandos. Se for solicitada matriz funcional somente com causas vinculadas, isso e outra revisao de engenharia, nao revisao visual, e exige decisao humana especifica.

**Origem matematica do 1,29:** pela especificacao OOXML da Microsoft (font de referencia com Maximum Digit Width `MDW=7` pixels e padding 5), `<col width="2"/>` produz aproximadamente **14 px** e aparece como **1,29 caracteres** na interface Excel. Para o usuário ver **2,00**, o valor fisico é `width="2.7109375"` (19px = 2.00 caracteres exibidos no Excel com MDW7). A decisao anterior DEC-MCE-039 que exigia `width="2"` em G:AR era INSUFICIENTE PARA O PEDIDO DE TELA. Perfil novo `column_width_profile=P09_L50_G_AR_DISPLAY_2` exige em cada aba **G:AR** (38 colunas) com `min=max=N, width=2.7109375, customWidth=1`, sem ranges sobrepostos, e **A:F inalteradas**. Borda fina `thin` de origem. Nao chamar o atributo interno `width=2.71` de largura 2.71 na interface: a exibicao correta alvo e **2,00**. Outros aplicativos/fontes/zoom exigem conferencia visual separada e nao podem ser alegados aprovados apenas por OOXML.

**Alturas:** per-causa avaliar as quebras visuais em B/C/F:G a Arial 8pt usando larguras REAIS de A:F, contando quebras explicitas e possivel wrap. `altura=20+10*(n_linhas-1)` pt; 1 linha=20, 2=30, 3=40, etc. O primeiro algoritmo que atribuiu 30 sem evidência inflou alturas; a correção seguinte que forçou tudo a 20 gerou texto quebrado. Para o exemplo documental ADM, medicao conservadora (Arimo metrico Arial com margen de 7px) indicou 12 linhas de 30 pt, concentradas FOLHA 2 (8) e FOLHA 3 (4). Essa é **estimativa**; Microsoft Excel nativo NAO foi executado e a prova definitiva de wrap permanece aberta.

**Gate de regressao independente:** reconstruir o workbook de 6 folhas da ultima copia **6-folhas** preexistente, nunca a variante 4-folhas; comparar 218 registros, 175 X e cada associação por titulo de efeito, 46 mesclas/aba, Arial10/8, area A1:AR50, border thin e hashes. Editar somente `<cols>` e alturas `row@ht` em copia derivada. Usar 4 estrategias GitHub Arena, Superpowers inline quando plugin oficial ou agentes verdadeiros nao estiverem expostos; nao chamar personas ou analises sequenciais de subagentes independentes.

**Fonte tecnica largura:** https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.column?view=openxml-3.0.1 . Estado de engenharia sempre `PRELIMINAR_NAO_HOMOLOGADO`, DataCenter `COPY_PENDING` ate recibo fisico, sem publicar XLSX industrial.


## DEC-MCE-041 — Excecao da coluna AR: exibida 96,00; G:AQ = 2,00 (2026-11-10)

**Retificacao expressa da DEC-MCE-040:** o responsavel confirmou que as colunas **G ate AQ**, inclusive H, devem ter **largura exibida 2,00**, mas **AR (Observacao) deve ter largura exibida 96,00**, e **nao 2,00**. Preservar as larguras A:F. Esta e a configuracao vigente da copia documental ADM P09 L50 de 6 abas.

- Para a fonte Normal com Maximum Digit Width (MDW) de 7 px, o perfil `P09_L50_G_AQ_DISPLAY_2_AR_96` exige armazenar em cada `FOLHA N`: **G:AQ = OOXML width=2.7109375** (valor exibido 2,00) e **AR = OOXML width=96.7109375** (valor exibido 96,00). `width=96` no XML nao equivale automaticamente a 96,00 na interface Excel. Valores dependentes do MDW/font e precisam de QA no aplicativo; sem Excel nativo, `QA_EXCEL_WINDOWS=NOT_RUN`.
- Uma unica definicao `<col min=N max=N>` por coluna G:AR, `customWidth=1`, sem sobreposicoes ou dimensoes implícitas. Validar G:AQ (N=7..43) e AR (N=44) separadamente; os perfis G:AR=2 historicos não representam mais o solicitado para ADM.
- **Ajuste estritamente visual:** partir da ultima matriz de **6 abas, 218 registros, 175 X**, preservar os 76 registros sem X como pendencias documentais, sem adicionar X, sem alterar a cardinalidade de causas, alturas, fontes, bordas thin, mesclas 46/aba, impressao A1:AR50 ou qualquer valor. O XLSX de 4 abas nao e baseline de formatacao.
- A auditoria deve comparar os demais elementos e partes do pacote OOXML byte-semanticamente antes/depois, com unica diferenca no atributo `width` de AR em cada aba. Nenhuma automacao no Windows nem homologacao de engenharia decorre desta mudanca.


## DEC-MCE-042 — SP somente com percentual no ADM, sem sufixo LIE (2026-11-10)

Na **MCE ADM Gamboa P09 L50**, a coluna `D` titulada **SP** (setpoint) deve apresentar **somente o valor percentual**, por exemplo `10%` e `20%`, **nunca `10% LIE` nem `20% LIE` no campo SP**. A grandeza `% LIE` pode e deve permanecer explicitada na **descricao tecnica da causa** (coluna C), quando documentada. Isso e uma **regra de apresentacao**, nao altera o limite ou unidade fisica de deteccao.

- Converter **apenas** SPs textuais ja documentados no formato `<numero>% LIE` para `<numero>%`, mantendo cada numero e sinal; nao aplicar se percentual for desconhecido, nao converter ppm ou outras unidades automaticamente, nem preencher SP vazio.
- Na copia documental ADM de 6 folhas, ocorrencias aprovadas para correcao estritamente visual: `FOLHA 1!D22` `10% LIE`→`10%`, `FOLHA 1!D23` `20% LIE`→`20%`. Nao remover `LIE` de `C22`/`C23`, que identificam a condicao tecnica.
- Controle de regressao: auditar toda coluna SP `D8:D50` em todas as folhas; nenhuma celula SP pode conservar a cadeia `LIE` nesse perfil. Confirmar diferenca de valores limitada a D22 e D23; mesmos 6 separadores de folha, 218 registros, 175 X, larguras G:AQ exibidas 2 e AR exibida 96, heights, bordas e demais componentes OOXML sem alteracao.
- Preservar status `PRELIMINAR_NAO_HOMOLOGADA`: edicao de formatacao nao concede `AUTORIZO_ELABORACAO_MCE` nem aprova riscos de incendio/explosao ou sua implementacao.

## Fase 1 — identificar, analisar e PARAR antes de escrever Excel

1. Identificar explicitamente projeto, **SS**, sistema, documento, revisão e disciplina. Inventariar **modelo mestre real** e fontes (P&ID, lista I/O, narrativa, memorial, filosofia de controle, SRS/HAZOP/LOPA quando aplicável) com SHA-256 e localização verificável; marcar ausência como `NAO_DOCUMENTADO`.
2. Distinguir topologia física em P&ID de lógica funcional: **P&ID e OCR nunca bastam para inferir trip, setpoint, votação, reset ou SIF**. Só converter relação causa→efeito quando narrativa/filosofia/SRS e sua revisão oferecerem evidência literal. Mapear TAG, estado, sequência e consequência em [references/metodo-e-saidas.md](references/metodo-e-saidas.md).
3. Classificar cada afirmação como `DOCUMENTADO`, `INFERIDO_PARA_REVISAO` ou `NAO_DOCUMENTADO`; registrar documento, SHA-256, revisão, folha/página, transcrição curta ou referência e disciplina responsável. Não elevar candidato derivado de OCR/grafo a fato ou comando de segurança.
4. Se houver executor Python autorizado com fontes locais, seguir `systems/mce/docs/EXECUCAO.md` e usar **somente** o executor canônico `systems/mce/.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py` (`init`, `understand`). Se não houver acesso ao executor, elaborar só relatório documental e informar `NOT_RUN` para comandos.
5. Apresentar inventário, relatório de entendimento, causas/efeitos candidatos e pendências; **parar em `ANALISADO_AGUARDANDO_DECISAO`** antes de alterar qualquer matriz. Não simular autorização.


### Exibição sem notas em coluna (opcional)
Quando a entrega pedir uma matriz limpa, manter a geometria e o cabeçalho da coluna AR, mas deixar AR8:AR50 vazio e não anexar notas/comentários a células. Preservar causas, TAGs, efeitos, X/I, impressão, mesclas e fontes. Registrar evidências em inventário privado separado; não publicar documentos industriais. Para o perfil L50 de modelo aprovado, indicar annotation_policy=EXTERNAL_ONLY no contrato para validação antes da autorização. Não impor este parâmetro a outros projetos sem pedido expresso.

## Perfil de paginação P09 com grade até a linha 50 (decisão visual por documento)

- A linha 50 refere-se à linha física do Excel; o cabeçalho ocupa as linhas 1:7 e cada folha comporta 43 posições de causa nas linhas 8:50, não 50 causas ou 50 efeitos.
- A numeração de vagas na coluna H progride 1..43, 44..86, 87..129, inclusive quando a última folha tem vagas sem descrição. Abas sequenciais FOLHA 1, FOLHA 2 etc.
- São 35 efeitos por folha em I:AQ, descrições giradas para cima em I5:AQ5 (90 graus), área de impressão A1:AR50, 46 mesclagens no layout derivado, Arial 10 pt nos títulos, Arial 8 pt no restante, alturas 20/30 pt e bordas thin.
- Identificador opcional no contrato: P09_L50_APROVADO_VISUALMENTE. O perfil P09 original L57 permanece intacto e não é alterado automaticamente em outros projetos.
- Em revisão reconstruída sem herança, não transportar TAGs, causas, efeitos ou X/I da revisão antiga; trabalhar somente com as fontes documentais atuais verificadas.
- O executor canônico confere o perfil declarado contra o próprio modelo antes de autorizar. Layout aceito visualmente não homologa engenharia nem dispensa modelo mestre aprovado, contrato de células, autorização humana, QA Excel Windows e auditoria OOXML.

## Fase 2 — elaborar SOMENTE após gate humano

1. Exigir modelo XLSX mestre **homologado e rastreado** (o exemplo local não é oficial), contrato `contract.json` aprovado com `editable_cells` exatas, `max_causes_per_sheet=50` (ou menos pela área real), projeto e SS documentados, fontes identificadas, e autorização humana verificável `AUTORIZO_ELABORACAO_MCE` vinculada ao baseline e aos hashes das fontes.
2. Apenas nesse estado, usar `authorize`, `apply --changes alteracoes.json` e `audit` do executor **canônico** em uma **cópia derivada** do `.xlsx`; editar somente **texto autorizado** e destacar apenas células realmente alteradas em cinza `D9D9D9`. Não alterar cabeçalhos, fórmulas, estilos funcionais, mesclas, imagens, abas, layout ou áreas de impressão.
3. Validar e rastrear lógica **AND/OR, m-de-n, estados seguros, falha, bypass, startup/shutdown, reset, temporização e implementação PLC/SIS/F&G** apenas quando fontes contratuais determinarem seu valor/comportamento; caso contrário manter `PENDENTE`.
4. Auditar OOXML, SHA de entrada, diff de células e permissões; emitir somente `MCE_PRELIMINAR_PARA_REVISAO`. Exigir revisão de Processo, Instrumentação, Automação, Operação e Segurança conforme escopo, sem homologar FAT/SAT por teste sintético.

## Responder e guardar continuidade

Usar [references/metodo-e-saidas.md](references/metodo-e-saidas.md) para os formatos de inventário, rastreabilidade, pendências e gates. Escrever com termos de engenharia; explicitar o que é fato versus pendência, fontes, revisão e status.

Se houver atualização de código/Skill autorizada, registrar no **mesmo commit** um evento datado em `systems/mce/spec/memoria.md`, atualizar ambos os espelhos da Skill e executar as verificações da CI MCE. Decisões publicáveis podem ser registradas no Issue #120 pelo conector GitHub **quando disponível e autorizado**; nunca enviar documentos confidenciais, Excel mestre, banco SQL privado ou transcrição integral de chat. A Skill e o GitHub não capturam mensagens automaticamente.

**STOP obrigatório:** ausência de fontes/SS, divergência de revisões, autorização, contrato ou modelo oficial, impacto funcional sem evidência, conflito de lógica de segurança ou tentativa de escrever fora de whitelist. Nunca fazer merge/deploy ou declarar `PRODUCTION_COMPLETE=YES` sem gates externos e aceite humano comprovado.

## Ferramenta executável de pré-análise — DataCenter e DataSheet MCE

**Uma única Skill orquestradora**, utilizando as três Skills de engenharia/padronização/fechamento e o **único DataCenter SQLite do MCE**. Não criar banco independente da ferramenta. Consultar [references/operacao-ferramenta.md](references/operacao-ferramenta.md) e `systems/mce/docs/MATRIZ_CAUSA_EFEITO_TOOL.md` antes de executar.

1. Para comparar as três interfaces GitHub já documentadas (`azure`, `houston`, `industrial`), preparar um `workspace` **já inventariado** pelo MCE com modelo `.xlsx` e fontes registradas por SHA. Entradas: exportações do próprio usuário, jamais clonagem de código de terceiros. O terceiro repositório `Industrial-Control` é apenas benchmark didático e não uma fonte funcional de segurança do projeto.
2. Preparar `manifest.json` com `schema=mce.matriz-tool.manifest.v1`, `run_id` único, lista `sources[]` (um registro por adaptador contendo `source_name`, `document`, `revision`, `location`) e `io_source_name` opcional. **Nenhum** dado industrial entra no GitHub.
3. Em host autorizado com checkout MCE e SQLite privado previamente inicializado, executar o script canônico **sem criar executor duplicado**:

   ```powershell
python .\systems\mce\scripts\matriz_causa_efeito_tool.py plan --workspace "C:\MCE_DADOS\PROJETO" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
python .\systems\mce\scripts\matriz_causa_efeito_tool.py run --workspace "C:\MCE_DADOS\PROJETO" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
```

4. Confirmar `PRE_ANALISE_PENDENTE_REVISAO`, `human_review_required=true`, `cause_effect_relations_approved=0` no `MCE_<run_id>_DATASHEET.json` e evento `MCE_TOOL_MATRIZ_CAUSA_EFEITO` no SQLite MCE. O DataSheet segue `systems/mce/datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json` e é privado. A memória pública do MCE continua `systems/mce/spec/memoria.md` + GitHub Issue #120.
5. Exigir uma `pid_integration_review[]` humana para **cada** derivado no `analise.json`; acionar o executor anterior `mce_workflow.py understand` para chegar a `ANALISADO_AGUARDANDO_DECISAO`. Nem o DataSheet nem o SQLite podem emitir `AUTORIZO_ELABORACAO_MCE` ou liberar edição no Excel.
6. Validação exclusiva em Windows, PowerShell e Python 3.12, por `.github/workflows/mce-matriz-tool-qa.yml` e demais workflows MCE. Não executar ou testar em Linux/WSL. Os testes usam somente fontes sintéticas. **Nao usar** o sistema REA, execução de código de repositórios de terceiros ou entrada automática do chat. **Sem merge/deploy** e `PRODUCTION_COMPLETE=YES` sem aceite real.

Se o ChatGPT Web não expuser execução local, limitar-se à análise documental e apresentar **NOT_RUN** para esses comandos. A presença da Skill instalada não comprova o runtime do script ou o modelo mestre aprovado.

## Windows como unica plataforma de desenvolvimento

- Criar, testar e operar `matriz-causa-efeito` **apenas em Windows nativo** com PowerShell e Python 3.12+. Não usar Linux, WSL, Bash nem contêiner Linux. A CLI recusa sistema operacional não Windows.
- Uma só Skill MCE coordena `engenharia-mce-projeto`, `padronizacao-mce` e `mce-fechamento-operacional`; não cria banco, executor OOXML nem serviço paralelo.
- Usar os três repositórios GitHub como contratos **auxiliares** de exportação, por adaptadores locais: Azure-Samples (grafo P&ID), S-Houston (OCR CSV) e ZzzJjt/Industrial-Control (benchmark didático, sem validade de trip ou SIF). Não executar fontes de terceiros.
- Os workflows **exclusivos do MCE** usam `windows-latest`. Workflows globais compartilhados permanecem sob governança própria e não são modificados por esta Skill.
- O workflow Windows cria o pacote `skill.zip` com `Compress-Archive` e publica o artefato `matriz-causa-efeito-windows-skill`. Instalação real no Codex/ChatGPT Web depende de teste separado.


## Memoria ligada a GitHub, DataCenter e novas conversas

Ao receber **"retomar MCE"** ou iniciar tarefa MCE em outro chat, seguir `systems/mce/docs/RETOMADA_ENTRE_CHATS.md` e consultar primeiro a memoria GitHub, Issue #120, PR #118 com HEAD/CI atual e as Skill/MCE AGENTS. Nao presumir que a versao instalada no ChatGPT Web iguala a do GitHub. Recuperar tambem eventos pendentes no Issue, sem tratar o mesmo ID como prova de semantica igual.

A unica ponte `systems/mce/scripts/mce_context_bridge.py` gera em **Windows nativo** checkpoint `mce.context-handoff.v1` somente com ponteiros GitHub, IDs e SHA-256 do Markdown e, opcionalmente, integridade/hash/contagens do **mesmo** DataCenter SQLite. Sem conexao autorizada, registrar `PRIVATE_NOT_CONNECTED`; nunca transmitir documentos, eventos privados, anexos, banco ou backup ao GitHub.

Evolucao continua **por eventos explicitamente capturados**, nao em segundo plano: decisao publicavel -> Issue #120 pelo GitHub autorizado; mudanca de codigo ou Skill -> `spec/memoria.md` no mesmo commit e CI Windows; evento operacional privado -> ledger SQLite/MCE. Novos fatos corrigem historico por adicao, nao o apagam. Alerta 30/10/2026: `PEND-MCE-014` no Issue e no Markdown têm assuntos divergentes; exigir conciliacao humana. Nao prometer retencao literal de todas as conversas, aprendizagem nativa permanente, autoaprovacao, edicao Excel sem autorizacao ou `PRODUCTION_COMPLETE=YES`.


## Backup obrigatorio de fontes e saidas — DEC-MCE-030

- Recuperar as decisoes canonicas do GitHub, inclusive Issue #120 e memoria.md. Em arquivos efetivamente recebidos no inbox privado, usar o arquivador **canônico existente** \`systems/mce/scripts/mce_document_archive.py\` para conferir hash SHA-256, gerar copia imutavel no vault, recibo por projeto/documento/revisao e evento no mesmo SQLite MCE. Nunca criar editor/banco alternativo nem colocar arquivos de engenharia no GitHub.
- A pasta inbox e o DataCenter devem ser preexistentes, privados, explicita e separadamente autorizados; o script \`scan\` reconcilia entradas e \`watch\` executa varreduras enquanto estiver ativo no Windows nativo. Nao pressupor que o ChatGPT transferiu anexos para o Windows ou ativou watcher. Esse transporte depende de integracao e acesso real.
- No adapter MCP, \`initialize\` precisa arquivar fonte e modelo antes de criar projeto; \`understand\` precisa arquivar arquivos de analise/contrato e \`apply\` arquiva a MCE preliminar. Escrever sem vault/SQLite/espelho configurados deve falhar fechado. Status \`ARCHIVED_VERIFIED\` e \`SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED\` so garantem copia verificada, nao dominio independente, criptografia, retencao, restauracao no host ou aceite de engenharia.
- Para segunda protecao fora do dominio de falha, avaliar Restic (\`restic/restic\`) ou Kopia (\`kopia/kopia\`) mediante decisao do operador; testar backup/snapshot/check/restore em host Windows autorizado com dados privados. \`watchdog\` (\`gorakhargosh/watchdog\`) e somente opcional para eventos de pasta; a varredura periodica corrige eventos perdidos. Nenhuma ferramenta externa e instalada automaticamente pelo ChatGPT.
- Se host/tunel desconectado, arquivo no ChatGPT/Library sem bytes transferidos, caminho nao aprovado ou recibo ausente, marcar \`COPY_PENDING\` e nao declarar que o documento esta arquivado. A permanencia ilimitada nao e comprovavel. Preservar gates humanos da MCE, P09, FAT/SAT, politica Windows-only, originais e assinaturas.

## Auxiliares de arquivo e recuperacao — forks WhiteChronos

Recuperar as tres Skills **somente quando a funcao for pertinente**; estas referencias nao adicionam outro banco, editor ou interface de engenharia:

- `mce-restic-backup`: snapshots criptografados, verificacao, retencao e restore (https://github.com/WhiteChronos/restic, `main`; upstream `restic/restic:master`).
- `mce-kopia-backup`: alternativa de backup com CLI/GUI, jamais requisito cumulativo a Restic (https://github.com/WhiteChronos/kopia, `main`; upstream `kopia/kopia:master`).
- `mce-watchdog-ingest`: eventos do inbox privado; varredura/reconciliacao do arquivador MCE continua obrigatoria (https://github.com/WhiteChronos/watchdog, `main`; upstream `gorakhargosh/watchdog:master`).

**Governanca:** usar `mce_document_archive.py` e `mce_memory.py` como fluxo canonico; so aplicar backup/monitoramento no host Windows conectado mediante autorizacao. Os forks sao referencias de origem, nao instalacoes locais. A inclusao de arquivos no GitHub nao equivale a instalacao da Skill no ChatGPT Web. Os SHAs de fork e upstream precisam ser auditados antes de cada atualizacao. Sem tunel, acesso ao documento, credenciais, RESTORE e dupla verificacao reais: `NOT_RUN` ou `COPY_PENDING`. Nao publicar arquivos industriais.


## Contrato de completude funcional — DEC-MCE-068 (2026-11-10)

**Aplicacao:** toda elaboracao, revisao e emissao de Matriz de Causa e Efeito. A referencia privada de apresentacao registrada por DEC-MCE-066 orienta forma e detalhamento; nao autoriza replicar TAGs, setpoints, logicas ou cruzamentos de outro projeto.

1. **Inventario integral:** para cada causa/linha candidata registrar ID, TAG, descricao da condicao e revisao da fonte. Distinguir EVENTO_CAUSAL, SUPERVISAO_SEM_ATUACAO, INTERFACE e ITEM_FORA_ESCOPO; nunca contar apenas X existentes como prova de completude.
2. **Efeitos completos:** descrever todas as funcoes aplicaveis do projeto, sem preencher artificialmente as posicoes disponiveis; cada efeito deve ter identidade funcional clara, responsavel e evidencia por documento, revisao, folha/pagina e SHA no relatorio PRIVADO.
3. **X seletivo e auditavel:** avaliar para cada linha TODAS as colunas de efeitos aplicaveis. Registrar em relatorio privado a decisao X, NAO_APLICAVEL_COM_JUSTIFICATIVA ou PENDENTE_DE_EVIDENCIA para cada par candidato. Cada X existente requer revalidacao; ausencia de X nao prova ausencia de efeito. Proibido aplicar X em todas as colunas para aparentar completude.
4. **Observacao por causa:** cada linha mantida da MCE deve ter observacao especifica, util e documental, descrevendo a atuacao, indicacao ou ausencia justificada de atuacao, fronteira de responsabilidade e condicoes de falha/rearme quando documentadas. Se faltar evidencia, redigir rascunho no relatorio de PENDENCIAS e bloquear a emissao; nunca inventar uma observacao afirmativa para eliminar celulas vazias.
5. **SP condicionado ao contrato:** preservar fisicamente a coluna se pertence ao modelo, mas nao assumir seu preenchimento. Quando o usuario/projeto determinar "SP nao utilizado", manter as celulas SP vazias SOMENTE na copia derivada aprovada; valores tecnicos documentados podem figurar na descricao/observacao conforme convencao aprovada, sem perder unidade fisica. Uma decisao de uso de SP e escopo projeto/revisao, nao padrao universal; nao apagar SP historico sem autorizacao de celula.
6. **Confronto documental:** reconciliar MD, ET, P&ID, arquitetura, lista I/O e manuais aplicaveis para alarme, comandos hardwired, falha de UTR, HVAC, exaustao, UPS, bypass, reset e interface SCADA. Distinguir divergencia de revisoes de requisito valido. Nao promover recomendacoes ou legenda de P&ID a logica de intertravamento.
7. **Preflight antes da emissao:** relatorio privado deve comprovar 100% das linhas revisadas, 100% das observacoes tecnicamente resolvidas, todos os X validados, todos os candidatos a pares causa/efeito classificados, SP conforme contrato e nenhuma divergencia funcional impeditiva. Se nao houver prova, STOP em ANALISADO_AGUARDANDO_DECISAO, sem XLSX/PDF "final".
8. **Entrega controlada:** arquivo principal XLSX P09 vigente em copia derivada, PDF somente representacao fiel se solicitado, QA OOXML/Excel Windows e cotejo entre as paginas. Nao editar mestre nem logica funcional sem modelo homologado, whitelist de celulas, AUTORIZO_ELABORACAO_MCE vinculado a hashes e revisao multidisciplinar.

**Anti-regressao:** o perfil de arquivo historico sem observacoes ou com SP preenchido nao substitui esta verificacao de completude para novas emissoes. Decisoes antigas de layout sao preservadas como historico, e eventual conflito exige revisao explicita do contrato, nao alteracao silenciosa do modelo.



## DEC-MCE-078 — Entregaveis PV e verificador documental

Para revisoes da MESMA matriz, usar CODIGO_DOCUMENTO-REVISAO - PV NN.xlsx, sequencial, sem overwrite, ate fechamento comprovado por aceite externo; proxima matriz inicia PV 01. O arquivo MCE_PRELIMINAR.xlsx do executor e apenas intermediario. Apos auditoria OOXML e gates humanos, usar o sequenciador de copia privada systems/mce/scripts/mce_pv_controller.py e verificar com systems/mce/scripts/mce_delivery_contract.py. O sequenciador nao edita workbook nem concede engenharia aprovada.

Quando disponiveis no catalogo PRIVADO: executar mce-verificacao-cruzamentos -> mce-verificacao-documental -> mce-verificacao-cruzamentos com ledger de handoff. Auditar cada X, relacao condicao/TAG/celula/revisao, repeticoes e nao-aplicabilidade. Nunca preencher colunas por contagem. Nao copiar/publicar codigo privado dessas Skills ao repositorio publico sem autorizacao especifica. Retomar memoria GitHub, checar projeto/SS/fontes e registrar aprendizagem como regra + teste revisado; nenhuma sincronizacao automatica com host ou DataCenter.

**DEC-MCE-079:** o nome entregavel e codigo tecnico completo, inclusive revisao, seguido literalmente de ` - PV NN.xlsx`; a expressao `(PRELIMINAR VERSÃO NN)` e proibida no nome novo. Corrigir erro de nome sem modificar XML, X, estilos, hashes ou incrementar PV. Rastrear nomenclatura no ledger privado sem apagar o registro historico e sem deduzir revisao documental.


## DEC-MCE-080 — Regra de nomeacao em Excel, Word e PDF
Todas as entregas do mesmo sistema seguem CODIGO_DOCUMENTO-REVISAO - PV NN.ext. Extensoes: .xlsx, .docx e .pdf conforme o artefato. NUNCA anexar titulo, comentario ou sufixo depois de PV NN ou antes da extensao, como PERGUNTAS_PENDENCIAS, RELATORIO, QUESTIONARIO ou FINAL. A finalidade fica dentro do documento e em metadados privados. Word do questionario permanece apenas com Localizacao, Folha e Pergunta. A PV do Word avanca conforme solicitacao; Excel e outros documentos nao sao renomeados automaticamente. Testar nome externamente por parse_deliverable_filename antes de entregar. Nenhuma mudanca de nome concede homologacao, modifica cruzamentos X ou dispensa gates de engenharia.
