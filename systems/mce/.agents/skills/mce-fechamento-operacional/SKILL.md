---
name: mce-fechamento-operacional
description: Auditar evidencias e pendencias do sistema independente de Matriz de Causa e Efeito (MCE) no GitHub, Codex ou ChatGPT Web. Usar quando pedirem comprovar producao, verificar pacote, validar hashes de fontes, modelo mestre, contratacao de celulas, revisoes, aprovacoes, FAT/SAT e aceite final sem alterar o Excel original ou inventar homologacao.
---

# MCE - Fechamento operacional rastreavel

Usar o workflow de engenharia MCE existente, sem depender do REA e sem promover dados sinteticos a evidencia oficial. Esta Skill **coordena evidencias**; nao cria autorizacao humana, nao instala sistema no host e nao faz merge.

## Roteiro

1. Identificar sistema `MCE_INDEPENDENTE` (nunca combinar com REA), projeto, SS, revisao, responsaveis e fonte da documentacao. Se nao houver identificacao comprovada, classificar `NAO_DOCUMENTADO` e parar a liberacao.
2. No GitHub, verificar PR e HEAD SHA atuais, regras de branch, CI, revisoes, artefatos de release e autorizacao de merge. Aplicar GitHub Arena por perspectivas diferentes e o fluxo de testes Superpowers. Nao alterar `main` automaticamente.
3. Executar apenas em codigo aprovado do sistema MCE: `python -m pytest -q systems/mce/tests`, `scripts/release_integrity.py`, e `scripts/production_readiness.py --workspace <workspace_real>`. Registrar os exit codes. Nao preencher/alterar Excel ao fazer essa auditoria.
4. Para conferir um inventario adicional de arquivos: `python scripts/verify_evidence.py --root <diretorio_autorizado> --manifest <evidence.json>` (ver formato em `references/evidencias.md`). `ARTIFACT_INTEGRITY_PASS` comprova somente correspondencia com hashes informados, nunca autenticidade do aprovador.
5. Exigir as condicoes inegociaveis do MCE: modelo mestre XLSX real aprovado, contrato de edicao com whitelist exata, fontes documentais autenticadas, projeto e SS, limite de 50 causas por folha, rastro SHA-256, autorizacao externa identificavel, copia derivada e auditoria OOXML. Nao usar o exemplo da Skill como modelo oficial.
6. Antes de emitir matriz preliminar, respeitar `ANALISADO_AGUARDANDO_DECISAO`, o gate `AUTORIZO_ELABORACAO_MCE` e revisao multidisciplinar. Nunca inferir setpoints, SIF, votacao, tempo ou reset sem evidencia literal.
7. Produzir tabela PASS/BLOCKED/USER_ACTION_REQUIRED/NOT_APPLICABLE por gate com artefato, SHA e link quando disponivel, mantendo `PRODUCTION_COMPLETE=NO` ate integracao no GitHub, ambiente definitivo, revisao e aceite **humanos** externos, FAT/SAT aplicavel e plano de reversao.

## Contrato de seguranca

- Nao usar Desktop Commander como dependencia.
- Nao publicar modelos, desenhos, SRS ou documentos industriais em repositorio publico.
- Nunca sobrescrever o workbook mestre nem alterar cabecalhos, estilos, formulas e vinculos do modelo.
- Este verificador de inventario nao prova autenticidade de aprovacoes. Requer fonte de confianca independente e revisao responsavel.
- Em ChatGPT Web sem executor/host MCE, fazer apenas analise documental; nao fingir que Python ou Codex foram executados.

Consultar `references/evidencias.md` e as Skills complementares `engenharia-mce-projeto` e `padronizacao-mce` antes da conclusao.
