# REA INDEPENDENTE — Engenharia Reversa / MCP / Arena

**Produto independente do MCE e de qualquer projeto Excel.** Este pacote NÃO é uma distribuição do REA oficial e não incorpora seu código. Possui uma ponte MCP própria, motor estático Python/JS/TS, grafo de imports, candidatos a risco com evidências SHA-256, análise de repositórios a partir de catálogo local, Arena de quatro perspectivas, interface Web de loopback e testes.

## REA oficial (opcional e separado)

O produto original é https://github.com/morluto/rea (`rea-agents`). Instale-o pelo método oficial em host com Node/npm compatíveis:

```bash
npx rea-agents setup
```

Escolha seu agente, revise mudanças e reinicie-o. A conexão no ChatGPT Web depende de servidor HTTPS compatível, permissões e autenticação no host. O nosso código não instala o REA oficial, não o substitui, nem prova que suas ferramentas foram descobertas.

## REA interno: executar sem MCE

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/
python scripts/rea_native_doctor.py
python scripts/create_mcp_config.py --data-root /DIRETORIO_DE_CODIGO_AUTORIZADO
python src/server.py --transport stdio --root /DIRETORIO_DE_CODIGO_AUTORIZADO
```

O servidor MCP expõe sete ferramentas estritamente de leitura; o root autorizado não deve incluir documentos sigilosos desnecessários. O ranking `rea_repositories_top10` recebe `catalog` com caminho relativo a um JSON próprio, formato `{"captured_at":"2026-10-28", "reviewed":[{"repo":"owner/project","score_editorial":75,"license":"MIT","head":"SHA"}]}`. Os escores são fornecidos pelo usuário, não medidos automaticamente.

## Painel Web local (não publicado)

```bash
export REA_MCP_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(36))')"
python src/web_app.py --root /DIRETORIO_DE_CODIGO_AUTORIZADO --host 127.0.0.1 --port 8769
```

Abra http://127.0.0.1:8769/ no mesmo host. Não exponha a porta na Internet sem autenticação e revisão adicional. Nenhum token é publicado neste ZIP.

## Garantias e limites

- Inspeção estática limitada a 100 arquivos / 8 MB; sem execução de aplicações alvo, descompilação, observação dinâmica ou análise binária nativa.
- O código independente não pode enviar arquivos à nuvem nem acessar caminhos fora do root permitido.
- O motor Arena local compara quatro abordagens por heurística; não é torneio de 100 subagentes.
- `REA_RUNTIME=UNAVAILABLE` se as ferramentas nativas não forem realmente expostas no host; arquivos de configuração não representam host ativado.
- O sistema não contém P&ID, lógica de matrizes ou modelos de Excel.

## Preparacao para producao (nao homologacao automatica)

Ver `docs/PRODUCTION_ACCEPTANCE.md` para a lista de evidencias obrigatorias e verificacao fail-closed. Exemplo de comando: `python scripts/production_smoke.py --url https://rea.sua-organizacao.example/mcp`. O resultado automatico nao certifica `PRODUCTION_COMPLETE`.

## Nova conexao padronizada ao ChatGPT (privada)

Para executar as sete ferramentas pelo SDK MCP **oficial v2**, sem alterar o motor REA interno:

```bash
python -m pip install -r requirements-mcp.txt
python src/sdk_server.py --root /CODIGO_AUTORIZADO --transport stdio
```

A conexao ChatGPT Web precisa de permissao do workspace e de um **Secure MCP Tunnel** configurado no host real. Consulte `docs/PRIVATE_MCP_TUNNEL.md` para autenticacao do tunel, validacao por `tunnel-client doctor`, modo de falha segura e gates de aceite. Nao executar `--host 0.0.0.0`. Ter codigo no GitHub ou passar CI nao equivale a host descoberto.

## Novo gate de integridade do release REA (sem depender do MCE)

Antes de instalar, execute `python scripts/release_integrity.py --zip /ARQUIVO_REA.zip --expected-sha256 SHA256_FORA_DO_ZIP --expected-git-sha COMMIT40_APROVADO`. O verificador nao extrai nem executa codigo; exige cobertura exata do manifesto e recusa caminhos inseguros, links, duplicatas e divergencias de hash. `INTEGRITY_PASS` **nao significa producao homologada**. Consulte `docs/RELEASE_INTEGRITY.md`.

## Plugin REA independente para Codex e ChatGPT Web (2026-10-29)

Este repositorio agora inclui `plugin.json` no formato portatil Agent Plugins e um overlay `.codex-plugin/plugin.json`, com as Skills `rea-setup` e `rea-operacao`. O motor `src/sdk_server.py` continua independente, somente leitura e restrito a loopback/stdio. Instalacao de Skills ou plugin **nao** cria conexao MCP remota; verificar `docs/PLUGIN_PORTABLE.md` para onboarding, runtime real e Secure MCP Tunnel autorizado. Nao acoplar MCE nem expor servidor publicamente.

## DataCenter SQL e memoria persistente independente (29/10/2026)

Memoria operacional SQLite versionada, DataSheet, busca, backup/restauracao e pipeline de status read-only descritos em `docs/DATACENTER_MEMORY.md`. Os bancos reais ficam em host privado. CI de seguranca e testes: `.github/workflows/rea-memory-qa.yml`. MCP e host ChatGPT Web dependem de configuracao e aceite externos. `PRODUCTION_COMPLETE=NO`.

## Memória canônica e retomada de contexto

Ler primeiro [`spec/memoria.md`](spec/memoria.md) e `AGENTS.md`, depois consultar `docs/DATACENTER_MEMORY.md` e o HEAD/CI do [PR #119](https://github.com/WhiteChronos/ChatGPT/pull/119). Os registros DEC-REA/PEND-REA preservam decisões, evidências e pendências. A memória é versionada no GitHub; o SQLite privado não captura conversas automaticamente.


## Memoria GitHub sem dependencia do ChatGPT

Issue indice permanente: https://github.com/WhiteChronos/ChatGPT/issues/121. Arquivo canonico: [spec/memoria.md](spec/memoria.md). Contrato: [docs/GITHUB_MEMORY.md](docs/GITHUB_MEMORY.md). Gate: .github/workflows/rea-github-memory.yml. Decisoes precisam ser registradas no GitHub; conversas nao sao importadas automaticamente.
