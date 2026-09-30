# PROMPT MASTER — ELABORAÇÃO COMPLETA DE PROJETO PN — V1

**ID:** PROMPT-MASTER-ELABORACAO-PROJETO-PN-V1
**Status:** MANDATORY / CONTROLLED
**Aplicação:** todo novo painel PN e toda revisão de painel PN existente
**Modelo visual:** PN-IMAGE-MODEL-001
**Diretriz visual:** PROMPT-DIRETRIZ-IMAGEM-PN-V1

## REGRA CENTRAL

> O projeto governa os dados. A LI/BOM governa as quantidades. O Data Sheet governa a revisão do painel. O MODEL 001 governa somente a forma do documento visual.

Nunca usar imagem, memória informal ou painel anterior para sobrescrever dados canônicos.

## ETAPA 0 — BOOTSTRAP DO SISTEMA

1. Carregar Golden Rules, pipeline, Data Center, memória metodológica, registros de plugins e controles de evolução.
2. Verificar se o PROJECT_NUMBER já existe no repositório e carregar seu histórico quando aplicável.
3. Não iniciar a LI/Carga antes do fechamento das ETAPAS 1, 2 e 3; não iniciar layout/imagem antes do fechamento da ETAPA 4.

## ETAPA 1 — LEVANTAMENTO DOCUMENTAL + NÚMERO DO PROJETO + QUANTIDADE DE PAINÉIS

Esta é a primeira etapa de engenharia do projeto.

### 1.1 Identidade do projeto

Todo projeto de painéis deve possuir obrigatoriamente:
- PROJECT_NUMBER;
- título/descrição quando disponível;
- revisão do projeto quando disponível;
- cliente/local quando aplicável.

PROJECT_NUMBER identifica o projeto completo.
PANEL_ID identifica um painel dentro daquele projeto.

Todo artefato downstream deve carregar:
PROJECT_NUMBER + PANEL_ID + DOCUMENT_TYPE + REVISION + STATUS.

### 1.2 Levantamento documental

Antes de LI/BOM, cálculo, seleção, layout ou imagem:
1. reunir os documentos recebidos;
2. cadastrar cada documento como REF-001, REF-002, ...;
3. registrar código, revisão, data, origem, idioma, link, página/seção e aplicação no projeto;
4. identificar documentos faltantes;
5. registrar conflitos.

### 1.3 Quantidade de painéis

Determinar, pelos documentos controlados:
- quantidade total de painéis;
- PANEL_ID de cada painel;
- função;
- localização quando disponível;
- documento/página que comprova sua existência.

Não transformar automaticamente em painel:
- I/O remoto;
- gateway;
- caixa de campo;
- caixa de junção;
- field device;
- equipamento instalado dentro de outro painel.

### 1.4 Saída e gate

Saída:
PROJECT_INTAKE_MANIFEST

Status de aprovação:
STEP1_SCOPE_FROZEN

Se documentos divergirem sobre número de painéis/PANEL_ID:
HOLD_SCOPE_CONFLICT

Até STEP1_SCOPE_FROZEN ficam bloqueadas as etapas de definição técnica do painel e todas as etapas downstream.

## ETAPA 2 — DEFINIÇÃO PARAMÉTRICA DOS PAINÉIS E MOTOR DE PERGUNTAS

Carregar obrigatoriamente:
- datacenter/AUT_PANEL_STEP2_PANEL_DEFINITION_V1.json;
- prompts/PROMPT_STEP2_DEFINICAO_PARAMETRICA_PAINEL_V1.md;
- memory/AUT_PANEL_PARAMETRIC_PROJECT_MEMORY.yaml;
- datacenter/AUT_PANEL_CATALOG_ARCHIVE_POLICY_V1.json.

### 2.1 Objetivo

