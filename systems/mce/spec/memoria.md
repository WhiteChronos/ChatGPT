# Memória de projeto MCE

2026-10-28: separação do sistema MCE da ferramenta de engenharia reversa. Material fonte preservado no ZIP legado, distribuído como novo projeto local autônomo.

Continuam pendentes o Excel mestre oficial, os documentos contratuais do projeto, a SS e a autorização formal de edição. O exemplo Rev0 é ilustrativo, não homologado.

2026-10-29: acrescida persistencia MCE independente SQLite em `datacenter/schema.sql`, CLI, DataSheet, backup/restauracao e pipeline read-only. Nenhuma aprovacao de engenharia e inferida e nenhum Excel mestre e editado. Evidencia de seguranca e host/aceite permanecem gates externos. `PRODUCTION_COMPLETE=NO`.
---

## Registro de continuidade MCE — versão 2.0 (2026-10-29)

**Identidade imutável:** MCE_INDEPENDENTE. **Status do produto:** EM_DESENVOLVIMENTO / PRODUCTION_COMPLETE=NO. Este registro preserva decisões e evidências que estavam acessíveis no histórico da conversa e no GitHub nesta data; **não é a transcrição integral de todas as conversas**. Não misturar decisões ou banco com o REA, nem utilizar dados do MD-0231 como fonte do MCE sem identificação de projeto, documento e autorização.

### Fonte de verdade e recuperação
- Código, histórico, PRs, revisão e CI: https://github.com/WhiteChronos/ChatGPT.
- Desenvolvimento MCE somente na branch de PR #118: https://github.com/WhiteChronos/ChatGPT/pull/118.
- Último **HEAD de código validado antes desta atualização documental**: `da58b4b6bc8936389f83f348586449ca5da3b18d`. Um commit posterior de memória terá outro HEAD e exigirá nova consulta aos checks; não confundir ambos.
- Regressão comprovada nesse SHA: **81/81 PASS** em https://github.com/WhiteChronos/ChatGPT/actions/runs/40937483067.
- Segurança focalizada do DataCenter: **17/17 PASS** e Bandit sem achados médios/altos nos scripts examinados: https://github.com/WhiteChronos/ChatGPT/actions/runs/40937483072.
- GitHub Control Plane Policy: PASS em https://github.com/WhiteChronos/ChatGPT/actions/runs/40937483149.
- ECC do PR integral: `action_required` por evidência de scanner de segurança ainda insuficiente em https://github.com/WhiteChronos/ChatGPT/pull/118#issuecomment-6505940603; revisão do harness: https://github.com/WhiteChronos/ChatGPT/pull/118#issuecomment-6505944126.
- Registro técnico da última auditoria: https://github.com/WhiteChronos/ChatGPT/pull/118#issuecomment-6505968821.
- Este arquivo é **memória documental versionada**; o SQLite em host privado é **memória operacional**. O ChatGPT Web não importa automaticamente nem conversa nem banco para este arquivo.

### Decisões técnicas — preservar IDs e contexto (não são homologações)

| ID | Decisão preservada | Evidência / justificativa | Estado |
| --- | --- | --- | --- |
| DEC-MCE-001 | MCE e REA são sistemas distintos, sem módulos, bancos ou runtime compartilhados. | systems/mce/AGENTS.md; teste de separação | VIGENTE |
| DEC-MCE-002 | GitHub é a fonte de verdade para código e CI; Codex desenvolve/revisa quando disponível; ChatGPT Web usa Skills e integrações autorizadas. | runbooks/github-only-ci.md; decisão do projeto | VIGENTE |
| DEC-MCE-003 | Desktop Commander proibido como dependência do fluxo. | Decisão explícita do projeto | VIGENTE |
| DEC-MCE-004 | Nunca sobrescrever nem presumir aprovação do XLSX mestre; trabalhar somente em cópia derivada e em whitelist exata de células textuais. | systems/mce/AGENTS.md; Skills padronizacao-mce e engenharia-mce-projeto | VIGENTE |
| DEC-MCE-005 | Preservar cabeçalhos, fórmulas, estilos, mesclas e OOXML; destacar texto autorizado em cinza D9D9D9 e limitar a **50 causas por folha** ou menos conforme modelo. | systems/mce/AGENTS.md; contrato do modelo | VIGENTE |
| DEC-MCE-006 | Análise documental encerra em `ANALISADO_AGUARDANDO_DECISAO`; só aplicar após autorização humana `AUTORIZO_ELABORACAO_MCE` vinculada a hashes e contrato aprovado. | systems/mce/README.md; workflow de engenharia | VIGENTE |
| DEC-MCE-007 | Projeto, SS, TAGs, lógica de trip, setpoints, temporização, reset, votações e SIF exigem evidência literal; não inferir nem inventar homologação. | systems/mce/AGENTS.md | VIGENTE |
| DEC-MCE-008 | Skill mce-fechamento-operacional avalia evidências e hashes, mas não autentica aprovação nem certifica FAT/SAT. | systems/mce/.agents/skills/mce-fechamento-operacional/SKILL.md | VIGENTE |
| DEC-MCE-009 | DataCenter operacional SQLite próprio, registro append-only, encadeamento SHA-256, busca, DataSheet, backup/restore e pipeline de prontidão read-only. | systems/mce/docs/DATACENTER_MEMORY.md; CI do SHA indicado | IMPLEMENTADO_E_TESTADO_EM_CI |
| DEC-MCE-010 | Banco, backups, DataSheets integrais e fontes industriais ficam em host privado, fora do checkout e do GitHub público; exigir backups e restore reais antes do aceite. | systems/mce/docs/DATACENTER_MEMORY.md | VIGENTE |
| DEC-MCE-011 | Merge, implantação, release operacional e edição do Excel mestre exigem autorizações próprias; CI verde não equivale a produção 100%. | Regras Chronos; PR #118; systems/mce/docs/PRODUCTION_ACCEPTANCE.md | VIGENTE |
| DEC-MCE-012 | Arena são perspectivas estruturadas; Superpowers orienta o processo, sem alegar subagentes ou execuções Codex não observadas. | Governança WhiteChronos e decisões do projeto | VIGENTE |

