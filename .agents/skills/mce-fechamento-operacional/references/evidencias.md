# Evidencias de fechamento MCE

## Manifesto opcional de arquivos

```json
{
  "product": "MCE_INDEPENDENTE",
  "files": [
    {"path": "documentos/narrativa_aprovada.pdf", "sha256": "<SHA256_REAL_64_HEX>"},
    {"path": "modelo/planilha_oficial.xlsx", "sha256": "<SHA256_REAL_64_HEX>"}
  ]
}
```

Substituir os marcadores por hashes reais obtidos de fontes independentes e autenticadas. Nunca colocar documentos confidenciais neste arquivo de Skill. O script apenas confere bytes e nao confirma o estado de aprovacao.

## Matriz de fechamento

| Gate | Prova requerida | Estado sem prova |
| --- | --- | --- |
| GitHub | PR revisado, commit em main, CI no SHA e artefato versionado | BLOCKED |
| Ambiente real | Runtime e dependencias validados no host autorizado | BLOCKED |
| Modelo | XLSX oficial aprovado, SHA, contrato de celulas e limite <=50 | BLOCKED |
| Projeto | Identificacao de projeto/SS em fontes com revisao | BLOCKED |
| Autorizacao | Aprovador e registro externo verificado | BLOCKED |
| Entrega | Derivado com auditoria OOXML e copia mestre intacta | BLOCKED |
| Engenharia | Pareceres de disciplinas e FAT/SAT quando exigidos | BLOCKED |
| Operacao | Aceite formal, restauracao/rollback e evidencia do host | BLOCKED |

Nunca promover PASS tecnico a producao integral sem todos os gates. Reportar bloqueios com o dono da acao, nao inventar um percentual de progresso.
