---
name: engenharia-mce-projeto
description: Analisar projetos de automacao, P&IDs, memoriais, narrativas, listas de I/O, alarmes, intertravamentos, HAZOP, LOPA e SRS para construir Matrizes de Causa e Efeito (MCE) rastreaveis. Usar em pedidos de entendimento de sistema, elaboracao por projeto, alteracao de causas e efeitos ou workflow de MCE com aprovacoes humanas e preservacao do Excel mestre.
---
# Engenharia MCE por projeto — workflow executavel

## Fase 1: entendimento, sem modificar matriz
1. Identificar projeto, SS, sistema, revisao, disciplinas e documentos em cada fonte. Nunca inferir ou preencher lacunas. Se necessario, consultar `references/metodo-causa-efeito.md`.
2. Ler as fontes reais e elaborar resumo tecnico com classificacao `DOCUMENTADO`, `INFERIDO_PARA_REVISAO` ou `NAO_DOCUMENTADO`. Exigir evidencia literal e revisao. Utilizar P&ID para topologia e narrativa/SRS/filosofia para logica, sem inferir efeito de um desenho fisico.
3. Executar o workflow local `python scripts/mce_workflow.py init --workspace PROJETO --master MODELO.xlsx --sources FONTES...`. Inventario cria copia mestre imutavel, hashes e contrato conservador.
4. Criar `analise.json` revisado pelo engenheiro e executar `understand`; o relatorio de entendimento e as pendencias sao gerados. **PARAR** em `ANALISADO_AGUARDANDO_DECISAO` e apresentar resultado ao usuario antes de elaborar a matriz.

## Fase 1A: integracao P&ID opcional e auditavel
- Se houver exportacoes JSON/CSV de P&ID, consultar `references/pesquisa-pid-github.md` e usar o adaptador **proprio** `scripts/pid_bridge.py`, que nao instala nenhum upstream e nunca cria MCE automaticamente.
- No pacote principal, orquestrar pelo `scripts/mce_system.py pid-import` antes do entendimento. O arquivo de exportacao deve estar no inventario de fontes do projeto e seu SHA-256 deve coincidir. `compare-io` compara texto literal com lista I/O sem promovê-lo a verdade tecnica.
- Cada derivado exige em `analise.json.pid_integration_review[]`: `output_file`, `output_sha256`, `review_status=REVISADO_COM_RESSALVAS|DESCARTADO`, `reviewer` e `comment`.
- **STOP:** na ausencia de revisao, ou se algum adaptador contradisser documento oficial, nao prosseguir. Referencias GitHub não autorizam copiar código, dados, setpoints ou lógicas de segurança.

## Fase 2: somente com autorizacao expressa
5. Exigir `project` e `ss` documentados e identificacao verificavel da fonte, contrato de modelo aprovado com cabecalho protegido, whitelist explicita, no maximo 50 itens por folha e autorizacao humana `AUTORIZO_ELABORACAO_MCE` correspondente aos hashes dos documentos.
6. Apos esta autorizacao, executar `authorize`, em seguida `apply --changes alteracoes.json`. Cada alteracao tem: aba, coordenada, valor original, novo texto, documento, SHA-256, localizacao, revisao e transcricao comprovavel. Nao preencher sem fonte.
7. Validar logica AND/OR, votacao m/n, setpoints, temporizacoes, reset, estados seguros, bypass, falhas, sequencias e implementacao PLC/SIS/F&G apenas se documentados. Nao transformar alarme em SIF sem requisitos de seguranca.
8. Usar o editor OOXML incorporado, que modifica somente texto autorizado e marcacao cinza, preservando as outras partes e o workbook mestre. Se o preenchimento tiver significado funcional, **STOP**.
9. Rodar `audit`, verificar diff, formula, cabecalho, estilizacao, fontes e QA. Emitir apenas `MCE_PRELIMINAR_PARA_REVISAO` para revisao de Processo, Instrumentacao, Automacao, Operacao e Seguranca quando aplicavel.
10. Nao publicar modelos/arquivos de projeto, instalar integracoes, fazer push/merge ou declarar homologacao Petrobras sem permissao especifica e evidencia.

## Referencias e execucao
- Consultar `references/metodo-causa-efeito.md`; prioridade as fontes contratuais do projeto e normas oficiais de aplicacao comprovada.
- Os scripts de engenharia sao ferramentas deterministas de **controle documental e edicao**, nao substituem o raciocinio de engenharia nem validam automaticamente lógicas de seguranca.
- A skill `padronizacao-mce` rege contrato e inviolabilidade do modelo.


## Perfil derivado P09 L50 — DEC-MCE-034

- Depois de validar o perfil P09 L50 e **somente sobre copia derivada sob gates humanos**, aplicar a politica de alturas da entrada `matriz-causa-efeito`: `20 + 10*(n_linhas_visuais - 1)` pt, de 20 a 400 em passos de 10. N=3 exige 40 pt, N=4 exige 50 pt; nao bloquear automaticamente textos de tres linhas.
- Para o perfil de larguras `P09_L50_20261110`, usar B=25, C=56, F=34 (F:G mesclado). Preservar todas as colunas de efeito I:AQ, titulo girado, print A1:AR50, 46 mesclagens e limite de 43 causas por folha; paginar continuamente a cada linha 50, sem usar as paginas dos desenhos como divisores.
- A rotina de estimar linhas pode sobrecontar/subcontar o Excel; conferir por visualizacao quando disponivel e manter status `QA_VISUAL_WINDOWS=NOT_RUN` caso nao realizado. A Skill nao altera master, nao inventa X, nao chama outro editor nem substitui o gate de `AUTORIZO_ELABORACAO_MCE`.


## DEC-MCE-037 — retorno a borda thin e largura A:AR=2
Revogada a regra `DEC-MCE-036` de aplicar `medium` nas bordas. Preservar `thin` original. Validador P09 L50 com `column_width_profile=P09_L50_ALL_COLUMNS_2` exige `width=2` em todas as colunas A:AR. Por coluna do Excel, a largura nao depende da linha: "somente superior" nao e configuravel. A variante I:AQ=2 com B/C/F legíveis nao substitui a saída A:AR literal. Gates de editor, contrato, whitelist e aprovacao de engenharia seguem obrigatorios para obra operacional.
