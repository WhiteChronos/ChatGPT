# MCE — DataCenter, memoria persistente e DataSheet

Produto: `MCE_INDEPENDENTE`. Este sistema nunca compartilha banco, script ou dependencia com o outro produto. O GitHub e fonte do codigo e CI; o SQLite **privado e local** e a fonte das anotacoes operacionais do host autorizado.

## Contrato de arquivos

- `datacenter/schema.sql`: esquema SQL com ledger append-only e triggers bloqueando update/delete.
- `scripts/mce_memory.py`: CLI de init, record, verify, datasheet, backup e restore.
- `datacenter/DATA_SHEET.schema.json`: esquema da exportacao DataSheet JSON.
- `scripts/continuity_pipeline.py`: registra o status *read-only* do motor existente, sem automaticamente aprovar nada.
- `tests/test_mce_memory_continuity.py` e `.github/workflows/mce-memory-qa.yml`: teste e scanner focado.

## Inicializacao privada, leitura, backup e restauracao

A pasta `C:\MCE_DADOS` representa um volume real preexistente, criptografado e com permissoes restritas, nao um caminho configurado automaticamente. Nunca enviar banco ou exportacao com dados de projeto/engenharia para GitHub, ChatGPT ou CI. Em um checkout GitHub o verificador bloqueia caminhos em qualquer ponto da raiz do repositorio.

```powershell
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" init
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" record --kind DECISION --subject 'Revisao pendente' --detail '{"approved":false}' --reference 'PR vigente'
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" verify
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" search --text 'Revisao pendente'
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" datasheet --output "C:\MCE_DADOS\mce-datasheet-001.json"
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce.sqlite3" backup --output "D:\MCE_BACKUP\mce-backup-001.sqlite3"
python .\systems\mce\scripts\mce_memory.py --db "C:\MCE_DADOS\mce-restored.sqlite3" restore --backup "D:\MCE_BACKUP\mce-backup-001.sqlite3"
```

Datasheet normal omite payloads. Adicionar `--full` somente para exportacao autorizada e armazenamento seguro. A exportacao, backup e restauracao jamais sobrescrevem o destino. Verificar digest e testar restauracao em outro volume periodicamente.

Pipeline de entendimento (somente leitura): `python .\systems\mce\scripts\continuity_pipeline.py --db "C:\MCE_DADOS\mce.sqlite3" --workspace "C:\MCE_DADOS\PROJETO" --datasheet "C:\MCE_DADOS\mce-run-001.json"`. O retorno 2 significa bloqueio tecnico, nao falha na memoria. Nenhuma celula do Excel mestre e editada. Os gates `ANALISADO_AGUARDANDO_DECISAO`, `AUTORIZO_ELABORACAO_MCE`, revisoes e FAT/SAT permanecem obrigatorios.

## Seguranca, durabilidade e limites de prova

- O hash encadeado e a integridade do SQLite detectam corrupcao e alteracao simples, mas **nao autenticam a identidade** do aprovador. Um administrador privilegiado pode recriar todos os eventos. Ancorar o digest em fonte externa de confianca.
- O filtro de strings sensiveis nao substitui DLP. Nao incluir credenciais, chaves, P&IDs, fontes confidenciais, dados pessoais nem dumps inteiros. O SQLite nao faz criptografia da aplicacao: exigir criptografia de volume e backup, IAM/ACL, politicas de retencao e auditoria do host.
- A permanencia de dados nao e infinita: verificar disco, backups versionados, restauracao periodica e recuperacao de desastres. Nunca afirmar que o ChatGPT memorizou automaticamente o conteudo do banco.
- `PRODUCTION_COMPLETE=NO` ate workflow GitHub no SHA, host real, autorizacoes, revisoes, monitoramento, rollback e aceite por responsaveis. Evidencias sintenticas de CI nao comprovam producao.

## Memoria da ferramenta no DataCenter do MCE

Nao criar banco isolado. O mesmo `mce_memory.py` armazena eventos `STATUS` com `subject=MCE_TOOL_MATRIZ_CAUSA_EFEITO` e `detail.tool=matriz-causa-efeito`. O DataSheet privado esta em `workspace/derived` conforme `datacenter/MATRIZ_CAUSA_EFEITO_DATASHEET.schema.json`. Nao publicar dados industriais no GitHub. Ver `docs/MATRIZ_CAUSA_EFEITO_TOOL.md`.

## Plataforma Windows para a ferramenta

A Skill matriz-causa-efeito e o conjunto de workflows próprios do MCE são exclusivos de Windows com Python 3.12+ e PowerShell. Não usar Linux, WSL ou Bash para desenvolver ou operar esta ferramenta. Banco SQLite e DataSheets operacionais continuam em volume privado Windows, sem criar outra base.
