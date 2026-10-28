---
name: padronizacao-mce
description: Controlar e preservar rigorosamente o modelo Excel mestre da Matriz de Causa e Efeito (MCE), inclusive estilos, cabecalhos, formulas, legendas e limite de 50 itens de causa por folha. Usar em qualquer projeto que precise inventariar, validar, proteger ou reutilizar um modelo de MCE ou conferir modificacoes textuais com identificacao cinza apenas nas celulas autorizadas.
---
# Padronizacao MCE — contrato imutavel do modelo Excel

1. **Nunca alterar o arquivo original**. Inventariar o XLSX por SHA-256, abas, conteudo, estilos, formulas, mesclas, imagens, protecoes, configuracao de impressao, ranges e relacionamentos OOXML.
2. Ler `references/contrato-modelo.md` antes de qualquer liberacao. Exemplos de Excel sao distribuicoes locais separadas e **nao homologadas**; nao existe modelo oficial publicado neste repositorio.
3. Definir no `contract.json` as abas congeladas, todas as faixas de cabecalho protegidas (`protected_rows_by_sheet`), os intervalos de causas por folha (`matrix_ranges`) e a whitelist precisa (`editable_cells`). Exigir revisao humana do contrato e declaracao `model_approved=true` com inventario `MODELO_APROVADO`. Nunca liberar todos os campos automaticamente.
4. `max_causes_per_sheet=50` e obrigatorio; se a area real for menor, respeitar o limite fisico. Caso haja necessidade de novas folhas, nao clonar/alterar sem autorizacao e validacao do modelo.
5. O cabecalho, logotipos, numeros de documento, projeto e SS no cabecalho, revisoes, legendas e rodapes continuam inalterados. Divergencias sao registradas como pendencias externas ao XLSX.
6. Editar **somente texto efetivamente autorizado e documentado**, em copia derivada, usando o executor conservador da skill `engenharia-mce-projeto`: `scripts/mce_workflow.py`. O executor altera XML de celula e cria estilo cinza `D9D9D9`, preservando bytes das demais partes do pacote XLSX.
7. Celula com fundo funcional diferente de branco/sem preenchimento deve **bloquear** o procedimento, evitando a perda de semantica do modelo. Nunca pintar uma celula nao editada.
8. Auditoria obrigatoria: hash da fonte intacto; lista exata de celulas alteradas; nenhuma outra propriedade alterada; formulas, mesclas e cabecalho preservados; demais partes OOXML intocadas; compare artefatos e logs. Estado final **PRELIMINAR PARA REVISAO** ate aceite multidisciplinar.
9. `scripts/inventariar_modelo.py` gera inventario sem escrita para apoiar a aprovacao do contrato.

## Dependencias e limitações
- A skill `engenharia-mce-projeto` implementa a orquestracao e o gate humano; esta skill define o contrato, nao inventa logica.
- Editor automatizado suporta **somente `.xlsx`** atualmente. XLSM e planilhas com recursos incompatíveis exigem fluxo especial e nao devem ser convertidos silenciosamente.
- O workflow local nao implica instalacao automatica no catalogo de Skills do ChatGPT nem ativacao remota.
