## REGRA DE OURO INVIOLAVEL — DEC-MCE-071 (2026-11-10)

**Contrato de entrega fail-closed do MCE.** Pedido de "criar/elaborar/corrigir/entregar a Matriz" = `MCE_XLSX`. O unico arquivo principal e Microsoft Excel `.xlsx` no perfil P09 **efetivamente contratado e homologado** para o projeto (L50, L57 ou outro aprovado). PDF e somente espelho fiel opcional do XLSX; PDF de auditoria, JSON, MD, CSV, planilha generica, template vazio e relatorio de pre-analise nunca substituem a Matriz.

1. **Antes de comecar e antes de responder:** classificar `MCE_XLSX` e conferir baseline por SHA, fontes revisadas, layout contratado, modelo mestre aprovado, lista exata de celulas, autorizacao formal `AUTORIZO_ELABORACAO_MCE`, observacao por causa, efeitos identificados, cada X/ausencia justificado, SP conforme contrato, QA OOXML, Excel Windows e PDF se solicitado. Consulta a fontes privadas somente por acesso autorizado.
2. **Gate faltando = STOP.** Dizer literalmente `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`, identificar bloqueios objetivos e proximo gate; nao anunciar "elaboracao entregue" e nao apresentar PDF/JSON ou o XLSX historico como substituto do arquivo atualizado. Se houver relatorio explicitamente pedido, rotular `AUXILIAR_NAO_E_MATRIZ`, nunca principal.
3. **Gate completo = copia derivada pelo unico executor canonico.** Verificar `FOLHA N`, geometria especifica do modelo homologado, texto, observacoes, X seletivos com evidencia, SP do projeto, formulas/mesclas/estilos, audit OOXML, Excel Windows e equivalencia PDF. Estado final do arquivo: `MCE_PRELIMINAR_PARA_REVISAO`, sem homologacao automatica de engenharia.
4. **Preflight de formato por ferramenta:** antes de declarar MCE entregue, executar no Windows `python systems/mce/scripts/mce_delivery_contract.py --manifest MANIFESTO_PRIVADO.json --root WORKSPACE_PRIVADO`. `FAIL_FORMAT_CONTRACT` e `FAIL_ENGINEERING_GATE` bloqueiam entrega. `PASS_BLOCKED_DECLARED` so confirma que o bloqueio foi comunicado, e `PASS_MCE_DELIVERY_PREFLIGHT_ONLY` nao substitui auditoria independente de engenharia.
5. **Falha de Skill espelhada = STOP:** atualizar `systems/mce/.agents/skills` E `.agents/skills` em mesmo commit. Testar igualdade binaria pelo `systems/mce/scripts/verify_mce_skill_mirrors.py` na CI Windows antes de considerar a mudanca validada.

Esta regra prevalece em novas emissoes sobre exemplos historicos de saida conflitantes, SEM apagar registros anteriores ou inventar logica. CI verde e testes sintéticos nao constituem autorizacao de engenharia. Nao fazer merge, deploy, editar master ou publicar documentos industriais sem autorizacoes proprias.

# Contratos de entrada, saida e autorizacao

## `analise.json` (fase A)
Campos obrigatorios: `project`, `ss`, `summary`, `findings`, `gaps`. Cada `findings[]` com classificacao `DOCUMENTADO` deve conter `text`, `source_name`, `line` (para .txt/.md) e `verbatim_excerpt`; a fonte registrada deve ser identificavel no inventario. Se projeto/SS nao forem `NAO IDENTIFICADO`, exigir `identity_evidence` para ambos, contendo fontes, linhas e trechos literais. Para PDF/DOCX/XLSX, necessaria verificacao manual do trecho, revisao, pagina/desenho e TAG; a sinalizacao `manual_evidence_verified` representa declaracao do revisor, nao prova automatizada.

