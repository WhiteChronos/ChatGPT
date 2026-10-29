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
