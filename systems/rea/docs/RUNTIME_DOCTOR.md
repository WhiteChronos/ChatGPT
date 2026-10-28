# Runtime Doctor — REA

CONFIGURED: Skill e documentacao publicadas apos integracao do PR.
LOCAL_RUNTIME_HEALTHY: somente os testes do motor interno no pacote anterior, nao comprovam o host do REA oficial.
HOST_DISCOVERED: nao confirmado nesta sessao para ferramentas `rea-agents`.
LIVE_VERIFIED: nao confirmado.

## Instalacao

Dois tipos independentes de runtime: motor Python do pacote `SISTEMA_REA_INDEPENDENTE.zip` e REA oficial em `morluto/rea`. Nenhuma dependencia MCE. Instalar separadamente e nao registrar ambos com nomes ambiguos.

O host local deve verificar Node.js/npm compativeis, o comando `npx rea-agents setup`, o registro MCP gerado e ferramentas realmente descobertas. Para uso remoto Web, exigir HTTPS autenticado e revisao explicita de escopo antes de disponibilizar sistema de arquivos.
