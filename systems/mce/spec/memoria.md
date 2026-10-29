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

