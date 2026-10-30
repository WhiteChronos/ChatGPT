---
name: matriz-causa-efeito
description: Elaborar, revisar e auditar Matrizes de Causa e Efeito (MCE) de automação industrial a partir de P&IDs, memoriais, narrativas, listas de I/O, filosofias de controle, HAZOP/LOPA/SRS e Excel mestre aprovado. Usar para mapear causas, efeitos, intertravamentos, alarmes, trips, votações, reset e bypass com evidências por TAG e revisão, pesquisar repositórios GitHub auxiliares e orquestrar as Skills MCE do WhiteChronos/ChatGPT. Não usar para engenharia reversa de software nem REA. Bloquear alterações do Excel sem autorização e manter histórico no GitHub.
---

# Matriz de Causa e Efeito — orquestração MCE independente

**Escopo exclusivo:** `MCE_INDEPENDENTE`. Conduzir apenas elaboração, revisão, consistência, evidências, padronização e fechamento de MCE. Não usar motor, código, banco ou ferramentas REA; não utilizar Desktop Commander.

## Recuperar a fonte de verdade antes de agir

1. Consultar no GitHub `WhiteChronos/ChatGPT` o **HEAD atual** do PR [#118](https://github.com/WhiteChronos/ChatGPT/pull/118), sua CI, revisões e regras. Tratar SHA citado nos documentos como histórico, não como HEAD atual.
2. Ler `systems/mce/AGENTS.md`, `systems/mce/spec/memoria.md`, `systems/mce/docs/EXECUCAO.md`, `systems/mce/docs/GITHUB_MEMORY.md` e o índice [Issue #120](https://github.com/WhiteChronos/ChatGPT/issues/120), incluindo comentários estruturados ainda pendentes de espelhamento. Preservar DEC/PEND e seguir o último estado **comprovado**.
3. Para P&ID digital e integração GitHub, consultar [references/repositorios-github.md](references/repositorios-github.md). Repositórios de pesquisa só ajudam a extrair/conferir topologia e texto; não fornecem lógica operacional aprovada.
4. Carregar/seguir as Skills do mesmo sistema `engenharia-mce-projeto`, `padronizacao-mce` e, no fechamento, `mce-fechamento-operacional`. Não as substituir por um segundo editor de Excel.

## Fase 1 — identificar, analisar e PARAR antes de escrever Excel

1. Identificar explicitamente projeto, **SS**, sistema, documento, revisão e disciplina. Inventariar **modelo mestre real** e fontes (P&ID, lista I/O, narrativa, memorial, filosofia de controle, SRS/HAZOP/LOPA quando aplicável) com SHA-256 e localização verificável; marcar ausência como `NAO_DOCUMENTADO`.
2. Distinguir topologia física em P&ID de lógica funcional: **P&ID e OCR nunca bastam para inferir trip, setpoint, votação, reset ou SIF**. Só converter relação causa→efeito quando narrativa/filosofia/SRS e sua revisão oferecerem evidência literal. Mapear TAG, estado, sequência e consequência em [references/metodo-e-saidas.md](references/metodo-e-saidas.md).
3. Classificar cada afirmação como `DOCUMENTADO`, `INFERIDO_PARA_REVISAO` ou `NAO_DOCUMENTADO`; registrar documento, SHA-256, revisão, folha/página, transcrição curta ou referência e disciplina responsável. Não elevar candidato derivado de OCR/grafo a fato ou comando de segurança.
4. Se houver executor Python autorizado com fontes locais, seguir `systems/mce/docs/EXECUCAO.md` e usar **somente** o executor canônico `systems/mce/.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py` (`init`, `understand`). Se não houver acesso ao executor, elaborar só relatório documental e informar `NOT_RUN` para comandos.
5. Apresentar inventário, relatório de entendimento, causas/efeitos candidatos e pendências; **parar em `ANALISADO_AGUARDANDO_DECISAO`** antes de alterar qualquer matriz. Não simular autorização.

## Fase 2 — elaborar SOMENTE após gate humano

1. Exigir modelo XLSX mestre **homologado e rastreado** (o exemplo local não é oficial), contrato `contract.json` aprovado com `editable_cells` exatas, `max_causes_per_sheet=50` (ou menos pela área real), projeto e SS documentados, fontes identificadas, e autorização humana verificável `AUTORIZO_ELABORACAO_MCE` vinculada ao baseline e aos hashes das fontes.
2. Apenas nesse estado, usar `authorize`, `apply --changes alteracoes.json` e `audit` do executor **canônico** em uma **cópia derivada** do `.xlsx`; editar somente **texto autorizado** e destacar apenas células realmente alteradas em cinza `D9D9D9`. Não alterar cabeçalhos, fórmulas, estilos funcionais, mesclas, imagens, abas, layout ou áreas de impressão.
3. Validar e rastrear lógica **AND/OR, m-de-n, estados seguros, falha, bypass, startup/shutdown, reset, temporização e implementação PLC/SIS/F&G** apenas quando fontes contratuais determinarem seu valor/comportamento; caso contrário manter `PENDENTE`.
4. Auditar OOXML, SHA de entrada, diff de células e permissões; emitir somente `MCE_PRELIMINAR_PARA_REVISAO`. Exigir revisão de Processo, Instrumentação, Automação, Operação e Segurança conforme escopo, sem homologar FAT/SAT por teste sintético.

## Responder e guardar continuidade

Usar [references/metodo-e-saidas.md](references/metodo-e-saidas.md) para os formatos de inventário, rastreabilidade, pendências e gates. Escrever com termos de engenharia; explicitar o que é fato versus pendência, fontes, revisão e status.

Se houver atualização de código/Skill autorizada, registrar no **mesmo commit** um evento datado em `systems/mce/spec/memoria.md`, atualizar ambos os espelhos da Skill e executar as verificações da CI MCE. Decisões publicáveis podem ser registradas no Issue #120 pelo conector GitHub **quando disponível e autorizado**; nunca enviar documentos confidenciais, Excel mestre, banco SQL privado ou transcrição integral de chat. A Skill e o GitHub não capturam mensagens automaticamente.

**STOP obrigatório:** ausência de fontes/SS, divergência de revisões, autorização, contrato ou modelo oficial, impacto funcional sem evidência, conflito de lógica de segurança ou tentativa de escrever fora de whitelist. Nunca fazer merge/deploy ou declarar `PRODUCTION_COMPLETE=YES` sem gates externos e aceite humano comprovado.

## Ferramenta executável de pré-análise — DataCenter e DataSheet MCE

**Uma única Skill orquestradora**, utilizando as três Skills de engenharia/padronização/fechamento e o **único DataCenter SQLite do MCE**. Não criar banco independente da ferramenta. Consultar [references/operacao-ferramenta.md](references/operacao-ferramenta.md) e `systems/mce/docs/MATRIZ_CAUSA_EFEITO_TOOL.md` antes de executar.

1. Para comparar as três interfaces GitHub já documentadas (`azure`, `houston`, `industrial`), preparar um `workspace` **já inventariado** pelo MCE com modelo `.xlsx` e fontes registradas por SHA. Entradas: exportações do próprio usuário, jamais clonagem de código de terceiros. O terceiro repositório `Industrial-Control` é apenas benchmark didático e não uma fonte funcional de segurança do projeto.
2. Preparar `manifest.json` com `schema=mce.matriz-tool.manifest.v1`, `run_id` único, lista `sources[]` (um registro por adaptador contendo `source_name`, `document`, `revision`, `location`) e `io_source_name` opcional. **Nenhum** dado industrial entra no GitHub.
3. Em host autorizado com checkout MCE e SQLite privado previamente inicializado, executar o script canônico **sem criar executor duplicado**:

   ```powershell
python .\systems\mce\scripts\matriz_causa_efeito_tool.py plan --workspace "C:\MCE_DADOS\PROJETO" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
python .\systems\mce\scripts\matriz_causa_efeito_tool.py run --workspace "C:\MCE_DADOS\PROJETO" --manifest "C:\MCE_DADOS\manifest.json" --db "C:\MCE_DADOS\mce.sqlite3"
```

4. Confirmar `PRE_ANALISE_PENDENTE_REVISAO`, `human_review_required=true`, `cause_effect_relations_approved=0` no `MCE_<run_id>_DATASHEET.json` e evento `MCE_TOOL_MATRIZ_CAUSA_EFEITO` no SQLite MCE. O DataSheet segue `systems/mce/datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json` e é privado. A memória pública do MCE continua `systems/mce/spec/memoria.md` + GitHub Issue #120.
5. Exigir uma `pid_integration_review[]` humana para **cada** derivado no `analise.json`; acionar o executor anterior `mce_workflow.py understand` para chegar a `ANALISADO_AGUARDANDO_DECISAO`. Nem o DataSheet nem o SQLite podem emitir `AUTORIZO_ELABORACAO_MCE` ou liberar edição no Excel.
6. Validação exclusiva em Windows, PowerShell e Python 3.12, por `.github/workflows/mce-matriz-tool-qa.yml` e demais workflows MCE. Não executar ou testar em Linux/WSL. Os testes usam somente fontes sintéticas. **Nao usar** o sistema REA, execução de código de repositórios de terceiros ou entrada automática do chat. **Sem merge/deploy** e `PRODUCTION_COMPLETE=YES` sem aceite real.

Se o ChatGPT Web não expuser execução local, limitar-se à análise documental e apresentar **NOT_RUN** para esses comandos. A presença da Skill instalada não comprova o runtime do script ou o modelo mestre aprovado.

## Windows como unica plataforma de desenvolvimento

- Criar, testar e operar `matriz-causa-efeito` **apenas em Windows nativo** com PowerShell e Python 3.12+. Não usar Linux, WSL, Bash nem contêiner Linux. A CLI recusa sistema operacional não Windows.
- Uma só Skill MCE coordena `engenharia-mce-projeto`, `padronizacao-mce` e `mce-fechamento-operacional`; não cria banco, executor OOXML nem serviço paralelo.
- Usar os três repositórios GitHub como contratos **auxiliares** de exportação, por adaptadores locais: Azure-Samples (grafo P&ID), S-Houston (OCR CSV) e ZzzJjt/Industrial-Control (benchmark didático, sem validade de trip ou SIF). Não executar fontes de terceiros.
- Os workflows **exclusivos do MCE** usam `windows-latest`. Workflows globais compartilhados permanecem sob governança própria e não são modificados por esta Skill.
- O workflow Windows cria o pacote `skill.zip` com `Compress-Archive` e publica o artefato `matriz-causa-efeito-windows-skill`. Instalação real no Codex/ChatGPT Web depende de teste separado.


## Memoria ligada a GitHub, DataCenter e novas conversas

Ao receber **"retomar MCE"** ou iniciar tarefa MCE em outro chat, seguir `systems/mce/docs/RETOMADA_ENTRE_CHATS.md` e consultar primeiro a memoria GitHub, Issue #120, PR #118 com HEAD/CI atual e as Skill/MCE AGENTS. Nao presumir que a versao instalada no ChatGPT Web iguala a do GitHub. Recuperar tambem eventos pendentes no Issue, sem tratar o mesmo ID como prova de semantica igual.

A unica ponte `systems/mce/scripts/mce_context_bridge.py` gera em **Windows nativo** checkpoint `mce.context-handoff.v1` somente com ponteiros GitHub, IDs e SHA-256 do Markdown e, opcionalmente, integridade/hash/contagens do **mesmo** DataCenter SQLite. Sem conexao autorizada, registrar `PRIVATE_NOT_CONNECTED`; nunca transmitir documentos, eventos privados, anexos, banco ou backup ao GitHub.

Evolucao continua **por eventos explicitamente capturados**, nao em segundo plano: decisao publicavel -> Issue #120 pelo GitHub autorizado; mudanca de codigo ou Skill -> `spec/memoria.md` no mesmo commit e CI Windows; evento operacional privado -> ledger SQLite/MCE. Novos fatos corrigem historico por adicao, nao o apagam. Alerta 30/10/2026: `PEND-MCE-014` no Issue e no Markdown têm assuntos divergentes; exigir conciliacao humana. Nao prometer retencao literal de todas as conversas, aprendizagem nativa permanente, autoaprovacao, edicao Excel sem autorizacao ou `PRODUCTION_COMPLETE=YES`.