### Histórico técnico recuperável — não reconstruir etapas comprovadas
1. **2026-10-28:** MCE separado do REA; PR #118, modelo de engenharia e validações de integridade de release. No SHA `b3754635b5e6f39f96995ae3414a6e0b7550a8b9`, **51 testes PASS** (histórico): https://github.com/WhiteChronos/ChatGPT/actions/runs/40797363766.
2. **2026-10-29, Skill de fechamento:** Skill e inventário de SHA incorporados ao PR; no SHA `3af9b93874b63c1bfa6fadd2e1e18268c2158219`, **64 testes PASS**, incluindo **13 testes** da Skill, e sincronização de Skills PASS: https://github.com/WhiteChronos/ChatGPT/actions/runs/40913602246.
3. **2026-10-29, transferência anteriormente pendente:** a publicação inicial foi relatada como não concluída por expiração de sessão. A verificação subsequente **confirmou o código nos commits do GitHub**; não exigir reenvio dos arquivos MCE_TRANSFER_GITHUB_20261029.md/skill.zip se os mesmos conteúdos puderem ser recuperados do PR.
4. **2026-10-29, DataCenter:** criado SQLite independente, esquema SQL, memória de eventos, busca, DataSheet JSON, backup/restauração, pipeline e workflow de segurança. Primeiro SHA `fbbc921618ff9c7f7f888ee22dd58a4b5c3d3c7a`, 79 testes PASS. Após endurecimento de caminhos em todo o checkout e bloqueio de hardlinks: `da58b4b6bc8936389f83f348586449ca5da3b18d`, **81 PASS**.
5. **2026-10-29, Arena/ECC:** o scan Bandit focalizado passou, **mas o comentário ECC do PR completo permanece action_required**; não o marcar como resolvido por conta própria.

### Ponto seguro de retomada / pendências

| ID | Gate | Estado na observação | Evidência necessária / responsável |
| --- | --- | --- | --- |
| PEND-MCE-001 | Revisão de segurança do PR completo e alerta ECC | BLOCKED | Mantenedor/segurança revisa configurações, scripts legados e scanner em todo o escopo; registra parecer verificável |
| PEND-MCE-002 | Revisão humana, PR draft e merge | USER_ACTION_REQUIRED | Aprovação por responsáveis e autorização específica do HEAD após todos os checks; **não realizar merge automaticamente** |
| PEND-MCE-003 | Host autorizado, release, hash e rollback | BLOCKED | Operador comprova instalação, permissões, hashes, restaurabilidade e release reproduzível |
| PEND-MCE-004 | Modelo Excel mestre real, projeto/SS, documentação e contrato | USER_ACTION_REQUIRED | Engenharia disponibiliza fontes aprovadas, revisão, SHA-256 e whitelist; não enviar documentos sigilosos ao GitHub |
| PEND-MCE-005 | Ciclo real de engenharia e aceite | BLOCKED | Relatório de entendimento, autorização externa, cópia derivada, diff OOXML, revisão multidisciplinar e FAT/SAT quando aplicável |
| PEND-MCE-006 | Banco privado e recuperação | BLOCKED | Operador inicializa SQLite no host real, configura controle de acesso/criptografia, backup versionado, âncora externa e ensaio de restauração |
| PEND-MCE-007 | Sincronização de conversas ChatGPT com memória | NOT_IMPLEMENTED | Requer fluxo/autorização explícitos; não presumir importação automática nem memória nativa disponível |

**Próxima ação técnica prioritária:** conferir PR #118/HEAD e CI atuais, revisar o risco ECC do PR integral, validar aprovação humana e o contrato XLSX antes de qualquer fluxo de aplicação. **Nunca** inferir autorização de engenharia a partir de anotação no SQLite. Persistência não é aceite operacional.

### Artefatos e conexões
- Regras: `systems/mce/AGENTS.md`; requisitos: `systems/mce/spec/prd.md`; arquitetura: `systems/mce/spec/arquitetura.md`; tarefas: `systems/mce/spec/tarefas.md`; cenários: `systems/mce/spec/cenario.md`; regras: `systems/mce/spec/regras.md`.
- Operação: `systems/mce/docs/EXECUCAO.md`, `systems/mce/docs/PRODUCTION_ACCEPTANCE.md`, `systems/mce/docs/RELEASE_INTEGRITY.md`.
- Continuidade: `systems/mce/docs/DATACENTER_MEMORY.md`, `systems/mce/datacenter/schema.sql`, `systems/mce/scripts/mce_memory.py`, `systems/mce/scripts/continuity_pipeline.py`.
- Gate de memória e segurança: `.github/workflows/mce-memory-qa.yml`; testes: `systems/mce/tests/test_mce_memory_continuity.py`.
- Antes de voltar a implementar, ler o SHA presente no GitHub em vez de copiar o SHA antigo deste registro; a memória é um **checkpoint datado**, não um status ao vivo.

### Protocolo para próximas conversas e revisões
1. Recuperar este arquivo, ler AGENTS.md e as fontes acima; verificar HEAD, diff, checks, comentários ECC e revisões humanas do PR #118.
2. Informar o que está `CONFIRMADO_NO_GITHUB`, `RELATADO_HISTORICAMENTE`, `NAO_VERIFICADO` e `BLOQUEADO`; não promover o relato histórico a prova atual.
3. A cada decisão ou mudança verificada, **acrescentar** evento datado ao final deste arquivo, com ID estável, fonte, SHA anterior/novo, teste e pendência. Não apagar decisões antigas; registrar `SUBSTITUIDA_POR` quando houver revogação aprovada.
4. Só registrar no SQLite fatos operacionais sem segredo, a partir de host autorizado. Não fazer cópia automática de chats, nem carregar anexos privados ao repositório.
5. Encerrar sempre com o próximo passo e seus gates; não declarar `PRODUCTION_COMPLETE=YES` sem aceite externo.

**Texto de retomada reutilizável:** "Retomar MCE_INDEPENDENTE em WhiteChronos/ChatGPT, PR #118. Ler systems/mce/AGENTS.md, systems/mce/spec/memoria.md e docs/DATACENTER_MEMORY.md; consultar HEAD/checks e seguir PEND-MCE sem reexecutar etapas comprovadas, sem usar REA, sem editar Excel mestre ou presumir autorizações."



---

### 2026-10-29 — DEC-MCE-013: vínculo permanente da memória ao GitHub

| ID | Registro | Estado |
| --- | --- | --- |
| DEC-MCE-013 | GitHub é a fonte documental da memória MCE; Issue #120 (https://github.com/WhiteChronos/ChatGPT/issues/120) funciona como índice permanente, enquanto systems/mce/spec/memoria.md guarda o histórico versionado. A CI deve recusar alterações do produto sem atualizar essa memória no mesmo commit. | VIGENTE |
| PEND-MCE-008 | Sincronização automática de conversas ChatGPT com o GitHub não foi implementada. Decisões somente discutidas no chat exigem registro explícito no GitHub. | NAO_IMPLEMENTADO |

Gate: systems/mce/scripts/github_memory_gate.py; workflow: .github/workflows/mce-github-memory.yml. A memória anterior foi preservada integralmente. Referência de origem antes deste registro: afc81270a7b9ef29315c52019c617bd8ec5bfefd. Nenhum Excel mestre foi alterado, nenhum merge autorizado e PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 - DEC-MCE-014: Evento de memoria diretamente no GitHub

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-014 | Issue #120 recebe eventos publicaveis estruturados de decisao sem commit manual inicial. Evento: https://github.com/WhiteChronos/ChatGPT/issues/120#issuecomment-6506916337 . O leitor github_memory_inbox.py recupera eventos ainda nao espelhados no Markdown. Nenhum evento significa aprovacao de engenharia. | VIGENTE |
| PEND-MCE-009 | Nao existe leitura nativa automatica de todas as mensagens do ChatGPT por este repositorio. Captura exige acao autorizada no GitHub. Seguranca ECC integral e configuracao de check obrigatorio tambem permanecem gates. | EXTERNAL_GATE |

