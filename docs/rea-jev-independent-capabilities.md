# REA e Jev — duas funcionalidades independentes

**REA**: engenharia reversa generica e ciclo de aprendizagem via evidencias e revisao. Upstream: https://github.com/morluto/rea.

**Jev**: gestao do contexto acessivel e verificacao de perda de informacao. Upstream: https://github.com/tamaratran/fast-jev-compaction.

Cada integracao possui skill, referencia upstream e limite proprio. Nenhuma requer Codex como alvo: as instrucoes `SKILL.md` destinam-se ao ChatGPT Web. O GitHub WhiteChronos/ChatGPT guarda fontes, historico e revisoes, nao injeta hooks em ChatGPT.

## Contratos separados
- REA: input = alvo autorizado; output = mapa de comportamento com evidencias e recomendacoes. Execucao do CLI/MCP depende do host.
- Jev: input = contexto acessivel; output = representacao reduzida ou plano de retencao com checagem. Motor npm upstream nao esta instalado no ChatGPT Web.
- Integracao: compartilhar apenas o protocolo de proveniencia, deduplicacao e revisao, jamais misturar API keys.

## Evolucao continua
Problemas reproduziveis viram propostas de atualizacao da skill original ou de uma nova skill somente se houver responsabilidade nova. Validar com testes antes/depois; PR separada para cada modificacao relevante. Nao instalar ou mesclar automaticamente.

## Limites e seguranca
Nao ha inferencia paga, instalacao em computadores, merge, deploy ou producao declarada por esta proposta. Nao afirmar reducao de latencia sem benchmark nem autonomia fora da sessao.
