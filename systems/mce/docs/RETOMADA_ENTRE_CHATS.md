# MCE — retomada entre conversas, memoria GitHub e DataCenter privado

Produto unico: **MCE_INDEPENDENTE**. Uma Skill orquestradora `matriz-causa-efeito` e as Skills de suporte recuperam decisoes verificaveis; nao existe um segundo sistema, outro banco ou captura invisivel do historico de chats.

## Fonte permanente — onde buscar primeiro

1. **GitHub**: confirmar o HEAD atual, estado, CI, revisoes e regras do [PR #118](https://github.com/WhiteChronos/ChatGPT/pull/118). Nunca assumir que o SHA citado num chat antigo ainda e atual.
2. **Memoria versionada**: ler `systems/mce/spec/memoria.md` (decisoes, pendencias, evidencias e historico) e `systems/mce/AGENTS.md`.
3. **Issue #120**: ler TODOS os comentarios estruturados `WC_MEMORY_EVENT_V1` do [Issue #120](https://github.com/WhiteChronos/ChatGPT/issues/120), inclusive os ainda `ISSUE_ONLY_PENDING_MIRROR`. Comparar identidade e conteudo; igualdade de ID isolada nao prova equivalencia semantica.
4. **DataCenter SQLite privado**: o banco MCE e seus backups ficam no host Windows; nao ficam automaticamente disponiveis no ChatGPT Web. Verificar integridade, digest e contagens somente com acesso autorizado.
5. **Dados de engenharia**: modelo XLSX mestre, documentos, SS, TAG, I/O, revisoes, SHA e autorizacoes permanecem privados. Ausencias: `NAO_DOCUMENTADO` ou `PENDENTE`; nao reconstruir por inferencia.

## Frase de retomada no proximo chat

**retomar MCE** — trabalhar exclusivamente em MCE_INDEPENDENTE, ler PR #118, Issue #120, `systems/mce/spec/memoria.md` e este documento; comparar HEAD, CI, requisitos vigentes, IDs, revisoes e pendencias. Nunca usar Linux, inferir intertravamento ou alterar o Excel mestre sem autorizacao.

A nova conversa deve consultar o GitHub por conector autorizado. Sem esse acesso, usar checkpoint sanitizado fornecido pelo operador, declarar HEAD remoto NAO_VERIFICADO e nao inventar continuidade. Skill instalada no ChatGPT Web pode estar desatualizada; comparar com GitHub.

## Checkpoint em Windows conectado ao DataCenter

No checkout MCE, em **Windows nativo / PowerShell / Python 3.12+**, o script read-only produz `mce.context-handoff.v1` com referencia GitHub, SHA-256 da memoria publica, IDs de DEC/PEND e, opcionalmente, integridade e contagens de eventos do SQLite. Nao devolve transcricoes, payloads privados, nomes de arquivos operacionais ou dados industriais.

```powershell
python .\systems\mce\scripts\mce_context_bridge.py
python .\systems\mce\scripts\mce_context_bridge.py --db "C:\MCE_DADOS\mce.sqlite3" --output "C:\MCE_DADOS\MCE_CONTEXT_001.json"
```

Pastas e banco sao exemplos de armazenamento externo privado **preexistente**; nunca sao criados automaticamente. Checkpoints existentes nao sao sobrescritos. Sem `--db`, retorna `PUBLIC_CONTEXT_ONLY` com `PRIVATE_NOT_CONNECTED`; com SQLite verificado, `CONTEXT_READY` e `INTEGRITY_PASS`. Falhas retornam `BLOCKED`. O SHA do checkout local nao comprova HEAD remoto: `remote_head_verified=false` ate confirmacao pelo conector GitHub. O checkpoint e indice de fontes, **nao** copia do chat nem validacao de aprovacao.

Nao enviar checkpoint ao ChatGPT caso politica de dados proiba compartilhar metadados; usar apenas o GitHub publico nesse caso. O banco privado e consultavel pelo MCP do MCE **somente quando realmente conectado e autorizado**, com controles do host e revisao independente.

## Evolucao controlada por evento

- Decisao publicavel nova: evento estruturado no Issue #120 pelo conector autorizado, com URL/ID verificados. Sem duplicar evento.
- Mudanca tecnica MCE: acrescentar registro datado ao `spec/memoria.md` **no mesmo commit**, sem reescrever historico; CI Windows `mce-github-memory.yml` audita cada commit. A memoria GitHub nao e coletor automatico de conversas.
- Evento operacional: usar o **unico SQLite** `mce_memory.py` com status/evidencia no Windows privado, DataSheet, backup/restauracao e verificacao SHA. Nao replicar banco no GitHub.
- Nova conversa: dizer `retomar MCE`; verificar as fontes e apontar explicitamente o que falta. Erros e feedback comprovados podem gerar melhorias via PR, CI, revisao e autorizacao. Sem autoexecucao em segundo plano, aprendizagem dos pesos ou instalacao automatica de Skill.

## Conflito real ja identificado em 30/10/2026

`PEND-MCE-014` tem **significados diferentes**: no `spec/memoria.md` refere-se a conexao MCP privada e aprovacao externa; no Issue #120, comentario https://github.com/WhiteChronos/ChatGPT/issues/120#issuecomment-6512633004, refere-se a instalacao da Skill no ChatGPT Web/Codex. **CONFLITO_DE_IDENTIDADE: conciliacao humana pendente**. Preservar ambos; nunca equiparar nem apagar. `github_memory_inbox.py` verifica correspondencia por ID, nao igualdade semantica.

## Gates de seguranca

Sem modelo XLSX mestre homologado, SS e fontes revisadas, contrato `editable_cells`, autorizacao `AUTORIZO_ELABORACAO_MCE`, manter `ANALISADO_AGUARDANDO_DECISAO` e `PRODUCTION_COMPLETE=NO`. Os repositorios Azure, Houston e Industrial-Control sao referencias auxiliares, nao fontes de comando de seguranca. Nao usar Linux/WSL, nao publicar documentos nem credenciais, nao fazer merge/deploy sem aceite separado.
