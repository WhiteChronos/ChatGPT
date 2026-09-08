# AUT Panel Control Standard v1.1

## Objetivo

Controlar a elaboração, validação, lista de material, renderização e liberação de painéis de automação e controle. A IA pode extrair requisitos candidatos, mas não aprova dimensões, seleção de componentes nem status de emissão.

## Fonte única de verdade

O Data Sheet JSON é o modelo canônico de gabinete, placa, vistas, componentes, UTR/cartões, posições, zona inferior, revisão e contrato de produção. O Data Center mantém os modelos de referência, evidências e o registro das Regras de Ouro. A Lista de Material é derivada desses dois artefatos e passa a ser a fonte obrigatória para a imagem do quadro.

## Regras de Ouro imutáveis

- **GR-021:** a vista frontal externa/porta é a geometria-mestra.
- **GR-022:** a vista interna frontal tem exatamente a mesma largura e altura externas.
- **GR-023:** a vista lateral é profundidade externa × altura externa.
- **GR-024:** uma única escala global `PX_PER_MM` é usada em todas as vistas.
- **GR-025:** proporção 1:1 obrigatória; escala individual de componente proibida.
- **GR-026:** o canvas cresce após conhecidas as dimensões reais; nunca comprime o painel.
- **GR-027:** bornes, canaleta inferior, curvatura/saída e prensa-cabos são zonas distintas.
- **GR-034 — Lista de Material antes da imagem:** a Lista de Material canônica deve ser elaborada e validada antes da imagem do quadro. A imagem deve usar exclusivamente os componentes presentes na BOM vigente. Nenhum componente pode ser acrescentado, removido ou substituído apenas na imagem. Qualquer alteração posterior na BOM invalida a imagem anterior e exige nova renderização e novo QA.

## Sequência obrigatória de produção

A sequência padrão é:

1. `DATACENTER` — cadastrar e validar modelos de referência e evidências;
2. `DATASHEET` — consolidar o modelo canônico do painel;
3. `SELECT` — selecionar os componentes aplicáveis;
4. `BOM` — elaborar e congelar a Lista de Material canônica;
5. `LAYOUT` — posicionar somente os itens constantes na BOM;
6. `RENDER_IMAGE` — gerar a imagem do quadro a partir da BOM/layout vigentes;
7. `QA` — comparar Data Center × Data Sheet × BOM × imagem;
8. `RELEASE` — liberar somente após os gates aplicáveis.

É proibido gerar a imagem como fonte para posterior criação da BOM. Se a imagem evidenciar necessidade de componente adicional, o fluxo deve retornar à BOM, revisar a lista, invalidar a imagem anterior e renderizar novamente.

## Regra de autorização para mudança de padrão

Depois de aprovado um padrão visual, dimensional ou de sequência, ele não pode ser alterado automaticamente. Qualquer mudança futura no padrão exige autorização explícita do responsável do projeto antes da alteração do Pipeline, Script, Data Center, Data Sheet ou padrão visual. Correções estritamente necessárias para manter consistência com uma alteração já autorizada podem ser aplicadas dentro do mesmo escopo de mudança.

Para gabinete 800 × 600 × 300 mm (A × L × P):

- frontal externa = 600 × 800 mm;
- frontal interna = 600 × 800 mm;
- lateral = 300 × 800 mm;
- placa de montagem = elemento interno, por exemplo 550 × 750 mm.

Qualquer divergência dimensional ou distorção resulta em `REPROVADO`.

## Data Center e evidências

Todo componente validado deve registrar fabricante, família, código exato, lifecycle, dimensões, folgas, documento, revisão, página/seção, data de consulta e canal de fornecimento. Campo ausente permanece `PENDING` e produz `HOLD`.

O registro `datacenter/AUT_PANEL_GOLDEN_RULES.json` mantém a GR-034 e seu contrato de rastreabilidade: toda linha da BOM referencia um `catalog_id` do Data Center; toda instância renderizada deve existir na BOM corrente.

O repositório público guarda somente catálogo redigido, regras, schemas, hashes e relatórios. PDFs de fabricante, documentos internos e dados de cliente não são publicados sem autorização.

## Controle GitHub

O workflow `AUT Panel Quality` executa em pull request e push para `main`:

1. valida o schema do Data Sheet;
2. executa testes de regressão;
3. aplica todas as Regras de Ouro;
4. gera Data Sheet consolidado;
5. gera Data Center SQLite;
6. gera a BOM canônica;
7. renderiza o SVG somente após a BOM;
8. verifica que BOM e imagem usam as mesmas instâncias e `catalog_id`;
9. gera relatório de QA e manifesto SHA-256;
10. verifica integridade e ordem dos artefatos;
11. publica os artefatos no workflow.

`REPROVADO` sempre falha o CI. `HOLD` bloqueia release formal. O template público pode rodar com `--allow-hold` apenas para demonstrar pendências reais de gabinete, UTR/cartões e lifecycle.
