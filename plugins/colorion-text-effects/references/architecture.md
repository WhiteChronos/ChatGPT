# Arquitetura local

## Objetivo

Manter uma camada estavel para reutilizar o conhecimento do Colorion sem acoplar o fluxo ao HTML do site nem congelar uma copia completa do upstream.

## Camadas

1. **Upstream**: repositorio oficial do Colorion.
2. **Sync**: `scripts/sync_colorion.py` obtem e interpreta `effects.ts`.
3. **Catalogo**: `references/effects-catalog.json` funciona como cache/snapshot pesquisavel.
4. **Search**: `scripts/search_effects.py` ranqueia candidatos por nome, tipo e texto de exemplo.
5. **Agent/Skill**: `SKILL.md` define como selecionar, adaptar e validar efeitos.
6. **Pesquisa externa**: GitHub e documentacao Web/CSS entram somente quando o catalogo nao resolve a necessidade ou quando o usuario pede alternativas.

## Principios

- Fonte oficial antes de espelhos.
- Snapshot local, mas sincronizavel.
- Sem dependencia Python externa para o nucleo.
- Sem copiar todo o CSS global quando um efeito isolado basta.
- Proveniencia explicita.
- Acessibilidade e `prefers-reduced-motion` preservados.
- Licenca verificada antes de incorporar codigo externo.

## Evolucoes planejadas

- Extrator de snippets por efeito a partir de `global.css`.
- Cache de `effect-data.json` com hash e data de sincronizacao.
- Gerador de variantes React/Next.js/Astro.
- Testes de regressao visual em navegador.
- CI para detectar adicoes/remocoes no catalogo upstream.
- Indice semantico por estilo: tecnico, neon, retro, 3D, editorial, glitch, industrial, sci-fi, minimalista e outros.
