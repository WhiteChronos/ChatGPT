# PROMPT - PASSO 2 - DEFINICAO PARAMETRICA DOS PAINEIS - V1

ID: PROMPT-STEP2-PANEL-DEFINITION-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITO: STEP1_SCOPE_FROZEN

## OBJETIVO

Definir tecnicamente cada painel do projeto antes de pesquisa detalhada, selecao de componentes, calculos, LI/BOM, layout ou imagem.

O sistema deve perguntar somente o que ainda nao puder ser resolvido com seguranca pelos documentos do projeto, Data Center, memoria validada, catalogos oficiais e regras parametrizadas.

## PRINCIPIO DE APRENDIZADO

A memoria e evolutiva.

Com o tempo:
- perguntas repetidas devem diminuir;
- respostas recorrentes devem virar parametros reutilizaveis;
- duvidas resolvidas devem virar regras ou defaults condicionais;
- catalogos e dados oficiais devem enriquecer a biblioteca tecnica;
- erros confirmados devem gerar regra preventiva e teste de regressao.

Mas nenhum parametro pode ser reutilizado cegamente fora do seu escopo.

## ORDEM OBRIGATORIA

1. Carregar PROJECT_NUMBER e PROJECT_INTAKE_MANIFEST.
2. Carregar PANEL_COUNT e o registro de PANEL_IDs.
3. Para cada painel, carregar todos os documentos vinculados.
4. Consultar Data Center do projeto.
5. Consultar memoria do projeto.
6. Consultar memoria metodologica.
7. Consultar biblioteca de catalogos e parametros ja validados.
8. Pesquisar fabricante/norma quando houver lacuna.
9. Somente depois gerar perguntas ao usuario.

## MOTOR DE PERGUNTAS

Cada pergunta deve possuir:
- QUESTION_ID;
- PROJECT_NUMBER;
- PANEL_ID;
- tema;
- motivo;
- informacao ja encontrada;
- lacuna real;
- opcoes quando aplicavel;
- impacto se nao respondida;
- fonte consultada;
- status.

As perguntas devem ser agrupadas por painel e por tema.

Temas tipicos:
- funcao do painel;
- equipamentos controlados;
- alimentacao;
- aterramento;
- autonomia/UPS;
- PLC/controlador;
- I/O;
- comunicacao;
- gateways;
- instrumentos;
- ambiente;
- grau de protecao;
- restricoes de instalacao;
- manutencao;
- expansao/reserva;
- interfaces com outros sistemas.

## REGRA DE NAO REPETIR

Antes de perguntar:
1. verificar se a resposta existe em documento controlado;
2. verificar se existe no Data Center;
3. verificar memoria do mesmo PROJECT_NUMBER;
4. verificar memoria do mesmo PANEL_ID;
5. verificar catalogo/fabricante;
6. verificar norma;
7. verificar parametro global reutilizavel e sua aplicabilidade.

Se existir resposta valida e aplicavel, NAO perguntar novamente.

Se houver conflito, perguntar somente a decisao que nao puder ser resolvida pela hierarquia das fontes.

## PARAMETRIZACAO

Toda resposta confirmada deve virar um parametro estruturado.

Campos minimos:
- PARAMETER_ID;
- PROJECT_NUMBER;
- PANEL_ID ou escopo GLOBAL/PROJECT/MANUFACTURER_FAMILY/EQUIPMENT_MODEL;
- nome;
- valor;
- unidade;
- origem;
- REF_ID;
- pagina/secao;
- data;
- revisao;
- status;
- regra de reutilizacao;
- regra de invalidacao.

Status permitidos:
- DOCUMENT_CONFIRMED;
- MANUFACTURER_CONFIRMED;
- USER_CONFIRMED;
- CALCULATED_VALIDATED;
- REUSED_VALIDATED;
- PENDING;
- CONFLICT;
- SUPERSEDED.

## ESCOPOS DE MEMORIA

GLOBAL_METHOD:
regras gerais da metodologia.

PROJECT:
premissas validas somente para um PROJECT_NUMBER.

PANEL:
premissas validas somente para um PANEL_ID.

MANUFACTURER_FAMILY:
fatos tecnicos oficiais reutilizaveis para uma familia, desde que revisao/lifecycle continuem validos.

EQUIPMENT_MODEL:
fatos tecnicos de um codigo exato.

Nunca promover automaticamente PROJECT/PANEL para GLOBAL.

## CATALOGOS

Todo catalogo/manual/datasheet utilizado deve ser cadastrado no Data Center.

Quando tecnicamente e juridicamente possivel, armazenar copia controlada do arquivo tecnico no Data Center do projeto ou biblioteca de catalogos.

Para cada arquivo:
- fabricante;
- familia/modelo;
- titulo;
- codigo;
- revisao;
- data;
- idioma;
- URL oficial;
- data de consulta;
- SHA-256;
- caminho da copia controlada;
- status de lifecycle;
- paginas/secoes utilizadas.

A memoria nao deve duplicar PDFs completos. Ela deve guardar:
- ponteiro para o arquivo do Data Center;
- hash;
- parametros extraidos;
- decisoes derivadas;
- paginas/secoes usadas.

## QUANDO UM DADO ESTIVER ERRADO

Nao sobrescrever silenciosamente.

Fluxo:
1. detectar conflito;
2. identificar fonte antiga e fonte nova;
3. classificar qual tem maior autoridade;
4. marcar parametro antigo como SUPERSEDED;
5. criar nova versao do parametro;
6. registrar motivo;
7. invalidar artefatos downstream afetados;
8. recalcular/revalidar;
9. perguntar ao usuario somente se a hierarquia das fontes nao resolver.

## FORMATO DAS PERGUNTAS AO USUARIO

Usar o padrao Visualize definido pelo projeto.

A tela deve mostrar:
- projeto;
- painel;
- perguntas pendentes;
- contexto curto;
- opcoes/resposta;
- impacto.

No final, sempre disponibilizar um bloco consolidado para copiar as respostas.

## METRICAS DE EVOLUCAO

Registrar por projeto:
- total_questions;
- auto_resolved_from_documents;
- auto_resolved_from_catalogs;
- reused_validated_parameters;
- user_questions;
- conflicts_detected;
- superseded_parameters;
- new_catalogs_added;
- new_reusable_parameters;
- regression_rules_created.

Objetivo:
reduzir user_questions ao longo dos projetos sem reduzir rastreabilidade ou qualidade.

## SAIDAS OBRIGATORIAS

- PANEL_DEFINITION_MANIFEST;
- PROJECT_PARAMETER_REGISTRY;
- QUESTION_DECISION_LOG;
- CATALOG_INDEX;
- MEMORY_SYNC_RECORD;
- STEP2_PANEL_DEFINITION_FROZEN.

## GATE

O Passo 2 fecha quando:
- todos os paineis do Passo 1 foram processados;
- perguntas criticas foram respondidas ou resolvidas por evidencias;
- parametros principais estao versionados;
- catalogos usados estao registrados;
- conflitos foram resolvidos;
- nenhuma definicao critica depende de suposicao oculta.

Status final:
STEP2_PANEL_DEFINITION_FROZEN

Se existir conflito critico:
HOLD_PANEL_DEFINITION_CONFLICT

## FRASE DE CONTROLE

PERGUNTAR MENOS NAO SIGNIFICA ASSUMIR MAIS.
PERGUNTAR MENOS SIGNIFICA REUTILIZAR MELHOR DADOS VALIDOS, PARAMETRIZADOS, VERSIONADOS E RASTREAVEIS.