## `contract.json` (Skill 01)
Criado com tudo bloqueado. Liberar `model_approved=true` apenas para o template efetivamente aprovado. Registrar `protected_rows_by_sheet` para todas as abas, `frozen_sheets`, `matrix_ranges` e as coordenadas exatas em `editable_cells`; o inventario inicial precisa ter `template_classification=MODELO_APROVADO`. `max_causes_per_sheet` deve permanecer 50. Antes de aprovar, revisar cabecalhos, legendas, notas fixas, protecao, formulas, mesclas, estilos condicionais e areas de impressao. A ferramenta rejeita intervalos que excedam as linhas existentes no modelo.

## `autorizacao.json` (gate humano)
Exemplo de formato (dados de demonstracao):

```json
{
  "decision": "AUTORIZO_ELABORACAO_MCE",
  "approver": "RESPONSAVEL PELA APROVACAO",
  "project": "DENOMINACAO DOCUMENTADA",
  "ss": "SS DOCUMENTADA",
  "source_manifest_sha256": "HASH DO INVENTARIO"
}
```

A autorizacao e guardada no `state.json`, vinculada ao inventario de fontes. Nao usar este arquivo de exemplo para representar aprovacao real: o agente so deve criar este registro depois da manifestacao expressa do responsavel.

## `alteracoes.json` (fase B)
Lista de edicoes **textuais** com `sheet`, `cell`, `old_text`, `new_text`, `source_name`, `source_sha256`, `source_location`, `reference_revision`, `verbatim_excerpt` e `evidence_status=DOCUMENTADO`. Sem fonte, sem alteracao. Nenhuma edicao e inferida automaticamente do grafo do P&ID.

## Saidas
- `base/modelo.xlsx` preservada por SHA-256.
- `sources/`: copias locais das fontes informadas.
- `state.json`: historico de fases e digests do modelo/documentos.
- `RELATORIO_ENTENDIMENTO.md`: relatorio fundamentado com STOP.
- `output/MCE_PRELIMINAR.xlsx`: apenas quando TODOS os gates forem satisfeitos.
- `ALTERACOES_MCE.json` e `AUDITORIA_MCE.json`: diff e QA detalhados.

## Erros impeditivos e limites
A falta de Projeto/SS, ausência de original oficial, liberação de celula de cabecalho, fonte divergente, mais de 50 causas por folha, alteracao em formula, cores funcionais, alteracao nao autorizada ou falha no audit bloqueiam a saida. O QA automatizado comprova invariantes estruturais analisadas e nao garante sozinho equivalencia visual de recursos Excel exóticos ou validade de uma SIF. Exigir revisao humana e FAT/SAT para aceite operacional.

## Pesquisa GitHub de P&ID

A extensao usa `scripts/mce_system.py` para orquestrar `pid_bridge.py` sem modificar `mce_workflow.py` no que se refere aos gates de autorizacao de MCE. Depois do inventario e antes do relatorio de entendimento, registrar as exportacoes de P&ID como fontes no init. Importar com `pid-import`, comparar com lista I/O com `compare-io` e exigir `pid_integration_review` para cada SHA derivado. Nao executar o modelo de terceiros; somente converter JSON/CSV entregue pelo usuario. Ver `README.md` e `research/top10_verificados.json`.

**Falha de seguranca detectada:** o exemplo didatico Industrial-Control tem sombreamento de parametro em `validate_coverage`, impedindo reconhecer efeitos ausentes; foi reimplementado em validador proprio com teste adversarial. **Licencas:** S-Houston e Industrial-Control sem licenca identificada; pyDEXPI AGPL-3.0 (nao incorporado). Nenhum dado de projeto publicado.


## Perfil opcional de paginação com última linha 50 — P09_L50_APROVADO_VISUALMENTE

Este perfil é uma derivação de formato aprovada visualmente pelo usuário, sem substituir automaticamente o modelo mestre P09 L57. Para selecioná-lo, o contrato de uma cópia de modelo efetivamente homologada deve declarar layout_profile = P09_L50_APROVADO_VISUALMENTE. O contrato inicial permanece bloqueado, com model_approved=false e editable_cells vazias.

Linhas de cabeçalho 1:7; causas em 8:50 = 43 posições; H8:H50 em sequência 1..43, 44..86, 87..129; 35 efeitos nas colunas I:AQ, descrição na linha 5 girada em 90 graus; área de impressão A1:AR50; 46 mesclagens na variante visual; Arial 10 títulos e 8 restante; alturas 20/30 pt e bordas thin. Nenhum dado abaixo da linha 50. O executor chama verify_p09_l50_model durante verify_contract, sem escrever no Excel, e rejeita qualquer inconformidade.