Para cada painel do PROJECT_INTAKE_MANIFEST:
1. reunir tudo que já é conhecido;
2. resolver automaticamente o que puder ser sustentado por documentos, Data Center, memória, fabricante ou normas;
3. gerar perguntas somente para lacunas reais;
4. transformar respostas e evidências em parâmetros versionados;
5. reduzir perguntas futuras pela reutilização validada desses parâmetros.

### 2.2 Ordem antes de perguntar ao usuário

Consultar nesta ordem:
1. documentos controlados do mesmo projeto;
2. Data Center do projeto;
3. memória do mesmo PROJECT_NUMBER;
4. memória do mesmo PANEL_ID;
5. catálogo/manual oficial já arquivado;
6. fabricante oficial;
7. normas aplicáveis;
8. parâmetros reutilizáveis compatíveis.

Somente depois gerar pergunta.

### 2.3 Perguntas

Toda pergunta deve ter:
- QUESTION_ID;
- PROJECT_NUMBER;
- PANEL_ID;
- tema;
- motivo;
- contexto já conhecido;
- lacuna real;
- impacto;
- opções quando aplicável;
- fontes já consultadas.

As perguntas ao usuário devem seguir:
VISUALIZE + BLOCO FINAL COPIÁVEL.

### 2.4 Memória evolutiva

Cada resposta confirmada ou fato validado vira parâmetro versionado com:
- PARAMETER_ID;
- escopo;
- valor/unidade;
- origem;
- REF_ID;
- revisão;
- status;
- regra de reutilização;
- invalidadores.

Escopos:
GLOBAL_METHOD, PROJECT, PANEL, MANUFACTURER_FAMILY, EQUIPMENT_MODEL.

Nunca promover automaticamente PANEL/PROJECT para GLOBAL.

### 2.5 Catálogos e documentação técnica

Todo catálogo/manual/datasheet usado:
- deve entrar no índice do Data Center;
- deve possuir URL oficial e metadados;
- quando tecnicamente/juridicamente possível, deve ter cópia controlada arquivada;
- deve possuir SHA-256 quando a cópia estiver disponível;
- deve registrar páginas/seções utilizadas.

A memória guarda ponteiro/hash/parâmetros extraídos e não duplica PDFs completos.

### 2.6 Tratamento de erro

Quando um dado estiver errado:
1. detectar conflito;
2. preservar histórico;
3. marcar valor antigo como SUPERSEDED;
4. registrar novo valor/fonte;
5. invalidar downstream;
6. recalcular/revalidar;
7. perguntar somente se a hierarquia das fontes não resolver.

### 2.7 Gate

Saídas:
- PANEL_DEFINITION_MANIFEST;
- PROJECT_PARAMETER_REGISTRY;
- QUESTION_DECISION_LOG;
- CATALOG_INDEX;
- MEMORY_SYNC_RECORD.

Status:
STEP2_PANEL_DEFINITION_FROZEN

Conflito crítico:
HOLD_PANEL_DEFINITION_CONFLICT

Regra:
PERGUNTAR MENOS NÃO SIGNIFICA ASSUMIR MAIS.
PERGUNTAR MENOS SIGNIFICA REUTILIZAR MELHOR DADOS VÁLIDOS, VERSIONADOS E RASTREÁVEIS.

## ETAPA 3 — CONFERÊNCIA NORMATIVA, ESTUDOS ACADÊMICOS E REFERÊNCIAS BIBLIOGRÁFICAS

Carregar obrigatoriamente:
- `datacenter/AUT_PANEL_STEP3_NORMATIVE_ACADEMIC_REVIEW_V1.json`;
- `prompts/PROMPT_STEP3_NORMATIVE_ACADEMIC_REVIEW_V1.md`;
- `memory/AUT_PANEL_NORMATIVE_ACADEMIC_MEMORY.yaml`;
- `datacenter/AUT_PANEL_BIBLIOGRAPHIC_ARCHIVE_POLICY_V1.json`;
- `skills/aut-panel-normative-academic-review/SKILL.md`.

### 3.1 Objetivo

