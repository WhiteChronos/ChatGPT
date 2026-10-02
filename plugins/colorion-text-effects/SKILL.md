---
name: colorion-text-effects
description: Pesquisar, selecionar, adaptar e implementar efeitos de texto animado em HTML/CSS com base no projeto Colorion Text Effects e em fontes abertas verificadas. Usar quando o usuario pedir efeitos de texto, titulos animados, neon, glitch, blueprint, microchip, 3D, gradientes, animacoes tipograficas, snippets CSS, conversao de um efeito do Colorion para outro texto/cores/framework, atualizacao do catalogo Colorion, ou pesquisa de alternativas e solucoes tecnicas no GitHub para efeitos tipograficos.
---

# Colorion Text Effects

## Objetivo

Usar o Colorion Text Effects como fonte principal de referencia para efeitos tipograficos em CSS e manter uma base local pesquisavel e sincronizavel para uso futuro.

## Fluxo principal

1. Ler `references/upstream.md` para confirmar a fonte oficial e a arquitetura do projeto.
2. Consultar `references/effects-catalog.json` para localizar efeitos conhecidos.
3. Quando a tarefa depender do estado atual do upstream, executar `scripts/sync_colorion.py` para atualizar o catalogo antes de decidir.
4. Para busca local rapida por nome, tipo ou texto de exemplo, executar `scripts/search_effects.py <termos>`.
5. Selecionar o efeito pelo objetivo visual e pelo contexto do usuario; nao escolher apenas por semelhanca do nome.
6. Preservar os tokens `--ink`, `--ink-2` e `--ink-3` ao adaptar efeitos do Colorion.
7. Preservar `prefers-reduced-motion` quando houver animacao.
8. Usar markup compativel com a estrutura exigida pelo efeito: texto simples, `data-text`, spans por letra, SVG ou markup especial.
9. Gerar HTML/CSS autocontido por padrao. Adicionar JavaScript somente quando o usuario pedir ou quando um novo efeito realmente exigir comportamento que CSS puro nao resolve.
10. Se a solucao nao existir no Colorion, pesquisar alternativas no GitHub e documentacao oficial. Verificar atividade do repositorio, compatibilidade, licenca e riscos antes de recomendar ou incorporar codigo.

## Adaptacao de efeitos

- Trocar o texto sem quebrar efeitos por letra; gerar um indice `--i` para cada caractere quando necessario.
- Para efeitos que usam pseudo-elementos duplicados, manter `data-text` sincronizado com o texto visivel.
- Para efeitos SVG, preservar acessibilidade com `role="img"` e `aria-label`.
- Manter classes do efeito quando a fidelidade ao upstream for importante.
- Permitir re-skin por variaveis CSS antes de alterar regras internas.
- Evitar copiar estilos globais do site quando apenas o bloco do efeito for necessario.

## Pesquisa e desenvolvimento

Ao buscar solucoes novas:

1. Procurar primeiro no repositorio oficial e issues/commits relacionados.
2. Procurar depois repositorios GitHub mantidos e documentacao de CSS/Web Platform.
3. Distinguir claramente codigo oficial, adaptacao local e proposta experimental.
4. Nao importar dependencias apenas para reproduzir um efeito que CSS puro ja resolve.
5. Registrar a origem de qualquer tecnica incorporada em `references/upstream.md` ou em uma nova referencia curta.
6. Nao redistribuir codigo de terceiros sem verificar a licenca aplicavel no momento da incorporacao.

## Saidas esperadas

Entregar conforme o pedido:

- recomendacao de um ou mais efeitos adequados;
- HTML e CSS prontos para uso;
- variante para React/Next.js/Astro quando solicitado;
- adaptacao de texto, paleta, velocidade e escala;
- comparacao tecnica entre efeitos;
- diagnostico de bugs visuais;
- pesquisa de alternativas GitHub;
- atualizacao do catalogo local.

## Recursos

- `references/upstream.md`: fontes oficiais, arquitetura e regras de proveniencia.
- `references/architecture.md`: desenho do sistema local e estrategia de evolucao.
- `references/effects-catalog.json`: snapshot pesquisavel do catalogo.
- `scripts/sync_colorion.py`: sincroniza o catalogo a partir do upstream oficial.
- `scripts/search_effects.py`: pesquisa efeitos no snapshot local.