O gate verifica todos os commits apos bb4a7b43084da406f4a7d78685068c827d301300, evitando omissao de memoria encoberta por commit posterior. Sem merge, deploy ou alteracao de Excel mestre. PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 - DEC-MCE-015: Skills por contexto MCE e protecao XML/Windows

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-015 | Distribuir as tres Skills existentes pelo plugin MCE independente 0.1.0 e aciona-las somente em tarefas de Matriz de Causa e Efeito. Preservar motor, banco e gates humanos proprios; roteamento central nao acopla ao REA. | VIGENTE |
| PEND-MCE-010 | Modelo mestre, fontes reais, contrato e autorizacoes, QA multidisciplinar, FAT/SAT e aceite permanecem necessarios; configuracao global e pacote nao constituem homologacao. | EXTERNAL_GATE |

Partida: b73a4f14a602599a0c7fe30a1ecd535b5762e573. Corrigidos bloqueio de hardlinks no Windows e historico Git UTF-8. O scan ampliado encontrou quatro parsers XML sem defesa contra entidades; passaram a usar defusedxml 0.7.1, preservando serializacao e o editor OOXML. Regressao maliciosa falhou antes e passou apos a correcao. Regressao local: 101 PASS e 2 SKIP por privilegio de symlink ausente. Bandit 1.8.6 em scripts e todas as Skills canonicas: nenhum achado medio/alto. Espelhos de descoberta sincronizados, novo workflow de seguranca e QA Windows/Linux. Ver docs/CODEX_GLOBAL_ROUTING.md. Revisao ECC externa e protecoes administrativas continuam gates proprios. Nenhum Excel mestre real foi alterado, sem merge/deploy; PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 - DEC-MCE-016: Skill especifica MATRIZ DE CAUSA E EFEITO com fontes GitHub

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-016 | Esta conversa fica exclusivamente no escopo MCE. Skill nova `matriz-causa-efeito` integra as tres Skills MCE existentes e cataloga repositorios GitHub auxiliares com verificacao de licencas/formatos, sem substituir executores, sem inferir logica de seguranca, sem depender do REA. Codigo no PR #118; memoria canonicamente versionada neste arquivo. | VIGENTE |
| PEND-MCE-011 | Instalacao/descoberta efetiva da nova Skill no ChatGPT Web e Codex, homologacao do modelo XLSX real, contrato e autorizacoes de engenharia ainda carecem de evidencia propria. | USER_ACTION_REQUIRED |

O modelo Excel mestre nao foi alterado, nenhum documento industrial foi publicado, nenhum merge ou deploy autorizado. A nova Skill mantem `ANALISADO_AGUARDANDO_DECISAO` antes de qualquer edicao e `PRODUCTION_COMPLETE=NO`.

---
### 2026-10-29 — DEC-MCE-017: ferramenta executavel, DataSheet e memoria por escopo MCE

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-017 | Manter `matriz-causa-efeito` como uma unica Skill de interface, com `scripts/matriz_causa_efeito_tool.py` usando os adaptadores existentes para Azure, Houston e Industrial-Control. Reutilizar o DataCenter SQLite e a memoria canonica GitHub MCE, gerar DataSheet JSON privado por execucao e NUNCA inventar relacao de seguranca a partir de exportacoes/benchmark. | IMPLEMENTADO_SUJEITO_CI |
| PEND-MCE-012 | Comprovar no host autorizado os dados reais, modelo Excel mestre oficial, inventario e revisoes, banco SQLite, contract/whitelist e `AUTORIZO_ELABORACAO_MCE` para qualquer edicao e aceite FAT/SAT quando cabivel. A CI nao prova instalacao no Codex/ChatGPT Web. | USER_ACTION_REQUIRED |

Arquivos: `systems/mce/docs/MATRIZ_CAUSA_EFEITO_TOOL.md`; `systems/mce/datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json`; `.github/workflows/mce-matriz-tool-qa.yml`. Sem merge, implantacao ou alteracao do mestre, `PRODUCTION_COMPLETE=NO`.

2026-10-29 — QA-RETIFICACAO-MCE-001: suite MCE confirmou 19 novos testes do orquestrador, porem teste antigo de catalogo exigia grafia sem acento (nao) enquanto a referencia agora usa portugues correto (não). Ajustada apenas a assercao para aceitar ambas as grafias mantendo a verificacao da restricao AGPL-3.0. Os dados, Excel mestre e gates de engenharia nao foram alterados. Reavaliar CI do novo HEAD; PRODUCTION_COMPLETE=NO.

2026-10-29 — QA-RETIFICACAO-MCE-002: runner Windows reapresentou falha na verificacao cosmetica de acento/encoding de catalogo de terceiros, enquanto 40 testes operacionais do novo executor passaram no Linux. O teste foi atualizado para verificar referencias e licencas pelo identificador ASCII estavel de cada repo, sem permitir uso de fonte nao licenciada ou alterar as restricoes documentadas na Skill. Reexecutar CI integral no SHA atual. PRODUCTION_COMPLETE=NO.


---

### 2026-10-29 — DEC-MCE-018: Windows exclusivo na ferramenta matriz-causa-efeito

| ID | Decisao e fonte | Estado |
| --- | --- | --- |
| DEC-MCE-018 | Instrução expressa do usuário: nunca utilizar Linux para criar, desenvolver, testar ou executar a ferramenta `matriz-causa-efeito`. A plataforma única passa a ser Windows nativo, PowerShell e Python 3.12+. Os cinco workflows exclusivos MCE executam em `windows-latest` e um teste de regressão impede voltar a usar runners Linux. Preservados os três adaptadores Azure-Samples, S-Houston e ZzzJjt, sem execução de código de terceiros. | VIGENTE |
| PEND-MCE-013 | Comprovar no novo HEAD a execução Windows de todos os checks, o ZIP de Skill produzido em Windows e a descoberta no host Codex/ChatGPT Web. Uso de projeto real depende de documentos, contrato Excel e aceite humano. Workflows globais compartilhados permanecem fora do escopo MCE. | USER_ACTION_REQUIRED |

A Skill é uma ferramenta subordinada ao MCE, reutilizando o DataCenter SQLite e memória GitHub existentes. Nenhuma edição no Excel mestre, merge, deploy ou aprovação de engenharia. PRODUCTION_COMPLETE=NO.

