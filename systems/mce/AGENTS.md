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
