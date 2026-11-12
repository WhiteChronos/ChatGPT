## DEC-MCE-088 — CORRECAO: prolongar divisoes das colunas ate a linha 47

Para variante `P09_L40_H_DISPLAY_3`, a area fisica e impressao seguem A1:AR47, mas NAO basta imprimir ate 47 e deixar linhas sem borda: **todas as colunas A:AR e suas divisoes horizontais/verticais devem prolongar-se pelas linhas 41:47**, copiando em cada coluna a topologia de bordas da linha 40. Linhas 41:46 sem texto/X/dados, porem COM grade de bordas `thin`; linha 47 mantem preenchimento cinza B:AR E divisorias de colunas. Verificar limite entre colunas quando divisoria definida pela borda da vizinha (nao impor que ambas tenham right/left). Preservar causas em 8:40, H visual 3,00, headers e X existentes, e perfil L50 historico. QA estatica comparar A41:AR47 celula por celula e Excel Windows verificar visual/impressao. Fonte: `datacenter/MCE_LAYOUT_LEARNING_POLICY.json`, `docs/MCE_LAYOUT_LEARNING_CONTINUITY.md`, DEC-MCE-088. Nao inserir relacao funcional, nao alterar mestre nem declarar homologacao.

## DEC-MCE-087 — imprimir ate linha 47; causas encerram na 40

CORRIGE a interpretacao DEC-MCE-086: para variante `P09_L40_H_DISPLAY_3`, causas seguem em 8:40 (33 slots), mas nao cortar folha em 40. Preservar seis linhas vazias 41:46, faixa cinza na linha 47 entre B:AR, e `print_area=A1:AR47`. H visual=3,00 no perfil MDW7 OOXML=3.7109375; nao desenhar verde de selecao como borda de documento. Retificar apenas o parametro fisico e area impressa, sem alterar X, causas, cabecalhos de efeito ou perfil L50 historico. No arquivo derivado, executar regressao causas/X, estilos, QA OOXML e validacao visual no Excel Windows. Nao editar mestre, inventar logica, publicar documentos privados ou declarar homologacao. Fonte: `datacenter/MCE_LAYOUT_LEARNING_POLICY.json`, `docs/MCE_LAYOUT_LEARNING_CONTINUITY.md`, DEC-MCE-087.

## DEC-MCE-086 — perfil de paginação P09 L40 e largura H 3,00

Quando o projeto selecionar explicitamente `P09_L40_H_DISPLAY_3`, a grade fisica termina na linha 40: causas em 8:40, limite de **33 causas** por folha, `print_area=A1:AR40`, 35 posicoes de efeitos I:AQ e coluna H visivel 3,00 (MDW7 OOXML width 3.7109375). NAO alterar automaticamente a P09 L50 de outros projetos. Ao paginar, preservar cada bloco original de cabecalhos de efeito e seus X: NUNCA redistribuir causas globalmente entre cabecalhos diferentes, nem preencher X por inferencia. Original intacto, derivado em revisao, verificador de causas/X/cabecalhos/OOXML e QA obrigatoria no Excel Windows. A variante nao homologa modelo nem libera edicao funcional sem contrato e aprovacao de engenharia. Referencia: datacenter/MCE_LAYOUT_LEARNING_POLICY.json e docs/MCE_LAYOUT_LEARNING_CONTINUITY.md.

## DEC-MCE-085 — Arquivamento corporativo DISPENSADO para continuidade documental

Nao bloquear o trabalho de leitura, auditoria read-only de X, perguntas Word e cruzamento MD/ET/P&ID/I/O por ausencia de cofre industrial GitHub, branch protection pago, backup cifrado ou DataCenter Windows. O usuario decidiu dispensar esse arquivamento como pre-requisito para o trabalho atual; `datacenter/CHAT_CONTINUITY_CONTRACT.json` explicita `OPTIONAL_NOT_APPLICABLE_FOR_CURRENT_WORKFLOW`. Usar arquivo real privado da Biblioteca autorizada apenas quando os bytes estiverem disponiveis e forem verificados; nunca supor acesso automatico entre chats. A medida NAO dispensa autorizacao para editar MCE, SHA e proveniencia, fontes/revisoes/SS, whitelist, engenharia, QA Excel Windows nem gates de seguranca de codigo. Nao publicar documentos industriais, fazer merge/deploy ou afirmar producao. `MCE_XLSX=NAO_EMITIDO_BLOQUEADO` ate gates reais para nova emissao. Referencias: docs/MCE_CHAT_CONTINUITY.md, memoria DEC-MCE-085.

