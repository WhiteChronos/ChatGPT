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


## DEC-MCE-039 — integridade física OOXML de largura G:AR
Em `column_width_profile=P09_L50_G_AR_2`, cada G..AR deve ter `width=2.0`, `min=max=indice_da_coluna` e nenhuma outra faixa de dimensão de coluna pode interceptar a mesma posição. Colunas com `width=2` mas com `min`/`max` abrangendo mais de uma coluna FAIL, mesmo quando openpyxl mostra 2. Registrar QA de conversão/visualizador separadamente. A:F e bordas thin intactas, sem mudança em valores, causas, X, efeitos ou autorização.


## DEC-MCE-040 — recuperar seis folhas, largura visivel 2 e heights 20/30
A regra de largura `P09_L50_G_AR_DISPLAY_2` usa `width=2.7109375` armazenado (MDW7, 19px), **exibido 2,00**; valor armazenado 2.000 resulta em 1,29 visivel. Teste de no-overlap isolado de DEC-MCE-039 nao garante 2,00 exibido. Quando a tarefa for so visual, preservar numero de causas/folhas e X em vez de eliminar as 76 pendencias do caso ADM. Height textual: 1=20pt 2=30pt 3=40pt etc; verificação independente e Excel visual nao simulado. Documento industrial nao entra no GitHub.


## DEC-MCE-041 — AR como excecao visivel 96
Validar o contrato `column_width_profile=P09_L50_G_AQ_DISPLAY_2_AR_96` por coluna em cada aba: G:AQ armazenar `2.7109375` para display `2.00`, AR armazenar `96.7109375` para display `96.00` sob MDW7, sem sobreposicoes. Nao aceitar no ADM o perfil `G:AR=2`, pois AR e excecao. Este gate e somente de layout; 6 abas, 218 causas/documentais e 175 X preservados, Excel/Windows NOT_RUN e gates de engenharia intocados.


## DEC-MCE-042 — convencao de visualizacao SP da MCE ADM
Para os dois alarmes H2 documentados do ADM, `FOLHA 1!D22` deve ser `10%` e `D23` deve ser `20%`, sem `LIE` no SP. A referencia `% LIE` deve permanecer na descricao da condicao, quando a fonte a utiliza. Nao mudar setpoint fisico, ppm, intervalo, latch, reset nem saídas PLC. A edicao documental permitida e apenas o texto do SP, sujeita a controle de fontes, sem alegar autorizacao de implantacao. Nao extrapolar formato para grandezas nao percentuais.

## Gate de completude metodologica DEC-MCE-068
Antes de concluir o entendimento e antes de qualquer emissao, seguir o Contrato de completude funcional em `../../matriz-causa-efeito/references/metodo-e-saidas.md`: observacao individual por causa, avaliacao de TODOS os efeitos aplicaveis e justificativa de cada X/ausencia de X; SP somente conforme contrato do projeto, preservando coluna do modelo. Caso nao exista prova ou autorizacao de celulas, STOP; nao usar texto generico para preencher observacao nem converter supervisao automaticamente em comando. A fonte de verdade continua sendo `systems/mce/docs/EXECUCAO.md`.
