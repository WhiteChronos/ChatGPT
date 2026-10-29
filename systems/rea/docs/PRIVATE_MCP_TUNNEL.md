# REA independente — MCP oficial e Secure MCP Tunnel privado

## Escopo e mecanismo escolhido (Arena + Superpowers)

O REA e um **motor interno proprio**, independente do MCE e do REA oficial `morluto/rea`. Esta integracao **nao** instala o REA oficial nem declara que esse upstream foi executado. O motor local de analise estatica continua sendo o mesmo, com acesso limitado ao diretorio autorizado. O novo `src/sdk_server.py` registra as sete ferramentas somente leitura no **SDK Python MCP oficial v2** e oferece transporte **stdio** ou **Streamable HTTP exclusivo em loopback**.

A recomendacao para ChatGPT Web e **Secure MCP Tunnel oficial**, que cria conexao de saida no host dentro da rede, sem abrir portas publicas. Referencia: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels . Um servidor HTTPS publico OAuth 2.1, se necessario, exige projeto e autorizacao de seguranca diferentes; **nao** substituir OAuth por token estatico em plugin publicado.

## Instalar no host de execucao real

1. Confirmar que o host tem Python 3.12+ e diretório de codigo de fonte **autorizado para acesso por um modelo**; limitar usuarios/arquivos e backups. Nao apontar para diretorios com segredos, credenciais, P&IDs ou documentos de projeto sem autorizacao.
2. Instalar as dependencias, preferencialmente no venv de service account sem privilegios:

   ```bash
   python -m pip install -r requirements-mcp.txt
   python -m pytest -q tests/
   python src/sdk_server.py --root /CAMINHO/SOMENTE_CODIGO_AUTORIZADO --transport stdio
   ```

   O ultimo comando e um servidor **stdio que aguarda um cliente MCP**. Nao imprime logs em stdout. Para diagnostico, usar um **cliente MCP oficial** e validar `initialize`, `tools/list`, `rea_bridge_status`, arquivo bloqueado e ferramenta autorizada. `mcp` v2 implementa a negociacao atual e os protocolos legados suportados pelo SDK.
3. Opcional: ensaio HTTP exclusivo em loopback:

   ```bash
   python src/sdk_server.py --root /CAMINHO/SOMENTE_CODIGO_AUTORIZADO --transport streamable-http --host 127.0.0.1 --port 8768
   ```

   Abrir somente `http://127.0.0.1:8768/mcp` no mesmo host. O SDK exige Host/Origin autorizados; uma tentativa `--host 0.0.0.0` deve ser bloqueada. A porta **nao** deve ser publicada na Internet.

## Integrar privadamente (somente quando houver autorizacao, tunel e host)

1. Um administrador do OpenAI Platform cria o `tunnel_id` e associa o tunel a **organizacao e workspace ChatGPT corretos**. Permissoes `Tunnels Read + Manage` sao necessarias para criar, e `Read + Use` para conectar; nao assumir que a conta tem acesso.
2. O operador instala o `tunnel-client` oficial no host que alcanca o REA. Sem publicar nenhuma chave em codigo/CI:

   ```bash
   export CONTROL_PLANE_API_KEY='CHAVE_GERENCIADA_FORA_DO_REPOSITORIO'
   tunnel-client init \
     --sample sample_mcp_stdio_local \
     --profile rea-privado \
     --tunnel-id TUNNEL_ID_AUTORIZADO \
     --mcp-command 'python /OPT/REA/src/sdk_server.py --root /DADOS_AUTORIZADOS --transport stdio'
   tunnel-client doctor --profile rea-privado --explain
   tunnel-client run --profile rea-privado
   ```

3. No ChatGPT Web, com permissao para MCP personalizado, instalar o plugin por **Add custom MCP server > Tunnel**, selecionar o tunel e conferir a ferramenta `rea_bridge_status` por uma chamada real. O `tunnel-client` deve permanecer rodando. Guardar `tunnel_id`, identidade do host, SHA do release e sinais de saúde, **nunca a chave** no relatorio.
4. **STOP** se `tunnel-client doctor` falhar, se `tools/list` nao apresentar exatamente as ferramentas permitidas, se o host/conta nao corresponderem, se houver segredo exposto ou se o monitoramento/rollback nao estiver pronto. Testar revogacao de acesso e reinicio, sem acessar codigo sigiloso desnecessario.

## Gates para afirmar `PRODUCTION_COMPLETE`

- CI dos novos commits, controle `Chronos`, revisao e merge aprovados na `main`.
- Servidor instalado no host real com codigo e deps versionados, usuario restrito e diretorio permitido revisado.
- `tunnel-client doctor` no host real, status conectado e inventario de sete ferramentas observado no **ChatGPT Web**.
- Smoke real com ferramenta read-only, autorizacao e negacao de acesso indevido, auditoria, observabilidade, disponibilidade, revogacao e rollback.
- Aceite operacional e de seguranca por responsaveis identificados. **Sem esses registros, a producao continua pendente.**

## Diferenca de escopo

`src/server.py` (antigo) e `scripts/production_smoke.py` (teste HTTPS com token estatico) permanecem para testes locais e retrocompatibilidade. Eles **nao** constituem prova de conformidade com MCP Web, OAuth, integracao ao ChatGPT, nem justificam exposicao publica. Para conexao nova, usar `src/sdk_server.py` com SDK oficial e tunel privado.
