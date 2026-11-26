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

## Contrato de completude funcional — DEC-MCE-068 (2026-11-10)

**Aplicacao:** toda elaboracao, revisao e emissao de Matriz de Causa e Efeito. A referencia privada de apresentacao registrada por DEC-MCE-066 orienta forma e detalhamento; nao autoriza replicar TAGs, setpoints, logicas ou cruzamentos de outro projeto.

1. **Inventario integral:** para cada causa/linha candidata registrar ID, TAG, descricao da condicao e revisao da fonte. Distinguir EVENTO_CAUSAL, SUPERVISAO_SEM_ATUACAO, INTERFACE e ITEM_FORA_ESCOPO; nunca contar apenas X existentes como prova de completude.
2. **Efeitos completos:** descrever todas as funcoes aplicaveis do projeto, sem preencher artificialmente as posicoes disponiveis; cada efeito deve ter identidade funcional clara, responsavel e evidencia por documento, revisao, folha/pagina e SHA no relatorio PRIVADO.
3. **X seletivo e auditavel:** avaliar para cada linha TODAS as colunas de efeitos aplicaveis. Registrar em relatorio privado a decisao X, NAO_APLICAVEL_COM_JUSTIFICATIVA ou PENDENTE_DE_EVIDENCIA para cada par candidato. Cada X existente requer revalidacao; ausencia de X nao prova ausencia de efeito. Proibido aplicar X em todas as colunas para aparentar completude.
4. **Observacao por causa:** cada linha mantida da MCE deve ter observacao especifica, util e documental, descrevendo a atuacao, indicacao ou ausencia justificada de atuacao, fronteira de responsabilidade e condicoes de falha/rearme quando documentadas. Se faltar evidencia, redigir rascunho no relatorio de PENDENCIAS e bloquear a emissao; nunca inventar uma observacao afirmativa para eliminar celulas vazias.
5. **SP condicionado ao contrato:** preservar fisicamente a coluna se pertence ao modelo, mas nao assumir seu preenchimento. Quando o usuario/projeto determinar "SP nao utilizado", manter as celulas SP vazias SOMENTE na copia derivada aprovada; valores tecnicos documentados podem figurar na descricao/observacao conforme convencao aprovada, sem perder unidade fisica. Uma decisao de uso de SP e escopo projeto/revisao, nao padrao universal; nao apagar SP historico sem autorizacao de celula.
6. **Confronto documental:** reconciliar MD, ET, P&ID, arquitetura, lista I/O e manuais aplicaveis para alarme, comandos hardwired, falha de UTR, HVAC, exaustao, UPS, bypass, reset e interface SCADA. Distinguir divergencia de revisoes de requisito valido. Nao promover recomendacoes ou legenda de P&ID a logica de intertravamento.
7. **Preflight antes da emissao:** relatorio privado deve comprovar 100% das linhas revisadas, 100% das observacoes tecnicamente resolvidas, todos os X validados, todos os candidatos a pares causa/efeito classificados, SP conforme contrato e nenhuma divergencia funcional impeditiva. Se nao houver prova, STOP em ANALISADO_AGUARDANDO_DECISAO, sem XLSX/PDF "final".
8. **Entrega controlada:** arquivo principal XLSX P09 vigente em copia derivada, PDF somente representacao fiel se solicitado, QA OOXML/Excel Windows e cotejo entre as paginas. Nao editar mestre nem logica funcional sem modelo homologado, whitelist de celulas, AUTORIZO_ELABORACAO_MCE vinculado a hashes e revisao multidisciplinar.

**Anti-regressao:** o perfil de arquivo historico sem observacoes ou com SP preenchido nao substitui esta verificacao de completude para novas emissoes. Decisoes antigas de layout sao preservadas como historico, e eventual conflito exige revisao explicita do contrato, nao alteracao silenciosa do modelo.

