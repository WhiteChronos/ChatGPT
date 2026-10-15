---
name: rea-engenharia-reversa-evolutiva
description: Investigar de forma autorizada codigo, aplicativos, APIs, binarios e comportamentos usando engenharia reversa com evidencias rastreaveis; usar quando o usuario pedir REA, analise reversa, descoberta do funcionamento de sistemas, avaliacao de lacunas ou proposta de uma nova skill a partir de deficiencia comprovada.
---

# REA — engenharia reversa evolutiva

- Roteie a investigacao de acordo com o alvo, autoridade e ferramentas efetivamente disponiveis. Consulte a referencia `references/upstream.md`.
- Priorize analise estatica e material fornecido ou publico; execute REA CLI/MCP apenas quando realmente disponivel e autorizado. Nao chame revisao de codigo comum de execucao REA.
- Registre para cada achado: arquivo, versao/commit, evidencia, limite de observacao, hipotese alternativa e teste de confirmacao.
- Nao realize engenharia reversa de sistemas privados sem permissao, nem burle autenticacao/protecoes.
- Antes de gerar skill candidata, verifique se corrigir skill existente e mais simples e nao duplica responsabilidade.
- Organize aprendizado por feedback e testes verificaveis; proponha atualizacoes versionadas, sem afirmar que pesos do GPT se alteraram.
- Nunca instale software, publique, faca merge ou transmita dados sigilosos apenas por esta skill.
- REA e independente de Jev: analisa sistemas, nao gerencia a compactacao de contexto.
