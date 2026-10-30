---
name: mce-operacao-web
description: Usar o MCE independente por MCP privado no ChatGPT ou Codex para consultar skills, inspecionar modelo, registrar entendimento e elaborar copia preliminar somente com aprovacao externa vinculada aos arquivos. Acionar apenas em Matriz de Causa e Efeito.
---

# MCE pela conexao privada

1. Confirmar contexto MCE e chamar `mce_status`. Sem ferramenta real, registrar
   NOT_RUN; pacote instalado nao comprova execucao.
2. Consultar a skill canonica pertinente com `mce_read_skill`: engenharia-mce-projeto,
   padronizacao-mce ou mce-fechamento-operacional. Elas continuam donas da metodologia.
3. Solicitar o modelo e as fontes na conversa atual. Anexos do ChatGPT nao aparecem
   automaticamente no Windows: transferir apenas com autorizacao para a pasta
   exclusiva MCE `inbox`. Nao reutilizar documentos de outras conversas.
4. `mce_inspect_model` devolve estrutura e SHA sem aprovar o modelo. `mce_initialize`
   cria baseline nova a partir dos nomes autorizados, sem sobrescrever originais.
5. Preparar analise e contrato com evidencias literais conforme as skills existentes.
   `mce_understand` registra o entendimento e para em ANALISADO_AGUARDANDO_DECISAO.
6. `mce_approval_request` devolve hashes para revisao externa: nao e aprovacao.
   O operador responsavel valida modelo, fontes, projeto/SS, contrato e alteracoes;
   assina localmente a solicitacao exata com chave privada fora da pasta remota.
   A interface web recebe apenas a chave publica e o arquivo de aprovacao assinado.
   Nunca assinar em nome do humano, aceitar um simples "approved=true" ou carregar
   chave privada pela conversa. Ver `docs/WEB_MCP.md` na raiz do produto.
7. `mce_apply` exige assinatura valida e nao expirada, gera uma copia em job exclusivo
   e delega authorize/apply/audit ao motor existente. Alteracao de entrada invalida
   a aprovacao; uma tentativa consome a solicitacao e exige nova revisao se falhar.
8. Entregar copia preliminar, SHA, pendencias e auditoria para revisao multidisciplinar.
   Preservar mestre, formulas e estilos, maximo de 50 causas por folha; nao inferir
   setpoints, trips ou SIF. Nenhuma ferramenta certifica FAT/SAT ou producao.

REA, banco de outro sistema, shell arbitrario, portas publicas e aprovacao remota
nao fazem parte deste adaptador. Merge/deploy exigem autorizacao do SHA especifico.