Conferir os assuntos presentes no projeto contra:
- regulamentos;
- normas técnicas;
- documentação oficial de fabricantes;
- artigos revisados por pares;
- estudos acadêmicos;
- livros e handbooks técnicos;
- teses/dissertações;
- referências bibliográficas reconhecidas.

A revisão deve produzir evidência rastreável para sustentar as etapas seguintes.

### 3.2 Aplicabilidade normativa

Para cada norma/regulamento:
- registrar número, título, organismo, edição/ano e status;
- identificar escopo e exclusões;
- registrar a base de aplicabilidade;
- apontar seção/página utilizada;
- registrar requisito extraído e efeito no projeto;
- registrar divergências.

Uma norma relevante não é automaticamente obrigatória. Aplicabilidade deve ser demonstrada por lei/regulamento, contrato, especificação, adoção do projeto, requisito do cliente ou escopo técnico documentado.

### 3.3 Estudos acadêmicos e bibliografia

Para cada artigo/livro/tese:
- registrar autores;
- título;
- ano;
- journal/editora;
- DOI/ISBN/ISSN;
- tipo de estudo;
- tema;
- resultado relevante;
- limitações;
- aplicação ao projeto.

Evidência acadêmica não deve ser tratada como requisito normativo.

### 3.4 Cópias controladas no Data Center

Todo documento utilizado deve possuir registro no Data Center.

Quando a cópia integral for permitida:
- arquivar cópia controlada;
- calcular SHA-256;
- registrar caminho e revisão;
- preservar versões substituídas.

Quando a cópia integral não for permitida:
- não contornar paywall, DRM ou licença;
- registrar metadados;
- link/DOI/ISBN;
- citação bibliográfica;
- resumo técnico;
- páginas/seções consultadas;
- pequenos trechos permitidos quando necessários.

A memória não duplica PDFs/binários completos. Ela guarda ponteiros, hashes, parâmetros/regras extraídos, aplicabilidade, conclusões e conflitos.

### 3.5 Ferramentas de pesquisa

Quando disponíveis:
- Scite e Consensus para literatura acadêmica;
- Tavily e Firecrawl para descoberta de fontes oficiais;
- GitHub/Data Center como armazenamento auditável;
- Engram como memória suplementar;
- Wolfram apenas para cálculos, nunca para decidir aplicabilidade normativa.

### 3.6 Saídas e gate

Saídas:
- NORMATIVE_APPLICABILITY_MATRIX;
- ACADEMIC_EVIDENCE_MATRIX;
- BIBLIOGRAPHIC_REFERENCE_REGISTER;
- CONTROLLED_SOURCE_ARCHIVE_INDEX;
- NORMATIVE_CONFLICT_REGISTER;
- STEP3_REVIEW_SUMMARY;
- MEMORY_SYNC_RECORD.

Status:
`STEP3_NORMATIVE_ACADEMIC_BASE_FROZEN`

Estados de bloqueio:
- `HOLD_NORMATIVE_CONFLICT`;
- `HOLD_NORMATIVE_EDITION`;
- `HOLD_APPLICABILITY_UNCERTAIN`.

Regra:
**PESQUISAR MAIS, PERGUNTAR MENOS, NÃO ASSUMIR. ARQUIVAR A EVIDÊNCIA, NÃO SOMENTE A RESPOSTA.**

## ETAPA 4 — LISTA DE MATERIAIS + CARGA POR PN

Carregar obrigatoriamente:
- `datacenter/AUT_PANEL_STEP4_LI_LOAD_CONTROL_V1.json`;
- `prompts/PROMPT_STEP4_LI_LOAD_V1.md`;
- `memory/AUT_PANEL_STEP4_LI_LOAD_MEMORY.yaml`;
- `skills/aut-panel-li-load-quantification/SKILL.md`.

### 4.1 Saída única do passo

Criar um único workbook do projeto.

