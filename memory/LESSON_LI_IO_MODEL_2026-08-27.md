# Lição aprendida — Padrão LI de Entradas e Saídas — 2026-08-27

## Ocorrência

Ao usar uma LI existente como referência visual, a quantidade de abas do arquivo-modelo foi copiada para o documento de destino. O destino precisava de quatro folhas, enquanto a referência visual possuía sete. Também foi incluída uma nota explicativa na última folha/mapa de memória e alguns textos receberam estilos incompatíveis.

## Causa

Houve mistura entre três conceitos distintos:

1. padrão visual;
2. conteúdo do documento de destino;
3. quantidade de folhas necessária à emissão.

O modelo visual foi tratado incorretamente como estrutura completa de conteúdo.

## Regra preventiva

- O modelo visual governa somente formato e identidade visual.
- O documento de destino governa conteúdo e quantidade de folhas.
- `sheet_count_source` deve ser `TARGET_DOCUMENT`.
- É proibido copiar a quantidade de abas do modelo.
- Texto inserido deve herdar exatamente o estilo da célula.
- Notas gerais devem permanecer na folha de notas/resumo/referências.
- É proibida nota genérica na última folha/mapa de memória.
- O binário oficial permanece no Data Center privado; o GitHub público recebe apenas manifesto redigido e hashes.

## Caso de regressão

O pipeline deve rejeitar LI E/S quando:

- `template_sheet_count_forced = true`;
- quantidade final divergir do destino ou da paginação declarada;
- `font_signature_match != true`;
- `layout_signature_match != true`;
- existir `ad_hoc_note_on_final_sheet = true`;
- uso + reserva for diferente do total;
- ferramenta externa for auto-instalada sem aprovação.

## Evidência consolidada

- Model ID: `LI_IO_PETROBRAS_AUTOMACAO_V1_0`;
- referência visual: ativo privado registrado por hash;
- instância canônica: ativo privado registrado por hash;
- política de folhas: `TARGET_DOCUMENT_DRIVEN`;
- modo: `BLOCK_ON_ANY_FAILURE`.
