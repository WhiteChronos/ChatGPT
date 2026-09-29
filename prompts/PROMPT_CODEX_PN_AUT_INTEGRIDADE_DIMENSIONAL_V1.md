# PROMPT CODEX - PN-AUT: integridade dimensional, fabricante e entrega

**Estado deste documento:** especificacao de implementacao; nao e certificado de engenharia nem comprovante de execucao.
**Consulta:** 2026-09-28.
**Repositorio de trabalho:** WhiteChronos/ChatGPT.
**Referencia inspecionada:** PR #23, branch feat/aut-panel-control-v1, commit a3d8c7d86e6403c46a0fcdb751bbedfdc526d66d. Resolver o HEAD atual antes de qualquer alteracao.

## Missao

Corrigir a cadeia real de elaboracao dos paineis PN-AUT. Os itens visuais 1 (frente interna com porta aberta) e 2 (frente externa com porta fechada) precisam mostrar o MESMO corpo de gabinete, com as mesmas dimensoes e os mesmos componentes fixos. A porta e a IHM devem ser instancias fisicas unicas; abrir a porta altera sua transformacao rigida, nao cria uma segunda porta. As entradas inferiores devem corresponder ao fornecimento do fabricante MAIS as modificacoes de projeto explicitamente aprovadas.

Nao resolver o problema gerando outra imagem livre. Nao aceitar a presenca de regras em YAML, nomes de agentes, um comentario de PR, um hash ou testes de fixtures como prova de conformidade da imagem entregue. Demonstrar a rastreabilidade entre dados, geometria efetiva, projecao e arquivo publicado.

## 1. Governanca e levantamento inicial

Ler AGENTS.md, Golden Rules, pipeline canonico, Data Center, Data Sheet, LI vigente, template, memoria operacional e registros de fontes antes de escrever codigo. Preservar LI R02, historico, quantitativos congelados e dimensoes aprovadas. Este pedido autoriza preparar a correcao de software e propor controles; nao autoriza mudar a engenharia silenciosamente, reduzir folgas, aprovar produtos sem fonte, alterar limites para obter PASS nem fazer merge automatico.

Inspecionar pelo menos:
- pipeline/render_panel_scaled.py;
- pipeline/aut_panel_control.py, especialmente gerar_svg;
- pipeline/panel_render_gate.py;
- pipeline/panel_3d_geometry_gate.py;
- pipeline/corrigir_proporcao_imagem.py;
- schemas/panel_render_manifest_v1.schema.json;
- pipeline/pipeline.yaml;
- li/PN-AUT-01_LI.json;
- templates/panel_template.yaml;
- datacenter/AUT_PANEL_VISUAL_STANDARD_V3.yaml;
- agents/AUT_PANEL_AGENT_SYSTEM.yaml;
- skills/aut-panel-engineering/SKILL.md;
- .github/workflows/ e os testes associados.

Verificar se o demonstrador PN_AUT_GEOMETRIA_V1/panel_math.py existe no checkout. Um arquivo entregue anteriormente no chat nao e automaticamente arquivo do repositorio. Se estiver disponivel, revisar e testar antes de aproveitar; nao presumir que foi integrado.

Registrar HEAD, diff inicial, arquivos lidos, hashes de entrada e comando de testes existente. Reproduzir primeiro os erros com casos minimos e guardar os resultados. Apresentar um plano curto antes de alterar interfaces ou contratos bloqueados. Priorizar corrigir o fluxo existente em vez de criar outro validador paralelo nao chamado.

## 2. Correcao de fonte: gabinete e saidas

Fonte oficial pesquisada: Schneider Electric NSYCRN86300, corpo nominal W=600, H=800, D=300 mm; a composicao publicada informa um corpo, uma porta, uma placa de entrada de cabos e uma fechadura. O fabricante disponibiliza referencias CAD 2D e STEP na pagina indicada ao final.

A LI R02 consultada contem quantidade 8 para CG-01..08, catalog_id SCHNEIDER-GLAND-REF e descricao de familia M20/M25/M32 a selecionar pelo cabo. Isso comprova o quantitativo registrado no projeto, NAO oito prensa-cabos instalados de fabrica, oito pre-furos, diametros ou coordenadas de furacao.

Separar no modelo:
1. factory_configuration: gabinete e itens efetivamente fornecidos;
2. project_modifications: furacoes, prensa-cabos, IHM, ventilacao e acessorios de projeto;
3. evidence: origem, documento/revisao, pagina ou secao e status de cada atributo.

Nao trocar 8 por 0 na LI congelada. Se faltarem fontes da personalizacao, preservar a linha historica e abrir HOLD_CABLE_ENTRY_DESIGN. Nao escrever "8 saidas conforme fabricante". A ausencia de numero de furos no catalogo nao prova que o numero seja zero.

