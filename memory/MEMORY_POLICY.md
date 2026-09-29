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
8. `BASELINE`: snapshot de referência usado para provar que uma revisão histórica não foi alterada.
9. `REVISION_EVENT`: evento controlado de criação de uma nova revisão documental.

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

## Regra específica para LI - Lista de Material

A memória canônica de controle de LI é `memory/LI_MATERIAL_CONTROL_MEMORY.yaml`.

Ela deve registrar cada nova revisão de LI, mas nunca substituir a própria planilha emitida. Para qualquer revisão:
- a coluna da revisão anterior permanece imutável;
- `REV. 0` nunca é apagada ou corrigida em lugar da nova revisão;
- a nova revisão entra na coluna imediatamente à direita;
- fontes de quantitativo e conflitos são registrados;
- `A LEVANTAR` deve ter justificativa;
- o QA deve registrar comparação estrutural e histórica;
- alteração de revisão histórica é regressão crítica e recebe `REPROVADO`.

## Hierarquia de verdade

A memória não substitui documentos contratuais ou normativos. Ela registra interpretação e histórico. Quando houver divergência, deve ser aplicado o critério de autoridade documental do projeto.

## Retenção

Não estabelecer prazos de descarte arbitrários para decisões, regras, conflitos, pendências, fontes, baselines, eventos de revisão ou regressões técnicas. Qualquer política de retenção deve ser definida explicitamente pelo projeto e registrada como regra versionada.

## Dados sensíveis

Este repositório é público. Não inserir desenhos proprietários, documentos contratuais, credenciais, dados pessoais, dados de cliente ou qualquer conteúdo confidencial. Guardar somente regras, estruturas, exemplos anonimizados e metadados não sensíveis.