Para cada PANEL_ID criar exatamente:
- `<PANEL_ID>_MATERIAIS`;
- `<PANEL_ID>_CARGA`.

Para N painéis devem existir exatamente 2N abas.

Não criar capa, QA, referências, arquitetura, memória, controle ou abas ocultas no workbook emitido.

### 4.2 Engenharia necessária para a LI

Dentro do Passo 4, executar antes da emissão:
1. pesquisa técnica dos fabricantes e fornecedores;
2. fechamento da arquitetura necessária para quantificar componentes;
3. inventário I/O/comunicação e endpoints;
4. seleção de componentes e acessórios;
5. grafo de conexões;
6. carga elétrica por PN;
7. geometria suficiente para medir materiais lineares;
8. cadeia completa de montagem;
9. quantitativo matemático;
10. QA de paridade.

Esses subpassos existem para gerar a LI/Carga correta; não criam abas adicionais.

### 4.3 Materiais

A aba MATERIAIS deve conter todo item fisicamente consumido:
- gabinete/placa/acessórios;
- automação, I/O, rede e gateways;
- fonte/UPS/bateria/conversores;
- proteção/distribuição;
- relés/interfaces;
- bornes e todos os acessórios;
- trilhos DIN;
- canaletas/tampas/fittings;
- fios internos com tipo, seção, cor e metragem;
- PE/equipotencialização/trança de porta;
- cabos de comunicação;
- ferrules/ilhós/terminais/heat-shrink;
- marcação;
- prensa-cabos/tampões/passagens;
- climatização;
- fixadores e kits;
- qualquer peça exigida pelo fabricante para montagem correta.

### 4.4 Quantificação matemática

Metragem interna deve vir de:
`GRAFO DE CONEXÕES + LAYOUT REAL + ROTAS`.

Para cada condutor:
`L_corte = L_rota + L_terminal_origem + L_terminal_destino + L_service_loop`.

Quantidade de compra só pode acrescentar margem de fabricação explicitamente parametrizada.

Materiais lineares como trilho, canaleta, PE e cabos internos também devem ser medidos geometricamente.

Bornes, jumpers, separadores, end stops, ferrules, terminais e marcadores devem ser derivados do grafo/plano de conexões.

### 4.5 Ferramentas

Prioridade:
- CAD/dimensões oficiais do fabricante;
- QElectroTech para esquemas/conexões;
- WireViz/QetWireManager para apoio à lista de fios;
- NetworkX para integridade do grafo;
- OR-Tools para otimização opcional de rotas;
- FreeCAD/CadQuery/build123d/OpenCascade para geometria/medição;
- Wolfram para conferência matemática de comprimento, área, volume, ocupação e carga;
- Remote Desktop Commander para operar ferramentas locais autorizadas;
- B&A Diagrams/tldraw/Miro apenas para revisão visual;
- Tavily/Firecrawl para fabricante/fornecedor;
- Scite/Consensus para suporte técnico/acadêmico.

### 4.6 Links e fornecedores

Cada item deve ter:
- REF_ID;
- link oficial do produto;
- link oficial de datasheet/manual;
- link de fornecedor/distribuidor autorizado quando disponível;
- lifecycle/status.

### 4.7 Carga

A aba CARGA de cada PN deve registrar os equipamentos energizados daquele PN, com:
- fabricante/modelo;
- quantidade;
- tensão;
- corrente/potência;
- duty/diversity apenas quando documentado;
- carga bruta;
- carga de projeto;
- criticidade UPS;
- perda térmica quando disponível;
- REF_ID;
- link oficial.

### 4.8 Evidência de montagem

Usar normas e estudos do Passo 3, manuais oficiais de instalação, catálogos, treinamentos oficiais e vídeos de montagem como apoio secundário.

Vídeo não define corrente, seção, Icu, IP, capacidade ou requisito normativo.

### 4.9 Gate

