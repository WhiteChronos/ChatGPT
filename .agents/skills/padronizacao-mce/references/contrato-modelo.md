# Contrato do modelo MCE

Conservar baseline por SHA-256. `model_approved` deve ser `false` ate a verificacao do modelo mestre; inventario do workspace deve registrar `MODELO_APROVADO` somente por identificacao expressa do usuario.

`contract.json` minimo (exemplo ilustrativo, nao copiar cegamente):

```json
{
  "template_sha256": "HASH_REAL_DO_MODELO",
  "model_approved": false,
  "max_causes_per_sheet": 50,
  "matrix_ranges": [{"sheet": "MCE", "first_data_row": 5, "last_data_row": 34}],
  "protected_rows_by_sheet": {
    "CONTROLE": [[1,27]],
    "CAUSAS": [[1,1]],
    "EFEITOS": [[1,1]],
    "MCE": [[1,4]],
    "PENDENCIAS": [[1,1]],
    "REFERENCIAS": [[1,1]]
  },
  "frozen_sheets": ["CONTROLE", "PENDENCIAS", "REFERENCIAS"],
  "editable_cells": {"CAUSAS": ["C2"], "MCE": ["E5"]}
}
```

O exemplo corresponde apenas a um layout ilustrativo; no modelo oficial, todos os intervalos e campos devem ser auditados e aprovados. `editable_cells` e a lista exata de celulas em que ha autorizacao de mudar **texto**, nunca uma faixa implicita. O editor bloqueia formulas, células de cabecalho e fundo funcional. O gray `D9D9D9` fica restrito a valores realmente diferentes.

Nao existe inferencia de TAG, causa, setpoint, acao, prioridade, votacao ou reset a partir da planilha modelo ou apenas do P&ID. Limite 50 aplica-se a numero de causas por folha; verificar capacidade fisica e paginação.
