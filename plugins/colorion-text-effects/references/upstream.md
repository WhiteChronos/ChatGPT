# Upstream e proveniencia

## Fonte primaria

- Site: `https://text-effects.colorion.co/`
- Repositorio: `https://github.com/ckissi/colorion-text-effects`
- Branch principal observada: `main`

## Arquivos centrais observados

- `src/data/effects.ts`: catalogo de efeitos, nomes, tipos e texto de demonstracao.
- `src/styles/global.css`: CSS global e blocos numerados de cada efeito.
- `src/utils/effectCss.ts`: extrai blocos de CSS, anexa keyframes compartilhados e gera snippets/prompts autocontidos.
- `src/components/Effect.astro`: markup de renderizacao por tipo de efeito.
- `src/pages/effect-data.json.ts`: publica `snippets` e `prompts` como JSON estatico.

## Contratos tecnicos do upstream

- Os efeitos usam tres tokens de cor: `--ink`, `--ink-2` e `--ink-3`.
- Efeitos por letra usam elementos indexados por `--i`.
- Alguns efeitos duplicam o texto via `data-text`.
- Alguns tipos possuem markup especial, como SVG.
- Animacoes devem respeitar `prefers-reduced-motion`.

## Licenca e copia de codigo

O README do upstream declara o projeto como MIT licensed. Em verificacoes futuras, confirme tambem a presenca/estado do arquivo de licenca ou metadados do repositorio antes de redistribuir trechos substanciais de codigo. Prefira referenciar e sincronizar a fonte oficial em vez de manter forks silenciosamente divergentes.

## Politica de atualizacao

1. Sincronizar `effects.ts` a partir do raw oficial.
2. Gerar o snapshot `effects-catalog.json` deterministicamente.
3. Registrar timestamp UTC e URL de origem no snapshot.
4. Nao sobrescrever referencias manuais sem necessidade.
5. Quando houver diferenca entre site, README e fonte atual, considerar `effects.ts` da branch principal como catalogo de codigo e relatar a divergencia.
