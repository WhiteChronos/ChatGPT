---
name: rea-operacao
description: Executar investigacao estatica read-only pelo motor REA independente, com analise de dependencias, SHA-256, lista de ferramentas MCP e comparacao Arena de alternativas. Usar somente para codigo-fonte ou catalogos autorizados no Codex ou ChatGPT Web com runtime REA de fato disponivel.
---

# REA independente - operacao read-only

1. Confirmar autorizacao para o diretorio-alvo e SHA de referencia. Nao analisar outros sistemas por inferencia nem obter dados externos nao autorizados.
2. Executar `rea_bridge_status` como primeira chamada e classificar o upstream `morluto/rea` como indisponivel se nenhum runtime independente o provar. Nunca afirmar que o motor proprio e o upstream oficial.
3. Quando o MCP estiver realmente disponivel, usar `rea_project_inventory`, `rea_source_inspect`, `rea_internal_analyze`, `rea_verify_evidence`, `rea_repositories_top10` e `rea_arena_compare` conforme a tarefa. As sete ferramentas sao somente leitura.
4. Registrar fonte, caminho, SHA-256, timestamp, versao, evidencia, incerteza e passo de reproducao. Arena gera perspectivas heuristicas, **never** agents/subagentes realmente independentes sem runtime comprovado.
5. Tratar recusas de caminho, symlink, arquivos sensiveis e outros erros de permissao como bloqueios de seguranca. Sem correcao documentada e teste adversarial, nao abrandar o filtro.
6. Proteger a separacao: REA nao importa MCE, nao edita o Excel mestre e nao escreve no projeto analisado. O SDK MCP local opera apenas em loopback, salvo tunel privado autorizado.
7. Em ChatGPT Web sem servidor descoberto, informar `REA_RUNTIME=UNAVAILABLE` e realizar somente revisao manual identificada, nunca simular uma chamada de ferramenta.

NUNCA emitir `PRODUCTION_COMPLETE=YES` por CI verde ou por manifestos; requer host, MCP conectado, chamada real, controle de acesso, auditoria e aceite operacional.
