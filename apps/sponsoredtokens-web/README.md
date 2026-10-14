# Chat local SponsoredTokens com Laya

Aplicação privada de navegador que usa o SponsoredTokens como único gerador de
respostas. O servidor do chat escuta somente em `127.0.0.1:8765`; o classificador
Laya escuta somente em `127.0.0.1:8770`. O histórico permanece na memória da aba
e é apagado quando a página é atualizada ou fechada.

O Laya apenas escolhe uma das rotas `fast`, `balanced` ou `deep`. Ele não gera a
resposta, não fornece créditos e não aumenta o saldo generativo. Quando o Laya
está indisponível ou incerto, um classificador determinístico local mantém o chat
funcionando.

## Pré-requisitos

- Windows 11 com PowerShell;
- Python 3.11 disponível pelo `py -3.11` ou pelo comando `python`;
- variável de usuário `SPONSOREDTOKENS_API_KEY` já configurada;
- conexão com a internet na primeira instalação para baixar os pacotes e o
  checkpoint multilíngue.

A credencial é lida diretamente da variável de usuário do Windows. Ela não é
gravada pelo instalador, enviada ao navegador, impressa, adicionada ao atalho nem
colocada na linha de comando.

## Instalar e iniciar automaticamente

Confira primeiro o plano da instalação sem alterar arquivos ou processos:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -WhatIf -Json
```

Instale o runtime Python 3.11 isolado, a cópia estável e o atalho de inicialização:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -Json
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Start -Json
```

O runtime fica em
`%LOCALAPPDATA%\WhiteChronos\SponsoredTokensRuntimes\laya-0.4.6-py311`.
Nada é instalado no Python global. Na primeira execução, o Laya pode baixar e
aquecer o checkpoint multilíngue; isso pode levar vários minutos. O chat inicia
mesmo durante esse período e usa `deterministic` até o classificador ficar pronto.

O Laya seleciona automaticamente o dispositivo disponível. A ausência de CUDA
não impede a execução: o checkpoint pode operar em CPU, com latência maior. O
supervisor mantém somente o checkpoint multilíngue residente.

## Consultar o estado

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Status -Json
```

Campos principais:

- `installed`: cópia estável, runtime e atalho estão presentes;
- `running`: o servidor do chat respondeu;
- `ready`: a credencial SponsoredTokens está disponível para o chat;
- `routerRunning`: o processo HTTP do Laya respondeu em loopback;
- `routerReady`: o chat confirmou o protocolo de decisão do Laya;
- `router`: `laya` após uma decisão local válida; caso contrário,
  `deterministic`;
- `url`: endereço privado do chat.

Abra [http://127.0.0.1:8765/](http://127.0.0.1:8765/) somente depois de
`running=true`. A interface mostra `Laya local` ou `Fallback determinístico`
conforme o roteador que selecionou o modelo daquela resposta.

## Roteamento

Somente a última mensagem do usuário, limitada a 4.000 caracteres, chega ao
Laya. A conversa completa e a credencial SponsoredTokens não chegam ao
classificador.

- `fast`: `sponsored/openai/gpt-6-luna`;
- `balanced`: `sponsored/openai/gpt-5.6-luna`;
- `deep`: `sponsored/openai/gpt-5.1-codex-mini`.

Rotas `fast` ou `balanced` exigem confiança mínima de `0.70`. Resposta inválida,
redirecionamento, timeout, confiança baixa ou processo parado acionam o fallback
determinístico. A disponibilidade do chat depende do SponsoredTokens, não do
Laya.

## Smoke test real opcional

O comando abaixo faz uma única solicitação gerativa real e pode consumir saldo.
Ele imprime somente provedor, modelo e roteador, nunca o texto da resposta:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Os códigos seguros incluem `configuration_required`, `authentication_failed`,
`quota_exhausted`, `rate_limited`, `upstream_timeout`, `upstream_unavailable`,
`invalid_request` e `invalid_upstream_response`.

## Parar, recuperar e remover

Pare os processos instalados com:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Stop -Json
```

A instalação prepara e verifica o novo runtime antes de parar a versão atual. Na
ativação, a cópia anterior permanece em
`%LOCALAPPDATA%\WhiteChronos\SponsoredTokensLocalChat.backup`; se a ativação
falhar, o instalador restaura essa cópia automaticamente. Para uma reversão
operacional posterior, execute `Stop`, use o instalador da revisão Git anterior
e execute `Start`. A variável `SPONSOREDTOKENS_API_KEY` não é alterada.

Remova o atalho, a aplicação e o runtime pertencente ao aplicativo com:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Uninstall -Json
```

A remoção recusa caminhos fora de `%LOCALAPPDATA%\WhiteChronos` e preserva a
credencial de usuário.

## Limites e separação

Este aplicativo não publica portas na rede, não persiste conversas, não troca o
provedor generativo e não converte classificação local em tokens gratuitos. O
ChatGPT web continua usando o login e o plano da conta e não lê esta configuração
local.
