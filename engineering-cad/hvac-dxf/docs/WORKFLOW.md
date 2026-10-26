# Workflow do Processo — Bloco Técnico

## Objetivo
Garantir que todo bloco técnico seja produzido a partir de evidência rastreável e possa ser auditado, revisado e melhorado sem perda de histórico.

## Fluxo canônico

```text
ENTRADA DO PROJETO
      |
      v
[1] IDENTIFICAR O OBJETO
      |
      +--> TAG / função / disciplina / família
      +--> fabricante/modelo já informado?
      |
      v
[2] RESOLVER IDENTIDADE TÉCNICA
      |
      +--> fabricante
      +--> série
      +--> modelo exato
      +--> part number / variante
      |
      +-- se ambíguo --> BLOQUEADO
      |
      v
[3] PESQUISAR FONTES
      |
      +--> página oficial
      +--> catálogo
      +--> ficha técnica PDF
      +--> manual
      +--> desenho dimensional
      +--> CAD/BIM
      +--> fornecedores
      |
      v
[4] CLASSIFICAR A FONTE
      |
      +--> CAD_FABRICANTE
      +--> RECONSTRUCAO_FICHA
      +--> REFERENCIA_PROJETO
      +--> BLOQUEADO
      |
      v
[5] ELABORAR / NORMALIZAR BLOCO
      |
      +--> 1:1
      +--> metros
      +--> Arial
      +--> layers
      +--> vistas
      +--> interfaces/montagem
      |
      v
[6] QA TÉCNICO
      |
      +--> identidade
      +--> dimensões
      +--> extents
      +--> furos/conexões
      +--> auditoria DXF
      +--> comparação visual
      +--> proveniência
      |
      +-- falha --> CORREÇÃO / EVOLUÇÃO
      |
      v
[7] APROVAR E PUBLICAR
      |
      +--> DXF
      +--> manifesto
      +--> fontes
      +--> QA
      +--> classe de confiança
      |
      v
[8] MEMÓRIA E MELHORIA
      |
      +--> registrar erro
      +--> causa raiz
      +--> regra reaproveitável
      +--> regressão
      +--> revisão humana quando necessário
```

## Gates obrigatórios

### Gate G0 — Entrada mínima
Necessário:
- objeto ou TAG;
- disciplina;
- função ou família.

Sem isso: não iniciar modelagem.

### Gate G1 — Identidade
Para avançar como bloco real:
- fabricante confirmado;
- modelo/part number confirmado ou família tecnicamente inequívoca;
- pelo menos dois discriminadores técnicos compatíveis.

Se não: `BLOQUEADO`.

### Gate G2 — Evidência dimensional
Aceitar:
- CAD/BIM do fabricante; ou
- desenho dimensional/ficha oficial suficiente para reconstrução.

Foto comercial não atende o gate.

### Gate G3 — Elaboração
O arquivo deve atender:
- Model Space 1:1;
- unidade em metros;
- Arial;
- geometria preservada ou reconstruída por cotas;
- views e interfaces conforme fonte.

### Gate G4 — QA
Todos os itens críticos devem passar:
- identidade;
- dimensões;
- extents;
- unidades;
- montagem;
- conexões;
- auditoria DXF;
- comparação visual;
- proveniência.

### Gate G5 — Publicação
Publicar somente com:
- DXF;
- manifesto;
- fontes;
- resultado de QA;
- classe de confiança;
- conflitos pendentes registrados.

## Saídas por status

| Status | Uso permitido |
|---|---|
| CAD_FABRICANTE | layout, interferência, montagem, biblioteca final |
| RECONSTRUCAO_FICHA | layout e interferência conforme evidência disponível |
| REFERENCIA_PROJETO | estudo preliminar/envelope somente |
| BLOQUEADO | não usar para projeto executivo |
