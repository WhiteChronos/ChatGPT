# Sistema MCE — regras locais exclusivas

Escopo: sistema de engenharia de Matriz de Causa e Efeito, independente de motor de engenharia reversa, MCP e interface Web.

1. Inventariar modelo mestre XLSX, P&IDs, I/O, narrativas, especificações, SRS e revisões com SHA-256.
2. Identificar Projeto e SS somente quando documentados. Não inferir setpoints, TAGs, trips, votações, alarmes ou SIFs.
3. Apresentar relatório de entendimento e PARAR em `ANALISADO_AGUARDANDO_DECISAO`.
4. Mediante autorização expressa, contrato de células permitido e modelo validado, editar exclusivamente texto documentado em CÓPIA do Excel.
5. Não alterar cabeçalho, estilos, fórmulas, mesclas, imagens, áreas de impressão ou artefatos não autorizados. Sinalizar alterações válidas em cinza `D9D9D9`.
6. No máximo 50 causas por folha (ou menos quando modelo limitar). Auditar OOXML e SHA da fonte e apresentar como preliminar à validação multidisciplinar.
7. Exportações P&ID OCR/grafo são auxiliares e exigem verificação humana por fonte/arquivo/revisão; nunca geram comandos de segurança.
8. Não importar módulos de outros produtos para executar este workflow. Não publicar documentos privados.
 
## Contrato de continuidade documental obrigatório (2026-10-29)

- Antes de planejar, implementar ou revisar este produto, **ler primeiro** `systems/mce/spec/memoria.md` e `systems/mce/docs/DATACENTER_MEMORY.md`, depois consultar o HEAD atual do PR #118, checks e bloqueios.
- Considerar o Markdown **checkpoint histórico** e o GitHub a fonte de verdade de código; banco SQLite separado no host privado não é acessível automaticamente pelo ChatGPT Web.
- Após cada mudança verificada ou decisão nova, acrescentar ao `spec/memoria.md` um evento com data, DEC/PEND estável, SHA, fonte, teste e pendência, preservando entradas anteriores. Nunca apagar decisão para ocultar conflito; registrar substituição justificada.
- Não alegar execução de Codex, Superpowers, MCP ou aceites humanos apenas porque há instrução ou configuração versionada.
- Não colocar segredos, transcrições integrais, documentos industriais, banco SQLite, backups ou DataSheets operacionais neste repositório; não usar a memória do outro sistema como dependência.
- O arquivo é *recuperável por consulta*, não há garantia de memória nativa entre chats nem persistência eterna. Para retomada, consultar o documento diretamente e comparar os fatos com o PR atual.


## Vinculo GitHub da memoria (2026-10-29)

- Indice permanente: https://github.com/WhiteChronos/ChatGPT/issues/120
- Consultar systems/mce/spec/memoria.md e systems/mce/docs/GITHUB_MEMORY.md antes de atuar.
- Alteracoes MCE devem acrescentar registro datado na memoria no mesmo commit. Validacao: .github/workflows/mce-github-memory.yml. Nao contornar falhas da CI.
- A memoria nao captura chats automaticamente; registrar decisoes verificadas no GitHub sem dados confidenciais.


## Vinculo com registro imediato GitHub

- Ler tambem os comentarios do Issue #120 no inicio de cada tarefa, nao apenas memoria.md.
- Quando uma decisao tecnica explicitamente publicavel for estabelecida e o GitHub conectado estiver autorizado, registrar evento estruturado WC_MEMORY_EVENT_V1 no Issue #120 e verificar o URL; nao esperar a proxima conversa.
- Nunca copiar conversas completas, P&IDs, Excel mestre, dados pessoais ou credenciais. Comentarios sao historico, nao aprovacao de engenharia. Se a ferramenta nao estiver disponivel, informar que nao houve gravacao.
- A CI inspeciona todos os commits posteriores ao checkpoint de ativacao, nao somente o HEAD.


## Entrada exclusiva para Matriz de Causa e Efeito (29/10/2026)

- Skill orquestradora: `systems/mce/.agents/skills/matriz-causa-efeito/SKILL.md`, espelhada identicamente em `.agents/skills/matriz-causa-efeito/SKILL.md` para descoberta no Codex/ChatGPT.
- Usar apenas para matriz causa→efeito de automacao industrial. Compor as Skills antigas `engenharia-mce-projeto`, `padronizacao-mce` e `mce-fechamento-operacional`; preservar o editor existente e todos os gates humanos.
- Consultar Issue #120, memoria.md e PR #118 antes de agir; catalogo de repos GitHub externos e pesquisa auxiliar, nao fonte contratual de intertravamentos. Nenhum dado industrial e enviado ao GitHub publico.

## Ferramenta matriz-causa-efeito: memoria e DataCenter do proprio MCE

- Uma unica Skill de entrada `matriz-causa-efeito` utiliza os tres motores de apoio MCE existentes, nao um segundo motor/editor nem outra base SQL.
- Executor de pre-analise `systems/mce/scripts/matriz_causa_efeito_tool.py`, detalhes em `systems/mce/docs/MATRIZ_CAUSA_EFEITO_TOOL.md`, DataSheet sob `datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json`.
- Os tres repositorios GitHub (Azure, Houston, Industrial-Control) sao formatos de exportacao para adaptadores proprios. Nao clonar/executar terceiros nem transformar benchmark/OCR/grafo em comando de seguranca.
- `plan` nao escreve; `run` exige inventario SHA, SQLite existente e devolve estado PRE_ANALISE_PENDENTE_REVISAO, nao autorizacao para Excel. Sem host autorizado: NOT_RUN.