A revisão pode ser reconstruída sem herança da anterior: a base funcional deve ser somente a documentação atual aprovada; identificadores antigos e marcações X/I não são transferidos por padrão. A autorização formal AUTORIZO_ELABORACAO_MCE, o SHA do master aprovado, whitelist e revisão de engenharia continuam indispensáveis; o teto geral de 50 causas não é confundido com as 43 vagas deste perfil.

Testes sintéticos (no Windows nativo): python -m pytest -q systems/mce/tests/test_mce_workflow.py. Verificar também preview/impressão do Excel Windows; CI não constitui aceite do host ou validação funcional.


## Perfil L50 sem notas em colunas

Quando o responsavel solicitar matriz limpa, registrar annotation_policy=EXTERNAL_ONLY no contrato aprovado. Para essa opcao o workflow impede notas preenchidas em AR8:AR50, comentarios/notas anexadas a celulas e novas edicoes autorizadas nesse intervalo. Preservar o cabecalho original AR7 e as bordas, fontes, indices, mesclas, X/I e impressão A1:AR50. Fonte, revisao e pendencias permanecem rastreadas externamente e privadamente; formato sem notas nao libera logica de engenharia.


## Contrato de saida MCE — formato imutavel DEC-MCE-032
- `MCE_XLSX` = **somente Microsoft Excel .xlsx, P09 validado**; projeto ADM Gamboa usa perfil L50 de DEC-MCE-027 e anotacoes EXTERNAL_ONLY de DEC-MCE-028.
- `RELATORIO_ENTENDIMENTO` e `PENDENCIAS` podem ser PDF/Markdown, sempre entregaveis complementares separados; nunca substituir o arquivo `.xlsx`.
- Sem `AUTORIZO_ELABORACAO_MCE`, modelo mestre aprovado, `editable_cells`, fontes e runtime Windows disponivel, manter `MCE_XLSX=NAO_EMITIDO_BLOQUEADO`; nenhuma MCE em PDF/MD e nenhuma planilha generica vazia representando MCE concluida.
- Gate de verificacao: saida Excel abre como XLSX, somente abas `FOLHA N`, assinatura de layout P09, 43 causas/folha, 35 efeitos, fonte 10/8, sem notas; auditoria OOXML obrigatoria. O PDF, mesmo que preliminar, nao e "a matriz".

- Violacao de formato, inclusive substituir o Excel solicitado por PDF/Markdown ou entregar XLSX vazio como MCE preenchida: `FAIL_FORMAT_CONTRACT`. Nao reinterpretar `FAIL_FORMAT_CONTRACT` como autorizacao para gerar relacoes funcionais fora do fluxo homologado.


## Politica DEC-MCE-034: altura progressiva e colunas P09 L50 (2026-11-10)

- Perfil `P09_L50_APROVADO_VISUALMENTE`: cada folha termina na **linha fisica 50**, com 43 posicoes de causa entre 8 e 50. Paginacao sequencial por causa preenchida, nao por folha de documento de arquitetura. Somente a ultima folha pode ficar parcialmente vazia.
- Regra de legibilidade: considerar o maximo de linhas visuais das descricoes B/C/F:G mesclado, com quebra de texto. `altura_pt=20+10*(n_linhas-1)`: 1=20, 2=30, 3=40, 4=50, 5=60, ... ate 400 pontos. Se o calculo resultar acima do limite Excel, bloquear e revisar texto/colunas.
- Perfil de largura `P09_L50_20261110` para novas derivacoes aprovadas: B=25, C=56, F=34; F:G permanece mesclado. Nao redimensionar I:AQ, G, D/E/H/AR nem cabecalhos. O validador canonico aceita alturas em passos de 10 e, se `column_width_profile` for declarado, valida essas tres larguras.
- A altura computada pela metrica de wrapping e **estimativa** sem Microsoft Excel: registrar `QA_VISUAL_WINDOWS=NOT_RUN` quando nao abrir o arquivo no Excel real. Esta orientacao nao altera modelo mestre nem se sobrepoe ao `AUTORIZO_ELABORACAO_MCE`.
- Comparar antes/depois valores, 175 X e 218 registros somente no caso ADM de 10/11/2026 (e nao como contagens globais). Preservar 35 efeitos, Arial10/8, 46 merges, print A1:AR50 e notas EXTERNAL_ONLY.


