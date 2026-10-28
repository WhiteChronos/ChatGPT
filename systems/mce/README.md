# MCE — Matriz de Causa e Efeito (sistema independente)

Este diretorio documenta o **nucleo publico e reutilizavel** das Skills MCE e o fluxo de edicao controlada. O codigo executavel principal reside em `.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py`. A Skill `padronizacao-mce` define o contrato de preservacao do Excel e oferece inventario somente-leitura.

## Isolamento

MCE nao importa REA, nao requer servidor MCP e nao possui dependencia do codigo de `systems/rea/`. REA e outro produto, com runtime proprio. Analise de P&ID, listas I/O e matriz pertencem somente ao MCE.

## Execucao local

```bash
python -m pip install -r systems/mce/requirements.txt
python .agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py --help
python .agents/skills/padronizacao-mce/scripts/inventariar_modelo.py ARQUIVO_MODELO.xlsx
```

Fluxo: `init` -> `understand` -> **STOP para revisao humana** -> `authorize` -> `apply` -> `audit`.

**Gates obrigatorios:** o XLSX mestre nao e alterado; protecao de cabecalhos, formulas e areas nao autorizadas; limite de 50 causas por folha; evidencia documental e autorizacao humana; sinalizacao cinza apenas nas celulas textuais realmente modificadas. Resultados para revisao multidisciplinar, nunca homologacao automatica.

## Escopo deste PR

Primeiro incremento publico: duas Skills e seu executor de workflow. Os adaptadores P&ID/OCR, o aplicativo de orquestracao e os testes completos existentes no pacote independente de entrega nao foram automaticamente transferidos para este PR. Eles exigem importacao de fonte e validacao de licencas/evidencias antes de nova versao. Nao alegar que este diretorio e a distribuicao integral daquele ZIP.

Nenhum documento confidencial, projeto, SS, modelo Excel nao homologado ou resultado real deve ser commitado neste repositorio publico.
