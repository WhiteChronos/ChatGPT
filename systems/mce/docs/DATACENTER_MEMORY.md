> **Estado real verificado em 2026-11-10:** NAO EXISTE DATACENTER WINDOWS LOCAL DO MCE. Os caminhos `C:\\MCE_DADOS`, SQLite, vault, mirror e MCP descritos nesta pagina representam um **contrato de software nao implantado**, nao infraestrutura descoberta. Nao pedir para ligar um servidor inexistente nem interpretar erro de tunnel-client como prova de sua existencia. O usuario escolheu estudar operacao GitHub-only; o plano e os gates estao em [GITHUB_ONLY_STORAGE.md](GITHUB_ONLY_STORAGE.md). Ate a migracao aprovada/implementada, as interfaces atuais sao legado de desenvolvimento com testes sinteticos; `CLOUD_VAULT=NOT_VERIFIED`, `DOCUMENT_RESTORE=NOT_VERIFIED`, `PRODUCTION_COMPLETE=NO`.

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


### Skills auxiliares versionadas para o backup MCE

As tres Skills `mce-restic-backup` (https://github.com/WhiteChronos/restic, `main`), `mce-kopia-backup` (https://github.com/WhiteChronos/kopia, `main`) e `mce-watchdog-ingest` (https://github.com/WhiteChronos/watchdog, `main`) orientam recursos de backup/restauracao e deteccao, permanecendo subordinadas a `matriz-causa-efeito` e ao mesmo DataCenter/SQLite. As bibliotecas upstream usam branch `master` e necessitam de revisao para cada sincronizacao; nao fazer merge automatico. A introducao de Skill nao comprova instalacao de ferramenta, ativacao do host ou copia de documentos no DataCenter.


### Recuperacao deterministica por inventario (DEC-MCE-043, candidato)

O comando Windows `catalog` fornece uma lista **privada** de versoes realmente arquivadas, por projeto, a partir de recibos imutaveis, objetos SHA-256, evento correspondente no unico SQLite e, quando `--mirror` e informado, integridade da segunda copia. Nao consulta nem copia conversas do ChatGPT. Nao cria recibos, eventos ou arquivos; em corrupcao retorna `ARCHIVE_BLOCKED`. `CATALOG_EMPTY` significa que nao foram encontrados recibos naquele projeto, nao que o chat ou outro computador nao possuam o arquivo.

Executar somente em host Windows nativo autorizado, com pastas e SQLite existentes, sem transmitir a saida do catalogo a repositorios publicos:

```powershell
py -3.12 .\systems\mce\scripts\mce_document_archive.py --inbox "C:\MCE_DADOS\inbox" --vault "C:\MCE_DADOS\vault" --db "C:\MCE_DADOS\mce.sqlite3" --project "ADM_GAMBOA" --revision "AS_RECEIVED" --mirror "D:\MCE_BACKUP\mce-vault" catalog
```

Usar a versao `document/revision/sha256` recuperada do catalogo para `verify` e `restore --output` a **destino novo**; conferir hash antes de usá-la. O mesmo SHA registrado no Issue #120 somente pode ser restaurado se os bytes correspondentes estiverem no vault privado e o recibo/ledger forem validos. Para arquivo ainda nao arquivado, operador deve transferir explicitamente bytes ao inbox autorizado e realizar `ingest` com espelho; anexo no ChatGPT nao chega ao Windows por esta implementacao. Arquivo sem recibo verificado continua `COPY_PENDING`. Um mirror no mesmo dominio de falha nao assegura backup independente; restore de desastre continua gate humano.

Este comando e implementacao candidata para CI Windows, nao prova `HOST_DISCOVERED`, `LIVE_VERIFIED`, backup offsite, transferencia automatica de anexo ou homologacao da MCE. A abertura do Issue #125 rastreia esses gates.


### Restaurar documento apos perda da copia primaria (DEC-MCE-045)

No Windows autorizado, com arquivos e banco SQLite MCE existentes, o operador pode executar `restore-secondary` para restaurar uma nova copia a partir do espelho verificado. O comando requer `--mirror`, projeto/documento/revisao, hash SHA-256, recibo correspondente e eventos `DOCUMENT_ARCHIVED` + `DOCUMENT_BACKUP_VERIFIED` ja persistidos. Se a origem primaria tiver sido apagada, o espelho pode ser usado sem recriar o vault primario. Nunca sobrescreve destino, nao escreve no SQLite e nao modifica o mestre.

```powershell
py -3.12 .\systems\mce\scripts\mce_document_archive.py --inbox "C:\MCE_DADOS\inbox" --vault "C:\MCE_DADOS\vault" --db "C:\MCE_DADOS\mce.sqlite3" --project "ADM_GAMBOA" --revision "AS_RECEIVED" --mirror "D:\MCE_BACKUP\mce-vault" restore-secondary --document "MCE" --sha "SHA256_DO_RECIBO" --output "C:\MCE_DADOS\recuperados\matriz-restaurada.xlsx"
```

A pasta pai do destino deve existir e o arquivo ainda nao pode existir. Se o unico SQLite tambem se perder, recuperar primeiro sua copia autenticada pelo `mce_memory.py restore` para destino novo e verificar integridade. O sucesso de testes sinteticos nao certifica independencia fisica do backup, disponibilidade de anexos de chats nem funcionamento do host MCE. O teste de desastre exige apagar somente copia sintetica isolada e comparar hash apos restauracao; nao apagar dados reais para testar.


## DEC-MCE-078 — PV no DataCenter MCE (esquema, NAO implantacao)

Cada documento preliminar recebe versao imutavel PV 01/PV 02/... gerada pelo mce_pv_controller.py. O ledger privado pv/pv_versions.jsonl armazena metadata append-only (sha256 de entrada e arquivo, prev_digest, digest, timestamp, document_name e numero) conforme datacenter/PV_VERSION_MANIFEST.schema.json. Arquivos de engenharia jamais sao gravados no repositorio PUBLICO e nao sao dados de exemplo de CI.

Quando o DataCenter MCE real estiver disponivel em ambiente PRIVADO autorizado, registrar a versao na tabela existente memory_events com kind=NOTE ou STATUS, subject=MCE_PV_VERSION e detail_json contendo APENAS referencias privadas e metadados consentidos; nao criar segundo SQLite ou inserir sem host. Antes de declarar persistencia: reler bytes/manifest, restaurar em ambiente independente, verificar SHA. Atualmente NAO EXISTE DATACENTER WINDOWS LOCAL MCE; GitHub-only vault permanece condicionado a gates do cofre privado. O resultado de CI nao prova arquivamento, restore ou rotina autonoma.

Aprendizado continuo: armazenar eventos da licao e teste validado no mesmo ledger MCE quando acesso for comprovado, e registrar no memoria.md somente a decisao sanitizada. Sem autoaprovacao, alteracao de pesos, alteracao de excel ou execucao entre chats sem acionamento.
