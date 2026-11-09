# Memoria de projeto REA

2026-10-28: REA interno independente do MCE e do upstream `morluto/rea`, com sete ferramentas read-only MCP. Validacao host Codex/ChatGPT Web pendente.

2026-10-29: acrescentado DataCenter SQLite privado, DataSheet, backup, recuperacao, script de continuidade e CI de seguranca; nao sao provas de integracao MCP real. `PRODUCTION_COMPLETE=NO`.
---

## Registro canônico de continuidade REA — versão 2.0 (2026-10-29)

**Produto:** REA_INDEPENDENTE. **Situação:** PR DRAFT / PRODUCTION_COMPLETE=NO. Este documento consolida as decisões e evidências disponíveis na conversa e no GitHub até esta data. **Não é uma transcrição integral nem captura automática de conversas passadas ou futuras.** Não misturar dados, decisões, importações ou banco com MCE.

### Fontes de verdade e checkpoint
- Código e CI: https://github.com/WhiteChronos/ChatGPT; branch dedicada do [PR #119](https://github.com/WhiteChronos/ChatGPT/pull/119).
- HEAD técnico com execução CI comprovada **antes desta alteração documental**: `734175897cc318a964196e9e08b6dbdb39e27010`. Validar novo HEAD e novos checks antes de alterar ou aprovar código.
- Regressão **55/55 PASS** no runner GitHub: https://github.com/WhiteChronos/ChatGPT/actions/runs/40937509776. Inclui testes do MCP SDK no ambiente de CI; **não** prova Codex/ChatGPT Web real.
- Testes específicos DataCenter: **17/17 PASS**, Bandit focalizado sem achados médios/altos nos scripts analisados: https://github.com/WhiteChronos/ChatGPT/actions/runs/40937509727.
- Política GitHub PASS: https://github.com/WhiteChronos/ChatGPT/actions/runs/40937509845.
- ECC `action_required` **ainda não resolvido** para escopo integral do PR: https://github.com/WhiteChronos/ChatGPT/pull/119#issuecomment-6505944804; alerta de harness: https://github.com/WhiteChronos/ChatGPT/pull/119#issuecomment-6505947722.
- Última auditoria publicada: https://github.com/WhiteChronos/ChatGPT/pull/119#issuecomment-6505970066.
- GitHub: memória documental versionada. SQLite local: memória operacional privada **não comprovadamente provisionada no host final**. Não existe sincronização automática com mensagens do ChatGPT.

### Decisões preservadas (IDs estáveis; não representam aprovações)

| ID | Decisão e justificativa | Estado |
| --- | --- | --- |
| DEC-REA-001 | REA é independente do MCE e de Excel, banco, engenharia de MCE ou servidores compartilhados; conferir systems/rea/AGENTS.md. | VIGENTE |
| DEC-REA-002 | O motor Python/JS/TS é interno e próprio, distinto do projeto oficial `morluto/rea`/`rea-agents`; instalar e identificar upstream só com prova. | VIGENTE |
| DEC-REA-003 | Sete ferramentas REA via SDK MCP devem ser somente leitura, com root explicitamente autorizado, SHA, restrições de caminhos e arquivos sensíveis. | VIGENTE |
| DEC-REA-004 | SDK oficial MCP, stdio e Streamable HTTP limitado a loopback, sem bind público; interfaces de túnel remoto exigem projeto de segurança independente. | VIGENTE |
| DEC-REA-005 | Plugin portátil `systems/rea/plugin.json`, overlay Codex `.codex-plugin/plugin.json`, Skills `rea-setup` e `rea-operacao`; arquivos instaláveis não demonstram descoberta pelo host. | IMPLEMENTADO_NO_REPOSITORIO |
| DEC-REA-006 | Integração ChatGPT Web exige host, workspace, identidade, túnel privado autorizado, `tunnel-client doctor`, `tools/list` e chamada `rea_bridge_status` reais. | VIGENTE |
| DEC-REA-007 | GitHub é fonte de verdade do código e CI; Codex é ambiente previsto para execução/teste/revisão; ChatGPT Web usa Skills e MCP somente quando conectados. | VIGENTE |
| DEC-REA-008 | Desktop Commander está excluído; não executar instalações em host, expor endpoint público, ultrapassar root autorizado ou analisar código não autorizado. | VIGENTE |
| DEC-REA-009 | DataCenter REA possui SQLite exclusivo, trilha append-only SHA-256, SQL parametrizado, busca, DataSheet, backup e restore; pipeline escreve status **local**, não status de host Web. | IMPLEMENTADO_TESTADO_EM_CI |
| DEC-REA-010 | SQLite, backups, credenciais e evidências privadas ficam em host controlado, fora do repositório/CI; criptografia de volume, âncoras confiáveis e ensaios de restauração precisam ser comprovados. | VIGENTE |
| DEC-REA-011 | GitHub Arena usa perspectivas heurísticas, não agentes independentes; a presença de Superpowers ou Skills não prova sua execução efetiva. | VIGENTE |
| DEC-REA-012 | Não fazer merge, deploy ou alegar 100% sem aprovação humana, segurança do PR integral, CI no HEAD, runtime real, controle de acesso, rollback e aceite externo. | VIGENTE |