Saídas:
- LI_LOAD_WORKBOOK;
- MATERIAL_QUANTITY_TRACE;
- INTERNAL_WIRE_CUTLIST;
- LOAD_CALCULATION_TRACE.

Status:
`STEP4_LI_LOAD_FROZEN`.

Bloquear se houver quantidade sem base, metragem estimada sem rota, cadeia de acessórios incompleta, link/modelo divergente, carga sem rastreabilidade ou workbook com abas extras.

## ETAPA 5 — DIMENSIONAMENTO FÍSICO DO QUADRO

Usar a LI congelada do Passo 4 como entrada obrigatória.

O tamanho do quadro é variável por projeto.

Dimensionar a partir de componentes, folgas, canaletas, trilhos, bornes, cabos, raio de curvatura, entrada/saída, porta, IHM, UPS/baterias, climatização, manutenção e reserva física.

Selecionar gabinete real somente depois de provar capacidade.

Nunca copiar H x W x D do MODEL 001 ou de outro PN.

## ETAPA 6 — LAYOUT

1. Uma escala em mm.
2. Uma única instância física de cada item da LI.
3. IHM somente na porta.
4. Separação funcional.
5. Acesso de manutenção.
6. Canaletas e bornes dimensionados.
7. Validar profundidade.
8. Validar interferência porta x placa.
9. Validar climatização e recortes.
10. Validar reserva remanescente.
11. Revalidar metragem interna se a rota física mudar.

Mudança de layout que altere metragem/quantidade retorna ao Passo 4 e gera nova revisão.

## ETAPA 7 — IMAGEM / MODEL 001

Somente após STEP4_LI_LOAD_FROZEN e fechamento dimensional/layout.

Carregar PN_MODEL_001 e PROMPT_DIRETRIZ_ELABORACAO_IMAGEM_PN_V1.

Gerar vistas, arquitetura elétrica, comunicação, comando, dimensionamento, legenda e dados usando a LI/Layout vigentes.

## ETAPA 8 — QA CRUZADO

Verificar:
LI = CARGA = CONEXÕES = LAYOUT = GEOMETRIA = IMAGEM.

Rejeitar dimensões desatualizadas, gateway subdimensionado, quantidade divergente, protocolo inventado, componente duplicado, item sem fonte, metragem incompatível com rota ou imagem com dado antigo.

## ETAPA 9 — MEMÓRIA E DATACENTER

Registrar decisão, erro, solução, fonte, mudança de premissa, invalidadores, parâmetros aprendidos, quantitativos validados e artefatos emitidos.

## ETAPA 10 — EVOLUÇÃO CONTROLADA

O sistema pode detectar padrões de erro, sugerir checks, automações, ferramentas, regras e testes.

Mudança bloqueada exige:
PROPOSTA -> SIMULAÇÃO -> QA -> HUMAN GATE -> VERSÃO.

## PLUGINS / FERRAMENTAS

Usar quando disponíveis:
- Tavily / Firecrawl: pesquisa e crawl de fabricantes/documentação;
- Scite: literatura científica e verificação acadêmica;
- Wolfram: cálculo rigoroso, geometria analítica, área/volume, conversões e checagens matemáticas;
- to3D: conversão de imagem em malha 3D para apoio visual/conceitual; não usar como autoridade dimensional;
- Adobe: acabamento e pós-processamento visual após a geometria técnica estar congelada; não alterar engenharia;
- Airtable: índice estruturado de componentes, fontes, HOLDs, modelos e revisões;
- Coda / Notion: base de conhecimento e documentação operacional;
- Acumen: sinalização de lacunas de contexto recente; toda informação deve ser reverificada;
- Engram: memória persistente suplementar entre sessões para contexto, decisões e histórico de metodologia; nunca substituir GitHub/Data Center/Data Sheet/LI-BOM como autoridade;
- GitHub/Codex: fonte auditável, versionamento, QA e automação.

Plugins nunca substituem documentação oficial.

## FRASE DE CONTROLE

