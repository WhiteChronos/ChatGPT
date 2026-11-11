# REA: memoria canonica somente no GitHub

Fonte documental: systems/rea/spec/memoria.md, versionada por Git. Nao depende da memoria nativa do ChatGPT, nao compartilha banco nem runtime com MCE.

## Enderecos persistentes
- Issue indice: https://github.com/WhiteChronos/ChatGPT/issues/121
- Memoria viva: https://github.com/WhiteChronos/ChatGPT/blob/feat/rea-independent-system-20261028/systems/rea/spec/memoria.md
- PR: https://github.com/WhiteChronos/ChatGPT/pull/119
- Gate: systems/rea/scripts/github_memory_gate.py
- Workflow: .github/workflows/rea-github-memory.yml

## Contrato
1. Antes de investigar, ler a memoria do GitHub, PR e HEAD efetivos, checks, comentarios ECC, revisoes e fontes.
2. Alteracoes no REA, SDK MCP, plugin ou Skills vinculadas devem incluir no **mesmo commit** registro datado acrescentado ao memoria.md. Usar IDs DEC/PEND estaveis, referencia e evidencias, sem apagar historico anterior.
3. A CI em pull_request valida memoria, IDs, prefixo historico exato, atualizacao conjunta e ausencia de credenciais obvias. Esse gate somente le dados do repositorio e nao instala servidor MCP.
4. Conversas nao sao capturadas automaticamente. Uma decisao discutida exclusivamente no ChatGPT precisa ser documentada no GitHub antes de integrar a memoria.
5. SQLite operacional, fontes sigilosas, credenciais, logs sensiveis e conversas integrais ficam em host privado. Nao utilizar Desktop Commander ou componentes do MCE.
6. Workflow em branch PR draft nao e check requerido da main ate protecao formal por administrador. CI nao autoriza merge, implantacao, conexao ChatGPT Web nem producao.

## Confirmacao de runtime
A presenca de manifesto/plugin e a passagem da CI nao significam HOST_DISCOVERED nem LIVE_VERIFIED. Exigir tools/list, rea_bridge_status, autenticação, revogacao, rollback e aceite no host real.


## Caixa de entrada estruturada do Issue #121

Decisoes tecnicas publicaveis podem ser registradas imediatamente no Issue https://github.com/WhiteChronos/ChatGPT/issues/121 como comentario com marcador WC_MEMORY_EVENT_V1 e bloco JSON contendo schema=1, system=REA_INDEPENDENTE, kind=DECISION, id=DEC-REA-014 (novo ID para cada evento), date, title, summary, origin=USER_REQUEST e approval=NOT_ENG_APPROVED. Evento inicial: https://github.com/WhiteChronos/ChatGPT/issues/121#issuecomment-6506917648 . Nao incluir codigo de terceiros, documentos privados, segredos ou transcricoes integrais.

O script python systems/rea/scripts/github_memory_inbox.py consulta os comentarios do GitHub de forma somente leitura (GITHUB_TOKEN opcional). Saidas MIRRORED_IN_GIT e ISSUE_ONLY_PENDING_MIRROR distinguem eventos consolidados dos que ainda precisam de revisao/atualizacao do memoria.md. Nao equivale a captura automatica de conversas, nem a aprovacao tecnica.

O workflow de memoria REA usa fetch-depth: 0 para validar todos os commits depois do checkpoint 88413a907366512169b6b0812296c64a8ee11ee5; recusa mudanca de codigo sem memoria no mesmo commit, mesmo quando a memoria aparece em commit posterior. Nao ha auto-merge ou deploy.
