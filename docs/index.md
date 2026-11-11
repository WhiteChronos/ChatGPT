# Digital Engineering Knowledge System

O **DEKS** transforma o glossário de engenharia em uma base interativa, pesquisável e rastreável. A fonte técnica permanece no datacenter estruturado; este site é uma visualização gerada e controlada por CI.

<div class="deks-hero-grid">
  <a class="deks-hero-card" href="generated/glossary/index/">
    <strong>Glossário interativo</strong>
    <span>Pesquisar termos, tags, funções e disciplinas.</span>
  </a>
  <a class="deks-hero-card" href="generated/knowledge-map/">
    <strong>Mapa de conhecimento</strong>
    <span>Navegar pelas relações entre objetos de engenharia.</span>
  </a>
  <a class="deks-hero-card" href="generated/sources/">
    <strong>Fontes e proveniência</strong>
    <span>Ver origem, papel e estado das fontes monitoradas.</span>
  </a>
  <a class="deks-hero-card" href="generated/status/">
    <strong>Estado do sistema</strong>
    <span>Ver validação, avisos e candidatos pendentes.</span>
  </a>
</div>

## Como o sistema funciona

```mermaid
flowchart LR
    A[Datacenter estruturado] --> B[Validação]
    B --> C[Modelo canônico]
    C --> D[Gerador de documentação]
    D --> E[Site interativo]
    C --> F[Datasheets / API / relatórios]
    G[Fontes GitHub permitidas] --> H[Sincronização]
    H --> I[Fila de candidatos]
    I --> J[Revisão técnica]
    J --> C
```

!!! warning "Regra de autoridade"
    GitHub é usado para tooling, software, modelos, validação e automação. Não substitui documentos aprovados do projeto, normas oficiais ou critérios de engenharia.

## Estado de maturidade

A versão atual entrega a fundação do sistema: datacenter, validação, geração automática, busca, filtros, mapa de relações, rastreabilidade de fontes e build reprodutível no GitHub Actions.
