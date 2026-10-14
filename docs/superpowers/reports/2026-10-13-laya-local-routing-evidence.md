# Evidência operacional — roteamento Laya local

Data: 2026-10-13  
Branch: `feat/sponsoredtokens-local-chat`  
Revisão validada antes deste relatório: `f4d3956688468a398d771b075fcd095ce4fb1de7`

Este relatório contém somente metadados operacionais seguros. Nenhuma chave,
mensagem, resposta gerativa, cabeçalho de autenticação ou corpo upstream foi
registrado.

## Runtime instalado

- Instalação: `%LOCALAPPDATA%\WhiteChronos\SponsoredTokensLocalChat`
- Runtime isolado: `%LOCALAPPDATA%\WhiteChronos\SponsoredTokensRuntimes\laya-0.4.6-py311`
- Python: `3.11.9`
- Laya: `0.4.6`
- Torch: `2.14.1`
- Transformers: `5.19.0`
- Checkpoint carregado: `multilingual`
- Revisão do checkpoint: `7b928d828b7b0e022f929d9bd2e44165aa270148`
- Dispositivo observado: `cpu`
- Listeners observados: `127.0.0.1:8765` e `127.0.0.1:8770`

O serviço Laya foi iniciado por `python -m laya.serve`. Essa forma evita o
launcher absoluto gerado por ambientes virtuais Windows e continua válida após
a ativação atômica do diretório preparado.

## Instalação e estado

O preview abaixo concluiu com código de saída zero e `changed=false`:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -WhatIf -Json
```

O preview informou a versão `laya[serve]==0.4.6`, o runtime versionado, os dois
endereços loopback e as fases `prepare-runtime`, `stage-application`,
`stop-installed`, `activate` e `shortcut`.

A instalação real e o início concluíram com código de saída zero e
`changed=true`:

```powershell
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Install -Json
pwsh -NoProfile -File apps/sponsoredtokens-web/windows/Manage-AutoStart.ps1 -Action Start -Json
```

Estado final observado:

```json
{"installed":true,"running":true,"ready":true,"routerRunning":true,"routerReady":true,"router":"laya","url":"http://127.0.0.1:8765/","task":"WhiteChronos-SponsoredTokens-LocalChat"}
```

## Decisão local e degradação

Uma requisição real e limitada ao endpoint local `/v1/systemone` retornou uma
decisão estruturalmente válida do checkpoint multilíngue. A chamada pela interface
`select_model` produziu:

```text
ROUTING_SEAM=PASS router=laya model=sponsored/openai/gpt-5.1-codex-mini
```

Em seguida, somente o processo Laya cujo executável e linha de comando pertenciam
ao runtime aprovado foi encerrado. Durante a indisponibilidade:

```text
LAYA_STOP=PASS
DEGRADED_ROUTE=PASS router=deterministic model=sponsored/openai/gpt-5.6-luna
CHAT_DURING_DEGRADE=PASS ready=True router=deterministic
```

Após 12 segundos, o supervisor restaurou automaticamente o processo e o estado
voltou a `routerReady=true` e `router=laya`.

## Smoke tests gerativos autorizados

As duas chamadas reais concluíram com código de saída zero e não imprimiram o
texto das respostas:

```text
LIVE_SMOKE=PASS provider=SponsoredTokens model=sponsored/openai/gpt-5.6-luna router=deterministic
LIVE_LAYA_SMOKE=PASS provider=SponsoredTokens model=sponsored/openai/gpt-5.1-codex-mini router=laya
```

Isso comprova que SponsoredTokens permaneceu o único gerador nos dois caminhos.

## Rollback

Antes da migração foram registrados o estado, os hashes SHA-256 da cópia estável
e o destino do atalho, sem valores de ambiente. O backup instalado foi então
testado de forma real:

1. os processos verificados foram parados;
2. `SponsoredTokensLocalChat.backup` foi ativado no mesmo caminho estável;
3. o supervisor foi iniciado;
4. o health check retornou `ready=True` e `router=deterministic`;
5. a revisão atual foi reinstalada;
6. o estado retornou a `installed=true`, `running=true`, `ready=true`,
   `routerReady=true` e `router=laya`;
7. somente diretórios temporários confirmados abaixo de
   `%LOCALAPPDATA%\WhiteChronos` foram removidos.

Resultado: `ROLLBACK_HEALTH=PASS` e revisão atual restaurada.

## Testes automatizados da aplicação

Comando:

```powershell
python -m unittest discover -s apps/sponsoredtokens-web/tests -v
```

Resultado mais recente antes do relatório: `67/67` testes aprovados, zero falhas
e zero erros. Os dois scripts PowerShell também foram analisados pelo parser do
PowerShell sem erro de sintaxe.

Os gates completos do repositório são registrados na etapa final do plano após
este relatório.
