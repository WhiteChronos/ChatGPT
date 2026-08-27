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
- `datacenter/`: manifestos redigidos e fingerprints de modelos privados;
- `datasheet/`: regras de consistência para LI e FD;
- `plugins/`: catálogo de ferramentas externas;
- `tests/`: testes de regressão;
- `.github/`: workflows e processo de revisão.

O aplicativo deve ler estas regras antes de gerar ou aprovar qualquer documento.