## DEC-MCE-035 — Verificação de alturas em uma linha visual

Para MCE P09 L50, fazer POSTFLIGHT de todas as abas contra a regra `20+10*(linhas_visuais-1)`. Regra legível de saída: **1 linha visual = 20 pt; 2 linhas = 30 pt; 3 linhas = 40 pt; 4 linhas = 50 pt**. Não aumentar para 30 pt se o texto completo ocupar uma unica linha no tamanho real Arial 8 pt com colunas B=25, C=56, F=34 (F:G mesclado). O incidente de 10/11/2026 revelou erro da contagem visual por subtrair **18 px arbitrarios** da largura útil da coluna C, transformando 34 textos de uma linha em falsos 30 pt. Usar métrica de texto proporcional a 8 pt (aprox. 10,67 px a 96 DPI), as larguras reais do workbook e quebras explicitas; registrar fonte substituta e riscos perto do limite. Entregar copia XLSX corrigida somente com alturas modificadas, mais prova de diff dos valores, X e geometria. Não afirmar QA nativo Windows ou subagente independente sem evidencias.

## DEC-MCE-037 — retificacao do formato P09 L50 em 2026-11-10
O usuario quis dizer **largura das colunas a partir de A = 2** no Excel, nao bordas espessura 2. A regra anterior DEC-MCE-036 de `medium` esta revogada. Restaurar `thin` de origem. O novo perfil `P09_L50_ALL_COLUMNS_2` valida width=2 em A:AR para cada folha; a largura de uma coluna vale em todas as linhas. Advertir risco de B/C/F ilegíveis; variante I:AQ width2 preservando B/C/F e opcional, nunca substituir pedido literal silenciosamente. Nao inventar relações, não alterar outros estilos. Sem host Windows: `NOT_RUN`.

## DEC-MCE-038 — perfil definitivo de largura G:AR e auditoria de X vazios
Pedido ADM: **A:F conservar larguras existentes**, **G:AR width=2** em todas as `FOLHA N`, bordas `thin` originais sem mudanca. Contrato `column_width_profile=P09_L50_G_AR_2` valida largura; `require_effect_per_cause=true` valida que toda linha com B/C/F preenchido possui pelo menos um X e titulo correspondente em I5:AQ5, sem X em linhas vazias. Nao inventar X para switches, painéis, interfaces ou divergencias: gerar relatorio XLSX externo `ITENS_SEM_EFEITO_DOCUMENTADO` e somente causas com efeitos sustentados permanecem na MCE. Paginacao a cada 43 linhas (8:50), remapeando links pelo titulo de efeito.
No caso ADM: do arquivo anterior de 218 registros e 175 X, 76 registros nao tinham X, ficando na pendencia externa. Nova MCE documental com 142 entradas (43/43/43/13) e 175 X originais, 4 folhas. Esta triagem e documental e provisoria, nao aprova intertravamentos. Manter logs/assinaturas, fonte MD-C ET-C ARQ-D, controle de whitelist e aprovacao humana. Sem Windows: `NOT_RUN`; DataCenter `COPY_PENDING`.

## DEC-MCE-039 — pós-auditoria XML para largura G:AR 2
Para `column_width_profile=P09_L50_G_AR_2`, validar todos os elementos OOXML `<cols><col .../></cols>`: 38 colunas G..AR com registro explícito único (`min=max`), `width="2"`, `customWidth="1"`, sem intervalos conflitantes. As medidas via `openpyxl.column_dimensions[col].width` são insuficientes quando há colunas agrupadas/sobrepostas (problema em arquivo ADM anterior). Após correção comparar canonização de `sheetData`, merges, fontes, áreas, valores, cruzamentos e demais partes do pacote XLSX. Excel nativo QA separado de OOXML PASS.

