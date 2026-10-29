---
name: rea-fechamento-operacional
description: Fechar pendencias de instalacao, integridade, MCP e evidencia do REA independente, distinguindo testes locais, descoberta real pelo Codex, conexao privada web e aceite operacional.
---

# Fechamento operacional REA

Ler primeiro `spec/memoria.md`, `docs/DATACENTER_MEMORY.md`, as Skills rea-setup e
rea-operacao, o HEAD da PR #119 e os comentarios do Issue #121. Resolver caminhos
relativamente a raiz do plugin. Este roteiro nao cria outro motor ou banco.

1. Conferir origin/HEAD, alteracoes humanas, dependencias e integridade do pacote
   pelo verificador existente `scripts/release_integrity.py`. Rodar os testes
   `python -m pytest -q tests` com Python do ambiente REA. Registrar SHA e resultado.
2. Para um alvo de codigo explicitamente autorizado, usar o servidor existente
   `src/sdk_server.py --root <alvo> --transport stdio` com um cliente SDK oficial.
   Verificar initialize, sete ferramentas, rea_bridge_status, chamada de leitura,
   SHA da fonte e negacao de escape/segredo. Nao executar o codigo do alvo.
3. Registrar separadamente teste SDK local e descoberta do host. Para Codex,
   consultar o inventario real da conversa depois de carregar a configuracao.
   `codex mcp list` comprova registro, nao chamada real pelo modelo. Sem ferramenta
   nativa carregada, indicar HOST_RELOAD_REQUIRED ou NOT_DISCOVERED.
4. Para ChatGPT Web, exigir endpoint privado HTTPS ou Secure MCP Tunnel aprovado,
   identidade/workspace e doctor conforme rea-setup. Nao criar porta publica,
   copiar credenciais ou usar Desktop Commander. Sem destino autorizado, manter
   WEB_MCP=NOT_CONNECTED; Skills e plugin nao substituem essa conexao.
5. Rever evidencias do scanner, testes adversariais, root restrito, revogacao,
   observabilidade, backup/restore privado e rollback. Uma observacao local nao
   autentica aprovador nem comprova aceite de producao.
6. Entregar tabela por gate com PASS, BLOCKED, NOT_RUN ou USER_ACTION_REQUIRED,
   fonte, SHA e proxima acao. Atualizar somente a memoria REA e registrar decisoes
   publicaveis conforme GITHUB_MEMORY.md. Nao misturar com MCE nem REA Lab antigo.

Preservar PRODUCTION_COMPLETE=NO ate aceite e comprovacao operacional. Nao fazer
merge/deploy sem autorizacao do SHA, enfraquecer controles, iniciar modelos ou
agentes como efeito deste fechamento. O roteiro e executado durante a tarefa,
sem monitoramento ou captura automatica das conversas.
