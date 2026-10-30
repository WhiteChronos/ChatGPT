# MCE em conversas de Matriz de Causa e Efeito

Plugin independente `mce-independent` 0.1.0: usa as tres Skills canonicas existentes
engenharia-mce-projeto, padronizacao-mce e mce-fechamento-operacional. O manifesto
Codex aponta para `.agents/skills/` dentro do sistema, sem novo editor de Excel.

Acionar somente para tarefas de Matriz de Causa e Efeito ou contexto MCE confirmado.
As Skills podem ser disponibilizadas globalmente; isso nao aplica MCE a qualquer
planilha nem vincula seu runtime, banco ou aprovacoes ao REA.

Ler memoria e Issue #120, identificar projeto/SS e inventariar as fontes reais da
conversa. Sem Excel mestre e contrato comprovados, registrar pendencias. Preservar
o gate ANALISADO_AGUARDANDO_DECISAO, AUTORIZO_ELABORACAO_MCE, 50 causas por folha,
cabecalhos, formulas, estilos e OOXML. Somente copia derivada e texto autorizado.

Leituras XML de workbook, relacionamentos, estilos e folhas usam defusedxml;
serializacao permanece no editor existente. Atualizacoes da skill canonica e do
espelho `.agents/skills` sao revisadas e verificadas por hash; nao sao dois motores.

Em Codex local, usar o Python MCE e arquivos autorizados. Na web sem executor,
executar apenas analise documental identificada e registrar NOT_RUN para comandos.
Nao declarar homologacao por instalacao, testes sinteticos ou metadata de aprovacao.
Memoria operacional, SQLite e backups ficam em host privado. PRODUCTION_COMPLETE=NO.


## Orquestrador canonico (2026-10-29)
Adicionar `matriz-causa-efeito` como quarta Skill, ponto de entrada para pedido de criacao/revisao de matriz. As tres Skills anteriores permanecem tecnicamente operativas, com scripts e contratos intactos. Nao ativar para REA nem assumir que um manifesto publicado no GitHub instala a Skill no host.

## Execucao do orquestrador matriz-causa-efeito

`plan` e `run` do script `systems/mce/scripts/matriz_causa_efeito_tool.py` usam os adaptadores existentes sem novo editor ou banco. Manifesto privado com referencias de origem e hashes do inventario. DataSheet privado e evento `STATUS` no SQLite MCE; revisar `pid_integration_review[]` antes de `mce_workflow.py understand`. Sem fonte real e host autorizado, marcar NOT_RUN.

## Plataforma para Codex — Windows exclusivo

A Skill `matriz-causa-efeito` só deve ser executada no Codex em Windows nativo (PowerShell/Python 3.12+). Não usar Linux, WSL ou Bash. Os três repositórios continuam como referências de formato, sem executar código de terceiros. O checkout GitHub não prova descoberta no host; validar na sessão real antes da utilização.
# Transporte privado opcional 0.2.0

A entrada continua matriz-causa-efeito. A quinta Skill mce-operacao-web orienta
somente o uso das sete ferramentas do adaptador MCP MCE, independente de REA.
Operacao e testes do produto permanecem Windows nativo. Ler WEB_MCP.md antes de
configurar raiz, pasta de aprovacoes e chave publica do operador; nao passar chave
privada ao servidor. Sem assinatura externa valida, nao aplicar alteracoes.
Instalacao, descoberta e chamada real no ChatGPT sao evidencias separadas.