## DEC-MCE-040 — corrigir causa raiz de 4 folhas, largura 1,29 e altura 20 incorreta
A MCE ADM é um artefato visual de **6 folhas** com 43/43/43/43/43/3 registros e 175 X. Uma edicao apenas de formatos NÃO pode remover 76 registros sem X; mantê-los como inventario pendente em matriz documental de seis folhas, com relatorio de pendencias externo e sem criar X. A antiga extração para 4 folhas só seria nova revisão de escopo mediante aceite humano. Para G:AR atingir **2,00 mostrado no Excel**, perfil `P09_L50_G_AR_DISPLAY_2` exige `<col min=max width="2.7109375" customWidth="1"/>` (MDW=7; 19 px); `width=2.0` mostrava 1,29. Fonte: https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.column?view=openxml-3.0.1 .
Linhas de causa: `20+10*(numero_de_linhas_visuais-1)` pt com fonte Arial 8 e larguras A:F originais; não forçar todas a 20 nem todas a 30. Em candidato ADM, aferição de fonte substituta marcou 12 linhas com 30 pt e demais a 20; validar no visualizador nativo antes da aprovação. OOXML/ZIP separado de QA visual e homologação de engenharia.

## DEC-MCE-041 — AR de largura 96,00 como excecao a G:AQ 2,00
Na copia documental ADM de **6 folhas**, a coluna AR Observacao nao participa da largura 2; ela deve exibir **96,00**. G:AQ (37 colunas) continuam exibindo **2,00**. Para arquivo Excel Normal MDW=7: `<col min=44 max=44 width="96.7109375" customWidth="1"/>`; demais G:AQ em `2.7109375`. A:F/estilos/mesclas/valores/175 X/218 registros/altura das linhas inalterados. Relacao documental sem X continua pendente; nenhuma nova marca criada. Perfil `P09_L50_G_AQ_DISPLAY_2_AR_96` exige essa excecao, sem redefinir os demais projetos automaticamente. A auditoria diferencial deve comprovar que apenas seis atributos width em AR mudaram. `QA_EXCEL_WINDOWS=NOT_RUN` ate abrir no Microsoft Excel; `DATACENTER=COPY_PENDING` ate recibo.

## DEC-MCE-042 — SP percentual sem LIE
Para ADM `DE-2713.01-6613-847-RPJ-006`, exibir `10%` e `20%` em `FOLHA 1!D22,D23`; texto `LIE` nao pertence a celula SP. Manter a identificacao `% LIE` na descricao funcional C22/C23; nao alterar valores numericos ou criar novos SPs. Na auditoria, comparar os arquivos OOXML: somente as duas cadeias inline dos SP mudam, todas as outras entradas e estilos, larguras G:AQ/AR, alturas, mesclas, 6 folhas, 218 registros e 175 X permanecem. Backup/DataCenter fisico e Excel nativo exigem evidencias separadas.


## Contrato de completude funcional — DEC-MCE-068 (2026-11-10)

**Aplicacao:** toda elaboracao, revisao e emissao de Matriz de Causa e Efeito. A referencia privada de apresentacao registrada por DEC-MCE-066 orienta forma e detalhamento; nao autoriza replicar TAGs, setpoints, logicas ou cruzamentos de outro projeto.

