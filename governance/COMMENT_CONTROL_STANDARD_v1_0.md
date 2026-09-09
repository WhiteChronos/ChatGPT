# Padrão de Controle de Comentários Técnicos v1.1

## Objetivo

Padronizar compilação, verificação, rastreabilidade, memória e emissão de comentários técnicos. O padrão é único e aplicável a qualquer disciplina ou tipo documental.

## Regra-mestra

1. A quantidade de comentários formais da origem deve ser exatamente igual à quantidade de registros formais da tabela principal.
2. Nenhum comentário formal pode ser omitido, fundido ou eliminado por constar como atendido em relatório anterior.
3. Todo comentário nasce com `status_control = UNCHECKED` e representação visual `☐`.
4. `☑` somente é permitido após verificação humana conforme processo de fechamento.
5. Novas divergências ficam separadas da contagem dos comentários formais.
6. Toda dúvida de interpretação deve ser resolvida **antes** da geração de Excel, Word, PDF, Power BI ou pacote de emissão.
7. Perguntas e dúvidas nunca são exportadas como linhas da planilha final.
8. Toda correção de lógica relevante gera memória, regra preventiva e teste de regressão.

## Gate de pré-verificação — dúvida antes da elaboração

O sistema opera em duas camadas:

### Camada interna de análise

Pode conter:
- candidatos a erro;
- hipóteses;
- dúvidas;
- perguntas de esclarecimento;
- comparações ainda não conclusivas.

Essa camada não é um documento de entrega.

### Camada de emissão

Só pode conter:
- objetivos formais fornecidos pelo solicitante;
- erros confirmados por evidência documental ou comparação inequívoca;
- ações objetivas de correção;
- status de atendimento `☐ / ☑`.

É proibido emitir:
- `DÚVIDA`;
- `A CONFIRMAR`;
- perguntas em vermelho ou em qualquer outra cor;
- hipóteses;
- alternativas não resolvidas;
- conclusões condicionais que dependam de resposta do solicitante.

## Fluxo obrigatório

`ANALYZE -> RESOLVE_FROM_SOURCES -> ASK_IF_NEEDED -> RESOLVE_QUESTIONS -> CLASSIFY -> VALIDATE -> GENERATE`

Se houver pergunta aberta, o estado deve ser `WAITING_CLARIFICATION` e o pipeline deve parar.

Após resposta do solicitante, a dúvida recebe uma resolução:
- `CONFIRMED_ERROR` — entra como erro;
- `DISMISSED` — é descartada da emissão;
- `FORMAL_OBJECTIVE` — entra somente por determinação explícita do solicitante.

Somente com zero perguntas abertas o lote pode mudar para `READY_TO_GENERATE`.

## Regra de classificação

### ERRO

Usar somente quando a não conformidade for diretamente observável ou demonstrável. Exemplos:
- número ou título incorreto;
- índice quebrado;
- quantidade matematicamente incompatível;
- contradição funcional objetiva;
- valores/faixas incompatíveis para o mesmo serviço;
- divergência inequívoca entre documentos que deveriam ser coerentes.

Uma divergência pode ser registrada como erro mesmo que ainda não esteja definido qual valor deve prevalecer. Nesse caso, a ação deve ser “corrigir/compatibilizar”, nunca uma pergunta na planilha.

### DÚVIDA INTERNA

Usar quando faltar evidência suficiente para concluir. Deve ser sanada antes da emissão e nunca aparece no artefato final.

## Regras de interpretação incorporadas

- Símbolo de descida somente quando houver mudança real para cota inferior.
- Elementos de outras disciplinas usados como referência devem ficar em cinza conforme padrão gráfico do projeto.
- Espaço em branco causado por menor quantidade de informação não caracteriza erro de impressão.
- Formatação deve ser corrigida sem alterar conteúdo técnico válido sem necessidade.
- Ausência de conteúdo em um tipo documental não é erro apenas porque outro documento possui esse conteúdo; considerar a função específica de ET, FD, LI, MD e DE.
- “Ou similar técnico” permite referências comerciais diferentes; somente classificar como erro quando houver incompatibilidade técnica demonstrada.
- Nomenclatura de pavimentos e escopo físico devem seguir o projeto, não convenções inferidas.
- Texto semelhante/copiad​o não é erro por si só; avaliar se a função técnica descrita é incompatível.

## Campos mínimos da emissão

- `comment_id`
- `severity`: GRAVE | ALTO | LEVE
- `document_code`
- `revision`
- `page_or_item`
- `original_comment` ou resumo do objetivo/erro
- `compiled_action`
- `finding_basis`
- `source_location`
- `origin_type`: FORMAL_COMMENT | NEW_DIVERGENCE
- `status_control`: UNCHECKED | CHECKED

## Campos internos de pré-verificação

- `question_id`
- `topic`
- `question_text`
- `why_needed`
- `related_documents`
- `status`: OPEN | RESOLVED | DISMISSED
- `resolution`
- `resolution_type`: CONFIRMED_ERROR | DISMISSED | FORMAL_OBJECTIVE
- `resolved_by`
- `resolved_at`

Esses campos nunca são exportados para a planilha final.

## Padrão do Excel

A aba principal deve conter somente:

1. ID
2. Grau
3. Documento(s)
4. Objetivo / Erro
5. O que precisa ser verificado / atendido
6. Evidência / constatação na revisão analisada
7. Fonte / localização
8. Comentário atendido

Regras visuais:
- quebra automática de texto;
- altura confortável;
- alinhamento vertical superior;
- borda externa preta grossa;
- bordas internas pretas normais;
- `☐ / ☑` centralizado, 22 pt;
- todos iniciam em `☐`.

Não criar colunas `Tipo`, `Evidência de atendimento`, `Responsável` ou `Data verificação`.
Não criar abas `Confronto_IO` ou `Verificacao`.
Não inserir dúvidas ou perguntas na planilha.

## Gate de integridade

O pipeline deve bloquear a emissão quando qualquer condição ocorrer:

- `formal_comment_count != registered_formal_comment_count`;
- comentário formal duplicado ou ausente;
- pergunta de esclarecimento aberta;
- nova divergência misturada à contagem formal;
- grau fora do domínio permitido;
- tentativa de exportar texto classificado como dúvida/pergunta.

Modo padrão: `BLOCK_ON_ANY_FAILURE`.

## Memória técnica

Cada erro de interpretação corrigido deve gerar:

1. ocorrência (`LESSON` ou `REGRESSION`);
2. regra preventiva (`RULE`);
3. teste automatizado (`TEST`).

Respostas do solicitante que resolvem dúvidas devem ser persistidas como `DECISION`, vinculadas ao tema e aos documentos, para evitar repetir a mesma pergunta quando o contexto for equivalente.

A memória é histórica e não substitui documento contratual ou normativo.

## Analítica e CI/CD

O sistema mantém estatística, risco baseline, Power BI e CI/CD. Os pipelines de GitHub Actions e GitLab CI devem validar, além dos testes existentes:

- nenhuma pergunta aberta antes da geração;
- nenhuma linha de planilha contendo `DÚVIDA`, `A CONFIRMAR` ou pergunta interna;
- ausência das colunas e abas proibidas;
- regressões conhecidas de interpretação.
