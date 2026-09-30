# PROMPT - PASSO 7 - VERIFICACAO FINAL DA IMAGEM - V1

ID: PROMPT-STEP7-FINAL-IMAGE-VERIFICATION-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITO: STEP6_ENGINEERING_IMAGE_DOCUMENT_FROZEN

## OBJETIVO

Verificar matematicamente e visualmente a imagem final de cada PN antes da liberacao.

O Passo 7 nao cria e nao corrige a imagem. Ele mede, compara, reprova/aprova e encaminha o erro para a etapa correta.

## ENTRADAS

Carregar:
- PROJECT_NUMBER;
- PANEL_ID;
- revisao;
- LI/Carga congeladas;
- STEP5 canonical assembly manifest;
- STEP5 multiview render manifest;
- STEP5 fingerprints;
- STEP6 engineering document manifest;
- imagem final;
- H/W/D controlados;
- camera/projection manifests;
- MODEL 001;
- tolerancias congeladas.

## CAMADAS DE VERIFICACAO

### 7.1 Identidade e revisao

Confirmar:
- mesmo PROJECT_NUMBER;
- mesmo PANEL_ID;
- mesma revisao;
- mesma LI/Carga;
- mesmo ASSEMBLY_HASH;
- mesmo fingerprint da imagem fisica inserida.

### 7.2 Concordancia das vistas

Comparar:
- H/W/D;
- enclosure bbox;
- door bbox;
- eixo de dobradica;
- instancias fisicas;
- escala de objetos;
- camera registrada.

Toda vista deve vir da mesma montagem.

### 7.3 Proporcao ortografica

Frontal/interna:
ratio_esperado = W_mm / H_mm
ratio_observado = bbox_width_px / bbox_height_px

Lateral/corte:
ratio_esperado = D_mm / H_mm

Calcular erro percentual.

### 7.4 Escala px/mm

Frontal:
px_per_mm_x = bbox_width_px / W_mm
px_per_mm_y = bbox_height_px / H_mm

Lateral:
px_per_mm_x = bbox_width_px / D_mm
px_per_mm_y = bbox_height_px / H_mm

Comparar eixos e comparar todas as vistas dimensionais contra a escala global.

### 7.5 Perspectiva/3-4

Nao usar comprimento aparente para validar medida.

Usar:
- matriz de camera;
- landmarks 3D canonicos;
- landmarks 2D renderizados;
- erro de reprojecao RMSE em pixels.

### 7.6 Enquadramento

Verificar:
- nenhum clipping;
- margem minima;
- viewports dentro do canvas;
- blocos do MODEL 001 inteiros;
- centralizacao quando a vista foi definida como centered;
- nenhum bloco dimensional reduzido.

### 7.7 Cotas

Comparar H/W/D impressos diretamente com os valores controlados.

Proibido validar cota medindo pixel do raster quando o manifest controlado existe.

### 7.8 Regressao visual

Quando existir baseline aprovado da mesma vista/revisao:
- SSIM;
- edge/mask overlap;
- perceptual hash;
- diferenca de dimensao/canvas.

Essas metricas sao secundarias. Nao podem aprovar geometria que falhou nos manifests.

## TOLERANCIAS INICIAIS

Defaults do sistema:
- aspect ratio ortografico <= 0.25%;
- mismatch px/mm por eixo <= 0.25%;
- desvio da escala comum entre vistas <= 0.50%;
- reprojecao <= 1.5 px;
- tolerancia de dimensao CAD/modelo <= 0.10 mm;
- desequilibrio de margem centered <= 5%.

Esses valores sao defaults internos de QA, nao limites de norma.
Se o projeto congelar valores mais rigorosos, usar os mais rigorosos.
Nunca afrouxar tolerancia para obter PASS.

## ROTEAMENTO DE ERRO

Retornar ao Passo 4:
quantidade/LI/Carga incorreta.

Retornar ao Passo 5:
geometria, H/W/D, porta, escala de objeto, camera, reprojecao ou proporcao fisica incorreta.

Retornar ao Passo 6:
canvas, enquadramento documental, cotas, legenda, blocos ou composicao incorreta.

## FERRAMENTAS

- Wolfram: verificacao matematica independente;
- OpenCV: camera/reprojecao/registro/contornos;
- scikit-image: SSIM;
- pytransform3d: transformacoes rigidas;
- trimesh/Open3D: geometria e bbox;
- Blender: metadata de camera/render;
- FreeCAD/CadQuery/build123d: geometria;
- ImageHash/Visual Regression Tracker: QA visual secundaria;
- Remote Desktop Commander: ponte de execucao local autorizada.

## SAIDAS

- FINAL_IMAGE_QA_MANIFEST
- MATHEMATICAL_IMAGE_PRECISION_REPORT
- MULTIVIEW_CONSISTENCY_REPORT
- FRAMING_AND_CANVAS_REPORT
- VISUAL_REGRESSION_REPORT
- STEP7_FINAL_IMAGE_VERIFIED

## REGRA FINAL

A IMAGEM SO E LIBERADA QUANDO A GEOMETRIA, A MATEMATICA, O ENQUADRAMENTO E A RASTREABILIDADE CONTAM A MESMA HISTORIA.