1. **Inventario integral:** para cada causa/linha candidata registrar ID, TAG, descricao da condicao e revisao da fonte. Distinguir EVENTO_CAUSAL, SUPERVISAO_SEM_ATUACAO, INTERFACE e ITEM_FORA_ESCOPO; nunca contar apenas X existentes como prova de completude.
2. **Efeitos completos:** descrever todas as funcoes aplicaveis do projeto, sem preencher artificialmente as posicoes disponiveis; cada efeito deve ter identidade funcional clara, responsavel e evidencia por documento, revisao, folha/pagina e SHA no relatorio PRIVADO.
3. **X seletivo e auditavel:** avaliar para cada linha TODAS as colunas de efeitos aplicaveis. Registrar em relatorio privado a decisao X, NAO_APLICAVEL_COM_JUSTIFICATIVA ou PENDENTE_DE_EVIDENCIA para cada par candidato. Cada X existente requer revalidacao; ausencia de X nao prova ausencia de efeito. Proibido aplicar X em todas as colunas para aparentar completude.
4. **Observacao por causa:** cada linha mantida da MCE deve ter observacao especifica, util e documental, descrevendo a atuacao, indicacao ou ausencia justificada de atuacao, fronteira de responsabilidade e condicoes de falha/rearme quando documentadas. Se faltar evidencia, redigir rascunho no relatorio de PENDENCIAS e bloquear a emissao; nunca inventar uma observacao afirmativa para eliminar celulas vazias.
5. **SP condicionado ao contrato:** preservar fisicamente a coluna se pertence ao modelo, mas nao assumir seu preenchimento. Quando o usuario/projeto determinar "SP nao utilizado", manter as celulas SP vazias SOMENTE na copia derivada aprovada; valores tecnicos documentados podem figurar na descricao/observacao conforme convencao aprovada, sem perder unidade fisica. Uma decisao de uso de SP e escopo projeto/revisao, nao padrao universal; nao apagar SP historico sem autorizacao de celula.
6. **Confronto documental:** reconciliar MD, ET, P&ID, arquitetura, lista I/O e manuais aplicaveis para alarme, comandos hardwired, falha de UTR, HVAC, exaustao, UPS, bypass, reset e interface SCADA. Distinguir divergencia de revisoes de requisito valido. Nao promover recomendacoes ou legenda de P&ID a logica de intertravamento.
7. **Preflight antes da emissao:** relatorio privado deve comprovar 100% das linhas revisadas, 100% das observacoes tecnicamente resolvidas, todos os X validados, todos os candidatos a pares causa/efeito classificados, SP conforme contrato e nenhuma divergencia funcional impeditiva. Se nao houver prova, STOP em ANALISADO_AGUARDANDO_DECISAO, sem XLSX/PDF "final".
8. **Entrega controlada:** arquivo principal XLSX P09 vigente em copia derivada, PDF somente representacao fiel se solicitado, QA OOXML/Excel Windows e cotejo entre as paginas. Nao editar mestre nem logica funcional sem modelo homologado, whitelist de celulas, AUTORIZO_ELABORACAO_MCE vinculado a hashes e revisao multidisciplinar.

**Anti-regressao:** o perfil de arquivo historico sem observacoes ou com SP preenchido nao substitui esta verificacao de completude para novas emissoes. Decisoes antigas de layout sao preservadas como historico, e eventual conflito exige revisao explicita do contrato, nao alteracao silenciosa do modelo.



## DEC-MCE-075 — Preparar contrato sem pedir a mesma autorizacao repetidamente

