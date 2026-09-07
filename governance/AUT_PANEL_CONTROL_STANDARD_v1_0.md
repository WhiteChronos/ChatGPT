# AUT Panel Control Standard v1.0

## Objetivo

Controlar a elaboração, validação, renderização e liberação de painéis de automação e controle. A IA pode extrair requisitos candidatos, mas não aprova dimensões, seleção de componentes nem status de emissão.

## Fonte única de verdade

O Data Sheet JSON é o modelo canônico de gabinete, placa, vistas, componentes, UTR/cartões, posições, zona inferior, revisão e contrato de renderização. O renderizador apenas apresenta o que já foi validado.

## Regras de Ouro imutáveis

- **GR-021:** a vista frontal externa/porta é a geometria-mestra.
- **GR-022:** a vista interna frontal tem exatamente a mesma largura e altura externas.
- **GR-023:** a vista lateral é profundidade externa × altura externa.
- **GR-024:** uma única escala global `PX_PER_MM` é usada em todas as vistas.
- **GR-025:** proporção 1:1 obrigatória; escala individual de componente proibida.
- **GR-026:** o canvas cresce após conhecidas as dimensões reais; nunca comprime o painel.
- **GR-027:** bornes, canaleta inferior, curvatura/saída e prensa-cabos são zonas distintas.

Para gabinete 800 × 600 × 300 mm (A × L × P):

- frontal externa = 600 × 800 mm;
- frontal interna = 600 × 800 mm;
- lateral = 300 × 800 mm;
- placa de montagem = elemento interno, por exemplo 550 × 750 mm.

Qualquer divergência dimensional ou distorção resulta em `REPROVADO`.

## Data Center e evidências

Todo componente validado deve registrar fabricante, família, código exato, lifecycle, dimensões, folgas, documento, revisão, página/seção, data de consulta e canal de fornecimento. Campo ausente permanece `PENDING` e produz `HOLD`.

O repositório público guarda somente catálogo redigido, regras, schemas, hashes e relatórios. PDFs de fabricante, documentos internos e dados de cliente não são publicados sem autorização.

## Controle GitHub

O workflow `AUT Panel Quality` executa em pull request e push para `main`:

1. valida o schema do Data Sheet;
2. executa testes de regressão;
3. aplica todas as Regras de Ouro;
4. gera Data Sheet consolidado;
5. gera Data Center SQLite;
6. renderiza SVG proporcional;
7. gera relatório de QA e manifesto SHA-256;
8. verifica integridade dos artefatos;
9. publica os artefatos no workflow.

`REPROVADO` sempre falha o CI. `HOLD` bloqueia release formal. O template público pode rodar com `--allow-hold` apenas para demonstrar pendências reais de gabinete, UTR/cartões e lifecycle.
