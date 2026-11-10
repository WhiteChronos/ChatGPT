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
