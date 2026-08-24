# Política de Memória Técnica Persistente

## Objetivo

Garantir que decisões, correções, falhas, lições aprendidas e critérios aprovados nunca sejam perdidos entre revisões do aplicativo e dos documentos de engenharia.

## Tipos de memória

1. `DECISION`: decisão técnica aprovada.
2. `LESSON`: lição aprendida a partir de erro ou retrabalho.
3. `RULE`: regra de engenharia ou validação.
4. `CONFLICT`: conflito entre documentos ou interpretações.
5. `PENDING`: informação ainda não confirmada.
6. `SOURCE`: fonte documental e evidência associada.
7. `REGRESSION`: erro que já ocorreu e deve possuir teste para impedir repetição.

## Regra de persistência

Cada registro deve conter, no mínimo:
- identificador único;
- data/hora;
- categoria;
- descrição;
- status;
- origem;
- documento e revisão quando aplicável;
- evidência (folha, página, nota, item ou hash);
- impacto;
- regra ou teste de regressão associado;
- versão do aplicativo em que foi incorporado.

## Nunca esquecer

Quando um erro for detectado e corrigido, devem existir três registros vinculados:
1. memória da ocorrência;
2. regra de prevenção;
3. teste automatizado de regressão.

Uma correção sem esses três elementos é considerada incompleta.

## Hierarquia de verdade

A memória não substitui documentos contratuais ou normativos. Ela registra interpretação e histórico. Quando houver divergência, deve ser aplicado o critério de autoridade documental do projeto.

## Retenção

Não estabelecer prazos de descarte arbitrários para decisões, regras, conflitos, pendências, fontes ou regressões técnicas. Qualquer política de retenção deve ser definida explicitamente pelo projeto e registrada como regra versionada.

## Dados sensíveis

Este repositório é público. Não inserir desenhos proprietários, documentos contratuais, credenciais, dados pessoais, dados de cliente ou qualquer conteúdo confidencial. Guardar somente regras, estruturas, exemplos anonimizados e metadados não sensíveis.
