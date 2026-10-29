---
name: rea-setup
description: Preparar e diagnosticar o plugin REA independente no GitHub, Codex ou ChatGPT Web, com MCP oficial read-only, teste de tools/list e Secure MCP Tunnel. Acionar ao instalar, ativar, conectar, depurar descoberta, validar host ou comprovar operacao do REA sem acesso ao computador remoto.
---

# REA independente - setup seguro

Este plugin inclui Skills e o servidor Python existente. **A instalacao das Skills nao instala nem inicia o servidor no ChatGPT Web**. Nunca usar o sistema MCE nem importar seus modulos.

1. Verificar a versao do release e o HEAD SHA do PR REA no GitHub. Nao tratar um PR draft como implantado.
2. Escolher um diretorio de codigo autorizado para inspecao. Bloquear segredos, chaves, documentacao de engenharia confidencial e symlinks de escape.
3. No ambiente autorizado de desenvolvimento, instalar as dependencias do produto: `python -m pip install -r requirements-mcp.txt`, executar `python -m pytest -q tests/` e iniciar `python src/sdk_server.py --root /DADOS_AUTORIZADOS --transport stdio` quando um cliente MCP estiver pronto. O servidor stdio nao retorna por si so.
4. Verificar com um cliente MCP oficial a negociacao initialize, `tools/list` (sete ferramentas), `rea_bridge_status`, arquivos autorizados e recusas de arquivos proibidos. Guardar logs sanitizados e SHA.
5. No ChatGPT Web, seguir o guia de Secure MCP Tunnel oficial (https://developers.openai.com/api/docs/guides/secure-mcp-tunnels). Um administrador autorizado associa o tunnel_id ao workspace e a organizacao corretos. O operador configura a chave em ambiente seguro, nunca neste chat/arquivo, e executa `tunnel-client doctor --profile rea-privado --explain`. Sem sucesso do doctor, nao continuar.
6. Em Plugins > Adicionar servidor MCP personalizado > Tunel, selecionar o tunnel_id e aprovar o registro. Exigir tools/list observado no ChatGPT Web e uma chamada read-only real. Registrar `HOST_DISCOVERED` apenas com inventario efetivamente observado; `LIVE_VERIFIED` apenas apos chamada real, negativa de acesso e revogacao testadas.
7. Verificar monitoramento, disponibilidade, rollback, revisao do PR e aceite de seguranca antes de qualquer producao. Sem provas completas, `PRODUCTION_COMPLETE=NO`.

Nao usar URL inventada, token compartilhado ou porta publica. Para Codex, usar o servidor MCP local com configuracao explicitamente autorizada no host; arquivos `.codex-plugin` sao manifestos, nao prova de carregamento no processo.
