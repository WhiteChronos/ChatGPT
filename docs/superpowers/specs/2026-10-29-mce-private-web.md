# MCE Independente — conexão web e elaboração controlada

Proposta de 29/10/2026. Fonte existente: WhiteChronos/ChatGPT, PR #118,
HEAD observado 873fdf2b2f8a49b92e9fc23bda3ce1d642392cee.
O usuário selecionou consulta e elaboração pela web. Este documento especifica
a nova interface; não autoriza editar qualquer modelo real ou publicar serviço.

## Resultado esperado

Um plugin MCE próprio no ChatGPT, com as skills canônicas de engenharia,
padronização e fechamento, e uma conexão privada com o motor MCE existente.
O pacote permanece utilizável localmente sem REA, túnel ou serviço web.

## Fluxo

1. Consultar estado, skills e requisitos; confirmar que a tarefa é MCE.
2. Receber somente fontes que o usuário autorize para este ambiente. Arquivos de
   outra conversa e anexos web não aparecem automaticamente no computador.
3. Inventariar hashes, congelar uma cópia do modelo e elaborar entendimento e
   pendências pelo workflow existente. Parar em ANALISADO_AGUARDANDO_DECISAO.
4. Antes de aplicar: exigir projeto/SS documentados, modelo validado, whitelist
   de células e AUTORIZO_ELABORACAO_MCE vinculada aos hashes e ao contrato.
   A interface remota não pode criar sua própria aprovação. Uma aprovação
   externa verificável, fora da área que a interface pode escrever, libera
   somente a alteração revisada; modificar qualquer entrada invalida a liberação.
5. Gerar uma cópia preliminar, destacar texto autorizado em cinza e executar a
   auditoria OOXML existente. Entregar cópia, pendências e evidências para revisão.

## Limites

- Usar os scripts canônicos; não copiar o motor REA nem criar outro editor Excel.
- Pasta MCE exclusiva, separada do código, do REA e do banco de outros sistemas.
- Entradas/saídas confinadas; bloquear travessia, links, segredos, arquivos grandes,
  arquivos compactados perigosos e saídas existentes. Sem shell arbitrário.
- Máximo de 50 causas por folha; preservar mestre, fórmulas, estilos, imagens e
  cabeçalhos. Nenhum setpoint, trip, TAG ou aprovação inferidos.
- Túnel e credencial próprios ou reutilização expressamente autorizada; sem portas
  públicas. Confirmar criação/conexão quando o acesso concreto estiver preparado.
- Documentos industriais e banco privado não vão para o GitHub.
- Merge/deploy somente com autorização do SHA específico; não publicar no workspace
  nem ampliar acesso por consequência da instalação pessoal.

## Verificação

Testes primeiro para bloqueios e autorização, regressão MCE Windows/Linux,
scanner do produto completo, integridade das skills e workflow de memória.
Prova separada de SDK local, conexão privada, descoberta no ChatGPT e chamada real.
Exemplos sintéticos verificam conectividade, nunca engenharia de projeto real.

## Alternativas avaliadas

- Só skills: distribuição imediata, mas sem execução comprovada do motor na web.
- Skills e conexão privada controlada: escolhida pelo usuário para consulta e
  elaboração; exige os gates acima e instalação própria do MCE.
- API pública ou escrita irrestrita: não atende à preservação documental exigida.

## Ainda necessários para aceite real

Modelo mestre, fontes/revisões, projeto/SS, contrato de células, aprovação humana,
revisão multidisciplinar, aceite e FAT/SAT quando aplicável. Produção permanece
não comprovada até essas evidências e a validação ponta a ponta.
