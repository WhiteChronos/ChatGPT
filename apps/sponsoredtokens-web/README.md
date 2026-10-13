# Chat local SponsoredTokens

Aplicacao privada de navegador para conversar pelo SponsoredTokens. O servidor
escuta somente em `127.0.0.1`, usa ativos locais e mantem o historico apenas na
memoria da aba. Atualizar ou fechar a pagina apaga a conversa.

## Iniciar

As variaveis de usuario `SPONSOREDTOKENS_API_KEY` e, opcionalmente,
`TYPESAFE_API_KEY` devem estar disponiveis no PowerShell. As chaves nunca sao
enviadas ao navegador, impressas ou gravadas pelo app. Crie a chave Jev no
painel oficial [TypeSafe AI](https://console.typesafe.ai/) e salve-a diretamente
como variavel de usuario do Windows; nao cole a chave em conversas nem no Git.

```powershell
python apps/sponsoredtokens-web/server.py --open
```

Sem `--open`, acesse o endereco local impresso. Use `--port 9000` para escolher
outra porta local. Pressione `Ctrl+C` no PowerShell para encerrar.

## Teste real opcional

O teste real faz uma unica chamada minima e informa somente resultado, provedor,
modelo e roteador:

```powershell
python apps/sponsoredtokens-web/server.py --live-smoke
```

Esse comando consome o servico real. Se o provedor estiver indisponivel, a
aplicacao pode retornar `upstream_unavailable`; aguarde a recuperacao do servico
e repita. Os demais codigos seguros incluem `configuration_required`,
`authentication_failed`, `quota_exhausted`, `rate_limited`, `upstream_timeout`,
`invalid_request` e `invalid_upstream_response`.

## Inicio automatico no Windows

O gerenciador instala uma copia estavel em `%LOCALAPPDATA%`, cria um atalho
oculto na pasta `Inicializar` apenas para o usuario atual e mantem um supervisor
que reinicia o processo se ele falhar. A chave e lida diretamente da variavel
de usuario do Windows; ela nao entra no atalho nem na linha de comando.

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

## Roteamento Jev

A Jev atua somente como roteador de decisao. Para cada envio, recebe apenas a
ultima mensagem do usuario, limitada a 4.000 caracteres, e escolhe uma rota:

- `fast`: `sponsored/openai/gpt-6-luna`;
- `balanced`: `sponsored/openai/gpt-5.6-luna`;
- `deep`: `sponsored/openai/gpt-5.1-codex-mini`.

O SponsoredTokens continua sendo o unico gerador de respostas. Se a chave Jev
nao estiver configurada, for invalida ou o servico estiver indisponivel, a
aplicacao usa automaticamente a rota `deep` e continua pelo SponsoredTokens.

## Limites e separacao

Este app nao possui agentes, ferramentas, persistencia, telemetria, publicacao
na internet ou escolha de provedor generativo. O Codex local pode usar o mesmo perfil
SponsoredTokens separadamente. O ChatGPT web continua usando o login e o plano
da conta; ele nao le a variavel desta aplicacao local.