**NÃO PERDER A REFERÊNCIA DO MODELO:**
MODEL 001 = estrutura visual.
Data Sheet = painel/revisão.
LI/BOM = quantidades/modelos.
Data Center = evidências.
Memória = decisões/erros/aprendizado.
Pipeline = ordem obrigatória.

## MEMÓRIA PERSISTENTE / ENGRAM

Quando Engram estiver disponível:
1. recuperar primeiro contexto relevante do projeto pelo PANEL_ID;
2. usar o resultado apenas como memória suplementar;
3. reconciliar qualquer lembrança com GitHub, Data Center, Data Sheet, LI/BOM e documentos controlados;
4. nunca promover memória Engram diretamente a fato de engenharia;
5. gravar apenas resumos não sensíveis de decisões, erros confirmados, regras metodológicas e marcos do projeto;
6. não gravar credenciais, segredos, dados pessoais sensíveis ou material incompatível com a política de segurança;
7. se a escrita for bloqueada ou indisponível, continuar com a memória canônica do repositório sem reduzir os gates.

Precedência:
GitHub/Data Center/Data Sheet/LI-BOM/documentação oficial > Engram > memória informal da conversa.

## STACK DE DIMENSIONAMENTO / 3D / IMAGEM

### Autoridade geométrica
Prioridade obrigatória:
1. CAD oficial do fabricante (STEP/IGES/DXF);
2. reconstrução paramétrica determinística por dimensões oficiais (CadQuery/build123d/OpenCascade/FreeCAD);
3. QA geométrico (trimesh/Open3D);
4. Blender somente para renderização com geometria bloqueada.

### Apoio matemático
Usar Wolfram para:
- volume útil do gabinete;
- área de placa;
- ocupação percentual;
- envelopes geométricos;
- folgas;
- área de canaletas;
- volume de reserva;
- relação de ocupação;
- verificações de conversão e fórmulas.

A entrada do cálculo deve vir de dimensões controladas; Wolfram não inventa medidas.

### Apoio 3D
to3D pode:
- criar prévia 3D a partir de imagem;
- exportar glTF/FBX/OBJ/STL;
- ajudar na visualização conceitual.

to3D não pode:
- provar dimensões;
- substituir CAD oficial;
- definir gabinete;
- validar folgas;
- corrigir geometria do projeto.

### Imagem
Adobe/ImageGen podem melhorar apresentação, composição e acabamento, mas não podem modificar:
- H/W/D;
- posição física congelada;
- quantidade;
- modelo;
- tags;
- topologia;
- arquitetura elétrica/comunicação;
- cotas.

Regra final:
**MATEMÁTICA PODE VERIFICAR A GEOMETRIA; 3D PODE REPRESENTAR A GEOMETRIA; SOMENTE A ENGENHARIA CONTROLADA DEFINE A GEOMETRIA.**

## MELHORIA AUTÔNOMA CONTROLADA

Ao final de cada marco ou quando houver erro/correção:
1. carregar `skills/aut-panel-autonomous-improvement/SKILL.md`;
2. classificar o evento e determinar causa raiz;
3. comparar com histórico de erros e HOLDs;
4. gerar proposta mensurável;
5. calcular prioridade;
6. propor teste de regressão;
7. simular em sandbox quando aplicável;
8. registrar no backlog;
9. pedir HUMAN GATE antes de alterar Golden Rules, revisão congelada, dependência central ou release;
10. depois da aprovação, versionar e medir resultado.

Para ferramentas/plugins/repositórios:
1. carregar `skills/aut-panel-open-source-toolchain/SKILL.md`;
2. identificar lacuna real;
3. preferir ferramenta já validada;
4. registrar candidato;
5. pin de versão/commit;
6. licença;
7. segurança;
8. sandbox;
9. teste/regressão;
10. HUMAN GATE antes de promoção.

O sistema deve sugerir melhorias autonomamente, mas não aplicá-las silenciosamente.