### Linha do tempo comprovada ou historicamente reportada

1. **2026-10-28:** REA separado do MCE; motor estático e ponte MCP read-only. SHA `00fbffa22f74b66003a869bdb42a6d6d47428f37`: **34 testes PASS** (histórico) em https://github.com/WhiteChronos/ChatGPT/actions/runs/40797384005.
2. **2026-10-29, plugin:** manifesto portátil, compatibilidade Codex e Skills de operação; SHA `ccd9f741a0d4eb6c8aaef7334e5a39d9fc1aeed3` com **38 testes PASS** em https://github.com/WhiteChronos/ChatGPT/actions/runs/40913332166.
3. **2026-10-29, transferência antiga:** REA_TRANSFER_GITHUB_20261029.md foi preparado numa sessão anterior; transferência inicialmente não concluída por sessão expirada. Depois os arquivos foram **recuperados e verificados no PR**. Evitar reconstruir conteúdo já recuperável no GitHub.
4. **2026-10-29, persistência:** DataCenter SQLite próprio, DataSheet, busca, memória, backup/restauração, pipeline read-only e workflow; SHA `9be3b5bcb4595bb252bc23d709841bfa143a9b48`, **53 testes PASS**. Endurecimento de caminhos e hardlinks em `734175897cc318a964196e9e08b6dbdb39e27010`, **55 testes PASS**.
5. **2026-10-29, segurança:** scanner Bandit focalizado aprovado; comentário ECC `action_required` do PR inteiro continua aberto. Sem evidência de MCP descoberto pelo Codex/ChatGPT Web real, sem aceite nem merge.

### Pendências e condição objetiva de liberação

| ID | Situação | Responsável e prova esperada |
| --- | --- | --- |
| PEND-REA-001 | BLOCKED: ECC de segurança integral e harness | Mantenedor/segurança examina configs/Skills, plugin, SDK MCP, endpoints, permissões, CI e produz evidência auditável por HEAD |
| PEND-REA-002 | USER_ACTION_REQUIRED: revisão humana/merge | Revisores autorizados aprovam PR draft, checks completos no novo SHA, autorização específica de merge sem bypass |
| PEND-REA-003 | BLOCKED: host Codex e pacote | Operador instala release validado por hash em host permitido; Runtime Doctor observa inventário real das sete ferramentas e Skills |
| PEND-REA-004 | BLOCKED: MCP privado ChatGPT Web | Infra aprova host, workspace e Tunnel; executar `tunnel-client doctor`, `tools/list`, `rea_bridge_status` observados no cliente real |
| PEND-REA-005 | BLOCKED: segurança operacional e rollback | Negação de acesso fora do root, logs, revogação, resiliência e restauração comprovados, com aceite externo |
| PEND-REA-006 | BLOCKED: banco privado em produção | Operador comprova permissões, criptografia do volume, backups versionados, verificação de digest externo e ensaio de restauração real |
| PEND-REA-007 | NOT_IMPLEMENTED: importação de conversas | Exige integração e autorização específicas; nem plugin nem SQLite capturam chats automaticamente |

**Próximo passo seguro:** consultar novo HEAD/CI do PR #119, tratar o ECC `action_required` do PR completo e obter revisão humana antes de qualquer mudança de estado de implantação. Posteriormente, comprovar host Codex e MCP privado com logs reais, sem confundir runner de CI com host definitivo.

