# Chat local SponsoredTokens

Aplicacao privada de navegador para conversar pelo SponsoredTokens. O servidor
escuta somente em `127.0.0.1`, usa ativos locais e mantem o historico apenas na
memoria da aba. Atualizar ou fechar a pagina apaga a conversa.

## Iniciar

A variavel de usuario `SPONSOREDTOKENS_API_KEY` deve estar disponivel no
PowerShell. A chave nunca e enviada ao navegador, impressa ou gravada pelo app.

```powershell
python apps/sponsoredtokens-web/server.py --open
```

Sem `--open`, acesse o endereco local impresso. Use `--port 9000` para escolher
outra porta local. Pressione `Ctrl+C` no PowerShell para encerrar.

## Teste real opcional

O teste real faz uma unica chamada minima e informa somente resultado, provedor
e modelo:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Esse comando consome o servico real. Se o provedor estiver indisponivel, a
aplicacao pode retornar `upstream_unavailable`; aguarde a recuperacao do servico
e repita. Os demais codigos seguros incluem `configuration_required`,
`authentication_failed`, `quota_exhausted`, `rate_limited`, `upstream_timeout`,
`invalid_request` e `invalid_upstream_response`.

## Inicio automatico no Windows

O gerenciador registra uma tarefa apenas para o usuario atual. A tarefa inicia
no login, reinicia o processo se ele falhar e le a chave diretamente da
variavel de usuario do Windows. A chave nao entra no agendamento nem na linha de
comando.

```powershell
pwsh -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install
pwsh -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Start
pwsh -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Status
```

Para parar ou remover o inicio automatico:

```powershell
pwsh -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Stop
pwsh -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Uninstall
```

O estado tambem pode ser lido por automacao acrescentando `-Json`.

## Limites e separacao

Este app nao possui agentes, ferramentas, persistencia, telemetria, publicacao
na internet ou escolha de provedor. O Codex local pode usar o mesmo perfil
SponsoredTokens separadamente. O ChatGPT web continua usando o login e o plano
da conta; ele nao le a variavel desta aplicacao local.
