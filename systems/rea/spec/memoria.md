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
