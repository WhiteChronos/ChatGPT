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


## Ponte read-only de retomada para ChatGPT e Codex (30/10/2026)

`scripts/mce_context_bridge.py`, restrito a Windows nativo, produz somente `mce.context-handoff.v1` com SHA/IDs publicos GitHub e `status`, `event_count`, `head_sha256` e `by_kind` do **mesmo** SQLite quando fornecido explicitamente. Nao cria outro banco nem publica detalhes de eventos, documentos, paths privados ou backups. O script bloqueia DB corrompido e nao sobrescreve arquivos. Ver `docs/RETOMADA_ENTRE_CHATS.md`; nao tomar checkpoint por prova de restore real, autenticação de aprovador ou captura de chats.


## Politica de preservacao de TODOS os documentos do MCE — DEC-MCE-030 (2026-11-10)

**Objetivo:** nenhum documento recebido ou gerado e considerado arquivado antes de comprovacao de copia byte a byte no DataCenter privado Windows. A politica aplica-se a documentos de entrada, originais, PDFs, desenhos, MD/ET, I/O, MCE XLSX, revisoes e saidas derivadas. Envolve somente dados fisicamente acessiveis ao host autorizado; arquivos apenas referenciados em ChatGPT/Drive nao sao capturados por esta documentacao.

**Ciclo de ingestao exigido para implementacao no unico MCE:**

1. **Origem e permissao:** confirmar `MCE_INDEPENDENTE`, projeto/SS quando documentados, fonte autorizada, bytes disponiveis, tipo/tamanho e registro da origem. Nunca buscar arquivos fora do root explicitamente autorizado.
2. **Copia imutavel:** copiar para armazenamento privado preexistente fora do checkout GitHub, em pasta por projeto e identificador de documento, usando caminho temporario seguro, criacao exclusiva e publicacao atomica; nao seguir links simbolicos, junctions ou hardlinks nao autorizados. Preservar exatamente os bytes; jamais sobrescrever original ou revisao existente.
3. **Integridade e versao:** calcular SHA-256 de origem e destino e comparar tamanho; atribuir versao imutavel ligada ao hash e a revisao declarada; manter manifests com ID, nome, tipo, origem, revisao, SHA-256, tamanho, instante de arquivamento e status. Se nome for igual e hash mudar, registrar revisao nova. Conteudo identico nao gera overwrite.
4. **Indexacao:** escrever evento `DOCUMENT_ARCHIVED`/registro equivalente no ledger do **mesmo SQLite MCE**, sem armazenar conteudo do documento no banco. O DataSheet deve registrar apenas metadados autorizados e referencia privada. Conferir integridade do ledger.
5. **Falha fechada:** se os bytes nao estiverem acessiveis ou a copia/hash/indice falhar, registrar `COPY_PENDING` ou `ARCHIVE_BLOCKED` sem afirmar sucesso e impedir que o documento seja considerado fonte preservada. Nao substituir por arquivo em `/mnt/data`, chat ou Github publico. A analise critica dependente do backup deve aguardar reconciliacao.
6. **Retencao/recuperacao:** manter copia redundante em outro volume/dominio de falha, criptografia, ACL, backup versionado, inventario, checagem de hashes e testes de restauracao documentados. Definir calendario e politica de retencao com o responsavel; somente teste real de restore comprova recuperabilidade.
7. **Escopo temporal:** requisitos para arquivos **futuros** quando o fluxo estiver integrado; documentos historicos disponiveis precisam de inventario e migracao aprovada, sem presumir que todos os chats antigos ou anexos ainda existem.

**Recibo minimo de ingestao:** `{project_id, document_id, source_kind, declared_revision, sha256, size_bytes, archived_at, location_ref_private, copy_sha256, status, backup_status, restore_test_reference}`. Nunca colocar caminhos privados, nomes confidenciais ou hashes de documentos industriais em memoria publica do GitHub; o recibo integral permanece somente no DataCenter privado.

**Cenarios obrigatorios para QA Windows:** original legivel/copia igual; upload repetido e idempotente; mesmo nome com bytes diferentes gera nova versao; alteracao durante copia falha; ausencia de host/bytes falha fechada; links/traversal bloqueados; autorizacao de acesso por projeto; backup secundario e restauracao conferidos. Validar fluxo real de anexo ChatGPT -> host antes de anunciar ingestao automatica. Inexistencia de segunda copia/restore impede declarar a promessa de nao perder informacao cumprida.

**Estado na data:** `REQUIREMENT_REGISTERED`; `AUTO_INGEST=NOT_IMPLEMENTED_OR_NOT_VERIFIED`; `PRIVATE_SQLITE_WRITE=NOT_RUN`; `BACKUP_RESTORE=NOT_VERIFIED`. O conector MCE foi descoberto mas seu tunel estava indisponivel. Nao tratar esta secao como comprovacao de copia de qualquer arquivo.


### Candidato executavel de ingestao Windows, ainda nao implantado

\`scripts/mce_document_archive.py\` aceita \`--inbox\` (pasta autorizada preexistente), \`--vault\` (DataCenter privado preexistente), \`--db\` (unico SQLite MCE inicializado), \`--project\`, \`--revision\` e \`--mirror\` (segunda pasta privada preexistente). Comandos:

- \`ingest --filename ARQUIVO --document IDENTIFICADOR\`: original intocado, copia por SHA, recibo imutavel, evento no SQLite, segunda copia quando configurada.
- \`scan --min-age 3\`: reconcilia arquivos ja entregues ao inbox e ignora arquivos temporarios; reaplicar e idempotente.
- \`watch --interval 10 --min-age 3\`: reexecuta reconciliação enquanto o processo estiver ativo; requer operacao/servico no **host real** e nao e inicializado automaticamente pelo ChatGPT.
- \`verify --document DOC --sha SHA\` e \`restore --document DOC --sha SHA --output DESTINO_NOVO\`: verificacao e restauracao de arquivo especifico (nunca sobrescreve).
- Toda saida inclui status e \`production_complete=false\`. \`SECONDARY_COPY_VERIFIED_FAILURE_DOMAIN_UNVERIFIED\` nao prova que a segunda pasta esta em outro disco/host. Um backup robusto deve configurar destino realmente independente e manter snapshots com Restic/Kopia aprovados pelo operador.

**IMPORTANTE:** plugin MCE continua com sete ferramentas de inbox e nao transfere anexos de conversa, e o host/tunel pode estar indisponivel; somente o operador instala/ativa a observacao de inbox em Windows. Rotina criptografada e verificacao offsite com Restic/Kopia dependem de instalacao, credencial, retencao e teste real de restauracao aprovados. O script nao instala ferramentas nem cria volume, nao substitui gates MCE/engenharia.


### Gate de integracao do plugin MCP (candidato)

O servidor \`mce_sdk_server.py\` aceita flags opcionais \`--archive-vault\`, \`--archive-db\` e \`--archive-mirror\`. Elas devem apontar para pastas privadas existentes e o unico SQLite inicializado, fora do checkout, configuradas somente pelo operador no Windows. Sem as tres flags, o servidor ainda permite status e leitura, mas \`initialize\`, \`understand\` e \`apply\` nao devem processar projetos sem copia validada. Ao habilitar, a operacao arquiva origem, contrato, analise e saida preliminar em duas pastas, conferindo SHA. O backup secundario no mesmo disco nao comprova independencia fisica; validar dominio de falha e restore real. Nenhum fluxo captura automaticamente bytes do ChatGPT para o host sem integracao adicional.
