# REA independente — contrato operacional

Sistema dedicado a engenharia reversa autorizada, com proteção de dados, inventário SHA-256, relatórios rastreáveis e análises estáticas. Não depende de outros produtos de engenharia.

- Usar upstream `morluto/rea` quando efetivamente instalado e descoberto; caso contrário, identificar a ferramenta local como independente e limitada.
- Escopo de caminhos sempre restrito ao root autorizado. Negar symlink de escape, credenciais, chaves e arquivos ocultos.
- Sem engenharia reversa em alvos não autorizados, bypass de licenças, captura indevida ou exfiltração.
- Evitar alegar execução de 100 agentes ou que o ranking automatizado é empírico.
- Não operar serviços em rede pública; exigir autenticação e revisão de segurança para qualquer implantação.
- Não modificar outros projetos nem arquivos analisados; análises são read-only.

## Leitura obrigatória de memória e continuidade (2026-10-29)

- Antes de qualquer alteração ou revisão REA, consultar `systems/rea/spec/memoria.md`, `systems/rea/docs/DATACENTER_MEMORY.md` e HEAD/CI do PR #119.
- Aplicar os registros DEC-REA e PEND-REA; ao final, acrescentar decisões novas à memória com data, evidência, SHA, testes e gate. Nunca sobrescrever decisões antigas para simular aprovação; documentar `SUBSTITUIDA_POR`.
- O banco SQLite é privado e não sincroniza automaticamente mensagens do ChatGPT; o GitHub permanece a fonte do código e do histórico documental.
- Nunca transferir dados, segredos, conteúdo de código analisado, backup ou conversas completas ao repositório público; manter o REA independente do MCE.
- Antes de afirmar host descoberto, MCP conectado ou `PRODUCTION_COMPLETE=YES`, exigir evidência operacional independente e aceite humano. Configuração/CI são prova insuficiente.


## Vinculo GitHub da memoria (2026-10-29)

- Indice permanente: https://github.com/WhiteChronos/ChatGPT/issues/121
- Consultar systems/rea/spec/memoria.md e systems/rea/docs/GITHUB_MEMORY.md antes de cada nova investigacao.
- Toda alteracao REA/Skills REA deve incluir registro datado no mesmo commit; gate read-only: .github/workflows/rea-github-memory.yml.
- Nao presumir captura automatica de chats, host MCP, conexao ChatGPT Web, aprovacoes ou producao.
