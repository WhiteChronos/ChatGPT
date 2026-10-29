# Estado do runtime REA separado

- Motor interno deste ZIP: leitura estatica Python, JavaScript e TypeScript; MCP stdio/HTTP local + Web loopback.
- Implementacao upstream: `https://github.com/morluto/rea` distribuida separadamente por `rea-agents`. Nao embutida.
- Para setup upstream ver README oficial; aprovar alteracoes antes de instalar e reiniciar host.
- Nao confundir `CONFIGURED` com `LOCAL_RUNTIME_HEALTHY`, `HOST_DISCOVERED` ou `LIVE_VERIFIED`.
- Este ZIP nao instala plugin, nao abre porta para Internet, nao cria hospedagem no ChatGPT Web e nao clona codigo upstream.
- GitHub Arena aqui: 4 perspectivas heuristicas, nao 100 agentes independentes.