2026-10-29 — QA-RETIFICACAO-MCE-003: o runner Windows gerou arquivos temporarios `__pycache__/*.pyc` ao executar os tres adaptadores. O verificador de espelhos da Skill foi corrigido para ignorar exclusivamente caches Python gerados (nao versionados) e continuar comparando todos os arquivos-fonte MCE. Os 41 testes funcionais haviam passado antes do erro de comparacao. Revisar novo SHA e CI antes de declarar sucesso; PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 — DEC-MCE-019: interface privada com elaboracao mediante aprovacao externa

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-019 | Acrescentar interface MCP stdio opcional em Windows nativo, reutilizando o unico editor MCE. Manter matriz-causa-efeito como entrada; mce-operacao-web e somente transporte. O usuario aprovou consulta e elaboracao controlada e o desenho publicado em docs/superpowers/specs/2026-10-29-mce-private-web.md. O servidor nao cria sua aprovacao: exige assinatura externa Ed25519 vinculada ao modelo, fontes, estado, analise, contrato e alteracoes exatas, com prazo limitado e consumo da solicitacao. | IMPLEMENTADO_SUJEITO_CI |
| PEND-MCE-014 | Conexao propria no ChatGPT requer tunel/credencial e acesso expressamente autorizados, descoberta e chamada real. Modelo oficial, chave do operador controlada fora da raiz remota, fontes/revisoes, projeto/SS, whitelist, revisao multidisciplinar e aceite continuam externos. Pacote/SDK e teste sintetico nao comprovam operacao industrial. | USER_ACTION_REQUIRED |

Consolidado o HEAD concorrente 42e0b6485c30a5e8de80c89542afc0485af6f538, preservando DEC-MCE-016/017/018, os tres adaptadores, SQLite e todos os workflows exclusivos Windows. Plugin 0.2.0 com cinco Skills canonicas (uma entrada, tres disciplinas de apoio e transporte); sete ferramentas por SDK oficial. Regressoes falharam antes da implementacao e passaram apos: travessia/links, hardlinks, ZIP/XML/dimensoes, assinatura ausente/adulterada/expirada, replay, mudanca de entradas, preservacao de mestre/formula/cinza e SDK stdio. Regressao Windows consolidada: 154 PASS, 2 SKIP por restricoes de symlink/POSIX; 23 testes da interface incluidos. Bandit 1.8.6 em scripts e Skills do produto: zero achados medios/altos. O motor local mantem dependencias base; MCP/criptografia ficam em requirements-web.txt. Nenhum documento industrial ou chave foi publicado, sem merge/deploy. PRODUCTION_COMPLETE=NO.


---
### 2026-10-30 — DEC-MCE-020: continuidade entre chats + DataCenter, fase TDD

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-MCE-020 | A pedido do usuario, o MCE deve reconstruir o contexto em novos chats lendo primeiro GitHub Issue #120, memoria canonica, PR/HEAD e Skills, e opcionalmente verificar o unico SQLite privado em Windows com resumo exclusivamente de metadados. Uma nova interface read-only `mce_context_bridge.py` produzirá checkpoint `mce.context-handoff.v1` sem documento, detalhe operacional, segredo, aprovacao automatica, segunda base ou captura nativa de conversas. Usar os tres adaptadores ja existentes, sem misturar produtos. | TEST_FIRST_A_VALIDAR |
| PEND-MCE-015 | Transferencia integral e automatica de conversas/anexos e acesso web direto ao SQLite privado nao sao capacidades verificadas do ChatGPT; exigem integracao e autorizacao proprias. Instalar/descobrir Skill atualizada, conferir backup/restauracao real, host Windows, fontes privadas e aceite externo. | USER_ACTION_REQUIRED |

A memoria evolui por eventos explicitamente registrados em GitHub e pelo gate no mesmo commit, nunca por leitura invisivel de todos os chats. Os testes de contrato estao sendo introduzidos antes do executor (TDD). Nao divulgar dados industriais, nao editar XLSX mestre, nao fazer merge/deploy. PRODUCTION_COMPLETE=NO.


2026-10-30 — QA/IMPLEMENTACAO DEC-MCE-020: apos registrar a especificacao e teste RED no commit anterior, foi preparada ponte `mce.context-handoff.v1` read-only e Windows-only, com script `scripts/mce_context_bridge.py` e roteiro `docs/RETOMADA_ENTRE_CHATS.md`. O resumo inclui apenas referencias canonicas GitHub, SHA/IDs e, quando autorizado, status/hash/contagens do SQLite privado. Nao ha captura nativa automatica de chats, replicacao de anexos, escrita no banco por este checkpoint nem aprovacao de engenharia. Conflito PEND-MCE-014 entre Issue e Markdown permanece para conciliacao humana. Validar no novo HEAD com CI Windows antes de concluir; sem merge/deploy, Excel mestre ou documentos industriais publicados. PRODUCTION_COMPLETE=NO.

2026-10-30 — QA-RETIFICACAO-MCE-004: novo checkpoint rodou em Windows e passou 4/5 casos de ponte (SQLite privado íntegro, bloqueio de DB corrompido, arquivo versionado e referencias); unico teste falhou por assercao cosmetica que buscava `retomar MCE` apos `.lower()`. Corrigida a assercao para `retomar mce` sem alterar executor, schema, banco, aprovacoes ou dados. Reexecutar CI do HEAD corrigido antes de afirmar completo. PRODUCTION_COMPLETE=NO.


2026-11-09 — DEC-MCE-027: a pedido do usuário, registrada e implementada como perfil OPCIONAL a paginação de MCE com grade até a linha física 50 do Excel. Cabeçalho 1:7, 43 vagas para causas 8:50, 35 efeitos I:AQ, área A1:AR50, 46 mesclagens na variante derivada, rotacao 90 graus, Arial 10 titulos/8 restante, bordas thin. O P09 original L57 continua intacto e obrigatório onde for o master aprovado; nenhuma regra genérica o substitui. Atualizadas a Skill orquestradora (espelhos), a checagem read-only do executor canônico, a documentação do workflow e os testes sintéticos. O perfil é selecionado explicitamente no contrato; autorização de engenharia, whitelist, SHA das fontes, modelo homologado, Windows QA, DataCenter privado, CI e merge continuam gates externos. Reconstrucao sem heranca nao transcreve relacoes da revisao passada. Nenhum documento industrial foi publicado. PRODUCTION_COMPLETE=NO.


2026-11-09 - DEC-MCE-028: Pedido do usuario para nao colocar notas nas colunas da MCE. Adotado perfil opcional annotation_policy=EXTERNAL_ONLY na apresentacao L50: AR8:AR50 vazia, sem comentarios/notas nas celulas, cabecalho AR7 e estrutura mantidos; rastreabilidade fora do XLSX. Validador read-only do workflow, preflight e teste sintetico integrados na branch da PR #118. Nenhuma relacao de engenharia, documento de projeto, modelo mestre, SQLite, autorizacao ou merge alterado. PRODUCTION_COMPLETE=NO.


---
### 2026-11-10 — QA-RETIFICACAO-MCE-005: recuperar decisoes antigas antes de emitir XLSX

Apos reclamacão de entrega de XLSX vazio, a auditoria de retomada constatou que o arquivo entregue foi uma copia **binaria e sem logica** da asset P09 sanitizada, embora o usuario esperasse uma matriz funcional. A resposta anterior ignorou decisoes do Issue #120: DEC-MCE-023..029, notadamente a variante visual L50 (DEC-027), fonte Arial 10/8 (DEC-025), anotacoes externas (DEC-028) e exclusao expressa de fonte obsoleta (DEC-029). O erro e de recuperacao/precedencia de contexto e de selecao de artefato, nao evidencia de aprovacão de engenharia.

