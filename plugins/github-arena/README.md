# GitHub Arena

Camada Arena global de qualidade para ChatGPT/Codex, com proteções adicionais para tarefas GitHub. Adaptada da metodologia MIT de [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill).

## Política

- **Micro Arena**: padrão para toda tarefa quando a Skill está instalada.
- **Review Arena**: para código, arquitetura, CI/CD, segurança, governança, APIs e mudanças de alto impacto.
- **Full Arena**: apenas quando explicitamente solicitado.
- Nunca afirmar que subagentes independentes foram executados quando o runtime não oferece essa capacidade.

## Codex global

O instalador copia a Skill para `$CODEX_HOME/skills/github-arena` (ou `~/.codex`) e acrescenta, sem apagar instruções existentes, um bloco global em `$CODEX_HOME/AGENTS.md`.

```bash
python plugins/github-arena/scripts/install_codex_global.py
```

Para apenas verificar:

```bash
python plugins/github-arena/scripts/install_codex_global.py --dry-run
```

## Componentes

- `SKILL.md`: contrato operacional e gatilhos globais.
- `agents/openai.yaml`: metadados da Skill.
- `references/upstream.md`: proveniência.
- `references/chatgpt-adaptation.md`: diferenças entre o Arena original e esta adaptação.
- `references/codex-global.md`: instalação e escopo global do Codex.
- `references/rubric.md`: pesos de avaliação.
- `scripts/arena_review.py`: planejador e distribuidor de strategy cards.
- `scripts/install_codex_global.py`: instalador idempotente do Codex.

## Teste

```bash
python plugins/github-arena/scripts/arena_review.py plan --agents 16
python plugins/github-arena/scripts/arena_review.py cards --agents 4 --seed 7
python plugins/github-arena/scripts/arena_review.py rubric
```
