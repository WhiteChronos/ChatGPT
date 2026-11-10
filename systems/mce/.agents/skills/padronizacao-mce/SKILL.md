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


## Perfil de paginação e altura progressiva P09 L50 — DEC-MCE-034

- Para `P09_L50_APROVADO_VISUALMENTE` nao confundir a linha fisica 50 com 50 causas: 43 posicoes em 8:50; folha seguinte quando a anterior estiver preenchida. A arquitetura com sete folhas nao gera automaticamente sete abas de MCE.
- Cada linha de causa adota `20 + 10*(n-1)` pontos para `n` linhas visuais: 20/30/40/50/60 etc, ate 400; vazio 20. Ler a ocupacao conjunta de B/C/F:G, as larguras e `wrap_text`. A contagem de linhas antes da revisao no Excel e preliminar.
- Para novo perfil de larguras `P09_L50_20261110`: B=25, C=56, F=34, sem tocar G (mesclado), D/E/H, I:AQ ou AR; preservar a geometria de cada aba, bordas, fontes 10/8, mesclagens e numero de causa. Divergencia gera STOP/documentacao, nunca reformatar silenciosamente um mestre oficial.
- A Skill de padronizacao apenas define e verifica contrato; o executor de engenharia continua unico e autoriza edicao apenas apos aprovacao humana. Revisao documental de workbook na conversa nao e homologacao nem prova de backup no DataCenter.


## DEC-MCE-037: largura A:AR=2 e bordas thin originais
A interpretacao `DEC-MCE-036` (borda media) foi REVOGADA. A largura solicitada pelo usuario e de COLUNA Excel=2. Perfil `P09_L50_ALL_COLUMNS_2` exige largura 2.0 em A:AR, 44 colunas em todas as FOLHA N, mantendo integralmente bordas `thin`. Excel nao ajusta largura somente no cabecalho, portanto B/C/F tambem estreitam e podem tornar descricoes ilegíveis. Variante visual alternativa I:AQ width 2 preserva descrições B/C/F; distinguir claramente os dois arquivos. Comparar antes/depois apenas larguras, todos X, mesclagens, fontes, alturas, cabecalhos, area A1:AR50. Sem autorizacao nao editar mestre nem lógica.


## DEC-MCE-038 — Perfil G:AR=2 e separacao de registros sem X
A:MCE P09 L50 com `column_width_profile=P09_L50_G_AR_2`: preservar A:F da copia aprovada, e ajustar G:AR=2 em todas as FOLHA N, bordas thin de origem e 35 efeitos I:AQ. Nenhum equipamento/sinal sem relacao documental pode ser transformado em causa com X inventado. A grade final deve ter ao menos um X associado a efeito nomeado (linha 5) para cada causa preenchida; mover cadastro/supervisao sem efeito demonstrado para pendencias XLSX **externas**, nunca como aba auxiliar. Paginar a cada 43 causas (8:50), repontando X pelo titulo de efeito e preservando integridade, fonte, mesclas e impressao. O contrato opcional `require_effect_per_cause` habilita este gate no validador canonico. Nao editar mestre nem autorizar engenharia tacitamente.
