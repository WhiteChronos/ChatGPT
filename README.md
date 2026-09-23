# AUTOMACAO Engineering Governance

Repositório de governança, memória técnica e validação para documentação de automação, instrumentação, HVAC, processo, tubulação, elétrica e desenhos funcionais.

## Princípios

- Regra técnica antes de estética.
- Evidência documental antes de inferência.
- Comando, retorno, falha e disponibilidade são sinais distintos.
- Toda alteração relevante deve deixar trilha de auditoria.
- Regras aprovadas são versionadas e nunca sobrescritas sem histórico.
- Dados de projeto confidenciais não são publicados neste repositório público.
- O padrão visual é imutável; o conteúdo e a quantidade de folhas pertencem ao documento de destino.

## Regra de Ouro — `/visualize`

Model ID:

`VISUALIZE_GOLDEN_RULE_v1_0`

`/visualize` significa **conteúdo técnico completo apresentado visualmente**. Não é sinônimo de resumo.

Toda compatibilização multidisciplinar e parecer técnico deve preservar evidências, comparações, causa-raiz, impactos, alternativas de viabilidade, documentos a ajustar, texto proposto, dependências e critérios de fechamento.

Arquivos de controle:

- `governance/VISUALIZE_GOLDEN_RULE_v1_0.md`;
- `governance/CODEX_COMPATIBILITY_v1_0.md`;
- `AGENTS.md`;
- `schemas/engineering_compatibility.schema.json`;
- `datacenter/ENGINEERING_COMPATIBILITY_CONFIG.json`;
- `datasheet/ENGINEERING_COMPATIBILITY_DATA_SHEET.json`;
- `pipeline/engineering_compatibility_gate.py`;
- `.github/workflows/engineering-compatibility-visualize.yml`.

O pipeline opera em `BLOCK_ON_FAILURE` para incompatibilidades críticas abertas, cobertura insuficiente, documentos mandatórios ausentes, baseline não reconciliada ou compatibilidade abaixo do limiar definido.

## Modelo permanente de compatibilização de Automação

Model ID:

`AUTOMATION_COMPATIBILITY_REPORT_MODEL_V1_0`

Toda compatibilização de Automação usa `/visualize` como camada de apresentação padrão e pode ser aprimorada com **Build Web Data Visualization** quando a ação estiver disponível.

Contrato mínimo:

- Protocol Zero: pergunta antes de finding;
- consultar primeiro baseline do projeto e, quando pertinente, normas/fontes oficiais antes de escalar dúvida ao usuário;
- separar dúvidas, erros confirmados, problemas de engenharia, compatíveis e NOT_VERIFIABLE;
- todo erro confirmado informa os documentos envolvidos: evidência, correlatos/conflitantes, normas/referências e documentos a corrigir;
- referências normativas possuem estado de aplicabilidade e não podem gerar não conformidade quando forem apenas `REFERENCE_ONLY`;
- revisão corrigida deve ser rechecada antes de fechar finding ou liberar o pacote.

Arquivos de controle:

- `governance/AUTOMATION_COMPATIBILITY_REPORT_MODEL_v1_0.md`;
- `datacenter/AUTOMATION_COMPATIBILITY_REPORT_MODEL.json`;
- `datacenter/AUTOMATION_REFERENCE_LIBRARY.json`;
- `schemas/engineering_compatibility.schema.json`;
- `pipeline/engineering_compatibility_gate.py`;
- `pipeline/protocol_zero_gate.py`.

A biblioteca padrão de consulta inclui os metadados e o gate de aplicabilidade para PETROBRAS N-1882 Rev. F, N-1883 Rev. F e N-2833 Rev. A. O repositório público não armazena o texto integral das normas.

## Compatibilidade com Codex

Codex e outros agentes de código devem ler `AGENTS.md` e a Regra de Ouro antes de alterar esquemas, cálculos de compatibilidade, relatórios, pipelines ou configuração do Data Center.

Fluxo obrigatório:

`/factcheck -> /thenvsnow -> /comparison -> /deepdive -> /rootcause -> /fivewhys -> /audit -> /redteam -> /premortem -> /viability -> /actionplan -> /visualize`

O agente deve preservar a diferença entre fato de fonte, inferência de engenharia, conhecimento externo e hipótese não resolvida.

## Padrão definitivo — LI de Entradas e Saídas

Model ID:

`LI_IO_PETROBRAS_AUTOMACAO_V1_0`

Regras centrais:

- usar o modelo somente como matriz de layout, fontes, dimensões, linhas, objetos e impressão;
- nunca copiar automaticamente a quantidade de abas do modelo visual;
- determinar a quantidade de folhas pelo documento de destino;
- alterar somente texto, valores, fórmulas autorizadas e paginação;
- condensar a redação antes de cogitar qualquer mudança visual;
- manter notas gerais na folha de notas/resumo/referências;
- proibir nota genérica na última folha ou no mapa de memória;
- validar estrutura, fórmulas, referências, paginação e renderização antes da emissão;
- operar em `BLOCK_ON_ANY_FAILURE`.

Documentos e módulos:

- `governance/LI_IO_STANDARD_v1_0.md`;
- `governance/PROMPT_MESTRE_LI_ENTRADA_SAIDA_v1_0.md`;
- `datacenter/LI_IO_STANDARD.json`;
- `datasheet/LI_IO_DATA_SHEET.json`;
- `pipeline/li_io_standard.py`;
- `pipeline/apply_li_io_text_patch.py`;
- `pipeline/xlsx_layout_guard.py`.

O binário oficial permanece no Data Center privado. O repositório público contém somente manifesto redigido, hashes, regras, esquemas e testes.

## Catálogo permanente de ferramentas

O catálogo em `plugins/document_tooling_registry.json` reúne ferramentas públicas do GitHub para DOCX, XLSX, PDF, OOXML, CAD, renderização, extração, comparação e segurança. Ele é curado e extensível; não existe uma lista finita de “todos os plugins” do GitHub.

O workflow mensal `document-tooling-discovery.yml` pesquisa novas candidatas. Descoberta não significa aprovação e nenhuma ferramenta é instalada automaticamente. Promoção para uso exige revisão de licença, segurança, manutenção, versão/commit fixo, sandbox e testes de regressão.

## Estrutura

- `governance/`: regras de ouro, políticas, prompts e padrões documentais;
- `memory/`: decisões, lições aprendidas, conflitos e pendências;
- `schemas/`: contratos de dados e validação;
- `pipeline/`: validadores, agentes e aplicação textual controlada;
- `datacenter/`: manifestos redigidos, fingerprints e configuração de compatibilização;
- `datasheet/`: regras de consistência e registros estruturados de compatibilidade;
- `plugins/`: catálogo de ferramentas externas;
- `tests/`: testes de regressão;
- `.github/`: workflows e processo de revisão.

O aplicativo deve ler estas regras antes de gerar ou aprovar qualquer documento.