### Índice de artefatos
- `systems/rea/AGENTS.md` — instruções obrigatórias; `systems/rea/README.md` — operação.
- `systems/rea/src/sdk_server.py`, `systems/rea/plugin.json`, `systems/rea/.codex-plugin/plugin.json`, `systems/rea/skills/rea-setup/SKILL.md`, `systems/rea/skills/rea-operacao/SKILL.md` — engine/plugin.
- `systems/rea/docs/PRIVATE_MCP_TUNNEL.md`, `systems/rea/docs/PLUGIN_PORTABLE.md`, `systems/rea/docs/PRODUCTION_ACCEPTANCE.md`, `systems/rea/docs/RUNTIME_DOCTOR.md` — gates de integração.
- `systems/rea/docs/DATACENTER_MEMORY.md`, `systems/rea/datacenter/schema.sql`, `systems/rea/scripts/rea_memory.py`, `systems/rea/scripts/continuity_pipeline.py` — persistência.
- `.github/workflows/rea-memory-qa.yml`, `systems/rea/tests/test_rea_memory_continuity.py` — testes.

### Protocolo de retomada sem perda de decisões
1. Ler `AGENTS.md` e **este arquivo**; checar HEAD/checks/revisões no GitHub PR #119. Nunca confiar em SHA antigo deste checkpoint como estado atual.
2. Marcar fatos `CONFIRMADO_NO_GITHUB`, `RELATADO_HISTORICAMENTE`, `NAO_VERIFICADO` ou `BLOQUEADO`; não tratar instrução de instalação como execução.
3. Acrescentar nova decisão/pêndencia com ID estável, data, origem, SHA e impacto; **não apagar** histórico. Revogação deve ter `SUBSTITUIDA_POR` e prova de autorização.
4. Memória SQLite recebe apenas metadados seguros no host autorizado. Nunca adicionar segredos, cópias integrais de chats ou dados privados ao GitHub/CI.
5. Encerrar sempre com bloqueios e próxima ação. Sem `PRODUCTION_COMPLETE=YES` sem aceite operacional comprovado.

**Prompt para futura conversa:** "Retomar REA_INDEPENDENTE no GitHub WhiteChronos/ChatGPT, PR #119. Ler systems/rea/AGENTS.md, systems/rea/spec/memoria.md e docs/DATACENTER_MEMORY.md; conferir HEAD/CI/ECC; preservar DEC-REA e PEND-REA e não reexecutar etapas comprovadas. REA independente de MCE; sem merge, deploy ou descoberta MCP inventada."



---

### 2026-10-29 — DEC-REA-013: vínculo permanente da memória ao GitHub

| ID | Registro | Estado |
| --- | --- | --- |
| DEC-REA-013 | GitHub é a fonte documental canônica do REA; Issue #121 (https://github.com/WhiteChronos/ChatGPT/issues/121) é índice estável, e systems/rea/spec/memoria.md é o histórico versionado. Alterações REA/Skills exigem atualização documental datada no mesmo commit para passar a CI de continuidade. | VIGENTE |
| PEND-REA-008 | Não há captura automática de conversas do ChatGPT, inclusive discussões sem commit. É preciso registrar nova decisão explicitamente no GitHub. | NAO_IMPLEMENTADO |

Gate independente: systems/rea/scripts/github_memory_gate.py; workflow: .github/workflows/rea-github-memory.yml. O texto anterior foi preservado. HEAD histórico de partida: 59dc18d73d758708ea9e652121bff1a17087fd59. A operação MCP remota continua condicionada a autorização e teste real. PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 - DEC-REA-014: Evento de memoria diretamente no GitHub

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-REA-014 | Issue #121 recebe eventos tecnicos publicaveis estruturados, sem commit manual na captura inicial. Evento: https://github.com/WhiteChronos/ChatGPT/issues/121#issuecomment-6506917648 . O leitor github_memory_inbox.py identifica registros ainda nao espelhados no Markdown, sem conceder aprovacoes. | VIGENTE |
| PEND-REA-009 | Nao existe exportacao nativa automatica de todas as mensagens do ChatGPT para este repositorio. Captura exige acao GitHub autorizada. Seguranca ECC integral, configuracao de check obrigatorio e comprovacao MCP no host continuam pendentes. | EXTERNAL_GATE |

