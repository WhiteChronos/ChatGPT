# REA — Engenharia Reversa (sistema independente)

REA e produto autonomo, **nao e modulo do sistema MCE**. A Skill em `.agents/skills/rea-engenharia-reversa-evolutiva/` organiza analises seguras, evidencias e lacunas verificaveis.

## Distincao de runtimes

1. REA **oficial**: [morluto/rea](https://github.com/morluto/rea) e pacote npm `rea-agents`. Instalar no computador/host suportado conforme documentacao oficial, por exemplo `npx rea-agents setup`; conferir versao e prerequisitos atuais, aprovar alteracoes, reiniciar agente e verificar `tools/list` real no host.
2. Motor **interno anterior**: artefato de entrega `SISTEMA_REA_INDEPENDENTE.zip`, com servidor Python de analise estatica/MCP. O ZIP nao foi automaticamente espelhado aqui. Nao chamar o motor interno de copia integral do REA oficial.
3. ChatGPT Web: Skills textuais disponiveis nao implicam servidor MCP ativo ou instalacao permanente. Para usar REA na Web, configurar uma integracao MCP aprovada e exposta por HTTPS com controle de acesso e depois comprovar descoberta e testes reais.

## Contratos operacionais

- Inspecionar apenas fontes autorizadas; nao contornar autenticacao, licencas ou protecoes.
- Registrar alvo, commit/SHA, localizacao, ferramenta, observacao e reproducibilidade.
- Usar GitHub Arena e Superpowers quando presentes; nunca representar perspectivas do mesmo modelo como subagentes independentes.
- Proibir publicacao de segredos, arquivos privados, dumps de memoria ou dados do usuario.
- Respeitar `AGENTS.md` e a governanca da raiz.

## Estado desta entrega

Este PR e uma **primeira integracao publicavel da Skill REA**, com documentacao de conexao, nao a instalacao de `rea-agents`, um espelhamento do ZIP interno, ou um deploy Web. Motor, testes de runtime, servidor e endpoint HTTPS sao gates posteriores a serem validados separadamente.
