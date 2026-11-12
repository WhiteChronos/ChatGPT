# MCE — contrato de retomada verificavel entre conversas

**Escopo:** somente `MCE_INDEPENDENTE`. Esta pagina descreve metadados de continuidade PUBLICAVEIS, nao documentos industriais, nem armazenamento operacional instalado. Versao de registro: 2026-11-11.

## Fontes de verdade e prioridade

1. Conferir o repositorio `WhiteChronos/ChatGPT`, os HEADs e status atuais das PRs MCE (historico #118/#126/#129/#130, sem presumir merge), as verificacoes GitHub Actions, `systems/mce/AGENTS.md` e `systems/mce/spec/memoria.md`.
2. Ler `systems/mce/docs/RETOMADA_ENTRE_CHATS.md`, `systems/mce/docs/DATACENTER_MEMORY.md`, `systems/mce/datacenter/CHAT_CONTINUITY_CONTRACT.json`, e os eventos do Issue #120. Se o indice `WhiteChronos/document-evaluation-system/system-memory/index.json` estiver apenas em PR, usar o ref/HEAD real e identificar que `main` pode nao conter a versao.
3. Validar a identidade de cada anexo privado por nome/documento/revisao, bytes, tamanho e SHA-256. Nao equiparar lembranca de conversa ou comentario GitHub ao arquivo real.
4. A ultima dupla de referencia informada e: **XLSX MCE PV 03** e **DOCX questionario PV 04**, como sequencias independentes. Os dois arquivos foram lidos em conversa autorizada, porem **nao houve prova de ingestao no cofre privado**. Numa nova conversa, buscar bytes pelo canal privado autorizado; se ausentes, pedir apenas o arquivo faltante e declarar `BYTES_NOT_AVAILABLE`. Nao rebaixar para PV 02 nem avancar numeracao sem mudanca e verificacao.
5. Conferir o questionario PV 04 contra o XLSX PV 03 em modo somente leitura, por folha, celula, pergunta e status. Preservar todas as perguntas e itens historicos; classificacoes: `DOCUMENTADO`, `PENDENTE_FONTE`, `PENDENTE_DECISAO_ENGENHARIA` ou `NAO_APLICAVEL_JUSTIFICADO`. Nao preencher X por contagem, copia ou inferencia.
6. Se houver fontes MD/ET/P&ID/I/O revisadas, confrontar TAG, sinal, causa, efeito, circuito, revisao e evidencia especifica. Conflitos permanecem pendentes ate engenharia decidir. Identificar SP, H da P09 L50, observacoes, bordas, mesclagens, formulas e areas de impressao sem alterar o mestre.
7. Qualquer emissao requer baseline autentico, copia derivada, identidade fisica separada (inclusive hardlinks), contrato `editable_cells`, `AUTORIZO_ELABORACAO_MCE` vinculada a hashes, QA OOXML/Excel Windows, revisao multidisciplinar e entrega real P09; se faltar, `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`. Word de perguntas e auxiliar, nunca prova de liberacao de X.
8. Mudancas no software: implementador, **agente revisor independente real**, testes Windows, CI no HEAD exato, registro de memoria no mesmo commit, PR em draft ate aprovacao; nao aceitar personas como agentes, nem fazer merge/deploy sem autorizacao especifica.

## Camadas de continuidade e estados

- **Memoria versionada publica:** regras, IDs e links em GitHub; nenhuma copia de XLSX, DOCX, pagina, TAG, pergunta, matriz de cruzamentos, SHA privado ou nome de arquivo industrial.
- **DataCenter:** o arquivo `CHAT_CONTINUITY_CONTRACT.json` e uma politica declarativa PUBLICA. Nao e SQLite, backup ou cofre. O DataCenter Windows local MCE **nao existe** no estado informado. Destino futuro = cofre privado GitHub-only aprovado, com recibos reais de ingestao, versionamento, SHA e restauracao.
- **Manifesto privado (quando houver ingestao autorizada):** guardar `project_id`, `document_identity`, `revision`, `artifact_kind`, `pv_number`, `sha256`, `bytes`, `vault_object_ref`, `ingest_receipt`, `restore_receipt`, `engineering_approval_ref`, `updated_at` e `pending_questions_ref`; separado do repo publico e sem overwrites.
- **Recuperacao em chat novo:** nunca afirmar anexos automaticamente recuperados. Citar status distinto de checkpoint, bytes, restore e engenharia. Se somente metadados existem, continuar com entendimento/pendencias read-only, nao com uma matriz inventada.

## Checkpoint sanitarizado (nao e copia documental)

- Referencias de trabalho: MCE XLSX PV 03; questionario DOCX PV 04.
- Correspondencia: ultima fase foi confrontar perguntas consolidadas com folhas, causas e X historicos antes de resolver discrepancias por documentos e circuito.
- Historico de correcao de software: PR #130 contem mitigacao hardlink testada e revisada; e dependente da #129, sem merge comprovado nesta data.
- `PRIVATE_VAULT_DOCUMENTS_STORED=NO`, `INDUSTRIAL_RESTORE_VERIFIED=NO`, `ENGINEERING_ACCEPTANCE=NO`, `PRODUCTION_COMPLETE=NO`.