O gate audita todos os commits desde 88413a907366512169b6b0812296c64a8ee11ee5; um commit tardio de memoria nao pode ocultar codigo anterior sem registro. Sem merge, deploy nem ativacao remota do REA. PRODUCTION_COMPLETE=NO.


---
### 2026-10-29 - DEC-REA-015: integracao seletiva entre conversas e correcao Windows

| ID | Decisao e evidencia | Estado |
| --- | --- | --- |
| DEC-REA-015 | Manter REA independente, com tres Skills do plugin 0.1.1 e a entrada de investigacao existente; adicionar fechamento operacional que coordena scripts existentes, sem outro motor. Integracao no indice central e roteamento entre conversas respeitam alvo autorizado e disponibilidade real. | VIGENTE |
| PEND-REA-010 | Tunel privado e cliente preparados no host, mas chave runtime segura, doctor, descoberta no Codex/Web, aceite e revisao de seguranca externa continuam dependencias verificaveis. Nao declarar producao ou captura automatica de chats. | EXTERNAL_GATE |

Partida: ba1d3301522cbed6e5d71f5683057d6728f7de9e. Corrigidos bloqueio de hardlinks tambem no Windows, decodificacao UTF-8 do historico e entrega HTTP 401/403 no Windows por descarte limitado de corpo rejeitado, sem processar o payload. Regressao local: 74 PASS, 2 SKIP por privilégio de symlink ausente; seis testes SDK/protocolo passaram com SDK 2.3.0. Scanner Bandit 1.8.6 sobre src/scripts/skills: sem achados medios/altos. Novo workflow de seguranca do produto e matriz QA Windows/Linux. Ver docs/CODEX_GLOBAL_ROUTING.md. Comentarios ECC antigos nao sao encerrados por esta memoria; nova revisao externa continua necessaria. Sem merge/deploy; PRODUCTION_COMPLETE=NO.

---

### 2026-11-08 - Fechamento interno e corpus sintetico (DEC-REA-016/017)

| ID | Registro | Estado |
| --- | --- | --- |
| DEC-REA-016 | O usuario decidiu pelo fechamento interno sem deploy externo. O motor REA e o MCP stdio podem operar localmente em root expressamente autorizado; uso por Codex ou ChatGPT Web e opcional, separado, sem alegar conexao. Evidencia de validacao Windows recebida: 76/76 testes da suite e 3/3 testes focados MCP no SHA 4dd0c90fefd3b788cae22225394c5390568283df. Registro de origem: https://github.com/WhiteChronos/ChatGPT/issues/121#issuecomment-6721603060. | VIGENTE_SEM_HOMOLOGACAO |
| DEC-REA-017 | Acrescentar corpus de referencia sintetico, reproduzivel e sem codigo privado: arestas Python/JS, candidatos de risco, hashes, ocultacao de literal, bloqueio de caminhos e sinalizacao de cobertura parcial. Estender teste de embalagem para a Skill rea-fechamento-operacional. Nao adicionar manifesto ECC artificial ou alterar o motor sem diagnostico. | IMPLEMENTADO_PENDENTE_CI |
| PEND-REA-011 | ECC: aviso de manifesto/harness para a Skill deve ser validado com o mantenedor ECC; manifestos reais ja existem em systems/rea/plugin.json e .agents/plugins/marketplace.json. Testar corpus no CI do novo HEAD, obter revisao humana da PR #119, comprovar operacao no root autorizado e DataCenter privado somente se utilizado. Nao fazer merge antes de todos os gates e autorizacao especifica do novo SHA. | REVIEW_REQUIRED |

Esta revisao nao instala Codex, nao cria cliente tunel, nao analisa codigo de terceiros, nao altera a operacao privada e nao concede aprovacao. PRODUCTION_COMPLETE=NO.

---

### 2026-11-09 - Evidencia local de retomada e DataCenter piloto

