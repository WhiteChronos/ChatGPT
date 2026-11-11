# Evolução verificável do adaptador Replica + Power + Arena

> Execução sequencial com executing-plans; preservar aprovações anteriores.

**Objetivo:** acrescentar diagnóstico, correção, regressão e aprendizado ao
adaptador existente, sem fundir os três repositórios oficiais.

**Desenho:** SKILL.md encaminha para uma referência curta de evolução. O agente
usa validadores existentes e registra antes/depois; não há daemon ou modelo
autônomo embutido. Atualizações de upstream ficam em PRs separados.

**Tecnologia:** Markdown, pacote de plugin existente e Python stdlib.

- [x] Preservar as onze skills e seis ferramentas upstream fixadas.
- [x] Definir ciclo com evidência, revisão Arena e limite de duas tentativas.
- [ ] Validar o pacote e referências; confirmar repositórios separados.
- [ ] Atualizar skill local, pacote web existente e PR #111 sem merge automático.

**Aceite:** doze skills permanecem válidas, instruções não prometem background,
aprendizado não altera memórias pessoais e cada host tem prova separada.
