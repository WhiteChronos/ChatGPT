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