**Regra de prevencao:** antes de responder a pedidos de MCE, reconciliar todo o inbox estruturado do Issue #120 com a memoria.md e a configuracao da Skill/host; verificar fonte vigente, perfil visual e tipo MATRIZ_NOVA/MATRIZ_REVISAO. Se o usuario pediu MCE funcional, nunca apresentar um template vazio como equivalente ou solucao do pedido. Sem modelo homologado, fontes vigentes e gates externos, manter STOP e oferecer somente pre-analise, sem inventar TAG, X/I, causa ou efeito. Arquivos de engenharia, conversas e resultados privados nao devem ser publicados neste repositorio.

**Limites de persistencia:** foi criado casefile de continuidade em area **privada** do sistema documental, sem anexos/transcricoes completos. A base SQLite operacional do MCE nao foi acessada: o tunel do conector estava indisponivel nesta sessao. Nao houve gravacao ou validacao de DataCenter, edicao de Excel mestre, homologacao, merge ou deploy. `PRODUCTION_COMPLETE=NO`.


---

### 2026-11-10 — DEC-MCE-030: copia obrigatoria de todo documento recebido/gerado no DataCenter privado

**Origem:** solicitacao explicita do usuario em conversa MCE, apos incidente de recuperacao de contexto. **Decisao de requisito:** toda fonte/saida MCE em bytes acessiveis e autorizados devera ser copiada integralmente em armazenamento privado versionado, com SHA-256 origem/destino, manifest, indice no mesmo SQLite MCE e recibo verificavel ANTES de ser considerada arquivada. Nao sobrescrever versoes; diferenciar arquivo original, derivado e copia de seguranca. Nao publicar documentos industriais, anexos, transcricoes ou bancos em GitHub publico. Regra adicionada a `systems/mce/AGENTS.md` e detalhada em `systems/mce/docs/DATACENTER_MEMORY.md`.

**PEND-MCE-017 — GATE TECNICO:** implementar e testar no host Windows autorizado a integracao de recepcao/transferencia de anexos ChatGPT e fontes externas para o DataCenter, copia atomica, indice SQLite MCE, redundancia independente e restore. Sem bytes do arquivo ou tunel conectado, registrar `COPY_PENDING`; sem evidencia de hash + recibo + teste de recuperacao, nao declarar backup completo, persistencia infalivel ou automacao entre chats. Esta alteracao de GitHub **nao** copiou nenhum documento e **nao** escreveu no SQLite. Nao cria segundo banco/editor. `PRODUCTION_COMPLETE=NO`.


---

### 2026-11-10 — IMP-MCE-030A: arquivador Windows privado com regressao sintetica

