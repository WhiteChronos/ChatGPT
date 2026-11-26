---
name: mce-kopia-backup
description: Planejar, verificar e recuperar backups de documentos e SQLite privado do MCE com Kopia em Windows, usando WhiteChronos/kopia como referência; acionar para snapshots, retenção, recuperação ou operação com interface gráfica, como alternativa ao Restic sob decisão humana.
---

# Kopia — alternativa de backup do DataCenter MCE

## Delimitação
Complementar `matriz-causa-efeito`, sem substituir o arquivamento imutável, SQLite append-only, motor OOXML ou assinatura externa. Usar Kopia como **alternativa** a Restic quando o responsável priorizar Kopia CLI/UI, políticas de snapshot ou gestão de retenção. Não manter duas fontes de verdade do DataCenter.

## Fonte e rastreabilidade
- Fork: https://github.com/WhiteChronos/kopia — `main`.
- Upstream: https://github.com/kopia/kopia — `master`; baseline 2026-11-10 `7498348d3cfb52c6ffd46bd2cdfef42987fcdf11`.
- Licença Apache-2.0. Preservar copyright, notices e proveniência. Promover atualizações somente depois de revisar SHA, diferenças e validações.
- Referência oficial: https://kopia.io/docs/

## Procedimento de operação
1. Consultar PR #118/Issue #120, o contrato DEC-MCE-030 e estado real do host MCE Windows. Sem conexão, `NOT_RUN`.
2. Exigir documento já arquivado com SHA, cópia privada, recibo e banco SQLite MCE existente. Não chamar arquivo presente apenas no ChatGPT de `ARCHIVED_VERIFIED`.
3. Confirmar versão Kopia, backend, criptografia, políticas de retenção, ACL, local redundante **independente** e acesso aprovado; não divulgar chaves e paths privados.
4. Preparar snapshot do vault e do backup lógico consistente do SQLite, sem copiar banco em escrita como prova de consistência.
5. Em Windows e com autorização, executar snapshot/verify e restaurar amostra em destino novo, verificar SHA e `mce_memory.py verify` do SQLite restaurado.
6. Registrar resultado e evidência no DataCenter privado, não no GitHub público. Se a solução Restic já estiver em uso aprovado, não instalar Kopia em paralelo sem decisão de migração e teste de restore.
7. Em falha de armazenamento, ausência de retenção, restore ou cliente não instalado, sinalizar `BACKUP_NOT_VERIFIED`. Nunca afirmar segurança absoluta ou `PRODUCTION_COMPLETE=YES`.

Skill documental/operacional, não instala software, cria credenciais, ativa jobs ou acessa o Windows sem executor autorizado. Não implementar outra base, REA ou serviço de upload público.
