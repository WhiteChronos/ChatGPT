# Plugin REA independente para Codex e ChatGPT Web

O manifesto portatil `plugin.json` segue Agent Plugins v1. O overlay `.codex-plugin/plugin.json` e compatibilidade Codex; ambos empacotam as duas Skills. O servidor oficial MCP SDK `src/sdk_server.py` continua **separado da instalacao do plugin no ChatGPT Web**. O plugin nao inclui URL publica inventada nem `mcp.json`: so pode ser vinculado a uma conexao MCP real e aprovada depois do provisionamento do host, ou usado com o Codex stdio local em ambiente autorizado.

## Codex

- Obter release versionado, verificar SHA-256 e Git SHA independentemente.
- Testar `python -m pytest -q tests/` com `requirements-mcp.txt`.
- Instalar/ativar o plugin a partir do pacote conforme o cliente Codex permitir.
- Registrar MCP stdio de forma explicita, com `python src/sdk_server.py --root <codigo_autorizado> --transport stdio` no ambiente correto, **sem** configuracao autonoma de permissao de arquivos.
- Realizar `initialize`, `tools/list`, `rea_bridge_status` via cliente real. Nao contar manifestos como HOST_DISCOVERED.

## ChatGPT Web

- Instalar Skills e criar uma conexao MCP personalizada apenas apos a equipe autorizada provisionar Secure MCP Tunnel ou HTTPS com auth adequada. Ver docs oficiais https://developers.openai.com/api/docs/guides/secure-mcp-tunnels .
- Em Plugins, adicionar servidor MCP personalizado por Tunnel, escolher o `tunnel_id` autorizado e validar `tools/list` e chamada segura. Sem tunel ou endpoint real, **Skill pode funcionar mas ferramentas REA nao**.
- Nenhum atalho com URL ou credencial ficticia e aceitavel.

## Gate final

Nao publicar como plugin de MCP publico sem servidor HTTPS estavel com auth e revisao de seguranca. Sem PR revisado, host/cliente observado, acesso, revogacao e aceite, `PRODUCTION_COMPLETE=NO`.
