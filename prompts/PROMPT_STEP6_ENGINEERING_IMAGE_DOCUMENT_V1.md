# PROMPT - PASSO 6 - DOCUMENTO VISUAL DE ENGENHARIA DO PN - V1

ID: PROMPT-STEP6-ENGINEERING-IMAGE-DOCUMENT-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITO: STEP5_PN_IMAGE_FIDELITY_FROZEN

## OBJETIVO

Usar a imagem física congelada no Passo 5 e montar o documento técnico visual de cada PN, sem alterar o painel.

## BLOCOS OBRIGATÓRIOS

- imagem física validada do PN;
- legenda dos principais componentes;
- dados do projeto/quadro;
- arquitetura elétrica;
- arquitetura de comunicação;
- diagrama de comando;
- dimensionamento do painel.

Usar MODEL 001 como padrão de composição.

## REGRA GEOMÉTRICA

O Passo 6 não redesenha o painel.

Se houver erro físico, retornar ao Passo 5.

É proibido corrigir geometria com edição raster/generativa.

## CANVAS GROW-ONLY

Nenhum bloco dimensional pode ser reduzido para caber.

Processo:
1. determinar tamanho nativo de cada bloco;
2. posicionar os blocos;
3. calcular bounding boxes;
4. aumentar o canvas até comportar tudo;
5. manter escala dimensional em 1,0 x 1,0.

O tamanho final da imagem/documento é consequência do conteúdo.

## DIMENSIONAMENTO

As cotas vêm diretamente de H/W/D controlados.

Não medir raster para obter cota.

Não usar perspectiva para calcular profundidade.

Frontal:
H x W reais.

Lateral/corte:
D real no eixo de profundidade.

Wolfram pode conferir relações, projeções e dimensões.

## DIAGRAMAS

Arquitetura elétrica:
derivada da topologia de potência/carga validada.

Arquitetura de comunicação:
derivada do inventário de endpoints, gateways, switches e protocolos validados.

Diagrama de comando:
derivado da lógica/I/O/comunicação aprovados.

Não inventar dispositivo, protocolo, DI/DO ou intertravamento.

Preferir:
- QElectroTech;
- SchemDraw/SVG;
- NetworkX/SVG;
- CairoSVG.

B&A Diagrams, tldraw e Miro servem para revisão, não como autoridade.

## LEGENDA/DADOS

A legenda deve mapear tags principais para descrição e modelo.

Dados do quadro devem usar PROJECT_NUMBER, PANEL_ID, revisão e dados técnicos reais.

Não usar logos decorativos grandes.

## QA FINAL

Validar:
STEP5 fingerprint = imagem inserida;
LI = instâncias físicas;
H/W/D = cotas;
carga = arquitetura elétrica;
endpoints = comunicação;
I/O/lógica = comando;
nenhum bloco dimensional reduzido;
canvas suficiente;
legibilidade preservada.

Gate:
STEP6_ENGINEERING_IMAGE_DOCUMENT_FROZEN.
