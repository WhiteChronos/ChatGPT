# PROMPT - PASSO 5 - IMAGEM FÍSICA FIEL DE CADA PN - V1

ID: PROMPT-STEP5-PN-IMAGE-FIDELITY-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITO: STEP4_LI_LOAD_FROZEN

## OBJETIVO

Gerar primeiro a imagem física de cada PN separadamente, com aparência realista de um painel montado e fidelidade dimensional entre todos os ângulos.

O Passo 5 não inclui legenda, dados do quadro, arquitetura elétrica, arquitetura de comunicação, diagrama de comando ou bloco documental final. Isso pertence ao Passo 6.

## UMA ÚNICA MONTAGEM

Cada PANEL_ID/revisão possui uma única montagem 3D canônica em milímetros.

Todas as vistas derivam da mesma montagem.

É proibido:
- redesenhar o gabinete em outra vista;
- recriar a porta/tampa em outra escala;
- alterar largura/altura/profundidade para melhorar composição;
- deformar a tampa;
- mover componentes somente para uma câmera;
- gerar uma segunda geometria para a vista 3/4.

## TAMPA/PORTA

A tampa/porta é um único objeto rígido.

Seu H/W/espessura, recortes, HMI, dobradiças e acessórios são invariantes.

Abrir/fechar = aplicar somente transformação rígida em torno do mesmo eixo de dobradiça.

A posição da câmera pode mudar. A geometria não.

## DIMENSÕES

H, W e D vêm do projeto e da geometria validada.

Toda vista dimensional usa projeção ortográfica/calibrada.

A vista 3/4 pode ser isométrica ortográfica ou perspectiva controlada para realismo, mas nenhuma cota é inferida da perspectiva.

## REALISMO

Usar referências de montagem real:
- manuais de gabinete;
- CAD/desenhos oficiais;
- instruções de montagem;
- referências de fiação/montagem;
- normas e evidências do Passo 3;
- treinamento/vídeos como apoio secundário.

Materiais, iluminação e sombras podem ser realistas, mas não podem esconder conflito geométrico.

## FERRAMENTAS

Geometria:
CAD do fabricante -> FreeCAD/CadQuery/build123d/OpenCascade.

QA geométrico:
trimesh/Open3D.

Render:
Blender após congelamento da geometria.

Matemática:
Wolfram.

Regressão visual:
OpenCV + ImageHash suplementar.

Plugins generativos:
to3D/Adobe/ImageGen somente como apresentação; sem autoridade dimensional.

## QA MULTIVISTA

Validar:
- mesmo ASSEMBLY_HASH;
- mesmo objeto da porta;
- mesmo bbox da porta;
- mesmo bbox do gabinete;
- mesmo H/W/D;
- mesma lista de instâncias físicas;
- escala de objetos = 1,1,1;
- mesmo eixo de dobradiça;
- transformações rígidas;
- câmeras registradas;
- nenhuma alteração geométrica por render.

## SAÍDA

Por PN:
- CANONICAL_3D_ASSEMBLY_MANIFEST;
- MULTIVIEW_RENDER_MANIFEST;
- imagem frontal fechada;
- imagem interna/porta aberta;
- imagem lateral/3-4;
- corte de profundidade quando necessário;
- STEP5_MULTIVIEW_QA_REPORT.

Gate:
STEP5_PN_IMAGE_FIDELITY_FROZEN.