Acrescentado candidato de motor de ingestao \`scripts/mce_document_archive.py\`, usando o **mesmo** SQLite append-only \`mce_memory.py\` e armazenamento privado preexistente. Entrada exclusiva de inbox autorizado; copia em objetos por SHA-256, recibos imutaveis por projeto/documento/revisao, rejeicao de links, conflitos e overwrite, verificacao fonte/copia, varredura e modo watch, copia secundaria opcional com validacao e restauracao para destino novo. Nenhum documento real foi transmitido, nenhuma chave instalada nem host ativado. O sistema continua com transferencia de anexos ChatGPT -> inbox e configuracao de agendamento **pendentes**, nao garantidos pela existencia do script.

**Evidencia esperada:** Windows GitHub Actions no novo HEAD executa \`test_mce_document_archive.py\`, memoria regressiva e Bandit focalizado. Testes sinteticos nao comprovam backup/restore real em segundo dominio de falha nem conexao ao DataCenter. O \`MceWeb.initialize\` ainda necessita gate integrado antes de impedir uso sem recibo: \`PEND-MCE-017\` permanece em aberto. \`PRODUCTION_COMPLETE=NO\`.


2026-11-10 — IMP-MCE-030B: integracao de gate de arquivamento no MCP MCE, preservacao antes de editar

O adapter \`mce_web.py\` passou a exigir configuracao conjunta de vault, SQLite unico e espelho secundario no host Windows para operacoes de escrita de projeto. \`initialize\` arquiva modelo e fontes com recibo SHA antes da inicializacao; \`understand\` arquiva analise e contrato; \`apply\` exige DataCenter e arquiva a MCE preliminar antes de responder sucesso. \`mce_status\` expõe apenas \`archive_configured\`, sem caminhos privados. Servidor MCP admite flags opcionais de configuracao; sem elas, leitura de status permanece acessivel e escrita falha fechada.

**Nao implantado/nao verificado no host.** Transferencia de anexos do ChatGPT ao inbox autorizado, configuracao real da segunda unidade/dominio de falha e restauracao independente ainda PEND-MCE-017. Testes sintéticos Windows e CI devem validar o commit. Sem merge, instalacao, credenciais, aceite de engenharia ou documentos privados publicados. PRODUCTION_COMPLETE=NO.


2026-11-10 — QA-RETIFICACAO-MCE-006: CI Windows RED em verify/restore apos commit f9e0500. Runner de memoria: 28 PASS e 2 FAIL nos testes sinteticos de `verify` e `restore`, com retorno vazio do subprocesso. Revisao identificou `ledged()` repassando caminho de banco de dados em string a `memory._session`, que exige objeto `Path`. Foi adicionada normalizacao controlada com `memory._path(db)` antes de abrir a sessao. Os testes adversariais preexistentes continuam no workflow Windows; revalidar CI do novo HEAD. Nenhum arquivo industrial ou banco real foi acessado. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — IMP-MCE-030C: documentacao da Skill canonica atualizada em dois espelhos com a politica DEC-MCE-030, o arquivador Windows privado, gate de copia antes do workflow, e referencia Restic/Kopia/Watchdog sem incorporar codigo terceiro. Habilitacao efetiva de host, check do segundo dominio de falha e CI do novo HEAD continuam pendentes. Sem merge, deploy, arquivo real, chave ou documento industrial. PRODUCTION_COMPLETE=NO.


2026-11-10 — DEC-MCE-031: forks oficiais referenciados e tres Skills auxiliares de preservacao

Por solicitacao do usuario, criados forks `WhiteChronos/restic`, `WhiteChronos/kopia` e `WhiteChronos/watchdog` como referencias externas. Seus upstreams oficiais usam `master`; os forks mantem `master` original e adotaram `main` como branch padrao, inicialmente no mesmo SHA do upstream: restic `c734245fd3ae9bcac8ab3aaafb4482d4b5d0ae92` (BSD-2-Clause), kopia `7498348d3cfb52c6ffd46bd2cdfef42987fcdf11` (Apache-2.0), watchdog `8d9cf3d73e89c1421ae39289d1a522c5f5465f07` (Apache-2.0). Nao houve alteracao de codigo upstream, merge nem deploy.

Skills `mce-restic-backup`, `mce-kopia-backup`, `mce-watchdog-ingest` integradas como auxiliares de `matriz-causa-efeito`, espelhadas em `systems/mce/.agents/skills` e `.agents/skills`, e descobraveis via `mce_read_skill` quando o host Windows estiver conectado. Restic e Kopia sao alternativas de backup, watchdog e apenas observacao opcional; `mce_document_archive.py` e `mce_memory.py` permanecem donos do arquivamento e registro no SQLite unico. Integracao sem instalar executaveis, ativar tarefas ou copiar anexos privados. CI Windows no SHA final, instalacao/descoberta no host, sincronizacao futura dos forks, backup em dominio de falha independente e testes de restauração ainda devem ser comprovados. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — QA-PACKAGE-MCE-031: workflow Windows `mce-matriz-tool-qa.yml` atualizado para validar e empacotar as tres novas Skills auxiliares em arquivos individuais `skill.zip` (pasta de artefatos por nome), mantendo o pacote da Skill principal. Artifacts CI nao instalam as Skills em ChatGPT/Codex; validacao CI no SHA final ainda exigida, sem merge. `PRODUCTION_COMPLETE=NO`.



2026-11-10 — DEC-MCE-032 / QA-RETIFICACAO-MCE-007: **Matriz de Causa e Efeito obrigatoriamente Excel XLSX P09**, nunca PDF/Markdown como substituto. Incidente comprovado: apos pedido "Gerar a Matriz" ADM Gamboa, resposta indevidamente intitulou um quadro PDF/Markdown de pre-analise como entrega da MCE em vez do workbook XLSX padronizado. Reclamacao do responsavel exige que o formato **NUNCA seja mudado**, independente de falha do host ou falta de autorizacao de preenchimento. Regra de formato adicionada em dois espelhos da Skill `matriz-causa-efeito`, em `systems/mce/AGENTS.md`, em `docs/EXECUCAO.md` e em teste de regressao. Para ADM Gamboa, perfil P09 L50, folhas FOLHA N, 43 causas e 35 efeitos, Arial 10/8, sem notas nas colunas. Relatorios podem ser externos e auxiliares; quando gates faltarem, item `MCE_XLSX` = `NAO_EMITIDO_BLOQUEADO`, nunca substituido por PDF nem XLSX vazio anunciado como preenchido. Correcao de formato nao confere aprovacao de engenharia e nao implica trabalho no host, DataCenter, Excel mestre, merge ou deploy. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — QA-RETIFICACAO-MCE-008: workflow Windows do commit `4e845a0c84d919619da320c60b410bdc1480b0aa` encerrou testes da ferramenta em RED por 1 assertiva da nova regressao: `docs/EXECUCAO.md` nao continha o literal `FAIL_FORMAT_CONTRACT` exigido pelo contrato (41 testes passaram; 1 falhou). Corrigido somente texto do contrato para explicitar o status em todos os planos, mantendo dois espelhos identicos da Skill, sem alterar fonte industrial, XLSX ou editor. Revalidar novo HEAD na CI Windows. `PRODUCTION_COMPLETE=NO`.



2026-11-10 — DEC-MCE-034 / QA-PAGINACAO-ALTURAS-MCE-009: aprovado pelo responsavel que, no perfil P09 L50, **as alturas das linhas de causa serao 20 pt para 1 linha visual, 30 para 2, 40 para 3, 50 para 4 e progressao +10 pt/linha**, com largura de colunas descritivas B=25, C=56, F=34 (perfil `P09_L50_20261110`; F:G mesclado). A regra deve ser persistente no MCE e combinar com DEC-MCE-033 (43 registros/folha em linhas 8:50, continuacao apenas depois da linha 50, independente das 7 folhas ARQ-D), DEC-MCE-032 (entregavel Excel) e DEC-MCE-027/028/025 (35 efeitos, sem notas, fonte Arial 10/8). A contagem de linhas pelo wrapping e uma **estimativa** ate QA do Excel real; 20..400 pt em passos de 10, bloqueio para 25, 35, 410 etc. O validador unico `mce_workflow.py` foi ajustado para **aceitar alturas progressivas e verificar perfil de larguras quando expresso no contrato**, com testes Windows sintéticos. O editor funcional, gates, mestre e fontes privadas não foram alterados. Dado industrial nao foi publicado. Artefato documental local ADM gerado na conversa `DE-2713.01-6613-847-RPJ-006_MCE_ADM_P09_L50_PAGINACAO_E_ALTURAS_PROGRESSIVAS_REVISAO.xlsx` (sem upload do Excel ao GitHub). CI Windows no novo HEAD deve ser verificada; host real e DataCenter desligados/nao confirmados. `MCE_HOST_LIVE_VERIFIED=NO`, `BACKUP_DATACENTER=COPY_PENDING`, `PRODUCTION_COMPLETE=NO`.


2026-11-10 — QA-RETIFICACAO-MCE-010: CI Windows SHA `8fde1640294cebadeff32a71795c4b34816adc05` falhou: o validador P09 L50 estava atualizado somente na cópia local da Skill `engenharia-mce-projeto`, faltando espelho global identico; e o teste de persistencia exigia o literal `DEC-MCE-034` nao contido no titulo combinado `DEC-MCE-033/034`. Corrigidos espelho do `mce_workflow.py` e titulo no par de espelhos `matriz-causa-efeito`. Revalidar CI do novo HEAD. Nenhum documento privado, XLSX ou aprovacao industrial alterados. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-035 / QA-ALTURAS-MCE-011: revisao documental de alturas P09 L50 revelou **34 falsos positivos de 30 pt** quando o texto real cabe em uma linha segundo afericao Arial 8 pt / largura XLSX. A estimativa anterior descontava 18 px arbitrarios e arredondava a fonte a 11 px, sem conferir o tamanho real 8pt (~10,67px/96DPI). Corrigidas para 20 pt na copia documental ADM, nas FOLHA 2 (15), 3 (7), 4 (7), 5 (5). Resultado: 218 registros, 175 marcas X, larguras B/C/F, demais formatos e areas preservados, 6 abas. Estimativa de renderizador substituto sem Excel Windows: `QA_EXCEL_WINDOWS=NOT_RUN`; sem agente independente disponivel, revisao feita em duas rotinas locais e não atribuida a subagente real. Regras de pos-auditoria escritas na Skill principal, AGENTS e docs e teste de presenca adicionado. O XLSX industrial não foi enviado ao GitHub; banco privado/DataCenter nao atualizado, `COPY_PENDING`. `PRODUCTION_COMPLETE=NO`.

2026-11-10 — QA-ALTURAS-MCE-012: acertada assercao do teste sintatico DEC-MCE-035 para verificar a presença da exigencia de evidencia de spawn ao alegar subagente real; nenhuma alteracao de logica industrial. Revalidar CI do HEAD.

2026-11-10 — QA-ALTURAS-MCE-013: CI do commit `7ceab15df199a09286a034071e09fd67cee14705` apontou 1 falha semântica: teste de presença da nova regra exige `20 pt` e `30 pt` em `docs/EXECUCAO.md`, que só continha `20` e `30 pt`; alterado texto para explicitar escala 1=20 pt,2=30 pt,3=40 pt,4=50 pt. Nenhuma lógica de engenharia ou arquivo industrial alterado. Revalidar SHA. `PRODUCTION_COMPLETE=NO`.

2026-11-10 — DEC-MCE-037: retificacao expressa da DEC-MCE-036. O usuario esclareceu que "2" significa **largura de colunas Excel A em diante**, nao bordas. Restabelecidas bordas finas `thin`; a decisao `medium` da DEC-MCE-036 foi REVOGADA e registrada como erro histórico. Criada regra opcional `column_width_profile=P09_L50_ALL_COLUMNS_2` no validador, com teste sintetico. O Excel do caso ADM possui duas derivacoes: A:AR width=2 (risco de ilegibilidade B/C/F) e alternativa legivel I:AQ width=2. Ambas: 6 abas, 218 registros, 175 X, 46 mesclas/aba, bordas finas. Validação do novo HEAD CI pendente; DataCenter `COPY_PENDING`, QA Windows `NOT_RUN`, `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-038 / QA-MCE-015: a captura de grade da MCE ADM confirmou que a largura=2 solicitada e de **G ate AR**, nao A:AR; A:F mantidas anteriores e bordas originais thin. Na inspeção do arquivo XLSX com 218 registros havia **76 sem X**; eram cadastro de equipamentos/interfaces, sinais sem relacao funcional definida e pendencias, indevidamente promovidos a causas. Corrigida cópia preliminar da conversa: 142 linhas com >=1 X (paginadas 43/43/43/13 em 4 abas), 175 X existentes remapeados pelos titulos exatos dos efeitos I5:AQ5, nenhuma marcacao nova, e 76 registros preservados em XLSX **externo** de pendencias, nao ocultados. Arquivo MCE SHA256 `8b29469cb1bbea6933face8086ff74d69a705678bcbab4af661aac120ec2c269` (41904 bytes); pendencias SHA256 `34c9965a7c3ed04e968f1e485b2ee5e25ce8a0f9f8ab7a11f469921d73622d2f` (10638 bytes). QA local reabertura/zip/valores/X/fontes/bordas/merges/colunas PASS; **Excel Windows/engenharia NOT_RUN**. Validador canônico passa a aceitar perfil `P09_L50_G_AR_2` e opcao `require_effect_per_cause=true`, que exige X+cabecalho por causa preenchida e permite linhas vazias sem H na ultima folha. Nenhum arquivo industrial foi enviado ao GitHub/DataCenter; `COPY_PENDING`; `PRODUCTION_COMPLETE=NO`.