**Causa-raiz:** \`mce_workflow.py init\` cria contrato bloqueado (\`model_approved=false\`, whitelist vazia), mas nao oferecia comando para propor coordenadas do Excel real. A ferramenta tambem limita edicoes a texto e protege X e efeitos; historicos \`EXTERNAL_ONLY\` nao correspondem a decisao mais recente ADM de observar na coluna AR.

**Correcao do fluxo de preparacao:** apos \`init\`, executar no host Windows privado:
\`\`\`powershell
python systems/mce/.agents/skills/engenharia-mce-projeto/scripts/mce_workflow.py propose-contract --workspace "C:\MCE_DADOS\ADM_GAMBOA" --annotation-policy IN_MATRIX --sp-policy UNUSED
\`\`\`
A saida \`contract.proposed.json\` e SOMENTE PROPOSTA: lista \`matrix_ranges\`, \`editable_cells\` de texto C/AR e SP historicos para revisao, preserva 35 efeitos, conta X existentes sem validalos e explicita os gates pendentes. Nao modifica \`contract.json\`, \`state.json\`, o XLSX original ou aprova o modelo. O responsavel revisa o contrato candidato, confirma o perfil vigente, protege cabecalhos e autoriza celulas especificas; mudancas de X/cabecalhos exigem analise e edicao funcional segregada, nunca X arbitrario.

**Sem novos bloqueios burocraticos:** quando a autorizacao de TRABALHO ja foi registrada (ADM: DEC-MCE-074), nao a solicitar novamente; preparar automaticamente dados, contrato candidato e pendencias. **Sem bypass de seguranca:** somente o gate de elaboracao documentado e modelo homologado permitem alterar matriz industrial; preparacao != emissao/revisao/aceite. Nao usar progresso de CI, modelo visual ou rascunho como homologacao de intertravamentos.



## DEC-MCE-078 — Versionamento preliminar PV 01, 02, ... e integracao documental

Em toda matriz MCE derivada, o ARQUIVO ENTREGAVEL deve chamar-se CODIGO_DOCUMENTO-REVISAO + " - PV NN.xlsx", por exemplo DE-000.00-0000-000-ABC-001-B - PV 01.xlsx. Numeracao crescente POR DOCUMENTO, inicial PV 01; sem pular, sobrescrever ou criar nova PV de bytes identicos. PDF espelho, se autorizado, segue mesmo nome base/PV e extensao .pdf. MCE_PRELIMINAR.xlsx e somente saida interna do editor canonico, nao nome de entrega.

Ordem obrigatoria: fontes e SHA -> auditoria mce-verificacao-cruzamentos -> verificacao de fonte/CLAIMS por mce-verificacao-documental -> reauditoria de X e classificacao de nao aplicavel -> proposta de contrato -> gates humanos e executor canonico init/understand/authorize/apply/audit -> mce_pv_controller.py copia binaria com ledger append-only privado -> mce_delivery_contract.py confere nome PV e gates -> aceite e fechamento externo -> PROXIMO DOCUMENTO PV 01. Skills verificadoras nao editam Excel e nao produzem X por inferencia; repeticao de efeito entre folhas nao valida X. As duas skills complementares estao no catalogo privado do usuario e nao sao instaladas/publicadas no GitHub publico automaticamente. Ausencia do runtime = NOT_RUN.

Preservar por PV: identificador do documento, PV, SHA-256 entrada/saida, digest encadeado, data, relatorio de alteracoes e pendencias, criterios de fechamento e elo com fontes/revisoes. Guarda de bytes industriais e banco somente em cofre PRIVADO comprovado. MCE DataCenter operacional Windows nao existe nesta fase; evento NOTA/STATUS no unico ledger de memoria MCE apenas se host privado conectado e autorizado. Aprendizado continuo: feedback -> falha comprovada -> regra candidata -> teste sintetico/adversarial -> revisao -> memoria + CI do mesmo commit; jamais autohomologar ou modificar pesos/modelo.

Contrato detalhado e fluxo: systems/mce/docs/PV_VERSION_WORKFLOW.md; schema publico SOMENTE de metadados: systems/mce/datacenter/PV_VERSION_MANIFEST.schema.json. Nenhuma aprovacao de trabalho anterior equivale a aprovacao funcional ou do modelo.

**DEC-MCE-079:** revisao documental (ex.: `-B`) e parte obrigatoria da identidade no nome; nao acrescentar nome da unidade ou parenteses PRELIMINAR VERSÃO. A renomeacao corretiva de PV 01 do mesmo SHA e metadado, nao alteracao de causa/efeito e nao cria PV 02. Manter registro de migracao do nome historico e nunca sobrescrever arquivo ou ledger original. Ver docs/PV_VERSION_WORKFLOW.md.


## DEC-MCE-081 — layout H=3 por perfil e perguntas úteis à MCE
Quando o perfil contratual aplicável for `P09_L50_H_DISPLAY_3`, conferir a largura EXIBIDA H=3.00, OOXML width=3.7109375 para MDW7, e nunca alterar as demais larguras ou dados por consequência dessa decisão. Como é alteração de layout, separar dos gates de engenharia: a comparação ZIP não comprova homologação nem substitui Excel Windows nativo. Questions Word: apenas Localização/Folha/Pergunta, de modo didático, sem repetir a mesma decisão por TAG; não omitir divergências individuais. Aprendizado testado em cada ciclo explícito, sem serviço em background ou persistência DataCenter sem recibo.
