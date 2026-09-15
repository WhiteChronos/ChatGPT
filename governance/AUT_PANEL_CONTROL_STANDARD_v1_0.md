# AUT Panel Control Standard v1.3

## Objetivo
Controlar Data Center, Data Sheet, LI quantitativa, Lista de Material, balanço de carga, layout, desenho e liberação dos painéis de automação. Quantidades não podem nascer do desenho: o desenho é sempre um artefato derivado da LI vigente.

## Fonte única de quantidade
A **LI quantitativa** é a única fonte autorizada para quantidade por painel. O Data Center mantém os `catalog_id`, o registro `AUT_PANEL_PANEL_QUANTITIES.json` e o registro de padrões documentais `AUT_PANEL_DOCUMENT_STANDARDS.json`; o Data Sheet mantém o contrato de produção e os grupos de posicionamento associados aos `li_tag`.

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
- **GR-039 — Padrão único de Excel:** o workbook do **PN-AUT-01 é o template mestre**. PN-AUT-02 e todos os futuros quadros devem manter a mesma ordem de abas, blocos, cabeçalhos, cores, organização, congelamentos e fórmulas-base. Apenas dados técnicos específicos do painel podem variar.
- **GR-040 — Padrão visual único da imagem:** cada quadro é gerado em **uma imagem própria**, seguindo o padrão visual aprovado pelo responsável: título/modelo, dimensões de gabinete e placa, aplicação, vista interna frontal com porta aberta, vista frontal externa/porta, vista lateral, lista técnica, arquitetura de conexão, níveis funcionais, características, aplicações/benefícios, referências visuais dos componentes e rodapé técnico. A IHM permanece na porta.
- **GR-041 — Padrão aprovado imutável sem autorização:** nenhum template de Excel, composição visual, disposição de blocos ou identidade aprovada pode ser alterado sem autorização explícita do responsável do projeto. Mudança não autorizada é `REPROVADO`.

## Template mestre de Excel
Identificador: `XLSX-PN-AUT-01-MASTER-R02`.

Ordem obrigatória das abas:
1. `LI - Quantitativo`
2. `Lista de Material`
3. `Carga Geral`
4. `Balanço de Carga`
5. `Regras de Ouro`
6. `Verificação Visual`
7. `Referências`

O PN-AUT-02 deve usar a mesma apresentação estrutural do PN-AUT-01, inclusive geometria das seções, larguras de coluna, hierarquia visual e posição relativa dos blocos. O número real de componentes e os dados do painel permanecem específicos do PN-AUT-02; linhas sem aplicação podem permanecer vazias para preservar o template, sem criar itens fictícios.

## Padrão visual das imagens
Padrão comum: `IMG-AUT-PANEL-MASTER-V1`.

Templates aprovados:
- PN-AUT-01: `IMG-PN-AUT-01-APPROVED-V1`.
- PN-AUT-02: `IMG-PN-AUT-02-APPROVED-V1`.

É proibido substituir esses layouts por outra composição visual por iniciativa automática. O desenho pode atualizar quantidades, modelos e dimensões somente quando a LI/Data Sheet forem revisados, preservando a composição aprovada.

## Sequência obrigatória
1. `DATACENTER` — validar catálogo, registro de quantidades e padrões documentais.
2. `DATASHEET` — consolidar geometria, contratos de LI e templates aprovados.
3. `SELECT` — selecionar componentes aplicáveis.
4. `LI_QUANTITY` — congelar quantitativo correto por `li_tag` e `catalog_id`.
5. `BOM` — gerar a Lista de Material diretamente da LI.
6. `LAYOUT` — posicionar os grupos com as mesmas quantidades da LI.
7. `RENDER_IMAGE` — gerar o desenho somente após validação LI/BOM/layout e do template visual aprovado.
8. `QA` — verificar paridade quantitativa, geometria, template de Excel, template de imagem, hashes e fontes.
9. `RELEASE` — liberar somente sem `REPROVADO` e sem `HOLD` de engenharia aplicável.

É proibido usar uma imagem para criar ou corrigir a quantidade da BOM sem retornar primeiro à LI. Se o desenho indicar necessidade de item adicional, a LI deve ser revisada, sua revisão deve aumentar e todos os artefatos posteriores devem ser regenerados.

## Quantitativos de referência congelados R02
### PN-AUT-01
Banco de bateria: 2 × 12 V / 12 Ah; proteção/distribuição 24 Vcc: 4; relés de interface: 4; bornes de campo PT 2,5: 32; bornes PE/FE/blindagem: 8; prensa-cabos: 8; módulos de I/O: IM 1, DI 1, DO 1, AI 1, RTD 1; IHM: 1 na porta.

### PN-AUT-02
Banco de bateria: 2 × 12 V / 12 Ah; proteção/distribuição 24 Vcc: 3; relés de interface: 4; bornes de campo PT 2,5: 24; bornes PE/FE/blindagem: 6; prensa-cabos: 6; cartões: DI 1, DO 1, AI 1, RTD 1; IHM: 1 na porta.

## Autorização para mudança de padrão
Depois de aprovado, nenhum padrão visual, documental, dimensional, de quantitativo ou de sequência pode ser alterado automaticamente. Alterações futuras exigem autorização explícita do responsável do projeto antes de modificar Pipeline, Script, Data Center, Data Sheet, workbook ou imagem.
