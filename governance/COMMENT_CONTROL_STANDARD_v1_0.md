# Padrão de Controle de Comentários Técnicos v1.0

## Objetivo

Padronizar a compilação, rastreabilidade, verificação, memória técnica e análise de comentários de engenharia. O padrão é único e pode ser aplicado a qualquer disciplina ou tipo documental.

## Regra-mestra

1. A quantidade de comentários formais da origem deve ser exatamente igual à quantidade de registros da tabela principal.
2. Nenhum comentário pode ser omitido, fundido ou eliminado por constar como atendido em relatório anterior.
3. Todo comentário nasce com `status_control = UNCHECKED` e representação visual `☐`.
4. `☑` somente é permitido após verificação humana e evidência documental registrada.
5. Se um comentário afetar mais de um documento, todos os documentos aplicáveis devem possuir evidência antes do fechamento.
6. Novas divergências ficam separadas da contagem dos comentários formais.
7. Toda correção relevante gera memória, regra preventiva e teste de regressão.
8. Hipótese não pode ser registrada como erro: quando faltar evidência conclusiva, o achado deve ser tratado como DÚVIDA.

## Erro x dúvida

- **ERRO**: não conformidade diretamente observável ou demonstrável por evidência documental. Exemplos: código/título errado, índice quebrado, texto pertencente a outro item, incompatibilidade matemática, faixa sobreposta ou contradição inequívoca entre documentos que tratam do mesmo requisito.
- **DÚVIDA**: situação cuja conclusão depende de informação ausente, decisão de engenharia, confirmação de escopo, equivalência técnica, requisito de compra, CAD/DWG, documento de referência não fornecido ou outra evidência ainda indisponível.
- Se houver incerteza material, prevalece DÚVIDA. O sistema deve indicar o dado necessário para resolver a questão.
- Diferença entre referências comerciais com expressão “ou similar técnico” não é erro automático; confirmar equivalência antes de reprovar.
- Objetivos formais fornecidos pelo solicitante permanecem como objetivos de verificação e não são descartados nem reclassificados como atendidos automaticamente.

## Regras de prevenção de falsos positivos

- Símbolo de descida somente é exigido quando existir mudança real para cota inferior. Mudança gráfica permanecendo em nível alto não caracteriza descida.
- Elementos, textos, ambientes e tags de outras disciplinas usados como referência devem ficar em cinza; elementos da disciplina de Automação permanecem no padrão próprio.
- Impressão deve ser avaliada por tamanho/padrão de folha, enquadramento, escala, cortes, margens e legibilidade. Espaço vazio por menor quantidade de conteúdo não constitui erro por si só.
- Em correções de formatação de ET/MD, preservar o texto técnico fornecido; corrigir apresentação sem reinventar conteúdo técnico.
- Quando não houver Matriz de Causa e Efeito aplicável ao projeto, não criar uma. Registrar apenas a explicação objetiva da não aplicabilidade quando solicitada.

## Campos mínimos

- project_id
- comment_id
- source_comment_id
- severity: GRAVE | ALTO | LEVE
- document_code
- revision
- page_or_item
- original_comment
- compiled_action
- origin_type: FORMAL_COMMENT | NEW_DIVERGENCE
- status_control: UNCHECKED | CHECKED
- evidence_text
- evidence_document
- evidence_revision
- evidence_location
- responsible
- created_at
- verified_at
- verifier

## Semântica do status

- `UNCHECKED` = ☐ = ainda não confirmado como atendido.
- `CHECKED` = ☑ = atendimento confirmado com evidência suficiente.

É proibido transformar automaticamente uma indicação textual como “100% atendido” em `CHECKED`.

## Criticidade

- `GRAVE`: segurança, intertravamento, filosofia operacional, função essencial, risco de execução/configuração incorreta.
- `ALTO`: incompatibilidade técnica relevante ou documental com impacto no projeto.
- `LEVE`: correção editorial, referência, identificação, paginação ou ajuste sem impacto funcional relevante.

## Gate de integridade

O pipeline deve bloquear a emissão quando qualquer uma das condições abaixo ocorrer:

- `formal_comment_count != registered_formal_comment_count`;
- comentário formal duplicado ou ausente;
- `CHECKED` sem evidência;
- comentário multi-documento sem evidência de todos os documentos requeridos;
- nova divergência misturada à contagem formal;
- grau fora do domínio permitido;
- achado marcado como ERRO sem evidência documental suficiente para sustentar a conclusão.

Modo padrão: `BLOCK_ON_ANY_FAILURE`.

## Memória técnica

Cada erro corrigido deve gerar três artefatos vinculados:

1. ocorrência (`LESSON` ou `REGRESSION`);
2. regra preventiva (`RULE`);
3. teste automatizado (`TEST`).

A memória é histórica e não substitui documento contratual ou normativo.

## Analítica

O sistema deve calcular, no mínimo:

- total de comentários formais;
- total pendente e confirmado;
- distribuição por grau;
- idade média e mediana dos comentários;
- tempo médio de fechamento;
- taxa de reabertura;
- taxa de comentários sem evidência;
- taxa de comentários multi-documento;
- taxa de regressão por documento e disciplina;
- índice de risco de atraso/recorrência.

## Análise preditiva

Até existir volume histórico suficiente para treinamento estatístico validado, a previsão deve ser tratada como `RISK_SCORE_BASELINE`, baseada em fatores explícitos e auditáveis. O sistema não deve apresentar heurística como modelo treinado.

## Power BI

O pipeline deve disponibilizar datasets tabulares estáveis para Power BI, sem depender da planilha Excel como fonte de verdade. A fonte de verdade é o banco de dados.

## CI/CD

GitHub Actions e GitLab CI devem executar:

1. validação de schema;
2. testes unitários;
3. testes de integridade de quantidade;
4. testes de status/evidência;
5. regressões conhecidas;
6. lint/compilação;
7. geração de artefatos analíticos quando aplicável.
