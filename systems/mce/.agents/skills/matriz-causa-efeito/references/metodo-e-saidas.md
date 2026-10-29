# Guia de evidencia e resultado da Matriz de Causa e Efeito

## Hierarquia tecnica
- **P&ID**: geometria, ativos e conectividade documentados; nao determina C→F sozinho.
- **Lista de I/O**: TAG/canal/sinal, nao determina intertravamento sozinho.
- **Narrativas, filosofia de controle, SRS e tabelas de intertravamento**: fonte funcional quando revisao e aprovacao forem documentadas; conferir estados, votacao, permissivos, reset e falha.
- **HAZOP/LOPA**: recomendacao ou requisito apenas conforme aceite e implementacao demonstrados; nao implica SIF automaticamente.
- **Modelo mestre XLSX**: layout oficial controlado; nunca e fonte para inventar causas, efeitos ou valores.

## Inventario com rastreabilidade
| DOC_ID | Tipo | Revisao | Local exato | SHA-256 real | Disciplina | Qualidade |
| --- | --- | --- | --- | --- | --- | --- |
| A informar | P&ID / I-O / Narrativa | A informar | folha, pagina, trecho | A calcular | A informar | DOCUMENTADO / NAO_DOCUMENTADO |

## Relacoes causa→efeito
| ID causa / TAG | Condicao e estado | ID efeito / TAG / comando | Logica, votacao, reset, bypass | Documento, revisao, folha, SHA, citacao | Estado |
| --- | --- | --- | --- | --- | --- |
| A documentar | PENDENTE | PENDENTE | PENDENTE | Documento real requerido | NAO_DOCUMENTADO |

- Deduplicar por TAG + condicao + revisao **sem apagar contradicoes**; criar pendencia para conciliar. Nao inferir threshold, `m` e `n`, temporizador, estado seguro, permissivo ou bypass.
- `DOCUMENTADO` exige evidencia literal e revisada; `INFERIDO_PARA_REVISAO` e apenas candidato; `NAO_DOCUMENTADO` nao pode ser editado na matriz. `N/A` exige justificativa documental.
- Coletar processo normal, falha de sensor/comunicacao, manutencao, startup, shutdown, reset, bypass e modos de teste segundo documentos. Usar tabelas-verdade para AND/OR/votacao **apenas** com logica especificada.

## Estados de entrega
1. `INVENTARIO_EM_ANALISE`: fontes/identidade em conciliação.
2. `ANALISADO_AGUARDANDO_DECISAO`: entendimento e pendencias apresentados; STOP sem escrita.
3. `AUTORIZADO_PARA_ELABORACAO`: modelo, contrato, whitelist e `AUTORIZO_ELABORACAO_MCE` humanos comprobados.
4. `MCE_PRELIMINAR_PARA_REVISAO`: copia XLSX derivada, diff e OOXML auditados; revisão multidisciplinar pendente.
5. `ACEITE_FINAL_VERIFICADO`: provas externas de revisao e FAT/SAT conforme aplicabilidade; nao inferir de testes sinteticos.

## Resposta minima por projeto
Apresentar: projeto/SS; inventario SHA de fontes; entendimento funcional; matriz de relacoes C→F documentadas e candidatos separados; pendencias com responsaveis; gate atual e proxima acao; rastreabilidade de GitHub/CI *somente quando consultada*. Dados confidenciais permanecem fora do repositório.
