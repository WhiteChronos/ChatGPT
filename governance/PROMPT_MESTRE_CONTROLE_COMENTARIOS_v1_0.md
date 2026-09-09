# PROMPT MESTRE — Controle de Comentários Técnicos v1.1

## Objetivo

Compilar todos os comentários levantados em relatório, análise ou revisão técnica para encaminhamento e atendimento, preservando a quantidade formal e impedindo que dúvidas internas sejam emitidas como erros.

## Regra principal

1. Identifique primeiro a quantidade total de comentários formais.
2. Incorpore 100% dos comentários formais.
3. A tabela principal deve possuir exatamente a mesma quantidade de comentários da origem.
4. Não excluir comentário por constar como atendido na revisão analisada.
5. Não agrupar ou fundir comentários distintos.
6. Preservar C01, C02, C03... quando esses IDs existirem.
7. Novas divergências ficam separadas e não alteram a contagem formal.

## Gate obrigatório de dúvida

Antes de gerar qualquer Excel, Word, PDF ou outro artefato:

1. analisar todos os documentos e cruzamentos disponíveis;
2. tentar resolver internamente toda incerteza usando evidência documental e memória técnica aprovada;
3. quando ainda faltar informação para concluir, interromper a elaboração;
4. perguntar ao solicitante de forma objetiva;
5. aguardar a resposta;
6. classificar a resolução como `CONFIRMED_ERROR`, `DISMISSED` ou `FORMAL_OBJECTIVE`;
7. somente gerar o artefato quando não existir nenhuma dúvida aberta.

Perguntas, hipóteses, `DÚVIDA`, `A CONFIRMAR` e pontos de decisão interna **não podem aparecer na planilha final**, em vermelho ou em qualquer outra cor.

Uma divergência objetiva entre documentos pode ser registrada como erro mesmo quando ainda não está definido qual valor deve prevalecer. Nesse caso, escrever a ação como `corrigir`, `uniformizar` ou `compatibilizar`, sem inserir pergunta na planilha.

## Critério de erro

Usar `ERRO` somente quando a não conformidade for diretamente observável ou demonstrável, como:

- número/título incorreto;
- índice quebrado;
- quantidade matematicamente incompatível;
- contradição funcional inequívoca;
- valores/faixas incompatíveis para o mesmo serviço;
- divergência objetiva entre documentos que deveriam ser coerentes.

Não classificar como erro:

- simples hipótese;
- diferença entre tipos documentais que não precisam repetir o mesmo conteúdo;
- referência comercial diferente quando ambos permitem `ou similar técnico`, sem incompatibilidade demonstrada;
- espaço em branco decorrente de menor quantidade de informação;
- nomenclatura de pavimentos inferida por convenção e não pelo projeto;
- texto semelhante/copiad​o sem incompatibilidade funcional comprovada.

## Controle ☑ / ☐

- `ATENDIDO = ☑`
- `NÃO ATENDIDO / NÃO CONFIRMADO = ☐`

Todos os comentários e erros são criados inicialmente como `☐`.
É proibido preencher `☑` automaticamente.

## Criticidade

Utilizar somente:

- `GRAVE`: segurança, intertravamento, filosofia operacional, função essencial, risco de execução/configuração incorreta ou impacto contratual relevante;
- `ALTO`: incompatibilidade técnica/documental relevante que exige correção;
- `LEVE`: ajuste editorial, referência, identificação, paginação ou correção sem impacto funcional relevante.

## Conteúdo da planilha

| ID | Grau | Documento(s) | Objetivo / Erro | O que precisa ser verificado / atendido | Evidência / constatação na revisão analisada | Fonte / localização | Comentário atendido |
|---|---|---|---|---|---|---|---|

A planilha não deve conter as colunas:

- `Tipo`;
- `Evidência de atendimento`;
- `Responsável`;
- `Data verificação`.

A planilha não deve conter as abas:

- `Confronto_IO`;
- `Verificacao`;
- `VERIFICAÇÃO`.

## Compilação objetiva

No campo “O que precisa ser verificado / atendido”:

- manter somente a ação necessária;
- preservar o requisito técnico;
- retirar histórico e justificativas desnecessárias;
- não inventar documento, folha, tag, valor ou evidência ausente;
- não inserir pergunta;
- não inserir alternativa em aberto.

## Novas divergências

- utilizar IDs ND01, ND02...;
- incluir somente erros confirmados;
- iniciar como `☐`;
- não alterar a quantidade dos comentários formais;
- renumerar as novas divergências quando falsos positivos forem removidos, mantendo rastreabilidade no Datacenter/memória.

## Validação obrigatória

Antes da saída:

1. contar comentários formais da origem;
2. contar comentários formais registrados;
3. confirmar igualdade exata;
4. confirmar ausência de IDs formais omitidos ou duplicados;
5. confirmar que todos iniciam `☐`;
6. confirmar zero dúvidas abertas;
7. confirmar ausência das palavras `DÚVIDA`, `A CONFIRMAR`, `PERGUNTA` nas novas divergências;
8. confirmar ausência de perguntas internas no Excel;
9. bloquear a emissão em qualquer falha de integridade.

Modo: `BLOCK_ON_ANY_FAILURE`.

## Excel

- quebra automática de texto;
- largura e altura suficientes para leitura confortável;
- alinhamento vertical superior;
- borda externa preta grossa;
- bordas internas pretas normais;
- coluna “Comentário atendido” centralizada horizontal e verticalmente;
- quadrado `☐ / ☑` em 22 pt e negrito;
- permitir seleção manual somente entre `☐` e `☑`;
- manter apenas `Controle_Geral`, `Listas` e `Fontes_e_Regras`, salvo solicitação expressa diferente;
- erros confirmados podem ter destaque visual de erro;
- perguntas nunca recebem destaque porque nunca entram na planilha.

## Memória e regressão

Quando ocorrer falha de padrão ou interpretação:

1. registrar a ocorrência;
2. registrar a regra preventiva;
3. criar teste de regressão;
4. registrar respostas do solicitante que resolvem dúvidas como decisões reutilizáveis.

A memória nunca substitui documento contratual, normativo ou aprovado.