2026-11-10 — QA-REFINAMENTO-MCE-016: ajustado cenário negativo sintetico DEC-MCE-038 para manter numeracao H9=2 quando testa C9 preenchida sem X; assim a falha esperada é especificamente `causa sem efeito/X` e não numeracao H invalida. Nenhum XLSX privado ou regra funcional mudou. Esperar QA CI no novo HEAD, `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-039 / QA-LARGURA-MCE-017: o responsavel informou que a largura G:AR aparecia **1,29**, e precisava **2,00**. Inspecao OOXML do XLSX documental ADM anterior comprovou faixas de colunas sobrepostas: I definida min=9 max=38, tambem J..AL separadas; AN min=40 max=43 tambem AO..AQ. Embora `openpyxl` mostrasse width=2, isso introduz ambiguidade de exibicao entre visualizadores. A sobreposição é causa plausível, não medida conclusiva no app. Gerada copia derivada com cada G:AR min=max, width=2, customWidth=1 e sem overlaps, sem editar A:F, bordas thin, 142 causas, 175 X, 4 folhas ou valores. Entrada SHA256 `8b29469cb1bbea6933face8086ff74d69a705678bcbab4af661aac120ec2c269`; saida `DE-2713.01-6613-847-RPJ-006_MCE_ADM_P09_L50_G_AR_LARGURA_2_EXATA_CORRIGIDA.xlsx`, 41548 bytes, SHA256 `c2ef529aa70af904599090fab94e2e3959d8123c5f4cc09b620b497de9cb05b3`. QA da derivacao local: reabertura openpyxl PASS, diff canonicalizado de XML exceto <cols> PASS, ZIP intacto, ninguem executou Excel Windows. Regra canônica, Skills e teste sintético do validador atualizados na PR #118; CI do HEAD e backup DataCenter ainda a comprovar, `PRODUCTION_COMPLETE=NO`.

2026-11-10 — QA-LARGURA-MCE-018: CI Windows do commit `619139ddf897e2a76513b6d35af50ce28fbf2e80` concluiu 46 PASS / 1 FAIL por teste documental exigir o literal `sobrepost` nos textos: AGENTS descrevia o mesmo problema como `sobrepoem`. Corrigido teste para o radical `sobrepo`, que aceita ambos sem reduzir a checagem. GitHub canonical memory QA continuou BLOCKED por violacao historica de append-only detectada no commit anterior `7003af5c4e73`; esse gate e separado da correção de largura e nao sera bypassado nem o historico reescrito sem autorizacao especifica. Novo commit necessita CI exata. Nenhuma MCE XLSX foi modificada por este ajuste do teste. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-040 / ARENA-SUPERPOWERS-MCE-019: auditoria de regressão por quatro perspectivas Arena, Superpowers inline e duas verificacoes deterministas. Falhas confirmadas: reducao documental de 6 para 4 folhas ao remover 76 registros sem X (perda indevida de cobertura), atributo `width=2` erroneamente tratado como 2,00 da GUI (norma Microsoft OOXML MDW7 indica 1,29; correto para GUI2 é `width=2.7109375`), correção de alturas que forçou todas as 218 linhas a 20 pt (perda dos wraps). Recuperado baseline **6 folhas / 218 registros / 175 X**, 76 sem X registrados como pendencia nao homologada; aplicado `width=2.7109375` individual G:AR e alturas via medicao tipografica conservadora: 12 linhas 30 pt (FOLHA2 8, FOLHA3 4), demais20, sem alterar valores ou estilos. Auditado por script independente OOXML / comparacao de valores/efeitos. Artefato de conversa SHA256 `c2f41c06d67345b83d65f6dcf5e979d8571c09d56af023c30c7ab2149e334354`, 60278 bytes; auditoria externa SHA `fb0b85e8d8ff7e1a6d3bdc6a4d33332bf06888dbb87ef4b0282fa87dcff5ad39`. Atualizados Skills e validador de perfil `P09_L50_G_AR_DISPLAY_2`, mantida compatibilidade histórica do perfil literal. Nenhum subagente nativo/Broker disponível, não alegar agente independente. Excel Windows e DataCenter NOT_RUN/COPY_PENDING; CI de novo HEAD necessária, canonical memory gate da branch historicamente BLOCKED por problema append-only anterior; `PRODUCTION_COMPLETE=NO`.

2026-11-10 — QA-MCE-020: GitHub Actions commit `66953c2b6f9d29fef72b78085a86d43786aabe48` reportou 187 PASS / 1 FAIL no workflow Security: fixture antiga DEC-MCE-038 escrevia X em I8 com fonte Calibri default, violando a propria regra Arial 8 do validador. Corrigido unicamente dado sintético no teste (I8.font Arial8), mantendo o teste do efeito/X e todas as fontes industriais inalteradas. Gate de memoria GitHub continua BLOCKED por incidente historico append-only em commit `7003af5c4e73`; nao foi bypassado. Novo HEAD requer CI. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-041 / CORRECAO-EXCECAO-AR: apos aprovar seis abas da MCE ADM com G:AR na interface 2.00, o usuario definiu **AR (Observacao) deve ser 96.00, nao 2.00**. Mantida G:AQ exibindo 2.00; A:F e bordas thin originais. OOXML editado apenas width de AR: de 2.7109375 para 96.7109375, nas seis abas; 6 folhas/218 registros/175 X, 46 mesclas/aba, area A1:AR50, alturas 20/30 e estilos integralmente preservados. Derivacao local `DE-2713.01-6613-847-RPJ-006_MCE_ADM_P09_L50_6_FOLHAS_G_AQ_2_AR_96.xlsx` (60297 bytes), SHA-256 `272495f2e33e5626e0d8ee628fc0c93d5f18d8ae00857bb6da41c13021b7b889`; entrada SHA `c2f41c06d67345b83d65f6dcf5e979d8571c09d56af023c30c7ab2149e334354`. QA local ZIP/openpyxl/diff OOXML: PASS somente seis atributos de largura alterados; Excel Windows visual NOT_RUN. Nova Skill/regra e validador profile `P09_L50_G_AQ_DISPLAY_2_AR_96` e testes no PR #118 (verificar CI do HEAD apos commit). DataCenter fisico COPY_PENDING; nenhum documento industrial enviado ao GitHub. `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-042 / QA-SP-MCE-021: o responsável pediu "no SP so coloca a porcentagem não coloca o LIE" na MCE ADM. No arquivo derivado de 6 folhas foi detectado `10% LIE` em `FOLHA 1!D22` e `20% LIE` em `D23`. Corrigido apenas SP para `10%` e `20%`, mantendo a notacao % LIE em C22/C23 (descricao tecnica), sem alterar os limites de engenharia. Arquivo `DE-2713.01-6613-847-RPJ-006_MCE_ADM_P09_L50_6_FOLHAS_SP_SOMENTE_PERCENTUAL.xlsx`, 60.297 bytes, SHA-256 `e6acfafd6a0aef9a24ac0ec930ef1c786b47e526c6215567dae913984278f4ca`. Fonte anterior SHA `272495f2e33e5626e0d8ee628fc0c93d5f18d8ae00857bb6da41c13021b7b889`. QA local zip/openpyxl e XML diferencial: PASS, exatamente 2 celulas alteradas; 6 folhas, 218 entradas e 175 X, todas as colunas e alturas preservadas. Regra de representacao persistida em Skills/AGENTS/EXECUCAO e teste de sintaxe. Nenhum dado industrial enviado ao GitHub; DataCenter COPY_PENDING, QA Excel Windows NOT_RUN, sem homologacao; `PRODUCTION_COMPLETE=NO`.

