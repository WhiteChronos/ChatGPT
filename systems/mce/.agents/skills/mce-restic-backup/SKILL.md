---
name: mce-restic-backup
description: Orientar snapshots criptografados, verificação e recuperação do DataCenter privado do MCE em Windows, utilizando fork WhiteChronos/restic; acionar quando for solicitado backup confiável, restauração ou teste de retenção. Atua como auxiliar da Skill matriz-causa-efeito, nunca instala ou executa sem host e autorização.
---

# Restic — backups e recuperação do DataCenter MCE

## Delimitação
Usar como **Skill auxiliar** da `matriz-causa-efeito`, sem criar outro banco, editor ou mecanismo de autorização. Arquivar documentos com `mce_document_archive.py` e ledger no único `mce_memory.py`. **Restic entra depois do arquivamento SHA**, para snapshots cifrados e retenção independente. Não substituir o original nem alterar células da MCE.

## Fonte e rastreabilidade
- Fork WhiteChronos: https://github.com/WhiteChronos/restic — branch-padrão `main`.
- Upstream oficial: https://github.com/restic/restic — branch `master`; baseline verificada em 2026-11-10: `c734245fd3ae9bcac8ab3aaafb4482d4b5d0ae92`.
- Licença upstream BSD-2-Clause. Fork não é código modificado ou auditado automaticamente. Atualizações `master` -> `main` exigem revisão de SHA, licenças, diferenças e CI; não fazer merge automático.
- Documentação: https://restic.readthedocs.io/ e https://restic.net/

## Procedimento condicionado a autorização
1. Conferir GitHub PR #118, Issue #120 (DEC-MCE-030), Skill principal e conexão do host Windows. Sem host real, responder `NOT_RUN`.
2. Validar projeto, fonte do backup, `ARCHIVED_VERIFIED`, SHA, manifest e evento no SQLite MCE privado; não assumir que anexos de chat foram transferidos.
3. Consultar a versão exata e documentação oficial de Restic antes de propor comandos. Verificar armazenamento **externo ao mesmo domínio de falha**, credenciais fornecidas **fora do chat**, volume criptografado/ACL e política de retenção aprovada.
4. Preparar plano para snapshot do vault documental e do backup transacional consistente de SQLite produzido por `mce_memory.py backup`; **nunca copiar SQLite aberto como se fosse backup consistente**.
5. Executar `backup`, `snapshots`, `check` e restauração amostral **somente no Windows autorizado e com aprovação**. Separar verificação estrutural do teste de recuperar documento e índice; comparar SHA-256 e integridade do banco restaurado.
6. Registrar recibos e evidência **somente** no DataCenter privado; GitHub recebe apenas decisão sanitizada e status. Alertar para WORM/imutabilidade e retenção fora do mesmo usuário/dispositivo como controles adicionais.
7. Se cliente indisponível, chave ausente, snapshot incompleto ou restore não testado: `BACKUP_NOT_VERIFIED`, `PRODUCTION_COMPLETE=NO`.

Restic e Kopia são **alternativas de mecanismo de backup**, não dois bancos nem duas dependências obrigatórias. Não executar simultaneamente sobre o mesmo repositório ou deduzir que CI demonstra produção. Operação Windows nativo/PowerShell, sem Linux/WSL/Bash.
