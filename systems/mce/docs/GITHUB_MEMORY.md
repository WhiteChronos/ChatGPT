# MCE: memoria canonica somente no GitHub

Registro oficial: systems/mce/spec/memoria.md, com historico recuperavel por Git. Este documento nao usa a memoria nativa do ChatGPT.

## Enderecos persistentes
- Issue index: https://github.com/WhiteChronos/ChatGPT/issues/120
- Memoria viva: https://github.com/WhiteChronos/ChatGPT/blob/feat/mce-independent-system-20261028/systems/mce/spec/memoria.md
- PR: https://github.com/WhiteChronos/ChatGPT/pull/118
- Gate de leitura: systems/mce/scripts/github_memory_gate.py
- Workflow: .github/workflows/mce-github-memory.yml

## Contrato
1. Ler sempre a memoria viva e verificar HEAD, PR, CI, revisoes e ECC antes de atuar.
2. Registrar cada decisao ou alteracao relevante em um commit MCE com registro datado acrescido ao final do arquivo canonico. Nunca reescrever historia: retificar com novo evento e referencia de substituicao.
3. GitHub Actions valida que mudancas MCE ou Skills MCE incluem memoria no mesmo commit. Exige preservacao exata do conteudo anterior, IDs DEC/PEND existentes, gate de producao e nenhum segredo obvio. O workflow e read-only.
4. Nao capturar chats automaticamente. Conversa sem registro via PR/Issue ou commit **nao** existe na memoria GitHub. Um agente em nova sessao precisa apenas do repositorio e do Issue indice para retomar.
5. Dados de engenharia confidenciais, arquivos mestre XLSX, base SQLite privada e transcricoes integrais nao entram no repositorio. Memoria documental e DataCenter operacional tem finalidades diferentes.
6. O workflow esta no PR draft e nao equivale a protecao obrigatoria de branch ate administrador a configurar; nada promove merge, deploy nem producao.

## Gate de aceitação
PASS da memoria indica preservacao de contexto versionado, nao execucao no Codex, autenticidade de aprovador, ausencia universal de segredo, homologacao de engenharia ou PRODUCTION_COMPLETE. O operador deve verificar backup, controle de acesso, revisao e autorizacoes humanas externamente.


## Inbox estruturado do GitHub Issue #120

Decisoes tecnicas publicaveis podem ser registradas no Issue #120 como comentario com marcador WC_MEMORY_EVENT_V1 e um bloco JSON contendo schema=1, system=MCE_INDEPENDENTE, kind=DECISION, id=DEC-MCE-014 (novo ID a cada evento), date, title, summary, origin=USER_REQUEST e approval=NOT_ENG_APPROVED. Exemplo verificado: https://github.com/WhiteChronos/ChatGPT/issues/120#issuecomment-6506916337. Nao enviar transcricoes inteiras, dados industriais ou segredos. Github salva o comentario imediatamente, sem commit manual.

Leitura somente consulta: python systems/mce/scripts/github_memory_inbox.py; o token GITHUB_TOKEN e opcional na API. O leitor distingue MIRRORED_IN_GIT de ISSUE_ONLY_PENDING_MIRROR; o segundo exige posterior revisao e consolidacao no arquivo canonico. O gate de continuidade passa a auditar todos os commits depois de bb4a7b43084da406f4a7d78685068c827d301300 com historico Git completo (fetch-depth: 0), sem auto-merge ou aprovacoes.


## Integração cross-chat e revisao de eventos (30/10/2026)

O roteiro oficial de recuperação de estado entre chats agora e `docs/RETOMADA_ENTRE_CHATS.md`. O checkpoint gerado por `scripts/mce_context_bridge.py` (Windows) apenas aponta para GitHub e, se fornecido, resume a integridade do SQLite privado. O gate de memoria continua append-only em cada commit; Issue #120 é inbox publico sob escrita autorizada, sem captura automatica de conversas.

**Alerta de semantica:** `PEND-MCE-014` tem assuntos diferentes no Issue e na memoria.md. O estado `MIRRORED_IN_GIT` calculado somente pelo ID nao prova conteudo correspondente: preservar ambos e exigir revisao humana antes de conciliacao.


## Reconciliacao fechada por hash de falha historica (DEC-MCE-044)

O audit de todos os commits revelou a excecao **historica unica**, no commit `7003af5c4e73c17a84f6905140c0a52aa65f3943`: DEC-MCE-036 foi removida do texto corrente ao substituir a interpretacao incorreta de bordas pela DEC-MCE-037. As duas versoes anteriores permanecem preservadas pelo proprio Git, com blobs `c2e9a91deebe1a8af41458b674cb7401ae0bb290` e `0d4be2f554746b17d28ee1caf5935f5f52b6fca7`.

O verificador historico so aceita essa anomalia mediante correspondencia **simultanea** de SHA completo do commit, blobs antigo/novo e motivo da falha, aferidos no repositório Git real. Nessa unica transicao, ainda verifica identidade MCE, IDs, protecao contra segredos e mudanca de memoria no mesmo commit. Todas as demais transicoes continuam exigindo prefixo textual identico e atualizacao datada; nenhuma permissao generica de reescrita foi adicionada. Qualquer novo desvio requer processo separado, nunca inclusao automatica em lista de excecoes.

Essa reconciliacao documental nao repara bytes inexistentes, nao confirma host/restore, e nao autoriza merge/deploy. Issue #125 mantem gates de anexos e DataCenter em aberto; somente CI Windows do SHA exato pode declarar auditoria PASS.
