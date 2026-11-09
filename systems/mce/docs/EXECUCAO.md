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