Registro local para revisao; ainda nao publicado no GitHub nem homologado.
Base de codigo: a8f13140655c1e35a487d288fd25f468147bce24 (PR #119 draft).
Preservados DEC-REA-016/017: fechamento interno sem deploy; Web opcional.

- Suite Windows/Python 3.12.14: 77 PASS, 2 SKIP por indisponibilidade de symlink.
  Bandit no src/scripts/skills: zero resultados medios/altos selecionados, sem erros.
- SDK MCP 2.3.0 no SHA atual: initialize, sete ferramentas, status, inventario,
  leitura, analise estatica, SHA e recusas de parent/oculto comprovados em fixture
  autorizada, sem alterar fonte. Chamadas nativas tambem responderam neste chat.
  Checkout configurado no host permanece 4dd0c90; cinco arquivos Python de src
  conferem byte a byte com a base atual. Nao alegar atualizacao do pacote completo.
- Por pedido atual do usuario, criado DataCenter piloto exclusivo fora de Git,
  banco vazio e ACL restrita ao usuario proprietario e SYSTEM. Backup inicial e
  restauracao verificados; ensaio separado com dois eventos sinteticos confirmou
  cadeia, digest, bloqueio de sobrescrita e de alteracao append-only.
- Criptografia do volume nao verificada, recuperacao em outro volume nao testada,
  revogacao MCP nao exercitada, revisao humana e aceite permanecem pendentes.
  Nenhum dado privado importado. Nao ha captura automatica de conversas.
- Consulta atual: 13 checks GitHub com success, nenhum review registrado;
  protecao de branch retornou 403 ao conector. Aviso ECC/harness neutral permanece
  para decisao do mantenedor, sem manifesto ficticio. Indice central acessivel na
  branch codex/documentation-system-20261027; nao presumir incorporacao na main.

PRODUCTION_COMPLETE=NO. Sem merge, deploy, mudanca de credenciais ou publicacao.

### 2026-11-09 - Complemento: protecao, revisao por IA e regressao de caminhos

| ID | Registro | Estado |
| --- | --- | --- |
| DEC-REA-018 | O usuario dispensou revisao humana para o fechamento tecnico interno e solicitou revisores por IA. Claude sem login foi substituido por revisor Codex com autorizacao expressa. Nao chamar o resultado de parecer humano. Nao altera gates de merge/deploy nem concede autorizacao por SHA. | VIGENTE_NO_ESCOPO_INTERNO |
| PEND-REA-012 | Custodia independente da chave de backup, disposicao externa do alerta ECC e confirmacao do resultado da solicitacao Cloud devem permanecer explicitas; nao declarar desastre recuperavel nem revisao remota executada sem prova. | LIMITES_OPERACIONAIS |

BitLocker confirmado por diagnostico administrativo somente leitura: volume do
DataCenter 100% criptografado, protecao ativa. Backup cifrado em disco distinto
restaurado com cadeia integra; adulteracao recusada. Chave mantida separada do
backup, sem revelar conteudo. Nao houve alteracao de BitLocker ou credenciais.
Ensaio de revogacao/reinicio restringiu-se a subprocesso stdio proprio; registro
nativo preservado. Ruleset Chronos ativo, PR e control-plane check obrigatorios,
sem bypass; nenhum merge autorizado.

Revisao independente por IA encontrou fuga lexical por '..' na restauracao e
ausencia de verificacao previa de ACL no helper. Tres testes de regressao
falharam antes da correcao em fixtures sinteticas. Corrigidos helper de entrega
e _path canonico para recusar traversal, symlink/junction e resolver caminhos.
O helper verifica ACL antes de descriptografar e confere staging/destino; seus
gates de backup nao dependem de assert removivel por Python -O. Regressao
adicional reproduziu handle aberto em falha de ACL; corrigida limpeza Windows.
Os detalhes locais, caminhos privados e chaves nao sao copiados a esta memoria.

Esta e uma revisao local posterior ao HEAD a8f13140655c1e35a487d288fd25f468147bce24,
sem publicacao no GitHub. Preservar fonte, novo hash local, logs e pareceres.
PRODUCTION_COMPLETE=NO ate resolver limites restantes; nao alegar 100% universal.

Segunda revisao por IA: reproduzidos em fixtures Windows inventario atravessando
junction e alias hardlink de arquivo externo; bloqueados ambos e revalidado cada
descendente por _resolve antes de ler/hash. Falhas sinteticas de verificacao de
destino SQLite reproduziram handle aberto na limpeza; backup/restore agora usam
_session tambem para o destino. O writer do backup privado verifica ACL de
diretorios e dos arquivos novos antes de gravar material sensivel. Registrar
resultados finais e hash do pacote local; esses reparos nao estao no HEAD da PR.