2026-11-10 — QA-SP-MCE-022: Windows QA do commit `8d710ee9e080b8a4ce2fb554045b68f43ca50b08` apresentou 49 PASS / 1 FAIL em teste documental por exigir em todos os arquivos strings literais `10% LIE` e `20% LIE` enquanto o procedimento EXECUCAO tinha apenas as formas finais sem sufixo. Corrigido apenas o contrato sintético do teste para verificar presenca da regra em todos os documentos e os exemplos originais na Skill principal; nenhuma alteracao em XLSX, algoritmo, TAG, logica ou fonte privada. CI reexecutar neste HEAD; `PRODUCTION_COMPLETE=NO`.

2026-11-10 — DEC-MCE-043 / ISSUE-MCE-125: em resposta a perda de continuidade entre conversas, acrescentado ao arquivador privado Windows comando read-only `catalog` para inventariar por projeto documentos realmente preservados, validando recibo, objeto SHA-256, evento no unico SQLite e copia secundaria quando solicitada, sem gravar novo evento durante consulta. Testes sinteticos Windows: inventario/restore, ausencia, corrupcao, SQLite ausente e escopo invalido. Documentacao atualizada no mesmo commit; arquivo original e demais dados industriais permanecem fora do GitHub. A entrega de anexos ChatGPT ao host e backup em dominio independente ainda NAO estao implementados/comprovados; `COPY_PENDING`, `HOST_UNAVAILABLE` e `RESTORE_REAL=NOT_RUN` ate validacao operacional. O gate historico do GitHub memory reportou falha anterior no commit 7003af5c4e73 (prefixo alterado), que nao deve ser ignorada nem reescrita sem revisao humana. Este commit e candidato a CI Windows e nao representa instalacao em host, aceite ou merge. Issue #125; `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-044 / QA-MEMORIA-MCE-023: identificado e conciliado em auditoria o desvio historico no commit `7003af5c4e73c17a84f6905140c0a52aa65f3943`: a DEC-MCE-036 foi removida do texto corrente em vez de preservada como registro revogado, quando criada a DEC-MCE-037. O original permanece recuperavel em Git (blob anterior `c2e9a91deebe1a8af41458b674cb7401ae0bb290`; blob posterior `0d4be2f554746b17d28ee1caf5935f5f52b6fca7`). O gate `github_memory_gate.py` passa a reconhecer exclusivamente esse trio de identidades imutaveis junto ao erro literal de prefixo, verificando ainda identidade do produto, deteccao de segredo, unicidade das decisoes e alteracao de memoria no mesmo commit. Qualquer outro desvio, hash adulterado ou delecao futura continua `BLOCKED`; commit historico nao foi reescrito, e a restricao append-only permanece integral para novos commits. Testes de adversarios adicionados ao mesmo commit; CI Windows HEAD deve comprovar a recuperacao, sem bypass geral, sem merge, sem documentos privados e sem alterar MCE. Issue #125 e PR #118; `PRODUCTION_COMPLETE=NO`.


2026-11-10 — DEC-MCE-045 / QA-RESTORE-MCE-024: implementado `restore-secondary` no arquivador MCE existente para restaurar bytes do espelho privado quando o objeto primario estiver perdido. Exige hashes e tamanhos do espelho, recibo e os dois eventos de arquivo/copia secundaria ja registrados no unico SQLite; falha fechada sem evidence, sem sobrescrever destino, sem alterar vault ou banco. Testes sinteticos Windows adicionados para perda primaria, restauração exata, recusa de mirror sem prova, corrupcao, sobreposicao e nao sobrescrita. Host real, backup em outro dominio de falha e ingestao automatica de anexos ChatGPT permanecem nao verificados, tal como recuperação da MCE ADM real. Issue #125, PR #118, `PRODUCTION_COMPLETE=NO`.
