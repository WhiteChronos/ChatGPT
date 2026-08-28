# Governança do conhecimento

## Autoridade técnica

O DEKS separa claramente **conteúdo técnico** de **tooling**.

A autoridade segue esta ordem:

1. documentos aprovados do projeto;
2. padrões gráficos e critérios do empreendimento;
3. listas, lógicas, C&E, I/O, datasheets e memoriais;
4. normas oficiais e legislação;
5. documentação oficial de fabricantes;
6. livros técnicos e artigos acadêmicos;
7. GitHub/open source.

## Mudanças externas

```mermaid
flowchart LR
    A[Commit upstream] --> B[Source Sync]
    B --> C[Candidato]
    C --> D[Revisão técnica]
    D -->|Aprovado| E[Datacenter]
    D -->|Rejeitado| F[Registro de rejeição]
    E --> G[Validação]
    G --> H[Publicação]
```

Mudança upstream **não** altera automaticamente definição técnica, tag, requisito normativo ou filosofia de controle.

## Controle de mudanças

Mudanças estruturais devem seguir branch e pull request. O CI precisa validar dados, schemas, testes e build documental antes de merge.

## Rastreabilidade

Cada verbete deve manter referência de fonte, classe de evidência, status e data de revisão. Quando houver conflito entre fontes, o sistema registra a condição em vez de escolher silenciosamente uma interpretação.
