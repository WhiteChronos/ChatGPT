# PROMPT - PASSO 3 - CONFERENCIA NORMATIVA E BIBLIOGRAFICA - V1

ID: PROMPT-STEP3-NORMATIVE-ACADEMIC-REVIEW-V1
STATUS: MANDATORY_CONTROLLED
PRE-REQUISITOS: STEP1_SCOPE_FROZEN + STEP2_PANEL_DEFINITION_FROZEN

## OBJETIVO

Conferir o projeto e cada painel contra normas, regulamentos, estudos academicos, livros tecnicos e referencias bibliograficas relacionadas aos assuntos efetivamente presentes nos documentos e parametros do projeto.

O resultado deve ser uma base de evidencia rastreavel que sustente as proximas etapas de engenharia.

## ORDEM DE TRABALHO

1. Carregar PROJECT_NUMBER, PROJECT_INTAKE_MANIFEST, PANEL_DEFINITION_MANIFEST e PROJECT_PARAMETER_REGISTRY.
2. Ler todos os documentos do projeto e listar temas tecnicos relevantes.
3. Para cada tema, identificar normas/regulamentos potencialmente aplicaveis.
4. Verificar numero, edicao, ano, escopo, exclusoes e motivo de aplicabilidade.
5. Localizar estudos academicos revisados por pares e referencias bibliograficas tecnicas.
6. Separar fato normativo, evidencia academica, orientacao de fabricante e decisao de projeto.
7. Registrar cada fonte em REF_ID proprio.
8. Arquivar copia controlada quando permitido.
9. Criar matriz de aplicabilidade e matriz de evidencia academica.
10. Registrar conflitos e lacunas.
11. Sincronizar Data Center e memoria do projeto.

## FONTES

Prioridade de pesquisa/evidencia:
1. regulador/governo e texto legal oficial;
2. organismo oficial de normalizacao;
3. fabricante oficial para fatos do produto;
4. artigos revisados por pares e editoras academicas;
5. livros/handbooks tecnicos reconhecidos;
6. repositorios universitarios/institucionais;
7. distribuidores autorizados;
8. fontes secundarias apenas como apoio e sempre identificadas.

A existencia de uma norma nao significa automaticamente que ela e obrigatoria. Registrar a base de aplicabilidade: lei, contrato, especificacao, requisito do cliente, norma adotada pelo projeto, escopo tecnico ou referencia informativa.

## MATRIZ NORMATIVA

Para cada norma/regulamento registrar:
- REF_ID;
- PROJECT_NUMBER;
- PANEL_ID/escopo;
- numero/titulo;
- organismo;
- edicao/ano;
- status da edicao;
- tema;
- escopo aplicavel;
- exclusoes;
- base de aplicabilidade;
- secao/pagina;
- requisito extraido;
- efeito no projeto;
- conflito;
- validadores;
- data de reverificacao.

## MATRIZ ACADEMICA

Para cada artigo/livro/tese:
- REF_ID;
- autores;
- titulo;
- ano;
- journal/editora;
- DOI/ISBN/ISSN;
- tipo de estudo;
- tema;
- populacao/sistema estudado quando aplicavel;
- resultado relevante;
- limitacoes;
- aplicacao ao projeto;
- nivel de evidencia/qualidade;
- link;
- status de copia controlada.

Nao transformar conclusao academica em requisito normativo.

## COPIAS NO DATACENTER

Todo documento usado deve ter registro no Data Center.

Quando permitido:
- arquivar copia integral controlada;
- calcular SHA-256;
- registrar caminho;
- manter revisoes antigas como SUPERSEDED_PRESERVED.

Quando a copia integral nao for permitida:
- nao contornar paywall/DRM/licenca;
- arquivar metadados;
- link oficial/DOI/ISBN;
- citacao bibliografica;
- resumo tecnico;
- paginas/secoes consultadas;
- pequenos trechos permitidos quando necessarios.

## MEMORIA DO PROJETO

A memoria deve armazenar:
- REF_ID;
- caminho ou link;
- SHA-256 quando houver copia;
- tema;
- regra/parametro extraido;
- aplicabilidade;
- paginas/secoes usadas;
- conclusao;
- conflito;
- data da revisao;
- regra de reutilizacao.

A memoria nao duplica PDFs completos.

## CONFLITOS

Classificar:
- INFORMATIVE;
- PROJECT_STRICTER;
- REFERENCE_STRICTER;
- APPLICABILITY_UNCERTAIN;
- CONFLICT.

Nao corrigir o projeto silenciosamente.

Conflito critico de edicao/aplicabilidade:
HOLD_NORMATIVE_CONFLICT
ou
HOLD_NORMATIVE_EDITION

## PLUGINS

Quando disponiveis:
- Scite e Consensus: descoberta e analise academica;
- Tavily e Firecrawl: busca e extracao controlada de fontes oficiais;
- GitHub/Data Center: armazenamento auditavel;
- Engram: memoria suplementar, nunca autoridade;
- Wolfram: calculos derivados, nunca decisao de aplicabilidade normativa.

## SAIDAS

- NORMATIVE_APPLICABILITY_MATRIX
- ACADEMIC_EVIDENCE_MATRIX
- BIBLIOGRAPHIC_REFERENCE_REGISTER
- CONTROLLED_SOURCE_ARCHIVE_INDEX
- NORMATIVE_CONFLICT_REGISTER
- STEP3_REVIEW_SUMMARY
- MEMORY_SYNC_RECORD

Gate:
STEP3_NORMATIVE_ACADEMIC_BASE_FROZEN

## REGRA DE CONTROLE

PESQUISAR MAIS, PERGUNTAR MENOS, NAO ASSUMIR.
ARQUIVAR A EVIDENCIA, NAO SOMENTE A RESPOSTA.