## DEC-MCE-084 — Retomada obrigatoria de Matriz e perguntas entre chats

Antes de iniciar ou retomar MCE, ler `systems/mce/docs/MCE_CHAT_CONTINUITY.md`, `systems/mce/datacenter/CHAT_CONTINUITY_CONTRACT.json`, `systems/mce/docs/RETOMADA_ENTRE_CHATS.md`, memoria e Issue #120, e consultar HEAD real das PRs. Ultima dupla documental **MCE XLSX PV 03 / DOCX perguntas PV 04** constitui checkpoint de versoes, NAO backup de bytes: nenhum anexo industrial ou SHA privado pode ir ao repositorio publico. Se os bytes nao estiverem acessiveis no contexto privado autorizado, solicitar fonte e bloquear emissao; nunca reconstruir MCE a partir de metadados. Codigo exige agente revisor independente real e CI SHA-scoped; engenharia exige aprovacoes humanas e contrato. Nao fazer merge/deploy automaticamente. `PRODUCTION_COMPLETE=NO`.

## REGRA DE OURO INVIOLAVEL — DEC-MCE-071 (2026-11-10)

**Contrato de entrega fail-closed do MCE.** Pedido de "criar/elaborar/corrigir/entregar a Matriz" = `MCE_XLSX`. O unico arquivo principal e Microsoft Excel `.xlsx` no perfil P09 **efetivamente contratado e homologado** para o projeto (L50, L57 ou outro aprovado). PDF e somente espelho fiel opcional do XLSX; PDF de auditoria, JSON, MD, CSV, planilha generica, template vazio e relatorio de pre-analise nunca substituem a Matriz.

1. **Antes de comecar e antes de responder:** classificar `MCE_XLSX` e conferir baseline por SHA, fontes revisadas, layout contratado, modelo mestre aprovado, lista exata de celulas, autorizacao formal `AUTORIZO_ELABORACAO_MCE`, observacao por causa, efeitos identificados, cada X/ausencia justificado, SP conforme contrato, QA OOXML, Excel Windows e PDF se solicitado. Consulta a fontes privadas somente por acesso autorizado.
2. **Gate faltando = STOP.** Dizer literalmente `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`, identificar bloqueios objetivos e proximo gate; nao anunciar "elaboracao entregue" e nao apresentar PDF/JSON ou o XLSX historico como substituto do arquivo atualizado. Se houver relatorio explicitamente pedido, rotular `AUXILIAR_NAO_E_MATRIZ`, nunca principal.
3. **Gate completo = copia derivada pelo unico executor canonico.** Verificar `FOLHA N`, geometria especifica do modelo homologado, texto, observacoes, X seletivos com evidencia, SP do projeto, formulas/mesclas/estilos, audit OOXML, Excel Windows e equivalencia PDF. Estado final do arquivo: `MCE_PRELIMINAR_PARA_REVISAO`, sem homologacao automatica de engenharia.
4. **Preflight de formato por ferramenta:** antes de declarar MCE entregue, executar no Windows `python systems/mce/scripts/mce_delivery_contract.py --manifest MANIFESTO_PRIVADO.json --root WORKSPACE_PRIVADO`. `FAIL_FORMAT_CONTRACT` e `FAIL_ENGINEERING_GATE` bloqueiam entrega. `PASS_BLOCKED_DECLARED` so confirma que o bloqueio foi comunicado, e `PASS_MCE_DELIVERY_PREFLIGHT_ONLY` nao substitui auditoria independente de engenharia.
5. **Falha de Skill espelhada = STOP:** atualizar `systems/mce/.agents/skills` E `.agents/skills` em mesmo commit. Testar igualdade binaria pelo `systems/mce/scripts/verify_mce_skill_mirrors.py` na CI Windows antes de considerar a mudanca validada.

Esta regra prevalece em novas emissoes sobre exemplos historicos de saida conflitantes, SEM apagar registros anteriores ou inventar logica. CI verde e testes sintéticos nao constituem autorizacao de engenharia. Nao fazer merge, deploy, editar master ou publicar documentos industriais sem autorizacoes proprias.

