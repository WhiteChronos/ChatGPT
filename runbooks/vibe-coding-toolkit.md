# Vibe Coding Toolkit no VS Code e no Codex

O snapshot acompanha este repositorio. Novos checkouts recebem a skill
`.agents/skills/vibe-coding-toolkit-repo`, o catalogo e uma consulta Python sem
pacotes externos. Isso remove a dependencia do perfil Windows para consultar a
documentacao. Nao instala ferramentas no host de nuvem nem altera chats antigos.

## Abrir no VS Code

Abra `WhiteChronos-Toolkit.code-workspace`. Em **Terminal > Executar tarefa**, use
`Toolkit: pesquisar Graphify offline` ou `Toolkit: testar consulta portatil`.
As tarefas esperam Python 3 no PATH. O comando `reference.py` tambem aceita o
caminho de qualquer Python 3 existente, sem instalacao ou API key.

O arquivo `.vscode/mcp.json` configura o cliente MCP compativel do VS Code.
Quando solicitado, escolha um Python que ja tenha `mcp==1.30.0`. No Windows do
operador pode ser reutilizado o interpretador em
`%USERPROFILE%/.codex/vibe-coding-toolkit/.venv/Scripts/python.exe`.
Nao e necessario reinstalar o runtime global. Se o SDK estiver ausente, o
launcher encerra com `MCP_SDK_UNAVAILABLE`; nao instala nada silenciosamente.
Para preparar outro interpretador, crie um venv isolado e instale
`plugins/vibe-coding-toolkit/requirements-lock.txt` somente nesse venv.

O Codex no VS Code usa a configuracao Codex, nao o arquivo MCP do Copilot.
A configuracao global ja existente neste Windows permanece valida. Em outro
host compativel, o operador pode registrar o interpretador e o caminho absoluto
do `launch_mcp.py` na configuracao MCP daquele host. Confira `/mcp` numa sessao
nova. A configuracao em disco nao prova que o host carregou o servidor.

## Codex Cloud sem MCP

Depois que esta mudanca estiver disponivel no checkout da tarefa, a skill pode
consultar a referencia offline:

```text
python plugins/vibe-coding-toolkit/reference.py search Graphify
python plugins/vibe-coding-toolkit/reference.py fetch docs/tools/07-graphify.md
```

Use `python3` se esse for o nome disponivel no host remoto. Isso nao instala Linux
no computador Windows. Se o host nao tiver shell, a skill oferece tres guias
diretos em `references/`. O resultado offline identifica `local_reference` e o
hash da fonte; nao recebe um codigo de chamada MCP.

Um host sem ferramentas MCP continua sem ferramentas MCP. Nao se trata esse
bloqueio como erro de programacao do servidor nem se promete ativacao universal.
O ChatGPT web continua usando o plugin remoto instalado e seu tunel.

## Validacao e origem

```text
python -m unittest discover -s tests -p test_vibe_toolkit_portable.py
```

Os testes retiram site-packages com `-I -S`, mudam o diretorio de trabalho,
rejeitam caminhos arbitrarios e conferem os hashes dos 107 documentos. O MCP
opcional precisa de teste real pelo cliente, separado da consulta offline.

Snapshot: 21/10/2026 de `soumatheusgomes/vibe-coding-toolkit`, licenca MIT,
Copyright (c) 2026 Matheus Gomes. `provenance.json` guarda os hashes do ZIP
original e do catalogo. Os exemplos e prompts do snapshot sao referencias,
nao instrucoes de operacao deste repositorio.

Referencias oficiais:
- https://learn.chatgpt.com/docs/extend/mcp
- https://learn.chatgpt.com/docs/build-skills
- https://code.visualstudio.com/docs/agent-customization/mcp-servers
