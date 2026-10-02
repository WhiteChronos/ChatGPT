# GitHub Arena

Camada de revisão multi-estratégia para tarefas GitHub, adaptada da metodologia do projeto MIT [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill).

## Política

- **Micro Arena**: obrigatório em toda tarefa GitHub.
- **Review Arena**: para mudanças de alto impacto.
- **Full Arena**: apenas quando explicitamente solicitado.
- Nunca afirmar que subagentes independentes foram executados quando o runtime não oferece essa capacidade.

## Componentes

- `SKILL.md`: contrato operacional e gatilhos.
- `agents/openai.yaml`: metadados da Skill.
- `references/upstream.md`: proveniência.
- `references/chatgpt-adaptation.md`: diferenças entre o Arena original e esta adaptação.
- `references/rubric.md`: pesos de avaliação.
- `scripts/arena_review.py`: planejador e distribuidor de strategy cards.

## Teste

```bash
python plugins/github-arena/scripts/arena_review.py plan --agents 16
python plugins/github-arena/scripts/arena_review.py cards --agents 4 --seed 7
python plugins/github-arena/scripts/arena_review.py rubric
```