> **ATUALIZACAO OPERACIONAL 2026-11-10 / GH-01...GH-08:** `WhiteChronos/mce-document-vault` existe e e **privado**. Restauração **sintetica** no runner Windows [42904158777](https://github.com/WhiteChronos/mce-document-vault/actions/runs/42904158777) PASS; prova **sintetica** de escrita com `GITHUB_TOKEN` efemero e job `contents:write` [42906001613](https://github.com/WhiteChronos/mce-document-vault/actions/runs/42906001613) PASS (default do repo continua `read`). O preflight tem modo `--read-only` para atestar **metadados privados** sem extrapolar permissao de escrita. Protecao forcada de branch no GitHub Free privado: BLOCKED (403, requer plano aprovado); copia independente de falha GitHub: BLOCKED; XLSX ADM GAMBOA original: NAO_LOCALIZADO. Nenhum documento industrial foi enviado, nem houve merge/deploy/aceite. [Matriz de gates no cofre privado](https://github.com/WhiteChronos/mce-document-vault/blob/main/docs/MCE_STATUS_RECUPERACAO.md). `PRODUCTION_COMPLETE=NO`.

> **CORRECAO DE CONTEXTO (2026-11-10):** O usuario confirmou que NAO EXISTE DataCenter Windows local MCE instalado. As referencias posteriores a pastas `C:\\MCE_DADOS`, SQLite privado, espelho e tunel MCP sao especificacoes e componentes de codigo legado, NAO evidencias de runtime real. NAO pedir para ligar ou reconectar servidor inexistente, nem declarar persistencia a partir da CI. A arquitetura alvo requisitada e GitHub-only: fonte de codigo publica, cofre documental privado ainda nao acessivel, GitHub Actions `windows-latest` efemero no contexto PRIVADO, com upload autorizado, SHA-256 e restore real. Ver `systems/mce/docs/GITHUB_ONLY_STORAGE.md`, PR #118, Issue #125. Os gates de engenharia, seguranca, autorizacao e protecao do Excel mestre permanecem integrais. `PRODUCTION_COMPLETE=NO` ate validacao real.

# Sistema MCE — regras locais exclusivas

Escopo: sistema de engenharia de Matriz de Causa e Efeito, independente de motor de engenharia reversa, MCP e interface Web.

1. Inventariar modelo mestre XLSX, P&IDs, I/O, narrativas, especificações, SRS e revisões com SHA-256.
2. Identificar Projeto e SS somente quando documentados. Não inferir setpoints, TAGs, trips, votações, alarmes ou SIFs.
3. Apresentar relatório de entendimento e PARAR em `ANALISADO_AGUARDANDO_DECISAO`.
4. Mediante autorização expressa, contrato de células permitido e modelo validado, editar exclusivamente texto documentado em CÓPIA do Excel.
5. Não alterar cabeçalho, estilos, fórmulas, mesclas, imagens, áreas de impressão ou artefatos não autorizados. Sinalizar alterações válidas em cinza `D9D9D9`.
6. No máximo 50 causas por folha (ou menos quando modelo limitar). Auditar OOXML e SHA da fonte e apresentar como preliminar à validação multidisciplinar.
7. Exportações P&ID OCR/grafo são auxiliares e exigem verificação humana por fonte/arquivo/revisão; nunca geram comandos de segurança.
8. Não importar módulos de outros produtos para executar este workflow. Não publicar documentos privados.
 
## Contrato de continuidade documental obrigatório (2026-10-29)

- Antes de planejar, implementar ou revisar este produto, **ler primeiro** `systems/mce/spec/memoria.md` e `systems/mce/docs/DATACENTER_MEMORY.md`, depois consultar o HEAD atual do PR #118, checks e bloqueios.
- Considerar o Markdown **checkpoint histórico** e o GitHub a fonte de verdade de código; banco SQLite separado no host privado não é acessível automaticamente pelo ChatGPT Web.
- Após cada mudança verificada ou decisão nova, acrescentar ao `spec/memoria.md` um evento com data, DEC/PEND estável, SHA, fonte, teste e pendência, preservando entradas anteriores. Nunca apagar decisão para ocultar conflito; registrar substituição justificada.
- Não alegar execução de Codex, Superpowers, MCP ou aceites humanos apenas porque há instrução ou configuração versionada.
- Não colocar segredos, transcrições integrais, documentos industriais, banco SQLite, backups ou DataSheets operacionais neste repositório; não usar a memória do outro sistema como dependência.
- O arquivo é *recuperável por consulta*, não há garantia de memória nativa entre chats nem persistência eterna. Para retomada, consultar o documento diretamente e comparar os fatos com o PR atual.


## Vinculo GitHub da memoria (2026-10-29)

- Indice permanente: https://github.com/WhiteChronos/ChatGPT/issues/120
- Consultar systems/mce/spec/memoria.md e systems/mce/docs/GITHUB_MEMORY.md antes de atuar.
- Alteracoes MCE devem acrescentar registro datado na memoria no mesmo commit. Validacao: .github/workflows/mce-github-memory.yml. Nao contornar falhas da CI.
- A memoria nao captura chats automaticamente; registrar decisoes verificadas no GitHub sem dados confidenciais.


## Vinculo com registro imediato GitHub

- Ler tambem os comentarios do Issue #120 no inicio de cada tarefa, nao apenas memoria.md.
- Quando uma decisao tecnica explicitamente publicavel for estabelecida e o GitHub conectado estiver autorizado, registrar evento estruturado WC_MEMORY_EVENT_V1 no Issue #120 e verificar o URL; nao esperar a proxima conversa.
- Nunca copiar conversas completas, P&IDs, Excel mestre, dados pessoais ou credenciais. Comentarios sao historico, nao aprovacao de engenharia. Se a ferramenta nao estiver disponivel, informar que nao houve gravacao.
- A CI inspeciona todos os commits posteriores ao checkpoint de ativacao, nao somente o HEAD.


## Entrada exclusiva para Matriz de Causa e Efeito (29/10/2026)

- Skill orquestradora: `systems/mce/.agents/skills/matriz-causa-efeito/SKILL.md`, espelhada identicamente em `.agents/skills/matriz-causa-efeito/SKILL.md` para descoberta no Codex/ChatGPT.
- Usar apenas para matriz causa→efeito de automacao industrial. Compor as Skills antigas `engenharia-mce-projeto`, `padronizacao-mce` e `mce-fechamento-operacional`; preservar o editor existente e todos os gates humanos.
- Consultar Issue #120, memoria.md e PR #118 antes de agir; catalogo de repos GitHub externos e pesquisa auxiliar, nao fonte contratual de intertravamentos. Nenhum dado industrial e enviado ao GitHub publico.

## Ferramenta matriz-causa-efeito: memoria e DataCenter do proprio MCE

- Uma unica Skill de entrada `matriz-causa-efeito` utiliza os tres motores de apoio MCE existentes, nao um segundo motor/editor nem outra base SQL.
- Executor de pre-analise `systems/mce/scripts/matriz_causa_efeito_tool.py`, detalhes em `systems/mce/docs/MATRIZ_CAUSA_EFEITO_TOOL.md`, DataSheet sob `datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json`.
- Os tres repositorios GitHub (Azure, Houston, Industrial-Control) sao formatos de exportacao para adaptadores proprios. Nao clonar/executar terceiros nem transformar benchmark/OCR/grafo em comando de seguranca.
- `plan` nao escreve; `run` exige inventario SHA, SQLite existente e devolve estado PRE_ANALISE_PENDENTE_REVISAO, nao autorizacao para Excel. Sem host autorizado: NOT_RUN.


## Restrição Windows-only para a ferramenta (2026-10-29)

- Desenvolver, criar, executar e testar `matriz-causa-efeito` somente em Windows nativo (PowerShell, Python 3.12+). Não usar Linux, WSL ou Bash.
- Todos os cinco workflows específicos MCE devem usar `windows-latest`. Não modificar controles globais compartilhados do GitHub, nem REA.
- Continuam obrigatórios GitHub como fonte de verdade, o banco SQLite MCE, as três Skills auxiliares do MCE, os três adaptadores de exportação GitHub e as autorizações antes de editar Excel mestre.


## Regra de retomada de contexto MCE (2026-10-30)

- Em cada conversa nova de MCE ou comando `retomar MCE`, ler `systems/mce/docs/RETOMADA_ENTRE_CHATS.md`, `spec/memoria.md`, o Issue #120 e o HEAD/CI atuais do PR #118, antes de concluir que algum passo foi feito.
- `scripts/mce_context_bridge.py` roda somente em Windows nativo e produz um checkpoint read-only com referencias GitHub e, quando autorizado, integridade/contagem do unico SQLite; nunca ler automaticamente todos os chats ou exportar eventos/arquivos privados.
- Atualizacao relevante: registrar no Issue #120 ou no `spec/memoria.md` de forma verificavel, obedecendo commit atomicamente versionado e CI; nao converter a existencia da Skill em comprovacao de instalacao atual ou de host.
- `PEND-MCE-014` no Issue #120 e no Markdown tem semanticas distintas: requer conciliacao humana, preservando os dois registros. Nao usar correspondencia de ID como comprovacao de conteudo identico.


## Ingestao e preservacao obrigatoria de documentos no DataCenter (2026-11-10)

- **Requisito de usuario DEC-MCE-030:** todo documento de entrada ou de saida do fluxo MCE com bytes efetivamente recebidos e acesso autorizado deve ser copiado integralmente ao DataCenter **privado e preexistente** antes de ser tratado como fonte arquivada. Inclui PDF, DOCX, XLSX, desenhos CAD, imagens, listas, memoriais, especificacoes, modelos mestres, revisoes e derivados. Uma referencia textual/link ou anexo nao transferido ao host nao prova posse dos bytes.
- A copia preserva o original byte a byte, em diretorio de documentos versionados por sistema/projeto/documento/revisao; calcular SHA-256 do original e da copia, comparar digests e tamanho, registrar manifest e evento no **unico** SQLite MCE; manter originais imutaveis, sem sobrescrita de revisoes nem edicao dos arquivos de origem. Mesmo nome com conteudo diferente gera nova versao; mesmo SHA repetido e idempotente, respeitando escopo e controle de acesso.
- **Gate antes de processar:** exigir `ARCHIVED_VERIFIED` com recibo de integridade. Se DataCenter/host/tunel ou bytes da origem indisponiveis, marcar `COPY_PENDING`/`HOST_UNAVAILABLE`, informar o usuario e bloquear afirmacoes de backup concluido ou emissao que dependa das fontes; nao copiar silenciosamente para GitHub ou criar SQLite alternativo.
- A copia de ingesta nao substitui backup: manter segunda copia independente, protecao contra exclusao, criptografia/ACL, retencao versionada, verificação periodica e teste de restauracao. Nunca prometer perda zero ou captura automatica do ChatGPT entre conversas sem integracao verificada.
- Esta regra e requisito documentado e pendencia de integracao; por si so nao instala um watcher, nao transfere anexos da interface e nao prova execucao no Windows. Ver `docs/DATACENTER_MEMORY.md` e DEC-MCE-030. Nao alterar gate de elaboracao `AUTORIZO_ELABORACAO_MCE`, whitelist, ou exclusividade Windows.


## Gate permanente de formato da Matriz — DEC-MCE-032 (2026-11-10)
- Ao pedido de "gerar matriz MCE", o unico artefato principal admissivel e `.xlsx` (Excel), no perfil P09 aplicavel ao projeto. Para ADM Gamboa, P09 L50 com 43 causas/folha, 35 efeitos, Arial 10/8, sem notas nas colunas; abas `FOLHA N`. Nunca trocar por PDF, Markdown, Word, CSV ou imagens.
- Arquivos PDF/MD/DOCX sao apenas relatorios auxiliares EXTERNOS ao workbook. Nao os denominar "Matriz" nem apresenta-los como substituto de Excel.
- Se faltar qualquer gate de aprovacao, contrato de celulas, modelo ou executor Windows, responder `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`; nao entregar quadro PDF como matriz nem XLSX generico vazio como MCE concluida. Preservar as fontes recebidas, nao solicitar outras inexistentes como bloqueio artificial.
- Antes de entrega, validar extensao XLSX, integridade OOXML, paginas P09, colunas de efeitos, mesclas, fontes, rotacao, modelo e status de auditoria. Falha gera `FAIL_FORMAT_CONTRACT`.
- Essa regra complementa os gates humanos existentes, nunca autoriza editar um Excel antes do contrato e `AUTORIZO_ELABORACAO_MCE`. Detalhe na Skill `matriz-causa-efeito`.


## Regras da MCE P09 L50 para paginas, larguras e alturas — DEC-MCE-033/034

- L50 = 43 causas/folha (linhas 8:50) e 35 efeitos I:AQ. Abrir proxima `FOLHA N` SOMENTE apos preencher todas as 43 vagas da anterior; numero de paginas do desenho de origem nao define abas de MCE.
- DEC-MCE-034: altura por maior numero de linhas visuais em B/C/F:G `20 + 10*(n-1)` pt (1=20, 2=30, 3=40, 4=50 etc) para linhas de causa; limite 400 por Excel. Texto nao pode ser cortado; contagem automatica exige verificacao visual.
- Perfil de largura `P09_L50_20261110`: colunas B=25, C=56, F=34; preservar G e todas I:AQ, AR, bordas, mesclas, area de impressao e cabecalhos. Nao alterar globalmente P09 L57 nem homologar com base no proprio chat.
- Antes de liberar modelo editar, validar na Skill/contrato canônico `mce_workflow.py`; nunca mudar o mestre original, inserir X sem fonte, tratar candidato documental como FAT/SAT, alegar QA Windows/backup quando nao executado.


## Revisao anti-falso-positivo de altura (DEC-MCE-035)
- Perfil P09 L50: altura 20 pt se todos os textos de B/C/F:G couberem em uma linha visual; 30 pt quando existir 2 linhas, 40 para 3 etc. Detectar falso 30 pt causado por margem pixel excessiva ou fonte arredondada; medir Arial 8 pt e larguras reais no XLSX, incluindo mescla F:G. Sem QA visual Excel nativo, classificar contagem como ESTIMATIVA.
- Em auditoria apenas de altura, alterar exclusivamente `row height` em copia XLSX derivada, preservando bytes logicos de valores, 35 colunas de efeito I:AQ, X, 46 mesclas por aba, larguras B/C/F e area A1:AR50. Se o solicitante mencionar agente, exigir evidencia de lifecycle e não inventar subagentes.
- Esta regra nao homologa engenharia, nao altera o mestre, nao autoriza comandos ou merges e nao supre a whitelist/contrato do MCE.

## DEC-MCE-037 — correcao da largura solicitada pelo responsavel
**Bordas continuam thin**: a regra DEC-MCE-036 de bordas medium foi REVOGADA por mal-entendido. O tamanho 2 refere-se a largura de COLUNAS Excel A:AR. `column_width_profile=P09_L50_ALL_COLUMNS_2`: width 2 em todas as 44 colunas de cada aba; nao e possivel largura diferente apenas nas linhas superiores. Isso compromete descricao B/C/F; alternativa I:AQ=2 preserva B/C/F e deve ser indicada separadamente. Validar valores, X, merges, alturas, fontes e impressao; nao permitir edicao funcional do master.

## DEC-MCE-038 — corrigir pagina e colunas com garantia de efeito documental
No perfil `P09_L50_G_AR_2` usar largura 2 nas 38 colunas G:AR, mantendo inalteradas as seis A:F. Borda `thin` original e obrigatoria. Em toda MCE P09 L50 preenchida para revisão, cada causa/condicao deve ter >=1 X com titulo de efeito na linha 5. Nenhum comando deve ser inventado: itens sem efeito sustentado por MD/ET/arquitetura saem da matriz para RELATORIO EXTERNO (nao aba de MCE) com rastreabilidade, para revisão. Paginacao continua de 43 causas por aba (8:50), max. 35 efeitos I:AQ, X remapeados pelo nome. Com `require_effect_per_cause=true` o validador impede causas sem X e X sem cabecalho; ultima folha pode ter H vazio nas linhas sem causa. `PRODUCTION_COMPLETE=NO` sem engenharia e gates.

## DEC-MCE-039 — largura 2 real em G:AR, sem sobreposição
O valor 2 em `column_dimensions` nao garante renderizacao coerente se faixas OOXML de colunas se sobrepoem (ex.: I max=38 e J..AL independentes). O validador deve exigir para cada G:AR um `col` físico com min=max=índice, width=2.00, sem qualquer outro intervalo que inclua esse índice. Corrigir em copia XLSX somente metadados de colunas; A:F, bordas thin, X e efeitos inalterados. O 1,29 reportado pelo usuário motivou a investigação; nao afirmar origem definitiva da exibicao sem teste no app Excel.

## DEC-MCE-040 — paginação e largura VISIVEL 2 validada por fórmula oficial
No ADM, o usuário exige **SEIS abas P09 L50** (218 registros, 175 X) e proibiu perder 76 registros sem X durante correção de formatação; eles ficam pendentes, não recebem X inventado. A redução a 4 abas foi erro de escopo. O atributo Excel OOXML `width=2` aparece como aproximadamente 1,29 no Excel com fonte Normal MDW=7. Para **largura de coluna visível 2,00** gravar `width=2.7109375` em cada G:AR, com col min=max, sem sobreposição, customWidth=1. A:F e bordas thin preservadas. Altura de linha pelo maior wrap em B/C/F:G, 20 pt para uma linha e 30 pt para duas (40 para três etc). Validar programaticamente e inspecionar visual nativo antes de declarar conformidade final; Excel/Windows não executado neste caso. Usar perfil canônico opcional `P09_L50_G_AR_DISPLAY_2`, manter legado `P09_L50_G_AR_2` apenas para compatibilidade.

## DEC-MCE-041 — coluna AR visivel 96.00
No P09 L50 de ADM, colunas A:F devem manter as larguras de origem; **G:AQ devem exibir 2,00**, **AR deve exibir 96,00** (nao 2). No OOXML Normal MDW7, exigir G:AQ `width=2.7109375` e AR `width=96.7109375`, com um elemento col sem sobreposicao por indice. Usar perfil `P09_L50_G_AQ_DISPLAY_2_AR_96` para impedir regressao; preserve 6 folhas, 218 entradas documentais, 175 X, alturas 20/30+ pt e bordas thin, sem mudar lógica, aprovar matriz ou copiar arquivo ao DataCenter sem recibo.

## DEC-MCE-042 — evitar sufixo LIE dentro do SP do ADM
Na MCE ADM P09 L50, SP da coluna D expressa apenas porcentagem (`10%`, `20%`), nao `10% LIE` nem `20% LIE`. A notacao `% LIE` fica na descricao tecnica da causa C quando documentada, sem alterar o significado do nivel de H2. Preservar todos os outros dados, seis folhas/218 registros/175 X, G:AQ largura exibida 2 e AR largura exibida 96. Verificar todos SP D8:D50 antes de emitir candidato; sem homologaçao de engenharia automatica.


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



## DEC-MCE-075 — Preparar contrato sem pedir a mesma autorizacao repetidamente

**Causa-raiz:** \`mce_workflow.py init\` cria contrato bloqueado (\`model_approved=false\`, whitelist vazia), mas nao oferecia comando para propor coordenadas do Excel real. A ferramenta tambem limita edicoes a texto e protege X e efeitos; historicos \`EXTERNAL_ONLY\` nao correspondem a decisao mais recente ADM de observar na coluna AR.

**Correcao do fluxo de preparacao:** apos \`init\`, executar no host Windows privado:
\`\`\`powershell
python systems/mce/.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py propose-contract --workspace "C:\MCE_DADOS\ADM_GAMBOA" --annotation-policy IN_MATRIX --sp-policy UNUSED
\`\`\`
A saida \`contract.proposed.json\` e SOMENTE PROPOSTA: lista \`matrix_ranges\`, \`editable_cells\` de texto C/AR e SP historicos para revisao, preserva 35 efeitos, conta X existentes sem validalos e explicita os gates pendentes. Nao modifica \`contract.json\`, \`state.json\`, o XLSX original ou aprova o modelo. O responsavel revisa o contrato candidato, confirma o perfil vigente, protege cabecalhos e autoriza celulas especificas; mudancas de X/cabecalhos exigem analise e edicao funcional segregada, nunca X arbitrario.

**Sem novos bloqueios burocraticos:** quando a autorizacao de TRABALHO ja foi registrada (ADM: DEC-MCE-074), nao a solicitar novamente; preparar automaticamente dados, contrato candidato e pendencias. **Sem bypass de seguranca:** somente o gate de elaboracao documentado e modelo homologado permitem alterar matriz industrial; preparacao != emissao/revisao/aceite. Nao usar progresso de CI, modelo visual ou rascunho como homologacao de intertravamentos.



## DEC-MCE-078 - Nomenclatura PV, auditoria cruzada e aprendizado rastreavel

Para entrega de cada Matriz MCE, usar CODIGO_DOCUMENTO-REVISAO - PV NN.xlsx, com PV 01, PV 02, PV 03 e assim sucessivamente POR documento. Nao sobrescrever PV, nao saltar versao, nao gerar nova PV quando bytes permanecem identicos; documento seguinte tem identidade independente e inicia PV 01. PDF opcional usa a mesma raiz e numero. MCE_PRELIMINAR.xlsx no executor e somente arquivo intermediario, nao nome de entrega.

Ordem: inventario/revisoes/hash -> Skill mce-verificacao-cruzamentos -> Skill mce-verificacao-documental -> reauditoria com handoff de evidencias -> contrato e aprovacoes -> UNICO editor MCE canonico -> audit de OOXML/Excel Windows -> copia PV imutavel mce_pv_controller.py -> preflight de entrega mce_delivery_contract.py -> aceite externo de fechamento e proximo documento. Coluna sem X nao gera X arbitrario. Repeticoes de titulo exigem verificacao local e fonte. Nenhuma Skill de verificacao modifica XLSX nem concede aceites.

O DataCenter usa o mesmo ledger MCE existente quando houver host real verificado; a entrada privada PV e metadado append-only por SHA, sem novo banco. O DataCenter local Windows MCE foi declarado inexistente; nao reportar runtime, cofre ou restore sem evidencia. As Skills novas sao privadas e entram por interface apenas quando descobertas; nao publicar codigo/arquivos industriais sem autorizacao especifica.

Aprendizado continuo = falha comprovada, licao, teste de regressao, aprovacao humana da evolucao, commit com memoria e CI no SHA exato; nao alterar pesos de modelo nem operar em segundo plano. Ver systems/mce/docs/PV_VERSION_WORKFLOW.md e datacenter/PV_VERSION_MANIFEST.schema.json. Sem merge/deploy, sem homologacao inferida.

**DEC-MCE-079 — Correcao de nome:** a regra atual prevalece sobre qualquer referencia historica a `(PRELIMINAR VERSÃO NN) PV NN`. A revisao do documento integra o codigo; sem alteracao dos bytes do Excel, corrigir apenas o nome/manifesto, mantendo a mesma PV. Testar o caso sintetico DE-000.00-0000-000-ABC-001-B - PV 01.xlsx e rejeitar a forma historica.


## DEC-MCE-080 — Regra de nomeacao em Excel, Word e PDF
Todas as entregas do mesmo sistema seguem CODIGO_DOCUMENTO-REVISAO - PV NN.ext. Extensoes: .xlsx, .docx e .pdf conforme o artefato. NUNCA anexar titulo, comentario ou sufixo depois de PV NN ou antes da extensao, como PERGUNTAS_PENDENCIAS, RELATORIO, QUESTIONARIO ou FINAL. A finalidade fica dentro do documento e em metadados privados. Word do questionario permanece apenas com Localizacao, Folha e Pergunta. A PV do Word avanca conforme solicitacao; Excel e outros documentos nao sao renomeados automaticamente. Testar nome externamente por parse_deliverable_filename antes de entregar. Nenhuma mudanca de nome concede homologacao, modifica cruzamentos X ou dispensa gates de engenharia.


## DEC-MCE-081 — coluna H visível 3 e melhoria contínua a cada execução
Adotar apenas quando o projeto contratar o perfil `P09_L50_H_DISPLAY_3`: coluna H exibida 3,00 no Excel equivale, no MDW7 já registrado, a OOXML width=3.7109375. As demais colunas e todas as relações X ficam INTACTAS. Validar 1 `<col min=8 max=8>` por folha, hashes, valores, estilos, amarelos e QA Excel Windows antes de homologar. Não alterar outros modelos silenciosamente. Regra e testes: `datacenter/MCE_LAYOUT_LEARNING_POLICY.json`, `tests/test_mce_layout_learning_policy.py`, `docs/MCE_LAYOUT_LEARNING_CONTINUITY.md`.
A cada execução MCE solicitada: avaliar falhas verificadas, deduplicar dúvidas sem apagar decisões causa-efeito diferentes, registrar uma lição com evidência, executar teste e submeter à revisão humana. `LEARNING_ENABLED_ON_EACH_RUN=true` é política de processo; não é agente contínuo em background, não muda pesos e não grava no DataCenter host sem conexão comprovada. Word de perguntas só com Localização/Folha/Pergunta; Excel com amarelo e sem comentários quando assim solicitado.
