---
name: arena-workflow
description: Conduzir Arena sozinho para revisar uma proposta, comparar soluções ou criticar um diff com evidências, usando o checklist ou perspectivas sequenciais sem iniciar torneio de agentes automaticamente.
---

# Entrada independente Arena

Defina o objeto da revisão, requisitos, restrições e evidências disponíveis.
Use a metodologia ou ferramentas realmente presentes no host:

1. Em revisão comum, use arena_review_checklist se exposto. Confira evidência,
   restrições, casos de borda e manutenção; use github=true para trabalho GitHub.
2. Quando alternativas complexas justificarem revisão ampliada, use arena_plan,
   arena_cards e arena_rubric, conforme a skill GitHub Arena instalada. Desenvolva
   e critique as perspectivas sequencialmente, com contexto necessário.
3. Produza achados sustentados, incertezas, recomendação e critérios de aceite.
   Verifique alegações técnicas com código, documentação e resultados reais.

Essas quatro ferramentas são planejamento/revisão; não executam agentes ou testes.
A skill Arena upstream descreve torneios, mas o padrão deste usuário é revisão
proporcional e sequencial. Um torneio real exige necessidade e autorização própria
com limite de consumo; o nome Arena no pedido não autoriza centenas de agentes.

Este modo funciona sem Replica ou Superpowers. Se o MCP estiver ausente, uma
revisão manual ainda pode ser útil, identificada como manual; não invente chamada
MCP. Não apresente pontuação como prova de execução, nem revisão sequencial como
revisão independente. Não publica comentários ou alterações por conta própria.
Para o conjunto de sistemas, encaminhe a replica-power-arena.
