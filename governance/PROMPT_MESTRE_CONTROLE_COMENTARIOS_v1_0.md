# PROMPT MESTRE — Controle de Comentários Técnicos v1.0

## Objetivo

Compilar todos os comentários levantados em relatório, análise ou revisão técnica para encaminhamento, atendimento, verificação e fechamento, sem perder nenhum comentário da origem.

## Regra principal

1. Identifique primeiro a quantidade total de comentários formais.
2. Incorpore 100% dos comentários formais.
3. A tabela principal deve possuir exatamente a mesma quantidade de comentários da origem.
4. Não excluir comentário por constar como atendido na revisão analisada.
5. Não agrupar, fundir ou renumerar comentários distintos.
6. Preservar C01, C02, C03... quando esses IDs existirem.
7. Novas divergências ficam separadas e não alteram a contagem formal.

## Controle ☑ / ☐

- `ATENDIDO = ☑`
- `NÃO ATENDIDO / NÃO CONFIRMADO = ☐`

### Regra de inicialização

Todos os comentários são criados inicialmente como `☐`.

É proibido preencher `☑` automaticamente, inclusive quando o relatório de origem declarar “atendido”, “100% atendido”, “encerrado” ou expressão equivalente.

### Regra de fechamento

O `☑` só pode ser aplicado após:

- confirmação humana;
- evidência documental registrada;
- verificação de todos os documentos afetados;
- documento, revisão e localização da evidência sempre que disponíveis.

`☑` sem evidência é inválido.

## Criticidade

Utilizar somente:

- `GRAVE`: segurança, intertravamento, filosofia operacional, função essencial, risco de execução/configuração incorreta ou impacto contratual relevante;
- `ALTO`: incompatibilidade técnica/documental relevante que exige correção;
- `LEVE`: ajuste editorial, referência, identificação, paginação ou correção sem impacto funcional relevante.

Quando a origem possuir classificação equivalente, preservar sua proporcionalidade.

## Conteúdo da tabela

| Nº / Comentário | Grau | Documento / Local | O que precisa ser atendido | Evidência da verificação | Comentário atendido |
|---|---|---|---|---|---|
| C01 | GRAVE / ALTO / LEVE | Documento / revisão / folha / item | Ação objetiva | Evidência posterior | ☐ |

## Compilação objetiva

No campo “O que precisa ser atendido”:

- manter somente a ação necessária;
- preservar o requisito técnico;
- retirar memória de cálculo, índices, histórico e justificativas extensas;
- não escrever somente “já atendido”;
- se a auditoria considerar o item atendido, registrar o requisito que deve ser confirmado;
- não inventar documento, folha, tag, valor ou evidência ausente.

## Comentário parcialmente atendido

- permanece na tabela;
- permanece `☐`;
- registrar objetivamente o que ainda precisa ser incorporado ou confirmado.

## Comentário considerado atendido no relatório

- permanece na tabela;
- permanece `☐`;
- registrar o requisito técnico que deve ser verificado;
- o controle somente muda para `☑` após evidência e confirmação humana.

## Comentários multi-documento

Quando um comentário afetar mais de um documento:

- listar todos os documentos aplicáveis;
- manter `☐` enquanto qualquer documento permanecer sem evidência;
- somente permitir `☑` após verificação integral.

## Novas divergências

- separar em seção/aba `NOVAS DIVERGÊNCIAS IDENTIFICADAS`;
- utilizar IDs ND01, ND02... quando necessário;
- iniciar também como `☐`;
- não alterar a quantidade dos comentários formais.

## Validação obrigatória

Antes da saída:

1. contar comentários formais da origem;
2. contar comentários formais registrados;
3. confirmar igualdade exata;
4. confirmar ausência de IDs omitidos ou duplicados;
5. confirmar que todos iniciam `☐`;
6. confirmar que nenhuma divergência nova foi misturada à contagem formal;
7. confirmar que nenhum comentário foi eliminado por constar como atendido;
8. bloquear a emissão em qualquer falha de integridade.

Modo: `BLOCK_ON_ANY_FAILURE`.

## Excel

Quando solicitado Excel:

- reproduzir exatamente a quantidade e ordem validadas;
- quebra automática de texto;
- largura e altura suficientes para leitura confortável;
- alinhamento vertical superior para textos;
- borda externa preta grossa;
- bordas internas pretas normais;
- coluna “Comentário atendido” centralizada horizontal e verticalmente;
- quadrado `☐` / `☑` em 22 pt e negrito;
- permitir seleção manual somente entre `☐` e `☑`;
- incluir coluna “Evidência da verificação”;
- incluir aba `VERIFICAÇÃO` com controle de quantidade, pendências e evidências;
- novas divergências em aba separada.

## Memória e regressão

Quando ocorrer falha de padrão ou erro recorrente, gerar:

1. memória da ocorrência;
2. regra preventiva;
3. teste de regressão.

A memória nunca substitui documento contratual, normativo ou aprovado.
