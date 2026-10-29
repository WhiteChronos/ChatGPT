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
