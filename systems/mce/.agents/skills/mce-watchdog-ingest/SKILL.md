---
name: mce-watchdog-ingest
description: Monitorar entradas de documentos no inbox privado Windows do MCE com referência watchdog, respeitando verificação periódica e cópia SHA-256 pelo arquivador existente; acionar em automação de pasta, detecção de novos arquivos, filas de ingestão e reconciliação de eventos.
---

# Watchdog — detecção de novos documentos do MCE

## Delimitação
A Skill auxiliar de `matriz-causa-efeito` **não** transforma eventos de arquivo em prova de backup. O arquivamento permanece exclusivamente com `scripts/mce_document_archive.py` (SHA-256 de origem/destino, recibo, único SQLite, cópia secundária). Watchdog pode acelerar detecção no Windows, mas varredura recorrente e reconciliação são obrigatórias para eventos perdidos.

## Fonte e rastreabilidade
- Fork: https://github.com/WhiteChronos/watchdog — branch `main`.
- Upstream: https://github.com/gorakhargosh/watchdog — branch `master`; baseline 2026-11-10 `8d9cf3d73e89c1421ae39289d1a522c5f5465f07`.
- Licença Apache-2.0 e avisos de terceiros, ver `THIRD_PARTY_LICENSES.md`. Preservar procedência na revisão antes de atualizar o fork.
- Documentação: https://python-watchdog.readthedocs.io/

## Processo recomendado
1. Confirmar root Windows explicitamente autorizado, túnel privado conectado, acesso aos bytes e projeto; não pesquisar outros diretórios ou conversas.
2. Priorizar o modo `scan`/`watch` **já existente** no arquivador MCE; avaliar watchdog apenas quando latência de detecção justificar a dependência extra. Os eventos são apenas gatilhos, não cópia.
3. Se watchdog estiver aprovado/instalado, observar exclusivamente a pasta `inbox` autorizada. Ignorar arquivos temporários, aguardar estabilidade de tamanho e `mtime`, rejeitar links/junctions/hardlinks e verificar integralidade antes do commit.
4. Executar ingestão idempotente pelo motor do MCE; reexecutar reconciliação periódica e no reinício do host, sem sobrescrever revisões. Registrar SHA e recibo do documento e da segunda cópia no SQLite.
5. Testar criação, substituição, gravacão parcial, renomeação, falha de processo, reinício, desconexão do destino, corrupção, reprocessamento e restore do original.
6. Se evento não recebido, host desconectado ou não houver prova de cópia: `COPY_PENDING`, não afirmar upload automático do ChatGPT ou proteção concluída.

Não instalar módulos automaticamente, criar daemon/serviço, ativar política de retenção, abrir porta de rede nem executar código upstream sem aprovação e QA Windows. `PRODUCTION_COMPLETE=NO` até validação live do caminho chat -> inbox -> DataCenter.