Obter o desenho oficial de fundo/placa de entrada e o CAD correspondente ao codigo exato. Confirmar montagem, limites de usinagem, protecao aplicavel e dimensoes do conjunto escolhido. Nao copiar grelhas, fechaduras ou ventiladores do poster como se fossem fornecimento de fabrica. A placa de montagem deve ser confirmada pelo seu proprio codigo e documento.

## 3. Modelo canonico unico

Manter uma montagem parametrica por painel, em milimetros, com IDs estaveis para corpo, porta, placa, IHM, equipamentos e cada entrada. Uma linha com quantity=N precisa ser expandida em N instancias fisicas rastreaveis; nao desenhar um retangulo para representar silenciosamente N pecas.

Cada instancia deve ter: instance_id, li_tag, catalog_id, quantidade de origem, parent_id, superficie de montagem, geometria ou proxy declarado, dimensoes oficiais, referencia de fonte, transformacao, folgas e estado de verificacao. Nao usar dicionarios que descartem instancias repetidas pelo li_tag.

Preferencia de geometria: CAD oficial STEP/IGES; CAD/DXF oficial; reconstrucao parametrica a partir de desenho oficial; por ultimo, envelope simplificado explicitamente marcado PROXY. Proxy nao e modelo detalhado do fabricante e nao libera render executivo fotorealista.

Normalizar unidades uma unica vez e registrar a conversao. Conversao mm/m e rotacao rigida sao legitimas; deformacao para caber nao. Verificar a geometria avaliada, incluindo parent transforms e modificadores, e nao apenas object.scale ou dimensoes declaradas em JSON. Medir em referencial local e transformar os vertices conforme a pose; AABB mundial muda com rotacao legitima.

## 4. Contrato matematico

Usar um unico fator s em px/mm para as vistas dimensionais. Definir e documentar eixos; por exemplo x=largura, y=profundidade, z=altura. Para a vista frontal sem inclinacao:

    u = ox + s*x
    v = oy + s*(H-z)

Itens 1 e 2 usam o mesmo operador de projecao frontal; so a origem da prancha muda para as pecas fixas. A porta usa a mesma geometria e uma rotacao rigida em torno da dobradica:

    P_aberta = T_dobradica * R(theta) * inverse(T_dobradica) * P_fechada

Invariantes do corpo nominal, excluindo a folha aberta e acessorios salientes:

    W1_px = W2_px = s*W
    H1_px = H2_px = s*H
    W1_px/H1_px = W2_px/H2_px = W/H

Exemplo de teste, nao nova selecao de produto: s=2, W=600 e H=800 resultam em 1200 x 1600 px para ambos os corpos. Lateral ortografica correspondente: 600 x 1600 px para D=300.

A imagem completa do item 1 pode ser mais larga devido a porta aberta, chamadas e margens; nao comparar a largura total desse bloco com a largura nominal do corpo. Comparar planos de referencia ou primitivas/object-ID da envoltoria fixa.

Para entradas inferiores aprovadas: os IDs, tipos, diametros e coordenadas locais pertencem a uma unica lista no modelo. Nas duas vistas frontais equivalentes, os conjuntos projetados e as multiplicidades devem coincidir, salvo oclusao calculada e justificada. Nas vistas laterais varias pecas podem ficar ocultas; nao inventar uma nova quantidade visivel para tornar os numeros iguais.

Usar Fraction/Decimal para dimensoes e coordenadas de projeto quando apropriado. Usar tolerancia numerica documentada nas operacoes CAD/raster. Distinguir precisao computacional, arredondamento em pixel e tolerancia de fabricacao. Nao instituir 1% como tolerancia de engenharia universal.

## 5. Ocupacao e reserva de cabos

Reservar o volume real para passagem dos cabos, acesso a prensa-cabos, curvatura e manutencao. Os 150 mm pedidos no estudo sao requisito de projeto a verificar, nao minimo universal imposto por qualquer norma. A altura grafica da reserva deve ser s*150; o retangulo de anotacao nao substitui um volume livre no modelo.

Testar interferencias de componentes, folgas de fabricante, corpo, porta/IHM, placa e cabos. Usar AABB como triagem conservadora, refinando por OBB/BRep/mesh quando necessario. Distinguir interfaces mecanicas intencionais de colisoes proibidas. Avaliar porta fechada e percurso de abertura quando o detalhamento existir.

Se o hardware nao couber: HOLD_LAYOUT_CAPACITY, diagnostico das restricoes, alternativas de rearranjo ou gabinete maior com codigo e evidencia. Nova dimensao fisica exige revisao e autorizacao; nunca esticar somente uma vista nem reduzir componentes.

## 6. Render e composicao

