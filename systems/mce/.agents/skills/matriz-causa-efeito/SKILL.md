---
name: matriz-causa-efeito
description: Elaborar, revisar e auditar Matrizes de Causa e Efeito (MCE) de automacao industrial a partir de P&IDs, memoriais, narrativas, listas de I/O, filosofias, HAZOP/LOPA/SRS e Excel mestre aprovado. Usar para identificar causas, efeitos, intertravamentos, alarmes, trips, votacao, reset e bypass com rastreabilidade por TAG, pagina, revisao e SHA-256, integrando repositorios GitHub auxiliares e as Skills MCE existentes de WhiteChronos/ChatGPT. Nao usar para REA ou engenharia reversa de software. Exigir gates humanos e proteger o Excel original.
---

# Matriz de Causa e Efeito — orquestrador independente MCE

**Escopo exclusivo:** `MCE_INDEPENDENTE`. Atender elaboracao, revisao, consistencia e comprovacao de MCE industrial. Nao usar o sistema REA, banco de outro produto ou Desktop Commander. Esta Skill organiza as Skills existentes, **nao implementa outro editor de Excel**.

## GitHub e memorias antes de trabalhar

1. Consultar o [PR #118](https://github.com/WhiteChronos/ChatGPT/pull/118), HEAD atual, diffs, checks, revisoes, regras, e [Issue #120](https://github.com/WhiteChronos/ChatGPT/issues/120) incluindo comentarios de decisoes. Ler `systems/mce/AGENTS.md`, `systems/mce/spec/memoria.md`, `systems/mce/docs/GITHUB_MEMORY.md` e `docs/EXECUCAO.md`. Nao presumir que a Skill conhece o HEAD atual ou captura novas conversas.
2. Coordenar **apenas** `engenharia-mce-projeto` (entendimento e executor), `padronizacao-mce` (contrato inviolavel XLSX) e `mce-fechamento-operacional` (evidencias/aceite). As tres sao anteriores; nao refazer trabalho ja comprovado.
3. Consultar [references/repositorios-github.md](references/repositorios-github.md) para P&ID digital e benchmarks. Repositorios externos fornecem apenas topologia/OCR auxiliar, nunca autorizacao nem logica de seguranca aprovada.

## Fase 1 — inventario, entendimento e STOP

1. Identificar **projeto, SS, sistema, revisao**; inventariar modelo mestre XLSX real e P&ID, listas I/O, memorais/narrativas, filosofia, SRS/HAZOP/LOPA quando aplicavel. Registrar DOC_ID, revisao, pagina/folha, SHA-256 real e disciplina. Ausente = `NAO_DOCUMENTADO`.
2. Mapear Causas C, Efeitos F, TAG, estado normal/anormal, limiar, intertravamento, permissivos, temporizacao, reset, bypass e estados seguros **somente** com evidencia literal em fontes aprovadas. P&ID prova topologia, nao acao funcional; OCR/grafo nao aprova trip, SIF, votacao ou setpoint. Consultar [references/metodo-e-saidas.md](references/metodo-e-saidas.md).
3. Classificar cada relacao `DOCUMENTADO`, `INFERIDO_PARA_REVISAO` ou `NAO_DOCUMENTADO`, com fonte e revisao; contradicoes viram pendencias, nunca 'N/A' automatico. Nenhum preenchimento de logica por suposicao.
4. Quando Python real e fontes locais forem acessiveis/autorizados, seguir o executor existente em `systems/mce/.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py`: `init` e `understand`, conforme `docs/EXECUCAO.md`. No ChatGPT Web sem executor, entregar apenas analise documental e marcar os comandos `NOT_RUN`.
5. Emitir inventario, relatorio de entendimento, relacoes C→F rastreaveis e pendencias; parar em **`ANALISADO_AGUARDANDO_DECISAO`** antes de editar qualquer matriz.

## Fase 2 — apos autorizacao comprovada

1. Exigir modelo XLSX mestre oficial verificado (exemplo ficticio nao e oficial), contrato `contract.json` aprovado com whitelist `editable_cells` exata, `max_causes_per_sheet=50` ou menor pela geometria, projeto/SS documentados e autorizacao verificavel `AUTORIZO_ELABORACAO_MCE` ligada a hashes do baseline/fontes.
2. Usar somente o executor **canonico** (`authorize`, `apply --changes` e `audit`) em **copia derivada**. Alterar apenas texto expressamente autorizado e documentado; pintar cinza `D9D9D9` apenas onde realmente mudar. Nao tocar cabecalho, formulas, estilos funcionais, mesclas, relacoes OOXML ou folha nao autorizada.
3. Verificar AND/OR, m-de-n, permissivos, SIF, falhas, bypass, reset, temporizadores, sequencia, PLC/SIS/F&G com fontes literais e responsavel. Se faltar especificacao, conservar `PENDENTE`. Nunca converter alarme em SIF por inferencia.
4. Verificar SHA de fontes, diff de celulas, estrutura OOXML e inexistencia de alteracoes fora da whitelist. Saida so `MCE_PRELIMINAR_PARA_REVISAO`, pendente de disciplinas e FAT/SAT quando aplicavel.

## Saida e continuidade

Seguir as tabelas de [references/metodo-e-saidas.md](references/metodo-e-saidas.md): fontes, fatos por TAG e relacao C→F, pendencias, diferencas, gate/estado, evidencias/limites. Publicar em GitHub so metadados e decisoes **publicaveis**; nunca P&ID industrial privado, Excel mestre, credencial ou transcricao integral. Quando houver alteracao de codigo/Skill autorizada, anexar evento datado a `systems/mce/spec/memoria.md` no **mesmo commit** e verificar checks do SHA. Decisao publica pode entrar antes no Issue #120 por comentario estruturado autorizado.

**STOP:** faltam SS/fontes/revisoes ou modelo oficial/whitelist/autorizacao; ha contradicao funcional; proposta impacta seguranca sem SRS; nao ha executor real ou se tenta escrever no mestre. Sem merge/deploy nem `PRODUCTION_COMPLETE=YES` por instalacao, CI ou evidencias sinteticas.
