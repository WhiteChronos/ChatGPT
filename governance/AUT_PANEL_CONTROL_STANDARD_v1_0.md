# AUT Panel Control Standard v1.2

## Objetivo
Controlar Data Center, Data Sheet, LI quantitativa, Lista de Material, layout, desenho e liberação dos painéis de automação. Quantidades não podem mais nascer do desenho: o desenho é sempre um artefato derivado da LI vigente.

## Fonte única de quantidade
A **LI quantitativa** é a única fonte autorizada para quantidade por painel. O Data Center mantém os `catalog_id` e o registro `AUT_PANEL_PANEL_QUANTITIES.json`; o Data Sheet mantém o contrato de produção e os grupos de posicionamento associados aos `li_tag`.

## Regras de Ouro imutáveis
- **GR-021:** vista frontal externa/porta = geometria-mestra.
- **GR-022:** vista interna frontal = mesmas dimensões externas.
- **GR-023:** vista lateral = profundidade × altura.
- **GR-024:** uma única escala global `PX_PER_MM`.
- **GR-025:** proporção 1:1; escala individual proibida.
- **GR-026:** canvas cresce; nunca comprime o painel.
- **GR-027:** bornes, canaleta, curvatura/saída e prensa-cabos em zonas distintas.
- **GR-034:** LI/BOM antes do desenho.
- **GR-035:** paridade quantitativa obrigatória LI ↔ BOM ↔ Data Sheet/layout ↔ desenho.
- **GR-036:** mudança de quantidade/catalog_id na LI invalida BOM, layout e desenho anteriores.
- **GR-037:** IHM local obrigatoriamente na porta/tampa do quadro.
- **GR-038:** nunca distorcer componentes para caber; reorganizar ou ampliar gabinete.

## Sequência obrigatória
1. `DATACENTER` — validar catálogo e registro de quantidades do painel.
2. `DATASHEET` — consolidar geometria e contrato de produção.
3. `SELECT` — selecionar componentes aplicáveis.
4. `LI_QUANTITY` — congelar quantitativo correto por `li_tag` e `catalog_id`.
5. `BOM` — gerar a Lista de Material diretamente da LI.
6. `LAYOUT` — posicionar os grupos com as mesmas quantidades da LI.
7. `RENDER_IMAGE` — gerar o desenho somente após validação LI/BOM/layout.
8. `QA` — verificar paridade quantitativa, geometria, hashes e fontes.
9. `RELEASE` — liberar somente sem `REPROVADO` e sem `HOLD` de engenharia aplicável.

É proibido usar uma imagem para criar ou corrigir a quantidade da BOM sem retornar primeiro à LI. Se o desenho indicar necessidade de item adicional, a LI deve ser revisada, sua revisão deve aumentar e todos os artefatos posteriores devem ser regenerados.

## Quantitativos de referência congelados R02
### PN-AUT-01
Banco de bateria: 2 × 12 V / 12 Ah; proteção/distribuição 24 Vcc: 4; relés de interface: 4; bornes de campo PT 2,5: 32; bornes PE/FE/blindagem: 8; prensa-cabos: 8; módulos de I/O: IM 1, DI 1, DO 1, AI 1, RTD 1; IHM: 1 na porta.

### PN-AUT-02
Banco de bateria: 2 × 12 V / 12 Ah; proteção/distribuição 24 Vcc: 3; relés de interface: 4; bornes de campo PT 2,5: 24; bornes PE/FE/blindagem: 6; prensa-cabos: 6; cartões: DI 1, DO 1, AI 1, RTD 1; IHM: 1 na porta.

## Autorização para mudança de padrão
Depois de aprovado, nenhum padrão visual, dimensional, de quantitativo ou de sequência pode ser alterado automaticamente. Alterações futuras exigem autorização explícita do responsável do projeto.