Gerar os itens 1, 2, 3 e 6 a partir da MESMA montagem. Usar cameras ortograficas nos blocos dimensionais, pixel aspect 1:1, orientacoes definidas e escala comum. Uma vista em perspectiva pode ser adicional e deve ser identificada como ilustrativa; nao substituir a vista dimensional.

Blender: importar geometria congelada por formato suportado/conversao verificada. Nao presumir importacao STEP nativa sem adaptador. Registrar unidades, transformacoes, geometria avaliada, versao, camera e resolucao. Materiais e luz podem mudar; geometria e posicoes nao. Salvar passes de object-ID/silhueta para QA junto do render final.

Revit: somente integrar quando houver necessidade BIM e ambiente autorizado. Usar IFC/revit-ifc/pyRevit; conferir unidades, IDs e geometria apos o intercambio. Nao chamar uso de IfcOpenShell de execucao Revit e nao tornar Revit dependencia obrigatoria do fluxo Python/Blender.

Criar legenda, tabelas, cotas e notas como texto/vetor derivado dos dados. Nao gerar codigos, numeros ou esquemas eletricos com texto sintetizado na imagem. Fonte de dados de carga/LI/I-O/protocolo nao resolvida continua HOLD.

Compor sem resize de vistas aprovadas: somente translacao e acrescimo de canvas. A pagina cresce para conter vistas, tabelas e chamadas. Se exceder memoria/limite de formato, usar SVG mestre, rasterizacao por tiles ou folhas adicionais na mesma escala, declarando a limitacao; nunca reduzir silenciosamente.

Fixar s antes do render. Ao aumentar a resolucao/campo da camera, ajustar os parametros em conjunto para preservar s. Nao calcular tamanho do quadro por uma moldura disponivel.

Formato visual aprovado: azul/branco; topo com itens 1, 2, 3 e 6; arquitetura eletrica, LI, comunicacao, comando, dimensoes, notas e cargas nos demais blocos. Manter ausentes os blocos SEMANTICOS de detalhe dedicado do verso da porta e vista inferior dedicada, anteriormente itens 4 e 8. Isso nao manda remover itens 4 e 8 da LI, nem retirar o planejamento das saidas inferiores. Proibir apenas renumerar os blocos removidos para reintroduzi-los.

## 7. Auditoria do arquivo entregue

Conectar verificadores ao entrypoint real e ao publicador. Uma funcao de QA sem chamada obrigatoria nao e controle operacional.

Reabrir o SVG e o PNG efetivamente produzidos. Auditar geometrias efetivas e transformacoes do SVG, nao so atributos data-* editaveis. Comparar primitivas/passagens object-ID com a projecao do modelo, incluindo corpo, porta, IHM e entradas. Verificar que anotacoes nao encobrem areas criticas.

Hash garante identidade, nao verdade de engenharia. Assinar ou registrar manifesto de proveniencia fora do alcance do agente autor contendo hashes de fontes, LI, modelo, codigo/HEAD, ferramenta, SVG, PNG e pareceres. O publicador deve consumir exatamente os arquivos aprovados. Proibir nova geracao de imagem apos QA.

Comparacao pixel a pixel so e reprodutivel com renderer/fontes/ambiente fixados. Para render fotorealista, separar verificacao exata de entrega, invariantes geometricos e tolerancias visuais de antialiasing. SSIM, perceptual hash e inspecao por IA sao complementos; nao substituem cotas, IDs e quantidades.

## 8. Testes de regressao requeridos

Adicionar testes que falhem antes da correcao. Cobrir, no minimo:
- W/H diferentes entre os corpos dos itens 1 e 2;
- mesmo aspect ratio com escala menor em uma vista;
- mesmo contorno externo com componente interno deformado;
- numero de portas ou IHMs fisicas duplicado;
- quantity>1 nao expandida e IDs duplicados;
- entradas inferiores a mais/a menos ou com coordenadas/modelo diferentes;
- conversao mm/m, parent scale e modificador alterando geometria;
- fonte "oficial" autodeclarada sem documento correspondente;
- panel_views omitido/vazio e schema nao aplicado;
- reserva de cabos inexistente, invadida ou anotada como 150 mas desenhada menor;
- quadro sem capacidade e proibicao de autoaumento do gabinete;
- blocos visuais removidos reaparecendo por outro numero;
- legenda falsa de conformidade/escala e cargas nao confirmadas;
- SVG transformado ou PNG trocado/reduzido apos QA;
- render, politica e aprovacao de commits diferentes;
- artefato de demonstração usado como se fosse o projeto real.

Usar pytest para exemplos, Hypothesis para propriedades geometricas e testes end-to-end do publicador. Informar quantidade real de testes, comandos, falhas e cobertura; nao inventar PASS. Se testes existentes falharem, registrar tambem.

## 9. Agentes e Skills executaveis

