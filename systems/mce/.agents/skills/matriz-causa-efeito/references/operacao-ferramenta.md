# Operação da ferramenta de MCE e seus três adaptadores

Use a implementação do repositório WhiteChronos/ChatGPT, PR #118. O pacote Skill descreve o fluxo; não contém editor Excel ou banco independente.

## Entradas verificáveis

- Modelo `.xlsx` fornecido pelo responsável: classificação inicial `MODELO_FORNECIDO_NAO_VERIFICADO`, sem alteração e sem aprovação implícita.
- P&ID, OCR ou exportações JSON/CSV fornecidas pela engenharia e incluídas no inventário SHA-256.
- Modelo do manifesto `mce.matriz-tool.manifest.v1`: `run_id` novo, `sources[]` com `adapter` em `azure|houston|industrial`, `source_name`, `document`, `revision`, `location`, e `io_source_name` ou `null`.
- SQLite de memória já inicializado e mantido fora do checkout GitHub.

## Três repositórios (formatos, não motores executados)

- `Azure-Samples/digitization-of-piping-and-instrument-diagrams`: JSON `assets[].connections[]`, topologia potencial **não validada**.
- `S-Houston/digitised-pid-mlops`: CSV `filename,consolidated_text`, somente OCR não aprovado.
- `ZzzJjt/Industrial-Control`: JSON didático `causes/effects/interlock_matrix`, **nunca** fonte de SIF ou trip do projeto. Licença não identificada na pesquisa anterior.

O adaptador local existente `pid_bridge.py` processa formatos entregues pelo usuário em host autorizado. Não executa o código desses repositórios nem envia documentação à nuvem. Se um adaptador não for informado, ele aparecerá como `missing_adapters` no DataSheet, não como integração executada.

## Saídas e STOP

O script `systems/mce/scripts/matriz_causa_efeito_tool.py` produz derivados privados em `workspace/derived`, arquivo `MCE_<run_id>_DATASHEET.json` e evento `STATUS` com `tool=matriz-causa-efeito` no SQLite compartilhado do MCE. Não gera nem altera planilhas. Dados de origem continuam sob controle de acesso no host.

A etapa permanece `INVENTARIADO` no estado canônico do workflow até o responsável revisar as integrações e executar `mce_workflow.py understand`; então para em `ANALISADO_AGUARDANDO_DECISAO`. Revisões, contrato de células, homologação do modelo, autorização `AUTORIZO_ELABORACAO_MCE` e FAT/SAT quando aplicável são requisitos separados.

Em nova conversa, ler GitHub Issue #120, `systems/mce/spec/memoria.md`, `systems/mce/AGENTS.md` e checks atuais do PR #118. A Skill não sincroniza conversas automaticamente.