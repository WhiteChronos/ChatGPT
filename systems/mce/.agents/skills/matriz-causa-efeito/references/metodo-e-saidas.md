# MCE — método de elaboração, matriz de rastreabilidade e estados

## Fontes com autoridade por informação

- P&ID revisado: topologia de equipamentos/tubulações, instrumentos e conexão representada; **não** determina lógica de segurança sozinho.
- Lista I/O revisada: TAG, endereço, natureza de sinal, canal/PLC; não determina causa/efeito sozinho.
- Narrativa, memorial, filosofia, tabela intertravamentos e SRS aplicável: condições de disparo, votação, ação, estados seguros, temporização, permissivos, reset e bypass **quando explicitamente descritos**.
- HAZOP/LOPA: recomendações e requisitos **somente** no grau de aprovação e incorporação contratualmente demonstrados; não converter recomendações em SIF automaticamente.
- Modelo mestre XLSX: geometria e contrato do artefato; não é fonte primária de TAG nem de lógica.

## Registro de fontes sugerido

| DOC_ID | Tipo | Revisão | Folha / página | SHA-256 | Data / responsável | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| PI-001 | P&ID | R00 | 2/4 | SHA real | responsável documental | DOCUMENTADO / NAO_DOCUMENTADO |

Não preencher com IDs falsos em projetos reais: a tabela é somente um esquema de saída.

## Registro de causa → efeito por evidência

| Causa ID / TAG | Condição, limiar e estado de falha | Efeito / TAG ou ação | Composição lógica | Fonte e citação literal | Revisão / SHA-256 / página | Status | Disciplina responsável |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A documentar | **PENDENTE** | **PENDENTE** | PENDENTE | documento / trecho real | revisão e SHA reais | NAO_DOCUMENTADO | Instrumentação / Automação |

A localização e a evidência são obrigatórias. Em cada relação considerar falha de instrumento, bypass, manutenção, partida/parada e reset, conforme os documentos. Para lógica m-de-n, não inventar m nem n. Evitar duplicidade de causas e efeitos usando TAG + condição + revisão como chave de análise, sem remover registros conflitantes: apresentar conflito para aprovação.

## Estados e gates

1. **INVENTARIO_EM_ANALISE** — documentos ainda sendo conciliados, sem editar matriz.
2. **ANALISADO_AGUARDANDO_DECISAO** — relatório de entendimento e lista de pendências apresentados, STOP até decisão externa.
3. **AUTORIZADO_PARA_ELABORACAO** — somente após modelo mestre validado, contrato `editable_cells`, autorização literal `AUTORIZO_ELABORACAO_MCE` e baseline SHA correto.
4. **MCE_PRELIMINAR_PARA_REVISAO** — cópia derivada, auditoria OOXML, logs e revisão de engenharia pendentes; não homologado.
5. **ACEITE_FINAL_VERIFICADO** — apenas por evidências externas de revisão multidisciplinar, FAT/SAT se aplicável, responsáveis identificados e gates de implantação; nunca inferido pelo ChatGPT.

## Resposta mínima por solicitação

1. **Escopo:** projeto, SS, sistema, documentos e revisão; quais partes estão verificadas.
2. **Entendimento técnico:** descrição funcional da planta, instrumentos e fronteiras, com referência por afirmação.
3. **Tabela de relações C→E:** incluir apenas evidências documentadas ou candidatos claramente segregados para revisão; nunca converter candidatos em lógica final.
4. **Pendências e conflitos:** ID, informação ausente, origem, disciplina e ação humana requerida.
5. **Estado e próximo gate:** `ANALISADO_AGUARDANDO_DECISAO` por padrão antes de autorização; inventário SHA, relatório de alterações e auditoria quando aplicáveis.
6. **Rastreabilidade GitHub:** branch/PR/HEAD/checks somente se consultados; evidências do projeto e confidencialidade permanecem fora do GitHub público.

Ao revisar Excel, respeitar a Skill `padronizacao-mce`, máximo 50 causas por folha, cinza `D9D9D9` em **texto autorizado alterado**, sem mudanças acidentais de OOXML. Executor e testes: `engenharia-mce-projeto`; fechamento: `mce-fechamento-operacional`.