Reaproveitar agentes existentes, com responsabilidades e evidencias distintas: SOURCE_VALIDATOR_A/B, CAD_GEOMETRY_GUARDIAN, SCALE_PROPORTION_GUARDIAN, CANVAS_COMPOSITION_GUARDIAN, BLENDER_RENDER_GUARDIAN, QA e MEMORY_CURATOR; adicionar responsabilidade explicita para identidade/furacao/entradas quando faltar.

Cada etapa deve gerar relatorio vinculado ao mesmo modelo e artefato. Nao simular dois revisores independentes rodando a mesma funcao e mudando o nome. Se nao houver segundo agente real, manter essa validacao pendente.

Empacotar procedimentos Python estaveis em Skills com SKILL.md, scripts delegando ao nucleo canonico, referencias e testes. Nao copiar a implementacao do gate para cada Skill. Expor as Skills pelo caminho de descoberta documentado do Codex (.agents/skills ou plugin registrado), mantendo uma unica fonte e evitando duplicatas. Usar o skill-creator/skill-installer nativo quando aplicavel e verificar a descoberta real.

Skills propostas: pn-aut-source-audit, pn-aut-canonical-geometry, pn-aut-cable-entry-audit, pn-aut-render-compose, pn-aut-delivery-audit. Estes nomes representam escopos propostos, nao instalacao concluida.

## 10. GitHub + Codex: duas automacoes separadas

A. CI deterministico em pull_request, push protegido e workflow_dispatch: instalar dependencias fixadas, validar contratos, executar testes, gerar projeto real em ambiente isolado, auditar modelo/SVG/PNG, publicar somente artefatos aprovados. Guardar diagnosticos HOLD em area separada e identificada. Falha tecnica nao pode ser convertida em sucesso por continue-on-error ou allow-hold na etapa de release.

B. Codex: executar diagnostico/revisao/proposta de patch usando integracao GitHub ou openai/codex-action. Prompt versionado; resultado estruturado; permissoes minimas; nenhum auto-merge. Codigo/politica/testes gerados pelo agente precisam de aprovacao humana e CI independente. @codex review e pedido de revisao, nao comprovante de renderer executado.

Separar jobs de render/teste sem segredos, job Codex e job de publicacao. Nao expor credenciais a codigo de PR nao confiavel. Usar eventos/atores autorizados, environment approval, limites de custo/tempo/repeticao, actions fixadas por SHA e dependencias por versao/hash. Nao executar checkout de codigo nao confiavel com segredos em pull_request_target. Em workflow_run, validar origem, autor, SHA e artefatos antes de confiar no resultado.

Verificar disponibilidade de credencial, permissao, runner e motor sem imprimir segredos. Se nao houver acesso, registrar HOLD_TOOL_ENVIRONMENT. Nenhum teste deve acessar ou comandar CLP/equipamento real.

## 11. Entregas e conclusao

Entregar: diagnostico reproduzivel; plano/diff; testes; modelo canonico; fontes registradas; vistas tecnicas; render derivado; manifesto; auditoria do arquivo final; Skills descobertas/testadas; workflows; atualizacao append-only da memoria; PR draft e rollback por commit.

Separar sempre: SOFTWARE_TESTS, SOURCE_VALIDATION, GEOMETRY_CHECK, IMAGE_DELIVERY_CHECK, HUMAN_APPROVAL e ENGINEERING_RELEASE. Ser verde em uma categoria nao aprova as outras. Nao escrever "nunca mais erra"; demonstrar quais falhas os controles detectam e quais permanecem fora do escopo.

## Fontes iniciais a reverificar

- Fabricante, produto Brasil: https://www.se.com/br/pt/product/NSYCRN86300/caixa-de-sobrepor-metalica-800x600x300mm/
- Fabricante, composicao e CAD: https://eshop.se.com/sa/nsycrn86300-spacial-crn-plain-door-w-o-mount-plate-h800-w600-d300-ip66-ik10ral7035.html
- Codex GitHub Action: https://developers.openai.com/codex/github-action
- Codex e GitHub: https://developers.openai.com/codex/integrations/github
- Descoberta e construcao de Skills: https://developers.openai.com/codex/skills
- Action oficial: https://github.com/openai/codex-action
- Catalogo de Skills: https://github.com/openai/skills
- Ferramentas CAD/render/QA: consultar prompts/CATALOGO_OPEN_SOURCE_PN_AUT_V1.md no repositorio e CATALOGO_OPEN_SOURCE_PN_AUT.json no pacote entregue.

**Limite da verificacao de fontes nesta preparacao:** a pagina oficial identifica uma porta e uma placa de entrada; nao foi importado o STEP do fabricante nem validada a furacao do painel completo. Nao atribuir essa verificacao ao fabricante.
